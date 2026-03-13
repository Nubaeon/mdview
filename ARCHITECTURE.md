# mdview Architecture

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


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="1019" height="80" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <defs>
    <marker id="arrowhead" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="1019" height="80" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="106.0" height="40.0" rx="6"/>
  <text class="box-header" x="73.0" y="40.0" text-anchor="middle" dominant-baseline="central">Markdown</text>
  <rect class="box-border" x="186.0" y="20.0" width="163.0" height="40.0" rx="6"/>
  <text class="box-text" x="267.5" y="40.0" text-anchor="middle" dominant-baseline="central">Extract Blocks</text>
  <polygon class="box-border" points="449.0,20.0 489.0,40.0 449.0,60.0 409.0,40.0"/>
  <text class="box-text" x="449.0" y="40.0" text-anchor="middle" dominant-baseline="central">Route</text>
  <rect class="box-border" x="549.0" y="20.0" width="134.5" height="40.0" rx="6"/>
  <text class="box-text" x="616.2" y="40.0" text-anchor="middle" dominant-baseline="central">Spec Render</text>
  <rect class="box-border" x="743.5" y="20.0" width="115.5" height="40.0" rx="6"/>
  <text class="box-text" x="801.2" y="40.0" text-anchor="middle" dominant-baseline="central">Heuristic</text>
  <rect class="box-border" x="919.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <text class="box-text" x="959.0" y="40.0" text-anchor="middle" dominant-baseline="central">SVG</text>
  <line class="arrow-line" x1="126.0" y1="40.0" x2="186.0" y2="40.0" marker-end="url(#arrowhead)"/>
  <line class="arrow-line" x1="349.0" y1="40.0" x2="409.0" y2="40.0" marker-end="url(#arrowhead)"/>
  <line class="arrow-line" x1="489.0" y1="40.0" x2="549.0" y2="40.0" marker-end="url(#arrowhead)"/>
  <rect class="arrow-label-bg" x="507.8" y="31.0" width="22.4" height="16.0" rx="3"/>
  <text class="arrow-label" x="519.0" y="40.0" dominant-baseline="central">AI</text>
  <line class="arrow-line" x1="489.0" y1="40.0" x2="743.5" y2="40.0" marker-end="url(#arrowhead)"/>
  <rect class="arrow-label-bg" x="583.5" y="31.0" width="65.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="616.2" y="40.0" dominant-baseline="central">fallback</text>
  <line class="arrow-line" x1="683.5" y1="40.0" x2="919.0" y2="40.0" marker-end="url(#arrowhead)"/>
  <line class="arrow-line" x1="859.0" y1="40.0" x2="919.0" y2="40.0" marker-end="url(#arrowhead)"/>
</svg>

<em>Rendering Pipeline</em>

</div>


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


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="194" height="480" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <defs>
    <marker id="arrowhead" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="194" height="480" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="115.5" height="40.0" rx="6"/>
  <text class="box-header" x="77.8" y="40.0" text-anchor="middle" dominant-baseline="central">ASCII Art</text>
  <rect class="box-border" x="20.0" y="120.0" width="134.5" height="40.0" rx="6"/>
  <text class="box-text" x="87.2" y="140.0" text-anchor="middle" dominant-baseline="central">AI Provider</text>
  <rect class="box-border" x="20.0" y="220.0" width="134.5" height="40.0" rx="6"/>
  <text class="box-text" x="87.2" y="240.0" text-anchor="middle" dominant-baseline="central">DiagramSpec</text>
  <rect class="box-border" x="20.0" y="320.0" width="153.5" height="40.0" rx="6"/>
  <text class="box-text" x="96.8" y="340.0" text-anchor="middle" dominant-baseline="central">specrender.py</text>
  <rect class="box-border" x="20.0" y="420.0" width="125.0" height="40.0" rx="6"/>
  <text class="box-text" x="82.5" y="440.0" text-anchor="middle" dominant-baseline="central">Themed SVG</text>
  <line class="arrow-line" x1="77.8" y1="60.0" x2="87.2" y2="120.0" marker-end="url(#arrowhead)"/>
  <rect class="arrow-label-bg" x="46.1" y="81.0" width="72.8" height="16.0" rx="3"/>
  <text class="arrow-label" x="82.5" y="90.0" dominant-baseline="central">interpret</text>
  <line class="arrow-line" x1="87.2" y1="160.0" x2="87.2" y2="220.0" marker-end="url(#arrowhead)"/>
  <rect class="arrow-label-bg" x="68.8" y="181.0" width="36.8" height="16.0" rx="3"/>
  <text class="arrow-label" x="87.2" y="190.0" dominant-baseline="central">JSON</text>
  <line class="arrow-line" x1="87.2" y1="260.0" x2="96.8" y2="320.0" marker-end="url(#arrowhead)"/>
  <rect class="arrow-label-bg" x="59.2" y="281.0" width="65.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="92.0" y="290.0" dominant-baseline="central">dispatch</text>
  <line class="arrow-line" x1="96.8" y1="360.0" x2="82.5" y2="420.0" marker-end="url(#arrowhead)"/>
  <rect class="arrow-label-bg" x="64.0" y="381.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="89.6" y="390.0" dominant-baseline="central">render</text>
</svg>

<em>AI-Driven Spec Pipeline</em>

</div>


### Two Paths to a Spec

| Path | When | Cost |
|------|------|------|
| **Direct emission** | The AI generating the ASCII also emits a DiagramSpec JSON | Zero — no extra inference |
| **Backend interpretation** | Configured provider (Anthropic, OpenAI, Ollama) interprets arbitrary ASCII | One API call per diagram |

### DiagramSpec Schema

The contract between interpretation and rendering:

```json
{
  "type": "flow|sequence|wireframe|table|box|state_machine",
  "title": "optional",
  "layout": "horizontal|vertical|grid|nested|sequence|auto",
  "elements": [
    {"id": "unique", "label": "text", "type": "node|actor|panel|...",
     "children": ["id"], "properties": {}}
  ],
  "connections": [
    {"from": "id", "to": "id", "label": "text",
     "style": "solid|dashed", "properties": {}}
  ]
}
```

## Module Architecture


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="1494" height="188" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="1494" height="188" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="116.4" height="82.0" rx="6"/>
  <text class="box-header" x="78.2" y="40.0" text-anchor="middle" dominant-baseline="central">cli.py</text>
  <line class="box-separator" x1="20.0" y1="52.0" x2="136.4" y2="52.0"/>
  <text class="box-text" x="32.0" y="74.0">argparse</text>
  <text class="box-text" x="32.0" y="90.0">entry point</text>
  <rect class="box-border" x="156.4" y="20.0" width="166.8" height="104.0" rx="6"/>
  <text class="box-header" x="239.8" y="40.0" text-anchor="middle" dominant-baseline="central">renderer.py</text>
  <line class="box-separator" x1="156.4" y1="52.0" x2="323.2" y2="52.0"/>
  <text class="box-text" x="168.4" y="74.0">render_html()</text>
  <text class="box-text" x="168.4" y="90.0">render_terminal()</text>
  <text class="box-text" x="168.4" y="106.0">render_file()</text>
  <rect class="box-border" x="343.2" y="20.0" width="225.6" height="104.0" rx="6"/>
  <text class="box-header" x="456.0" y="40.0" text-anchor="middle" dominant-baseline="central">diagrams.py</text>
  <line class="box-separator" x1="343.2" y1="52.0" x2="568.8" y2="52.0"/>
  <text class="box-text" x="355.2" y="74.0">extract_diagram_blocks()</text>
  <text class="box-text" x="355.2" y="90.0">render_svg()</text>
  <text class="box-text" x="355.2" y="106.0">render_from_spec()</text>
  <rect class="box-border" x="588.8" y="20.0" width="292.8" height="126.0" rx="6"/>
  <text class="box-header" x="735.2" y="40.0" text-anchor="middle" dominant-baseline="central">Spec Pipeline</text>
  <line class="box-separator" x1="588.8" y1="52.0" x2="881.6" y2="52.0"/>
  <text class="box-text" x="600.8" y="74.0">spec.py — DiagramSpec schema</text>
  <line class="box-separator" x1="588.8" y1="80.0" x2="881.6" y2="80.0"/>
  <text class="box-text" x="600.8" y="102.0">config.py — mdview.yaml loader</text>
  <line class="box-separator" x1="588.8" y1="108.0" x2="881.6" y2="108.0"/>
  <text class="box-text" x="600.8" y="130.0">providers.py — AI backends</text>
  <line class="box-separator" x1="588.8" y1="136.0" x2="881.6" y2="136.0"/>
  <text class="box-text" x="600.8" y="158.0">specrender.py — 6 type renderers</text>
  <rect class="box-border" x="901.6" y="20.0" width="284.4" height="148.0" rx="6"/>
  <text class="box-header" x="1043.8" y="40.0" text-anchor="middle" dominant-baseline="central">Heuristic Renderers</text>
  <line class="box-separator" x1="901.6" y1="52.0" x2="1186.0" y2="52.0"/>
  <text class="box-text" x="913.6" y="74.0">routing.py — confidence scoring</text>
  <line class="box-separator" x1="901.6" y1="80.0" x2="1186.0" y2="80.0"/>
  <text class="box-text" x="913.6" y="102.0">flowrender.py</text>
  <line class="box-separator" x1="901.6" y1="108.0" x2="1186.0" y2="108.0"/>
  <text class="box-text" x="913.6" y="130.0">sequencerender.py</text>
  <line class="box-separator" x1="901.6" y1="136.0" x2="1186.0" y2="136.0"/>
  <text class="box-text" x="913.6" y="158.0">boxrender.py, tablerender.py</text>
  <line class="box-separator" x1="901.6" y1="164.0" x2="1186.0" y2="164.0"/>
  <text class="box-text" x="913.6" y="186.0">wireframerender.py</text>
  <rect class="box-border" x="1206.0" y="20.0" width="267.6" height="82.0" rx="6"/>
  <text class="box-header" x="1339.8" y="40.0" text-anchor="middle" dominant-baseline="central">Shared</text>
  <line class="box-separator" x1="1206.0" y1="52.0" x2="1473.6" y2="52.0"/>
  <text class="box-text" x="1218.0" y="74.0">renderlib.py — SVG primitives</text>
  <line class="box-separator" x1="1206.0" y1="80.0" x2="1473.6" y2="80.0"/>
  <text class="box-text" x="1218.0" y="102.0">themes.py — color system</text>
</svg>

<em>Module Architecture</em>

</div>


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


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="670" height="340" class="mdview-diagram">
  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .bg { fill: #1a1b26; }
    .mdview-diagram .actor-box { fill: #24283b; stroke: #7aa2f7; stroke-width: 1.5; }
    .mdview-diagram .actor-text { fill: #9ece6a; font-weight: 600; text-anchor: middle; dominant-baseline: central; }
    .mdview-diagram .lifeline { stroke: #565f89; stroke-width: 1; stroke-dasharray: 6,4; }
    .mdview-diagram .msg-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .msg-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .msg-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .bg { fill: #f8f8fc; }
      .mdview-diagram .actor-box { fill: #e8e8f0; stroke: #2e7de9; }
      .mdview-diagram .actor-text { fill: #587539; }
      .mdview-diagram .lifeline { stroke: #9ca0b0; }
      .mdview-diagram .msg-line { stroke: #7847bd; }
      .mdview-diagram .msg-head { fill: #7847bd; }
      .mdview-diagram .msg-label { fill: #8c6c3e; }
    }
  </style>
  <defs>
    <marker id="seq-arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="msg-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="670" height="340" rx="6"/>
  <rect class="actor-box" x="40.0" y="20" width="110" height="32" rx="4"/>
  <text class="actor-text" x="95.0" y="36.0">diagrams.py</text>
  <rect class="actor-box" x="40.0" y="288" width="110" height="32" rx="4"/>
  <text class="actor-text" x="95.0" y="304.0">diagrams.py</text>
  <rect class="actor-box" x="200.0" y="20" width="110" height="32" rx="4"/>
  <text class="actor-text" x="255.0" y="36.0">MdviewConfig</text>
  <rect class="actor-box" x="200.0" y="288" width="110" height="32" rx="4"/>
  <text class="actor-text" x="255.0" y="304.0">MdviewConfig</text>
  <rect class="actor-box" x="360.0" y="20" width="110" height="32" rx="4"/>
  <text class="actor-text" x="415.0" y="36.0">create_provider</text>
  <rect class="actor-box" x="360.0" y="288" width="110" height="32" rx="4"/>
  <text class="actor-text" x="415.0" y="304.0">create_provider</text>
  <rect class="actor-box" x="520.0" y="20" width="110" height="32" rx="4"/>
  <text class="actor-text" x="575.0" y="36.0">AI Provider</text>
  <rect class="actor-box" x="520.0" y="288" width="110" height="32" rx="4"/>
  <text class="actor-text" x="575.0" y="304.0">AI Provider</text>
  <line class="lifeline" x1="95.0" y1="64" x2="95.0" y2="276"/>
  <line class="lifeline" x1="255.0" y1="64" x2="255.0" y2="276"/>
  <line class="lifeline" x1="415.0" y1="64" x2="415.0" y2="276"/>
  <line class="lifeline" x1="575.0" y1="64" x2="575.0" y2="276"/>
  <line class="msg-line" x1="95.0" y1="80.0" x2="255.0" y2="80.0" marker-end="url(#seq-arrow)"/>
  <text class="msg-label" x="175.0" y="72.0">load()</text>
  <line class="msg-line" x1="95.0" y1="112.0" x2="255.0" y2="112.0" stroke-dasharray="6,3" marker-start="url(#seq-arrow)"/>
  <text class="msg-label" x="175.0" y="104.0">AIConfig</text>
  <line class="msg-line" x1="95.0" y1="144.0" x2="415.0" y2="144.0" marker-end="url(#seq-arrow)"/>
  <text class="msg-label" x="255.0" y="136.0">create(config)</text>
  <line class="msg-line" x1="95.0" y1="176.0" x2="415.0" y2="176.0" stroke-dasharray="6,3" marker-start="url(#seq-arrow)"/>
  <text class="msg-label" x="255.0" y="168.0">Provider</text>
  <line class="msg-line" x1="95.0" y1="208.0" x2="575.0" y2="208.0" marker-end="url(#seq-arrow)"/>
  <text class="msg-label" x="335.0" y="200.0">interpret(ascii)</text>
  <line class="msg-line" x1="95.0" y1="240.0" x2="575.0" y2="240.0" stroke-dasharray="6,3" marker-start="url(#seq-arrow)"/>
  <text class="msg-label" x="335.0" y="232.0">DiagramSpec</text>
</svg>

<em>Provider Interpretation Flow</em>

</div>


### Supported Providers

| Provider | Model Default | API Key | Notes |
|----------|---------------|---------|-------|
| `anthropic` | claude-haiku-4-5 | `ANTHROPIC_API_KEY` | Recommended for speed |
| `openai` | gpt-4o-mini | `OPENAI_API_KEY` | JSON mode response format |
| `ollama` | llama3.2 | None needed | Local, zero-cost |
| `none` | — | — | Heuristic fallback only |

## Configuration


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="658" height="220" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <style>
    .mdview-diagram .table-header-bg { fill: #24283b; }
    .mdview-diagram .table-cell-bg { fill: none; }
    .mdview-diagram .table-border { stroke: #7aa2f7; stroke-width: 1; fill: none; }
    .mdview-diagram .table-header-text { fill: #9ece6a; font-weight: 600; white-space: pre; }
    .mdview-diagram .table-cell-text { fill: #a9b1d6; white-space: pre; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .table-header-bg { fill: #e8e8f0; }
      .mdview-diagram .table-border { stroke: #2e7de9; }
      .mdview-diagram .table-header-text { fill: #587539; }
      .mdview-diagram .table-cell-text { fill: #343b58; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="658" height="220" rx="6"/>
  <rect class="table-border" x="20" y="20" width="617.6" height="180.0"/>
  <rect class="table-header-bg" x="20" y="20.0" width="617.6" height="30"/>
  <text class="table-header-text" x="63.6" y="35.0" text-anchor="middle" dominant-baseline="central">Section</text>
  <text class="table-header-text" x="163.4" y="35.0" text-anchor="middle" dominant-baseline="central">Key</text>
  <text class="table-header-text" x="275.8" y="35.0" text-anchor="middle" dominant-baseline="central">Default</text>
  <text class="table-header-text" x="484.8" y="35.0" text-anchor="middle" dominant-baseline="central">Description</text>
  <line class="table-border" x1="20" y1="50.0" x2="637.6" y2="50.0"/>
  <text class="table-cell-text" x="63.6" y="65.0" text-anchor="middle" dominant-baseline="central">ai</text>
  <text class="table-cell-text" x="163.4" y="65.0" text-anchor="middle" dominant-baseline="central">provider</text>
  <text class="table-cell-text" x="275.8" y="65.0" text-anchor="middle" dominant-baseline="central">none</text>
  <text class="table-cell-text" x="484.8" y="65.0" text-anchor="middle" dominant-baseline="central">anthropic / openai / ollama / none</text>
  <text class="table-cell-text" x="63.6" y="95.0" text-anchor="middle" dominant-baseline="central">ai</text>
  <text class="table-cell-text" x="163.4" y="95.0" text-anchor="middle" dominant-baseline="central">model</text>
  <text class="table-cell-text" x="275.8" y="95.0" text-anchor="middle" dominant-baseline="central">(auto)</text>
  <text class="table-cell-text" x="484.8" y="95.0" text-anchor="middle" dominant-baseline="central">Model name (e.g. claude-haiku-4-5)</text>
  <text class="table-cell-text" x="63.6" y="125.0" text-anchor="middle" dominant-baseline="central">ai</text>
  <text class="table-cell-text" x="163.4" y="125.0" text-anchor="middle" dominant-baseline="central">api_key_env</text>
  <text class="table-cell-text" x="275.8" y="125.0" text-anchor="middle" dominant-baseline="central">(auto)</text>
  <text class="table-cell-text" x="484.8" y="125.0" text-anchor="middle" dominant-baseline="central">Env var with API key</text>
  <text class="table-cell-text" x="63.6" y="155.0" text-anchor="middle" dominant-baseline="central"></text>
  <text class="table-cell-text" x="163.4" y="155.0" text-anchor="middle" dominant-baseline="central">theme</text>
  <text class="table-cell-text" x="275.8" y="155.0" text-anchor="middle" dominant-baseline="central">tokyo-night</text>
  <text class="table-cell-text" x="484.8" y="155.0" text-anchor="middle" dominant-baseline="central">Color theme name</text>
  <text class="table-cell-text" x="63.6" y="185.0" text-anchor="middle" dominant-baseline="central">diagrams</text>
  <text class="table-cell-text" x="163.4" y="185.0" text-anchor="middle" dominant-baseline="central">fallback</text>
  <text class="table-cell-text" x="275.8" y="185.0" text-anchor="middle" dominant-baseline="central">heuristic</text>
  <text class="table-cell-text" x="484.8" y="185.0" text-anchor="middle" dominant-baseline="central">heuristic / svgbob / none</text>
  <line class="table-border" x1="107.2" y1="20" x2="107.2" y2="200.0"/>
  <line class="table-border" x1="219.6" y1="20" x2="219.6" y2="200.0"/>
  <line class="table-border" x1="332.0" y1="20" x2="332.0" y2="200.0"/>
  <line class="table-border" x1="20" y1="50.0" x2="637.6" y2="50.0"/>
  <line class="table-border" x1="20" y1="80.0" x2="637.6" y2="80.0"/>
  <line class="table-border" x1="20" y1="110.0" x2="637.6" y2="110.0"/>
  <line class="table-border" x1="20" y1="140.0" x2="637.6" y2="140.0"/>
  <line class="table-border" x1="20" y1="170.0" x2="637.6" y2="170.0"/>
</svg>

<em>Configuration Options (mdview.yaml)</em>

</div>


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


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="720" height="278" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <defs>
    <marker id="arrowhead" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <style>
    .mdview-diagram .state-node { stroke: #7aa2f7; stroke-width: 2; fill: #24283b; rx: 20; }
    .mdview-diagram .state-initial { stroke: #7aa2f7; stroke-width: 2.5; }
    .mdview-diagram .state-text { fill: #9ece6a; font-weight: 600; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .state-node { stroke: #2e7de9; fill: #e8e8f0; }
      .mdview-diagram .state-initial { stroke: #2e7de9; }
      .mdview-diagram .state-text { fill: #587539; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="720" height="278" rx="6"/>
  <rect class="state-node" x="20.0" y="50.0" width="100.0" height="44.0" rx="20"/>
  <text class="state-text" x="70.0" y="72.0" text-anchor="middle" dominant-baseline="central">Flow</text>
  <rect class="state-node" x="216.0" y="50.0" width="116.0" height="44.0" rx="20"/>
  <text class="state-text" x="274.0" y="72.0" text-anchor="middle" dominant-baseline="central">Sequence</text>
  <rect class="state-node" x="431.0" y="50.0" width="125.5" height="44.0" rx="20"/>
  <text class="state-text" x="493.8" y="72.0" text-anchor="middle" dominant-baseline="central">Wireframe</text>
  <rect class="state-node" x="560.0" y="50.0" width="100.0" height="44.0" rx="20"/>
  <text class="state-text" x="610.0" y="72.0" text-anchor="middle" dominant-baseline="central">Table</text>
  <rect class="state-node" x="20.0" y="174.0" width="125.5" height="44.0" rx="20"/>
  <text class="state-text" x="82.8" y="196.0" text-anchor="middle" dominant-baseline="central">Box/Class</text>
  <rect class="state-node" x="263.5" y="174.0" width="163.5" height="44.0" rx="20"/>
  <text class="state-text" x="345.2" y="196.0" text-anchor="middle" dominant-baseline="central">State Machine</text>
  <line class="arrow-line" x1="120.0" y1="72.0" x2="216.0" y2="72.0" marker-end="url(#arrowhead)"/>
  <line class="arrow-line" x1="332.0" y1="72.0" x2="431.0" y2="72.0" marker-end="url(#arrowhead)"/>
  <line class="arrow-line" x1="556.5" y1="72.0" x2="560.0" y2="72.0" marker-end="url(#arrowhead)"/>
  <path class="arrow-line" d="M 560.0,72.0 C -40.0,134.0 -40.0,134.0 20.0,196.0" marker-end="url(#arrowhead)"/>
  <line class="arrow-line" x1="145.5" y1="196.0" x2="263.5" y2="196.0" marker-end="url(#arrowhead)"/>
</svg>

<em>Supported Diagram Types</em>

</div>


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
