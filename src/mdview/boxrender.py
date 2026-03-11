"""Native ASCII box diagram → SVG renderer.

Renders AI-generated box diagrams directly to SVG without external APIs.
Handles the patterns that AI tools (Claude Code, Cursor, Copilot) produce:
- Box layouts with ┌─┐│└─┘ or +---+|+---+ borders
- Text content inside boxes (preserved exactly)
- Horizontal separators (├─┤ or +---+)
- Section headers and body text

This renderer parses structure first (find boxes, extract text),
then renders clean SVG. Text is always text, lines are always lines.
"""

from __future__ import annotations

from . import renderlib as rl


def has_box_structure(source: str) -> bool:
    """Check if source contains detectable box structures."""
    grid, width, height = rl.parse_grid(source)
    if width == 0:
        return False
    return len(rl.find_boxes(grid)) > 0


def render_box_svg(source: str) -> str:
    """Render an ASCII box diagram to SVG.

    Args:
        source: ASCII art with box-drawing characters.

    Returns:
        SVG string.
    """
    grid, width, height = rl.parse_grid(source)

    if not grid or width == 0:
        return rl.fallback_svg(source)

    boxes = rl.find_boxes(grid)
    if not boxes:
        return rl.fallback_svg(source)

    texts = rl.extract_box_texts(grid, boxes)

    # Build SVG with tight bounding box
    parts: list[str] = [
        rl.svg_open_tight(boxes, height),
        rl.THEME_CSS,
        rl.svg_background_tight(boxes, height),
    ]

    for box in boxes:
        parts.append(rl.svg_rect(box))
        for sep_row in box.separators:
            parts.append(rl.svg_separator(box, sep_row))

    headers = rl.classify_headers(texts, boxes)
    for i, span in enumerate(texts):
        box = boxes[span.box_index] if 0 <= span.box_index < len(boxes) else None
        parts.append(rl.svg_text(span, is_header=(i in headers), box=box))

    parts.append("</svg>")
    return "\n".join(parts)
