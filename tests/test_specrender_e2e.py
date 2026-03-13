"""End-to-end tests for spec-based rendering pipeline.

Tests the full flow: construct DiagramSpec → render_spec_svg → validate SVG structure.
Covers all 6 diagram types with realistic specs.
"""

import re
import pytest
from mdview.spec import DiagramSpec, Element, Connection, validate_spec
from mdview.specrender import render_spec_svg


def _svg_has_element(svg: str, tag: str, **attrs) -> bool:
    """Check if SVG contains an element with given tag and attributes."""
    for key, val in attrs.items():
        pattern = f'<{tag}[^>]*{key}="[^"]*{re.escape(val)}[^"]*"'
        if re.search(pattern, svg):
            return True
    return False


def _count_elements(svg: str, css_class: str) -> int:
    """Count SVG elements with a given CSS class."""
    return len(re.findall(f'class="[^"]*{re.escape(css_class)}[^"]*"', svg))


# ── State machine E2E ──────────────────────────────────────────────

class TestStateMachineE2E:

    def test_basic_state_machine(self):
        spec = DiagramSpec(
            type="state_machine",
            elements=[
                Element(id="idle", label="Idle", type="initial"),
                Element(id="running", label="Running", type="node"),
                Element(id="done", label="Done", type="node"),
            ],
            connections=[
                Connection(from_id="idle", to_id="running", label="start"),
                Connection(from_id="running", to_id="done", label="finish"),
            ],
        )
        assert validate_spec(spec) == []
        svg = render_spec_svg(spec)
        assert 'Idle' in svg
        assert 'Running' in svg
        assert 'Done' in svg
        assert 'start' in svg
        assert 'finish' in svg
        assert 'state-node' in svg
        assert 'state-initial' in svg

    def test_self_loop(self):
        spec = DiagramSpec(
            type="state_machine",
            elements=[
                Element(id="s", label="Processing", type="node"),
            ],
            connections=[
                Connection(from_id="s", to_id="s", label="retry"),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'retry' in svg
        # Self-loop uses <path> with curve, not <line>
        assert '<path' in svg

    def test_back_edge(self):
        spec = DiagramSpec(
            type="state_machine",
            elements=[
                Element(id="a", label="Start", type="initial"),
                Element(id="b", label="Process", type="node"),
                Element(id="c", label="Error", type="node"),
            ],
            connections=[
                Connection(from_id="a", to_id="b", label="go"),
                Connection(from_id="b", to_id="c", label="fail"),
                Connection(from_id="c", to_id="a", label="reset", style="dashed"),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'reset' in svg
        # Back-edge uses curved path
        assert svg.count('<path') >= 1
        # Dashed back-edge
        assert 'stroke-dasharray' in svg

    def test_complex_state_machine(self):
        """Full order lifecycle with back-edges and multiple transitions."""
        spec = DiagramSpec(
            type="state_machine",
            title="Order Lifecycle",
            elements=[
                Element(id="new", label="New", type="initial"),
                Element(id="pending", label="Pending", type="node"),
                Element(id="paid", label="Paid", type="node"),
                Element(id="shipped", label="Shipped", type="node"),
                Element(id="delivered", label="Delivered", type="node"),
                Element(id="cancelled", label="Cancelled", type="node"),
            ],
            connections=[
                Connection(from_id="new", to_id="pending", label="checkout"),
                Connection(from_id="pending", to_id="paid", label="pay"),
                Connection(from_id="pending", to_id="cancelled", label="timeout"),
                Connection(from_id="paid", to_id="shipped", label="ship"),
                Connection(from_id="shipped", to_id="delivered", label="deliver"),
                Connection(from_id="cancelled", to_id="new", label="retry",
                           style="dashed"),
            ],
        )
        assert validate_spec(spec) == []
        svg = render_spec_svg(spec)
        # All states present
        for label in ["New", "Pending", "Paid", "Shipped", "Delivered", "Cancelled"]:
            assert label in svg
        # All transitions
        for label in ["checkout", "pay", "timeout", "ship", "deliver", "retry"]:
            assert label in svg
        # Has arrowhead markers
        assert 'marker-end="url(#d' in svg


# ── Flow E2E ───────────────────────────────────────────────────────

class TestFlowE2E:

    def test_cicd_pipeline(self):
        spec = DiagramSpec(
            type="flow",
            layout="horizontal",
            elements=[
                Element(id="push", label="Git Push", type="node"),
                Element(id="build", label="Build", type="node"),
                Element(id="test", label="Test", type="node"),
                Element(id="check", label="Pass?", type="decision"),
                Element(id="deploy", label="Deploy", type="node"),
            ],
            connections=[
                Connection(from_id="push", to_id="build", label="trigger"),
                Connection(from_id="build", to_id="test"),
                Connection(from_id="test", to_id="check"),
                Connection(from_id="check", to_id="deploy", label="yes"),
            ],
        )
        assert validate_spec(spec) == []
        svg = render_spec_svg(spec)
        assert _count_elements(svg, "box-border") >= 4  # rects
        assert 'polygon' in svg  # decision diamond
        assert 'trigger' in svg
        assert 'marker-end="url(#d' in svg


# ── Sequence E2E ───────────────────────────────────────────────────

class TestSequenceE2E:

    def test_auth_flow(self):
        spec = DiagramSpec(
            type="sequence",
            elements=[
                Element(id="browser", label="Browser", type="actor"),
                Element(id="api", label="API", type="actor"),
                Element(id="db", label="DB", type="actor"),
            ],
            connections=[
                Connection(from_id="browser", to_id="api", label="request",
                           properties={"order": 1}),
                Connection(from_id="api", to_id="db", label="query",
                           properties={"order": 2}),
                Connection(from_id="db", to_id="api", label="result",
                           properties={"order": 3}, style="dashed"),
                Connection(from_id="api", to_id="browser", label="response",
                           properties={"order": 4}, style="dashed"),
            ],
        )
        assert validate_spec(spec) == []
        svg = render_spec_svg(spec)
        assert _count_elements(svg, "actor-box") == 6  # 3 top + 3 bottom
        assert _count_elements(svg, "lifeline") == 3
        assert svg.count('stroke-dasharray') >= 2  # dashed responses


# ── Table E2E ──────────────────────────────────────────────────────

class TestTableE2E:

    def test_api_endpoints_table(self):
        spec = DiagramSpec(
            type="table",
            elements=[
                Element(id="h", label="", type="header",
                        properties={"cells": ["Method", "Path", "Auth"]}),
                Element(id="r1", label="", type="row",
                        properties={"cells": ["GET", "/users", "JWT"]}),
                Element(id="r2", label="", type="row",
                        properties={"cells": ["POST", "/users", "Admin"]}),
            ],
        )
        svg = render_spec_svg(spec)
        assert 'table-header-bg' in svg
        assert 'Method' in svg
        assert '/users' in svg
        assert _count_elements(svg, "table-cell-text") >= 6


# ── Wireframe E2E ──────────────────────────────────────────────────

class TestWireframeE2E:

    def test_dashboard_wireframe(self):
        spec = DiagramSpec(
            type="wireframe",
            layout="nested",
            elements=[
                Element(id="app", label="App", type="panel",
                        children=["sidebar", "content"]),
                Element(id="sidebar", label="Nav", type="sidebar"),
                Element(id="content", label="Main", type="panel",
                        children=["search"]),
                Element(id="search", label="Search", type="input",
                        properties={"value": "Search..."}),
            ],
        )
        assert validate_spec(spec) == []
        svg = render_spec_svg(spec)
        assert 'wf-panel' in svg
        assert 'wf-input' in svg
        assert 'Search...' in svg
        # Nested structure: multiple panel rects
        assert _count_elements(svg, "wf-panel") >= 3


# ── Box E2E ────────────────────────────────────────────────────────

class TestBoxE2E:

    def test_class_diagram(self):
        spec = DiagramSpec(
            type="box",
            layout="horizontal",
            elements=[
                Element(id="user", label="User", type="box",
                        properties={"sections": [
                            ["id: UUID", "email: String"],
                            ["login()", "logout()"],
                        ]}),
                Element(id="role", label="Role", type="box",
                        properties={"sections": [
                            ["name: String"],
                        ]}),
            ],
            connections=[
                Connection(from_id="user", to_id="role", label="has"),
            ],
        )
        assert validate_spec(spec) == []
        svg = render_spec_svg(spec)
        assert 'User' in svg
        assert 'Role' in svg
        assert 'id: UUID' in svg
        assert 'login()' in svg
        assert 'has' in svg
        assert _count_elements(svg, "box-separator") >= 2


# ── Cross-cutting ──────────────────────────────────────────────────

class TestCrossCutting:

    def test_all_types_produce_valid_svg(self):
        """Every supported type produces well-formed SVG."""
        specs = [
            DiagramSpec(type="flow", elements=[Element(id="a", label="A", type="node")]),
            DiagramSpec(type="sequence", elements=[
                Element(id="a", label="A", type="actor"),
                Element(id="b", label="B", type="actor"),
            ], connections=[
                Connection(from_id="a", to_id="b", label="msg", properties={"order": 1}),
            ]),
            DiagramSpec(type="wireframe", elements=[
                Element(id="p", label="Panel", type="panel"),
            ]),
            DiagramSpec(type="table", elements=[
                Element(id="h", label="", type="header", properties={"cells": ["A"]}),
                Element(id="r", label="", type="row", properties={"cells": ["1"]}),
            ]),
            DiagramSpec(type="box", elements=[
                Element(id="b", label="Box", type="box"),
            ]),
            DiagramSpec(type="state_machine", elements=[
                Element(id="s", label="Start", type="initial"),
                Element(id="e", label="End", type="node"),
            ], connections=[
                Connection(from_id="s", to_id="e", label="go"),
            ]),
        ]

        for spec in specs:
            svg = render_spec_svg(spec)
            assert svg.startswith('<svg'), f"{spec.type} SVG doesn't start with <svg"
            assert svg.endswith('</svg>'), f"{spec.type} SVG doesn't end with </svg>"
            assert 'xmlns="http://www.w3.org/2000/svg"' in svg
            assert 'class="mdview-diagram"' in svg
            assert 'prefers-color-scheme' in svg, f"{spec.type} missing theme CSS"

    def test_spec_validation_catches_bad_refs(self):
        """Validation catches broken references before rendering."""
        spec = DiagramSpec(
            type="state_machine",
            elements=[Element(id="a", label="A", type="node")],
            connections=[Connection(from_id="a", to_id="missing", label="bad")],
        )
        errors = validate_spec(spec)
        assert any("unknown" in e for e in errors)
        # Should still render (partial specs are ok)
        svg = render_spec_svg(spec)
        assert '<svg' in svg

    def test_special_characters_escaped(self):
        """HTML special chars in labels are properly escaped."""
        spec = DiagramSpec(
            type="flow",
            elements=[
                Element(id="a", label="A & B <test>", type="node"),
                Element(id="b", label='C "quoted"', type="node"),
            ],
            connections=[
                Connection(from_id="a", to_id="b", label="x > y"),
            ],
        )
        svg = render_spec_svg(spec)
        assert '&amp;' in svg
        assert '&lt;test&gt;' in svg
        assert '&quot;' in svg or '"quoted"' not in svg
        assert '<script>' not in svg
