#!/usr/bin/env python3
"""Generate EMPIRICA_MAP.md — epistemic map of Empirica's architecture.

Dogfoods mdview on a real, complex system: Empirica's cognitive infrastructure.
Each diagram is a DiagramSpec rendered to inline SVG. This stress-tests mdview
on the same architecture it's designed to support.
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. EPISTEMIC TRANSACTION LIFECYCLE (state machine)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRANSACTION_LIFECYCLE = DiagramSpec(
    type="state_machine",
    title="Epistemic Transaction Lifecycle",
    elements=[
        Element(id="idle", label="Idle", type="initial"),
        Element(id="preflight", label="PREFLIGHT", type="node"),
        Element(id="noetic", label="Noetic", type="node"),
        Element(id="check", label="CHECK", type="node"),
        Element(id="praxic", label="Praxic", type="node"),
        Element(id="postflight", label="POSTFLIGHT", type="node"),
        Element(id="posttest", label="POST-TEST", type="node"),
    ],
    connections=[
        Connection(from_id="idle", to_id="preflight", label="start"),
        Connection(from_id="preflight", to_id="noetic", label="investigate"),
        Connection(from_id="noetic", to_id="check", label="assess"),
        Connection(from_id="check", to_id="noetic", label="investigate",
                   style="dashed"),
        Connection(from_id="check", to_id="praxic", label="proceed"),
        Connection(from_id="praxic", to_id="postflight", label="complete"),
        Connection(from_id="postflight", to_id="posttest", label="verify"),
        Connection(from_id="posttest", to_id="idle", label="close",
                   style="dashed"),
        Connection(from_id="noetic", to_id="noetic", label="discover"),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. FOUR-LAYER STORAGE ARCHITECTURE (box diagram)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STORAGE_LAYERS = DiagramSpec(
    type="box",
    title="Four-Layer Storage Architecture",
    layout="horizontal",
    elements=[
        Element(id="hot", label="HOT", type="box",
                properties={"sections": [
                    ["Active session state"],
                    ["In-memory", "Conversation context"],
                ]}),
        Element(id="warm", label="WARM", type="box",
                properties={"sections": [
                    ["Persistent structured data"],
                    ["SQLite", "Transactions", "Artifacts", "Calibration"],
                ]}),
        Element(id="search", label="SEARCH", type="box",
                properties={"sections": [
                    ["Semantic retrieval"],
                    ["Qdrant", "Eidetic facts", "Episodic narratives"],
                ]}),
        Element(id="cold", label="COLD", type="box",
                properties={"sections": [
                    ["Archival + versioned"],
                    ["Git notes", "YAML snapshots", ".breadcrumbs.yaml"],
                ]}),
    ],
    connections=[
        Connection(from_id="hot", to_id="warm", label="persist"),
        Connection(from_id="warm", to_id="search", label="embed"),
        Connection(from_id="warm", to_id="cold", label="archive"),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. CLI → SENTINEL → STORAGE FLOW (sequence diagram)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLI_FLOW = DiagramSpec(
    type="sequence",
    title="Transaction Flow: Agent → CLI → Storage",
    elements=[
        Element(id="agent", label="AI Agent", type="actor"),
        Element(id="cli", label="Empirica CLI", type="actor"),
        Element(id="sentinel", label="Sentinel", type="actor"),
        Element(id="sqlite", label="SQLite", type="actor"),
        Element(id="qdrant", label="Qdrant", type="actor"),
    ],
    connections=[
        Connection(from_id="agent", to_id="cli",
                   label="preflight-submit",
                   properties={"order": 1}),
        Connection(from_id="cli", to_id="sqlite",
                   label="store vectors",
                   properties={"order": 2}),
        Connection(from_id="agent", to_id="cli",
                   label="finding-log",
                   properties={"order": 3}),
        Connection(from_id="cli", to_id="sqlite",
                   label="insert artifact",
                   properties={"order": 4}),
        Connection(from_id="agent", to_id="cli",
                   label="check-submit",
                   properties={"order": 5}),
        Connection(from_id="cli", to_id="sentinel",
                   label="assess readiness",
                   properties={"order": 6}),
        Connection(from_id="sentinel", to_id="cli",
                   label="proceed / investigate",
                   properties={"order": 7}, style="dashed"),
        Connection(from_id="agent", to_id="cli",
                   label="postflight-submit",
                   properties={"order": 8}),
        Connection(from_id="cli", to_id="sqlite",
                   label="close transaction",
                   properties={"order": 9}),
        Connection(from_id="cli", to_id="qdrant",
                   label="embed snapshot",
                   properties={"order": 10}),
        Connection(from_id="cli", to_id="agent",
                   label="delta + calibration",
                   properties={"order": 11}, style="dashed"),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. ARTIFACT TAXONOMY (box diagram)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ARTIFACT_TAXONOMY = DiagramSpec(
    type="box",
    title="Artifact Taxonomy",
    layout="horizontal",
    elements=[
        Element(id="noetic", label="Noetic Artifacts", type="box",
                properties={"sections": [
                    ["Investigation outputs"],
                    ["findings", "unknowns", "dead-ends",
                     "mistakes", "blindspots", "lessons"],
                ]}),
        Element(id="intent", label="Epistemic Intent", type="box",
                properties={"sections": [
                    ["Intent layer"],
                    ["assumptions", "decisions", "intent edges"],
                ]}),
        Element(id="praxic", label="Praxic Artifacts", type="box",
                properties={"sections": [
                    ["Action outputs"],
                    ["goals", "subtasks", "commits"],
                ]}),
        Element(id="state", label="Epistemic State", type="box",
                properties={"sections": [
                    ["State measurements"],
                    ["vectors", "calibration", "drift", "deltas"],
                ]}),
        Element(id="grounded", label="Grounded Evidence", type="box",
                properties={"sections": [
                    ["Verification outputs"],
                    ["test results", "git metrics",
                     "goal completion", "artifact ratios"],
                ]}),
    ],
    connections=[
        Connection(from_id="noetic", to_id="intent", label="inform"),
        Connection(from_id="intent", to_id="praxic", label="drive"),
        Connection(from_id="praxic", to_id="state", label="measure"),
        Connection(from_id="state", to_id="grounded", label="verify"),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. DUAL-TRACK CALIBRATION (flow diagram)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CALIBRATION_PIPELINE = DiagramSpec(
    type="flow",
    title="Dual-Track Calibration Pipeline",
    layout="vertical",
    elements=[
        Element(id="preflight", label="PREFLIGHT Vectors", type="node"),
        Element(id="work", label="Noetic + Praxic Work", type="node"),
        Element(id="postflight", label="POSTFLIGHT Vectors", type="node"),
        Element(id="split", label="Compare?", type="decision"),
        Element(id="track1", label="Track 1: Self-Referential", type="node"),
        Element(id="track2", label="Track 2: Grounded", type="node"),
        Element(id="converge", label="Calibration Score", type="node"),
    ],
    connections=[
        Connection(from_id="preflight", to_id="work", label="measure"),
        Connection(from_id="work", to_id="postflight", label="assess"),
        Connection(from_id="postflight", to_id="split"),
        Connection(from_id="split", to_id="track1",
                   label="delta"),
        Connection(from_id="split", to_id="track2",
                   label="evidence"),
        Connection(from_id="track1", to_id="converge"),
        Connection(from_id="track2", to_id="converge"),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. COGNITIVE IMMUNE SYSTEM (state machine)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMMUNE_SYSTEM = DiagramSpec(
    type="state_machine",
    title="Cognitive Immune System",
    elements=[
        Element(id="finding", label="Finding", type="initial"),
        Element(id="extract", label="Extract Keywords", type="node"),
        Element(id="match", label="Match Lessons", type="node"),
        Element(id="decay", label="Reduce Confidence", type="node"),
        Element(id="floor", label="Floor: 0.3", type="node"),
    ],
    connections=[
        Connection(from_id="finding", to_id="extract", label="new finding"),
        Connection(from_id="extract", to_id="match", label="keywords"),
        Connection(from_id="match", to_id="decay", label="related lessons"),
        Connection(from_id="decay", to_id="floor", label="min confidence"),
        Connection(from_id="decay", to_id="match", label="next lesson",
                   style="dashed"),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. 13 EPISTEMIC VECTORS (table)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VECTORS_TABLE = DiagramSpec(
    type="table",
    title="13 Epistemic Vectors",
    elements=[
        Element(id="h", label="", type="header",
                properties={"cells": ["Category", "Vector", "Measures"]}),
        Element(id="r1", label="", type="row",
                properties={"cells": ["Foundation", "know", "Domain knowledge depth"]}),
        Element(id="r2", label="", type="row",
                properties={"cells": ["Foundation", "do", "Implementation capability"]}),
        Element(id="r3", label="", type="row",
                properties={"cells": ["Foundation", "context", "Situational awareness"]}),
        Element(id="r4", label="", type="row",
                properties={"cells": ["Comprehension", "clarity", "Understanding precision"]}),
        Element(id="r5", label="", type="row",
                properties={"cells": ["Comprehension", "coherence", "Internal consistency"]}),
        Element(id="r6", label="", type="row",
                properties={"cells": ["Comprehension", "signal", "Information relevance"]}),
        Element(id="r7", label="", type="row",
                properties={"cells": ["Comprehension", "density", "Knowledge compactness"]}),
        Element(id="r8", label="", type="row",
                properties={"cells": ["Execution", "state", "System state awareness"]}),
        Element(id="r9", label="", type="row",
                properties={"cells": ["Execution", "change", "Delta from baseline"]}),
        Element(id="r10", label="", type="row",
                properties={"cells": ["Execution", "completion", "Goal progress"]}),
        Element(id="r11", label="", type="row",
                properties={"cells": ["Execution", "impact", "Consequence significance"]}),
        Element(id="r12", label="", type="row",
                properties={"cells": ["Meta", "engagement", "Active participation"]}),
        Element(id="r13", label="", type="row",
                properties={"cells": ["Meta", "uncertainty", "Epistemic humility"]}),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. PLATFORM INTEGRATION (table)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLATFORM_TABLE = DiagramSpec(
    type="table",
    title="Platform Integration Matrix",
    elements=[
        Element(id="h", label="", type="header",
                properties={"cells": ["Platform", "Hooks", "Sentinel", "Status"]}),
        Element(id="r1", label="", type="row",
                properties={"cells": [
                    "Claude Code", "Full (10 events)", "Automatic", "Production"]}),
        Element(id="r2", label="", type="row",
                properties={"cells": [
                    "Gemini CLI", "Full (11 events)", "Possible", "Experimental"]}),
        Element(id="r3", label="", type="row",
                properties={"cells": [
                    "Cline", "Full (5 events)", "Possible", "Experimental"]}),
        Element(id="r4", label="", type="row",
                properties={"cells": [
                    "Copilot CLI", "Full (6 events)", "Possible", "Experimental"]}),
        Element(id="r5", label="", type="row",
                properties={"cells": [
                    "Cursor", "Partial (6 events)", "Possible", "Experimental"]}),
        Element(id="r6", label="", type="row",
                properties={"cells": [
                    "Windsurf", "Limited (2)", "None", "Manual"]}),
        Element(id="r7", label="", type="row",
                properties={"cells": [
                    "Aider", "None", "None", "Manual"]}),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. NOETIC FIREWALL (flow diagram)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NOETIC_FIREWALL = DiagramSpec(
    type="flow",
    title="Noetic Firewall — Sentinel Gate",
    layout="horizontal",
    elements=[
        Element(id="tool", label="Tool Call", type="node"),
        Element(id="classify", label="Noetic or Praxic?", type="decision"),
        Element(id="allow", label="Allow", type="node"),
        Element(id="gate", label="CHECK Passed?", type="decision"),
        Element(id="block", label="Block", type="node"),
        Element(id="execute", label="Execute", type="node"),
    ],
    connections=[
        Connection(from_id="tool", to_id="classify"),
        Connection(from_id="classify", to_id="allow", label="noetic"),
        Connection(from_id="classify", to_id="gate", label="praxic"),
        Connection(from_id="gate", to_id="execute", label="yes"),
        Connection(from_id="gate", to_id="block", label="no"),
        Connection(from_id="allow", to_id="execute"),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. EMPIRICA-AUTONOMY VISION (wireframe)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AUTONOMY_WIREFRAME = DiagramSpec(
    type="wireframe",
    title="empirica-autonomy Remote Control Vision",
    layout="nested",
    elements=[
        Element(id="app", label="Remote Control", type="panel",
                children=["sidebar", "main"]),
        Element(id="sidebar", label="Sessions", type="sidebar",
                children=["session_search", "session_list"]),
        Element(id="session_search", label="Filter", type="input",
                properties={"value": "Search sessions..."}),
        Element(id="session_list", label="Active Agents", type="panel"),
        Element(id="main", label="Live View", type="panel",
                children=["vectors", "diagrams", "artifacts"]),
        Element(id="vectors", label="Epistemic Vectors", type="panel"),
        Element(id="diagrams", label="Architecture Map", type="panel"),
        Element(id="artifacts", label="Artifact Stream", type="panel"),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 11. META: THIS PLAN (flow diagram)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THIS_PLAN = DiagramSpec(
    type="flow",
    title="This Plan — Epistemic Map of mdview Roadmap",
    layout="vertical",
    elements=[
        Element(id="map", label="Empirica Map", type="node"),
        Element(id="docs", label="Documentation", type="node"),
        Element(id="skill", label="/map Skill", type="node"),
        Element(id="ws", label="WebSocket Layer", type="node"),
        Element(id="remote", label="/remote-control", type="node"),
        Element(id="app", label="Android App", type="node"),
    ],
    connections=[
        Connection(from_id="map", to_id="docs",
                   label="dogfood"),
        Connection(from_id="docs", to_id="skill",
                   label="generalize"),
        Connection(from_id="skill", to_id="ws",
                   label="live updates"),
        Connection(from_id="ws", to_id="remote",
                   label="oversight"),
        Connection(from_id="remote", to_id="app",
                   label="mobile"),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 12. ECOSYSTEM VISION (box diagram)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ECOSYSTEM = DiagramSpec(
    type="box",
    title="Empirica Ecosystem",
    layout="horizontal",
    elements=[
        Element(id="core", label="empirica (core)", type="box",
                properties={"sections": [
                    ["CLI + SQLite + Qdrant"],
                    ["Transactions", "Calibration", "Sentinel"],
                ]}),
        Element(id="plugin", label="empirica-integration", type="box",
                properties={"sections": [
                    ["Claude Code Plugin"],
                    ["Hooks", "Skills", "Agents", "Commands"],
                ]}),
        Element(id="autonomy", label="empirica-autonomy", type="box",
                properties={"sections": [
                    ["Remote Oversight"],
                    ["WebSocket", "Live Dashboard", "Android App"],
                ]}),
        Element(id="mdview", label="mdview", type="box",
                properties={"sections": [
                    ["Diagram Rendering"],
                    ["DiagramSpec", "6 SVG Renderers", "Themes"],
                ]}),
    ],
    connections=[
        Connection(from_id="core", to_id="plugin", label="hooks"),
        Connection(from_id="core", to_id="autonomy", label="data"),
        Connection(from_id="mdview", to_id="autonomy", label="render"),
        Connection(from_id="plugin", to_id="mdview", label="/map"),
    ],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Document generation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate() -> str:
    return f"""# Empirica Epistemic Map

> Architecture of cognitive infrastructure — rendered by mdview.
> Every diagram is a `DiagramSpec` stress-testing mdview on a live system.

---

## Transaction Lifecycle

The core measurement cycle. PREFLIGHT opens a window, noetic investigation
builds understanding, CHECK gates the transition to praxic action, and
POSTFLIGHT captures the learning delta. POST-TEST grounds it against
objective evidence.

{_svg_block(TRANSACTION_LIFECYCLE)}

## Storage Architecture

Four layers, hot to cold. Active session state lives in memory, structured
data persists in SQLite, semantic retrieval via Qdrant, and archival
in git notes and YAML snapshots.

{_svg_block(STORAGE_LAYERS)}

## Transaction Flow

A typical epistemic transaction from the AI agent's perspective. The CLI
mediates between agent and storage, with the Sentinel gating the
noetic-to-praxic transition.

{_svg_block(CLI_FLOW)}

## Artifact Taxonomy

Five layers of epistemic artifacts. Noetic artifacts come from investigation,
epistemic intent captures beliefs and choices, praxic artifacts record actions,
state measurements track progress, and grounded evidence verifies it all.

{_svg_block(ARTIFACT_TAXONOMY)}

## Dual-Track Calibration

Two independent tracks measure different things. Track 1 (self-referential)
captures learning trajectory via PREFLIGHT→POSTFLIGHT delta. Track 2
(grounded) compares self-assessment against objective evidence. When they
diverge, Track 2 wins.

{_svg_block(CALIBRATION_PIPELINE)}

## Cognitive Immune System

Lessons are antibodies, findings are antigens. When a new finding arrives,
keywords are extracted and matched against existing lessons. Related lessons
have their confidence reduced — but never below 0.3. Lessons never fully die.

{_svg_block(IMMUNE_SYSTEM)}

## 13 Epistemic Vectors

The state space. Every PREFLIGHT, CHECK, and POSTFLIGHT submits
these 13 vectors on a 0.0–1.0 scale.

{_svg_block(VECTORS_TABLE)}

## Noetic Firewall

The Sentinel classifies every tool call as noetic (investigation) or praxic
(action). Noetic tools always pass. Praxic tools require a valid CHECK
with `proceed` — preventing action before sufficient understanding.

{_svg_block(NOETIC_FIREWALL)}

## Platform Integration

Empirica works with any AI platform. Integration depth varies by hook support.

{_svg_block(PLATFORM_TABLE)}

## Remote Control Vision

The end state: empirica-autonomy renders live epistemic state via WebSocket.
mdview provides the diagram rendering layer. A companion Android app sits
alongside Claude Chat for mobile oversight.

{_svg_block(AUTONOMY_WIREFRAME)}

## Ecosystem

All roads lead back to Empirica. The core CLI provides measurement.
The plugin integrates with coding agents. mdview renders diagrams.
empirica-autonomy provides remote oversight. Plugins in, knowledge out.

{_svg_block(ECOSYSTEM)}

## Roadmap

This plan, rendered as a flow diagram. Each step builds on the last:
dogfood the map, write documentation, generalize to a /map skill,
add live WebSocket updates, build remote control, ship mobile.

{_svg_block(THIS_PLAN)}

---

*Every diagram in this document is rendered by mdview's spec-based pipeline.
This is the system documenting itself — epistemic infrastructure all the way down.*
"""


if __name__ == "__main__":
    doc = generate()
    Path("EMPIRICA_MAP.md").write_text(doc)
    print(f"Generated EMPIRICA_MAP.md ({len(doc)} bytes, {doc.count('<svg')} diagrams)")
