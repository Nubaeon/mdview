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

<svg xmlns="http://www.w3.org/2000/svg" width="704" height="180" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
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
      .mdview-diagram .box-fill { fill: #f8f8fc; }
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
    <marker id="d0-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="704" height="180" rx="6"/>
  <line class="arrow-line" x1="126.0" y1="40.0" x2="186.0" y2="40.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="349.0" y1="40.0" x2="409.0" y2="40.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="489.0" y1="40.0" x2="549.0" y2="40.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="409.0" y1="40.0" x2="135.5" y2="140.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="549.0" y1="40.0" x2="275.5" y2="140.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="135.5" y1="140.0" x2="195.5" y2="140.0" marker-end="url(#d0-ah)"/>
  <rect class="box-fill" x="20.0" y="20.0" width="106.0" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="106.0" height="40.0" rx="6"/>
  <rect class="box-fill" x="186.0" y="20.0" width="163.0" height="40.0" rx="6"/>
  <rect class="box-border" x="186.0" y="20.0" width="163.0" height="40.0" rx="6"/>
  <polygon class="box-fill" points="449.0,20.0 489.0,40.0 449.0,60.0 409.0,40.0"/>
  <polygon class="box-border" points="449.0,20.0 489.0,40.0 449.0,60.0 409.0,40.0"/>
  <rect class="box-fill" x="549.0" y="20.0" width="134.5" height="40.0" rx="6"/>
  <rect class="box-border" x="549.0" y="20.0" width="134.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="20.0" y="120.0" width="115.5" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="120.0" width="115.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="195.5" y="120.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-border" x="195.5" y="120.0" width="80.0" height="40.0" rx="6"/>
  <rect class="arrow-label-bg" x="495.8" y="31.0" width="22.4" height="16.0" rx="3"/>
  <text class="arrow-label" x="507.0" y="40.0" dominant-baseline="central">AI</text>
  <rect class="arrow-label-bg" x="294.1" y="61.0" width="65.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="326.9" y="70.0" dominant-baseline="central">fallback</text>
  <text class="box-header" x="73.0" y="40.0" text-anchor="middle" dominant-baseline="central">Markdown</text>
  <text class="box-text" x="267.5" y="40.0" text-anchor="middle" dominant-baseline="central">Extract Blocks</text>
  <text class="box-text" x="449.0" y="40.0" text-anchor="middle" dominant-baseline="central">Route</text>
  <text class="box-text" x="616.2" y="40.0" text-anchor="middle" dominant-baseline="central">Spec Render</text>
  <text class="box-text" x="77.8" y="140.0" text-anchor="middle" dominant-baseline="central">Heuristic</text>
  <text class="box-text" x="235.5" y="140.0" text-anchor="middle" dominant-baseline="central">SVG</text>
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

<svg xmlns="http://www.w3.org/2000/svg" width="194" height="480" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
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
      .mdview-diagram .box-fill { fill: #f8f8fc; }
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
    <marker id="d1-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="194" height="480" rx="6"/>
  <line class="arrow-line" x1="96.8" y1="60.0" x2="96.8" y2="120.0" marker-end="url(#d1-ah)"/>
  <line class="arrow-line" x1="96.8" y1="160.0" x2="96.8" y2="220.0" marker-end="url(#d1-ah)"/>
  <line class="arrow-line" x1="96.8" y1="260.0" x2="96.8" y2="320.0" marker-end="url(#d1-ah)"/>
  <line class="arrow-line" x1="96.8" y1="360.0" x2="96.8" y2="420.0" marker-end="url(#d1-ah)"/>
  <rect class="box-fill" x="39.0" y="20.0" width="115.5" height="40.0" rx="6"/>
  <rect class="box-border" x="39.0" y="20.0" width="115.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="29.5" y="120.0" width="134.5" height="40.0" rx="6"/>
  <rect class="box-border" x="29.5" y="120.0" width="134.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="29.5" y="220.0" width="134.5" height="40.0" rx="6"/>
  <rect class="box-border" x="29.5" y="220.0" width="134.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="20.0" y="320.0" width="153.5" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="320.0" width="153.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="34.2" y="420.0" width="125.0" height="40.0" rx="6"/>
  <rect class="box-border" x="34.2" y="420.0" width="125.0" height="40.0" rx="6"/>
  <rect class="arrow-label-bg" x="60.4" y="69.0" width="72.8" height="16.0" rx="3"/>
  <text class="arrow-label" x="96.8" y="78.0" dominant-baseline="central">interpret</text>
  <rect class="arrow-label-bg" x="78.3" y="169.0" width="36.8" height="16.0" rx="3"/>
  <text class="arrow-label" x="96.8" y="178.0" dominant-baseline="central">JSON</text>
  <rect class="arrow-label-bg" x="64.0" y="269.0" width="65.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="96.8" y="278.0" dominant-baseline="central">dispatch</text>
  <rect class="arrow-label-bg" x="71.2" y="369.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="96.8" y="378.0" dominant-baseline="central">render</text>
  <text class="box-header" x="96.8" y="40.0" text-anchor="middle" dominant-baseline="central">ASCII Art</text>
  <text class="box-text" x="96.8" y="140.0" text-anchor="middle" dominant-baseline="central">AI Provider</text>
  <text class="box-text" x="96.8" y="240.0" text-anchor="middle" dominant-baseline="central">DiagramSpec</text>
  <text class="box-text" x="96.8" y="340.0" text-anchor="middle" dominant-baseline="central">specrender.py</text>
  <text class="box-text" x="96.8" y="440.0" text-anchor="middle" dominant-baseline="central">Themed SVG</text>
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

<svg xmlns="http://www.w3.org/2000/svg" width="691" height="456" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
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
      .mdview-diagram .box-fill { fill: #f8f8fc; }
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
  <rect class="bg" x="0" y="0" width="691" height="456" rx="6"/>
  <defs>
    <clipPath id="d2-bc0"><rect x="20.0" y="20.0" width="131.0" height="84.0" rx="6"/></clipPath>
    <clipPath id="d2-bc1"><rect x="171.0" y="20.0" width="185.0" height="100.0" rx="6"/></clipPath>
    <clipPath id="d2-bc2"><rect x="376.0" y="20.0" width="248.0" height="100.0" rx="6"/></clipPath>
    <clipPath id="d2-bc3"><rect x="20.0" y="140.0" width="320.0" height="152.0" rx="6"/></clipPath>
    <clipPath id="d2-bc4"><rect x="360.0" y="140.0" width="311.0" height="180.0" rx="6"/></clipPath>
    <clipPath id="d2-bc5"><rect x="20.0" y="340.0" width="293.0" height="96.0" rx="6"/></clipPath>
  </defs>
  <rect class="box-fill" x="20.0" y="20.0" width="131.0" height="84.0" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="131.0" height="84.0" rx="6"/>
  <g clip-path="url(#d2-bc0)">
    <text class="box-header" x="85.5" y="40.0" text-anchor="middle" dominant-baseline="central">cli.py</text>
    <line class="box-separator" x1="20.0" y1="52.0" x2="151.0" y2="52.0"/>
    <text class="box-text" x="32.0" y="74.0">argparse</text>
    <text class="box-text" x="32.0" y="90.0">entry point</text>
  </g>
  <rect class="box-fill" x="171.0" y="20.0" width="185.0" height="100.0" rx="6"/>
  <rect class="box-border" x="171.0" y="20.0" width="185.0" height="100.0" rx="6"/>
  <g clip-path="url(#d2-bc1)">
    <text class="box-header" x="263.5" y="40.0" text-anchor="middle" dominant-baseline="central">renderer.py</text>
    <line class="box-separator" x1="171.0" y1="52.0" x2="356.0" y2="52.0"/>
    <text class="box-text" x="183.0" y="74.0">render_html()</text>
    <text class="box-text" x="183.0" y="90.0">render_terminal()</text>
    <text class="box-text" x="183.0" y="106.0">render_file()</text>
  </g>
  <rect class="box-fill" x="376.0" y="20.0" width="248.0" height="100.0" rx="6"/>
  <rect class="box-border" x="376.0" y="20.0" width="248.0" height="100.0" rx="6"/>
  <g clip-path="url(#d2-bc2)">
    <text class="box-header" x="500.0" y="40.0" text-anchor="middle" dominant-baseline="central">diagrams.py</text>
    <line class="box-separator" x1="376.0" y1="52.0" x2="624.0" y2="52.0"/>
    <text class="box-text" x="388.0" y="74.0">extract_diagram_blocks()</text>
    <text class="box-text" x="388.0" y="90.0">render_svg()</text>
    <text class="box-text" x="388.0" y="106.0">render_from_spec()</text>
  </g>
  <rect class="box-fill" x="20.0" y="140.0" width="320.0" height="152.0" rx="6"/>
  <rect class="box-border" x="20.0" y="140.0" width="320.0" height="152.0" rx="6"/>
  <g clip-path="url(#d2-bc3)">
    <text class="box-header" x="180.0" y="160.0" text-anchor="middle" dominant-baseline="central">Spec Pipeline</text>
    <line class="box-separator" x1="20.0" y1="172.0" x2="340.0" y2="172.0"/>
    <text class="box-text" x="32.0" y="194.0">spec.py — DiagramSpec schema</text>
    <line class="box-separator" x1="20.0" y1="200.0" x2="340.0" y2="200.0"/>
    <text class="box-text" x="32.0" y="222.0">config.py — mdview.yaml loader</text>
    <line class="box-separator" x1="20.0" y1="228.0" x2="340.0" y2="228.0"/>
    <text class="box-text" x="32.0" y="250.0">providers.py — AI backends</text>
    <line class="box-separator" x1="20.0" y1="256.0" x2="340.0" y2="256.0"/>
    <text class="box-text" x="32.0" y="278.0">specrender.py — 6 type renderers</text>
  </g>
  <rect class="box-fill" x="360.0" y="140.0" width="311.0" height="180.0" rx="6"/>
  <rect class="box-border" x="360.0" y="140.0" width="311.0" height="180.0" rx="6"/>
  <g clip-path="url(#d2-bc4)">
    <text class="box-header" x="515.5" y="160.0" text-anchor="middle" dominant-baseline="central">Heuristic Renderers</text>
    <line class="box-separator" x1="360.0" y1="172.0" x2="671.0" y2="172.0"/>
    <text class="box-text" x="372.0" y="194.0">routing.py — confidence scoring</text>
    <line class="box-separator" x1="360.0" y1="200.0" x2="671.0" y2="200.0"/>
    <text class="box-text" x="372.0" y="222.0">flowrender.py</text>
    <line class="box-separator" x1="360.0" y1="228.0" x2="671.0" y2="228.0"/>
    <text class="box-text" x="372.0" y="250.0">sequencerender.py</text>
    <line class="box-separator" x1="360.0" y1="256.0" x2="671.0" y2="256.0"/>
    <text class="box-text" x="372.0" y="278.0">boxrender.py, tablerender.py</text>
    <line class="box-separator" x1="360.0" y1="284.0" x2="671.0" y2="284.0"/>
    <text class="box-text" x="372.0" y="306.0">wireframerender.py</text>
  </g>
  <rect class="box-fill" x="20.0" y="340.0" width="293.0" height="96.0" rx="6"/>
  <rect class="box-border" x="20.0" y="340.0" width="293.0" height="96.0" rx="6"/>
  <g clip-path="url(#d2-bc5)">
    <text class="box-header" x="166.5" y="360.0" text-anchor="middle" dominant-baseline="central">Shared</text>
    <line class="box-separator" x1="20.0" y1="372.0" x2="313.0" y2="372.0"/>
    <text class="box-text" x="32.0" y="394.0">renderlib.py — SVG primitives</text>
    <line class="box-separator" x1="20.0" y1="400.0" x2="313.0" y2="400.0"/>
    <text class="box-text" x="32.0" y="422.0">themes.py — color system</text>
  </g>
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

<svg xmlns="http://www.w3.org/2000/svg" width="866" height="340" style="display:block;margin:auto" class="mdview-diagram">
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
    <marker id="d3-sa" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="msg-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="866" height="340" rx="6"/>
  <rect class="actor-box" x="40.0" y="20" width="159.0" height="32" rx="4"/>
  <text class="actor-text" x="119.5" y="36.0">diagrams.py</text>
  <rect class="actor-box" x="40.0" y="288" width="159.0" height="32" rx="4"/>
  <text class="actor-text" x="119.5" y="304.0">diagrams.py</text>
  <rect class="actor-box" x="249.0" y="20" width="159.0" height="32" rx="4"/>
  <text class="actor-text" x="328.5" y="36.0">MdviewConfig</text>
  <rect class="actor-box" x="249.0" y="288" width="159.0" height="32" rx="4"/>
  <text class="actor-text" x="328.5" y="304.0">MdviewConfig</text>
  <rect class="actor-box" x="458.0" y="20" width="159.0" height="32" rx="4"/>
  <text class="actor-text" x="537.5" y="36.0">create_provider</text>
  <rect class="actor-box" x="458.0" y="288" width="159.0" height="32" rx="4"/>
  <text class="actor-text" x="537.5" y="304.0">create_provider</text>
  <rect class="actor-box" x="667.0" y="20" width="159.0" height="32" rx="4"/>
  <text class="actor-text" x="746.5" y="36.0">AI Provider</text>
  <rect class="actor-box" x="667.0" y="288" width="159.0" height="32" rx="4"/>
  <text class="actor-text" x="746.5" y="304.0">AI Provider</text>
  <line class="lifeline" x1="119.5" y1="64" x2="119.5" y2="276"/>
  <line class="lifeline" x1="328.5" y1="64" x2="328.5" y2="276"/>
  <line class="lifeline" x1="537.5" y1="64" x2="537.5" y2="276"/>
  <line class="lifeline" x1="746.5" y1="64" x2="746.5" y2="276"/>
  <line class="msg-line" x1="119.5" y1="80.0" x2="328.5" y2="80.0" marker-end="url(#d3-sa)"/>
  <text class="msg-label" x="224.0" y="72.0">load()</text>
  <line class="msg-line" x1="119.5" y1="112.0" x2="328.5" y2="112.0" stroke-dasharray="6,3" marker-start="url(#d3-sa)"/>
  <text class="msg-label" x="224.0" y="104.0">AIConfig</text>
  <line class="msg-line" x1="119.5" y1="144.0" x2="537.5" y2="144.0" marker-end="url(#d3-sa)"/>
  <text class="msg-label" x="328.5" y="136.0">create(config)</text>
  <line class="msg-line" x1="119.5" y1="176.0" x2="537.5" y2="176.0" stroke-dasharray="6,3" marker-start="url(#d3-sa)"/>
  <text class="msg-label" x="328.5" y="168.0">Provider</text>
  <line class="msg-line" x1="119.5" y1="208.0" x2="746.5" y2="208.0" marker-end="url(#d3-sa)"/>
  <text class="msg-label" x="433.0" y="200.0">interpret(ascii)</text>
  <line class="msg-line" x1="119.5" y1="240.0" x2="746.5" y2="240.0" stroke-dasharray="6,3" marker-start="url(#d3-sa)"/>
  <text class="msg-label" x="433.0" y="232.0">DiagramSpec</text>
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

<svg xmlns="http://www.w3.org/2000/svg" width="658" height="220" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
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
      .mdview-diagram .box-fill { fill: #f8f8fc; }
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

<svg xmlns="http://www.w3.org/2000/svg" width="720" height="278" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
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
      .mdview-diagram .box-fill { fill: #f8f8fc; }
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
    <marker id="d4-ah" viewBox="0 0 10 10" refX="9" refY="5"
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
  <line class="arrow-line" x1="213.5" y1="72.0" x2="273.5" y2="72.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="437.0" y1="72.0" x2="497.0" y2="72.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="497.0" y1="72.0" x2="213.5" y2="196.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="213.5" y1="196.0" x2="273.5" y2="196.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="437.0" y1="196.0" x2="497.0" y2="196.0" marker-end="url(#d4-ah)"/>
  <rect class="state-node" x="50.0" y="50.0" width="163.5" height="44.0" rx="20"/>
  <rect class="state-node" x="273.5" y="50.0" width="163.5" height="44.0" rx="20"/>
  <rect class="state-node" x="497.0" y="50.0" width="163.5" height="44.0" rx="20"/>
  <rect class="state-node" x="50.0" y="174.0" width="163.5" height="44.0" rx="20"/>
  <rect class="state-node" x="273.5" y="174.0" width="163.5" height="44.0" rx="20"/>
  <rect class="state-node" x="497.0" y="174.0" width="163.5" height="44.0" rx="20"/>
  <text class="state-text" x="131.8" y="72.0" text-anchor="middle" dominant-baseline="central">Flow</text>
  <text class="state-text" x="355.2" y="72.0" text-anchor="middle" dominant-baseline="central">Sequence</text>
  <text class="state-text" x="578.8" y="72.0" text-anchor="middle" dominant-baseline="central">Wireframe</text>
  <text class="state-text" x="131.8" y="196.0" text-anchor="middle" dominant-baseline="central">Table</text>
  <text class="state-text" x="355.2" y="196.0" text-anchor="middle" dominant-baseline="central">Box/Class</text>
  <text class="state-text" x="578.8" y="196.0" text-anchor="middle" dominant-baseline="central">State Machine</text>
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
