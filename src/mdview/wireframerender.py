"""Wireframe / UI mockup renderer.

Renders ASCII wireframes with nested boxes, form elements, and
title-on-border text to SVG. Handles the layout patterns AI tools
produce for UI mockups and architecture diagrams.

Features:
- Nested boxes with depth-based fill (inner boxes get lighter fills)
- Title text on borders: ┌─── My App ───┐
- Form elements: [____] inputs, [x]/[ ] checkboxes, (*)/( ) radios
- List markers: > Item, * Item, - Item
- Text labels next to form elements

Structure-first: find boxes, build containment tree, detect form
elements within boxes, render with depth-appropriate styling.
"""

from __future__ import annotations

import html as html_mod

from . import renderlib as rl
from .themes import DEFAULT_THEME


def has_wireframe_structure(source: str) -> bool:
    """Check if source contains wireframe structure (nested boxes).

    Returns True if there are nested boxes (at least one box contained
    within another). Simple non-nested boxes should go to the box renderer.
    """
    grid, width, height = rl.parse_grid(source)
    if width == 0 or height < 4:
        return False

    boxes = rl.find_boxes_tolerant(grid)
    if len(boxes) < 2:
        return False

    # Check for containment — at least one box inside another
    for i, outer in enumerate(boxes):
        for j, inner in enumerate(boxes):
            if i == j:
                continue
            if _box_contains(outer, inner):
                return True

    return False


def render_wireframe_svg(source: str) -> str:
    """Render an ASCII wireframe to SVG."""
    grid, width, height = rl.parse_grid(source)

    if not grid or width == 0:
        return rl.fallback_svg(source)

    boxes = rl.find_boxes_tolerant(grid)
    if not boxes:
        return rl.fallback_svg(source)

    # Build containment tree and assign depths
    depths = _compute_depths(boxes)

    # Build child map (which boxes are direct children of which)
    children = _build_children_map(boxes)

    # Extract titles from box borders
    titles = _extract_border_titles(grid, boxes)

    # Detect internal column dividers within boxes
    col_dividers = _detect_column_dividers(grid, boxes)

    # Extract content (text, form elements, list items) from boxes
    # skipping regions claimed by child boxes
    contents = _extract_box_contents(grid, boxes, children, col_dividers)

    # Generate SVG
    return _generate_wireframe_svg(
        grid, boxes, depths, titles, contents, col_dividers, width, height
    )


# ── Containment logic ──────────────────────────────────────────────

def _box_contains(outer: rl.Box, inner: rl.Box) -> bool:
    """Check if outer box fully contains inner box."""
    return (outer.top < inner.top and outer.bottom > inner.bottom and
            outer.left < inner.left and outer.right > inner.right)


def _compute_depths(boxes: list[rl.Box]) -> list[int]:
    """Compute nesting depth for each box (0 = outermost)."""
    depths = [0] * len(boxes)
    for i, box in enumerate(boxes):
        for j, other in enumerate(boxes):
            if i != j and _box_contains(other, box):
                depths[i] += 1
    return depths


def _build_children_map(boxes: list[rl.Box]) -> list[list[int]]:
    """For each box, list the indices of boxes it directly contains."""
    children: list[list[int]] = [[] for _ in boxes]
    for i, outer in enumerate(boxes):
        for j, inner in enumerate(boxes):
            if i != j and _box_contains(outer, inner):
                children[i].append(j)
    return children


# ── Column divider detection ──────────────────────────────────────

def _detect_column_dividers(
    grid: list[list[str]], boxes: list[rl.Box]
) -> list[list[int]]:
    """For each box, find internal vertical column divider positions.

    A column divider exists at column C within a box if:
    - A separator row has a tee char (┬, ┼, ╦, ╬) at column C, OR
    - The bottom border has ┴/╩ at column C, OR
    - The top border has ┬/╦ at column C
    AND the column has │ running through interior rows.
    """
    all_dividers: list[list[int]] = []

    tee_top = frozenset("┬╦+")
    tee_bot = frozenset("┴╩+")
    tee_cross = frozenset("┼╬+")
    vert = rl.VERT_CHARS | frozenset("│║|")

    for box in boxes:
        dividers: list[int] = []

        for c in range(box.left + 1, box.right):
            # Check top border, bottom border, and separator rows for tee chars
            is_divider = False
            top_ch = grid[box.top][c]
            bot_ch = grid[box.bottom][c]

            if top_ch in tee_top or top_ch in tee_cross:
                is_divider = True
            if bot_ch in tee_bot or bot_ch in tee_cross:
                is_divider = True
            for sep_row in box.separators:
                sep_ch = grid[sep_row][c]
                if sep_ch in tee_top | tee_bot | tee_cross:
                    is_divider = True

            if not is_divider:
                continue

            # Verify: column has │ in at least some interior rows
            vert_count = 0
            interior_rows = box.bottom - box.top - 1
            for r in range(box.top + 1, box.bottom):
                if grid[r][c] in vert:
                    vert_count += 1

            if vert_count >= interior_rows * 0.5:
                dividers.append(c)

        all_dividers.append(dividers)

    return all_dividers


# ── Title extraction ───────────────────────────────────────────────

def _extract_border_titles(
    grid: list[list[str]], boxes: list[rl.Box]
) -> list[str | None]:
    """Extract title text from box top borders.

    Pattern: ┌─── Title Text ───┐ or +--- Title ---+
    """
    titles: list[str | None] = []

    for box in boxes:
        row = box.top
        text_chars: list[str] = []

        for c in range(box.left + 1, box.right):
            ch = grid[row][c]
            if ch in rl.HORIZ_CHARS or ch in rl.TEE_CHARS:
                continue
            if ch == ' ' and not text_chars:
                continue  # skip leading spaces
            text_chars.append(ch)

        title_text = "".join(text_chars).strip()
        titles.append(title_text if title_text else None)

    return titles


# ── Content extraction ─────────────────────────────────────────────

class _ContentItem:
    """A content element inside a wireframe box."""

    def __init__(
        self,
        row: int,
        col: int,
        text: str,
        kind: str = "text",  # "text", "input", "checkbox", "radio", "list"
        checked: bool = False,
    ):
        self.row = row
        self.col = col
        self.text = text
        self.kind = kind
        self.checked = checked


def _extract_box_contents(
    grid: list[list[str]],
    boxes: list[rl.Box],
    children: list[list[int]],
    col_dividers: list[list[int]],
) -> list[list[_ContentItem]]:
    """Extract content items from inside each box.

    Skips rows that fall within child boxes to prevent duplicate rendering.
    When column dividers exist, splits content into per-panel segments
    so that text in different columns renders at correct positions.
    """
    all_contents: list[list[_ContentItem]] = []

    for i, box in enumerate(boxes):
        items: list[_ContentItem] = []
        dividers = col_dividers[i] if i < len(col_dividers) else []

        # Build column panels: ranges of columns between dividers
        panel_starts = [box.left + 1]
        panel_ends = []
        for d in dividers:
            panel_ends.append(d)
            panel_starts.append(d + 1)
        panel_ends.append(box.right)

        # Build regions claimed by child boxes (for per-panel overlap check)
        child_regions: list[tuple[int, int, int, int]] = []
        for ci in children[i]:
            child = boxes[ci]
            child_regions.append((child.top, child.bottom, child.left, child.right))

        sep_set = set(box.separators)
        for r in range(box.top + 1, box.bottom):
            if r in sep_set:
                continue

            # Process each panel (column region) separately
            for ps, pe in zip(panel_starts, panel_ends):
                # Skip if this panel region overlaps a child box on this row
                skip = False
                for ct, cb, cl, cr in child_regions:
                    if ct <= r <= cb and cl < pe and cr > ps:
                        skip = True
                        break
                if skip:
                    continue

                row_text = ""
                for c in range(ps, pe):
                    ch = grid[r][c]
                    if ch in rl.VERT_CHARS or ch in rl.CORNER_CHARS or ch in rl.TEE_CHARS:
                        row_text += " "
                    else:
                        row_text += ch

                if not row_text.strip():
                    continue

                _parse_content_row(items, r, ps, row_text)

        all_contents.append(items)

    return all_contents


def _parse_content_row(
    items: list[_ContentItem], row: int, base_col: int, text: str
) -> None:
    """Parse a content row for form elements and text labels.

    Detects form elements (checkbox, radio, input) and list markers.
    For rows with form elements, also captures surrounding text as labels.
    """
    # Track character ranges consumed by form elements
    consumed_ranges: list[tuple[int, int]] = []

    i = 0
    while i < len(text):
        # Checkbox: [x] or [ ]
        if text[i:i + 3] in ("[x]", "[ ]", "[X]"):
            checked = text[i + 1].lower() == "x"
            items.append(_ContentItem(
                row=row, col=base_col + i, text=text[i:i + 3],
                kind="checkbox", checked=checked,
            ))
            consumed_ranges.append((i, i + 3))
            i += 3
            continue

        # Radio: (*) or ( )
        if text[i:i + 3] in ("(*)", "( )"):
            checked = text[i + 1] == "*"
            items.append(_ContentItem(
                row=row, col=base_col + i, text=text[i:i + 3],
                kind="radio", checked=checked,
            ))
            consumed_ranges.append((i, i + 3))
            i += 3
            continue

        # Text input: [___] (underscores) or [ text... ] (placeholder with padding)
        if text[i] == "[" and i + 3 < len(text):
            end = text.find("]", i + 1)
            if end > i + 2:
                inner = text[i + 1:end]
                # Classic blank input: [____]
                is_blank_input = inner.replace("_", "").strip() == "" and "_" in inner
                # Placeholder input: [ Search...     ] — text with trailing spaces, total width > 5
                is_placeholder = (
                    end - i > 5 and inner.strip() and
                    len(inner) - len(inner.rstrip()) >= 2  # trailing padding
                )
                if is_blank_input or is_placeholder:
                    items.append(_ContentItem(
                        row=row, col=base_col + i, text=text[i:end + 1],
                        kind="input",
                    ))
                    consumed_ranges.append((i, end + 1))
                    i = end + 1
                    continue

        i += 1

    # No form elements found — check for list markers or plain text
    if not consumed_ranges:
        stripped = text.lstrip()
        leading = len(text) - len(stripped)
        if stripped[:2] in ("> ", "* ", "- "):
            rest = stripped[2:].strip()
            if rest:
                items.append(_ContentItem(
                    row=row, col=base_col + leading, text=rest,
                    kind="list",
                ))
                return

        # Split on runs of 3+ spaces to preserve column layout
        import re
        segments = re.split(r'(\s{3,})', text)
        pos = 0
        for seg in segments:
            if not seg.strip():
                pos += len(seg)
                continue
            seg_stripped = seg.strip()
            seg_offset = text.index(seg_stripped, pos)
            items.append(_ContentItem(
                row=row, col=base_col + seg_offset, text=seg_stripped,
                kind="text",
            ))
            pos = seg_offset + len(seg_stripped)
        return

    # Has form elements — extract remaining text segments as labels
    consumed = set()
    for start, end in consumed_ranges:
        consumed.update(range(start, end))

    seg_start = None
    segment = ""
    for ci in range(len(text)):
        if ci not in consumed:
            if seg_start is None:
                seg_start = ci
            segment += text[ci]
        else:
            if segment.strip():
                items.append(_ContentItem(
                    row=row, col=base_col + (seg_start or 0),
                    text=segment.strip(), kind="text",
                ))
            segment = ""
            seg_start = None
    if segment.strip():
        items.append(_ContentItem(
            row=row, col=base_col + (seg_start or 0),
            text=segment.strip(), kind="text",
        ))


# ── SVG generation ─────────────────────────────────────────────────

def _generate_wireframe_svg(
    grid: list[list[str]],
    boxes: list[rl.Box],
    depths: list[int],
    titles: list[str | None],
    contents: list[list[_ContentItem]],
    col_dividers: list[list[int]],
    width: int,
    height: int,
) -> str:
    """Generate SVG from wireframe structure."""
    theme = DEFAULT_THEME

    # Compute tight bounds
    max_right = max(b.right for b in boxes)
    max_bottom = max(b.bottom for b in boxes)
    svg_w = (max_right + 2) * rl.CHAR_W + rl.PAD_X * 2
    svg_h = (max_bottom + 2) * rl.CHAR_H + rl.PAD_Y * 2

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_w:.0f}" height="{svg_h:.0f}" '
        f'class="mdview-diagram">',
        theme.svg_css(),
        _wireframe_css(theme),
        f'  <rect class="bg" x="0" y="0" width="{svg_w:.0f}" height="{svg_h:.0f}" rx="6"/>',
    ]

    # Sort boxes by depth (render outermost first so inner boxes overlay)
    box_order = sorted(range(len(boxes)), key=lambda i: depths[i])

    for idx in box_order:
        box = boxes[idx]
        depth = depths[idx]
        title = titles[idx]
        box_contents = contents[idx]

        # Box rectangle with depth-based fill
        x = rl.PAD_X + box.left * rl.CHAR_W
        y = rl.PAD_Y + box.top * rl.CHAR_H
        w = (box.right - box.left) * rl.CHAR_W
        h = (box.bottom - box.top) * rl.CHAR_H

        depth_class = f"wf-depth-{min(depth, 3)}"
        parts.append(
            f'  <rect class="wf-box {depth_class}" x="{x:.1f}" y="{y:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" rx="4"/>'
        )

        # Separators (horizontal)
        for sep_row in box.separators:
            sy = rl.PAD_Y + sep_row * rl.CHAR_H + rl.CHAR_H * 0.5
            parts.append(
                f'  <line class="wf-separator" '
                f'x1="{x:.1f}" y1="{sy:.1f}" '
                f'x2="{x + w:.1f}" y2="{sy:.1f}"/>'
            )

        # Column dividers (vertical)
        dividers = col_dividers[idx] if idx < len(col_dividers) else []
        # Find the vertical extent: from first separator (or top+1) to bottom
        div_top_row = box.separators[0] if box.separators else box.top
        for div_col in dividers:
            dx = rl.PAD_X + div_col * rl.CHAR_W + rl.CHAR_W * 0.5
            dy1 = rl.PAD_Y + div_top_row * rl.CHAR_H + rl.CHAR_H * 0.5
            dy2 = rl.PAD_Y + box.bottom * rl.CHAR_H + rl.CHAR_H * 0.5
            parts.append(
                f'  <line class="wf-separator" '
                f'x1="{dx:.1f}" y1="{dy1:.1f}" '
                f'x2="{dx:.1f}" y2="{dy2:.1f}"/>'
            )

        # Title on border
        if title:
            tx = x + 12  # small offset from left edge
            ty = y + 1  # sit on the border
            escaped = html_mod.escape(title)
            parts.append(
                f'  <rect class="wf-title-bg" x="{tx - 4:.1f}" y="{ty - 9:.1f}" '
                f'width="{len(title) * 7.2 + 8:.1f}" height="14" rx="2"/>'
            )
            parts.append(
                f'  <text class="wf-title" x="{tx:.1f}" y="{ty:.1f}">{escaped}</text>'
            )

        # Content items
        for item in box_contents:
            # Skip if this text is the same as the title (already rendered)
            if title and item.kind == "text" and item.text.strip() == title.strip():
                continue

            iy = rl.PAD_Y + item.row * rl.CHAR_H + rl.CHAR_H * 0.75
            ix = rl.PAD_X + item.col * rl.CHAR_W

            if item.kind == "input":
                input_w = len(item.text) * rl.CHAR_W
                input_h = rl.CHAR_H * 0.8
                iy_rect = rl.PAD_Y + item.row * rl.CHAR_H + rl.CHAR_H * 0.1
                parts.append(
                    f'  <rect class="wf-input" x="{ix:.1f}" y="{iy_rect:.1f}" '
                    f'width="{input_w:.1f}" height="{input_h:.1f}" rx="3"/>'
                )
            elif item.kind == "checkbox":
                cb_size = 10
                cb_x = ix + 2
                cb_y = iy - cb_size + 2
                parts.append(
                    f'  <rect class="wf-checkbox" x="{cb_x:.1f}" y="{cb_y:.1f}" '
                    f'width="{cb_size}" height="{cb_size}" rx="2"/>'
                )
                if item.checked:
                    parts.append(
                        f'  <polyline class="wf-check" points="'
                        f'{cb_x + 2:.1f},{cb_y + 5:.1f} '
                        f'{cb_x + 4:.1f},{cb_y + 8:.1f} '
                        f'{cb_x + 8:.1f},{cb_y + 2:.1f}"/>'
                    )
            elif item.kind == "radio":
                cr = 5
                cx = ix + cr + 2
                cy = iy - cr + 2
                parts.append(
                    f'  <circle class="wf-radio" cx="{cx:.1f}" cy="{cy:.1f}" r="{cr}"/>'
                )
                if item.checked:
                    parts.append(
                        f'  <circle class="wf-radio-fill" cx="{cx:.1f}" cy="{cy:.1f}" r="3"/>'
                    )
            elif item.kind == "list":
                bx = ix + 4
                by = iy - 3
                parts.append(
                    f'  <circle class="wf-bullet" cx="{bx:.1f}" cy="{by:.1f}" r="2.5"/>'
                )
                escaped = html_mod.escape(item.text)
                parts.append(
                    f'  <text class="wf-text" x="{ix + 12:.1f}" y="{iy:.1f}">{escaped}</text>'
                )
            else:
                # Plain text — left-aligned at grid position
                escaped = html_mod.escape(item.text)
                parts.append(
                    f'  <text class="wf-text" x="{ix:.1f}" y="{iy:.1f}">{escaped}</text>'
                )

    parts.append("</svg>")
    return "\n".join(parts)


def _wireframe_css(theme: DEFAULT_THEME.__class__) -> str:
    """Generate wireframe-specific CSS."""
    d = theme.dark
    l = theme.light
    return f"""  <style>
    .mdview-diagram .wf-box {{ stroke: {d.border}; stroke-width: 1.5; }}
    .mdview-diagram .wf-depth-0 {{ fill: {d.bg}; }}
    .mdview-diagram .wf-depth-1 {{ fill: {d.bg_secondary}; fill-opacity: 0.6; }}
    .mdview-diagram .wf-depth-2 {{ fill: {d.bg_secondary}; fill-opacity: 0.8; }}
    .mdview-diagram .wf-depth-3 {{ fill: {d.bg_secondary}; }}
    .mdview-diagram .wf-separator {{ stroke: {d.border}; stroke-width: 1; stroke-opacity: 0.5; }}
    .mdview-diagram .wf-title {{ fill: {d.header_text}; font-weight: 600; font-size: 12px; }}
    .mdview-diagram .wf-title-bg {{ fill: {d.bg}; fill-opacity: 0.9; }}
    .mdview-diagram .wf-text {{ fill: {d.fg}; }}
    .mdview-diagram .wf-input {{ fill: none; stroke: {d.muted}; stroke-width: 1; stroke-dasharray: 3,2; }}
    .mdview-diagram .wf-checkbox {{ fill: none; stroke: {d.border}; stroke-width: 1.5; }}
    .mdview-diagram .wf-check {{ fill: none; stroke: {d.header_text}; stroke-width: 2; }}
    .mdview-diagram .wf-radio {{ fill: none; stroke: {d.border}; stroke-width: 1.5; }}
    .mdview-diagram .wf-radio-fill {{ fill: {d.arrow}; }}
    .mdview-diagram .wf-bullet {{ fill: {d.arrow}; }}
    @media (prefers-color-scheme: light) {{
      .mdview-diagram .wf-box {{ stroke: {l.border}; }}
      .mdview-diagram .wf-depth-0 {{ fill: {l.bg}; }}
      .mdview-diagram .wf-depth-1 {{ fill: {l.bg_secondary}; fill-opacity: 0.4; }}
      .mdview-diagram .wf-depth-2 {{ fill: {l.bg_secondary}; fill-opacity: 0.6; }}
      .mdview-diagram .wf-depth-3 {{ fill: {l.bg_secondary}; }}
      .mdview-diagram .wf-separator {{ stroke: {l.border}; }}
      .mdview-diagram .wf-title {{ fill: {l.header_text}; }}
      .mdview-diagram .wf-title-bg {{ fill: {l.bg}; }}
      .mdview-diagram .wf-text {{ fill: {l.fg}; }}
      .mdview-diagram .wf-input {{ stroke: {l.muted}; }}
      .mdview-diagram .wf-checkbox {{ stroke: {l.border}; }}
      .mdview-diagram .wf-check {{ stroke: {l.header_text}; }}
      .mdview-diagram .wf-radio {{ stroke: {l.border}; }}
      .mdview-diagram .wf-radio-fill {{ fill: {l.arrow}; }}
      .mdview-diagram .wf-bullet {{ fill: {l.arrow}; }}
    }}
  </style>"""
