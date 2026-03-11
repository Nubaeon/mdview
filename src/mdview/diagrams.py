"""Diagram rendering: mermaid (mermaid.ink), ASCII art (kroki/svgbob), ditaa.

Zero local dependencies — HTTP calls to mermaid.ink and kroki.io.
Configurable via MDVIEW_DIAGRAM_SERVICE env var for local kroki.
"""

from __future__ import annotations

import base64
import logging
import os
import re
import urllib.request
import urllib.error
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Default services — zero-install
MERMAID_SERVICE = "https://mermaid.ink"
KROKI_SERVICE = "https://kroki.io"

# User-Agent required by mermaid.ink (403 without it)
_USER_AGENT = "mdview/0.1"

# Heuristic: lines containing these suggest ASCII art (not code)
_BOX_CHARS = set("┌┐└┘├┤┬┴┼─│╔╗╚╝║═╠╣╦╩╬+|")
_ARROW_PATTERNS = re.compile(r"[─═]-+[>→]|[<←]-+[─═]|[│║▼▲↓↑]")


class DiagramType(Enum):
    """Supported diagram types."""

    MERMAID = "mermaid"
    SVGBOB = "svgbob"
    DITAA = "ditaa"
    ASCII_AUTO = "ascii_auto"  # Auto-detected ASCII art


@dataclass
class DiagramBlock:
    """A diagram code block extracted from markdown."""

    source: str
    start_line: int
    end_line: int
    diagram_type: DiagramType
    title: str | None = None


def extract_diagram_blocks(markdown: str, *, detect_ascii: bool = True) -> list[DiagramBlock]:
    """Extract diagram code blocks from markdown text.

    Handles:
    - ```mermaid blocks (explicit)
    - ```svgbob blocks (explicit)
    - ```ditaa blocks (explicit)
    - Unmarked code blocks with ASCII art heuristic (if detect_ascii=True)

    Returns list of DiagramBlock with source code and line positions.
    """
    blocks: list[DiagramBlock] = []
    lines = markdown.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line.startswith("```"):
            i += 1
            continue

        # Determine diagram type from fence marker
        lang = line[3:].strip().split()[0] if len(line) > 3 else ""
        lang_lower = lang.lower()

        # Extract optional title
        title = None
        if "title=" in line:
            try:
                title = line.split("title=")[1].strip().strip('"').strip("'")
            except (IndexError, ValueError):
                pass

        # Find closing fence
        start = i + 1
        j = start
        while j < len(lines) and lines[j].strip() != "```":
            j += 1
        source = "\n".join(lines[start:j])

        # Classify
        if lang_lower == "mermaid":
            blocks.append(DiagramBlock(
                source=source, start_line=i, end_line=j,
                diagram_type=DiagramType.MERMAID, title=title,
            ))
        elif lang_lower == "svgbob":
            blocks.append(DiagramBlock(
                source=source, start_line=i, end_line=j,
                diagram_type=DiagramType.SVGBOB, title=title,
            ))
        elif lang_lower == "ditaa":
            blocks.append(DiagramBlock(
                source=source, start_line=i, end_line=j,
                diagram_type=DiagramType.DITAA, title=title,
            ))
        elif detect_ascii and lang_lower in ("", "text", "ascii") and _looks_like_ascii_art(source):
            blocks.append(DiagramBlock(
                source=source, start_line=i, end_line=j,
                diagram_type=DiagramType.ASCII_AUTO, title=title,
            ))

        i = j + 1

    return blocks


def _looks_like_ascii_art(source: str) -> bool:
    """Heuristic: does this code block look like ASCII art diagram?

    Checks for box-drawing characters, arrow patterns, and
    structural regularity typical of diagrams vs code.

    Excludes: file trees (├── patterns), shell output, code.
    """
    if not source.strip():
        return False

    lines = source.strip().split("\n")
    if len(lines) < 3:
        return False

    # Reject file trees (├── <name> or └── <name> patterns dominate)
    # But NOT box separators like ├────────────┤ or box content like │ text │
    tree_lines = 0
    for l in lines:
        stripped = l.strip()
        # File tree: ├── or └── followed by a name (not more box-drawing)
        if ("├── " in l or "└── " in l) and not stripped.endswith(("┤", "┘", "│")):
            tree_lines += 1
        # File tree indent: │ followed by spaces then ├── or └──
        elif stripped.startswith("│") and ("├── " in stripped or "└── " in stripped):
            tree_lines += 1
    if tree_lines > len(lines) * 0.3:
        return False

    # Reject if it looks like code (common code patterns)
    code_indicators = sum(1 for l in lines
                         if l.strip().startswith(('#', '//', 'def ', 'class ',
                                                  'import ', 'from ', 'if ', 'for ',
                                                  'return ', 'async ', 'await ')))
    if code_indicators > len(lines) * 0.2:
        return False

    box_char_lines = 0
    arrow_lines = 0
    has_top_border = False
    has_bottom_border = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if any(c in _BOX_CHARS for c in line):
            box_char_lines += 1
        if _ARROW_PATTERNS.search(line):
            arrow_lines += 1
        border_chars = sum(1 for c in stripped if c in '─═-+┌┐└┘├┤┬┴┼╔╗╚╝╠╣╦╩╬')
        if len(stripped) > 5 and border_chars > len(stripped) * 0.6:
            if i < 2:
                has_top_border = True
            if i > len(lines) - 3:
                has_bottom_border = True

    total = len(lines)
    diagram_ratio = (box_char_lines + arrow_lines) / total

    if has_top_border and has_bottom_border and diagram_ratio > 0.25:
        return True
    return diagram_ratio > 0.45


def render_svg(
    diagram: str,
    diagram_type: DiagramType = DiagramType.MERMAID,
    service_url: str | None = None,
) -> str | None:
    """Render a diagram to SVG via HTTP API.

    Args:
        diagram: Diagram source code.
        diagram_type: Type of diagram (mermaid, svgbob, ditaa).
        service_url: Override service URL.

    Returns:
        SVG string, or None if rendering failed.
    """
    if diagram_type == DiagramType.MERMAID:
        return _render_mermaid(diagram, service_url)
    elif diagram_type in (DiagramType.SVGBOB, DiagramType.ASCII_AUTO):
        # Try native renderers for structure-recognized diagrams (no HTTP needed)
        if diagram_type == DiagramType.ASCII_AUTO:
            from .flowrender import has_flow_structure, render_flow_svg
            from .sequencerender import has_sequence_structure, render_sequence_svg
            from .tablerender import has_table_structure, render_table_svg
            from .boxrender import has_box_structure, render_box_svg
            # Most specific first: flow (boxes + arrows)
            if has_flow_structure(diagram):
                return render_flow_svg(diagram)
            # Sequence diagrams (vertical lanes + horizontal messages)
            if has_sequence_structure(diagram):
                return render_sequence_svg(diagram)
            # Tables (grid intersections)
            if has_table_structure(diagram):
                return render_table_svg(diagram)
            # Plain boxes (most permissive structural match)
            if has_box_structure(diagram):
                return render_box_svg(diagram)
        return _render_kroki(diagram, "svgbob", service_url)
    elif diagram_type == DiagramType.DITAA:
        return _render_kroki(diagram, "ditaa", service_url)
    else:
        logger.warning(f"Unknown diagram type: {diagram_type}")
        return None


def _render_mermaid(diagram: str, service_url: str | None = None) -> str | None:
    """Render mermaid via mermaid.ink or kroki."""
    service = (
        service_url
        or os.environ.get("MDVIEW_DIAGRAM_SERVICE")
        or MERMAID_SERVICE
    )

    if "kroki" in service:
        return _render_kroki(diagram, "mermaid", service)

    encoded = base64.urlsafe_b64encode(diagram.encode("utf-8")).decode("ascii")
    url = f"{service.rstrip('/')}/svg/{encoded}"
    return _http_get(url)


def _prepare_for_svgbob(source: str) -> str:
    """Pre-process diagram source for svgbob rendering.

    Converts Unicode box-drawing to ASCII equivalents and escapes
    characters that svgbob misinterprets in text regions.

    Key insights:
    - svgbob treats ( ) as arc/circle primitives → escape to [ ] in text
    - Unicode arrows (→ ← ▼ ▲) render as text in svgbob — keep them
    - ASCII arrows (-> <-) trigger arrow drawing — avoid converting to these
    """
    result = source
    # Unicode box-drawing → ASCII (more predictable for complex layouts)
    result = result.replace('┌', '+').replace('┐', '+')
    result = result.replace('└', '+').replace('┘', '+')
    result = result.replace('├', '+').replace('┤', '+')
    result = result.replace('┬', '+').replace('┴', '+')
    result = result.replace('┼', '+')
    result = result.replace('─', '-')
    result = result.replace('│', '|')
    # Double-line box drawing
    result = result.replace('╔', '+').replace('╗', '+')
    result = result.replace('╚', '+').replace('╝', '+')
    result = result.replace('║', '|').replace('═', '=')
    result = result.replace('╠', '+').replace('╣', '+')
    result = result.replace('╦', '+').replace('╩', '+')
    result = result.replace('╬', '+')

    # Escape parentheses in text regions (box content + text annotations).
    # svgbob interprets ( ) as arc/circle drawing primitives.
    out_lines = []
    for line in result.split("\n"):
        stripped = line.strip()
        if "(" in line or ")" in line:
            is_box = stripped.startswith("|") and stripped.endswith("|")
            has_text_parens = bool(re.search(r"\w", line) and re.search(r"[()]", line))
            if is_box or has_text_parens:
                line = line.replace("(", "[").replace(")", "]")
        out_lines.append(line)

    return "\n".join(out_lines)


def _render_kroki(
    diagram: str,
    diagram_kind: str,
    service_url: str | None = None,
) -> str | None:
    """Render via kroki (POST with source body)."""
    service = (
        service_url
        or os.environ.get("MDVIEW_DIAGRAM_SERVICE")
        or KROKI_SERVICE
    )

    if diagram_kind == "svgbob":
        diagram = _prepare_for_svgbob(diagram)

    url = f"{service.rstrip('/')}/{diagram_kind}/svg"
    req = urllib.request.Request(
        url,
        data=diagram.encode("utf-8"),
        headers={
            "Content-Type": "text/plain",
            "User-Agent": _USER_AGENT,
        },
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        logger.warning(f"Kroki render failed (HTTP {e.code}) for {diagram_kind}: {url}")
        return None
    except (urllib.error.URLError, TimeoutError) as e:
        logger.warning(f"Kroki render failed (network) for {diagram_kind}: {e}")
        return None


def _http_get(url: str) -> str | None:
    """Simple GET with User-Agent."""
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        logger.warning(f"Diagram render failed (HTTP {e.code}): {url[:100]}")
        return None
    except (urllib.error.URLError, TimeoutError) as e:
        logger.warning(f"Diagram render failed (network): {e}")
        return None


def render_svg_data_uri(
    diagram: str,
    diagram_type: DiagramType = DiagramType.MERMAID,
    service_url: str | None = None,
) -> str | None:
    """Render diagram to an SVG data URI for embedding in HTML."""
    svg = render_svg(diagram, diagram_type, service_url)
    if not svg:
        return None
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
