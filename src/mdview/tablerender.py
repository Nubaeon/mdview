"""ASCII table → SVG renderer.

Renders AI-generated ASCII tables directly to SVG without external APIs.
Handles both Unicode and ASCII table borders:

  ┌──────┬────────┬───────┐     +------+--------+-------+
  │ Name │ Status │ Owner │     | Name | Status | Owner |
  ├──────┼────────┼───────┤     +------+--------+-------+
  │ Auth │ Done   │ Alice │     | Auth | Done   | Alice |
  └──────┴────────┴───────┘     +------+--------+-------+

Structure-first: find grid intersections, trace borders, extract cells.
"""

from __future__ import annotations

from . import renderlib as rl
from .themes import DEFAULT_THEME


def has_table_structure(source: str) -> bool:
    """Check if source contains an ASCII table.

    A table has:
    - At least 2 columns (3+ vertical borders at consistent positions)
    - At least 2 rows (3+ horizontal borders)
    - Grid intersections where horizontal and vertical borders meet
    """
    grid, width, height = rl.parse_grid(source)
    if width == 0 or height < 3:
        return False

    table = _detect_table(grid, width, height)
    return table is not None


def render_table_svg(source: str) -> str:
    """Render an ASCII table to SVG."""
    grid, width, height = rl.parse_grid(source)

    if not grid or width == 0:
        return rl.fallback_svg(source)

    table = _detect_table(grid, width, height)
    if table is None:
        return rl.fallback_svg(source)

    return _generate_table_svg(grid, table, width, height)


# ── Internal types ──────────────────────────────────────────────────

class _Table:
    """Detected table structure."""
    def __init__(
        self,
        col_positions: list[int],
        row_positions: list[int],
        header_sep: int | None = None,
    ):
        self.col_positions = col_positions  # column border positions
        self.row_positions = row_positions  # row border positions
        self.header_sep = header_sep        # row of header separator (if any)

    @property
    def num_cols(self) -> int:
        return max(0, len(self.col_positions) - 1)

    @property
    def num_rows(self) -> int:
        return max(0, len(self.row_positions) - 1)


# ── Detection ───────────────────────────────────────────────────────

_INTERSECTION_CHARS = rl.CORNER_CHARS | rl.TEE_CHARS


def _detect_table(
    grid: list[list[str]], width: int, height: int
) -> _Table | None:
    """Detect a table by finding consistent grid intersections."""
    rows = len(grid)
    cols = width

    # Find all intersection points
    intersections: list[tuple[int, int]] = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] in _INTERSECTION_CHARS:
                # Verify it's a real intersection: has borders in at least 2 directions
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

    if len(intersections) < 4:
        return None

    # Find column positions: columns where intersections appear on multiple rows
    col_counts: dict[int, int] = {}
    for _, c in intersections:
        col_counts[c] = col_counts.get(c, 0) + 1

    # Columns appearing on at least 2 rows
    col_positions = sorted(c for c, count in col_counts.items() if count >= 2)
    if len(col_positions) < 2:
        return None

    # Find row positions: rows where intersections appear at multiple columns
    row_counts: dict[int, int] = {}
    for r, _ in intersections:
        row_counts[r] = row_counts.get(r, 0) + 1

    row_positions = sorted(r for r, count in row_counts.items() if count >= 2)
    if len(row_positions) < 2:
        return None

    # Verify borders exist between adjacent intersections
    valid_cols: list[int] = [col_positions[0]]
    for i in range(1, len(col_positions)):
        c = col_positions[i]
        prev_c = valid_cols[-1]
        # Check that at least one row has a horizontal border between these columns
        has_border = False
        for r in row_positions:
            if rl.has_horiz_border(grid, r, prev_c, c):
                has_border = True
                break
        if has_border:
            valid_cols.append(c)

    valid_rows: list[int] = [row_positions[0]]
    for i in range(1, len(row_positions)):
        r = row_positions[i]
        prev_r = valid_rows[-1]
        has_border = False
        for c in valid_cols:
            if rl.has_vert_border(grid, c, prev_r, r):
                has_border = True
                break
        if has_border:
            valid_rows.append(r)

    if len(valid_cols) < 3 or len(valid_rows) < 3:
        return None

    # Detect header separator (first internal row border)
    header_sep = None
    if len(valid_rows) >= 3:
        header_sep = valid_rows[1]

    return _Table(
        col_positions=valid_cols,
        row_positions=valid_rows,
        header_sep=header_sep,
    )


# ── SVG generation ──────────────────────────────────────────────────

def _generate_table_svg(
    grid: list[list[str]],
    table: _Table,
    width: int,
    height: int,
) -> str:
    """Generate SVG from detected table."""
    parts: list[str] = [
        rl.svg_open(width, height),
        rl.THEME_CSS,
        rl.svg_background(width, height),
    ]

    # Add table-specific styles (from theme)
    parts.append(DEFAULT_THEME.table_css())

    cols = table.col_positions
    tbl_rows = table.row_positions

    # Outer table border
    x1 = rl.PAD_X + cols[0] * rl.CHAR_W
    y1 = rl.PAD_Y + tbl_rows[0] * rl.CHAR_H
    tw = (cols[-1] - cols[0]) * rl.CHAR_W
    th = (tbl_rows[-1] - tbl_rows[0]) * rl.CHAR_H
    parts.append(
        f'  <rect class="table-border" x="{x1:.1f}" y="{y1:.1f}" '
        f'width="{tw:.1f}" height="{th:.1f}" rx="3"/>'
    )

    # Header background (if header separator exists)
    if table.header_sep is not None:
        hy = rl.PAD_Y + tbl_rows[0] * rl.CHAR_H
        # Extend header bg to the separator line position
        sep_y = rl.PAD_Y + table.header_sep * rl.CHAR_H + rl.CHAR_H * 0.5
        hh = sep_y - hy
        parts.append(
            f'  <rect class="table-header-bg" x="{x1 + 1:.1f}" y="{hy + 1:.1f}" '
            f'width="{tw - 2:.1f}" height="{hh - 2:.1f}" rx="2"/>'
        )

    # Internal horizontal borders
    for r_idx in range(1, len(tbl_rows) - 1):
        r = tbl_rows[r_idx]
        ly = rl.PAD_Y + r * rl.CHAR_H + rl.CHAR_H * 0.5
        parts.append(
            f'  <line class="table-border" x1="{x1:.1f}" y1="{ly:.1f}" '
            f'x2="{x1 + tw:.1f}" y2="{ly:.1f}"/>'
        )

    # Internal vertical borders
    for c_idx in range(1, len(cols) - 1):
        c = cols[c_idx]
        lx = rl.PAD_X + c * rl.CHAR_W + rl.CHAR_W * 0.5
        parts.append(
            f'  <line class="table-border" x1="{lx:.1f}" y1="{y1:.1f}" '
            f'x2="{lx:.1f}" y2="{y1 + th:.1f}"/>'
        )

    # Extract and render cell text
    for r_idx in range(len(tbl_rows) - 1):
        r_top = tbl_rows[r_idx]
        r_bot = tbl_rows[r_idx + 1]
        is_header = (table.header_sep is not None and r_idx == 0)

        for c_idx in range(len(cols) - 1):
            c_left = cols[c_idx]
            c_right = cols[c_idx + 1]

            # Extract cell content (filter out border chars)
            for r in range(r_top + 1, r_bot):
                content = ""
                for c in range(c_left + 1, c_right):
                    if c < len(grid[r]):
                        ch = grid[r][c]
                        if ch in rl.VERT_CHARS or ch in rl.CORNER_CHARS or ch in rl.TEE_CHARS:
                            content += " "
                        else:
                            content += ch
                content = content.strip()
                if content:
                    tx = rl.PAD_X + (c_left + 1) * rl.CHAR_W + 2
                    ty = rl.PAD_Y + r * rl.CHAR_H + rl.CHAR_H * 0.75
                    css = "table-header-text" if is_header else "table-cell-text"
                    import html as html_mod
                    escaped = html_mod.escape(content)
                    parts.append(
                        f'  <text class="{css}" x="{tx:.1f}" y="{ty:.1f}">{escaped}</text>'
                    )

    parts.append("</svg>")
    return "\n".join(parts)
