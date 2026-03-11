"""Shared rendering primitives for ASCII diagram → SVG conversion.

Grid operations, structure detection, and SVG generation utilities
shared across all diagram renderers (box, flow, table, sequence).
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field


# ── Character sets ──────────────────────────────────────────────────

CORNER_CHARS = frozenset("┌┐└┘╔╗╚╝+")
HORIZ_CHARS = frozenset("─═-")
VERT_CHARS = frozenset("│║|")
TEE_CHARS = frozenset("├┤┬┴┼╠╣╦╩╬+")
ARROW_HEADS_RIGHT = frozenset(">→▶")
ARROW_HEADS_LEFT = frozenset("<←◀")
ARROW_HEADS_DOWN = frozenset("▼↓")
ARROW_HEADS_UP = frozenset("▲↑^")
ALL_ARROW_HEADS = ARROW_HEADS_RIGHT | ARROW_HEADS_LEFT | ARROW_HEADS_DOWN | ARROW_HEADS_UP


# ── Data classes ────────────────────────────────────────────────────

@dataclass
class Box:
    """A detected box region in the ASCII art."""
    top: int
    left: int
    bottom: int
    right: int
    separators: list[int] = field(default_factory=list)

    @property
    def center_row(self) -> float:
        return (self.top + self.bottom) / 2

    @property
    def center_col(self) -> float:
        return (self.left + self.right) / 2

    @property
    def mid_top(self) -> tuple[float, int]:
        """Midpoint of top edge."""
        return (self.top, round((self.left + self.right) / 2))

    @property
    def mid_bottom(self) -> tuple[float, int]:
        """Midpoint of bottom edge."""
        return (self.bottom, round((self.left + self.right) / 2))

    @property
    def mid_left(self) -> tuple[int, float]:
        """Midpoint of left edge."""
        return (round((self.top + self.bottom) / 2), self.left)

    @property
    def mid_right(self) -> tuple[int, float]:
        """Midpoint of right edge."""
        return (round((self.top + self.bottom) / 2), self.right)


@dataclass
class TextSpan:
    """A text segment inside a box."""
    row: int
    col: int
    text: str
    section: int = 0


@dataclass
class Arrow:
    """A detected arrow/connection between boxes."""
    points: list[tuple[int, int]]  # (row, col) waypoints
    direction: str  # 'right', 'left', 'down', 'up'
    label: str | None = None
    from_box: int | None = None  # index into boxes list
    to_box: int | None = None


# ── Grid operations ─────────────────────────────────────────────────

def parse_grid(source: str) -> tuple[list[list[str]], int, int]:
    """Parse source string into a 2D character grid.

    Returns (grid, width, height).
    """
    lines = source.split("\n")
    max_len = max((len(l) for l in lines), default=0)
    grid = [list(l.ljust(max_len)) for l in lines]
    return grid, max_len, len(lines)


def char_at(grid: list[list[str]], r: int, c: int) -> str:
    """Safe character lookup with bounds checking."""
    if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
        return grid[r][c]
    return ""


# ── Box detection ───────────────────────────────────────────────────

def find_boxes(grid: list[list[str]]) -> list[Box]:
    """Find rectangular boxes defined by corner + border characters."""
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    boxes: list[Box] = []

    for r in range(rows):
        for c in range(cols):
            ch = grid[r][c]
            if ch not in CORNER_CHARS:
                continue

            # Must be a top-left corner: horiz right, vert down
            if c + 1 >= cols or grid[r][c + 1] not in HORIZ_CHARS:
                continue
            if r + 1 >= rows or grid[r + 1][c] not in (VERT_CHARS | TEE_CHARS):
                continue

            right = _trace_horiz(grid, r, c + 1, cols)
            if right is None:
                continue

            bottom = _trace_vert(grid, c, r + 1, rows)
            if bottom is None:
                continue

            if grid[bottom][right] not in CORNER_CHARS:
                continue
            if not has_horiz_border(grid, bottom, c, right):
                continue
            if not has_vert_border(grid, right, r, bottom):
                continue

            separators = []
            for sr in range(r + 1, bottom):
                if grid[sr][c] in TEE_CHARS and grid[sr][right] in TEE_CHARS:
                    if has_horiz_border(grid, sr, c, right):
                        separators.append(sr)

            is_new = True
            for existing in boxes:
                if (existing.top == r and existing.left == c and
                        existing.bottom == bottom and existing.right == right):
                    is_new = False
                    break
            if is_new:
                boxes.append(Box(
                    top=r, left=c, bottom=bottom, right=right,
                    separators=separators,
                ))

    return boxes


def _trace_horiz(grid: list[list[str]], row: int, start_col: int, max_col: int) -> int | None:
    """Trace horizontal border right, return column of corner/tee."""
    for c in range(start_col, max_col):
        ch = grid[row][c]
        if ch in CORNER_CHARS:
            return c
        if ch not in HORIZ_CHARS and ch != ' ':
            return None
    return None


def _trace_vert(grid: list[list[str]], col: int, start_row: int, max_row: int) -> int | None:
    """Trace vertical border down, return row of corner/tee."""
    for r in range(start_row, max_row):
        ch = grid[r][col]
        if ch in CORNER_CHARS:
            return r
        if ch not in (VERT_CHARS | TEE_CHARS):
            return None
    return None


def has_horiz_border(grid: list[list[str]], row: int, left: int, right: int) -> bool:
    """Check if row has a continuous horizontal border between left and right."""
    for c in range(left + 1, right):
        if grid[row][c] not in (HORIZ_CHARS | frozenset(' ')):
            return False
    return True


def has_vert_border(grid: list[list[str]], col: int, top: int, bottom: int) -> bool:
    """Check if col has a continuous vertical border between top and bottom."""
    for r in range(top + 1, bottom):
        if grid[r][col] not in (VERT_CHARS | TEE_CHARS):
            return False
    return True


# ── Text extraction ─────────────────────────────────────────────────

def extract_box_texts(grid: list[list[str]], boxes: list[Box]) -> list[TextSpan]:
    """Extract text content from inside boxes."""
    texts: list[TextSpan] = []

    for box in boxes:
        section_breaks = [box.top] + box.separators + [box.bottom]

        for section_idx in range(len(section_breaks) - 1):
            section_top = section_breaks[section_idx]
            section_bottom = section_breaks[section_idx + 1]

            for r in range(section_top + 1, section_bottom):
                content = ""
                for c in range(box.left + 1, box.right):
                    content += grid[r][c]

                content = content.rstrip()
                if content.strip():
                    texts.append(TextSpan(
                        row=r,
                        col=box.left + 1,
                        text=content,
                        section=section_idx,
                    ))

    return texts


# ── Arrow detection ─────────────────────────────────────────────────

def find_arrows(grid: list[list[str]], boxes: list[Box]) -> list[Arrow]:
    """Find arrow connections between boxes.

    Detects horizontal and vertical arrow segments, traces their paths,
    and connects them to the nearest box edges.
    """
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    used: set[tuple[int, int]] = set()
    arrows: list[Arrow] = []

    # Mark all box border cells as used (not part of arrows)
    for box in boxes:
        for c in range(box.left, box.right + 1):
            used.add((box.top, c))
            used.add((box.bottom, c))
        for r in range(box.top, box.bottom + 1):
            used.add((r, box.left))
            used.add((r, box.right))
        for sep in box.separators:
            for c in range(box.left, box.right + 1):
                used.add((sep, c))

    # Scan for horizontal arrow segments
    for r in range(rows):
        c = 0
        while c < cols:
            if (r, c) in used:
                c += 1
                continue

            ch = grid[r][c]
            # Start of horizontal segment: ─, ═, -, or arrow head
            if ch in HORIZ_CHARS or ch in ARROW_HEADS_RIGHT:
                arrow = _trace_horiz_arrow(grid, r, c, cols, used, boxes)
                if arrow:
                    arrows.append(arrow)
                    for pr, pc in arrow.points:
                        used.add((pr, pc))
                    c = arrow.points[-1][1] + 1
                    continue
            c += 1

    # Scan for vertical arrow segments
    for c in range(cols):
        r = 0
        while r < rows:
            if (r, c) in used:
                r += 1
                continue

            ch = grid[r][c]
            if ch in VERT_CHARS or ch in ARROW_HEADS_DOWN:
                arrow = _trace_vert_arrow(grid, r, c, rows, used, boxes)
                if arrow:
                    arrows.append(arrow)
                    for pr, pc in arrow.points:
                        used.add((pr, pc))
                    r = arrow.points[-1][0] + 1
                    continue
            r += 1

    return arrows


def _trace_horiz_arrow(
    grid: list[list[str]],
    row: int,
    start_col: int,
    max_col: int,
    used: set[tuple[int, int]],
    boxes: list[Box],
) -> Arrow | None:
    """Trace a horizontal arrow segment and identify direction."""
    points: list[tuple[int, int]] = []
    direction = "right"  # default

    # Check for left arrowhead at start
    if grid[row][start_col] in ARROW_HEADS_LEFT:
        direction = "left"

    c = start_col
    while c < max_col:
        if (row, c) in used:
            break
        ch = grid[row][c]
        if ch in HORIZ_CHARS or ch in ARROW_HEADS_RIGHT or ch in ARROW_HEADS_LEFT:
            points.append((row, c))
            if ch in ARROW_HEADS_RIGHT:
                direction = "right"
                c += 1
                break  # arrowhead is the end
            c += 1
        elif ch == ' ':
            # Allow small gaps (1-2 spaces) in arrows
            if c + 1 < max_col and grid[row][c + 1] in (HORIZ_CHARS | ARROW_HEADS_RIGHT):
                points.append((row, c))
                c += 1
            else:
                break
        else:
            break

    if len(points) < 2:
        return None

    # Find connected boxes
    from_box = _find_adjacent_box(boxes, row, points[0][1], "left")
    to_box = _find_adjacent_box(boxes, row, points[-1][1], "right")

    # Extract label: text above or below the arrow
    label = _find_arrow_label(grid, row, points[0][1], points[-1][1])

    return Arrow(
        points=points,
        direction=direction,
        label=label,
        from_box=from_box,
        to_box=to_box,
    )


def _trace_vert_arrow(
    grid: list[list[str]],
    start_row: int,
    col: int,
    max_row: int,
    used: set[tuple[int, int]],
    boxes: list[Box],
) -> Arrow | None:
    """Trace a vertical arrow segment and identify direction."""
    points: list[tuple[int, int]] = []
    direction = "down"  # default

    if grid[start_row][col] in ARROW_HEADS_UP:
        direction = "up"

    r = start_row
    while r < max_row:
        if (r, col) in used:
            break
        ch = grid[r][col]
        if ch in VERT_CHARS or ch in ARROW_HEADS_DOWN or ch in ARROW_HEADS_UP:
            points.append((r, col))
            if ch in ARROW_HEADS_DOWN:
                direction = "down"
                r += 1
                break
            r += 1
        elif ch == ' ':
            if r + 1 < max_row and grid[r + 1][col] in (VERT_CHARS | ARROW_HEADS_DOWN):
                points.append((r, col))
                r += 1
            else:
                break
        else:
            break

    if len(points) < 2:
        return None

    from_box = _find_adjacent_box(boxes, points[0][0], col, "above")
    to_box = _find_adjacent_box(boxes, points[-1][0], col, "below")

    label = _find_arrow_label_vert(grid, col, points[0][0], points[-1][0])

    return Arrow(
        points=points,
        direction=direction,
        label=label,
        from_box=from_box,
        to_box=to_box,
    )


def _find_adjacent_box(boxes: list[Box], row: int, col: int, side: str) -> int | None:
    """Find the box adjacent to a point on the given side."""
    for i, box in enumerate(boxes):
        if side == "left":
            # Arrow starts just right of this box's right edge
            if box.right == col - 1 and box.top <= row <= box.bottom:
                return i
        elif side == "right":
            # Arrow ends just left of this box's left edge
            if box.left == col + 1 and box.top <= row <= box.bottom:
                return i
        elif side == "above":
            # Arrow starts just below this box's bottom edge
            if box.bottom == row - 1 and box.left <= col <= box.right:
                return i
        elif side == "below":
            # Arrow ends just above this box's top edge
            if box.top == row + 1 and box.left <= col <= box.right:
                return i
    return None


def _find_arrow_label(
    grid: list[list[str]], row: int, start_col: int, end_col: int
) -> str | None:
    """Find text label above or below a horizontal arrow."""
    rows = len(grid)

    # Check row above
    if row > 0:
        label = _extract_text_near(grid, row - 1, start_col, end_col)
        if label:
            return label

    # Check row below
    if row + 1 < rows:
        label = _extract_text_near(grid, row + 1, start_col, end_col)
        if label:
            return label

    return None


def _find_arrow_label_vert(
    grid: list[list[str]], col: int, start_row: int, end_row: int
) -> str | None:
    """Find text label to the left or right of a vertical arrow."""
    cols = len(grid[0]) if grid else 0

    # Check right of arrow
    for r in range(start_row, end_row + 1):
        if col + 2 < cols:
            text = ""
            for c in range(col + 2, min(col + 20, cols)):
                ch = grid[r][c]
                if ch in HORIZ_CHARS | VERT_CHARS | CORNER_CHARS | TEE_CHARS:
                    break
                text += ch
            text = text.strip()
            if text and len(text) > 1:
                return text

    return None


def _extract_text_near(
    grid: list[list[str]], row: int, start_col: int, end_col: int
) -> str | None:
    """Extract text content from a region near an arrow."""
    text = ""
    for c in range(max(0, start_col), min(end_col + 1, len(grid[0]))):
        ch = grid[row][c]
        if ch in HORIZ_CHARS | VERT_CHARS | CORNER_CHARS | TEE_CHARS | ALL_ARROW_HEADS:
            continue
        text += ch
    text = text.strip()
    if text and len(text) > 1:
        return text
    return None


# ── SVG generation helpers ──────────────────────────────────────────

# Character cell dimensions (shared across all renderers)
CHAR_W = 8.4
CHAR_H = 16
PAD_X = 12
PAD_Y = 8

# Theme CSS — shared across all renderers
THEME_CSS = """
  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>"""


def classify_headers(texts: list[TextSpan], boxes: list[Box]) -> set[int]:
    """Return indices of TextSpan entries that are section headers.

    A header is the first text line in section 0 of each box.
    """
    headers: set[int] = set()
    # Group texts by which box they belong to (by row/col containment)
    for box in boxes:
        first_in_section0 = None
        for i, span in enumerate(texts):
            if span.section == 0 and box.left < span.col <= box.right:
                if box.top < span.row < box.bottom:
                    if first_in_section0 is None:
                        first_in_section0 = i
                        headers.add(i)
                        break
    return headers


def svg_open(width: int, height: int) -> str:
    """SVG opening tag with dimensions."""
    svg_w = width * CHAR_W + PAD_X * 2
    svg_h = height * CHAR_H + PAD_Y * 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_w:.0f}" height="{svg_h:.0f}" '
        f'class="mdview-diagram">'
    )


def svg_background(width: int, height: int) -> str:
    """Background rectangle."""
    svg_w = width * CHAR_W + PAD_X * 2
    svg_h = height * CHAR_H + PAD_Y * 2
    return f'  <rect class="bg" x="0" y="0" width="{svg_w:.0f}" height="{svg_h:.0f}" rx="6"/>'


def svg_arrowhead_defs() -> str:
    """SVG <defs> with arrowhead marker.

    One marker, orient=auto-start-reverse: the polygon points right,
    SVG auto-rotates it to match line direction. marker-end places it
    at the end; marker-start flips it for reverse arrows.
    """
    return """  <defs>
    <marker id="arrowhead" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>"""


def svg_rect(box: Box) -> str:
    """Render a box as an SVG rounded rectangle."""
    x = PAD_X + box.left * CHAR_W
    y = PAD_Y + box.top * CHAR_H
    w = (box.right - box.left) * CHAR_W
    h = (box.bottom - box.top) * CHAR_H
    return (
        f'  <rect class="box-border" x="{x:.1f}" y="{y:.1f}" '
        f'width="{w:.1f}" height="{h:.1f}" rx="4"/>'
    )


def svg_separator(box: Box, sep_row: int) -> str:
    """Render a box separator line."""
    x = PAD_X + box.left * CHAR_W
    w = (box.right - box.left) * CHAR_W
    sy = PAD_Y + sep_row * CHAR_H + CHAR_H * 0.5
    return (
        f'  <line class="box-separator" '
        f'x1="{x:.1f}" y1="{sy:.1f}" '
        f'x2="{x + w:.1f}" y2="{sy:.1f}"/>'
    )


def svg_text(span: TextSpan, is_header: bool = False) -> str:
    """Render a text span as SVG text element."""
    tx = PAD_X + span.col * CHAR_W
    ty = PAD_Y + span.row * CHAR_H + CHAR_H * 0.75
    css_class = "box-header" if is_header else "box-text"
    escaped = html.escape(span.text)
    return f'  <text class="{css_class}" x="{tx:.1f}" y="{ty:.1f}">{escaped}</text>'


def svg_arrow(arrow: Arrow) -> list[str]:
    """Render an arrow as SVG line/path with arrowhead marker."""
    if len(arrow.points) < 2:
        return []

    parts: list[str] = []

    # Convert grid coords to SVG coords
    def to_svg(r: int, c: int) -> tuple[float, float]:
        return (PAD_X + c * CHAR_W + CHAR_W / 2, PAD_Y + r * CHAR_H + CHAR_H / 2)

    start = arrow.points[0]
    end = arrow.points[-1]
    x1, y1 = to_svg(*start)
    x2, y2 = to_svg(*end)

    # Determine marker — single "arrowhead" marker with orient="auto-start-reverse"
    # Forward arrows (right, down): marker-end places arrowhead at line endpoint
    # Reverse arrows (left, up): marker-start places flipped arrowhead at line start
    marker = ""
    if arrow.direction in ("right", "down"):
        marker = ' marker-end="url(#arrowhead)"'
    elif arrow.direction in ("left", "up"):
        marker = ' marker-start="url(#arrowhead)"'

    parts.append(
        f'  <line class="arrow-line" x1="{x1:.1f}" y1="{y1:.1f}" '
        f'x2="{x2:.1f}" y2="{y2:.1f}"{marker}/>'
    )

    # Render label if present
    if arrow.label:
        mid_x = (x1 + x2) / 2
        mid_y = min(y1, y2) - 4  # above the arrow
        escaped = html.escape(arrow.label)
        parts.append(
            f'  <text class="arrow-label" x="{mid_x:.1f}" y="{mid_y:.1f}">{escaped}</text>'
        )

    return parts


def fallback_svg(source: str) -> str:
    """Render source as plain monospace text in SVG (fallback)."""
    lines = source.split("\n")
    pad = 16
    width = max((len(l) for l in lines), default=20) * CHAR_W + pad * 2
    height = len(lines) * CHAR_H + pad * 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" class="mdview-diagram">',
        '  <style>.mdview-diagram { font-family: monospace; font-size: 13px; } .mdview-diagram text { fill: #a9b1d6; white-space: pre; } .mdview-diagram .bg { fill: #1a1b26; }</style>',
        f'  <rect class="bg" x="0" y="0" width="{width:.0f}" height="{height:.0f}" rx="6"/>',
    ]
    for i, line in enumerate(lines):
        y = pad + i * CHAR_H + CHAR_H * 0.75
        parts.append(f'  <text x="{pad}" y="{y:.1f}">{html.escape(line)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)
