"""DiagramSpec — the contract between AI interpretation and SVG generation.

The generating AI (or a configured inference backend) produces a DiagramSpec
from ASCII art. The SVG generator consumes it. No heuristic character parsing.

Schema is intentionally simple — a flat list of elements + connections.
The AI provides the structure; the renderer provides the visuals.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class Element:
    """A diagram element (box, actor, panel, cell, etc.)."""

    id: str
    label: str
    type: str  # "node", "actor", "panel", "input", "header", "row", "box"
    children: list[str] = field(default_factory=list)
    properties: dict = field(default_factory=dict)
    # properties examples:
    #   {"sections": [["field1", "field2"]]}  — box with separator
    #   {"cells": ["Name", "Type", "Default"]}  — table row
    #   {"value": "John Doe"}  — form input
    #   {"role": "sidebar"}  — wireframe panel role
    #   {"checked": True}  — checkbox/radio


@dataclass
class Connection:
    """A directed connection between two elements."""

    from_id: str
    to_id: str
    label: str | None = None
    style: str = "solid"  # "solid", "dashed", "dotted"
    properties: dict = field(default_factory=dict)
    # properties examples:
    #   {"order": 1}  — message ordering in sequence diagrams
    #   {"direction": "return"}  — return arrow in sequence


@dataclass
class DiagramSpec:
    """Complete diagram specification.

    Produced by AI interpretation, consumed by SVG generators.
    """

    type: str  # "flow", "sequence", "wireframe", "table", "box"
    elements: list[Element] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
    title: str | None = None
    layout: str = "auto"  # "horizontal", "vertical", "grid", "nested", "sequence", "auto"
    properties: dict = field(default_factory=dict)
    # properties examples:
    #   {"columns": 3}  — table column count

    def to_dict(self) -> dict:
        """Serialize to plain dict (for JSON output)."""
        return {
            "type": self.type,
            "title": self.title,
            "layout": self.layout,
            "elements": [
                {
                    "id": e.id,
                    "label": e.label,
                    "type": e.type,
                    **({"children": e.children} if e.children else {}),
                    **({"properties": e.properties} if e.properties else {}),
                }
                for e in self.elements
            ],
            "connections": [
                {
                    "from": c.from_id,
                    "to": c.to_id,
                    **({"label": c.label} if c.label else {}),
                    **({"style": c.style} if c.style != "solid" else {}),
                    **({"properties": c.properties} if c.properties else {}),
                }
                for c in self.connections
            ],
            **({"properties": self.properties} if self.properties else {}),
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict) -> DiagramSpec:
        """Deserialize from a dict (parsed JSON)."""
        elements = []
        for e in data.get("elements", []):
            elements.append(Element(
                id=e["id"],
                label=e.get("label", ""),
                type=e.get("type", "node"),
                children=e.get("children", []),
                properties=e.get("properties", {}),
            ))

        connections = []
        for c in data.get("connections", []):
            connections.append(Connection(
                from_id=c["from"],
                to_id=c["to"],
                label=c.get("label"),
                style=c.get("style", "solid"),
                properties=c.get("properties", {}),
            ))

        return cls(
            type=data["type"],
            elements=elements,
            connections=connections,
            title=data.get("title"),
            layout=data.get("layout", "auto"),
            properties=data.get("properties", {}),
        )

    @classmethod
    def from_json(cls, json_str: str) -> DiagramSpec:
        """Deserialize from a JSON string."""
        return cls.from_dict(json.loads(json_str))


# ── Validation ────────────────────────────────────────────────────

VALID_TYPES = {"flow", "sequence", "wireframe", "table", "box"}
VALID_LAYOUTS = {"auto", "horizontal", "vertical", "grid", "nested", "sequence"}


def validate_spec(spec: DiagramSpec) -> list[str]:
    """Validate a DiagramSpec. Returns list of error messages (empty = valid)."""
    errors: list[str] = []

    if spec.type not in VALID_TYPES:
        errors.append(f"Unknown diagram type: {spec.type!r} (valid: {VALID_TYPES})")

    if spec.layout not in VALID_LAYOUTS:
        errors.append(f"Unknown layout: {spec.layout!r} (valid: {VALID_LAYOUTS})")

    # Check element IDs are unique
    ids = [e.id for e in spec.elements]
    dupes = [eid for eid in ids if ids.count(eid) > 1]
    if dupes:
        errors.append(f"Duplicate element IDs: {set(dupes)}")

    # Check connections reference valid elements
    id_set = set(ids)
    for conn in spec.connections:
        if conn.from_id not in id_set:
            errors.append(f"Connection from unknown element: {conn.from_id!r}")
        if conn.to_id not in id_set:
            errors.append(f"Connection to unknown element: {conn.to_id!r}")

    # Check children reference valid elements
    for elem in spec.elements:
        for child_id in elem.children:
            if child_id not in id_set:
                errors.append(f"Element {elem.id!r} has unknown child: {child_id!r}")

    return errors
