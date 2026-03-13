# mdview

Lightweight markdown + multi-diagram viewer. ASCII art in, themed SVG out.

## What it does

mdview renders markdown documents with embedded diagrams to interactive HTML.
It extracts diagram code blocks, renders them to SVG, and produces a
self-contained HTML file with pan/zoom lightbox.

**The key idea:** AI coding tools generate ASCII diagrams in markdown — flowcharts,
state machines, sequence diagrams, architecture layouts. No existing tool renders
these correctly because they all use character-level interpretation where `v` in
"server" becomes a downward arrow and `/` in "I/O" becomes a diagonal line.

mdview solves this with a structured `DiagramSpec` that separates content from
rendering. The AI that drew the diagram already knows what it is — let it say so.

## Supported diagram types

| Type | Description | Example use |
|------|-------------|-------------|
| **flow** | Flowcharts with nodes, decisions, arrows | CI/CD pipelines, decision trees |
| **sequence** | Actor lifelines with ordered messages | API flows, auth sequences |
| **box** | Structured boxes with sections and connections | Class diagrams, architecture |
| **state_machine** | States with transitions, back-edges, self-loops | Order lifecycle, protocols |
| **table** | Header + rows with auto-sized columns | API endpoints, config tables |
| **wireframe** | Nested panels, sidebars, inputs, forms | UI mockups, dashboard layouts |

All diagrams support automatic dark/light theme via `prefers-color-scheme`.

## Install

```bash
pip install asciisvg
```

Or install from source:

```bash
git clone https://github.com/Nubaeon/mdview.git
cd mdview
pip install -e .
```

## Usage

### CLI

```bash
# Render markdown to HTML and open in browser
mdview document.md

# Write to specific file without opening
mdview document.md -o output.html --no-open

# Terminal rendering (requires rich)
pip install asciisvg[rich]
mdview document.md --terminal

# Live reload server (watches for changes)
mdview document.md --serve --port 8090
```

### Python API

```python
from mdview.spec import DiagramSpec, Element, Connection
from mdview.specrender import render_spec_svg

# Build a spec
spec = DiagramSpec(
    type="flow",
    layout="horizontal",
    elements=[
        Element(id="start", label="Start", type="node"),
        Element(id="check", label="Valid?", type="decision"),
        Element(id="done", label="Done", type="node"),
    ],
    connections=[
        Connection(from_id="start", to_id="check"),
        Connection(from_id="check", to_id="done", label="yes"),
    ],
)

# Render to SVG string
svg = render_spec_svg(spec)
```

### Rendering markdown files

```python
from mdview import render_file

# To HTML
render_file("document.md", format="html", output_path="output.html")

# To terminal
render_file("document.md", format="terminal")
```

### Heuristic rendering (no AI needed)

mdview includes heuristic renderers that detect diagram type from ASCII art
structure. These work as a fallback when no `DiagramSpec` is provided:

```python
from mdview import has_flow_structure, render_flow_svg
from mdview import has_sequence_structure, render_sequence_svg
from mdview import has_box_structure, render_box_svg

ascii_art = """
+--------+     +--------+     +--------+
|  Start | --> | Process| --> |  End   |
+--------+     +--------+     +--------+
"""

if has_flow_structure(ascii_art):
    svg = render_flow_svg(ascii_art)
```

## Architecture

```
DiagramSpec (structured data)
     |
     v
specrender.py  --- render_spec_svg()
     |                  |
     |    +-------------+-------------+-------------+
     v    v             v             v              v
   flow  sequence     box      state_machine    wireframe  table
     |    |             |             |              |        |
     v    v             v             v              v        v
              Themed SVG with dark/light support
```

Two rendering paths:
1. **Spec-based** (preferred): `DiagramSpec` -> `render_spec_svg()` -> SVG
2. **Heuristic** (fallback): ASCII text -> `has_*_structure()` -> `render_*_svg()` -> SVG

The spec-based path is what AI tools should use. The heuristic path handles
existing ASCII art in markdown files.

## Theming

All diagrams support dark and light themes automatically via CSS
`prefers-color-scheme` media queries. Custom themes can be passed to renderers:

```python
from mdview.themes import Theme, ThemeColors

custom = Theme(
    name="custom",
    dark=ThemeColors(
        bg="#1a1b26", bg_secondary="#24283b", fg="#a9b1d6",
        heading="#9ece6a", header_text="#9ece6a", label="#e0af68",
        border="#7aa2f7", separator="#7aa2f7", muted="#565f89",
        arrow="#bb9af7", arrow_label_bg="#1a1b26",
    ),
    light=ThemeColors(
        bg="#f8f8fc", bg_secondary="#e8e8f0", fg="#343b58",
        heading="#33635c", header_text="#33635c", label="#8c6c3e",
        border="#34548a", separator="#34548a", muted="#9699a3",
        arrow="#5a4a78", arrow_label_bg="#f8f8fc",
    ),
)

svg = render_spec_svg(spec, theme=custom)
```

## Development

```bash
# Install dev dependencies
pip install -e ".[all]"

# Run tests
python -m pytest tests/ -v

# Run specific test suite
python -m pytest tests/test_specrender.py -v        # Unit tests
python -m pytest tests/test_specrender_e2e.py -v     # End-to-end tests
python -m pytest tests/test_specrender_random.py -v  # Randomized stress tests

# Lint
ruff check src/ tests/
```

## License

MIT - see [LICENSE](LICENSE).
