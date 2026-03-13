"""ASCII sequence diagram → SVG renderer.

Renders AI-generated sequence diagrams directly to SVG without external APIs.
Detects vertical lifelines (lanes), actor labels, and horizontal message arrows.

Typical LLM-generated sequence diagram:

  Client          Server          Database
    │                │                │
    │── GET /api ──>│                │
    │                │── SELECT * ──>│
    │                │<── Results ───│
    │<── JSON 200 ──│                │
    │                │                │

Structure-first: find vertical lanes, then trace horizontal messages between them.
"""

from __future__ import annotations

import html as html_mod

from . import renderlib as rl
from .themes import DEFAULT_THEME


def has_sequence_structure(source: str) -> bool:
    """Check if source contains a sequence diagram.

    A sequence diagram has:
    - 2+ vertical lanes (columns with consistent │ characters)
    - At least 1 horizontal message arrow between lanes
    - Actor labels above the lanes
    """
    grid, width, height = rl.parse_grid(source)
    if width == 0 or height < 4:
        return False

    lanes = _detect_lanes(grid, width, height)
    if len(lanes) < 2:
        return False

    messages = _detect_messages(grid, lanes, height)
    return len(messages) >= 1


def render_sequence_svg(source: str) -> str:
    """Render an ASCII sequence diagram to SVG."""
    grid, width, height = rl.parse_grid(source)

    if not grid or width == 0:
        return rl.fallback_svg(source)

    lanes = _detect_lanes(grid, width, height)
    if len(lanes) < 2:
        return rl.fallback_svg(source)

    messages = _detect_messages(grid, lanes, height)
    if not messages:
        return rl.fallback_svg(source)

    return _generate_sequence_svg(grid, lanes, messages, width, height)


# ── Internal types ──────────────────────────────────────────────────

class _Lane:
    """A vertical lifeline in the sequence diagram."""
    def __init__(self, col: int, label: str, label_row: int):
        self.col = col          # column position of the │ character
        self.label = label      # actor name
        self.label_row = label_row  # row where label appears
        self.first_bar = 0      # first row with │
        self.last_bar = 0       # last row with │


class _Message:
    """A horizontal message arrow between lanes."""
    def __init__(
        self,
        from_lane: int,
        to_lane: int,
        row: int,
        label: str,
        direction: str,  # 'right' or 'left'
    ):
        self.from_lane = from_lane  # index into lanes list
        self.to_lane = to_lane
        self.row = row
        self.label = label
        self.direction = direction


# ── Detection ───────────────────────────────────────────────────────

def _detect_lanes(
    grid: list[list[str]], width: int, _height: int
) -> list[_Lane]:
    """Detect vertical lanes by finding columns with consistent │ characters.

    A lane is a column position where │ appears on many rows (at least 40%
    of the non-empty rows below the header).
    """
    rows = len(grid)

    # Count │ occurrences per column
    col_counts: dict[int, list[int]] = {}
    for r in range(rows):
        for c in range(width):
            if grid[r][c] in rl.VERT_CHARS:
                if c not in col_counts:
                    col_counts[c] = []
                col_counts[c].append(r)

    if not col_counts:
        return []

    # Find the maximum count to establish threshold
    max_count = max(len(rows_list) for rows_list in col_counts.values())
    if max_count < 3:
        return []  # need substantial vertical runs, not just box borders

    # Lanes: columns with │ count >= 40% of max_count and at least 3 occurrences
    threshold = max(3, int(max_count * 0.4))
    lane_cols = sorted(
        c for c, rows_list in col_counts.items()
        if len(rows_list) >= threshold
    )

    if len(lane_cols) < 2:
        return []

    # Filter out columns that are too close together (likely box borders)
    filtered_cols: list[int] = [lane_cols[0]]
    for c in lane_cols[1:]:
        if c - filtered_cols[-1] >= 3:  # at least 3 chars apart
            filtered_cols.append(c)

    if len(filtered_cols) < 2:
        return []

    # Find the header row: the row just above where │ characters start
    first_bar_row = min(
        min(col_counts[c]) for c in filtered_cols if c in col_counts
    )

    # Extract actor labels from the header area (rows above first_bar_row)
    lanes: list[_Lane] = []
    for col in filtered_cols:
        label = _extract_lane_label(grid, col, first_bar_row, width)
        bar_rows = col_counts.get(col, [])

        lane = _Lane(
            col=col,
            label=label,
            label_row=max(0, first_bar_row - 1),
        )
        if bar_rows:
            lane.first_bar = min(bar_rows)
            lane.last_bar = max(bar_rows)
        lanes.append(lane)

    return lanes


def _extract_lane_label(
    grid: list[list[str]], col: int, first_bar_row: int, _width: int
) -> str:
    """Extract the actor label above a lane's lifeline.

    Scans header rows above the first │ to find text centered
    on or near the lane's column position. Skips rows that contain
    only box-drawing characters (borders).
    """
    if first_bar_row == 0:
        return f"Actor {col}"

    # Structural characters to ignore when looking for label text
    structural = rl.HORIZ_CHARS | rl.VERT_CHARS | rl.CORNER_CHARS | rl.TEE_CHARS

    # Scan upward from first_bar_row to find a row with actual text
    for header_row in range(first_bar_row - 1, -1, -1):
        row_text = "".join(grid[header_row])

        # Skip rows that are all structural chars or whitespace
        stripped = row_text.strip()
        if not stripped:
            continue
        if all(ch in structural or ch == ' ' for ch in stripped):
            continue

        # This row has actual text — extract segments
        segments: list[tuple[int, int, str]] = []
        i = 0
        while i < len(row_text):
            if row_text[i] != ' ' and row_text[i] not in structural:
                start = i
                end = i
                while end < len(row_text):
                    if row_text[end] == ' ':
                        next_char = end
                        while next_char < len(row_text) and row_text[next_char] == ' ':
                            next_char += 1
                        if next_char < len(row_text) and next_char - end <= 2 and row_text[next_char] not in (rl.VERT_CHARS | structural):
                            end = next_char
                        else:
                            break
                    elif row_text[end] in structural:
                        break
                    else:
                        end += 1
                text = row_text[start:end].strip()
                if text:
                    segments.append((start, end, text))
                i = end
            else:
                i += 1

        if not segments:
            continue

        # Find the segment whose center is closest to the lane column
        best_segment = None
        best_dist = float('inf')
        for start, end, text in segments:
            center = (start + end) / 2
            dist = abs(center - col)
            if dist < best_dist:
                best_dist = dist
                best_segment = text

        if best_segment:
            return best_segment

    return f"Actor {col}"


def _detect_messages(
    grid: list[list[str]], lanes: list[_Lane], _height: int
) -> list[_Message]:
    """Detect horizontal message arrows between lanes."""
    messages: list[_Message] = []
    rows = len(grid)
    cols = len(grid[0]) if grid else 0

    # Build lane column lookup for fast nearest-lane finding
    lane_cols = [lane.col for lane in lanes]

    for r in range(rows):
        # Look for arrow patterns on this row
        msg = _parse_message_row(grid, r, cols, lanes, lane_cols)
        if msg:
            messages.append(msg)

    return messages


def _parse_message_row(
    grid: list[list[str]],
    row: int,
    cols: int,
    lanes: list[_Lane],
    lane_cols: list[int],
) -> _Message | None:
    """Parse a single row for a message arrow between lanes.

    Message patterns:
    - │── Label ──>│  (right arrow)
    - │<── Label ──│  (left arrow)
    - │── Label ───────────>│  (long right arrow)
    """
    row_str = "".join(grid[row])

    # Must have at least one arrow character and horizontal line chars
    has_arrow_right = any(c in rl.ARROW_HEADS_RIGHT for c in row_str)
    has_arrow_left = any(c in rl.ARROW_HEADS_LEFT for c in row_str)
    has_horiz = any(c in rl.HORIZ_CHARS for c in row_str)

    if not has_horiz or not (has_arrow_right or has_arrow_left):
        return None

    # Find the arrow segment: contiguous region of ─, ═, -, >, <, spaces, and text
    # between two lane positions
    arrow_start = None
    arrow_end = None
    direction = "right"

    # Find first horizontal char or arrowhead
    for c in range(cols):
        ch = grid[row][c]
        if ch in rl.HORIZ_CHARS or ch in rl.ARROW_HEADS_LEFT:
            arrow_start = c
            if ch in rl.ARROW_HEADS_LEFT:
                direction = "left"
            break

    if arrow_start is None:
        return None

    # Trace to end
    for c in range(cols - 1, arrow_start, -1):
        ch = grid[row][c]
        if ch in rl.HORIZ_CHARS or ch in rl.ARROW_HEADS_RIGHT:
            arrow_end = c
            if ch in rl.ARROW_HEADS_RIGHT:
                direction = "right"
            break

    if arrow_end is None or arrow_end - arrow_start < 2:
        return None

    # Find which lanes this arrow connects
    from_lane_idx = _nearest_lane(arrow_start, lane_cols)
    to_lane_idx = _nearest_lane(arrow_end, lane_cols)

    if from_lane_idx is None or to_lane_idx is None:
        return None
    if from_lane_idx == to_lane_idx:
        return None

    # Ensure from < to in lane order, adjust direction
    if from_lane_idx > to_lane_idx:
        from_lane_idx, to_lane_idx = to_lane_idx, from_lane_idx
        direction = "left" if direction == "right" else "right"

    # Extract label: text between the horizontal line chars
    label = _extract_message_label(grid, row, arrow_start, arrow_end)

    return _Message(
        from_lane=from_lane_idx,
        to_lane=to_lane_idx,
        row=row,
        label=label,
        direction=direction,
    )


def _nearest_lane(col: int, lane_cols: list[int]) -> int | None:
    """Find the nearest lane to a column position."""
    best_idx = None
    best_dist = float('inf')
    for i, lc in enumerate(lane_cols):
        dist = abs(col - lc)
        if dist < best_dist and dist <= 3:  # within 3 chars of a lane
            best_dist = dist
            best_idx = i
    return best_idx


def _extract_message_label(
    grid: list[list[str]], row: int, start: int, end: int
) -> str:
    """Extract the text label from a message arrow.

    First checks the arrow row itself for inline labels, then checks
    the row above (common in sequence diagrams where the label sits
    above the arrow line).
    """
    # Check on the arrow row itself
    text_chars: list[str] = []
    for c in range(start, end + 1):
        ch = grid[row][c]
        if ch in rl.HORIZ_CHARS or ch in rl.ALL_ARROW_HEADS:
            continue
        text_chars.append(ch)

    label = "".join(text_chars).strip()
    if label:
        return label

    # Check the row above for label text (common in sequence diagrams)
    if row > 0:
        above_chars: list[str] = []
        for c in range(start, end + 1):
            if c < len(grid[row - 1]):
                ch = grid[row - 1][c]
                if ch in rl.HORIZ_CHARS or ch in rl.ALL_ARROW_HEADS or ch in rl.VERT_CHARS:
                    continue
                above_chars.append(ch)
        label = "".join(above_chars).strip()

    return label


# ── SVG generation ──────────────────────────────────────────────────

# Layout constants
_ACTOR_BOX_W = 100
_ACTOR_BOX_H = 30
_LANE_SPACING = 160
_MSG_ROW_H = 28
_TOP_PAD = 20
_SIDE_PAD = 40


def _generate_sequence_svg(
    _grid: list[list[str]],
    lanes: list[_Lane],
    messages: list[_Message],
    _width: int,
    _height: int,
) -> str:
    """Generate SVG from detected sequence diagram."""

    # Calculate layout dimensions
    num_lanes = len(lanes)
    svg_width = _SIDE_PAD * 2 + (num_lanes - 1) * _LANE_SPACING + _ACTOR_BOX_W
    actor_y = _TOP_PAD

    # Find the row range of messages
    msg_rows = [m.row for m in messages]
    first_msg_row = min(msg_rows) if msg_rows else 0
    last_msg_row = max(msg_rows) if msg_rows else 0

    # Map grid rows to SVG y positions
    row_range = last_msg_row - first_msg_row + 1
    lifeline_top = actor_y + _ACTOR_BOX_H + 10
    lifeline_bottom = lifeline_top + max(row_range * _MSG_ROW_H, 60) + 20
    svg_height = lifeline_bottom + _ACTOR_BOX_H + _TOP_PAD + 10

    # Calculate lane x positions
    lane_x_positions: list[float] = []
    for i in range(num_lanes):
        x = _SIDE_PAD + _ACTOR_BOX_W / 2 + i * _LANE_SPACING
        lane_x_positions.append(x)

    parts: list[str] = []

    # SVG header
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_width}" height="{svg_height}" '
        f'class="mdview-diagram">'
    )

    # Theme CSS (from theme system)
    parts.append(DEFAULT_THEME.sequence_css())

    # Arrowhead marker
    parts.append("""  <defs>
    <marker id="seq-arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="msg-head"/>
    </marker>
  </defs>""")

    # Background
    parts.append(
        f'  <rect class="bg" x="0" y="0" width="{svg_width}" height="{svg_height}" rx="6"/>'
    )

    # Actor boxes (top)
    for i, lane in enumerate(lanes):
        x = lane_x_positions[i] - _ACTOR_BOX_W / 2
        parts.append(
            f'  <rect class="actor-box" x="{x:.1f}" y="{actor_y}" '
            f'width="{_ACTOR_BOX_W}" height="{_ACTOR_BOX_H}" rx="4"/>'
        )
        escaped = html_mod.escape(lane.label)
        parts.append(
            f'  <text class="actor-text" x="{lane_x_positions[i]:.1f}" '
            f'y="{actor_y + _ACTOR_BOX_H / 2}">{escaped}</text>'
        )

    # Actor boxes (bottom, mirrored)
    bottom_actor_y = lifeline_bottom + 10
    for i, lane in enumerate(lanes):
        x = lane_x_positions[i] - _ACTOR_BOX_W / 2
        parts.append(
            f'  <rect class="actor-box" x="{x:.1f}" y="{bottom_actor_y}" '
            f'width="{_ACTOR_BOX_W}" height="{_ACTOR_BOX_H}" rx="4"/>'
        )
        escaped = html_mod.escape(lane.label)
        parts.append(
            f'  <text class="actor-text" x="{lane_x_positions[i]:.1f}" '
            f'y="{bottom_actor_y + _ACTOR_BOX_H / 2}">{escaped}</text>'
        )

    # Lifelines (dashed vertical lines)
    for i in range(num_lanes):
        x = lane_x_positions[i]
        parts.append(
            f'  <line class="lifeline" x1="{x:.1f}" y1="{lifeline_top}" '
            f'x2="{x:.1f}" y2="{lifeline_bottom}"/>'
        )

    # Message arrows
    for msg in messages:
        msg_y = lifeline_top + (msg.row - first_msg_row + 0.5) * _MSG_ROW_H

        from_x = lane_x_positions[msg.from_lane]
        to_x = lane_x_positions[msg.to_lane]

        if msg.direction == "right":
            x1, x2 = from_x, to_x
            marker = ' marker-end="url(#seq-arrow)"'
        else:
            x1, x2 = to_x, from_x
            marker = ' marker-start="url(#seq-arrow)"'

        parts.append(
            f'  <line class="msg-line" x1="{x1:.1f}" y1="{msg_y:.1f}" '
            f'x2="{x2:.1f}" y2="{msg_y:.1f}"{marker}/>'
        )

        # Label above the arrow
        if msg.label:
            label_x = (from_x + to_x) / 2
            label_y = msg_y - 8
            escaped = html_mod.escape(msg.label)
            parts.append(
                f'  <text class="msg-label" x="{label_x:.1f}" '
                f'y="{label_y:.1f}">{escaped}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)
