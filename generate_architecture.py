#!/usr/bin/env python3
"""Generate ARCHITECTURE.md with spec-rendered SVG diagrams.

Dogfoods the mdview spec-based rendering pipeline to document itself.
Each diagram is a DiagramSpec rendered to inline SVG.
"""

from pathlib import Path
from mdview.spec import DiagramSpec, Element, Connection
from mdview.specrender import render_spec_svg


def _svg_block(spec: DiagramSpec) -> str:
    """Render a spec to an HTML details block with inline SVG."""
    svg = render_spec_svg(spec)
    title = spec.title or f"{spec.type} diagram"
    # Wrap in a div so markdown renderers pass it through
    return f"""
<div align="center">

{svg}

<em>{title}</em>

</div>
"""


# ── Diagrams ───────────────────────────────────────────────────────

RENDERING_PIPELINE = DiagramSpec(
    type="flow",
    title="Rendering Pipeline",
    layout="horizontal",
    elements=[
        Element(id="md", label="Markdown", type="node"),
        Element(id="extract", label="Extract Blocks", type="node"),
        Element(id="route", label="Route", type="decision"),
        Element(id="spec", label="Spec Render", type="node"),
        Element(id="heuristic", label="Heuristic", type="node"),
        Element(id="svg", label="SVG", type="node"),
    ],
    connections=[
        Connection(from_id="md", to_id="extract"),
        Connection(from_id="extract", to_id="route"),
        Connection(from_id="route", to_id="spec", label="AI"),
        Connection(from_id="route", to_id="heuristic", label="fallback"),
        Connection(from_id="spec", to_id="svg"),
        Connection(from_id="heuristic", to_id="svg"),
    ],
)

AI_PIPELINE = DiagramSpec(
    type="flow",
    title="AI-Driven Spec Pipeline",
    layout="vertical",
    elements=[
        Element(id="ascii", label="ASCII Art", type="node"),
        Element(id="provider", label="AI Provider", type="node"),
        Element(id="diagspec", label="DiagramSpec", type="node"),
        Element(id="specrender", label="specrender.py", type="node"),
        Element(id="themed", label="Themed SVG", type="node"),
    ],
    connections=[
        Connection(from_id="ascii", to_id="provider", label="interpret"),
        Connection(from_id="provider", to_id="diagspec", label="JSON"),
        Connection(from_id="diagspec", to_id="specrender", label="dispatch"),
        Connection(from_id="specrender", to_id="themed", label="render"),
    ],
)

MODULE_MAP = DiagramSpec(
    type="box",
    title="Module Architecture",
    layout="horizontal",
    elements=[
        Element(id="cli", label="cli.py", type="box",
                properties={"sections": [["argparse", "entry point"]]}),
        Element(id="renderer", label="renderer.py", type="box",
                properties={"sections": [["render_html()", "render_terminal()", "render_file()"]]}),
        Element(id="diagrams", label="diagrams.py", type="box",
                properties={"sections": [["extract_diagram_blocks()", "render_svg()", "render_from_spec()"]]}),
        Element(id="specpipe", label="Spec Pipeline", type="box",
                properties={"sections": [
                    ["spec.py — DiagramSpec schema"],
                    ["config.py — mdview.yaml loader"],
                    ["providers.py — AI backends"],
                    ["specrender.py — 6 type renderers"],
                ]}),
        Element(id="heuristic", label="Heuristic Renderers", type="box",
                properties={"sections": [
                    ["routing.py — confidence scoring"],
                    ["flowrender.py"],
                    ["sequencerender.py"],
                    ["boxrender.py, tablerender.py"],
                    ["wireframerender.py"],
                ]}),
        Element(id="shared", label="Shared", type="box",
                properties={"sections": [
                    ["renderlib.py — SVG primitives"],
                    ["themes.py — color system"],
                ]}),
    ],
)

PROVIDER_ARCHITECTURE = DiagramSpec(
    type="sequence",
    title="Provider Interpretation Flow",
    layout="sequence",
    elements=[
        Element(id="caller", label="diagrams.py", type="actor"),
        Element(id="config", label="MdviewConfig", type="actor"),
        Element(id="factory", label="create_provider", type="actor"),
        Element(id="provider", label="AI Provider", type="actor"),
    ],
    connections=[
        Connection(from_id="caller", to_id="config", label="load()",
                   properties={"order": 1}),
        Connection(from_id="config", to_id="caller", label="AIConfig",
                   properties={"order": 2}, style="dashed"),
        Connection(from_id="caller", to_id="factory", label="create(config)",
                   properties={"order": 3}),
        Connection(from_id="factory", to_id="caller", label="Provider",
                   properties={"order": 4}, style="dashed"),
        Connection(from_id="caller", to_id="provider", label="interpret(ascii)",
                   properties={"order": 5}),
        Connection(from_id="provider", to_id="caller", label="DiagramSpec",
                   properties={"order": 6}, style="dashed"),
    ],
)

CONFIG_TABLE = DiagramSpec(
    type="table",
    title="Configuration Options (mdview.yaml)",
    elements=[
        Element(id="h", label="", type="header",
                properties={"cells": ["Section", "Key", "Default", "Description"]}),
        Element(id="r1", label="", type="row",
                properties={"cells": ["ai", "provider", "none", "anthropic / openai / ollama / none"]}),
        Element(id="r2", label="", type="row",
                properties={"cells": ["ai", "model", "(auto)", "Model name (e.g. claude-haiku-4-5)"]}),
        Element(id="r3", label="", type="row",
                properties={"cells": ["ai", "api_key_env", "(auto)", "Env var with API key"]}),
        Element(id="r4", label="", type="row",
                properties={"cells": ["", "theme", "tokyo-night", "Color theme name"]}),
        Element(id="r5", label="", type="row",
                properties={"cells": ["diagrams", "fallback", "heuristic", "heuristic / svgbob / none"]}),
    ],
)

DIAGRAM_TYPES = DiagramSpec(
    type="state_machine",
    title="Supported Diagram Types",
    elements=[
        Element(id="flow", label="Flow", type="node"),
        Element(id="seq", label="Sequence", type="node"),
        Element(id="wire", label="Wireframe", type="node"),
        Element(id="table", label="Table", type="node"),
        Element(id="box", label="Box/Class", type="node"),
        Element(id="sm", label="State Machine", type="node"),
    ],
    connections=[
        Connection(from_id="flow", to_id="seq", label=""),
        Connection(from_id="seq", to_id="wire", label=""),
        Connection(from_id="wire", to_id="table", label=""),
        Connection(from_id="table", to_id="box", label=""),
        Connection(from_id="box", to_id="sm", label=""),
    ],
)

# ── Document generation ────────────────────────────────────────────

def generate() -> str:
    return f"""# mdview Architecture

> Lightweight markdown + multi-diagram viewer.
> ASCII art in, themed SVG out. AI-agnostic interpretation.

## Overview

mdview renders markdown documents with embedded diagrams to interactive HTML.
It extracts diagram code blocks (mermaid, svgbob, ditaa, or auto-detected ASCII art),
renders them to SVG, and produces a self-contained HTML file with pan/zoom lightbox.

The key architectural decision: **replace brittle heuristic ASCII parsing with
AI-driven interpretation**. The generating AI (or a configured backend) produces
a structured `DiagramSpec`, which the renderer converts to themed SVG. No character
guessing — the AI that drew the diagram already knows what it is.

{_svg_block(RENDERING_PIPELINE)}

## Rendering Pipeline

1. **Extract** — `diagrams.py` scans markdown for fenced code blocks
   (`mermaid`, `svgbob`, `ditaa`) and auto-detects ASCII art in unmarked blocks.

2. **Route** — For ASCII art, two paths:
   - **Spec path (primary):** If an AI provider is configured in `mdview.yaml`,
     the ASCII art is interpreted to a `DiagramSpec` and rendered by `specrender.py`.
   - **Heuristic path (fallback):** Confidence-scored routing in `routing.py`
     picks the best character-parsing renderer. Falls back to kroki.io/svgbob.

3. **Render** — Type-specific renderer produces themed SVG with dark/light CSS.

4. **Assemble** — `renderer.py` wraps everything in self-contained HTML with
   inline SVGs, fullscreen lightbox, and optional live-reload via SSE.

## AI-Driven Spec Pipeline

The spec pipeline is the core architectural innovation. It separates
**interpretation** (understanding what the diagram is) from **rendering**
(producing SVG). This is AI-agnostic — configure any backend.

{_svg_block(AI_PIPELINE)}

### Two Paths to a Spec

| Path | When | Cost |
|------|------|------|
| **Direct emission** | The AI generating the ASCII also emits a DiagramSpec JSON | Zero — no extra inference |
| **Backend interpretation** | Configured provider (Anthropic, OpenAI, Ollama) interprets arbitrary ASCII | One API call per diagram |

### DiagramSpec Schema

The contract between interpretation and rendering:

```json
{{
  "type": "flow|sequence|wireframe|table|box|state_machine",
  "title": "optional",
  "layout": "horizontal|vertical|grid|nested|sequence|auto",
  "elements": [
    {{"id": "unique", "label": "text", "type": "node|actor|panel|...",
     "children": ["id"], "properties": {{}}}}
  ],
  "connections": [
    {{"from": "id", "to": "id", "label": "text",
     "style": "solid|dashed", "properties": {{}}}}
  ]
}}
```

## Module Architecture

{_svg_block(MODULE_MAP)}

### Module Responsibilities

| Module | Lines | Role |
|--------|-------|------|
| `cli.py` | 115 | Argparse entry point, dispatch to render/serve |
| `renderer.py` | 966 | HTML/terminal output, markdown processing, lightbox |
| `diagrams.py` | 386 | Block extraction, render dispatch, kroki/mermaid HTTP |
| `spec.py` | 170 | DiagramSpec/Element/Connection dataclasses, validation |
| `config.py` | 144 | mdview.yaml loading, AIConfig, theme/diagram settings |
| `providers.py` | 266 | AI provider interface (Anthropic, OpenAI, Ollama) |
| `specrender.py` | 947 | 6 type-specific SVG renderers from DiagramSpec |
| `renderlib.py` | 1342 | Shared SVG primitives, box detection, arrow rendering |
| `themes.py` | 248 | ThemeColors, dark/light CSS generation, YAML loading |
| `routing.py` | 474 | Confidence-scored heuristic routing (fallback path) |
| `server.py` | 364 | Live reload HTTP server with SSE file watching |

## Provider Architecture

Providers are configured like embedding models — set the backend in `mdview.yaml`,
and the system handles the rest. Each provider uses the same interpretation prompt
but calls a different API.

{_svg_block(PROVIDER_ARCHITECTURE)}

### Supported Providers

| Provider | Model Default | API Key | Notes |
|----------|---------------|---------|-------|
| `anthropic` | claude-haiku-4-5 | `ANTHROPIC_API_KEY` | Recommended for speed |
| `openai` | gpt-4o-mini | `OPENAI_API_KEY` | JSON mode response format |
| `ollama` | llama3.2 | None needed | Local, zero-cost |
| `none` | — | — | Heuristic fallback only |

## Configuration

{_svg_block(CONFIG_TABLE)}

Example `mdview.yaml`:

```yaml
ai:
  provider: anthropic
  model: claude-haiku-4-5
  # api_key_env: ANTHROPIC_API_KEY  # auto-detected

theme: tokyo-night

diagrams:
  fallback: heuristic
  types: [flow, sequence, wireframe, table, box, state_machine]
```

Config search order: `./mdview.yaml` → `~/.config/mdview/config.yaml` → defaults.

## Diagram Types

Six diagram types, each with a dedicated renderer in `specrender.py`:

{_svg_block(DIAGRAM_TYPES)}

| Type | Elements | Use Case |
|------|----------|----------|
| `flow` | Nodes + arrows | CI/CD pipelines, data flows, decision trees |
| `sequence` | Actors + messages | API flows, auth sequences, protocols |
| `wireframe` | Nested panels | UI mockups, dashboard layouts |
| `table` | Headers + rows | Config tables, API docs, comparisons |
| `box` | Boxes + sections | Class diagrams, UML-style components |
| `state_machine` | States + transitions | Lifecycles, protocols, FSMs |

## Theme System

Themes provide 11 color slots with automatic dark/light switching via
CSS `prefers-color-scheme` media queries. Built-in: Tokyo Night.

Custom themes: `~/.config/mdview/themes/mytheme.yaml`

```yaml
dark:
  bg: "#1a1b26"
  fg: "#a9b1d6"
  border: "#7aa2f7"
  arrow: "#bb9af7"
  # ... 7 more slots
light:
  bg: "#f8f8fc"
  # ...
```

## Test Coverage

183 tests across 4 test files:

| File | Tests | Coverage |
|------|-------|----------|
| `test_renderers.py` | 78 | Heuristic renderers (flow, sequence, box, table, wireframe) |
| `test_spec.py` | 24 | DiagramSpec roundtrip, validation, config, providers |
| `test_specrender.py` | 25 | Spec-based SVG generation, theme, all 6 types |
| `test_specrender_e2e.py` | 12 | Full pipeline integration, realistic specs |
| Other tests | 44 | Routing, detection, edge cases |

## Usage

```bash
# Render markdown to HTML (opens in browser)
mdview SPEC.md

# Live reload server
mdview SPEC.md --serve

# Terminal output (requires rich)
mdview SPEC.md --terminal

# Write to specific file
mdview SPEC.md -o output.html
```

---

*Architecture diagrams in this document are rendered by mdview's own spec-based pipeline.*
"""


if __name__ == "__main__":
    doc = generate()
    Path("ARCHITECTURE.md").write_text(doc)
    print(f"Generated ARCHITECTURE.md ({len(doc)} bytes, {doc.count('<svg')} diagrams)")
