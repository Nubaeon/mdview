#!/usr/bin/env python3
"""Generate showcase.html from constructed DiagramSpecs.

Demonstrates spec-based rendering for all 6 diagram types:
flow, sequence, wireframe, table, box, state_machine.
"""

import html
from pathlib import Path
from mdview.spec import DiagramSpec, Element, Connection
from mdview.specrender import render_spec_svg

# ── Diagram specs ──────────────────────────────────────────────────

SPECS = [
    # 1. Flow diagram — CI/CD pipeline
    DiagramSpec(
        type="flow",
        title="CI/CD Pipeline",
        layout="horizontal",
        elements=[
            Element(id="push", label="Git Push", type="node"),
            Element(id="build", label="Build", type="node"),
            Element(id="test", label="Test", type="node"),
            Element(id="check", label="Pass?", type="decision"),
            Element(id="deploy", label="Deploy", type="node"),
        ],
        connections=[
            Connection(from_id="push", to_id="build", label="trigger"),
            Connection(from_id="build", to_id="test"),
            Connection(from_id="test", to_id="check"),
            Connection(from_id="check", to_id="deploy", label="yes"),
        ],
    ),

    # 2. Vertical flow — data pipeline
    DiagramSpec(
        type="flow",
        title="Data Pipeline",
        layout="vertical",
        elements=[
            Element(id="ingest", label="Ingest", type="node"),
            Element(id="validate", label="Validate", type="node"),
            Element(id="transform", label="Transform", type="node"),
            Element(id="load", label="Load to DW", type="node"),
        ],
        connections=[
            Connection(from_id="ingest", to_id="validate", label="raw"),
            Connection(from_id="validate", to_id="transform", label="clean"),
            Connection(from_id="transform", to_id="load", label="enriched"),
        ],
    ),

    # 3. Sequence diagram — auth flow
    DiagramSpec(
        type="sequence",
        title="Authentication Flow",
        layout="sequence",
        elements=[
            Element(id="browser", label="Browser", type="actor"),
            Element(id="api", label="API Server", type="actor"),
            Element(id="auth", label="Auth Service", type="actor"),
            Element(id="db", label="Database", type="actor"),
        ],
        connections=[
            Connection(from_id="browser", to_id="api", label="POST /login",
                       properties={"order": 1}),
            Connection(from_id="api", to_id="auth", label="validate(token)",
                       properties={"order": 2}),
            Connection(from_id="auth", to_id="db", label="SELECT user",
                       properties={"order": 3}),
            Connection(from_id="db", to_id="auth", label="user record",
                       properties={"order": 4}, style="dashed"),
            Connection(from_id="auth", to_id="api", label="JWT token",
                       properties={"order": 5}, style="dashed"),
            Connection(from_id="api", to_id="browser", label="200 OK + cookie",
                       properties={"order": 6}, style="dashed"),
        ],
    ),

    # 4. Wireframe — dashboard layout
    DiagramSpec(
        type="wireframe",
        title="Dashboard",
        layout="nested",
        elements=[
            Element(id="app", label="Dashboard", type="panel",
                    children=["sidebar", "main"]),
            Element(id="sidebar", label="Navigation", type="sidebar",
                    properties={"role": "sidebar"}),
            Element(id="main", label="Main Content", type="panel",
                    children=["search", "metrics", "chart"]),
            Element(id="search", label="Search", type="input",
                    properties={"value": "Search metrics..."}),
            Element(id="metrics", label="Key Metrics", type="panel"),
            Element(id="chart", label="Revenue Chart", type="panel"),
        ],
    ),

    # 5. Table — API endpoints
    DiagramSpec(
        type="table",
        title="API Endpoints",
        layout="grid",
        properties={"columns": 4},
        elements=[
            Element(id="h", label="", type="header",
                    properties={"cells": ["Method", "Path", "Auth", "Description"]}),
            Element(id="r1", label="", type="row",
                    properties={"cells": ["GET", "/api/users", "JWT", "List users"]}),
            Element(id="r2", label="", type="row",
                    properties={"cells": ["POST", "/api/users", "JWT", "Create user"]}),
            Element(id="r3", label="", type="row",
                    properties={"cells": ["GET", "/api/health", "None", "Health check"]}),
            Element(id="r4", label="", type="row",
                    properties={"cells": ["DELETE", "/api/users/:id", "Admin", "Delete user"]}),
        ],
    ),

    # 6. Box — class diagram
    DiagramSpec(
        type="box",
        title="Domain Model",
        layout="horizontal",
        elements=[
            Element(id="user", label="User", type="box",
                    properties={"sections": [
                        ["id: UUID", "email: String", "role: Role"],
                        ["authenticate()", "hasPermission(p)"],
                    ]}),
            Element(id="role", label="Role", type="box",
                    properties={"sections": [
                        ["name: String", "permissions: List"],
                        ["grant(p)", "revoke(p)"],
                    ]}),
        ],
        connections=[
            Connection(from_id="user", to_id="role", label="has"),
        ],
    ),

    # 7. State machine — order lifecycle
    DiagramSpec(
        type="state_machine",
        title="Order Lifecycle",
        elements=[
            Element(id="new", label="New", type="initial"),
            Element(id="pending", label="Pending Payment", type="node"),
            Element(id="paid", label="Paid", type="node"),
            Element(id="shipped", label="Shipped", type="node"),
            Element(id="delivered", label="Delivered", type="node"),
            Element(id="cancelled", label="Cancelled", type="node"),
        ],
        connections=[
            Connection(from_id="new", to_id="pending", label="checkout"),
            Connection(from_id="pending", to_id="paid", label="pay"),
            Connection(from_id="pending", to_id="cancelled", label="timeout"),
            Connection(from_id="paid", to_id="shipped", label="ship"),
            Connection(from_id="shipped", to_id="delivered", label="deliver"),
            Connection(from_id="paid", to_id="cancelled", label="refund"),
            # Back-edge
            Connection(from_id="cancelled", to_id="new", label="retry", style="dashed"),
        ],
    ),

    # 8. State machine with self-loop
    DiagramSpec(
        type="state_machine",
        title="Connection State",
        elements=[
            Element(id="idle", label="Idle", type="initial"),
            Element(id="connecting", label="Connecting", type="node"),
            Element(id="connected", label="Connected", type="node"),
            Element(id="error", label="Error", type="node"),
        ],
        connections=[
            Connection(from_id="idle", to_id="connecting", label="connect()"),
            Connection(from_id="connecting", to_id="connected", label="success"),
            Connection(from_id="connecting", to_id="error", label="fail"),
            Connection(from_id="error", to_id="connecting", label="retry"),
            Connection(from_id="connected", to_id="idle", label="disconnect"),
            # Self-loop
            Connection(from_id="connected", to_id="connected", label="heartbeat"),
        ],
    ),
]


def generate_showcase() -> str:
    """Generate showcase HTML with all spec-rendered diagrams."""
    sections: list[str] = []

    for spec in SPECS:
        svg = render_spec_svg(spec)
        title = spec.title or f"{spec.type} diagram"
        sections.append(f"""
    <section>
      <h2>{html.escape(title)}</h2>
      <p class="meta">Type: {spec.type} | Layout: {spec.layout} |
         Elements: {len(spec.elements)} | Connections: {len(spec.connections)}</p>
      <div class="diagram">{svg}</div>
    </section>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>mdview Spec Rendering Showcase</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: #1a1b26; color: #a9b1d6;
      font-family: -apple-system, system-ui, sans-serif;
      padding: 40px 20px;
    }}
    h1 {{ color: #7aa2f7; text-align: center; margin-bottom: 10px; font-size: 28px; }}
    .subtitle {{ text-align: center; color: #565f89; margin-bottom: 40px; }}
    section {{
      max-width: 900px; margin: 0 auto 40px;
      background: #24283b; border-radius: 12px; padding: 24px;
      border: 1px solid #3b4261;
    }}
    h2 {{ color: #9ece6a; font-size: 18px; margin-bottom: 8px; }}
    .meta {{ color: #565f89; font-size: 12px; margin-bottom: 16px; }}
    .diagram {{
      overflow-x: auto; padding: 8px;
      background: #1a1b26; border-radius: 8px;
    }}
    .diagram svg {{ display: block; margin: 0 auto; }}
    @media (prefers-color-scheme: light) {{
      body {{ background: #f8f8fc; color: #343b58; }}
      h1 {{ color: #2e7de9; }}
      .subtitle {{ color: #9ca0b0; }}
      section {{ background: #e8e8f0; border-color: #c8c8d0; }}
      h2 {{ color: #587539; }}
      .meta {{ color: #9ca0b0; }}
      .diagram {{ background: #f8f8fc; }}
    }}
  </style>
</head>
<body>
  <h1>mdview Spec Rendering Showcase</h1>
  <p class="subtitle">All diagrams rendered from DiagramSpec — no ASCII parsing</p>
{"".join(sections)}
</body>
</html>"""


if __name__ == "__main__":
    output = generate_showcase()
    Path("showcase_spec.html").write_text(output)
    print(f"Generated showcase_spec.html ({len(SPECS)} diagrams)")

    # Also write individual SVGs
    svg_dir = Path("svg_output")
    svg_dir.mkdir(exist_ok=True)
    for spec in SPECS:
        name = f"spec_{spec.type}_{(spec.title or spec.type).lower().replace(' ', '_').replace('/', '_')}"
        svg = render_spec_svg(spec)
        (svg_dir / f"{name}.svg").write_text(svg)
    print(f"Wrote {len(SPECS)} SVGs to svg_output/")
