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

    # Draw nodes
    for n in nodes:
        is_decision = n.get("elem_type") == "decision"
        if is_decision:
            parts.append(_svg_diamond(n["x"], n["y"], n["w"], n["h"]))
        else:
            parts.append(
                f'  <rect class="box-border" x="{n["x"]:.1f}" y="{n["y"]:.1f}" '
                f'width="{n["w"]:.1f}" height="{n["h"]:.1f}" rx="{BOX_RX}"/>'
            )
        cx = n["x"] + n["w"] / 2
        cy = n["y"] + n["h"] / 2
        escaped = html_mod.escape(n["label"])
        css = "box-header" if n.get("is_first") else "box-text"
        parts.append(
            f'  <text class="{css}" x="{cx:.1f}" y="{cy:.1f}" '
            f'text-anchor="middle" dominant-baseline="central">{escaped}</text>'
        )

    # Draw connections
    for conn in connections:
        src = id_to_node.get(conn.from_id)
        dst = id_to_node.get(conn.to_id)
        if not src or not dst:
            continue
        parts.extend(_svg_connection(src, dst, conn))

    parts.append("</svg>")
    return "\n".join(parts)


def _layout_flow_nodes(
    elements: list[Element], horizontal: bool
) -> list[dict]:
    """Position flow nodes. Returns list of {id, label, x, y, w, h, elem_type}."""
    nodes = []
    x, y = PAD, PAD
    gap = 60

    for i, elem in enumerate(elements):
        label = elem.label or elem.id
        w = max(len(label) * 9.5 + 30, 80)
        h = BOX_H

        nodes.append({
            "id": elem.id,
            "label": label,
            "elem_type": elem.type,
            "x": x, "y": y,
            "w": w, "h": h,
            "is_first": i == 0,
        })

        if horizontal:
            x += w + gap
        else:
            y += h + gap

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

    # Layout
    side_pad = 40
    actor_y = PAD
    lane_xs = [side_pad + ACTOR_BOX_W / 2 + i * LANE_SPACING for i in range(num_actors)]
    svg_w = side_pad * 2 + (num_actors - 1) * LANE_SPACING + ACTOR_BOX_W

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
        x = lane_xs[i] - ACTOR_BOX_W / 2
        label = html_mod.escape(actor.label or actor.id)
        for ay in (actor_y, bottom_actor_y):
            parts.append(
                f'  <rect class="actor-box" x="{x:.1f}" y="{ay}" '
                f'width="{ACTOR_BOX_W}" height="{ACTOR_BOX_H}" rx="4"/>'
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
    x = start_x
    y = start_y
    max_w = 0.0
    total_h = 0.0
    inner_pad = 8
    title_h = 28

    for eid in element_ids:
        elem = id_to_elem.get(eid)
        if not elem:
            continue

        kids = children_of.get(eid, [])
        label = elem.label or eid

        if kids:
            # Container panel — layout children inside
            child_x = x + inner_pad
            child_y = y + title_h
            child_w, child_h = _layout_wireframe(
                kids, id_to_elem, children_of, layout,
                child_x, child_y, depth + 1,
            )
            w = max(child_w + inner_pad * 2, len(label) * 8 + 30, 120)
            h = child_h + title_h + inner_pad
        else:
            # Leaf element
            w = max(len(label) * 8 + 30, 120)
            h = 56 if elem.type in ("input", "form") else 36

        layout[eid] = {"x": x, "y": y, "w": w, "h": h, "depth": depth}
        y += h + inner_pad
        max_w = max(max_w, w)
        total_h = y - start_y

    # Equalize widths for siblings
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

    nodes: list[dict] = []
    x, y = PAD, PAD
    gap = 20
    horizontal = spec.layout in ("horizontal", "auto")

    for elem in spec.elements:
        label = elem.label or elem.id
        sections = elem.properties.get("sections", [])

        # Width based on widest content
        max_text_len = len(label)
        for sec in sections:
            for line in sec:
                max_text_len = max(max_text_len, len(line))
        w = max(max_text_len * 8.4 + 24, 100)

        # Height: header + sections
        section_lines = sum(len(sec) for sec in sections)
        content_rows = 1 + section_lines  # header + section lines
        h = max(content_rows * 22 + 16, BOX_H)

        nodes.append({
            "x": x, "y": y, "w": w, "h": h,
            "label": label, "sections": sections,
        })

        if horizontal:
            x += w + gap
        else:
            y += h + gap

    max_x = max(n["x"] + n["w"] for n in nodes)
    max_y = max(n["y"] + n["h"] for n in nodes)
    svg_w = max_x + PAD
    svg_h = max_y + PAD

    parts = [
        _svg_open(svg_w, svg_h),
        theme.svg_css(),
        _svg_bg(svg_w, svg_h),
    ]

    for n in nodes:
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]

        # Box border
        parts.append(
            f'  <rect class="box-border" x="{x:.1f}" y="{y:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" rx="{BOX_RX}"/>'
        )

        # Header text
        header_y = y + 20
        escaped = html_mod.escape(n["label"])
        parts.append(
            f'  <text class="box-header" x="{x + w / 2:.1f}" y="{header_y:.1f}" '
            f'text-anchor="middle" dominant-baseline="central">{escaped}</text>'
        )

        # Sections
        sec_y = y + 32
        for sec in n["sections"]:
            # Separator line before section
            parts.append(
                f'  <line class="box-separator" x1="{x:.1f}" y1="{sec_y:.1f}" '
                f'x2="{x + w:.1f}" y2="{sec_y:.1f}"/>'
            )
            sec_y += 6
            for line in sec:
                sec_y += 16
                escaped = html_mod.escape(line)
                parts.append(
                    f'  <text class="box-text" x="{x + 12:.1f}" y="{sec_y:.1f}">{escaped}</text>'
                )
            sec_y += 6

    # Draw connections if any
    if spec.connections:
        parts.append(_svg_arrowhead_defs())
        id_to_node = {}
        for i, elem in enumerate(spec.elements):
            if i < len(nodes):
                id_to_node[elem.id] = nodes[i]
        for conn in spec.connections:
            src = id_to_node.get(conn.from_id)
            dst = id_to_node.get(conn.to_id)
            if src and dst:
                parts.extend(_svg_connection(src, dst, conn))

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

    # Extra space for self-loop arcs above nodes
    max_x = max(n["x"] + n["w"] for n in nodes) + 40
    max_y = max(n["y"] + n["h"] for n in nodes) + 40
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

    # Draw states (rounded rectangles, more rounded than flow nodes)
    for n in nodes:
        is_initial = n.get("elem_type") in ("initial", "start")
        css = "state-node state-initial" if is_initial else "state-node"
        parts.append(
            f'  <rect class="{css}" x="{n["x"]:.1f}" y="{n["y"]:.1f}" '
            f'width="{n["w"]:.1f}" height="{n["h"]:.1f}" rx="20"/>'
        )
        cx = n["x"] + n["w"] / 2
        cy = n["y"] + n["h"] / 2
        escaped = html_mod.escape(n["label"])
        parts.append(
            f'  <text class="state-text" x="{cx:.1f}" y="{cy:.1f}" '
            f'text-anchor="middle" dominant-baseline="central">{escaped}</text>'
        )

    # Draw transitions — handle self-loops, back-edges, and forward edges
    for conn in connections:
        src = id_to_node.get(conn.from_id)
        dst = id_to_node.get(conn.to_id)
        if not src or not dst:
            continue

        if conn.from_id == conn.to_id:
            # Self-loop: arc above the node
            parts.extend(_svg_self_loop(src, conn))
        else:
            # Check if this is a back-edge (dst is left/above src)
            src_cx = src["x"] + src["w"] / 2
            dst_cx = dst["x"] + dst["w"] / 2
            src_cy = src["y"] + src["h"] / 2
            dst_cy = dst["y"] + dst["h"] / 2

            is_back_edge = (dst_cx < src_cx - 20) or (dst_cy < src_cy - 20)

            if is_back_edge:
                parts.extend(_svg_curved_connection(src, dst, conn))
            else:
                parts.extend(_svg_connection(src, dst, conn))

    parts.append("</svg>")
    return "\n".join(parts)


def _layout_state_nodes(elements: list[Element]) -> list[dict]:
    """Position state machine nodes in a grid layout.

    Uses a 2D grid: fills rows left-to-right, wraps after ~3 nodes.
    More natural for state machines than a single line.
    """
    nodes = []
    cols_per_row = min(max(len(elements), 2), 4)
    gap_x, gap_y = 80, 80

    for i, elem in enumerate(elements):
        label = elem.label or elem.id
        w = max(len(label) * 9.5 + 40, 100)
        h = BOX_H + 4  # slightly taller for rounded look

        col = i % cols_per_row
        row = i // cols_per_row

        x = PAD + col * (w + gap_x)
        y = PAD + 30 + row * (h + gap_y)  # +30 for self-loop space above

        nodes.append({
            "id": elem.id,
            "label": label,
            "elem_type": elem.type,
            "x": x, "y": y,
            "w": w, "h": h,
        })

    return nodes


def _svg_self_loop(node: dict, conn: Connection) -> list[str]:
    """Render a self-loop arc above a node."""
    parts: list[str] = []
    cx = node["x"] + node["w"] / 2
    top_y = node["y"]

    # Arc: start from top-left of node, go up, come back to top-right
    x1 = cx - 15
    x2 = cx + 15
    arc_top = top_y - 30

    dash = ' stroke-dasharray="6,3"' if conn.style == "dashed" else ""
    parts.append(
        f'  <path class="arrow-line" d="M {x1:.1f},{top_y:.1f} '
        f'C {x1:.1f},{arc_top:.1f} {x2:.1f},{arc_top:.1f} {x2:.1f},{top_y:.1f}" '
        f'marker-end="url(#arrowhead)"{dash}/>'
    )

    if conn.label:
        label_x = cx
        label_y = arc_top - 4
        escaped = html_mod.escape(conn.label)
        label_w = len(conn.label) * 7.2 + 8
        parts.append(
            f'  <rect class="arrow-label-bg" x="{label_x - label_w / 2:.1f}" '
            f'y="{label_y - 8:.1f}" width="{label_w:.1f}" height="16" rx="3"/>'
        )
        parts.append(
            f'  <text class="arrow-label" x="{label_x:.1f}" y="{label_y:.1f}" '
            f'dominant-baseline="central">{escaped}</text>'
        )

    return parts


def _svg_curved_connection(src: dict, dst: dict, conn: Connection) -> list[str]:
    """Render a back-edge as a curved path (avoids overlapping forward arrows)."""
    parts: list[str] = []

    sx, sy, sw, sh = src["x"], src["y"], src["w"], src["h"]
    dx, dy, dw, dh = dst["x"], dst["y"], dst["w"], dst["h"]

    src_cx = sx + sw / 2
    dst_cx = dx + dw / 2

    # Route below for same-row back-edges, above for multi-row
    if abs(sy - dy) < sh:
        # Same row: curve below
        x1, y1 = src_cx, sy + sh
        x2, y2 = dst_cx, dy + dh
        ctrl_y = max(y1, y2) + 50
        ctrl_x1 = x1
        ctrl_x2 = x2
    else:
        # Different rows: curve to the side
        if dst_cx < src_cx:
            x1, y1 = sx, sy + sh / 2
            x2, y2 = dx, dy + dh / 2
        else:
            x1, y1 = sx + sw, sy + sh / 2
            x2, y2 = dx + dw, dy + dh / 2
        ctrl_y = (y1 + y2) / 2
        offset = 60
        ctrl_x1 = min(x1, x2) - offset
        ctrl_x2 = ctrl_x1

    dash = ' stroke-dasharray="6,3"' if conn.style == "dashed" else ""
    parts.append(
        f'  <path class="arrow-line" d="M {x1:.1f},{y1:.1f} '
        f'C {ctrl_x1:.1f},{ctrl_y:.1f} {ctrl_x2:.1f},{ctrl_y:.1f} {x2:.1f},{y2:.1f}" '
        f'marker-end="url(#arrowhead)"{dash}/>'
    )

    if conn.label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2 + ctrl_y) / 3
        escaped = html_mod.escape(conn.label)
        label_w = len(conn.label) * 7.2 + 8
        parts.append(
            f'  <rect class="arrow-label-bg" x="{mid_x - label_w / 2:.1f}" '
            f'y="{mid_y - 9:.1f}" width="{label_w:.1f}" height="16" rx="3"/>'
        )
        parts.append(
            f'  <text class="arrow-label" x="{mid_x:.1f}" y="{mid_y:.1f}" '
            f'dominant-baseline="central">{escaped}</text>'
        )

    return parts


def _svg_open(w: float, h: float) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w:.0f}" height="{h:.0f}" '
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


def _svg_diamond(x: float, y: float, w: float, h: float) -> str:
    """Render a diamond shape for decision nodes."""
    cx, cy = x + w / 2, y + h / 2
    hw, hh = w / 2, h / 2
    points = f"{cx},{cy - hh} {cx + hw},{cy} {cx},{cy + hh} {cx - hw},{cy}"
    return f'  <polygon class="box-border" points="{points}"/>'


def _svg_connection(src: dict, dst: dict, conn: Connection) -> list[str]:
    """Draw an arrow between two positioned nodes."""
    parts: list[str] = []

    # Determine exit/entry sides
    sx, sy, sw, sh = src["x"], src["y"], src["w"], src["h"]
    dx, dy, dw, dh = dst["x"], dst["y"], dst["w"], dst["h"]

    src_cx, src_cy = sx + sw / 2, sy + sh / 2
    dst_cx, dst_cy = dx + dw / 2, dy + dh / 2

    # Pick edge midpoints based on relative position
    if abs(dst_cx - src_cx) > abs(dst_cy - src_cy):
        # Horizontal: exit right/left
        if dst_cx > src_cx:
            x1, y1 = sx + sw, src_cy
            x2, y2 = dx, dst_cy
        else:
            x1, y1 = sx, src_cy
            x2, y2 = dx + dw, dst_cy
    else:
        # Vertical: exit bottom/top
        if dst_cy > src_cy:
            x1, y1 = src_cx, sy + sh
            x2, y2 = dst_cx, dy
        else:
            x1, y1 = src_cx, sy
            x2, y2 = dst_cx, dy + dh

    dash = ' stroke-dasharray="6,3"' if conn.style == "dashed" else ""
    marker = ' marker-end="url(#arrowhead)"'

    parts.append(
        f'  <line class="arrow-line" x1="{x1:.1f}" y1="{y1:.1f}" '
        f'x2="{x2:.1f}" y2="{y2:.1f}"{dash}{marker}/>'
    )

    # Label
    if conn.label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        escaped = html_mod.escape(conn.label)
        label_w = len(conn.label) * 7.2 + 8
        label_h = 16
        parts.append(
            f'  <rect class="arrow-label-bg" x="{mid_x - label_w / 2:.1f}" '
            f'y="{mid_y - label_h / 2 - 1:.1f}" '
            f'width="{label_w:.1f}" height="{label_h:.1f}" rx="3"/>'
        )
        parts.append(
            f'  <text class="arrow-label" x="{mid_x:.1f}" y="{mid_y:.1f}" '
            f'dominant-baseline="central">{escaped}</text>'
        )

    return parts


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
