"""Confidence-scored diagram routing.

Each renderer scores how well a diagram matches its type (0.0-1.0).
The router picks the highest-scoring renderer above a minimum threshold,
eliminating the fragile boolean priority chain that caused cascading regressions.

Inspired by Empirica's holistic confidence gating — don't gate on a fragile
binary, score confidence and let the best match claim it.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from . import renderlib as rl

logger = logging.getLogger(__name__)

# Minimum score to claim a diagram (below this → svgbob fallback)
MIN_SCORE = 0.30


@dataclass
class RendererScore:
    """Score from a single renderer."""
    name: str
    score: float
    signals: dict[str, float]  # individual signal contributions for debugging


def score_sequence(source: str) -> RendererScore:
    """Score how likely this is a sequence diagram.

    Strong signals: vertical lifeline lanes with horizontal message arrows
    between them. Sequence diagrams are characterized by parallel vertical
    lines (lifelines) with horizontal arrows crossing between them.
    """
    grid, width, height = rl.parse_grid(source)
    signals: dict[str, float] = {}

    if width == 0 or height < 4:
        return RendererScore("sequence", 0.0, signals)

    rows = len(grid)

    # Detect vertical lanes: columns with consistent │ characters
    col_counts: dict[int, list[int]] = {}
    for r in range(rows):
        for c in range(width):
            if grid[r][c] in rl.VERT_CHARS:
                if c not in col_counts:
                    col_counts[c] = []
                col_counts[c].append(r)

    if not col_counts:
        return RendererScore("sequence", 0.0, signals)

    max_count = max(len(rows_list) for rows_list in col_counts.values())
    if max_count < 3:
        return RendererScore("sequence", 0.0, signals)

    threshold = max(3, int(max_count * 0.4))
    lane_cols = sorted(
        c for c, rows_list in col_counts.items()
        if len(rows_list) >= threshold
    )

    # Filter close columns (box borders are close together, lifelines are spaced apart)
    filtered_cols: list[int] = [lane_cols[0]] if lane_cols else []
    for c in lane_cols[1:]:
        if c - filtered_cols[-1] >= 3:
            filtered_cols.append(c)

    num_lanes = len(filtered_cols)
    if num_lanes < 2:
        return RendererScore("sequence", 0.0, signals)

    signals["lanes"] = min(0.35, 0.15 + (num_lanes - 2) * 0.05)

    # Count horizontal message arrows (rows with arrow heads + horizontal chars)
    arrow_count = 0
    for r in range(rows):
        row_str = "".join(grid[r])
        has_arrow = any(c in rl.ARROW_HEADS_RIGHT for c in row_str) or \
                    any(c in rl.ARROW_HEADS_LEFT for c in row_str)
        has_horiz = any(c in rl.HORIZ_CHARS for c in row_str)
        if has_arrow and has_horiz:
            arrow_count += 1

    if arrow_count < 1:
        return RendererScore("sequence", 0.0, signals)

    signals["arrows"] = min(0.35, 0.15 + (arrow_count - 1) * 0.05)

    # Even lane spacing (sequence diagrams typically have regular spacing)
    if num_lanes >= 3:
        spacings = [filtered_cols[i+1] - filtered_cols[i] for i in range(len(filtered_cols)-1)]
        avg_spacing = sum(spacings) / len(spacings)
        variance = sum((s - avg_spacing) ** 2 for s in spacings) / len(spacings)
        if variance < avg_spacing * 2:
            signals["even_spacing"] = 0.10

    # Actor labels above lanes
    first_bar_row = min(
        min(col_counts[c]) for c in filtered_cols if c in col_counts
    )
    if first_bar_row > 0:
        structural = rl.HORIZ_CHARS | rl.VERT_CHARS | rl.CORNER_CHARS | rl.TEE_CHARS
        for hr in range(first_bar_row - 1, -1, -1):
            header_text = "".join(grid[hr]).strip()
            if header_text and not all(ch in structural or ch == ' ' for ch in header_text):
                signals["actor_labels"] = 0.15
                break

    # Ratio of lifeline rows to total height — sequence diagrams are tall and thin
    lifeline_extent = max(len(col_counts.get(c, [])) for c in filtered_cols)
    if lifeline_extent >= height * 0.5:
        signals["tall_lifelines"] = 0.10

    total = max(0.0, min(1.0, sum(signals.values())))
    return RendererScore("sequence", total, signals)


def score_flow(source: str) -> RendererScore:
    """Score how likely this is a flow diagram.

    Strong signals: boxes connected by arrows. The defining characteristic
    is directional connections between boxes (flowcharts, architecture diagrams).
    """
    grid, width, height = rl.parse_grid(source)
    signals: dict[str, float] = {}

    if width == 0:
        return RendererScore("flow", 0.0, signals)

    boxes = rl.find_boxes(grid)
    if len(boxes) < 2:
        return RendererScore("flow", 0.0, signals)

    signals["boxes"] = min(0.20, 0.10 + (len(boxes) - 2) * 0.03)

    arrows = rl.find_arrows(grid, boxes)
    connected = [a for a in arrows if a.from_box is not None or a.to_box is not None]

    if not connected:
        # No connected arrows = not a flow diagram
        return RendererScore("flow", 0.0, signals)

    signals["connected_arrows"] = min(0.35, 0.20 + (len(connected) - 1) * 0.05)

    # Labels on arrows
    labeled = [a for a in arrows if a.label]
    if labeled:
        signals["arrow_labels"] = min(0.10, len(labeled) * 0.03)

    # Flat layout (boxes not nested) — flow diagrams are typically flat
    nested = False
    for i, outer in enumerate(boxes):
        for j, inner in enumerate(boxes):
            if i != j and _box_contains(outer, inner):
                nested = True
                break
        if nested:
            break

    if not nested:
        signals["flat_layout"] = 0.10
    else:
        signals["nested_penalty"] = -0.20

    total = max(0.0, min(1.0, sum(signals.values())))
    return RendererScore("flow", total, signals)


def score_wireframe(source: str) -> RendererScore:
    """Score how likely this is a wireframe/UI mockup.

    Strong signals: nested boxes (containment), form elements, title-on-border,
    column dividers. Wireframes are characterized by boxes-within-boxes creating
    a layout structure.
    """
    grid, width, height = rl.parse_grid(source)
    signals: dict[str, float] = {}

    if width == 0 or height < 4:
        return RendererScore("wireframe", 0.0, signals)

    boxes = rl.find_boxes_tolerant(grid)
    if len(boxes) < 2:
        return RendererScore("wireframe", 0.0, signals)

    # Check for containment (nested boxes) — the defining wireframe signal
    containment_count = 0
    for i, outer in enumerate(boxes):
        for j, inner in enumerate(boxes):
            if i != j and _box_contains(outer, inner):
                containment_count += 1

    if containment_count == 0:
        return RendererScore("wireframe", 0.0, signals)

    signals["nesting"] = min(0.40, 0.25 + (containment_count - 1) * 0.05)

    # Form elements: [____], [x], (*), ( )
    form_count = 0
    for pattern in ("[____", "[x]", "[ ]", "[X]", "(*)", "( )"):
        form_count += source.count(pattern)
    if form_count:
        signals["form_elements"] = min(0.20, form_count * 0.05)

    # Title-on-border: alphabetic text on the top border of boxes
    for box in boxes:
        row = box.top
        for c in range(box.left + 1, box.right):
            ch = grid[row][c]
            if ch not in rl.HORIZ_CHARS and ch not in rl.TEE_CHARS and ch != ' ':
                if ch.isalpha():
                    signals["title_on_border"] = 0.10
                    break
        if "title_on_border" in signals:
            break

    # Column dividers (tee chars creating panel layouts)
    tee_top = frozenset("┬╦")
    tee_bot = frozenset("┴╩")
    for box in boxes:
        for c in range(box.left + 1, box.right):
            top_ch = grid[box.top][c]
            bot_ch = grid[box.bottom][c]
            if top_ch in tee_top or bot_ch in tee_bot:
                signals["column_dividers"] = 0.10
                break
        if "column_dividers" in signals:
            break

    # Deep nesting (depth >= 2)
    for i, box in enumerate(boxes):
        depth = sum(1 for j, other in enumerate(boxes) if i != j and _box_contains(other, box))
        if depth >= 2:
            signals["deep_nesting"] = 0.10
            break

    total = max(0.0, min(1.0, sum(signals.values())))
    return RendererScore("wireframe", total, signals)


def score_table(source: str) -> RendererScore:
    """Score how likely this is a table.

    The key distinction from boxes: tables have INTERIOR vertical columns —
    vertical borders running through the middle of the structure, not just
    at the left and right edges. A box has 2 column borders (left/right);
    a table has 3+ (left, interior(s), right).

    Interior columns are detected by finding intersection points at consistent
    column positions between the leftmost and rightmost borders.
    """
    grid, width, height = rl.parse_grid(source)
    signals: dict[str, float] = {}

    if width == 0 or height < 3:
        return RendererScore("table", 0.0, signals)

    rows = len(grid)
    cols = width
    intersection_chars = rl.CORNER_CHARS | rl.TEE_CHARS

    # Find all intersection points with borders in 2+ directions
    intersections: list[tuple[int, int]] = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] in intersection_chars:
                dirs = 0
                if c + 1 < cols and grid[r][c + 1] in rl.HORIZ_CHARS:
                    dirs += 1
                if c > 0 and grid[r][c - 1] in rl.HORIZ_CHARS:
                    dirs += 1
                if r + 1 < rows and grid[r + 1][c] in rl.VERT_CHARS:
                    dirs += 1
                if r > 0 and grid[r - 1][c] in rl.VERT_CHARS:
                    dirs += 1
                if dirs >= 2:
                    intersections.append((r, c))

    if len(intersections) < 6:  # need at least a 2x2 grid (6 intersections)
        return RendererScore("table", 0.0, signals)

    # Group by column position
    col_to_rows: dict[int, set[int]] = {}
    for r, c in intersections:
        if c not in col_to_rows:
            col_to_rows[c] = set()
        col_to_rows[c].add(r)

    # Only keep columns that appear on 2+ border rows
    stable_cols = sorted(c for c, row_set in col_to_rows.items() if len(row_set) >= 2)
    if len(stable_cols) < 2:
        return RendererScore("table", 0.0, signals)

    # Group by row position
    row_to_cols: dict[int, set[int]] = {}
    for r, c in intersections:
        if r not in row_to_cols:
            row_to_cols[r] = set()
        row_to_cols[r].add(c)

    # Interior columns: those between the leftmost and rightmost
    left_edge = stable_cols[0]
    right_edge = stable_cols[-1]
    interior_cols = [c for c in stable_cols if left_edge < c < right_edge]

    # THE KEY SIGNAL: interior columns distinguish tables from boxes
    if not interior_cols:
        return RendererScore("table", 0.0, signals)

    # Verify grid connectivity: an interior column must have continuous horizontal
    # border connecting it to BOTH left_edge AND right_edge on the same row.
    # This rejects side-by-side boxes (gap between them) as tables.
    connected_interior = []
    for ic in interior_cols:
        is_connected = False
        for r in sorted(row_to_cols.keys()):
            r_cols = row_to_cols.get(r, set())
            if left_edge in r_cols and ic in r_cols and right_edge in r_cols:
                if (rl.has_horiz_border(grid, r, left_edge, ic) and
                        rl.has_horiz_border(grid, r, ic, right_edge)):
                    is_connected = True
                    break
        if is_connected:
            connected_interior.append(ic)

    if not connected_interior:
        return RendererScore("table", 0.0, signals)

    signals["interior_columns"] = min(0.40, 0.25 + (len(connected_interior) - 1) * 0.05)

    # Full-span rows (intersections at all stable column positions)
    full_rows = sum(1 for cols_set in row_to_cols.values()
                    if len(cols_set) >= len(stable_cols))
    if full_rows >= 3:
        signals["row_consistency"] = 0.20
    elif full_rows >= 2:
        signals["row_consistency"] = 0.15

    # Regular row spacing
    sorted_row_positions = sorted(row_to_cols.keys())
    if len(sorted_row_positions) >= 3:
        spacings = [sorted_row_positions[i+1] - sorted_row_positions[i]
                     for i in range(len(sorted_row_positions)-1)]
        if all(s == spacings[0] for s in spacings):
            signals["regular_spacing"] = 0.10

    total = max(0.0, min(1.0, sum(signals.values())))
    return RendererScore("table", total, signals)


def score_box(source: str) -> RendererScore:
    """Score how likely this is a plain box diagram.

    This is the most permissive renderer — catches anything with boxes
    that isn't a more specific type. Scores are naturally lower than
    more specific renderers so they win when they match.
    """
    grid, width, height = rl.parse_grid(source)
    signals: dict[str, float] = {}

    if width == 0:
        return RendererScore("box", 0.0, signals)

    boxes = rl.find_boxes(grid)
    if not boxes:
        return RendererScore("box", 0.0, signals)

    signals["has_boxes"] = min(0.25, 0.15 + (len(boxes) - 1) * 0.05)

    # Text inside boxes
    texts = rl.extract_box_texts(grid, boxes)
    if texts:
        signals["box_text"] = 0.10

    # Separators (class-diagram style)
    sep_count = sum(len(b.separators) for b in boxes)
    if sep_count:
        signals["separators"] = 0.05

    # Penalty if arrows are present (should be flow, not box)
    arrows = rl.find_arrows(grid, boxes)
    if any(a.from_box is not None or a.to_box is not None for a in arrows):
        signals["arrow_penalty"] = -0.10

    total = max(0.0, min(1.0, sum(signals.values())))
    return RendererScore("box", total, signals)


# ── Router ───────────────────────────────────────────────────────────

_SCORERS = {
    "sequence": score_sequence,
    "flow": score_flow,
    "wireframe": score_wireframe,
    "table": score_table,
    "box": score_box,
}

_RENDERERS: dict[str, Callable[[str], str]] | None = None


def _get_renderers() -> dict[str, Callable[[str], str]]:
    """Lazy-load renderer functions to avoid circular imports."""
    global _RENDERERS
    if _RENDERERS is None:
        from .sequencerender import render_sequence_svg
        from .flowrender import render_flow_svg
        from .wireframerender import render_wireframe_svg
        from .tablerender import render_table_svg
        from .boxrender import render_box_svg
        _RENDERERS = {
            "sequence": render_sequence_svg,
            "flow": render_flow_svg,
            "wireframe": render_wireframe_svg,
            "table": render_table_svg,
            "box": render_box_svg,
        }
    return _RENDERERS


def route_diagram(source: str) -> str | None:
    """Route an ASCII diagram to the best-matching renderer.

    Scores all renderers, picks highest score above MIN_SCORE.
    Returns SVG string, or None if no renderer claims it (use svgbob fallback).
    """
    scores = score_all(source)

    if not scores:
        return None

    best = scores[0]
    if best.score < MIN_SCORE:
        logger.debug(
            "No renderer scored above %.2f for diagram (best: %s=%.2f)",
            MIN_SCORE, best.name, best.score,
        )
        return None

    logger.debug(
        "Routing to %s (score=%.2f): %s",
        best.name, best.score,
        {s.name: f"{s.score:.2f}" for s in scores},
    )

    renderers = _get_renderers()
    render_fn = renderers.get(best.name)
    if render_fn is None:
        return None

    return render_fn(source)


def score_all(source: str) -> list[RendererScore]:
    """Score all renderers and return sorted (highest first)."""
    scores = [scorer(source) for scorer in _SCORERS.values()]
    scores.sort(key=lambda s: s.score, reverse=True)
    return scores


# ── Helpers ──────────────────────────────────────────────────────────

def _box_contains(outer: rl.Box, inner: rl.Box) -> bool:
    """Check if outer box fully contains inner box."""
    return (outer.top < inner.top and outer.bottom > inner.bottom and
            outer.left < inner.left and outer.right > inner.right)
