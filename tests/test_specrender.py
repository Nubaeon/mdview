"""Tests for spec-based SVG rendering."""

import pytest
from mdview.spec import DiagramSpec, Element, Connection
from mdview.specrender import render_spec_svg


# ── Flow rendering ─────────────────────────────────────────────────

class TestFlowRendering:

    def test_basic_flow(self):
        spec = DiagramSpec(
            type="flow",
            elements=[
                Element(id="a", label="Start", type="node"),
                Element(id="b", label="Process", type="node"),
                Element(id="c", label="End", type="node"),
            ],
            connections=[
                Connection(from_id="a", to_id="b", label="step 1"),
                Connection(from_id="b", to_id="c"),
            ],
        )
        svg = render_spec_svg(spec)
        assert '<svg' in svg
        assert '</svg>' in svg
        assert 'Start' in svg
        assert 'Process' in svg
        assert 'End' in svg
        assert 'step 1' in svg
        assert 'class="mdview-diagram"' in svg

    def test_vertical_flow(self):
        spec = DiagramSpec(
            type="flow",
            layout="vertical",
            elements=[
                Element(id="a", label="Top", type="node"),
                Element(id="b", label="Bottom", type="node"),
            ],
            connections=[Connection(from_id="a", to_id="b")],
        )
        svg = render_spec_svg(spec)
        assert 'Top' in svg
        assert 'Bottom' in svg

    def test_decision_node(self):
        spec = DiagramSpec(
            type="flow",
            elements=[
                Element(id="d", label="Check?", type="decision"),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'polygon' in svg
        assert 'Check?' in svg

    def test_empty_flow_fallback(self):
        spec = DiagramSpec(type="flow")
        svg = render_spec_svg(spec)
        assert '<svg' in svg
        assert '[flow]' in svg

    def test_dashed_connection(self):
        spec = DiagramSpec(
            type="flow",
            elements=[
                Element(id="a", label="A", type="node"),
                Element(id="b", label="B", type="node"),
            ],
            connections=[Connection(from_id="a", to_id="b", style="dashed")],
        )
        svg = render_spec_svg(spec)
        assert 'stroke-dasharray' in svg


# ── Sequence rendering ─────────────────────────────────────────────

class TestSequenceRendering:

    def test_basic_sequence(self):
        spec = DiagramSpec(
            type="sequence",
            layout="sequence",
            elements=[
                Element(id="client", label="Client", type="actor"),
                Element(id="server", label="Server", type="actor"),
            ],
            connections=[
                Connection(from_id="client", to_id="server", label="request",
                           properties={"order": 1}),
                Connection(from_id="server", to_id="client", label="response",
                           properties={"order": 2}),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'Client' in svg
        assert 'Server' in svg
        assert 'request' in svg
        assert 'response' in svg
        assert 'lifeline' in svg
        assert 'actor-box' in svg

    def test_three_actors(self):
        spec = DiagramSpec(
            type="sequence",
            elements=[
                Element(id="a", label="A", type="actor"),
                Element(id="b", label="B", type="actor"),
                Element(id="c", label="C", type="actor"),
            ],
            connections=[
                Connection(from_id="a", to_id="b", label="m1",
                           properties={"order": 1}),
                Connection(from_id="b", to_id="c", label="m2",
                           properties={"order": 2}),
            ],
        )
        svg = render_spec_svg(spec)
        # Should have 3 lifelines
        assert svg.count('class="lifeline"') == 3

    def test_sequence_ordering(self):
        spec = DiagramSpec(
            type="sequence",
            elements=[
                Element(id="a", label="A", type="actor"),
                Element(id="b", label="B", type="actor"),
            ],
            connections=[
                Connection(from_id="b", to_id="a", label="second",
                           properties={"order": 2}),
                Connection(from_id="a", to_id="b", label="first",
                           properties={"order": 1}),
            ],
        )
        svg = render_spec_svg(spec)
        # Both labels should appear
        assert 'first' in svg
        assert 'second' in svg

    def test_sequence_too_few_actors(self):
        spec = DiagramSpec(
            type="sequence",
            elements=[Element(id="a", label="A", type="actor")],
        )
        svg = render_spec_svg(spec)
        # Falls back
        assert '[sequence]' in svg


# ── Wireframe rendering ────────────────────────────────────────────

class TestWireframeRendering:

    def test_nested_wireframe(self):
        spec = DiagramSpec(
            type="wireframe",
            layout="nested",
            elements=[
                Element(id="outer", label="App", type="panel",
                        children=["nav", "main"]),
                Element(id="nav", label="Navigation", type="sidebar"),
                Element(id="main", label="Content", type="panel"),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'App' in svg
        assert 'Navigation' in svg
        assert 'Content' in svg
        assert 'wf-panel' in svg

    def test_wireframe_with_input(self):
        spec = DiagramSpec(
            type="wireframe",
            elements=[
                Element(id="form", label="Login", type="panel",
                        children=["email"]),
                Element(id="email", label="Email", type="input",
                        properties={"value": "user@example.com"}),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'Login' in svg
        assert 'user@example.com' in svg
        assert 'wf-input' in svg

    def test_wireframe_with_form(self):
        spec = DiagramSpec(
            type="wireframe",
            elements=[
                Element(id="f", label="Profile Form", type="form"),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'Profile Form' in svg


# ── Table rendering ────────────────────────────────────────────────

class TestTableRendering:

    def test_basic_table(self):
        spec = DiagramSpec(
            type="table",
            elements=[
                Element(id="h", label="", type="header",
                        properties={"cells": ["Name", "Type", "Default"]}),
                Element(id="r1", label="", type="row",
                        properties={"cells": ["host", "string", "localhost"]}),
                Element(id="r2", label="", type="row",
                        properties={"cells": ["port", "int", "8080"]}),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'Name' in svg
        assert 'Type' in svg
        assert 'Default' in svg
        assert 'host' in svg
        assert '8080' in svg
        assert 'table-header-bg' in svg
        assert 'table-header-text' in svg
        assert 'table-cell-text' in svg

    def test_table_without_header(self):
        spec = DiagramSpec(
            type="table",
            elements=[
                Element(id="r1", label="", type="row",
                        properties={"cells": ["A", "B"]}),
                Element(id="r2", label="", type="row",
                        properties={"cells": ["C", "D"]}),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'A' in svg
        assert 'D' in svg

    def test_empty_table_fallback(self):
        spec = DiagramSpec(type="table")
        svg = render_spec_svg(spec)
        assert '[table]' in svg


# ── Box rendering ──────────────────────────────────────────────────

class TestBoxRendering:

    def test_simple_box(self):
        spec = DiagramSpec(
            type="box",
            elements=[
                Element(id="comp", label="Component", type="box"),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'Component' in svg
        assert 'box-border' in svg

    def test_box_with_sections(self):
        spec = DiagramSpec(
            type="box",
            elements=[
                Element(id="cls", label="MyClass", type="box",
                        properties={"sections": [
                            ["name: String", "count: Int"],
                            ["getName()", "getCount()"],
                        ]}),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'MyClass' in svg
        assert 'name: String' in svg
        assert 'getName()' in svg
        assert 'box-separator' in svg

    def test_multiple_boxes_horizontal(self):
        spec = DiagramSpec(
            type="box",
            layout="horizontal",
            elements=[
                Element(id="a", label="Box A", type="box"),
                Element(id="b", label="Box B", type="box"),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'Box A' in svg
        assert 'Box B' in svg

    def test_box_with_connections(self):
        spec = DiagramSpec(
            type="box",
            elements=[
                Element(id="a", label="A", type="box"),
                Element(id="b", label="B", type="box"),
            ],
            connections=[Connection(from_id="a", to_id="b", label="uses")],
        )
        svg = render_spec_svg(spec)
        assert 'arrowhead' in svg
        assert 'uses' in svg


# ── Unknown type ───────────────────────────────────────────────────

class TestUnknownType:

    def test_unknown_type_fallback(self):
        spec = DiagramSpec(type="unknown_thing")
        svg = render_spec_svg(spec)
        assert '<svg' in svg
        assert '[unknown_thing]' in svg


# ── Theme integration ──────────────────────────────────────────────

class TestThemeIntegration:

    def test_has_theme_css(self):
        spec = DiagramSpec(
            type="flow",
            elements=[Element(id="a", label="A", type="node")],
        )
        svg = render_spec_svg(spec)
        # Should have theme CSS with dark/light media query
        assert 'prefers-color-scheme' in svg

    def test_custom_theme(self):
        from mdview.themes import Theme, ThemeColors
        custom = Theme(
            name="test",
            dark=ThemeColors(
                bg="#000", bg_secondary="#111", fg="#fff",
                heading="#f00", header_text="#0f0", label="#ff0",
                border="#00f", separator="#0ff", muted="#888",
                arrow="#f0f", arrow_label_bg="#000",
            ),
            light=ThemeColors(
                bg="#fff", bg_secondary="#eee", fg="#000",
                heading="#00f", header_text="#080", label="#880",
                border="#00f", separator="#0ff", muted="#888",
                arrow="#80f", arrow_label_bg="#fff",
            ),
        )
        spec = DiagramSpec(
            type="flow",
            elements=[Element(id="a", label="A", type="node")],
        )
        svg = render_spec_svg(spec, theme=custom)
        assert '#000' in svg  # dark bg
        assert '#fff' in svg  # light bg


# ── SVG structure ──────────────────────────────────────────────────

class TestSvgStructure:

    def test_valid_svg_wrapper(self):
        spec = DiagramSpec(
            type="flow",
            elements=[Element(id="a", label="A", type="node")],
        )
        svg = render_spec_svg(spec)
        assert svg.startswith('<svg')
        assert svg.endswith('</svg>')
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg

    def test_has_background(self):
        spec = DiagramSpec(
            type="box",
            elements=[Element(id="a", label="A", type="box")],
        )
        svg = render_spec_svg(spec)
        assert 'class="bg"' in svg

    def test_html_escaping(self):
        spec = DiagramSpec(
            type="box",
            elements=[Element(id="a", label="A <script>", type="box")],
        )
        svg = render_spec_svg(spec)
        assert '&lt;script&gt;' in svg
        assert '<script>' not in svg
