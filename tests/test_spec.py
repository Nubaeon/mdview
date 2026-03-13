"""Tests for DiagramSpec schema, config, and provider interface."""

import json
import pytest
from mdview.spec import DiagramSpec, Element, Connection, validate_spec, VALID_TYPES
from mdview.config import MdviewConfig, AIConfig
from mdview.providers import _parse_spec_response, create_provider


# ── DiagramSpec roundtrip ────────────────────────────────────────

class TestDiagramSpecRoundtrip:
    """Test serialization/deserialization."""

    def test_flow_roundtrip(self):
        spec = DiagramSpec(
            type="flow",
            layout="horizontal",
            elements=[
                Element(id="input", label="Input", type="node"),
                Element(id="process", label="Process", type="node"),
                Element(id="output", label="Output", type="node"),
            ],
            connections=[
                Connection(from_id="input", to_id="process", label="data"),
                Connection(from_id="process", to_id="output"),
            ],
        )
        json_str = spec.to_json()
        restored = DiagramSpec.from_json(json_str)
        assert restored.type == "flow"
        assert len(restored.elements) == 3
        assert len(restored.connections) == 2
        assert restored.connections[0].label == "data"

    def test_sequence_roundtrip(self):
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
        d = spec.to_dict()
        assert d["connections"][0]["properties"]["order"] == 1
        restored = DiagramSpec.from_dict(d)
        assert restored.connections[1].properties["order"] == 2

    def test_wireframe_roundtrip(self):
        spec = DiagramSpec(
            type="wireframe",
            layout="nested",
            title="My Application",
            elements=[
                Element(id="outer", label="My Application", type="panel",
                        children=["nav", "main"]),
                Element(id="nav", label="Nav", type="sidebar",
                        properties={"role": "sidebar"}),
                Element(id="main", label="Main Content", type="panel",
                        children=["profile"]),
                Element(id="profile", label="User Profile", type="form"),
            ],
        )
        restored = DiagramSpec.from_json(spec.to_json())
        assert restored.title == "My Application"
        assert restored.elements[0].children == ["nav", "main"]
        assert restored.elements[1].properties["role"] == "sidebar"

    def test_table_roundtrip(self):
        spec = DiagramSpec(
            type="table",
            layout="grid",
            properties={"columns": 3},
            elements=[
                Element(id="h", label="", type="header",
                        properties={"cells": ["Name", "Type", "Default"]}),
                Element(id="r1", label="", type="row",
                        properties={"cells": ["host", "string", "localhost"]}),
                Element(id="r2", label="", type="row",
                        properties={"cells": ["port", "int", "8080"]}),
            ],
        )
        restored = DiagramSpec.from_json(spec.to_json())
        assert restored.properties["columns"] == 3
        assert restored.elements[0].properties["cells"][0] == "Name"

    def test_box_with_sections(self):
        spec = DiagramSpec(
            type="box",
            elements=[
                Element(id="comp", label="Component", type="box",
                        properties={"sections": [["name: String", "count: Int"]]}),
            ],
        )
        restored = DiagramSpec.from_json(spec.to_json())
        assert restored.elements[0].properties["sections"][0][0] == "name: String"

    def test_minimal_spec(self):
        spec = DiagramSpec(type="flow")
        d = spec.to_dict()
        assert d["type"] == "flow"
        assert d["elements"] == []
        assert d["connections"] == []

    def test_json_omits_empty_optionals(self):
        spec = DiagramSpec(
            type="flow",
            elements=[Element(id="a", label="A", type="node")],
        )
        d = spec.to_dict()
        elem = d["elements"][0]
        assert "children" not in elem
        assert "properties" not in elem


# ── Validation ────────────────────────────────────────────────────

class TestValidation:

    def test_valid_spec(self):
        spec = DiagramSpec(
            type="flow",
            elements=[
                Element(id="a", label="A", type="node"),
                Element(id="b", label="B", type="node"),
            ],
            connections=[Connection(from_id="a", to_id="b")],
        )
        assert validate_spec(spec) == []

    def test_invalid_type(self):
        spec = DiagramSpec(type="unknown")
        errors = validate_spec(spec)
        assert any("Unknown diagram type" in e for e in errors)

    def test_invalid_layout(self):
        spec = DiagramSpec(type="flow", layout="circular")
        errors = validate_spec(spec)
        assert any("Unknown layout" in e for e in errors)

    def test_duplicate_ids(self):
        spec = DiagramSpec(
            type="flow",
            elements=[
                Element(id="a", label="A", type="node"),
                Element(id="a", label="B", type="node"),
            ],
        )
        errors = validate_spec(spec)
        assert any("Duplicate" in e for e in errors)

    def test_connection_to_unknown(self):
        spec = DiagramSpec(
            type="flow",
            elements=[Element(id="a", label="A", type="node")],
            connections=[Connection(from_id="a", to_id="missing")],
        )
        errors = validate_spec(spec)
        assert any("unknown element" in e for e in errors)

    def test_child_references_unknown(self):
        spec = DiagramSpec(
            type="wireframe",
            elements=[Element(id="a", label="A", type="panel", children=["ghost"])],
        )
        errors = validate_spec(spec)
        assert any("unknown child" in e for e in errors)


# ── Config ────────────────────────────────────────────────────────

class TestConfig:

    def test_default_config(self):
        cfg = MdviewConfig()
        assert cfg.ai.provider == "none"
        assert cfg.theme == "tokyo-night"
        assert cfg.diagrams.fallback == "heuristic"
        assert not cfg.ai.is_configured

    def test_from_dict(self):
        data = {
            "ai": {
                "provider": "anthropic",
                "model": "claude-haiku-4-5",
                "api_key_env": "MY_KEY",
            },
            "theme": "dracula",
            "diagrams": {"fallback": "svgbob"},
        }
        cfg = MdviewConfig._from_dict(data)
        assert cfg.ai.provider == "anthropic"
        assert cfg.ai.model == "claude-haiku-4-5"
        assert cfg.theme == "dracula"
        assert cfg.diagrams.fallback == "svgbob"

    def test_ollama_no_key_needed(self):
        cfg = AIConfig(provider="ollama", model="llama3.2")
        assert cfg.is_configured


# ── Response parsing ──────────────────────────────────────────────

class TestResponseParsing:

    def test_parse_bare_json(self):
        resp = json.dumps({
            "type": "flow",
            "elements": [{"id": "a", "label": "A", "type": "node"}],
            "connections": [],
        })
        spec = _parse_spec_response(resp)
        assert spec is not None
        assert spec.type == "flow"

    def test_parse_fenced_json(self):
        resp = '```json\n{"type": "box", "elements": [], "connections": []}\n```'
        spec = _parse_spec_response(resp)
        assert spec is not None
        assert spec.type == "box"

    def test_parse_invalid_json(self):
        spec = _parse_spec_response("not json at all")
        assert spec is None

    def test_parse_missing_type(self):
        spec = _parse_spec_response('{"elements": []}')
        assert spec is None


# ── Provider factory ──────────────────────────────────────────────

class TestProviderFactory:

    def test_none_returns_none(self):
        cfg = AIConfig(provider="none")
        assert create_provider(cfg) is None

    def test_unknown_returns_none(self):
        cfg = AIConfig(provider="deepseek")
        assert create_provider(cfg) is None

    def test_anthropic_creates(self):
        cfg = AIConfig(provider="anthropic", model="claude-haiku-4-5")
        provider = create_provider(cfg)
        assert provider is not None
        assert provider.__class__.__name__ == "AnthropicProvider"

    def test_ollama_creates(self):
        cfg = AIConfig(provider="ollama")
        provider = create_provider(cfg)
        assert provider is not None
        assert provider.__class__.__name__ == "OllamaProvider"
