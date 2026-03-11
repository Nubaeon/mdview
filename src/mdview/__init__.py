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
from .diagrams import DiagramBlock, DiagramType, extract_diagram_blocks, render_svg
from .flowrender import has_flow_structure, render_flow_svg
from .renderer import render_file, render_html, render_terminal
from .server import serve

__all__ = [
    "DiagramBlock",
    "DiagramType",
    "extract_diagram_blocks",
    "has_box_structure",
    "has_flow_structure",
    "render_box_svg",
    "render_flow_svg",
    "render_svg",
    "render_file",
    "render_html",
    "render_terminal",
    "serve",
]
