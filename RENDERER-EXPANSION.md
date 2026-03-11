# Native Renderer Expansion Plan

## Problem

AI coding tools (Claude Code, Cursor, Copilot, Gemini) generate ASCII diagrams in markdown
output — architecture layouts, flowcharts, state machines, sequence diagrams, wireframes.
No existing tool renders these correctly.

**Why existing tools fail:**

Every tool in the space (svgbob, GoAT, Typograms, markdeep, ditaa, asciitosvg) uses
**character-level interpretation** — each character is independently classified as a drawing
primitive or text. This breaks on AI-generated content where text and structure share the
same character space:

| Character | In text context | Tool interprets as |
|-----------|-----------------|--------------------|
| `v` | "server", "overview" | Downward arrow |
| `/` | "dark/light", "I/O" | Diagonal line |
| `--` | "co-edit", "self-aware" | Horizontal line |
| `( )` | "(optional)" | Arc/circle |
| `'` | "it's", "don't" | Quote/stroke |
| `o` | "protocol" | Circle marker |
| `*` | emphasis | Bullet/marker |

**svgbob's escape mechanism** (double-quoting text) requires modifying the source, which
is unusable for auto-detection of unmarked code blocks.

## Our Approach: Structure-First Parsing

Instead of character-level scanning, we **parse structure first** — find boxes, borders,
arrows, lanes — and then everything inside structural regions is treated as text. Text is
always text, lines are always lines. No ambiguity.

```
Character-level (existing tools):
  For each char → "drawing or text?" → render

Structure-first (our approach):
  Find structural skeleton → extract text regions → render separately
```

This is the same insight that makes a real compiler better than regex: parse the grammar,
don't pattern-match characters.

## Diagram Types (Priority Order)

### Phase 1: Boxes (DONE)
**Status:** `boxrender.py` — shipped and integrated, uses shared `renderlib.py`

Handles:
- Single and multi-section boxes (┌─┐│└─┘ and +---+|+---+)
- Section separators (├─┤)
- Header vs body text styling
- Unicode and ASCII box-drawing characters
- Dark/light theme

```
┌─────────────────┐
│ Component Name   │
├─────────────────┤
│ Property: value  │
│ Another: value   │
└─────────────────┘
```

### Phase 2: Boxes + Arrows (Flowcharts) (DONE)
**Status:** `flowrender.py` — shipped. Horizontal + vertical arrows, auto-rotating arrowheads.

What LLMs produce:
```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Input   │────>│ Process  │────>│  Output  │
└──────────┘     └──────────┘     └──────────┘
                      │
                      ▼
                 ┌──────────┐
                 │  Store   │
                 └──────────┘
```

Parsing approach:
1. Detect boxes (reuse Phase 1 box finder)
2. Find arrow segments between boxes:
   - Horizontal: `───>`, `──→`, `-->`, `->`, `<───`, `←──`
   - Vertical: sequences of `│` or `|` terminated by `▼`, `▲`, `v`, `^`
   - Right-angle turns: `│` meeting `─` at a corner
3. Connect arrows to nearest box edges
4. Render: boxes as rounded rects, arrows as SVG paths with arrowhead markers

Key challenge: Arrow character `v` vs the letter `v`. Resolution: `v` is an arrow
**only** when it appears at the end of a vertical line of `│` characters, or standalone
between two vertically-aligned boxes. In all other contexts, it's text.

### Phase 3: Tables (DONE)
**Status:** `tablerender.py` — shipped. Unicode + ASCII borders, header detection, cell extraction.

What LLMs produce:
```
+----------+--------+-------+
| Feature  | Status | Owner |
+----------+--------+-------+
| Auth     | Done   | Alice |
| Search   | WIP    | Bob   |
| Export   | TODO   | ---   |
+----------+--------+-------+
```

Also with Unicode borders:
```
┌──────────┬────────┬───────┐
│ Feature  │ Status │ Owner │
├──────────┼────────┼───────┤
│ Auth     │ Done   │ Alice │
└──────────┴────────┴───────┘
```

Parsing approach:
1. Detect grid structure: find intersections (+ or ┼/┬/┴/├/┤)
2. Trace horizontal and vertical borders between intersections
3. Extract cell contents
4. Render as SVG table (rect grid + text)

Differentiation from boxes: Tables have **column alignment** — multiple vertical borders
at consistent column positions across rows. Boxes are free-positioned.

### Phase 4: Sequence Diagrams (DONE)
**Status:** `sequencerender.py` — shipped. 2-4+ actors, cross-lane messages, bidirectional arrows.

What LLMs produce:
```
  Client          Server          Database
    │                │                │
    │──── Request ──>│                │
    │                │──── Query ────>│
    │                │<─── Result ────│
    │<── Response ───│                │
    │                │                │
```

Parsing approach:
1. Detect vertical lanes (consistent `│` columns with labels above)
2. Find horizontal arrows between lanes (with labels)
3. Detect activation boxes (thicker segments)
4. Render: vertical lifelines, horizontal arrows with labels, actor boxes

### Phase 5: State Machines / Node Graphs
**Priority:** Medium — used for user journeys, process flows

What LLMs produce:
```
  ┌─────┐    login     ┌────────┐   timeout   ┌────────┐
  │ Idle │────────────>│ Active │────────────>│ Expired│
  └─────┘              └────────┘              └────────┘
     ^                      │
     │       logout         │
     └──────────────────────┘
```

Parsing approach:
1. Find boxes (reuse Phase 1)
2. Find arrow paths (reuse Phase 2 arrow detection)
3. Extract labels on arrows (text adjacent to arrow segments)
4. Render: rounded boxes for states, curved arrows with labels

### Phase 6: Wireframes / UI Mockups
**Priority:** Lower — valuable but less common and more complex

What LLMs produce:
```
┌─── My App ──────────────────────┐
│ ┌──────────────────────────────┐│
│ │ Navigation    Search [____]  ││
│ └──────────────────────────────┘│
│                                 │
│ ┌──────────┐  ┌───────────────┐│
│ │ Sidebar  │  │               ││
│ │          │  │  Main Content ││
│ │ > Item 1 │  │               ││
│ │ > Item 2 │  │               ││
│ └──────────┘  └───────────────┘│
│                                 │
│ ┌──────────────────────────────┐│
│ │ Footer                       ││
│ └──────────────────────────────┘│
└─────────────────────────────────┘
```

Parsing approach:
1. Detect nested boxes (already supported by Phase 1 box finder, needs depth tracking)
2. Detect form elements: `[____]` inputs, `[x]` checkboxes, `( )` radio buttons
3. Detect list markers: `>`, `*`, `-` at consistent indentation
4. Render: nested rects with different fills for depth, form elements as styled shapes

## Architecture

### Module Structure

```
src/mdview/
├── boxrender.py          # Phase 1 (exists) — shared box/text extraction
├── flowrender.py         # Phase 2 — boxes + arrows
├── tablerender.py        # Phase 3 — grid tables
├── sequencerender.py     # Phase 4 — sequence diagrams
├── diagrams.py           # Router — detection + dispatch
└── renderlib.py          # Shared SVG primitives + grid utilities
```

### Shared Foundation: `renderlib.py`

Common utilities extracted from boxrender.py and shared across all renderers:

```python
# Grid operations
def parse_grid(source: str) -> Grid           # String → 2D char grid
def find_char_at(grid, r, c, charset) -> bool # Character detection

# Structure detection (reusable across renderers)
def find_boxes(grid) -> list[Box]             # Corner + border detection
def find_arrows(grid, boxes) -> list[Arrow]   # Arrow path tracing
def find_intersections(grid) -> list[Point]   # Grid intersection detection

# SVG generation
def svg_start(width, height, class_name)      # SVG header + theme CSS
def svg_rect(x, y, w, h, class_name, rx=4)   # Rounded rectangle
def svg_line(x1, y1, x2, y2, class_name)     # Line segment
def svg_arrow(points, direction, class_name)  # Path with arrowhead
def svg_text(x, y, text, class_name)          # Escaped text element
```

### Detection + Routing in `diagrams.py`

```python
def render_svg(diagram, diagram_type, service_url):
    if diagram_type == DiagramType.ASCII_AUTO:
        # Try recognizers in priority order
        for recognizer in [
            try_flow_render,      # Phase 2: boxes + arrows
            try_table_render,     # Phase 3: tables
            try_sequence_render,  # Phase 4: sequence diagrams
            try_box_render,       # Phase 1: plain boxes (most permissive)
        ]:
            svg = recognizer(diagram)
            if svg is not None:
                return svg
    # Fallback to svgbob via kroki
    return _render_kroki(diagram, "svgbob", service_url)
```

Detection order matters — more specific recognizers first (flow > table > sequence),
with plain boxes as the most permissive structural match. svgbob remains the ultimate
fallback for freeform ASCII art that doesn't match any structural pattern.

### Theming

All renderers share a CSS theme (dark/light via `prefers-color-scheme`):

```css
.box-border  { stroke: #7aa2f7; }     /* Structure lines */
.box-text    { fill: #a9b1d6; }       /* Body text */
.box-header  { fill: #9ece6a; }       /* Section headers */
.arrow-line  { stroke: #bb9af7; }     /* Connections */
.arrow-label { fill: #e0af68; }       /* Arrow labels */
.table-header { fill: #9ece6a; }      /* Table headers */
.table-cell  { fill: #a9b1d6; }       /* Table cells */
```

## Transaction Plan

### T1: Extract shared renderlib (DONE)
- ✅ Extracted grid parsing, box detection, SVG primitives into `renderlib.py`
- ✅ `boxrender.py` is now a thin wrapper calling renderlib
- **Commit:** `97126f7`

### T2: Arrow detection + flow renderer (DONE)
- ✅ Arrow path tracing in renderlib (horizontal, vertical)
- ✅ `flowrender.py` detects boxes + arrows, renders connected diagrams
- ✅ Auto-rotating SVG arrowhead markers (`orient="auto-start-reverse"`)
- **Commit:** `97126f7` (combined with T1), fix: `8033ecf`

### T3: Table renderer (DONE)
- ✅ Grid intersection detection in `tablerender.py`
- ✅ Unicode and ASCII table borders
- ✅ Header detection and cell extraction
- **Commit:** `b6e1012`

### T4: Sequence diagram renderer (DONE)
- ✅ Vertical lane detection with actor labels
- ✅ Horizontal message arrows with labels
- ✅ 2-4+ actors, cross-lane messages, bidirectional arrows
- **Commit:** `2813c82`

### T5: Test suite + border fix (DONE)
- ✅ 78 tests: detection, rendering, cross-type discrimination, edge cases
- ✅ Fixed `has_horiz_border` to require 60% border chars (prevents gap false positives)
- ✅ Updated RENDERER-EXPANSION.md status
- **Commit:** (this commit)

### T6: Standalone package consideration
- Evaluate extracting renderer as standalone PyPI package (`aiart2svg` or similar)
- Would be useful beyond mdview — any tool processing AI-generated markdown
- Separate decision point: discuss with David

## Success Criteria

1. ARCHITECTURE.md box diagram renders perfectly (Phase 1 — done)
2. Flowcharts with horizontal and vertical arrows render correctly (Phase 2)
3. ASCII tables render as clean grid SVGs (Phase 3)
4. No character misinterpretation in text regions (core differentiator)
5. All rendering is local (no HTTP calls for structure-recognized diagrams)
6. svgbob fallback still works for unrecognized patterns
7. Dark/light theme on all diagram types

## Open Questions

- Should we support arrow labels on flow diagrams? (e.g., text on arrow segments)
- How aggressive should table detection be? (risk: code output that looks tabular)
- Should nested boxes (wireframes) be Phase 2 or Phase 6?
- Standalone package name: `aiart2svg`? `asciirender`? `structsvg`?
