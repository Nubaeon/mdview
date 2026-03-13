"""Randomized stress tests for spec-based rendering pipeline.

Generates random DiagramSpecs with varying element counts, label lengths,
connection patterns, and layout options to catch edge cases that predefined
tests miss. Each test run produces different inputs.
"""

import random
import re
import string

import pytest
from mdview.spec import DiagramSpec, Element, Connection
from mdview.specrender import render_spec_svg


def _random_label(min_len: int = 2, max_len: int = 25) -> str:
    length = random.randint(min_len, max_len)
    return "".join(random.choices(string.ascii_letters + " ", k=length)).strip() or "X"


def _random_id(prefix: str = "n") -> str:
    return f"{prefix}{random.randint(0, 9999)}"


def _validate_svg(svg: str, diagram_type: str) -> None:
    """Common SVG validation assertions."""
    assert svg.startswith("<svg"), f"{diagram_type}: doesn't start with <svg"
    assert svg.endswith("</svg>"), f"{diagram_type}: doesn't end with </svg>"
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg
    assert 'class="mdview-diagram"' in svg
    assert "prefers-color-scheme" in svg, f"{diagram_type}: missing theme CSS"

    # Check dimensions are positive
    m = re.search(r'width="(\d+)" height="(\d+)"', svg)
    assert m, f"{diagram_type}: no width/height found"
    w, h = int(m.group(1)), int(m.group(2))
    assert w > 0 and h > 0, f"{diagram_type}: zero dimensions {w}x{h}"
    assert w < 3000, f"{diagram_type}: unreasonably wide {w}px"
    assert h < 3000, f"{diagram_type}: unreasonably tall {h}px"

    # No negative coordinates in critical positions
    for match in re.finditer(r'(?:x|x1|x2|cx)="(-?\d+\.?\d*)"', svg):
        val = float(match.group(1))
        assert val >= -5, f"{diagram_type}: negative x coord {val}"

    # Check for unclosed tags (basic well-formedness)
    assert svg.count("<svg") == 1
    assert svg.count("</svg>") == 1


def _check_unique_ids(svg: str, diagram_type: str) -> None:
    """Verify no duplicate element IDs within a single SVG."""
    ids = re.findall(r'id="([^"]+)"', svg)
    seen = set()
    for eid in ids:
        assert eid not in seen, f"{diagram_type}: duplicate ID '{eid}'"
        seen.add(eid)


# ── Randomized flow diagrams ─────────────────────────────────────

class TestRandomFlow:

    @pytest.mark.parametrize("seed", range(10))
    def test_random_flow_horizontal(self, seed: int) -> None:
        random.seed(seed)
        n = random.randint(2, 12)
        elements = []
        for i in range(n):
            etype = random.choice(["node", "node", "node", "decision"])
            elements.append(Element(
                id=_random_id("f"), label=_random_label(), type=etype,
            ))

        connections = []
        for i in range(n - 1):
            connections.append(Connection(
                from_id=elements[i].id, to_id=elements[i + 1].id,
                label=_random_label(1, 10) if random.random() > 0.3 else "",
            ))

        spec = DiagramSpec(type="flow", layout="horizontal", elements=elements,
                          connections=connections)
        svg = render_spec_svg(spec)
        _validate_svg(svg, f"flow-h-seed{seed}")
        _check_unique_ids(svg, f"flow-h-seed{seed}")

    @pytest.mark.parametrize("seed", range(10))
    def test_random_flow_vertical(self, seed: int) -> None:
        random.seed(seed + 100)
        n = random.randint(2, 10)
        elements = [Element(id=_random_id("v"), label=_random_label(), type="node")
                    for _ in range(n)]
        connections = [Connection(from_id=elements[i].id, to_id=elements[i + 1].id)
                      for i in range(n - 1)]

        spec = DiagramSpec(type="flow", layout="vertical", elements=elements,
                          connections=connections)
        svg = render_spec_svg(spec)
        _validate_svg(svg, f"flow-v-seed{seed}")


# ── Randomized sequence diagrams ─────────────────────────────────

class TestRandomSequence:

    @pytest.mark.parametrize("seed", range(10))
    def test_random_sequence(self, seed: int) -> None:
        random.seed(seed + 200)
        n_actors = random.randint(2, 6)
        actors = [Element(id=_random_id("a"), label=_random_label(3, 20), type="actor")
                  for _ in range(n_actors)]

        n_msgs = random.randint(1, 15)
        connections = []
        for i in range(n_msgs):
            fi = random.randint(0, n_actors - 1)
            ti = random.randint(0, n_actors - 1)
            while ti == fi:
                ti = random.randint(0, n_actors - 1)
            connections.append(Connection(
                from_id=actors[fi].id, to_id=actors[ti].id,
                label=_random_label(2, 15),
                properties={"order": i + 1},
                style=random.choice(["solid", "dashed"]),
            ))

        spec = DiagramSpec(type="sequence", elements=actors, connections=connections)
        svg = render_spec_svg(spec)
        _validate_svg(svg, f"seq-seed{seed}")
        # All actor labels should appear
        for a in actors:
            assert a.label in svg or a.id in svg


# ── Randomized box diagrams ──────────────────────────────────────

class TestRandomBox:

    @pytest.mark.parametrize("seed", range(10))
    def test_random_box(self, seed: int) -> None:
        random.seed(seed + 300)
        n = random.randint(1, 8)
        elements = []
        for _ in range(n):
            n_sections = random.randint(0, 4)
            sections = []
            for _ in range(n_sections):
                n_lines = random.randint(1, 5)
                sections.append([_random_label(3, 20) for _ in range(n_lines)])
            elements.append(Element(
                id=_random_id("b"), label=_random_label(3, 18), type="box",
                properties={"sections": sections},
            ))

        # Random connections between boxes
        connections = []
        for i in range(min(n - 1, random.randint(0, n))):
            fi = random.randint(0, n - 1)
            ti = random.randint(0, n - 1)
            if fi != ti:
                connections.append(Connection(
                    from_id=elements[fi].id, to_id=elements[ti].id,
                    label=_random_label(1, 8) if random.random() > 0.5 else "",
                ))

        spec = DiagramSpec(type="box", layout=random.choice(["horizontal", "vertical"]),
                          elements=elements, connections=connections)
        svg = render_spec_svg(spec)
        _validate_svg(svg, f"box-seed{seed}")
        _check_unique_ids(svg, f"box-seed{seed}")


# ── Randomized state machines ────────────────────────────────────

class TestRandomStateMachine:

    @pytest.mark.parametrize("seed", range(10))
    def test_random_state_machine(self, seed: int) -> None:
        random.seed(seed + 400)
        n = random.randint(2, 10)
        elements = []
        for i in range(n):
            etype = "initial" if i == 0 else "node"
            elements.append(Element(
                id=_random_id("s"), label=_random_label(3, 12), type=etype,
            ))

        # Forward edges + optional back-edges and self-loops
        connections = []
        for i in range(n - 1):
            connections.append(Connection(
                from_id=elements[i].id, to_id=elements[i + 1].id,
                label=_random_label(2, 8),
            ))
        # Random back-edges
        for _ in range(random.randint(0, 3)):
            fi = random.randint(1, n - 1)
            ti = random.randint(0, fi - 1) if fi > 0 else 0
            connections.append(Connection(
                from_id=elements[fi].id, to_id=elements[ti].id,
                label=_random_label(2, 8), style="dashed",
            ))
        # Random self-loop
        if random.random() > 0.5:
            idx = random.randint(0, n - 1)
            connections.append(Connection(
                from_id=elements[idx].id, to_id=elements[idx].id,
                label=_random_label(2, 6),
            ))

        spec = DiagramSpec(type="state_machine", elements=elements,
                          connections=connections)
        svg = render_spec_svg(spec)
        _validate_svg(svg, f"sm-seed{seed}")
        _check_unique_ids(svg, f"sm-seed{seed}")


# ── Randomized wireframes ────────────────────────────────────────

class TestRandomWireframe:

    @pytest.mark.parametrize("seed", range(10))
    def test_random_wireframe(self, seed: int) -> None:
        random.seed(seed + 500)
        elements = []
        # Root panel with 2-4 children
        n_children = random.randint(2, 4)
        child_ids = [_random_id("c") for _ in range(n_children)]
        elements.append(Element(
            id="root", label=_random_label(4, 15), type="panel",
            children=child_ids,
        ))
        for cid in child_ids:
            ctype = random.choice(["panel", "sidebar", "input", "form"])
            if ctype in ("panel", "sidebar") and random.random() > 0.5:
                # Nested children
                n_nested = random.randint(1, 3)
                nested_ids = [_random_id("n") for _ in range(n_nested)]
                elements.append(Element(
                    id=cid, label=_random_label(3, 12), type=ctype,
                    children=nested_ids,
                ))
                for nid in nested_ids:
                    ntype = random.choice(["panel", "input", "form"])
                    props = {"value": _random_label(5, 20)} if ntype == "input" else {}
                    elements.append(Element(
                        id=nid, label=_random_label(3, 10), type=ntype,
                        properties=props,
                    ))
            else:
                props = {"value": _random_label(5, 20)} if ctype == "input" else {}
                elements.append(Element(
                    id=cid, label=_random_label(3, 12), type=ctype,
                    properties=props,
                ))

        spec = DiagramSpec(type="wireframe", layout="nested", elements=elements)
        svg = render_spec_svg(spec)
        _validate_svg(svg, f"wf-seed{seed}")


# ── Randomized tables ────────────────────────────────────────────

class TestRandomTable:

    @pytest.mark.parametrize("seed", range(10))
    def test_random_table(self, seed: int) -> None:
        random.seed(seed + 600)
        n_cols = random.randint(2, 7)
        n_rows = random.randint(1, 10)

        header = Element(
            id="h", label="", type="header",
            properties={"cells": [_random_label(3, 15) for _ in range(n_cols)]},
        )
        rows = []
        for i in range(n_rows):
            rows.append(Element(
                id=f"r{i}", label="", type="row",
                properties={"cells": [_random_label(1, 20) for _ in range(n_cols)]},
            ))

        spec = DiagramSpec(type="table", elements=[header] + rows)
        svg = render_spec_svg(spec)
        _validate_svg(svg, f"table-seed{seed}")


# ── Cross-diagram uniqueness ─────────────────────────────────────

class TestMultipleDiagramsOnPage:

    def test_no_id_collisions_across_diagrams(self) -> None:
        """Multiple diagrams rendered in sequence must have unique IDs."""
        specs = [
            DiagramSpec(type="flow", elements=[
                Element(id="a", label="A", type="node"),
                Element(id="b", label="B", type="node"),
            ], connections=[Connection(from_id="a", to_id="b")]),
            DiagramSpec(type="box", elements=[
                Element(id="a", label="A", type="box"),
                Element(id="b", label="B", type="box"),
            ], connections=[Connection(from_id="a", to_id="b")]),
            DiagramSpec(type="state_machine", elements=[
                Element(id="a", label="A", type="initial"),
                Element(id="b", label="B", type="node"),
            ], connections=[Connection(from_id="a", to_id="b")]),
        ]

        all_ids: list[str] = []
        for spec in specs:
            svg = render_spec_svg(spec)
            ids = re.findall(r'id="([^"]+)"', svg)
            all_ids.extend(ids)

        # Every ID across all SVGs should be unique
        assert len(all_ids) == len(set(all_ids)), (
            f"Duplicate IDs across diagrams: "
            f"{[x for x in all_ids if all_ids.count(x) > 1]}"
        )

    def test_html_special_chars_in_random_labels(self) -> None:
        """Labels with special HTML chars shouldn't break SVG."""
        spec = DiagramSpec(type="flow", elements=[
            Element(id="a", label='A & B <C> "D"', type="node"),
            Element(id="b", label="E > F", type="node"),
        ], connections=[
            Connection(from_id="a", to_id="b", label="x < y"),
        ])
        svg = render_spec_svg(spec)
        _validate_svg(svg, "html-escape")
        assert "&amp;" in svg
        assert "&lt;" in svg
        assert "<script>" not in svg
