"""Flow diagram renderer — boxes connected by arrows.

Handles the most common AI-generated diagram pattern: boxes with
directional connections between them (flowcharts, architecture diagrams,
state machines).

Structure-first: find boxes, find arrows between them, render both.
Text inside boxes is always text. Arrow characters between boxes are
always arrows.
"""

from __future__ import annotations

from . import renderlib as rl


def has_flow_structure(source: str) -> bool:
    """Check if source has flow diagram structure (boxes + arrows).

    Returns True only if there are boxes AND arrows connecting them.
    Plain boxes without arrows should go to the box renderer instead.
    """
    grid, width, height = rl.parse_grid(source)
    if width == 0:
        return False

    boxes = rl.find_boxes(grid)
    if len(boxes) < 2:
        return False

    arrows = rl.find_arrows(grid, boxes)
    # Need at least one arrow that connects to a box
    return any(a.from_box is not None or a.to_box is not None for a in arrows)


def render_flow_svg(source: str) -> str:
    """Render an ASCII flow diagram to SVG.

    Detects boxes and arrows, renders as connected diagram with
    arrowhead markers and optional labels.

    Args:
        source: ASCII art with boxes and arrow connections.

    Returns:
        SVG string.
    """
    grid, width, height = rl.parse_grid(source)

    if not grid or width == 0:
        return rl.fallback_svg(source)

    boxes = rl.find_boxes(grid)
    if not boxes:
        return rl.fallback_svg(source)

    arrows = rl.find_arrows(grid, boxes)
    texts = rl.extract_box_texts(grid, boxes)

    # Also extract free text (text outside boxes that isn't part of arrows)
    free_texts = _extract_free_text(grid, boxes, arrows)

    # Build SVG with tight bounding box
    parts: list[str] = [
        rl.svg_open_tight(boxes, height),
        rl.THEME_CSS,
        rl.svg_arrowhead_defs(),
        rl.svg_background_tight(boxes, height),
    ]

    # Render boxes
    for box in boxes:
        parts.append(rl.svg_rect(box))
        for sep_row in box.separators:
            parts.append(rl.svg_separator(box, sep_row))

    # Render arrows (with box-snapped endpoints)
    for arrow in arrows:
        parts.extend(rl.svg_arrow(arrow, boxes))

    # Render box text (centered within boxes)
    headers = rl.classify_headers(texts, boxes)
    for i, span in enumerate(texts):
        box = boxes[span.box_index] if 0 <= span.box_index < len(boxes) else None
        parts.append(rl.svg_text(span, is_header=(i in headers), box=box))

    # Render free text (filter out text that duplicates arrow labels)
    arrow_labels = {a.label.lower() for a in arrows if a.label}
    for span in free_texts:
        if span.text.strip().lower() not in arrow_labels:
            parts.append(rl.svg_text(span))

    parts.append("</svg>")
    return "\n".join(parts)


def _extract_free_text(
    grid: list[list[str]],
    boxes: list[rl.Box],
    arrows: list[rl.Arrow],
) -> list[rl.TextSpan]:
    """Extract text that's outside boxes and not part of arrow paths."""
    rows = len(grid)
    cols = len(grid[0]) if grid else 0

    # Mark cells that belong to boxes or arrows
    used: set[tuple[int, int]] = set()

    for box in boxes:
        for r in range(box.top, box.bottom + 1):
            for c in range(box.left, box.right + 1):
                used.add((r, c))

    for arrow in arrows:
        for r, c in arrow.points:
            used.add((r, c))

    # Scan for text runs outside used cells
    texts: list[rl.TextSpan] = []
    for r in range(rows):
        run_start = None
        run_text = ""

        for c in range(cols):
            if (r, c) in used:
                if run_text.strip():
                    texts.append(rl.TextSpan(
                        row=r,
                        col=run_start or 0,
                        text=run_text.rstrip(),
                    ))
                run_start = None
                run_text = ""
                continue

            ch = grid[r][c]
            # Skip structural characters that aren't text
            # Note: ALL_ARROW_HEADS excluded — chars like 'v' can be text.
            # Actual arrow chars are already in the 'used' set from detection.
            if ch in (rl.HORIZ_CHARS | rl.VERT_CHARS | rl.CORNER_CHARS
                      | rl.TEE_CHARS):
                if run_text.strip():
                    texts.append(rl.TextSpan(
                        row=r,
                        col=run_start or 0,
                        text=run_text.rstrip(),
                    ))
                run_start = None
                run_text = ""
                continue

            if run_start is None:
                run_start = c
            run_text += ch

        if run_text.strip():
            texts.append(rl.TextSpan(
                row=r,
                col=run_start or 0,
                text=run_text.rstrip(),
            ))

    return texts
