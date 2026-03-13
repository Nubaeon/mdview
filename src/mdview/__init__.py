"""mdview — Lightweight markdown + multi-diagram viewer.

Renders markdown with mermaid, ASCII art (svgbob), and ditaa diagrams
to interactive HTML with fullscreen pan/zoom. Zero local dependencies —
uses mermaid.ink and kroki.io APIs.

Usage:
    mdview SPEC.md                  # Open in browser
    mdview SPEC.md --terminal       # Render in terminal (requires rich)
    mdview serve SPEC.md --watch    # Live reload server
"""

__version__ = "0.1.0"

from .boxrender import has_box_structure, render_box_svg
from .diagrams import DiagramBlock, DiagramType, extract_diagram_blocks, render_svg, render_from_spec
from .specrender import render_spec_svg
from .flowrender import has_flow_structure, render_flow_svg
from .renderer import render_file, render_html, render_terminal
from .sequencerender import has_sequence_structure, render_sequence_svg
from .server import serve
from .tablerender import has_table_structure, render_table_svg
from .wireframerender import has_wireframe_structure, render_wireframe_svg

__all__ = [
    "DiagramBlock",
    "DiagramType",
    "extract_diagram_blocks",
    "has_box_structure",
    "has_flow_structure",
    "has_sequence_structure",
    "has_wireframe_structure",
    "render_box_svg",
    "render_flow_svg",
    "render_sequence_svg",
    "render_from_spec",
    "render_spec_svg",
    "render_svg",
    "render_wireframe_svg",
    "render_file",
    "render_html",
    "render_terminal",
    "serve",
]
