"""Spec-based SVG generators — DiagramSpec → themed SVG.

Takes structured DiagramSpec data (from AI interpretation or direct emission)
and produces SVG for each diagram type. No ASCII parsing — the structure is
already known. This is the rendering engine for the AI-driven architecture.

Supported types: flow, sequence, wireframe, table, box.
"""

from __future__ import annotations

import html as html_mod
import logging

from .spec import DiagramSpec, Element, Connection
from .themes import DEFAULT_THEME, Theme

logger = logging.getLogger(__name__)

# Layout constants (px)
PAD = 20         # outer padding
BOX_H = 40       # standard node height
BOX_RX = 6       # box corner radius
LANE_SPACING = 160
MSG_ROW_H = 32
ACTOR_BOX_W = 110
ACTOR_BOX_H = 32


def render_spec_svg(spec: DiagramSpec, theme: Theme | None = None) -> str:
    """Render a DiagramSpec to SVG. Dispatches by spec.type."""
    t = theme or DEFAULT_THEME
    renderer = _RENDERERS.get(spec.type)  # type: ignore[arg-type]
    if renderer is None:
        logger.warning(f"No spec renderer for type: {spec.type!r}")
        return _render_fallback(spec, t)
    return renderer(spec, t)  # type: ignore[operator]


# ── Flow renderer ──────────────────────────────────────────────────

def _render_flow(spec: DiagramSpec, theme: Theme) -> str:
    """Render flow diagram: nodes connected by arrows."""
    elements = spec.elements
    connections = spec.connections
    if not elements:
        return _render_fallback(spec, theme)

    horizontal = spec.layout in ("horizontal", "auto")

    # Measure node sizes
    nodes = _layout_flow_nodes(elements, horizontal)
    id_to_node = {n["id"]: n for n in nodes}

    # Compute canvas size
    max_x = max(n["x"] + n["w"] for n in nodes)
    max_y = max(n["y"] + n["h"] for n in nodes)
    svg_w = max_x + PAD
    svg_h = max_y + PAD

    parts = [
        _svg_open(svg_w, svg_h),
        theme.svg_css(),
        _svg_arrowhead_defs(),
        _svg_bg(svg_w, svg_h),
    ]

    # Layer 1: connection lines (underneath)
    conn_labels: list[str] = []
    for conn in connections:
        src = id_to_node.get(conn.from_id)
        dst = id_to_node.get(conn.to_id)
        if not src or not dst:
            continue
        line_parts, label_parts = _svg_connection_layered(src, dst, conn)
        parts.extend(line_parts)
        conn_labels.extend(label_parts)

    # Layer 2: node shapes (opaque fill + border, on top of arrows)
    for n in nodes:
        is_decision = n.get("elem_type") == "decision"
        if is_decision:
            parts.append(_svg_diamond_fill(n["x"], n["y"], n["w"], n["h"]))
            parts.append(_svg_diamond(n["x"], n["y"], n["w"], n["h"]))
        else:
            # Opaque fill rect first, then border rect
            parts.append(
                f'  <rect class="box-fill" x="{n["x"]:.1f}" y="{n["y"]:.1f}" '
                f'width="{n["w"]:.1f}" height="{n["h"]:.1f}" rx="{BOX_RX}"/>'
            )
            parts.append(
                f'  <rect class="box-border" x="{n["x"]:.1f}" y="{n["y"]:.1f}" '
                f'width="{n["w"]:.1f}" height="{n["h"]:.1f}" rx="{BOX_RX}"/>'
            )

    # Layer 3: connection labels (on top of shapes)
    parts.extend(conn_labels)

    # Layer 4: node text (topmost)
    for n in nodes:
        cx = n["x"] + n["w"] / 2
        cy = n["y"] + n["h"] / 2
        escaped = html_mod.escape(n["label"])
        css = "box-header" if n.get("is_first") else "box-text"
        parts.append(
            f'  <text class="{css}" x="{cx:.1f}" y="{cy:.1f}" '
            f'text-anchor="middle" dominant-baseline="central">{escaped}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def _layout_flow_nodes(
    elements: list[Element], horizontal: bool
) -> list[dict]:
    """Position flow nodes. Returns list of {id, label, x, y, w, h, elem_type}."""
    MAX_ROW_W = 800
    nodes = []
    x, y = PAD, PAD
    gap = 60
    row_max_h = 0.0

    for i, elem in enumerate(elements):
        label = elem.label or elem.id
        w = max(len(label) * 9.5 + 30, 80)
        h = BOX_H

        # Row wrapping for horizontal layout
        if horizontal and nodes and x + w + PAD > MAX_ROW_W:
            x = PAD
            y += row_max_h + gap
            row_max_h = 0.0

        nodes.append({
            "id": elem.id,
            "label": label,
            "elem_type": elem.type,
            "x": x, "y": y,
            "w": w, "h": h,
            "is_first": i == 0,
        })

        if horizontal:
            row_max_h = max(row_max_h, h)
            x += w + gap
        else:
            y += h + gap

    # Center nodes horizontally in vertical layout
    if not horizontal and nodes:
        max_w = max(n["w"] for n in nodes)
        center_x = PAD + max_w / 2
        for n in nodes:
            n["x"] = center_x - n["w"] / 2

    return nodes


# ── Sequence renderer ──────────────────────────────────────────────

def _render_sequence(spec: DiagramSpec, theme: Theme) -> str:
    """Render sequence diagram: actors with ordered messages."""
    actors = [e for e in spec.elements if e.type == "actor"]
    if len(actors) < 2:
        return _render_fallback(spec, theme)

    # Sort connections by order property
    ordered_conns = sorted(
        spec.connections,
        key=lambda c: c.properties.get("order", 0),
    )

    num_actors = len(actors)
    actor_idx = {a.id: i for i, a in enumerate(actors)}

    # Layout — dynamic actor box width based on widest label
    actor_box_w = max(
        max(len(a.label or a.id) * 9.0 + 24 for a in actors),
        ACTOR_BOX_W,
    )
    lane_spacing = max(actor_box_w + 50, LANE_SPACING)
    side_pad = 40
    actor_y = PAD
    lane_xs = [side_pad + actor_box_w / 2 + i * lane_spacing for i in range(num_actors)]
    svg_w = side_pad * 2 + (num_actors - 1) * lane_spacing + actor_box_w

    lifeline_top = actor_y + ACTOR_BOX_H + 12
    num_msgs = max(len(ordered_conns), 1)
    lifeline_bottom = lifeline_top + num_msgs * MSG_ROW_H + 20
    bottom_actor_y = lifeline_bottom + 12
    svg_h = bottom_actor_y + ACTOR_BOX_H + PAD

    parts = [
        _svg_open(svg_w, svg_h),
        theme.sequence_css(),
        _svg_seq_arrowhead_defs(),
        _svg_bg(svg_w, svg_h),
    ]

    # Actor boxes (top + bottom)
    for i, actor in enumerate(actors):
        x = lane_xs[i] - actor_box_w / 2
        label = html_mod.escape(actor.label or actor.id)
        for ay in (actor_y, bottom_actor_y):
            parts.append(
                f'  <rect class="actor-box" x="{x:.1f}" y="{ay}" '
                f'width="{actor_box_w:.1f}" height="{ACTOR_BOX_H}" rx="4"/>'
            )
            parts.append(
                f'  <text class="actor-text" x="{lane_xs[i]:.1f}" '
                f'y="{ay + ACTOR_BOX_H / 2}">{label}</text>'
            )

    # Lifelines
    for i in range(num_actors):
        parts.append(
            f'  <line class="lifeline" x1="{lane_xs[i]:.1f}" y1="{lifeline_top}" '
            f'x2="{lane_xs[i]:.1f}" y2="{lifeline_bottom}"/>'
        )

    # Messages
    for msg_i, conn in enumerate(ordered_conns):
        fi = actor_idx.get(conn.from_id)
        ti = actor_idx.get(conn.to_id)
        if fi is None or ti is None:
            continue

        msg_y = lifeline_top + (msg_i + 0.5) * MSG_ROW_H
        from_x = lane_xs[fi]
        to_x = lane_xs[ti]

        is_dashed = conn.style == "dashed"
        dash_attr = ' stroke-dasharray="6,3"' if is_dashed else ""

        if to_x > from_x:
            marker = ' marker-end="url(#seq-arrow)"'
        else:
            marker = ' marker-start="url(#seq-arrow)"'
            from_x, to_x = to_x, from_x

        parts.append(
            f'  <line class="msg-line" x1="{from_x:.1f}" y1="{msg_y:.1f}" '
            f'x2="{to_x:.1f}" y2="{msg_y:.1f}"{dash_attr}{marker}/>'
        )

        if conn.label:
            label_x = (lane_xs[fi] + lane_xs[ti]) / 2
            label_y = msg_y - 8
            escaped = html_mod.escape(conn.label)
            parts.append(
                f'  <text class="msg-label" x="{label_x:.1f}" '
                f'y="{label_y:.1f}">{escaped}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


# ── Wireframe renderer ─────────────────────────────────────────────

def _render_wireframe(spec: DiagramSpec, theme: Theme) -> str:
    """Render wireframe: nested panels with UI elements."""
    if not spec.elements:
        return _render_fallback(spec, theme)

    # Build element lookup and parent-child tree
    id_to_elem = {e.id: e for e in spec.elements}
    children_of: dict[str, list[str]] = {}
    has_parent: set[str] = set()
    for e in spec.elements:
        children_of[e.id] = e.children
        for cid in e.children:
            has_parent.add(cid)

    # Root elements = those without parents
    roots = [e.id for e in spec.elements if e.id not in has_parent]
    if not roots:
        roots = [spec.elements[0].id]

    # Layout: recursive nested boxes
    layout: dict[str, dict] = {}
    _layout_wireframe(roots, id_to_elem, children_of, layout, PAD, PAD, depth=0)

    # Canvas size
    max_x = max((r["x"] + r["w"] for r in layout.values()), default=200)
    max_y = max((r["y"] + r["h"] for r in layout.values()), default=200)
    svg_w = max_x + PAD
    svg_h = max_y + PAD

    d = theme.dark
    parts = [
        _svg_open(svg_w, svg_h),
        theme.svg_css(),
        f"""  <style>
    .mdview-diagram .wf-panel {{ stroke: {d.border}; stroke-width: 1.5; fill: none; rx: 4; }}
    .mdview-diagram .wf-panel-fill {{ fill: {d.bg_secondary}; fill-opacity: 0.3; rx: 4; }}
    .mdview-diagram .wf-title {{ fill: {d.header_text}; font-weight: 600; font-size: 13px; }}
    .mdview-diagram .wf-label {{ fill: {d.fg}; font-size: 12px; }}
    .mdview-diagram .wf-input {{ stroke: {d.muted}; stroke-width: 1; fill: none; rx: 3; }}
    .mdview-diagram .wf-input-text {{ fill: {d.muted}; font-size: 11px; font-style: italic; }}
    @media (prefers-color-scheme: light) {{
      .mdview-diagram .wf-panel {{ stroke: {theme.light.border}; }}
      .mdview-diagram .wf-panel-fill {{ fill: {theme.light.bg_secondary}; }}
      .mdview-diagram .wf-title {{ fill: {theme.light.header_text}; }}
      .mdview-diagram .wf-label {{ fill: {theme.light.fg}; }}
      .mdview-diagram .wf-input {{ stroke: {theme.light.muted}; }}
      .mdview-diagram .wf-input-text {{ fill: {theme.light.muted}; }}
    }}
  </style>""",
        _svg_bg(svg_w, svg_h),
    ]

    # Render panels (depth-first for proper layering)
    for eid, rect in sorted(layout.items(), key=lambda kv: kv[1].get("depth", 0)):
        elem = id_to_elem.get(eid)
        if not elem:
            continue

        x, y, w, h = rect["x"], rect["y"], rect["w"], rect["h"]

        # Panel background (deeper = more opaque)
        if elem.children or elem.type in ("panel", "sidebar"):
            opacity = min(0.15 + rect.get("depth", 0) * 0.08, 0.5)
            parts.append(
                f'  <rect class="wf-panel-fill" x="{x:.1f}" y="{y:.1f}" '
                f'width="{w:.1f}" height="{h:.1f}" style="fill-opacity:{opacity:.2f}"/>'
            )

        # Panel border
        parts.append(
            f'  <rect class="wf-panel" x="{x:.1f}" y="{y:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}"/>'
        )

        # Title
        if elem.label:
            escaped = html_mod.escape(elem.label)
            parts.append(
                f'  <text class="wf-title" x="{x + 8:.1f}" y="{y + 18:.1f}">{escaped}</text>'
            )

        # Form elements
        if elem.type == "input":
            ix, iy = x + 8, y + 26
            iw = w - 16
            value = elem.properties.get("value", elem.label)
            parts.append(
                f'  <rect class="wf-input" x="{ix:.1f}" y="{iy:.1f}" '
                f'width="{iw:.1f}" height="24"/>'
            )
            if value:
                parts.append(
                    f'  <text class="wf-input-text" x="{ix + 6:.1f}" '
                    f'y="{iy + 15:.1f}">{html_mod.escape(value)}</text>'
                )
        elif elem.type == "form":
            # Render label and a simple input field
            fy = y + 28
            parts.append(
                f'  <rect class="wf-input" x="{x + 8:.1f}" y="{fy:.1f}" '
                f'width="{w - 16:.1f}" height="24"/>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


def _layout_wireframe(
    element_ids: list[str],
    id_to_elem: dict[str, Element],
    children_of: dict[str, list[str]],
    layout: dict[str, dict],
    start_x: float,
    start_y: float,
    depth: int,
) -> tuple[float, float]:
    """Recursively layout wireframe panels. Returns (total_w, total_h)."""
    inner_pad = 12
    title_h = 28

    # Detect horizontal layout: if siblings include a sidebar + panel, lay out side-by-side
    has_sidebar = any(
        (id_to_elem.get(eid) or Element(id="", label="")).type == "sidebar"
        for eid in element_ids
    )
    use_horizontal = has_sidebar and len(element_ids) >= 2

    x = start_x
    y = start_y
    max_w = 0.0
    total_h = 0.0
    row_max_h = 0.0

    for eid in element_ids:
        elem = id_to_elem.get(eid)
        if not elem:
            continue

        kids = children_of.get(eid, [])
        label = elem.label or eid

        # Wider min-widths for realistic wireframe appearance
        if elem.type in ("input", "form"):
            min_w = 200
        elif elem.type == "sidebar":
            min_w = 160
        elif kids:
            min_w = 220
        else:
            min_w = 150

        if kids:
            # Container panel — layout children inside
            child_x = x + inner_pad
            child_y = y + title_h
            child_w, child_h = _layout_wireframe(
                kids, id_to_elem, children_of, layout,
                child_x, child_y, depth + 1,
            )
            w = max(child_w + inner_pad * 2, len(label) * 8 + 30, min_w)
            h = child_h + title_h + inner_pad
        else:
            # Leaf element
            w = max(len(label) * 8 + 30, min_w)
            h = 56 if elem.type in ("input", "form") else 40

        layout[eid] = {"x": x, "y": y, "w": w, "h": h, "depth": depth}

        if use_horizontal:
            row_max_h = max(row_max_h, h)
            x += w + inner_pad
            max_w = x - start_x - inner_pad
        else:
            y += h + inner_pad
            max_w = max(max_w, w)
            total_h = y - start_y

    if use_horizontal:
        total_h = row_max_h + inner_pad
        # Equalize heights for horizontal siblings
        for eid in element_ids:
            if eid in layout:
                layout[eid]["h"] = max(layout[eid]["h"], row_max_h)
    else:
        # Equalize widths for vertical siblings
        for eid in element_ids:
            if eid in layout:
                layout[eid]["w"] = max(layout[eid]["w"], max_w)

    return max_w, total_h


# ── Table renderer ─────────────────────────────────────────────────

def _render_table(spec: DiagramSpec, theme: Theme) -> str:
    """Render table: header row + data rows in a grid."""
    if not spec.elements:
        return _render_fallback(spec, theme)

    headers = [e for e in spec.elements if e.type == "header"]
    rows = [e for e in spec.elements if e.type == "row"]

    if not headers and not rows:
        return _render_fallback(spec, theme)

    # Determine columns from header or first row
    header_cells: list[str] = []
    if headers:
        header_cells = headers[0].properties.get("cells", [])

    data_rows: list[list[str]] = []
    for r in rows:
        data_rows.append(r.properties.get("cells", []))

    num_cols = max(
        len(header_cells),
        max((len(r) for r in data_rows), default=0),
    )
    if num_cols == 0:
        return _render_fallback(spec, theme)

    # Measure column widths
    col_widths: list[float] = []
    for ci in range(num_cols):
        max_len = 0
        if ci < len(header_cells):
            max_len = max(max_len, len(header_cells[ci]))
        for dr in data_rows:
            if ci < len(dr):
                max_len = max(max_len, len(dr[ci]))
        col_widths.append(max(max_len * 8.4 + 20, 60))

    row_h = 30
    num_rows = (1 if header_cells else 0) + len(data_rows)
    table_w = sum(col_widths)
    table_h = num_rows * row_h
    svg_w = table_w + PAD * 2
    svg_h = table_h + PAD * 2

    parts = [
        _svg_open(svg_w, svg_h),
        theme.svg_css(),
        theme.table_css(),
        _svg_bg(svg_w, svg_h),
    ]

    # Table border
    parts.append(
        f'  <rect class="table-border" x="{PAD}" y="{PAD}" '
        f'width="{table_w:.1f}" height="{table_h:.1f}"/>'
    )

    row_i = 0

    # Header row
    if header_cells:
        ry = PAD + row_i * row_h
        parts.append(
            f'  <rect class="table-header-bg" x="{PAD}" y="{ry:.1f}" '
            f'width="{table_w:.1f}" height="{row_h}"/>'
        )
        cx = PAD
        for ci, cell in enumerate(header_cells):
            cw = col_widths[ci] if ci < len(col_widths) else 60
            escaped = html_mod.escape(cell)
            parts.append(
                f'  <text class="table-header-text" x="{cx + cw / 2:.1f}" '
                f'y="{ry + row_h / 2:.1f}" text-anchor="middle" '
                f'dominant-baseline="central">{escaped}</text>'
            )
            cx += cw
        # Header separator
        sep_y = ry + row_h
        parts.append(
            f'  <line class="table-border" x1="{PAD}" y1="{sep_y:.1f}" '
            f'x2="{PAD + table_w:.1f}" y2="{sep_y:.1f}"/>'
        )
        row_i += 1

    # Data rows
    for dr in data_rows:
        ry = PAD + row_i * row_h
        cx = PAD
        for ci, cell in enumerate(dr):
            cw = col_widths[ci] if ci < len(col_widths) else 60
            escaped = html_mod.escape(cell)
            parts.append(
                f'  <text class="table-cell-text" x="{cx + cw / 2:.1f}" '
                f'y="{ry + row_h / 2:.1f}" text-anchor="middle" '
                f'dominant-baseline="central">{escaped}</text>'
            )
            cx += cw
        row_i += 1

    # Column separators
    cx = PAD
    for ci in range(num_cols - 1):
        cx += col_widths[ci]
        parts.append(
            f'  <line class="table-border" x1="{cx:.1f}" y1="{PAD}" '
            f'x2="{cx:.1f}" y2="{PAD + table_h:.1f}"/>'
        )

    # Row separators (skip header — already drawn)
    for ri in range(1 if header_cells else 0, num_rows):
        ry = PAD + ri * row_h
        parts.append(
            f'  <line class="table-border" x1="{PAD}" y1="{ry:.1f}" '
            f'x2="{PAD + table_w:.1f}" y2="{ry:.1f}"/>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


# ── Box renderer ───────────────────────────────────────────────────

def _render_box(spec: DiagramSpec, theme: Theme) -> str:
    """Render box diagram: standalone boxes with optional sections."""
    if not spec.elements:
        return _render_fallback(spec, theme)

    MAX_ROW_W = 800  # wrap to next row if exceeding this width

    nodes: list[dict] = []
    x, y = PAD, PAD
    gap = 20
    horizontal = spec.layout in ("horizontal", "auto")
    row_max_h = 0.0  # tallest box in current row

    for elem in spec.elements:
        label = elem.label or elem.id
        sections = elem.properties.get("sections", [])

        # Width based on widest content (wider char estimate for special chars)
        max_text_len = len(label)
        for sec in sections:
            for line in sec:
                max_text_len = max(max_text_len, len(line))
        w = max(max_text_len * 9.0 + 32, 100)

        # Height: 32px header area + per-section (12px overhead + lines*16px) + bottom pad
        section_h = sum(12 + len(sec) * 16 for sec in sections)
        h = max(32 + section_h + 8, BOX_H)

        # Row wrapping for horizontal layout
        if horizontal and nodes and x + w + PAD > MAX_ROW_W:
            x = PAD
            y += row_max_h + gap
            row_max_h = 0.0

        nodes.append({
            "x": x, "y": y, "w": w, "h": h,
            "label": label, "sections": sections,
        })

        if horizontal:
            row_max_h = max(row_max_h, h)
            x += w + gap
        else:
            y += h + gap

    max_x = max(n["x"] + n["w"] for n in nodes)
    max_y = max(n["y"] + n["h"] for n in nodes)

    # Build connection data for layered rendering
    id_to_node = {}
    for i, elem in enumerate(spec.elements):
        if i < len(nodes):
            id_to_node[elem.id] = nodes[i]

    # Check if any connections need routing below boxes (extra height)
    has_routed = _box_has_routed_connections(spec, id_to_node, nodes)
    if has_routed:
        max_y += 40

    svg_w = max_x + PAD
    svg_h = max_y + PAD

    parts = [
        _svg_open(svg_w, svg_h),
        theme.svg_css(),
        _svg_bg(svg_w, svg_h),
    ]

    # ClipPath and arrowhead defs
    defs = ['  <defs>']
    for i, n in enumerate(nodes):
        defs.append(
            f'    <clipPath id="box-clip-{i}"><rect x="{n["x"]:.1f}" y="{n["y"]:.1f}" '
            f'width="{n["w"]:.1f}" height="{n["h"]:.1f}" rx="{BOX_RX}"/></clipPath>'
        )
    defs.append('  </defs>')
    parts.extend(defs)

    # Layer 1: connection lines (underneath boxes)
    conn_labels: list[str] = []
    if spec.connections:
        parts.append(_svg_arrowhead_defs())
        for conn in spec.connections:
            src = id_to_node.get(conn.from_id)
            dst = id_to_node.get(conn.to_id)
            if src and dst:
                line_parts, label_parts = _svg_box_connection_layered(
                    src, dst, conn, nodes
                )
                parts.extend(line_parts)
                conn_labels.extend(label_parts)

    # Layer 2: box fills + borders + clipped text (on top of arrows)
    for i, n in enumerate(nodes):
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]

        # Opaque fill rect
        parts.append(
            f'  <rect class="box-fill" x="{x:.1f}" y="{y:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" rx="{BOX_RX}"/>'
        )

        # Box border
        parts.append(
            f'  <rect class="box-border" x="{x:.1f}" y="{y:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" rx="{BOX_RX}"/>'
        )

        # Clipped group for all text content
        parts.append(f'  <g clip-path="url(#box-clip-{i})">')

        # Header text
        header_y = y + 20
        escaped = html_mod.escape(n["label"])
        parts.append(
            f'    <text class="box-header" x="{x + w / 2:.1f}" y="{header_y:.1f}" '
            f'text-anchor="middle" dominant-baseline="central">{escaped}</text>'
        )

        # Sections
        sec_y = y + 32
        for sec in n["sections"]:
            # Separator line before section
            parts.append(
                f'    <line class="box-separator" x1="{x:.1f}" y1="{sec_y:.1f}" '
                f'x2="{x + w:.1f}" y2="{sec_y:.1f}"/>'
            )
            sec_y += 6
            for line in sec:
                sec_y += 16
                escaped = html_mod.escape(line)
                parts.append(
                    f'    <text class="box-text" x="{x + 12:.1f}" y="{sec_y:.1f}">{escaped}</text>'
                )
            sec_y += 6

        parts.append('  </g>')

    # Layer 3: connection labels (on top of boxes)
    parts.extend(conn_labels)

    parts.append("</svg>")
    return "\n".join(parts)


# ── Shared SVG helpers ─────────────────────────────────────────────

# ── State machine renderer ─────────────────────────────────────────

def _render_state_machine(spec: DiagramSpec, theme: Theme) -> str:
    """Render state machine: states with transitions, supports self-loops and back-edges."""
    elements = spec.elements
    connections = spec.connections
    if not elements:
        return _render_fallback(spec, theme)

    # Layout states in a grid pattern (better for cycles than linear)
    nodes = _layout_state_nodes(elements)
    id_to_node = {n["id"]: n for n in nodes}

    # Pre-compute back-edge curve bounds to size SVG correctly
    min_curve_x = PAD  # track leftmost curve control point
    max_curve_y = 0.0
    for conn in connections:
        src = id_to_node.get(conn.from_id)
        dst = id_to_node.get(conn.to_id)
        if not src or not dst or conn.from_id == conn.to_id:
            continue
        dst_cy = dst["y"] + dst["h"] / 2
        src_cy = src["y"] + src["h"] / 2
        goes_up = dst_cy < src_cy - 20
        same_row_left = (
            abs(dst_cy - src_cy) < src["h"]
            and dst["x"] + dst["w"] < src["x"]
        )
        if goes_up or same_row_left:
            # Compute curve control points (mirrors _svg_curved_connection_layered)
            sx, sy, sw, sh = src["x"], src["y"], src["w"], src["h"]
            dx, dy = dst["x"], dst["y"]
            if abs(sy - dy) < sh:
                ctrl_y = max(sy + sh, dy + dst["h"]) + 50
                max_curve_y = max(max_curve_y, ctrl_y)
            else:
                src_cx = sx + sw / 2
                dst_cx = dx + dst["w"] / 2
                dist = abs(src_cx - dst_cx) + abs(sy - dy)
                offset = max(80, dist * 0.3)
                ctrl_x = min(sx, dx) - offset
                min_curve_x = min(min_curve_x, ctrl_x)

    # Shift nodes right if curves extend past left edge
    x_shift = 0.0
    if min_curve_x < PAD:
        x_shift = PAD - min_curve_x + 20  # extra margin for labels
        for n in nodes:
            n["x"] += x_shift

    # Extra space for self-loop arcs above nodes and curves
    max_x = max(n["x"] + n["w"] for n in nodes) + 40
    max_y = max(
        max(n["y"] + n["h"] for n in nodes) + 40,
        max_curve_y + 30 if max_curve_y > 0 else 0,
    )
    svg_w = max_x + PAD
    svg_h = max_y + PAD

    d = theme.dark
    parts = [
        _svg_open(svg_w, svg_h),
        theme.svg_css(),
        _svg_arrowhead_defs(),
        f"""  <style>
    .mdview-diagram .state-node {{ stroke: {d.border}; stroke-width: 2; fill: {d.bg_secondary}; rx: 20; }}
    .mdview-diagram .state-initial {{ stroke: {d.heading}; stroke-width: 2.5; }}
    .mdview-diagram .state-text {{ fill: {d.header_text}; font-weight: 600; }}
    @media (prefers-color-scheme: light) {{
      .mdview-diagram .state-node {{ stroke: {theme.light.border}; fill: {theme.light.bg_secondary}; }}
      .mdview-diagram .state-initial {{ stroke: {theme.light.heading}; }}
      .mdview-diagram .state-text {{ fill: {theme.light.header_text}; }}
    }}
  </style>""",
        _svg_bg(svg_w, svg_h),
    ]

    # Layer 1: transition lines (underneath)
    conn_labels: list[str] = []
    for conn in connections:
        src = id_to_node.get(conn.from_id)
        dst = id_to_node.get(conn.to_id)
        if not src or not dst:
            continue

        if conn.from_id == conn.to_id:
            line_parts, label_parts = _svg_self_loop_layered(src, conn)
        else:
            # Back-edge detection: goes upward OR goes leftward on the same row
            # Grid wrapping (left + down) is a forward edge, NOT a back-edge
            dst_cy = dst["y"] + dst["h"] / 2
            src_cy = src["y"] + src["h"] / 2
            goes_up = dst_cy < src_cy - 20
            same_row_left = (
                abs(dst_cy - src_cy) < src["h"]
                and dst["x"] + dst["w"] < src["x"]
            )
            is_back_edge = goes_up or same_row_left

            if is_back_edge:
                line_parts, label_parts = _svg_curved_connection_layered(src, dst, conn)
            else:
                line_parts, label_parts = _svg_connection_layered(src, dst, conn)
        parts.extend(line_parts)
        conn_labels.extend(label_parts)

    # Layer 2: state shapes (on top of arrows)
    for n in nodes:
        is_initial = n.get("elem_type") in ("initial", "start")
        css = "state-node state-initial" if is_initial else "state-node"
        parts.append(
            f'  <rect class="{css}" x="{n["x"]:.1f}" y="{n["y"]:.1f}" '
            f'width="{n["w"]:.1f}" height="{n["h"]:.1f}" rx="20"/>'
        )

    # Layer 3: transition labels (on top of shapes)
    parts.extend(conn_labels)

    # Layer 4: state text (topmost)
    for n in nodes:
        cx = n["x"] + n["w"] / 2
        cy = n["y"] + n["h"] / 2
        escaped = html_mod.escape(n["label"])
        parts.append(
            f'  <text class="state-text" x="{cx:.1f}" y="{cy:.1f}" '
            f'text-anchor="middle" dominant-baseline="central">{escaped}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


def _layout_state_nodes(elements: list[Element]) -> list[dict]:
    """Position state machine nodes in a grid layout.

    Uses a 2D grid: fills rows left-to-right, wraps to fit ~800px max width.
    Consistent column widths so arrows align cleanly.
    """
    MAX_W = 800
    gap_x, gap_y = 60, 80

    # First pass: measure all nodes to find uniform width
    raw_widths = []
    for elem in elements:
        label = elem.label or elem.id
        raw_widths.append(max(len(label) * 9.5 + 40, 100))
    uniform_w = max(raw_widths) if raw_widths else 120
    h = BOX_H + 4

    # Cell size (uniform for grid alignment)
    cell_w = uniform_w + gap_x

    # Determine cols_per_row: fit within MAX_W
    cols_per_row = max(1, int((MAX_W - 2 * PAD + gap_x) / cell_w))
    cols_per_row = min(cols_per_row, len(elements))

    nodes = []
    for i, elem in enumerate(elements):
        label = elem.label or elem.id
        col = i % cols_per_row
        row = i // cols_per_row

        # Center node within its grid cell
        x = PAD + col * cell_w + (cell_w - uniform_w) / 2
        y = PAD + 30 + row * (h + gap_y)

        nodes.append({
            "id": elem.id,
            "label": label,
            "elem_type": elem.type,
            "x": x, "y": y,
            "w": uniform_w, "h": h,
        })

    return nodes


def _svg_self_loop_layered(
    node: dict, conn: Connection
) -> tuple[list[str], list[str]]:
    """Render a self-loop arc above a node. Returns (lines, labels)."""
    lines: list[str] = []
    labels: list[str] = []
    cx = node["x"] + node["w"] / 2
    top_y = node["y"]

    x1 = cx - 15
    x2 = cx + 15
    arc_top = top_y - 30

    dash = ' stroke-dasharray="6,3"' if conn.style == "dashed" else ""
    lines.append(
        f'  <path class="arrow-line" d="M {x1:.1f},{top_y:.1f} '
        f'C {x1:.1f},{arc_top:.1f} {x2:.1f},{arc_top:.1f} {x2:.1f},{top_y:.1f}" '
        f'marker-end="url(#arrowhead)"{dash}/>'
    )

    if conn.label:
        label_x = cx
        label_y = arc_top - 4
        escaped = html_mod.escape(conn.label)
        label_w = len(conn.label) * 7.2 + 8
        labels.append(
            f'  <rect class="arrow-label-bg" x="{label_x - label_w / 2:.1f}" '
            f'y="{label_y - 8:.1f}" width="{label_w:.1f}" height="16" rx="3"/>'
        )
        labels.append(
            f'  <text class="arrow-label" x="{label_x:.1f}" y="{label_y:.1f}" '
            f'dominant-baseline="central">{escaped}</text>'
        )

    return lines, labels


def _svg_curved_connection_layered(
    src: dict, dst: dict, conn: Connection
) -> tuple[list[str], list[str]]:
    """Render a back-edge as a curved path. Returns (lines, labels)."""
    lines: list[str] = []
    labels: list[str] = []

    sx, sy, sw, sh = src["x"], src["y"], src["w"], src["h"]
    dx, dy, dw, dh = dst["x"], dst["y"], dst["w"], dst["h"]

    src_cx = sx + sw / 2
    dst_cx = dx + dw / 2

    # Route below for same-row back-edges, wide curve for multi-row
    if abs(sy - dy) < sh:
        x1, y1 = src_cx, sy + sh
        x2, y2 = dst_cx, dy + dh
        ctrl_y = max(y1, y2) + 50
        ctrl_x1 = x1
        ctrl_x2 = x2
    else:
        # Different rows: curve wide to the left to avoid overlapping content
        x1, y1 = sx, sy + sh / 2
        x2, y2 = dx, dy + dh / 2
        ctrl_y = (y1 + y2) / 2
        # Wider offset proportional to distance between nodes
        dist = abs(src_cx - dst_cx) + abs(sy - dy)
        offset = max(80, dist * 0.3)
        ctrl_x1 = min(x1, x2) - offset
        ctrl_x2 = ctrl_x1

    dash = ' stroke-dasharray="6,3"' if conn.style == "dashed" else ""
    lines.append(
        f'  <path class="arrow-line" d="M {x1:.1f},{y1:.1f} '
        f'C {ctrl_x1:.1f},{ctrl_y:.1f} {ctrl_x2:.1f},{ctrl_y:.1f} {x2:.1f},{y2:.1f}" '
        f'marker-end="url(#arrowhead)"{dash}/>'
    )

    if conn.label:
        mid_x = (ctrl_x1 + ctrl_x2) / 2
        mid_y = ctrl_y
        escaped = html_mod.escape(conn.label)
        label_w = len(conn.label) * 7.2 + 8
        labels.append(
            f'  <rect class="arrow-label-bg" x="{mid_x - label_w / 2:.1f}" '
            f'y="{mid_y - 9:.1f}" width="{label_w:.1f}" height="16" rx="3"/>'
        )
        labels.append(
            f'  <text class="arrow-label" x="{mid_x:.1f}" y="{mid_y:.1f}" '
            f'dominant-baseline="central">{escaped}</text>'
        )

    return lines, labels


def _svg_open(w: float, h: float) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w:.0f}" height="{h:.0f}" '
        f'style="display:block;margin:auto" '
        f'class="mdview-diagram">'
    )


def _svg_bg(w: float, h: float) -> str:
    return f'  <rect class="bg" x="0" y="0" width="{w:.0f}" height="{h:.0f}" rx="6"/>'


def _svg_arrowhead_defs() -> str:
    return """  <defs>
    <marker id="arrowhead" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>"""


def _svg_seq_arrowhead_defs() -> str:
    return """  <defs>
    <marker id="seq-arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="msg-head"/>
    </marker>
  </defs>"""


def _box_has_routed_connections(
    spec: DiagramSpec, id_to_node: dict, nodes: list[dict]
) -> bool:
    """Check if any box connections need routing around intermediate boxes."""
    if not spec.connections:
        return False
    for conn in spec.connections:
        src = id_to_node.get(conn.from_id)
        dst = id_to_node.get(conn.to_id)
        if not src or not dst:
            continue
        _, y1, _, y2 = _compute_connection_endpoints(src, dst)
        min_cx = min(src["x"] + src["w"], dst["x"] + dst["w"])
        max_cx = max(src["x"], dst["x"])
        for n in nodes:
            if n is src or n is dst:
                continue
            if n["x"] < max_cx and n["x"] + n["w"] > min_cx:
                arrow_y_min = min(y1, y2) - 10
                arrow_y_max = max(y1, y2) + 10
                if n["y"] < arrow_y_max and n["y"] + n["h"] > arrow_y_min:
                    return True
    return False


def _svg_diamond_fill(x: float, y: float, w: float, h: float) -> str:
    """Render opaque fill for a diamond decision node."""
    cx, cy = x + w / 2, y + h / 2
    hw, hh = w / 2, h / 2
    points = f"{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}"
    return f'  <polygon class="box-fill" points="{points}"/>'


def _svg_diamond(x: float, y: float, w: float, h: float) -> str:
    """Render a diamond shape for decision nodes."""
    cx, cy = x + w / 2, y + h / 2
    hw, hh = w / 2, h / 2
    points = f"{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}"
    return f'  <polygon class="box-border" points="{points}"/>'


def _compute_connection_endpoints(
    src: dict, dst: dict
) -> tuple[float, float, float, float]:
    """Compute arrow start/end points between two nodes."""
    sx, sy, sw, sh = src["x"], src["y"], src["w"], src["h"]
    dx, dy, dw, dh = dst["x"], dst["y"], dst["w"], dst["h"]

    src_cx, src_cy = sx + sw / 2, sy + sh / 2
    dst_cx, dst_cy = dx + dw / 2, dy + dh / 2

    if abs(dst_cx - src_cx) > abs(dst_cy - src_cy):
        if dst_cx > src_cx:
            x1, y1 = sx + sw, src_cy
            x2, y2 = dx, dst_cy
        else:
            x1, y1 = sx, src_cy
            x2, y2 = dx + dw, dst_cy
    else:
        if dst_cy > src_cy:
            x1, y1 = src_cx, sy + sh
            x2, y2 = dst_cx, dy
        else:
            x1, y1 = src_cx, sy
            x2, y2 = dst_cx, dy + dh

    return x1, y1, x2, y2


def _svg_connection_layered(
    src: dict, dst: dict, conn: Connection
) -> tuple[list[str], list[str]]:
    """Draw arrow between nodes. Returns (line_parts, label_parts) for z-ordering."""
    lines: list[str] = []
    labels: list[str] = []

    x1, y1, x2, y2 = _compute_connection_endpoints(src, dst)

    dash = ' stroke-dasharray="6,3"' if conn.style == "dashed" else ""
    marker = ' marker-end="url(#arrowhead)"'

    lines.append(
        f'  <line class="arrow-line" x1="{x1:.1f}" y1="{y1:.1f}" '
        f'x2="{x2:.1f}" y2="{y2:.1f}"{dash}{marker}/>'
    )

    if conn.label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        escaped = html_mod.escape(conn.label)
        label_w = len(conn.label) * 7.2 + 8
        label_h = 16
        labels.append(
            f'  <rect class="arrow-label-bg" x="{mid_x - label_w / 2:.1f}" '
            f'y="{mid_y - label_h / 2 - 1:.1f}" '
            f'width="{label_w:.1f}" height="{label_h:.1f}" rx="3"/>'
        )
        labels.append(
            f'  <text class="arrow-label" x="{mid_x:.1f}" y="{mid_y:.1f}" '
            f'dominant-baseline="central">{escaped}</text>'
        )

    return lines, labels


def _svg_box_connection_layered(
    src: dict, dst: dict, conn: Connection, all_nodes: list[dict]
) -> tuple[list[str], list[str]]:
    """Draw arrow between box nodes, routing below if intermediate boxes exist."""
    lines: list[str] = []
    labels: list[str] = []

    x1, y1, x2, y2 = _compute_connection_endpoints(src, dst)

    # Check if any intermediate box sits between src and dst horizontally
    min_x = min(src["x"] + src["w"], dst["x"] + dst["w"])
    max_x = max(src["x"], dst["x"])
    has_blocker = False
    for n in all_nodes:
        if n is src or n is dst:
            continue
        # Box overlaps the horizontal span between src and dst
        if n["x"] < max_x and n["x"] + n["w"] > min_x:
            # And vertically overlaps the arrow path
            arrow_y_min = min(y1, y2) - 10
            arrow_y_max = max(y1, y2) + 10
            if n["y"] < arrow_y_max and n["y"] + n["h"] > arrow_y_min:
                has_blocker = True
                break

    dash = ' stroke-dasharray="6,3"' if conn.style == "dashed" else ""
    marker = ' marker-end="url(#arrowhead)"'

    if has_blocker:
        # Route below all boxes
        bottom_y = max(n["y"] + n["h"] for n in all_nodes) + 20
        # Start from bottom of src, end at bottom of dst, curve below
        sx = src["x"] + src["w"] / 2
        sy = src["y"] + src["h"]
        dx = dst["x"] + dst["w"] / 2
        dy = dst["y"] + dst["h"]
        lines.append(
            f'  <path class="arrow-line" d="M {sx:.1f},{sy:.1f} '
            f'L {sx:.1f},{bottom_y:.1f} L {dx:.1f},{bottom_y:.1f} '
            f'L {dx:.1f},{dy:.1f}" '
            f'{marker}{dash}/>'
        )
        if conn.label:
            mid_x = (sx + dx) / 2
            mid_y = bottom_y
            escaped = html_mod.escape(conn.label)
            label_w = len(conn.label) * 7.2 + 8
            labels.append(
                f'  <rect class="arrow-label-bg" x="{mid_x - label_w / 2:.1f}" '
                f'y="{mid_y - 9:.1f}" width="{label_w:.1f}" height="16" rx="3"/>'
            )
            labels.append(
                f'  <text class="arrow-label" x="{mid_x:.1f}" y="{mid_y:.1f}" '
                f'dominant-baseline="central">{escaped}</text>'
            )
    else:
        # Direct arrow (no blockers)
        lines.append(
            f'  <line class="arrow-line" x1="{x1:.1f}" y1="{y1:.1f}" '
            f'x2="{x2:.1f}" y2="{y2:.1f}"{dash}{marker}/>'
        )
        if conn.label:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            escaped = html_mod.escape(conn.label)
            label_w = len(conn.label) * 7.2 + 8
            labels.append(
                f'  <rect class="arrow-label-bg" x="{mid_x - label_w / 2:.1f}" '
                f'y="{mid_y - 9:.1f}" width="{label_w:.1f}" height="16" rx="3"/>'
            )
            labels.append(
                f'  <text class="arrow-label" x="{mid_x:.1f}" y="{mid_y:.1f}" '
                f'dominant-baseline="central">{escaped}</text>'
            )

    return lines, labels


def _render_fallback(spec: DiagramSpec, theme: Theme) -> str:
    """Minimal fallback: render spec info as text."""
    lines = [f"[{spec.type}]"]
    if spec.title:
        lines.append(spec.title)
    for e in spec.elements:
        lines.append(f"  {e.label or e.id} ({e.type})")
    for c in spec.connections:
        arrow = f"{c.from_id} -> {c.to_id}"
        if c.label:
            arrow += f" [{c.label}]"
        lines.append(f"  {arrow}")

    w = max((len(l) for l in lines), default=20) * 8.4 + PAD * 2
    h = len(lines) * 16 + PAD * 2

    return "\n".join([
        _svg_open(w, h),
        theme.svg_css(),
        _svg_bg(w, h),
        *(
            f'  <text class="box-text" x="{PAD}" y="{PAD + i * 16 + 12:.1f}">'
            f'{html_mod.escape(line)}</text>'
            for i, line in enumerate(lines)
        ),
        "</svg>",
    ])


# ── Renderer dispatch ──────────────────────────────────────────────

_RENDERERS = {
    "flow": _render_flow,
    "sequence": _render_sequence,
    "wireframe": _render_wireframe,
    "table": _render_table,
    "box": _render_box,
    "state_machine": _render_state_machine,
}
