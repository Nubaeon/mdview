#!/usr/bin/env python3
"""Generate SHOWCASE.md with diverse diagram types for visual testing.

Covers realistic scenarios: CI/CD pipelines, API architectures,
UI wireframes, deployment state machines, config tables, microservice boxes.
"""

from pathlib import Path
from mdview.spec import DiagramSpec, Element, Connection
from mdview.specrender import render_spec_svg


def _svg_block(spec: DiagramSpec) -> str:
    svg = render_spec_svg(spec)
    title = spec.title or f"{spec.type} diagram"
    return f"""
<div align="center">

{svg}

<em>{title}</em>

</div>
"""


# ── 1. CI/CD Pipeline (flow, horizontal) ─────────────────────────

CICD_PIPELINE = DiagramSpec(
    type="flow",
    title="GitHub Actions CI/CD Pipeline",
    layout="horizontal",
    elements=[
        Element(id="push", label="Push", type="node"),
        Element(id="lint", label="Lint", type="node"),
        Element(id="test", label="Test", type="node"),
        Element(id="build", label="Build", type="node"),
        Element(id="gate", label="Pass?", type="decision"),
        Element(id="stage", label="Staging", type="node"),
        Element(id="approve", label="Approve?", type="decision"),
        Element(id="prod", label="Production", type="node"),
    ],
    connections=[
        Connection(from_id="push", to_id="lint", label="trigger"),
        Connection(from_id="lint", to_id="test"),
        Connection(from_id="test", to_id="build"),
        Connection(from_id="build", to_id="gate"),
        Connection(from_id="gate", to_id="stage", label="yes"),
        Connection(from_id="stage", to_id="approve"),
        Connection(from_id="approve", to_id="prod", label="yes"),
    ],
)

# ── 2. RAG Pipeline (flow, vertical) ─────────────────────────────

RAG_PIPELINE = DiagramSpec(
    type="flow",
    title="RAG Pipeline",
    layout="vertical",
    elements=[
        Element(id="query", label="User Query", type="node"),
        Element(id="embed", label="Embed Query", type="node"),
        Element(id="search", label="Vector Search", type="node"),
        Element(id="rerank", label="Rerank", type="decision"),
        Element(id="context", label="Build Context", type="node"),
        Element(id="llm", label="LLM Generate", type="node"),
        Element(id="response", label="Response", type="node"),
    ],
    connections=[
        Connection(from_id="query", to_id="embed"),
        Connection(from_id="embed", to_id="search", label="k-NN"),
        Connection(from_id="search", to_id="rerank"),
        Connection(from_id="rerank", to_id="context", label="top-k"),
        Connection(from_id="context", to_id="llm", label="prompt"),
        Connection(from_id="llm", to_id="response"),
    ],
)

# ── 3. OAuth2 Flow (sequence) ─────────────────────────────────────

OAUTH_FLOW = DiagramSpec(
    type="sequence",
    title="OAuth2 Authorization Code Flow",
    elements=[
        Element(id="browser", label="Browser", type="actor"),
        Element(id="app", label="App Server", type="actor"),
        Element(id="auth", label="Auth Provider", type="actor"),
        Element(id="api", label="Resource API", type="actor"),
    ],
    connections=[
        Connection(from_id="browser", to_id="app", label="GET /login",
                   properties={"order": 1}),
        Connection(from_id="app", to_id="browser", label="redirect to auth",
                   properties={"order": 2}, style="dashed"),
        Connection(from_id="browser", to_id="auth", label="authorize",
                   properties={"order": 3}),
        Connection(from_id="auth", to_id="browser", label="code",
                   properties={"order": 4}, style="dashed"),
        Connection(from_id="browser", to_id="app", label="callback + code",
                   properties={"order": 5}),
        Connection(from_id="app", to_id="auth", label="exchange code",
                   properties={"order": 6}),
        Connection(from_id="auth", to_id="app", label="access_token",
                   properties={"order": 7}, style="dashed"),
        Connection(from_id="app", to_id="api", label="GET /data + token",
                   properties={"order": 8}),
        Connection(from_id="api", to_id="app", label="JSON response",
                   properties={"order": 9}, style="dashed"),
        Connection(from_id="app", to_id="browser", label="render page",
                   properties={"order": 10}, style="dashed"),
    ],
)

# ── 4. Dashboard Wireframe ────────────────────────────────────────

DASHBOARD_WIREFRAME = DiagramSpec(
    type="wireframe",
    title="Admin Dashboard Wireframe",
    layout="nested",
    elements=[
        Element(id="app", label="Dashboard", type="panel",
                children=["sidebar", "main"]),
        Element(id="sidebar", label="Navigation", type="sidebar",
                children=["nav_search", "nav_links"]),
        Element(id="nav_search", label="Search", type="input",
                properties={"value": "Search..."}),
        Element(id="nav_links", label="Menu Items", type="panel"),
        Element(id="main", label="Content", type="panel",
                children=["toolbar", "cards", "table_area"]),
        Element(id="toolbar", label="Actions", type="panel",
                children=["filter_input"]),
        Element(id="filter_input", label="Filter", type="input",
                properties={"value": "Filter results..."}),
        Element(id="cards", label="Metrics", type="panel"),
        Element(id="table_area", label="Data Table", type="panel"),
    ],
)

# ── 5. Microservice Architecture (box) ───────────────────────────

MICROSERVICES = DiagramSpec(
    type="box",
    title="Microservice Architecture",
    layout="horizontal",
    elements=[
        Element(id="gateway", label="API Gateway", type="box",
                properties={"sections": [
                    ["Rate limiting", "Auth middleware", "Request routing"],
                ]}),
        Element(id="users", label="User Service", type="box",
                properties={"sections": [
                    ["GET /users", "POST /users", "PUT /users/:id"],
                    ["PostgreSQL"],
                ]}),
        Element(id="orders", label="Order Service", type="box",
                properties={"sections": [
                    ["POST /orders", "GET /orders/:id"],
                    ["MongoDB"],
                ]}),
        Element(id="notify", label="Notification Service", type="box",
                properties={"sections": [
                    ["Email", "SMS", "Push"],
                    ["Redis queue"],
                ]}),
    ],
    connections=[
        Connection(from_id="gateway", to_id="users", label="REST"),
        Connection(from_id="gateway", to_id="orders", label="REST"),
        Connection(from_id="orders", to_id="notify", label="events"),
    ],
)

# ── 6. Deployment State Machine ───────────────────────────────────

DEPLOY_SM = DiagramSpec(
    type="state_machine",
    title="Deployment Lifecycle",
    elements=[
        Element(id="pending", label="Pending", type="initial"),
        Element(id="building", label="Building", type="node"),
        Element(id="testing", label="Testing", type="node"),
        Element(id="staging", label="Staging", type="node"),
        Element(id="live", label="Live", type="node"),
        Element(id="rollback", label="Rollback", type="node"),
        Element(id="failed", label="Failed", type="node"),
    ],
    connections=[
        Connection(from_id="pending", to_id="building", label="start"),
        Connection(from_id="building", to_id="testing", label="built"),
        Connection(from_id="testing", to_id="staging", label="passed"),
        Connection(from_id="testing", to_id="failed", label="failed"),
        Connection(from_id="staging", to_id="live", label="promote"),
        Connection(from_id="live", to_id="rollback", label="issue"),
        Connection(from_id="rollback", to_id="staging", label="reverted",
                   style="dashed"),
        Connection(from_id="failed", to_id="pending", label="retry",
                   style="dashed"),
    ],
)

# ── 7. API Reference Table ────────────────────────────────────────

API_TABLE = DiagramSpec(
    type="table",
    title="REST API Endpoints",
    elements=[
        Element(id="h", label="", type="header",
                properties={"cells": ["Method", "Endpoint", "Auth", "Description"]}),
        Element(id="r1", label="", type="row",
                properties={"cells": ["GET", "/api/users", "JWT", "List all users"]}),
        Element(id="r2", label="", type="row",
                properties={"cells": ["POST", "/api/users", "Admin", "Create user"]}),
        Element(id="r3", label="", type="row",
                properties={"cells": ["GET", "/api/orders", "JWT", "List orders"]}),
        Element(id="r4", label="", type="row",
                properties={"cells": ["POST", "/api/orders", "JWT", "Create order"]}),
        Element(id="r5", label="", type="row",
                properties={"cells": ["DELETE", "/api/orders/:id", "Admin", "Cancel order"]}),
    ],
)

# ── 8. LLM Agent Loop (state machine with self-loop) ─────────────

AGENT_LOOP = DiagramSpec(
    type="state_machine",
    title="LLM Agent Loop",
    elements=[
        Element(id="idle", label="Idle", type="initial"),
        Element(id="think", label="Think", type="node"),
        Element(id="act", label="Act", type="node"),
        Element(id="observe", label="Observe", type="node"),
        Element(id="done", label="Done", type="node"),
    ],
    connections=[
        Connection(from_id="idle", to_id="think", label="task"),
        Connection(from_id="think", to_id="act", label="plan"),
        Connection(from_id="act", to_id="observe", label="execute"),
        Connection(from_id="observe", to_id="think", label="iterate",
                   style="dashed"),
        Connection(from_id="observe", to_id="done", label="complete"),
        Connection(from_id="think", to_id="think", label="reason"),
    ],
)

# ── 9. Login Page Wireframe ───────────────────────────────────────

LOGIN_WIREFRAME = DiagramSpec(
    type="wireframe",
    title="Login Page Wireframe",
    layout="nested",
    elements=[
        Element(id="page", label="Login", type="panel",
                children=["logo", "form_area"]),
        Element(id="logo", label="App Logo", type="panel"),
        Element(id="form_area", label="Credentials", type="panel",
                children=["email", "password", "submit"]),
        Element(id="email", label="Email", type="input",
                properties={"value": "user@example.com"}),
        Element(id="password", label="Password", type="input",
                properties={"value": "********"}),
        Element(id="submit", label="Sign In", type="form"),
    ],
)

# ── 10. K8s Architecture (box) ────────────────────────────────────

K8S_ARCH = DiagramSpec(
    type="box",
    title="Kubernetes Deployment",
    layout="horizontal",
    elements=[
        Element(id="ingress", label="Ingress", type="box",
                properties={"sections": [
                    ["nginx controller"],
                    ["TLS termination", "Path routing"],
                ]}),
        Element(id="frontend", label="Frontend", type="box",
                properties={"sections": [
                    ["React SPA"],
                    ["3 replicas", "HPA: 2-10"],
                ]}),
        Element(id="backend", label="Backend API", type="box",
                properties={"sections": [
                    ["FastAPI"],
                    ["5 replicas", "HPA: 3-20"],
                ]}),
        Element(id="data", label="Data Layer", type="box",
                properties={"sections": [
                    ["PostgreSQL 15", "Redis 7"],
                    ["PVC: 100Gi", "Backup: hourly"],
                ]}),
    ],
    connections=[
        Connection(from_id="ingress", to_id="frontend"),
        Connection(from_id="ingress", to_id="backend", label="/api"),
        Connection(from_id="backend", to_id="data"),
    ],
)


# ── Document generation ────────────────────────────────────────────

def generate() -> str:
    return f"""# mdview Diagram Showcase

> Demonstrating all 6 diagram types with realistic engineering scenarios.
> Every diagram is a `DiagramSpec` rendered to themed SVG with dark/light support.

---

## 1. CI/CD Pipeline

A typical GitHub Actions pipeline with lint, test, build gates and manual approval.

{_svg_block(CICD_PIPELINE)}

## 2. RAG Pipeline

Retrieval-Augmented Generation flow — from user query to LLM response.

{_svg_block(RAG_PIPELINE)}

## 3. OAuth2 Authorization Flow

Full OAuth2 authorization code flow with browser, app server, auth provider, and resource API.

{_svg_block(OAUTH_FLOW)}

## 4. Admin Dashboard Wireframe

Nested UI wireframe with sidebar navigation, toolbar, and content areas.

{_svg_block(DASHBOARD_WIREFRAME)}

## 5. Microservice Architecture

Service decomposition with API gateway, domain services, and data stores.

{_svg_block(MICROSERVICES)}

## 6. Deployment Lifecycle

State machine showing deployment progression with rollback and retry paths.

{_svg_block(DEPLOY_SM)}

## 7. REST API Reference

API endpoint documentation as a styled table.

{_svg_block(API_TABLE)}

## 8. LLM Agent Loop

Think-Act-Observe cycle with self-loop reasoning and iteration back-edges.

{_svg_block(AGENT_LOOP)}

## 9. Login Page Wireframe

Simple login form wireframe with email, password, and submit button.

{_svg_block(LOGIN_WIREFRAME)}

## 10. Kubernetes Deployment

Infrastructure as boxes showing ingress, services, and data layer with replicas.

{_svg_block(K8S_ARCH)}

---

*All diagrams rendered by mdview's spec-based pipeline. Zero external dependencies.*
"""


if __name__ == "__main__":
    doc = generate()
    Path("SHOWCASE.md").write_text(doc)
    print(f"Generated SHOWCASE.md ({len(doc)} bytes, {doc.count('<svg')} diagrams)")
