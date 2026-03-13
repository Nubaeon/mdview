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
ARROW_HEADS_DOWN = frozenset("▼↓v")
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
    box_index: int = -1  # index into boxes list, -1 for free text


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

            bottom = _trace_vert(grid, c, r + 1, rows)
            if bottom is None:
                continue

            # Try each possible right edge — '+' can be a corner OR a
            # mid-border tee, so _trace_horiz may stop too early.
            search_start = c + 1
            while True:
                right = _trace_horiz(grid, r, search_start, cols)
                if right is None:
                    break

                if grid[bottom][right] not in CORNER_CHARS:
                    search_start = right + 1
                    continue
                if not has_horiz_border(grid, bottom, c, right):
                    search_start = right + 1
                    continue
                if not has_vert_border(grid, right, r, bottom):
                    search_start = right + 1
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
                break  # found valid box for this top-left corner

    return boxes


def _trace_horiz(grid: list[list[str]], row: int, start_col: int, max_col: int) -> int | None:
    """Trace horizontal border right, return column of corner/tee.

    Allows arrowhead characters (▼, ▲, etc.) in borders — these are
    common where arrows enter/exit a box through its border.
    """
    for c in range(start_col, max_col):
        ch = grid[row][c]
        if ch in CORNER_CHARS:
            return c
        if ch not in HORIZ_CHARS and ch not in TEE_CHARS and ch != ' ' and ch not in ALL_ARROW_HEADS:
            return None
    return None


def _trace_vert(grid: list[list[str]], col: int, start_row: int, max_row: int) -> int | None:
    """Trace vertical border down, return row of corner/tee.

    Allows arrowhead characters in borders where arrows cross.
    """
    for r in range(start_row, max_row):
        ch = grid[r][col]
        if ch in CORNER_CHARS:
            return r
        if ch not in (VERT_CHARS | TEE_CHARS) and ch not in ALL_ARROW_HEADS:
            return None
    return None


def has_horiz_border(grid: list[list[str]], row: int, left: int, right: int) -> bool:
    """Check if row has a continuous horizontal border between left and right.

    Requires at least 60% of characters to be actual border chars (not just spaces).
    Arrowheads are allowed — they appear where arrows enter/exit boxes.
    Rejects borders with gaps of 2+ consecutive spaces (separate structures).
    """
    span = right - left - 1
    if span <= 0:
        return False
    border_count = 0
    consecutive_spaces = 0
    for c in range(left + 1, right):
        ch = grid[row][c]
        if ch in HORIZ_CHARS or ch in TEE_CHARS:
            border_count += 1
            consecutive_spaces = 0
        elif ch in ALL_ARROW_HEADS:
            border_count += 1  # arrowheads count as border chars
            consecutive_spaces = 0
        elif ch == ' ':
            consecutive_spaces += 1
            if consecutive_spaces >= 2:
                return False
        else:
            return False
    return border_count / span >= 0.6


def has_vert_border(grid: list[list[str]], col: int, top: int, bottom: int) -> bool:
    """Check if col has a continuous vertical border between top and bottom."""
    for r in range(top + 1, bottom):
        if grid[r][col] not in (VERT_CHARS | TEE_CHARS):
            return False
    return True


# ── Tolerant box detection (wireframes) ────────────────────────────

def _trace_horiz_tolerant(grid: list[list[str]], row: int, start_col: int, max_col: int) -> int | None:
    """Trace horizontal border right, allowing text on borders (title-on-border pattern).

    Only stops on vertical border chars. Accepts text and spaces between borders.
    Returns column of corner/tee, or None if a vertical border interrupts.
    """
    for c in range(start_col, max_col):
        ch = grid[row][c]
        if ch in CORNER_CHARS:
            return c
        if ch in VERT_CHARS:
            return None
    return None


def find_boxes_tolerant(grid: list[list[str]]) -> list[Box]:
    """Find boxes allowing text on top/bottom borders (wireframe title pattern).

    Like find_boxes but uses tolerant horizontal tracing and density-based
    border validation instead of strict character-only tracing.
    """
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    boxes: list[Box] = []

    for r in range(rows):
        for c in range(cols):
            ch = grid[r][c]
            if ch not in CORNER_CHARS:
                continue

            # Must have vert down
            if r + 1 >= rows or grid[r + 1][c] not in (VERT_CHARS | TEE_CHARS):
                continue

            # Tolerant horizontal trace (allows title text)
            right = _trace_horiz_tolerant(grid, r, c + 1, cols)
            if right is None:
                continue

            bottom = _trace_vert(grid, c, r + 1, rows)
            if bottom is None:
                continue

            if grid[bottom][right] not in CORNER_CHARS:
                continue
            # Bottom border must be valid (use has_horiz_border which allows text + 60% density)
            if not _has_horiz_border_tolerant(grid, bottom, c, right):
                continue
            if not _has_vert_border_tolerant(grid, right, r, bottom):
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


def _has_vert_border_tolerant(grid: list[list[str]], col: int, top: int, bottom: int) -> bool:
    """Tolerant vertical border check (allows short lines / missing chars).

    Uses 50% threshold for larger spans. For very short boxes (1-2 content rows),
    the corners themselves are sufficient evidence — common in wireframes where
    inner content │ sits one column off from the corner position.
    """
    span = bottom - top - 1
    if span <= 0:
        return False
    if span <= 2:
        return True  # corners already validated; short boxes get a pass
    border_count = 0
    for r in range(top + 1, bottom):
        if col < len(grid[r]) and grid[r][col] in (VERT_CHARS | TEE_CHARS):
            border_count += 1
    return border_count / span >= 0.5


def _has_horiz_border_tolerant(grid: list[list[str]], row: int, left: int, right: int) -> bool:
    """Like has_horiz_border but allows any non-vertical chars (text on border)."""
    span = right - left - 1
    if span <= 0:
        return False
    border_count = 0
    for c in range(left + 1, right):
        ch = grid[row][c]
        if ch in HORIZ_CHARS or ch in TEE_CHARS:
            border_count += 1
        elif ch in VERT_CHARS:
            return False  # vertical border interrupts
    return border_count / span >= 0.4  # lower threshold for tolerant mode


# ── Text extraction ─────────────────────────────────────────────────

def extract_box_texts(grid: list[list[str]], boxes: list[Box]) -> list[TextSpan]:
    """Extract text content from inside boxes (stripped of padding)."""
    texts: list[TextSpan] = []

    for box_idx, box in enumerate(boxes):
        section_breaks = [box.top] + box.separators + [box.bottom]

        for section_idx in range(len(section_breaks) - 1):
            section_top = section_breaks[section_idx]
            section_bottom = section_breaks[section_idx + 1]

            for r in range(section_top + 1, section_bottom):
                content = ""
                for c in range(box.left + 1, box.right):
                    content += grid[r][c]

                content = content.strip()
                if content:
                    texts.append(TextSpan(
                        row=r,
                        col=box.left + 1,
                        text=content,
                        section=section_idx,
                        box_index=box_idx,
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
            # Start of horizontal segment: ─, ═, -, or arrow head (either direction)
            if ch in HORIZ_CHARS or ch in ARROW_HEADS_RIGHT or ch in ARROW_HEADS_LEFT:
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
            if ch in VERT_CHARS or ch in ARROW_HEADS_DOWN or ch in ARROW_HEADS_UP:
                arrow = _trace_vert_arrow(grid, r, c, rows, used, boxes)
                if arrow:
                    arrows.append(arrow)
                    for pr, pc in arrow.points:
                        used.add((pr, pc))
                    r = arrow.points[-1][0] + 1
                    continue
            r += 1

    # Join adjacent segments that form multi-segment (L-shaped, U-shaped) arrows
    arrows = _join_arrow_segments(arrows, grid, boxes)

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

    # Find connected boxes — assignment depends on arrow direction
    if direction == "left":
        # Left-pointing: source is on the right, target on the left
        # Reverse points so they go source→target for consistent marker-end
        points = list(reversed(points))
        from_box = _find_adjacent_box(boxes, row, points[0][1], "right")
        to_box = _find_adjacent_box(boxes, row, points[-1][1], "left")
    else:
        from_box = _find_adjacent_box(boxes, row, points[0][1], "left")
        to_box = _find_adjacent_box(boxes, row, points[-1][1], "right")

    # Extract label: text above or below the arrow
    label = _find_arrow_label(grid, row, min(p[1] for p in points), max(p[1] for p in points))

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

    # Check left of arrow
    for r in range(start_row, end_row + 1):
        if col - 2 >= 0:
            text = ""
            for c in range(max(0, col - 20), col - 1):
                ch = grid[r][c]
                if ch in HORIZ_CHARS | VERT_CHARS | CORNER_CHARS | TEE_CHARS:
                    text = ""  # reset — only take text after last structural char
                    continue
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


# ── Multi-segment arrow joining ────────────────────────────────────

def _join_arrow_segments(
    arrows: list[Arrow], grid: list[list[str]], boxes: list[Box]
) -> list[Arrow]:
    """Join adjacent arrow segments into multi-segment arrows.

    Two merge passes:
    1. Corner merging: L/U-shaped arrows through corner characters (└, ┌, etc.)
    2. Collinear merging: same-row/column segments with text gaps between them
       (e.g., ── REST ─> becomes one arrow with label "REST")
    """
    if len(arrows) < 2:
        return arrows

    # Pass 1: Corner merging (L-shaped, U-shaped)
    joined: set[int] = set()
    result: list[Arrow] = []

    for i in range(len(arrows)):
        if i in joined:
            continue

        current = arrows[i]
        merged = True

        while merged:
            merged = False
            for j in range(len(arrows)):
                if j in joined or j == i:
                    continue
                if id(arrows[j]) == id(current):
                    continue

                other = arrows[j]
                merged_arrow = _try_merge(current, other, grid, boxes)
                if merged_arrow:
                    current = merged_arrow
                    joined.add(j)
                    merged = True
                    break

        result.append(current)

    # Pass 2: Collinear merging — join same-row or same-column segments
    # separated by text (inline labels like ── REST ─>)
    result = _join_collinear_segments(result, grid, boxes)

    return result


def _join_collinear_segments(
    arrows: list[Arrow], grid: list[list[str]], boxes: list[Box]
) -> list[Arrow]:
    """Join collinear arrow segments separated by inline text.

    Pattern: ── REST ─>  (two horizontal segments on the same row with text gap)
    The text in the gap becomes the arrow label.
    """
    if len(arrows) < 2:
        return arrows

    joined: set[int] = set()
    result: list[Arrow] = []

    for i in range(len(arrows)):
        if i in joined:
            continue

        current = arrows[i]
        merged = True

        while merged:
            merged = False
            for j in range(len(arrows)):
                if j in joined or (j == i and id(arrows[j]) == id(current)):
                    continue
                if j in joined:
                    continue

                other = arrows[j]
                merged_arrow = _try_collinear_merge(current, other, grid, boxes)
                if merged_arrow:
                    current = merged_arrow
                    joined.add(j)
                    merged = True
                    break

        result.append(current)

    return result


def _try_collinear_merge(
    a: Arrow, b: Arrow, grid: list[list[str]], boxes: list[Box]
) -> Arrow | None:
    """Try to merge two collinear arrow segments with a text gap.

    For horizontal: both on the same row, gap <= 15 chars, text in the gap.
    For vertical: both on the same column, gap <= 10 rows, text beside the gap.
    Does NOT merge across box borders (a box boundary in the gap blocks merging).
    """
    if not a.points or not b.points:
        return None

    a_row_set = {p[0] for p in a.points}
    b_row_set = {p[0] for p in b.points}
    a_col_set = {p[1] for p in a.points}
    b_col_set = {p[1] for p in b.points}

    # Horizontal: same single row
    if len(a_row_set) == 1 and len(b_row_set) == 1 and a_row_set == b_row_set:
        row = next(iter(a_row_set))
        a_min_c = min(p[1] for p in a.points)
        a_max_c = max(p[1] for p in a.points)
        b_min_c = min(p[1] for p in b.points)
        b_max_c = max(p[1] for p in b.points)

        # Determine which is left and which is right
        if a_max_c < b_min_c:
            left_a, right_b = a, b
            gap_start, gap_end = a_max_c + 1, b_min_c - 1
        elif b_max_c < a_min_c:
            left_a, right_b = b, a
            gap_start, gap_end = b_max_c + 1, a_min_c - 1
        else:
            return None  # overlapping

        gap = gap_end - gap_start + 1
        if gap < 1 or gap > 15:
            return None

        # Don't merge across box borders — if any column in the gap
        # is a box left or right edge on this row, abort
        for box in boxes:
            if box.top <= row <= box.bottom:
                if gap_start <= box.left <= gap_end or gap_start <= box.right <= gap_end:
                    return None

        # Extract text from the gap
        label_chars = []
        for c in range(gap_start, gap_end + 1):
            ch = grid[row][c]
            if ch in HORIZ_CHARS | ALL_ARROW_HEADS:
                continue
            label_chars.append(ch)
        label = "".join(label_chars).strip()

        if not label:
            return None

        # Merge points (left to right)
        merged_points = sorted(
            left_a.points + right_b.points, key=lambda p: p[1]
        )

        # Determine direction from arrowhead
        ah_end, ah_dir = _find_arrowhead_direction(grid, merged_points)
        if ah_end == "start":
            merged_points = list(reversed(merged_points))

        from_box = _find_adjacent_box_any_side(
            boxes, merged_points[0][0], merged_points[0][1]
        )
        to_box = _find_adjacent_box_any_side(
            boxes, merged_points[-1][0], merged_points[-1][1]
        )

        return Arrow(
            points=merged_points,
            direction=ah_dir,
            label=label,
            from_box=from_box,
            to_box=to_box,
        )

    # Vertical: same single column
    if len(a_col_set) == 1 and len(b_col_set) == 1 and a_col_set == b_col_set:
        col = next(iter(a_col_set))
        a_min_r = min(p[0] for p in a.points)
        a_max_r = max(p[0] for p in a.points)
        b_min_r = min(p[0] for p in b.points)
        b_max_r = max(p[0] for p in b.points)

        if a_max_r < b_min_r:
            top_a, bot_b = a, b
            gap_start, gap_end = a_max_r + 1, b_min_r - 1
        elif b_max_r < a_min_r:
            top_a, bot_b = b, a
            gap_start, gap_end = b_max_r + 1, a_min_r - 1
        else:
            return None

        gap = gap_end - gap_start + 1
        if gap < 1 or gap > 10:
            return None

        # Don't merge across box borders — if any row in the gap
        # is a box top or bottom edge at this column, abort
        for box in boxes:
            if box.left <= col <= box.right:
                if gap_start <= box.top <= gap_end or gap_start <= box.bottom <= gap_end:
                    return None

        # Look for label text to the right of the gap rows
        label = _find_arrow_label_vert(grid, col, gap_start, gap_end)

        # Merge points (top to bottom)
        merged_points = sorted(
            top_a.points + bot_b.points, key=lambda p: p[0]
        )

        ah_end, ah_dir = _find_arrowhead_direction(grid, merged_points)
        if ah_end == "start":
            merged_points = list(reversed(merged_points))

        from_box = _find_adjacent_box_any_side(
            boxes, merged_points[0][0], merged_points[0][1]
        )
        to_box = _find_adjacent_box_any_side(
            boxes, merged_points[-1][0], merged_points[-1][1]
        )

        return Arrow(
            points=merged_points,
            direction=ah_dir,
            label=label or top_a.label or bot_b.label,
            from_box=from_box,
            to_box=to_box,
        )

    return None


def _find_arrowhead_direction(grid: list[list[str]], points: list[tuple[int, int]]) -> tuple[str | None, str]:
    """Find which end of a point list has an arrowhead character.

    Scans all points (not just first/last) because after multi-segment merging,
    the arrowhead may be in the interior of the point list.

    Returns (end, direction) where end is 'start', 'end', or None,
    and direction is the arrowhead direction.
    """
    if not points:
        return None, "right"

    for idx, (r, c) in enumerate(points):
        ch = char_at(grid, r, c)
        direction = None
        if ch in ARROW_HEADS_RIGHT:
            direction = "right"
        elif ch in ARROW_HEADS_LEFT:
            direction = "left"
        elif ch in ARROW_HEADS_DOWN:
            direction = "down"
        elif ch in ARROW_HEADS_UP:
            direction = "up"
        if direction:
            end = "start" if idx < len(points) / 2 else "end"
            return end, direction

    return None, "right"


def _try_merge(a: Arrow, b: Arrow, grid: list[list[str]], boxes: list[Box]) -> Arrow | None:
    """Try to merge two arrows that meet at a corner point.

    Returns merged arrow or None if they don't connect.
    Points are ordered so the arrowhead end is last (matching svg_arrow convention).
    """
    if not a.points or not b.points:
        return None

    a_start = a.points[0]
    a_end = a.points[-1]
    b_start = b.points[0]
    b_end = b.points[-1]

    def adjacent(p1: tuple[int, int], p2: tuple[int, int]) -> bool:
        return abs(p1[0] - p2[0]) <= 1 and abs(p1[1] - p2[1]) <= 1

    def find_corner_between(p1: tuple[int, int], p2: tuple[int, int]) -> tuple[int, int] | None:
        """Find corner character cell between two adjacent segment endpoints."""
        for r in range(min(p1[0], p2[0]), max(p1[0], p2[0]) + 1):
            for c in range(min(p1[1], p2[1]), max(p1[1], p2[1]) + 1):
                if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                    if grid[r][c] in CORNER_CHARS:
                        return (r, c)
        return None

    # Try all 4 endpoint combinations, inserting corner point between segments
    merged_points = None
    pairs = [
        (a_end, b_start, lambda c: a.points + [c] + b.points),
        (a_end, b_end, lambda c: a.points + [c] + list(reversed(b.points))),
        (a_start, b_start, lambda c: list(reversed(a.points)) + [c] + b.points),
        (a_start, b_end, lambda c: b.points + [c] + a.points),
    ]
    for ep1, ep2, merge_fn in pairs:
        if adjacent(ep1, ep2):
            corner = find_corner_between(ep1, ep2)
            if corner:
                merged_points = merge_fn(corner)
                break

    if merged_points is None:
        return None

    # Find actual arrowhead in the merged points to determine direction
    ah_end, ah_dir = _find_arrowhead_direction(grid, merged_points)

    # Orient points so arrowhead is at the END (target)
    # This matches svg_arrow convention: start=source, end=target
    if ah_end == "start":
        merged_points = list(reversed(merged_points))

    direction = ah_dir

    # Find box connections: start point = source (from_box), end point = target (to_box)
    start_pt = merged_points[0]
    end_pt = merged_points[-1]

    from_box = _find_adjacent_box_any_side(boxes, start_pt[0], start_pt[1])
    to_box = _find_adjacent_box_any_side(boxes, end_pt[0], end_pt[1])

    # Merge labels
    label = a.label or b.label

    return Arrow(
        points=merged_points,
        direction=direction,
        label=label,
        from_box=from_box,
        to_box=to_box,
    )


def _find_adjacent_box_any_side(boxes: list[Box], row: int, col: int) -> int | None:
    """Find a box adjacent to a point on any side."""
    for side in ("left", "right", "above", "below"):
        result = _find_adjacent_box(boxes, row, col, side)
        if result is not None:
            return result
    return None


# ── SVG generation helpers ──────────────────────────────────────────

# Character cell dimensions (shared across all renderers)
CHAR_W = 8.4
CHAR_H = 16
PAD_X = 12
PAD_Y = 8

# Theme CSS — generated from default theme, shared across all renderers
from .themes import DEFAULT_THEME
THEME_CSS = DEFAULT_THEME.svg_css()


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


def svg_open_tight(boxes: list[Box], height: int) -> str:
    """SVG opening tag with tight width based on content bounds."""
    if boxes:
        max_right = max(b.right for b in boxes)
        svg_w = (max_right + 1) * CHAR_W + PAD_X * 2
    else:
        svg_w = PAD_X * 2
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


def svg_background_tight(boxes: list[Box], height: int) -> str:
    """Background rectangle with tight width based on content bounds."""
    if boxes:
        max_right = max(b.right for b in boxes)
        svg_w = (max_right + 1) * CHAR_W + PAD_X * 2
    else:
        svg_w = PAD_X * 2
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


def svg_text(span: TextSpan, is_header: bool = False, box: Box | None = None) -> str:
    """Render a text span as SVG text element, centered within box if provided."""
    css_class = "box-header" if is_header else "box-text"
    escaped = html.escape(span.text)

    if box is not None:
        # Center text horizontally within the box
        cx = PAD_X + (box.left + box.right) / 2 * CHAR_W + CHAR_W / 2

        # Compute section bounds for vertical centering
        section_breaks = [box.top] + box.separators + [box.bottom]
        if span.section < len(section_breaks) - 1:
            sec_top = section_breaks[span.section]
            sec_bot = section_breaks[span.section + 1]
        else:
            sec_top = box.top
            sec_bot = box.bottom

        # Section visual bounds
        sec_top_y = PAD_Y + sec_top * CHAR_H
        sec_bot_y = PAD_Y + sec_bot * CHAR_H
        sec_center_y = (sec_top_y + sec_bot_y) / 2

        # Content rows in this section
        content_count = sec_bot - sec_top - 1
        if content_count <= 0:
            content_count = 1
        relative_pos = span.row - (sec_top + 1)
        center_row = (content_count - 1) / 2
        offset = relative_pos - center_row
        # +2px visual nudge: dominant-baseline="central" centers on em-box
        # but text with mostly uppercase/ascenders looks better slightly lower
        ty = sec_center_y + offset * CHAR_H + 2

        return (
            f'  <text class="{css_class}" x="{cx:.1f}" y="{ty:.1f}" '
            f'text-anchor="middle" dominant-baseline="central">{escaped}</text>'
        )

    tx = PAD_X + span.col * CHAR_W
    ty = PAD_Y + span.row * CHAR_H + CHAR_H * 0.75
    return f'  <text class="{css_class}" x="{tx:.1f}" y="{ty:.1f}">{escaped}</text>'


def svg_arrow(arrow: Arrow, boxes: list[Box] | None = None) -> list[str]:
    """Render an arrow as SVG line or polyline with arrowhead marker.

    Single-segment arrows render as <line>. Multi-segment (L/U-shaped)
    arrows render as <polyline> with waypoints at each corner.

    When boxes are provided, endpoints are snapped to box edge centers
    for proper visual alignment.
    """
    if len(arrow.points) < 2:
        return []

    parts: list[str] = []

    def to_svg(r: int, c: int) -> tuple[float, float]:
        return (PAD_X + c * CHAR_W + CHAR_W / 2, PAD_Y + r * CHAR_H + CHAR_H / 2)

    def box_edge_svg(box: Box, side: str) -> tuple[float, float]:
        """Get SVG coordinate for the midpoint of a box edge."""
        bx = PAD_X + box.left * CHAR_W
        by = PAD_Y + box.top * CHAR_H
        bw = (box.right - box.left) * CHAR_W
        bh = (box.bottom - box.top) * CHAR_H
        if side == "right":
            return (bx + bw, by + bh / 2)
        elif side == "left":
            return (bx, by + bh / 2)
        elif side == "bottom":
            return (bx + bw / 2, by + bh)
        else:  # top
            return (bx + bw / 2, by)

    # Arrowhead marker: always marker-end since points are ordered source→target
    marker = ' marker-end="url(#arrowhead)"'

    # Deduplicate consecutive waypoints and extract corners for polyline
    waypoints = _arrow_waypoints(arrow.points)
    svg_pts = [to_svg(r, c) for r, c in waypoints]

    # Snap start/end to box edge centers when connected
    # For multi-segment arrows, use per-segment direction (not overall arrow.direction)
    is_multi = len(waypoints) > 2

    if boxes and arrow.from_box is not None and len(svg_pts) >= 2:
        fb = boxes[arrow.from_box]
        if is_multi and len(waypoints) >= 2:
            # Use first segment direction for from_box exit side
            dr = waypoints[1][0] - waypoints[0][0]
            dc = waypoints[1][1] - waypoints[0][1]
            if abs(dc) > abs(dr):
                svg_pts[0] = box_edge_svg(fb, "right" if dc > 0 else "left")
            else:
                svg_pts[0] = box_edge_svg(fb, "bottom" if dr > 0 else "top")
        elif arrow.direction in ("right", "left"):
            svg_pts[0] = box_edge_svg(fb, "right") if arrow.direction == "right" else box_edge_svg(fb, "left")
        else:
            svg_pts[0] = box_edge_svg(fb, "bottom") if arrow.direction == "down" else box_edge_svg(fb, "top")

    if boxes and arrow.to_box is not None and len(svg_pts) >= 2:
        tb = boxes[arrow.to_box]
        if is_multi and len(waypoints) >= 2:
            # Use last segment direction for to_box entry side
            dr = waypoints[-1][0] - waypoints[-2][0]
            dc = waypoints[-1][1] - waypoints[-2][1]
            if abs(dc) > abs(dr):
                svg_pts[-1] = box_edge_svg(tb, "left" if dc > 0 else "right")
            else:
                svg_pts[-1] = box_edge_svg(tb, "top" if dr > 0 else "bottom")
        elif arrow.direction in ("right", "left"):
            svg_pts[-1] = box_edge_svg(tb, "left") if arrow.direction == "right" else box_edge_svg(tb, "right")
        else:
            svg_pts[-1] = box_edge_svg(tb, "top") if arrow.direction == "down" else box_edge_svg(tb, "bottom")

    # After snapping endpoints to box edges, align adjacent waypoints so
    # vertical segments stay vertical and horizontal segments stay horizontal
    if is_multi and len(svg_pts) > 2:
        # Align first segment: if mostly vertical, match x; if mostly horizontal, match y
        dx0 = abs(svg_pts[1][0] - svg_pts[0][0])
        dy0 = abs(svg_pts[1][1] - svg_pts[0][1])
        if dy0 > dx0:  # vertical segment
            svg_pts[1] = (svg_pts[0][0], svg_pts[1][1])
        else:  # horizontal segment
            svg_pts[1] = (svg_pts[1][0], svg_pts[0][1])
        # Align last segment
        dxn = abs(svg_pts[-1][0] - svg_pts[-2][0])
        dyn = abs(svg_pts[-1][1] - svg_pts[-2][1])
        if dyn > dxn:  # vertical segment
            svg_pts[-2] = (svg_pts[-1][0], svg_pts[-2][1])
        else:  # horizontal segment
            svg_pts[-2] = (svg_pts[-2][0], svg_pts[-1][1])

    if len(svg_pts) == 2:
        # Simple straight line
        (x1, y1), (x2, y2) = svg_pts
        parts.append(
            f'  <line class="arrow-line" x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}"{marker}/>'
        )
    else:
        # Multi-segment: use polyline with corner waypoints
        points_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in svg_pts)
        parts.append(
            f'  <polyline class="arrow-line" points="{points_str}"{marker}/>'
        )

    # Render label if present — centered ON the arrow line with transparent bg
    if arrow.label:
        if len(svg_pts) <= 2:
            mid_x = (svg_pts[0][0] + svg_pts[1][0]) / 2
            mid_y = (svg_pts[0][1] + svg_pts[1][1]) / 2
        else:
            # Find longest segment and place label at its midpoint
            best_len = 0.0
            best_mid = (svg_pts[0][0], svg_pts[0][1])
            for k in range(len(svg_pts) - 1):
                sx, sy = svg_pts[k]
                ex, ey = svg_pts[k + 1]
                seg_len = abs(ex - sx) + abs(ey - sy)
                if seg_len > best_len:
                    best_len = seg_len
                    best_mid = ((sx + ex) / 2, (sy + ey) / 2)
            mid_x, mid_y = best_mid
        escaped = html.escape(arrow.label)
        # Semi-transparent background pill behind label
        label_w = len(arrow.label) * 7.2 + 8  # ~7.2px per char at 12px mono + padding
        label_h = 16
        parts.append(
            f'  <rect class="arrow-label-bg" x="{mid_x - label_w / 2:.1f}" '
            f'y="{mid_y - label_h / 2 - 1:.1f}" '
            f'width="{label_w:.1f}" height="{label_h:.1f}" rx="3"/>'
        )
        parts.append(
            f'  <text class="arrow-label" x="{mid_x:.1f}" y="{mid_y:.1f}" dominant-baseline="central">{escaped}</text>'
        )

    return parts


def _arrow_waypoints(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Reduce a dense point list to corner waypoints for polyline rendering.

    Keeps start, end, and any points where direction changes (corners).
    For simple straight arrows, returns just [start, end].
    """
    if len(points) <= 2:
        return points

    result = [points[0]]

    for i in range(1, len(points) - 1):
        prev = points[i - 1]
        curr = points[i]
        nxt = points[i + 1]
        # Direction change = corner point
        dr_prev = (curr[0] - prev[0], curr[1] - prev[1])
        dr_next = (nxt[0] - curr[0], nxt[1] - curr[1])
        if dr_prev != dr_next:
            result.append(curr)

    result.append(points[-1])
    return result


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
