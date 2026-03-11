"""Native ASCII box diagram → SVG renderer.

Renders AI-generated box diagrams directly to SVG without external APIs.
Handles the patterns that AI tools (Claude Code, Cursor, Copilot) produce:
- Box layouts with ┌─┐│└─┘ or +---+|+---+ borders
- Text content inside boxes (preserved exactly)
- Horizontal separators (├─┤ or +---+)
- Section headers and body text

Why not svgbob/ditaa?
- svgbob interprets individual characters as drawing primitives
  ('v' becomes arrow, '/' becomes diagonal, '--' becomes line)
- ditaa requires specific markup and doesn't handle Unicode
- Both fail on AI-generated content with mixed text and borders

This renderer parses structure first (find boxes, extract text),
then renders clean SVG. Text is always text, lines are always lines.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field


# Character sets for box detection
_CORNER_CHARS = set("┌┐└┘╔╗╚╝+")
_HORIZ_CHARS = set("─═-")
_VERT_CHARS = set("│║|")
_TEE_CHARS = set("├┤┬┴┼╠╣╦╩╬+")
_BOX_CHARS = _CORNER_CHARS | _HORIZ_CHARS | _VERT_CHARS | _TEE_CHARS


@dataclass
class _Box:
    """A detected box region in the ASCII art."""
    top: int        # row of top border
    left: int       # col of left border
    bottom: int     # row of bottom border
    right: int      # col of right border
    separators: list[int] = field(default_factory=list)  # rows of internal ├─┤ separators


@dataclass
class _TextSpan:
    """A text segment inside a box."""
    row: int
    col: int
    text: str
    section: int = 0  # which section (0 = first, separated by ├─┤)


def has_box_structure(source: str) -> bool:
    """Check if source contains detectable box structures.

    Used by the diagram router to decide between native box rendering
    and svgbob fallback.
    """
    lines = source.split("\n")
    max_len = max((len(l) for l in lines), default=0)
    if max_len == 0:
        return False
    grid = [list(l.ljust(max_len)) for l in lines]
    return len(_find_boxes(grid)) > 0


def render_box_svg(source: str) -> str:
    """Render an ASCII box diagram to SVG.

    Args:
        source: ASCII art with box-drawing characters.

    Returns:
        SVG string.
    """
    lines = source.split("\n")
    # Pad lines to same length
    max_len = max((len(l) for l in lines), default=0)
    grid = [list(l.ljust(max_len)) for l in lines]

    if not grid or max_len == 0:
        return _fallback_svg(source)

    boxes = _find_boxes(grid)
    if not boxes:
        return _fallback_svg(source)

    texts = _extract_texts(grid, boxes)

    return _generate_svg(boxes, texts, max_len, len(lines))


def _find_boxes(grid: list[list[str]]) -> list[_Box]:
    """Find rectangular boxes defined by corner + border characters."""
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    boxes: list[_Box] = []

    # Find top-left corners and trace boxes
    for r in range(rows):
        for c in range(cols):
            ch = grid[r][c]
            if ch not in _CORNER_CHARS:
                continue

            # Check if this is a top-left corner:
            # - has horizontal border going right
            # - has vertical border going down
            if c + 1 >= cols or grid[r][c + 1] not in _HORIZ_CHARS:
                continue
            if r + 1 >= rows or grid[r + 1][c] not in (_VERT_CHARS | _TEE_CHARS):
                continue

            # Trace right to find top-right corner
            right = _trace_horizontal(grid, r, c + 1, cols)
            if right is None:
                continue

            # Trace down to find bottom-left corner
            bottom = _trace_vertical(grid, c, r + 1, rows)
            if bottom is None:
                continue

            # Verify bottom-right corner exists
            if grid[bottom][right] not in _CORNER_CHARS:
                continue

            # Verify bottom border exists
            if not _has_horizontal_border(grid, bottom, c, right):
                continue

            # Verify right border exists
            if not _has_vertical_border(grid, right, r, bottom):
                continue

            # Find internal separators (├─┤ lines)
            separators = []
            for sr in range(r + 1, bottom):
                if grid[sr][c] in _TEE_CHARS and grid[sr][right] in _TEE_CHARS:
                    if _has_horizontal_border(grid, sr, c, right):
                        separators.append(sr)

            # Check this box isn't a duplicate or subset
            is_new = True
            for existing in boxes:
                if (existing.top == r and existing.left == c and
                        existing.bottom == bottom and existing.right == right):
                    is_new = False
                    break
            if is_new:
                boxes.append(_Box(
                    top=r, left=c, bottom=bottom, right=right,
                    separators=separators,
                ))

    return boxes


def _trace_horizontal(grid: list[list[str]], row: int, start_col: int, max_col: int) -> int | None:
    """Trace horizontal border right from start_col, return column of corner/tee."""
    for c in range(start_col, max_col):
        ch = grid[row][c]
        if ch in _CORNER_CHARS:
            return c
        if ch not in _HORIZ_CHARS and ch != ' ':
            # Allow spaces in borders (some AI output has gaps)
            return None
    return None


def _trace_vertical(grid: list[list[str]], col: int, start_row: int, max_row: int) -> int | None:
    """Trace vertical border down from start_row, return row of corner/tee."""
    for r in range(start_row, max_row):
        ch = grid[r][col]
        if ch in _CORNER_CHARS:
            return r
        if ch not in (_VERT_CHARS | _TEE_CHARS):
            return None
    return None


def _has_horizontal_border(grid: list[list[str]], row: int, left: int, right: int) -> bool:
    """Check if row has a continuous horizontal border between left and right."""
    for c in range(left + 1, right):
        if grid[row][c] not in (_HORIZ_CHARS | {' '}):
            return False
    return True


def _has_vertical_border(grid: list[list[str]], col: int, top: int, bottom: int) -> bool:
    """Check if col has a continuous vertical border between top and bottom."""
    for r in range(top + 1, bottom):
        if grid[r][col] not in (_VERT_CHARS | _TEE_CHARS):
            return False
    return True


def _extract_texts(grid: list[list[str]], boxes: list[_Box]) -> list[_TextSpan]:
    """Extract text content from inside boxes."""
    texts: list[_TextSpan] = []

    for box in boxes:
        # Determine sections (separated by ├─┤ lines)
        section_breaks = [box.top] + box.separators + [box.bottom]

        for section_idx in range(len(section_breaks) - 1):
            section_top = section_breaks[section_idx]
            section_bottom = section_breaks[section_idx + 1]

            for r in range(section_top + 1, section_bottom):
                # Extract text between left and right borders
                content = ""
                for c in range(box.left + 1, box.right):
                    content += grid[r][c]

                content = content.rstrip()
                if content.strip():
                    # Find actual text start (skip leading spaces but preserve indent)
                    texts.append(_TextSpan(
                        row=r,
                        col=box.left + 1,
                        text=content,
                        section=section_idx,
                    ))

    return texts


def _generate_svg(
    boxes: list[_Box],
    texts: list[_TextSpan],
    width: int,
    height: int,
) -> str:
    """Generate SVG from parsed boxes and text."""
    # Character cell dimensions
    char_w = 8.4
    char_h = 16
    pad_x = 12
    pad_y = 8

    svg_w = width * char_w + pad_x * 2
    svg_h = height * char_h + pad_y * 2

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_w:.0f}" height="{svg_h:.0f}" '
        f'class="mdview-box">'
    )

    # Style
    parts.append("""
  <style>
    .mdview-box { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-box .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-box .box-separator { stroke: #7aa2f7; stroke-width: 1; stroke-dasharray: none; }
    .mdview-box .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-box .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-box .box-bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-box .box-border { stroke: #2e7de9; }
      .mdview-box .box-separator { stroke: #2e7de9; }
      .mdview-box .box-text { fill: #343b58; }
      .mdview-box .box-header { fill: #587539; }
      .mdview-box .box-bg { fill: #f8f8fc; }
    }
  </style>""")

    # Background
    parts.append(f'  <rect class="box-bg" x="0" y="0" width="{svg_w:.0f}" height="{svg_h:.0f}" rx="6"/>')

    # Render boxes as rounded rectangles
    for box in boxes:
        x = pad_x + box.left * char_w
        y = pad_y + box.top * char_h
        w = (box.right - box.left) * char_w
        h = (box.bottom - box.top) * char_h

        parts.append(
            f'  <rect class="box-border" x="{x:.1f}" y="{y:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" rx="4"/>'
        )

        # Render separators
        for sep_row in box.separators:
            sy = pad_y + sep_row * char_h + char_h * 0.5
            parts.append(
                f'  <line class="box-separator" '
                f'x1="{x:.1f}" y1="{sy:.1f}" '
                f'x2="{x + w:.1f}" y2="{sy:.1f}"/>'
            )

    # Render text
    for span in texts:
        tx = pad_x + span.col * char_w
        ty = pad_y + span.row * char_h + char_h * 0.75  # baseline offset

        # First line in a section = header style
        css_class = "box-header" if span.section == 0 and span.text.strip() and not span.text.startswith("  ") else "box-text"

        # Check if it's the first text in its section for this box
        # (simplified: non-indented text in section 0 = header)
        escaped = html.escape(span.text)
        parts.append(
            f'  <text class="{css_class}" x="{tx:.1f}" y="{ty:.1f}">{escaped}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def _fallback_svg(source: str) -> str:
    """Render source as plain monospace text in SVG (fallback)."""
    lines = source.split("\n")
    char_w = 8.4
    char_h = 16
    pad = 16
    width = max((len(l) for l in lines), default=20) * char_w + pad * 2
    height = len(lines) * char_h + pad * 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" class="mdview-box">',
        '  <style>.mdview-box { font-family: monospace; font-size: 13px; } .mdview-box text { fill: #a9b1d6; white-space: pre; } .mdview-box .box-bg { fill: #1a1b26; }</style>',
        f'  <rect class="box-bg" x="0" y="0" width="{width:.0f}" height="{height:.0f}" rx="6"/>',
    ]
    for i, line in enumerate(lines):
        y = pad + i * char_h + char_h * 0.75
        parts.append(f'  <text x="{pad}" y="{y:.1f}">{html.escape(line)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)
