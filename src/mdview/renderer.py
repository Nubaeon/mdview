"""Markdown + diagram renderer with terminal and HTML output.

Terminal mode: Uses rich for markdown, shows diagram source in code blocks.
HTML mode: Self-contained HTML with inline SVGs from mermaid.ink + kroki.io.

Supported diagram types:
- ```mermaid  → rendered via mermaid.ink
- ```svgbob   → rendered via kroki.io/svgbob
- ```ditaa    → rendered via kroki.io/ditaa
- Unmarked ASCII art → auto-detected and rendered via kroki.io/svgbob

Usage:
    render_terminal("path/to/SPEC.md")           # Print to terminal
    render_html("path/to/SPEC.md", "output.html") # Generate HTML
    render_file("path/to/SPEC.md", format="html") # Auto-detect
"""

from __future__ import annotations

import html
import logging
import re
import sys
import webbrowser
from pathlib import Path
from typing import TextIO

from .diagrams import DiagramType, extract_diagram_blocks, render_svg

logger = logging.getLogger(__name__)


def _strip_frontmatter(text: str) -> tuple[dict | None, str]:
    """Strip YAML frontmatter from markdown, return (metadata, body).

    Frontmatter is delimited by --- at the start of the file.
    """
    if not text.startswith("---"):
        return None, text

    # Find closing ---
    end = text.find("\n---", 3)
    if end == -1:
        return None, text

    frontmatter_text = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")

    # Parse YAML if available
    metadata = None
    try:
        import yaml
        metadata = yaml.safe_load(frontmatter_text)
    except (ImportError, Exception):
        pass

    return metadata, body


def render_terminal(
    filepath: str | Path,
    *,
    width: int | None = None,
    output: TextIO | None = None,
) -> None:
    """Render a markdown file to the terminal using rich.

    Mermaid blocks are shown as syntax-highlighted source code
    with a header indicating they're diagrams.

    Args:
        filepath: Path to markdown file.
        width: Console width (None = auto-detect).
        output: Output stream (None = stdout).
    """
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.syntax import Syntax

    filepath = Path(filepath)
    text = filepath.read_text(encoding="utf-8")
    metadata, body = _strip_frontmatter(text)

    console = Console(file=output or sys.stdout, width=width)

    # Show file header
    title = filepath.name
    if metadata and isinstance(metadata, dict):
        # Try to extract a meaningful title from frontmatter
        for key in ("title", "name", "description"):
            if key in metadata:
                title = f"{filepath.name} — {metadata[key]}"
                break

    console.rule(f"[bold blue]{title}[/]")
    console.print()

    # Split body around diagram blocks for mixed rendering
    blocks = extract_diagram_blocks(body)

    if not blocks:
        # No diagrams — render entire body as markdown
        console.print(Markdown(body))
        console.print()
        return

    # Diagram type labels for terminal display
    _TYPE_LABELS = {
        DiagramType.MERMAID: "Mermaid Diagram",
        DiagramType.SVGBOB: "SVG Bob Diagram",
        DiagramType.DITAA: "Ditaa Diagram",
        DiagramType.ASCII_AUTO: "ASCII Diagram",
    }

    # Render sections between diagram blocks
    lines = body.split("\n")
    cursor = 0

    for block in blocks:
        # Render markdown before this diagram block
        if cursor < block.start_line:
            md_section = "\n".join(lines[cursor:block.start_line])
            if md_section.strip():
                console.print(Markdown(md_section))
                console.print()

        # Render diagram block as a panel with syntax highlighting
        type_label = _TYPE_LABELS.get(block.diagram_type, "Diagram")
        diagram_title = block.title or type_label
        syntax = Syntax(
            block.source,
            "text",
            theme="monokai",
            line_numbers=False,
            word_wrap=True,
        )
        console.print(Panel(
            syntax,
            title=f"[bold cyan]{diagram_title}[/]",
            subtitle=f"[dim]{type_label} — use --html to render as SVG[/]",
            border_style="cyan",
        ))
        console.print()

        cursor = block.end_line + 1

    # Render any remaining markdown after last mermaid block
    if cursor < len(lines):
        remaining = "\n".join(lines[cursor:])
        if remaining.strip():
            console.print(Markdown(remaining))
            console.print()

    # Show frontmatter summary if present
    if metadata and isinstance(metadata, dict):
        console.rule("[dim]Frontmatter[/]")
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                console.print(f"  [dim]{key}:[/] {value}")
            elif isinstance(value, dict):
                console.print(f"  [dim]{key}:[/] {{{len(value)} keys}}")
            elif isinstance(value, list):
                console.print(f"  [dim]{key}:[/] [{len(value)} items]")
        console.print()


def render_html(
    filepath: str | Path,
    output_path: str | Path | None = None,
    *,
    open_browser: bool = False,
    diagram_service: str | None = None,
) -> str:
    """Render a markdown file to self-contained HTML with inline SVGs.

    Args:
        filepath: Path to markdown file.
        output_path: Where to write HTML. None = return as string.
        open_browser: Open in default browser after rendering.
        diagram_service: Mermaid rendering service URL.

    Returns:
        HTML string.
    """
    filepath = Path(filepath)
    text = filepath.read_text(encoding="utf-8")
    metadata, body = _strip_frontmatter(text)

    # Extract title
    title = filepath.stem
    if metadata and isinstance(metadata, dict):
        for key in ("title", "name"):
            if key in metadata:
                title = metadata[key]
                break

    # Convert markdown to HTML (basic conversion)
    body_html = _markdown_to_html(body, diagram_service=diagram_service)

    # Generate table of contents from headings
    toc_html = _generate_toc(body)

    # Build self-contained HTML
    html_doc = _HTML_TEMPLATE.format(
        title=html.escape(title),
        body=body_html,
        toc=toc_html,
        filename=html.escape(filepath.name),
    )

    if output_path:
        output_path = Path(output_path)
        output_path.write_text(html_doc, encoding="utf-8")
        logger.info(f"HTML written to {output_path}")

        if open_browser:
            webbrowser.open(f"file://{output_path.resolve()}")

    return html_doc


def render_file(
    filepath: str | Path,
    *,
    format: str = "terminal",
    output_path: str | Path | None = None,
    open_browser: bool = False,
    width: int | None = None,
) -> None:
    """Render a file in the specified format.

    Args:
        filepath: Path to markdown file.
        format: "terminal" or "html".
        output_path: For HTML, where to write. None = auto-name.
        open_browser: For HTML, open in browser.
        width: For terminal, console width.
    """
    filepath = Path(filepath)

    if format == "html":
        if output_path is None:
            output_path = filepath.with_suffix(".html")
        render_html(filepath, output_path, open_browser=open_browser)
        print(f"Rendered: {output_path}")
    else:
        render_terminal(filepath, width=width)


def _markdown_to_html(
    markdown_text: str,
    *,
    diagram_service: str | None = None,
) -> str:
    """Convert markdown to HTML, rendering mermaid blocks as inline SVGs.

    Uses a simple regex-based converter. For complex markdown, falls back
    to the markdown library if available.
    """
    blocks = extract_diagram_blocks(markdown_text)
    lines = markdown_text.split("\n")

    # Try using the markdown library for better conversion
    try:
        import markdown as md_lib
        has_markdown_lib = True
    except ImportError:
        has_markdown_lib = False

    if not blocks:
        # No mermaid — convert straight
        if has_markdown_lib:
            return md_lib.markdown(
                markdown_text,
                extensions=["tables", "fenced_code", "toc"],
            )
        return _simple_md_to_html(markdown_text)

    # Build HTML with rendered diagrams replacing mermaid blocks
    parts: list[str] = []
    cursor = 0

    for i, block in enumerate(blocks):
        # Convert markdown section before this block
        md_section = "\n".join(lines[cursor:block.start_line])
        if md_section.strip():
            if has_markdown_lib:
                parts.append(md_lib.markdown(
                    md_section,
                    extensions=["tables", "fenced_code", "toc"],
                ))
            else:
                parts.append(_simple_md_to_html(md_section))

        # Render diagram to SVG
        svg = render_svg(block.source, block.diagram_type, service_url=diagram_service)
        diagram_title = block.title or f"Diagram {i + 1}"

        if svg:
            parts.append(
                f'<figure class="diagram-container" data-diagram-id="{i}">\n'
                f'  <figcaption>{html.escape(diagram_title)}</figcaption>\n'
                f'  <div class="diagram-preview">\n'
                f'    <div class="diagram-svg">{svg}</div>\n'
                f'    <div class="diagram-expand-hint">'
                f'Click to expand</div>\n'
                f'  </div>\n'
                f'</figure>\n'
            )
        else:
            # Fallback: show source in a code block
            parts.append(
                f'<figure class="diagram-container diagram-fallback">\n'
                f'  <figcaption>{html.escape(diagram_title)} '
                f'(render unavailable)</figcaption>\n'
                f'  <pre><code>{html.escape(block.source)}</code></pre>\n'
                f'</figure>\n'
            )

        cursor = block.end_line + 1

    # Convert remaining markdown
    if cursor < len(lines):
        remaining = "\n".join(lines[cursor:])
        if remaining.strip():
            if has_markdown_lib:
                parts.append(md_lib.markdown(
                    remaining,
                    extensions=["tables", "fenced_code", "toc"],
                ))
            else:
                parts.append(_simple_md_to_html(remaining))

    return "\n".join(parts)


def _generate_toc(markdown_text: str) -> str:
    """Generate HTML table of contents from markdown headings."""
    headings: list[tuple[int, str]] = []
    in_code = False

    for line in markdown_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            level = min(level, 6)
            text = stripped[level:].strip()
            if text:
                headings.append((level, text))

    if len(headings) < 3:
        return ""  # Not enough headings to warrant a TOC

    items: list[str] = []
    for level, text in headings:
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[\s]+', '-', slug).strip('-')
        indent = "  " * (level - 1)
        items.append(f'{indent}<li><a href="#{html.escape(slug)}">'
                     f'{html.escape(text)}</a></li>')

    return (
        '<details class="toc" open>\n'
        '  <summary>Table of Contents</summary>\n'
        '  <ul>\n'
        + "\n".join(items)
        + '\n  </ul>\n'
        '</details>\n'
    )


def _simple_md_to_html(text: str) -> str:
    """Minimal markdown to HTML — headings, bold, italic, code, links, lists.

    Used when the `markdown` library is not installed.
    """
    result_lines: list[str] = []
    in_code_block = False
    in_list = False

    for line in text.split("\n"):
        stripped = line.strip()

        # Code blocks
        if stripped.startswith("```"):
            if in_code_block:
                result_lines.append("</code></pre>")
                in_code_block = False
            else:
                lang = stripped[3:].strip()
                cls = f' class="language-{html.escape(lang)}"' if lang else ""
                result_lines.append(f"<pre><code{cls}>")
                in_code_block = True
            continue

        if in_code_block:
            result_lines.append(html.escape(line))
            continue

        # Close list if no longer in one
        if in_list and not stripped.startswith(("- ", "* ", "1.")):
            result_lines.append("</ul>")
            in_list = False

        # Empty line
        if not stripped:
            result_lines.append("")
            continue

        # Headings
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            level = min(level, 6)
            content = stripped[level:].strip()
            slug = re.sub(r'[^\w\s-]', '', content.lower())
            slug = re.sub(r'[\s]+', '-', slug).strip('-')
            result_lines.append(
                f'<h{level} id="{html.escape(slug)}">'
                f'{_inline_md(content)}</h{level}>'
            )
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            result_lines.append("<hr>")
            continue

        # List items
        if stripped.startswith(("- ", "* ")):
            if not in_list:
                result_lines.append("<ul>")
                in_list = True
            result_lines.append(f"<li>{_inline_md(stripped[2:])}</li>")
            continue

        # Tables (basic)
        if "|" in stripped:
            if stripped.replace("|", "").replace("-", "").replace(" ", "") == "":
                continue  # Separator row
            cells = [c.strip() for c in stripped.split("|")]
            cells = [c for c in cells if c]  # Remove empty edge cells
            row = "".join(f"<td>{_inline_md(c)}</td>" for c in cells)
            result_lines.append(f"<tr>{row}</tr>")
            continue

        # Paragraph
        result_lines.append(f"<p>{_inline_md(stripped)}</p>")

    if in_list:
        result_lines.append("</ul>")
    if in_code_block:
        result_lines.append("</code></pre>")

    return "\n".join(result_lines)


def _inline_md(text: str) -> str:
    """Convert inline markdown: bold, italic, code, links."""
    text = html.escape(text)
    # Code (must come first to avoid interfering with other patterns)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    # Links
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


# Self-contained HTML template with dark/light theme support
_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root {{
    --bg: #1a1b26;
    --fg: #a9b1d6;
    --heading: #7aa2f7;
    --accent: #9ece6a;
    --border: #3b4261;
    --code-bg: #24283b;
    --link: #7dcfff;
    --table-stripe: #1e2030;
  }}
  @media (prefers-color-scheme: light) {{
    :root {{
      --bg: #ffffff;
      --fg: #343b58;
      --heading: #2e7de9;
      --accent: #587539;
      --border: #c0caf5;
      --code-bg: #f0f0f4;
      --link: #166775;
      --table-stripe: #f5f5f8;
    }}
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--fg);
    line-height: 1.7;
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }}
  h1, h2, h3, h4, h5, h6 {{
    color: var(--heading);
    margin: 1.5em 0 0.5em;
    line-height: 1.3;
  }}
  h1 {{ font-size: 2em; border-bottom: 2px solid var(--border); padding-bottom: 0.3em; }}
  h2 {{ font-size: 1.5em; border-bottom: 1px solid var(--border); padding-bottom: 0.2em; }}
  h3 {{ font-size: 1.25em; }}
  p {{ margin: 0.8em 0; }}
  a {{ color: var(--link); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  code {{
    background: var(--code-bg);
    padding: 0.15em 0.4em;
    border-radius: 3px;
    font-size: 0.9em;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  }}
  pre {{
    background: var(--code-bg);
    padding: 1em;
    border-radius: 6px;
    overflow-x: auto;
    margin: 1em 0;
    border: 1px solid var(--border);
  }}
  pre code {{
    background: none;
    padding: 0;
    font-size: 0.85em;
    line-height: 1.5;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
  }}
  th, td {{
    padding: 0.5em 0.8em;
    border: 1px solid var(--border);
    text-align: left;
  }}
  tr:nth-child(even) {{ background: var(--table-stripe); }}
  th {{ background: var(--code-bg); font-weight: 600; }}
  ul, ol {{ padding-left: 1.5em; margin: 0.5em 0; }}
  li {{ margin: 0.3em 0; }}
  hr {{ border: none; border-top: 1px solid var(--border); margin: 2em 0; }}
  blockquote {{
    border-left: 3px solid var(--accent);
    padding-left: 1em;
    margin: 1em 0;
    color: var(--fg);
    opacity: 0.85;
  }}
  /* Diagram inline preview */
  .diagram-container {{
    margin: 1.5em 0;
    position: relative;
  }}
  .diagram-container figcaption {{
    font-size: 0.85em;
    color: var(--accent);
    margin-bottom: 0.5em;
    font-weight: 500;
    text-align: center;
  }}
  .diagram-preview {{
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--code-bg);
    padding: 1em;
    text-align: center;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    max-height: 400px;
  }}
  .diagram-preview:hover {{
    border-color: var(--accent);
  }}
  .diagram-preview:hover .diagram-expand-hint {{
    opacity: 1;
  }}
  .diagram-preview svg {{
    max-width: 100%;
    height: auto;
  }}
  .diagram-expand-hint {{
    position: absolute;
    bottom: 8px;
    right: 12px;
    font-size: 0.75em;
    color: var(--accent);
    opacity: 0.4;
    transition: opacity 0.2s;
    pointer-events: none;
  }}
  .diagram-fallback pre {{
    text-align: left;
  }}
  /* Fullscreen lightbox */
  .lightbox-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    z-index: 1000;
    background: var(--bg);
  }}
  .lightbox-overlay.active {{
    display: flex;
    flex-direction: column;
  }}
  .lightbox-toolbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    background: var(--code-bg);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }}
  .lightbox-title {{
    font-size: 0.9em;
    color: var(--accent);
    font-weight: 500;
  }}
  .lightbox-controls {{
    display: flex;
    gap: 6px;
    align-items: center;
  }}
  .lightbox-controls button {{
    background: var(--bg);
    color: var(--fg);
    border: 1px solid var(--border);
    border-radius: 4px;
    width: 32px;
    height: 32px;
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.15s, border-color 0.15s;
  }}
  .lightbox-controls button:hover {{
    background: var(--code-bg);
    border-color: var(--accent);
  }}
  .lightbox-zoom-label {{
    font-size: 0.8em;
    color: var(--fg);
    opacity: 0.7;
    min-width: 48px;
    text-align: center;
  }}
  .lightbox-close {{
    width: 36px !important;
    height: 36px !important;
    font-size: 20px !important;
    margin-left: 12px;
    color: var(--accent) !important;
  }}
  .lightbox-viewport {{
    flex: 1;
    overflow: hidden;
    cursor: grab;
    position: relative;
  }}
  .lightbox-viewport:active {{
    cursor: grabbing;
  }}
  .lightbox-content {{
    transform-origin: 0 0;
    position: absolute;
    top: 0;
    left: 0;
  }}
  .lightbox-content svg {{
    max-width: none;
    height: auto;
    display: block;
  }}
  .file-header {{
    font-size: 0.8em;
    color: var(--fg);
    opacity: 0.5;
    margin-bottom: 2em;
  }}
  /* Table of contents */
  .toc {{
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1em 1.5em;
    margin: 1.5em 0;
  }}
  .toc summary {{
    cursor: pointer;
    font-weight: 600;
    color: var(--heading);
    margin-bottom: 0.5em;
  }}
  .toc ul {{
    list-style: none;
    padding-left: 0;
  }}
  .toc ul ul {{
    padding-left: 1.2em;
  }}
  .toc li {{
    margin: 0.2em 0;
  }}
  .toc a {{
    color: var(--link);
    text-decoration: none;
  }}
  .toc a:hover {{
    text-decoration: underline;
  }}
  /* Keyboard hint in lightbox */
  .lightbox-hint {{
    position: absolute;
    bottom: 12px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.75em;
    color: var(--fg);
    opacity: 0.3;
    pointer-events: none;
  }}
</style>
</head>
<body>
<div class="file-header">{filename}</div>
{toc}
{body}
<!-- Lightbox overlay for fullscreen diagram viewing -->
<div class="lightbox-overlay" id="lightbox">
  <div class="lightbox-toolbar">
    <span class="lightbox-title" id="lightbox-title"></span>
    <div class="lightbox-controls">
      <button id="lb-zoom-out" title="Zoom out (-)">&#x2212;</button>
      <span class="lightbox-zoom-label" id="lb-zoom-label">100%</span>
      <button id="lb-zoom-in" title="Zoom in (+)">+</button>
      <button id="lb-fit" title="Fit to screen (F)">&#x2922;</button>
      <button id="lb-reset" title="Reset zoom (0)">1:1</button>
      <button class="lightbox-close" id="lb-close" title="Close (Esc)">&times;</button>
    </div>
  </div>
  <div class="lightbox-viewport" id="lb-viewport">
    <div class="lightbox-content" id="lb-content"></div>
    <div class="lightbox-hint">Scroll to zoom &middot; Drag to pan &middot; Esc to close</div>
  </div>
</div>
<script>
// Lightbox: click diagram to expand fullscreen with pan/zoom
(function() {{
  var overlay = document.getElementById('lightbox');
  var viewport = document.getElementById('lb-viewport');
  var content = document.getElementById('lb-content');
  var titleEl = document.getElementById('lightbox-title');
  var zoomLabel = document.getElementById('lb-zoom-label');

  var scale = 1, panX = 0, panY = 0;
  var isPanning = false, dragStartX = 0, dragStartY = 0;
  var minScale = 0.1, maxScale = 10;

  function applyTransform() {{
    content.style.transform = 'translate(' + panX + 'px,' + panY + 'px) scale(' + scale + ')';
    zoomLabel.textContent = Math.round(scale * 100) + '%';
  }}

  function fitToScreen() {{
    var svg = content.querySelector('svg');
    if (!svg) return;
    var vw = viewport.clientWidth;
    var vh = viewport.clientHeight;
    var sw = svg.getAttribute('width') || svg.getBoundingClientRect().width / scale;
    var sh = svg.getAttribute('height') || svg.getBoundingClientRect().height / scale;
    sw = parseFloat(sw); sh = parseFloat(sh);
    if (sw <= 0 || sh <= 0) return;
    scale = Math.min(vw / sw, vh / sh) * 0.9;
    panX = (vw - sw * scale) / 2;
    panY = (vh - sh * scale) / 2;
    applyTransform();
  }}

  function openLightbox(diagramEl) {{
    var fig = diagramEl.closest('.diagram-container');
    var caption = fig ? fig.querySelector('figcaption') : null;
    titleEl.textContent = caption ? caption.textContent : 'Diagram';
    var svgEl = diagramEl.querySelector('.diagram-svg');
    content.innerHTML = svgEl ? svgEl.innerHTML : '';
    scale = 1; panX = 0; panY = 0;
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    // Auto-fit after a frame (so dimensions are available)
    requestAnimationFrame(fitToScreen);
  }}

  function closeLightbox() {{
    overlay.classList.remove('active');
    document.body.style.overflow = '';
    content.innerHTML = '';
  }}

  // Click diagram previews to open
  document.querySelectorAll('.diagram-preview').forEach(function(el) {{
    el.addEventListener('click', function() {{ openLightbox(el); }});
  }});

  // Close button
  document.getElementById('lb-close').addEventListener('click', closeLightbox);

  // Click outside diagram (on viewport background) to close
  viewport.addEventListener('dblclick', function(e) {{
    if (e.target === viewport) closeLightbox();
  }});

  // Escape key
  document.addEventListener('keydown', function(e) {{
    if (!overlay.classList.contains('active')) return;
    if (e.key === 'Escape') closeLightbox();
    else if (e.key === '+' || e.key === '=') {{
      scale = Math.min(maxScale, scale * 1.25);
      applyTransform();
    }}
    else if (e.key === '-') {{
      scale = Math.max(minScale, scale * 0.8);
      applyTransform();
    }}
    else if (e.key === '0') {{
      scale = 1; panX = 0; panY = 0;
      applyTransform();
    }}
    else if (e.key === 'f' || e.key === 'F') {{
      fitToScreen();
    }}
  }});

  // Mouse wheel zoom — centered on cursor position
  viewport.addEventListener('wheel', function(e) {{
    e.preventDefault();
    var rect = viewport.getBoundingClientRect();
    var mx = e.clientX - rect.left;
    var my = e.clientY - rect.top;
    var prev = scale;
    var factor = e.deltaY > 0 ? 0.9 : 1.1;
    scale = Math.min(maxScale, Math.max(minScale, scale * factor));
    // Keep point under cursor stable
    panX = mx - (mx - panX) * (scale / prev);
    panY = my - (my - panY) * (scale / prev);
    applyTransform();
  }});

  // Mouse drag pan
  viewport.addEventListener('mousedown', function(e) {{
    if (e.button !== 0) return;
    isPanning = true;
    dragStartX = e.clientX - panX;
    dragStartY = e.clientY - panY;
    e.preventDefault();
  }});
  document.addEventListener('mousemove', function(e) {{
    if (!isPanning) return;
    panX = e.clientX - dragStartX;
    panY = e.clientY - dragStartY;
    applyTransform();
  }});
  document.addEventListener('mouseup', function() {{ isPanning = false; }});

  // Touch: one-finger pan, two-finger pinch zoom
  var lastTouchDist = 0, lastTouchCenter = null;
  viewport.addEventListener('touchstart', function(e) {{
    if (e.touches.length === 1) {{
      isPanning = true;
      dragStartX = e.touches[0].clientX - panX;
      dragStartY = e.touches[0].clientY - panY;
    }} else if (e.touches.length === 2) {{
      isPanning = false;
      lastTouchDist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      lastTouchCenter = {{
        x: (e.touches[0].clientX + e.touches[1].clientX) / 2,
        y: (e.touches[0].clientY + e.touches[1].clientY) / 2
      }};
    }}
  }}, {{ passive: true }});

  viewport.addEventListener('touchmove', function(e) {{
    if (e.touches.length === 1 && isPanning) {{
      panX = e.touches[0].clientX - dragStartX;
      panY = e.touches[0].clientY - dragStartY;
      applyTransform();
    }} else if (e.touches.length === 2 && lastTouchDist > 0) {{
      var dist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      var cx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      var cy = (e.touches[0].clientY + e.touches[1].clientY) / 2;
      var rect = viewport.getBoundingClientRect();
      var mx = cx - rect.left;
      var my = cy - rect.top;
      var prev = scale;
      scale = Math.min(maxScale, Math.max(minScale, scale * (dist / lastTouchDist)));
      panX = mx - (mx - panX) * (scale / prev);
      panY = my - (my - panY) * (scale / prev);
      lastTouchDist = dist;
      applyTransform();
    }}
  }}, {{ passive: true }});

  viewport.addEventListener('touchend', function() {{
    isPanning = false;
    lastTouchDist = 0;
    lastTouchCenter = null;
  }});

  // Toolbar buttons
  document.getElementById('lb-zoom-in').addEventListener('click', function() {{
    var rect = viewport.getBoundingClientRect();
    var cx = rect.width / 2, cy = rect.height / 2;
    var prev = scale;
    scale = Math.min(maxScale, scale * 1.3);
    panX = cx - (cx - panX) * (scale / prev);
    panY = cy - (cy - panY) * (scale / prev);
    applyTransform();
  }});
  document.getElementById('lb-zoom-out').addEventListener('click', function() {{
    var rect = viewport.getBoundingClientRect();
    var cx = rect.width / 2, cy = rect.height / 2;
    var prev = scale;
    scale = Math.max(minScale, scale * 0.7);
    panX = cx - (cx - panX) * (scale / prev);
    panY = cy - (cy - panY) * (scale / prev);
    applyTransform();
  }});
  document.getElementById('lb-reset').addEventListener('click', function() {{
    scale = 1; panX = 0; panY = 0;
    applyTransform();
  }});
  document.getElementById('lb-fit').addEventListener('click', fitToScreen);
}})();
</script>
</body>
</html>"""
