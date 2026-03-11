"""Comprehensive tests for ASCII diagram renderers.

Tests cover:
- Detection (has_*_structure): correct identification and cross-type discrimination
- Rendering: SVG output structure and content
- Edge cases: minimal diagrams, Unicode vs ASCII borders, ambiguous inputs
- Pipeline routing: correct renderer selection in diagrams.py
"""

from __future__ import annotations

import pytest

from mdview.boxrender import has_box_structure, render_box_svg
from mdview.flowrender import has_flow_structure, render_flow_svg
from mdview.sequencerender import has_sequence_structure, render_sequence_svg
from mdview.tablerender import has_table_structure, render_table_svg
from mdview.renderlib import (
    Arrow,
    Box,
    TextSpan,
    find_arrows,
    find_boxes,
    extract_box_texts,
    parse_grid,
    classify_headers,
    svg_arrow,
    svg_arrowhead_defs,
    svg_rect,
    svg_text,
)


# ── Fixtures: Real LLM-generated diagrams ──────────────────────────

SIMPLE_BOX = """\
┌──────────────────┐
│ Component Name   │
├──────────────────┤
│ Property: value  │
│ Another: value   │
└──────────────────┘"""

MULTI_BOX = """\
┌─────────────┐
│ CLI Layer   │
├─────────────┤
│ commands    │
└─────────────┘

┌─────────────┐
│ Core Engine │
├─────────────┤
│ processing  │
└─────────────┘"""

ASCII_BOX = """\
+-------------------+
| Component Name    |
+-------------------+
| Property: value   |
+-------------------+"""

HORIZONTAL_FLOW = """\
┌──────┐     ┌──────┐     ┌──────┐
│ Start│────>│ Work │────>│ Done │
└──────┘     └──────┘     └──────┘"""

VERTICAL_FLOW = """\
┌──────────┐
│  Input   │
└──────────┘
      │
      ▼
┌──────────┐
│ Process  │
└──────────┘
      │
      ▼
┌──────────┐
│  Output  │
└──────────┘"""

UNICODE_TABLE = """\
┌──────────┬────────┬───────┐
│ Feature  │ Status │ Owner │
├──────────┼────────┼───────┤
│ Auth     │ Done   │ Alice │
│ Search   │ WIP    │ Bob   │
└──────────┴────────┴───────┘"""

ASCII_TABLE = """\
+----------+--------+-------+
| Feature  | Status | Owner |
+----------+--------+-------+
| Auth     | Done   | Alice |
| Search   | WIP    | Bob   |
+----------+--------+-------+"""

SEQUENCE_3_ACTOR = """\
  Client          Server          Database
    │                │                │
    │── GET /api ──>│                │
    │                │── SELECT * ──>│
    │                │<── Results ───│
    │<── JSON 200 ──│                │
    │                │                │"""

SEQUENCE_2_ACTOR = """\
  Alice       Bob
    │           │
    │── Hi! ──>│
    │<── Hey! ──│
    │           │"""

STATE_MACHINE = """\
  ┌──────┐          ┌────────┐          ┌─────────┐
  │ Idle │─────────>│ Active │─────────>│ Expired │
  └──────┘          └────────┘          └─────────┘
     ^                   │
     │      logout       │
     └───────────────────┘"""

STATE_MACHINE_SIMPLE = """\
┌─────┐     ┌─────┐
│ Off │────>│ On  │
└─────┘     └─────┘
  ^           │
  └───────────┘"""

FILE_TREE = """\
src/
├── main.py
├── utils/
│   ├── helpers.py
│   └── config.py
└── tests/
    └── test_main.py"""

CODE_BLOCK = """\
def hello():
    print("Hello, world!")

for i in range(10):
    hello()"""


# ── Box Renderer Tests ──────────────────────────────────────────────

class TestBoxDetection:
    def test_simple_box(self):
        assert has_box_structure(SIMPLE_BOX) is True

    def test_multi_box(self):
        assert has_box_structure(MULTI_BOX) is True

    def test_ascii_box(self):
        assert has_box_structure(ASCII_BOX) is True

    def test_not_a_box_file_tree(self):
        assert has_box_structure(FILE_TREE) is False

    def test_not_a_box_code(self):
        assert has_box_structure(CODE_BLOCK) is False

    def test_not_a_box_empty(self):
        assert has_box_structure("") is False

    def test_not_a_box_plain_text(self):
        assert has_box_structure("Just some text\nwith lines") is False


class TestBoxRendering:
    def test_renders_svg(self):
        svg = render_box_svg(SIMPLE_BOX)
        assert svg.startswith("<svg")
        assert "</svg>" in svg
        assert "box-border" in svg

    def test_contains_text(self):
        svg = render_box_svg(SIMPLE_BOX)
        assert "Component Name" in svg

    def test_has_separator(self):
        svg = render_box_svg(SIMPLE_BOX)
        assert "box-separator" in svg

    def test_has_header_styling(self):
        svg = render_box_svg(SIMPLE_BOX)
        assert "box-header" in svg

    def test_has_theme_css(self):
        svg = render_box_svg(SIMPLE_BOX)
        assert "prefers-color-scheme" in svg

    def test_fallback_for_non_box(self):
        svg = render_box_svg("just text\nnothing here")
        assert "<svg" in svg  # fallback SVG


# ── Flow Renderer Tests ─────────────────────────────────────────────

class TestFlowDetection:
    def test_horizontal_flow(self):
        assert has_flow_structure(HORIZONTAL_FLOW) is True

    def test_vertical_flow(self):
        assert has_flow_structure(VERTICAL_FLOW) is True

    def test_not_flow_plain_box(self):
        """Box without arrows should NOT be detected as flow."""
        assert has_flow_structure(SIMPLE_BOX) is False

    def test_not_flow_table(self):
        assert has_flow_structure(UNICODE_TABLE) is False

    def test_not_flow_sequence(self):
        assert has_flow_structure(SEQUENCE_3_ACTOR) is False


class TestFlowRendering:
    def test_horizontal_renders_svg(self):
        svg = render_flow_svg(HORIZONTAL_FLOW)
        assert svg.startswith("<svg")
        assert "arrow-line" in svg
        assert "arrowhead" in svg  # marker reference

    def test_vertical_renders_svg(self):
        svg = render_flow_svg(VERTICAL_FLOW)
        assert svg.startswith("<svg")
        assert "arrow-line" in svg

    def test_contains_box_text(self):
        svg = render_flow_svg(HORIZONTAL_FLOW)
        assert "Start" in svg
        assert "Work" in svg
        assert "Done" in svg

    def test_horizontal_arrow_count(self):
        svg = render_flow_svg(HORIZONTAL_FLOW)
        # Should have 2 arrows (Start→Work, Work→Done)
        # Count <line elements, not CSS class definitions
        assert svg.count('class="arrow-line"') == 2

    def test_vertical_arrow_count(self):
        svg = render_flow_svg(VERTICAL_FLOW)
        # Should have 2 arrows (Input→Process, Process→Output)
        assert svg.count('class="arrow-line"') == 2


# ── Table Renderer Tests ─────────────────────────────────────────────

class TestTableDetection:
    def test_unicode_table(self):
        assert has_table_structure(UNICODE_TABLE) is True

    def test_ascii_table(self):
        assert has_table_structure(ASCII_TABLE) is True

    def test_not_table_single_box(self):
        """A single box should NOT be detected as a table."""
        assert has_table_structure(SIMPLE_BOX) is False

    def test_not_table_flow(self):
        assert has_table_structure(HORIZONTAL_FLOW) is False

    def test_not_table_sequence(self):
        assert has_table_structure(SEQUENCE_3_ACTOR) is False


class TestTableRendering:
    def test_unicode_renders_svg(self):
        svg = render_table_svg(UNICODE_TABLE)
        assert svg.startswith("<svg")
        assert "table-border" in svg

    def test_ascii_renders_svg(self):
        svg = render_table_svg(ASCII_TABLE)
        assert svg.startswith("<svg")

    def test_contains_cell_text(self):
        svg = render_table_svg(UNICODE_TABLE)
        assert "Feature" in svg
        assert "Auth" in svg
        assert "Done" in svg
        assert "Alice" in svg

    def test_has_header_styling(self):
        svg = render_table_svg(UNICODE_TABLE)
        assert "table-header-text" in svg

    def test_has_theme_css(self):
        svg = render_table_svg(UNICODE_TABLE)
        assert "prefers-color-scheme" in svg


# ── Sequence Renderer Tests ──────────────────────────────────────────

class TestSequenceDetection:
    def test_three_actor(self):
        assert has_sequence_structure(SEQUENCE_3_ACTOR) is True

    def test_two_actor(self):
        assert has_sequence_structure(SEQUENCE_2_ACTOR) is True

    def test_not_sequence_flow(self):
        """Flow diagram should NOT be detected as sequence."""
        assert has_sequence_structure(HORIZONTAL_FLOW) is False

    def test_not_sequence_box(self):
        assert has_sequence_structure(SIMPLE_BOX) is False

    def test_not_sequence_table(self):
        assert has_sequence_structure(UNICODE_TABLE) is False

    def test_not_sequence_code(self):
        assert has_sequence_structure(CODE_BLOCK) is False


class TestSequenceRendering:
    def test_renders_svg(self):
        svg = render_sequence_svg(SEQUENCE_3_ACTOR)
        assert svg.startswith("<svg")
        assert "</svg>" in svg

    def test_has_actor_labels(self):
        svg = render_sequence_svg(SEQUENCE_3_ACTOR)
        assert "Client" in svg
        assert "Server" in svg
        assert "Database" in svg

    def test_has_lifelines(self):
        svg = render_sequence_svg(SEQUENCE_3_ACTOR)
        assert "lifeline" in svg

    def test_has_message_labels(self):
        svg = render_sequence_svg(SEQUENCE_3_ACTOR)
        assert "GET /api" in svg
        assert "Results" in svg

    def test_has_message_arrows(self):
        svg = render_sequence_svg(SEQUENCE_3_ACTOR)
        assert "msg-line" in svg
        assert "seq-arrow" in svg

    def test_has_theme(self):
        svg = render_sequence_svg(SEQUENCE_3_ACTOR)
        assert "prefers-color-scheme" in svg

    def test_two_actor_renders(self):
        svg = render_sequence_svg(SEQUENCE_2_ACTOR)
        assert "Alice" in svg
        assert "Bob" in svg
        assert "Hi!" in svg


# ── Renderlib Tests ──────────────────────────────────────────────────

class TestParseGrid:
    def test_simple(self):
        grid, w, h = parse_grid("abc\ndef")
        assert w == 3
        assert h == 2
        assert grid[0] == ['a', 'b', 'c']
        assert grid[1] == ['d', 'e', 'f']

    def test_uneven_lines(self):
        grid, w, h = parse_grid("ab\ncdef")
        assert w == 4
        assert h == 2
        # Short line padded with spaces
        assert grid[0] == ['a', 'b', ' ', ' ']

    def test_empty(self):
        grid, w, h = parse_grid("")
        assert w == 0
        assert h == 1


class TestFindBoxes:
    def test_single_unicode_box(self):
        grid, w, h = parse_grid(SIMPLE_BOX)
        boxes = find_boxes(grid)
        assert len(boxes) == 1
        box = boxes[0]
        assert box.top == 0
        assert box.left == 0

    def test_single_ascii_box(self):
        grid, w, h = parse_grid(ASCII_BOX)
        boxes = find_boxes(grid)
        assert len(boxes) >= 1

    def test_multiple_boxes(self):
        grid, w, h = parse_grid(HORIZONTAL_FLOW)
        boxes = find_boxes(grid)
        assert len(boxes) == 3

    def test_box_separators(self):
        grid, w, h = parse_grid(SIMPLE_BOX)
        boxes = find_boxes(grid)
        assert len(boxes[0].separators) == 1

    def test_no_boxes_in_text(self):
        grid, w, h = parse_grid("hello world\nfoo bar")
        boxes = find_boxes(grid)
        assert len(boxes) == 0


class TestFindArrows:
    def test_horizontal_arrows(self):
        grid, w, h = parse_grid(HORIZONTAL_FLOW)
        boxes = find_boxes(grid)
        arrows = find_arrows(grid, boxes)
        assert len(arrows) == 2
        assert all(a.direction == "right" for a in arrows)

    def test_vertical_arrows(self):
        grid, w, h = parse_grid(VERTICAL_FLOW)
        boxes = find_boxes(grid)
        arrows = find_arrows(grid, boxes)
        assert len(arrows) == 2
        assert all(a.direction == "down" for a in arrows)

    def test_arrow_box_connections(self):
        grid, w, h = parse_grid(HORIZONTAL_FLOW)
        boxes = find_boxes(grid)
        arrows = find_arrows(grid, boxes)
        # First arrow: Start → Work
        assert arrows[0].from_box == 0
        assert arrows[0].to_box == 1


class TestExtractBoxTexts:
    def test_text_extraction(self):
        grid, w, h = parse_grid(SIMPLE_BOX)
        boxes = find_boxes(grid)
        texts = extract_box_texts(grid, boxes)
        text_strs = [t.text.strip() for t in texts]
        assert "Component Name" in text_strs

    def test_section_assignment(self):
        grid, w, h = parse_grid(SIMPLE_BOX)
        boxes = find_boxes(grid)
        texts = extract_box_texts(grid, boxes)
        # First text should be section 0 (header), others section 1 (body)
        sections = [t.section for t in texts]
        assert 0 in sections
        assert 1 in sections


class TestClassifyHeaders:
    def test_first_text_is_header(self):
        grid, w, h = parse_grid(SIMPLE_BOX)
        boxes = find_boxes(grid)
        texts = extract_box_texts(grid, boxes)
        headers = classify_headers(texts, boxes)
        assert 0 in headers  # first text span is a header
        assert 1 not in headers


class TestSvgHelpers:
    def test_svg_rect(self):
        box = Box(top=0, left=0, bottom=3, right=10)
        svg = svg_rect(box)
        assert "box-border" in svg
        assert "rect" in svg

    def test_svg_text_escaping(self):
        span = TextSpan(row=1, col=1, text="<script>alert('xss')</script>")
        svg = svg_text(span)
        assert "&lt;script&gt;" in svg
        assert "<script>" not in svg

    def test_svg_arrow_forward(self):
        arrow = Arrow(
            points=[(0, 0), (0, 10)],
            direction="right",
        )
        parts = svg_arrow(arrow)
        assert len(parts) >= 1
        assert 'marker-end="url(#arrowhead)"' in parts[0]

    def test_svg_arrow_reverse(self):
        """Reverse arrows still use marker-end since points are source→target ordered."""
        arrow = Arrow(
            points=[(0, 10), (0, 0)],
            direction="left",
        )
        parts = svg_arrow(arrow)
        assert len(parts) >= 1
        assert 'marker-end="url(#arrowhead)"' in parts[0]

    def test_svg_arrowhead_defs(self):
        defs = svg_arrowhead_defs()
        assert "auto-start-reverse" in defs
        assert 'id="arrowhead"' in defs

    def test_svg_arrow_with_label(self):
        arrow = Arrow(
            points=[(0, 0), (0, 10)],
            direction="right",
            label="test label",
        )
        parts = svg_arrow(arrow)
        assert len(parts) == 2
        assert "test label" in parts[1]


# ── State Machine / Multi-Segment Arrow Tests ────────────────────────

class TestStateMachineDetection:
    """State machines are flow diagrams with back-edges (U-shaped arrows)."""

    def test_state_machine_is_flow(self):
        assert has_flow_structure(STATE_MACHINE) is True

    def test_simple_state_machine_is_flow(self):
        assert has_flow_structure(STATE_MACHINE_SIMPLE) is True


class TestStateMachineArrows:
    """Test multi-segment arrow joining for back-edges."""

    def test_back_edge_detected(self):
        """The U-shaped back-edge from Active→Idle should be one arrow."""
        grid, _, _ = parse_grid(STATE_MACHINE)
        boxes = find_boxes(grid)
        arrows = find_arrows(grid, boxes)
        assert len(arrows) == 3

    def test_back_edge_direction(self):
        """Back-edge direction should reflect the arrowhead (^=up)."""
        grid, _, _ = parse_grid(STATE_MACHINE)
        boxes = find_boxes(grid)
        arrows = find_arrows(grid, boxes)
        # Find the back-edge (the one with label)
        back_edge = [a for a in arrows if a.label][0]
        assert back_edge.direction == "up"

    def test_back_edge_box_connections(self):
        """Back-edge should connect Active (from) to Idle (to)."""
        grid, _, _ = parse_grid(STATE_MACHINE)
        boxes = find_boxes(grid)
        arrows = find_arrows(grid, boxes)
        back_edge = [a for a in arrows if a.label][0]
        # from_box should be Active (box 1), to_box should be Idle (box 0)
        assert back_edge.from_box == 1
        assert back_edge.to_box == 0

    def test_back_edge_label(self):
        grid, _, _ = parse_grid(STATE_MACHINE)
        boxes = find_boxes(grid)
        arrows = find_arrows(grid, boxes)
        back_edge = [a for a in arrows if a.label][0]
        assert back_edge.label == "logout"

    def test_forward_arrows_unaffected(self):
        """Forward arrows should still be simple 2-waypoint lines."""
        from mdview.renderlib import _arrow_waypoints
        grid, _, _ = parse_grid(STATE_MACHINE)
        boxes = find_boxes(grid)
        arrows = find_arrows(grid, boxes)
        forward = [a for a in arrows if not a.label]
        for a in forward:
            wps = _arrow_waypoints(a.points)
            assert len(wps) == 2, f"Forward arrow has {len(wps)} waypoints, expected 2"

    def test_polyline_rendering(self):
        """Back-edge renders as SVG polyline (not line)."""
        grid, _, _ = parse_grid(STATE_MACHINE)
        boxes = find_boxes(grid)
        arrows = find_arrows(grid, boxes)
        back_edge = [a for a in arrows if a.label][0]
        parts = svg_arrow(back_edge)
        assert any("polyline" in p for p in parts), "Back-edge should render as polyline"

    def test_full_render(self):
        """Full state machine SVG should contain all elements."""
        svg = render_flow_svg(STATE_MACHINE)
        assert svg is not None
        assert 'class="mdview-diagram"' in svg
        assert "polyline" in svg  # back-edge
        assert "Idle" in svg
        assert "Active" in svg
        assert "Expired" in svg
        assert "logout" in svg

    def test_simple_cycle(self):
        """Simple 2-state cycle (Off→On→Off)."""
        svg = render_flow_svg(STATE_MACHINE_SIMPLE)
        assert svg is not None
        assert "Off" in svg
        assert "On" in svg


# ── Cross-Type Discrimination Tests ─────────────────────────────────

class TestCrossTypeDiscrimination:
    """Ensure each diagram type is NOT misidentified as another type."""

    def test_box_is_only_box(self):
        assert has_box_structure(SIMPLE_BOX) is True
        assert has_flow_structure(SIMPLE_BOX) is False
        assert has_table_structure(SIMPLE_BOX) is False
        assert has_sequence_structure(SIMPLE_BOX) is False

    def test_flow_is_flow_and_box(self):
        """Flow diagrams have boxes, so has_box_structure is True.
        But flow should be detected first in the pipeline."""
        assert has_flow_structure(HORIZONTAL_FLOW) is True
        assert has_box_structure(HORIZONTAL_FLOW) is True  # boxes exist
        assert has_table_structure(HORIZONTAL_FLOW) is False
        assert has_sequence_structure(HORIZONTAL_FLOW) is False

    def test_table_is_only_table(self):
        assert has_table_structure(UNICODE_TABLE) is True
        assert has_flow_structure(UNICODE_TABLE) is False
        assert has_sequence_structure(UNICODE_TABLE) is False

    def test_sequence_is_only_sequence(self):
        assert has_sequence_structure(SEQUENCE_3_ACTOR) is True
        assert has_flow_structure(SEQUENCE_3_ACTOR) is False
        assert has_box_structure(SEQUENCE_3_ACTOR) is False

    def test_file_tree_is_nothing(self):
        """File trees should not match any diagram type."""
        assert has_box_structure(FILE_TREE) is False
        assert has_flow_structure(FILE_TREE) is False
        assert has_table_structure(FILE_TREE) is False
        assert has_sequence_structure(FILE_TREE) is False

    def test_code_is_nothing(self):
        """Code blocks should not match any diagram type."""
        assert has_box_structure(CODE_BLOCK) is False
        assert has_flow_structure(CODE_BLOCK) is False
        assert has_table_structure(CODE_BLOCK) is False
        assert has_sequence_structure(CODE_BLOCK) is False


# ── Edge Cases ───────────────────────────────────────────────────────

class TestEdgeCases:
    def test_minimal_box(self):
        """Smallest possible box."""
        src = "┌─┐\n│x│\n└─┘"
        assert has_box_structure(src) is True

    def test_wide_box(self):
        """Very wide box."""
        border = "┌" + "─" * 100 + "┐"
        content = "│" + " " * 100 + "│"
        bottom = "└" + "─" * 100 + "┘"
        src = f"{border}\n{content}\n{bottom}"
        assert has_box_structure(src) is True

    def test_table_with_many_columns(self):
        """Table with 5+ columns."""
        src = """\
+---+---+---+---+---+
| A | B | C | D | E |
+---+---+---+---+---+
| 1 | 2 | 3 | 4 | 5 |
+---+---+---+---+---+"""
        assert has_table_structure(src) is True

    def test_sequence_four_actors(self):
        """Sequence diagram with 4 actors."""
        src = """\
  A       B       C       D
  │       │       │       │
  │──────>│       │       │
  │       │──────>│       │
  │       │       │──────>│
  │       │       │<──────│
  │       │       │       │"""
        assert has_sequence_structure(src) is True

    def test_empty_string(self):
        """Empty string should not match anything."""
        assert has_box_structure("") is False
        assert has_flow_structure("") is False
        assert has_table_structure("") is False
        assert has_sequence_structure("") is False

    def test_single_line(self):
        """Single line should not match anything."""
        assert has_box_structure("hello") is False
        assert has_flow_structure("hello") is False
        assert has_table_structure("hello") is False
        assert has_sequence_structure("hello") is False
