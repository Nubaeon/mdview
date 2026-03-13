# Empirica Epistemic Map

> Architecture of cognitive infrastructure — rendered by mdview.
> Every diagram is a `DiagramSpec` stress-testing mdview on a live system.

---

## Transaction Lifecycle

The core measurement cycle. PREFLIGHT opens a window, noetic investigation
builds understanding, CHECK gates the transition to praxic action, and
POSTFLIGHT captures the learning delta. POST-TEST grounds it against
objective evidence.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="974" height="278" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <defs>
    <marker id="d0-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <style>
    .mdview-diagram .state-node { stroke: #7aa2f7; stroke-width: 2; fill: #24283b; rx: 20; }
    .mdview-diagram .state-initial { stroke: #7aa2f7; stroke-width: 2.5; }
    .mdview-diagram .state-text { fill: #9ece6a; font-weight: 600; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .state-node { stroke: #2e7de9; fill: #e8e8f0; }
      .mdview-diagram .state-initial { stroke: #2e7de9; }
      .mdview-diagram .state-text { fill: #587539; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="974" height="278" rx="6"/>
  <line class="arrow-line" x1="329.2" y1="72.0" x2="389.2" y2="72.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="524.2" y1="72.0" x2="584.2" y2="72.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="719.2" y1="72.0" x2="779.2" y2="72.0" marker-end="url(#d0-ah)"/>
  <path class="arrow-line" d="M 846.7,94.0 C 846.7,144.0 651.7,144.0 651.7,94.0" marker-end="url(#d0-ah)" stroke-dasharray="6,3"/>
  <line class="arrow-line" x1="779.2" y1="72.0" x2="329.2" y2="196.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="329.2" y1="196.0" x2="389.2" y2="196.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="524.2" y1="196.0" x2="584.2" y2="196.0" marker-end="url(#d0-ah)"/>
  <path class="arrow-line" d="M 584.2,196.0 C 40.0,134.0 40.0,134.0 194.2,72.0" marker-end="url(#d0-ah)" stroke-dasharray="6,3"/>
  <path class="arrow-line" d="M 636.7,50.0 C 636.7,20.0 666.7,20.0 666.7,50.0" marker-end="url(#d0-ah)"/>
  <rect class="state-node state-initial" x="194.2" y="50.0" width="135.0" height="44.0" rx="20"/>
  <rect class="state-node" x="389.2" y="50.0" width="135.0" height="44.0" rx="20"/>
  <rect class="state-node" x="584.2" y="50.0" width="135.0" height="44.0" rx="20"/>
  <rect class="state-node" x="779.2" y="50.0" width="135.0" height="44.0" rx="20"/>
  <rect class="state-node" x="194.2" y="174.0" width="135.0" height="44.0" rx="20"/>
  <rect class="state-node" x="389.2" y="174.0" width="135.0" height="44.0" rx="20"/>
  <rect class="state-node" x="584.2" y="174.0" width="135.0" height="44.0" rx="20"/>
  <rect class="arrow-label-bg" x="337.2" y="63.0" width="44.0" height="16.0" rx="3"/>
  <text class="arrow-label" x="359.2" y="72.0" dominant-baseline="central">start</text>
  <rect class="arrow-label-bg" x="510.6" y="63.0" width="87.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="554.2" y="72.0" dominant-baseline="central">investigate</text>
  <rect class="arrow-label-bg" x="723.6" y="63.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="749.2" y="72.0" dominant-baseline="central">assess</text>
  <rect class="arrow-label-bg" x="705.6" y="122.5" width="87.2" height="16" rx="3"/>
  <text class="arrow-label" x="749.2" y="131.5" dominant-baseline="central">investigate</text>
  <rect class="arrow-label-bg" x="525.0" y="125.0" width="58.4" height="16.0" rx="3"/>
  <text class="arrow-label" x="554.2" y="134.0" dominant-baseline="central">proceed</text>
  <rect class="arrow-label-bg" x="326.4" y="187.0" width="65.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="359.2" y="196.0" dominant-baseline="central">complete</text>
  <rect class="arrow-label-bg" x="528.6" y="187.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="554.2" y="196.0" dominant-baseline="central">verify</text>
  <rect class="arrow-label-bg" x="105.3" y="125.0" width="44.0" height="16" rx="3"/>
  <text class="arrow-label" x="127.3" y="134.0" dominant-baseline="central">close</text>
  <rect class="arrow-label-bg" x="618.9" y="8.0" width="65.6" height="16" rx="3"/>
  <text class="arrow-label" x="651.7" y="16.0" dominant-baseline="central">discover</text>
  <text class="state-text" x="261.7" y="72.0" text-anchor="middle" dominant-baseline="central">Idle</text>
  <text class="state-text" x="456.7" y="72.0" text-anchor="middle" dominant-baseline="central">PREFLIGHT</text>
  <text class="state-text" x="651.7" y="72.0" text-anchor="middle" dominant-baseline="central">Noetic</text>
  <text class="state-text" x="846.7" y="72.0" text-anchor="middle" dominant-baseline="central">CHECK</text>
  <text class="state-text" x="261.7" y="196.0" text-anchor="middle" dominant-baseline="central">Praxic</text>
  <text class="state-text" x="456.7" y="196.0" text-anchor="middle" dominant-baseline="central">POSTFLIGHT</text>
  <text class="state-text" x="651.7" y="196.0" text-anchor="middle" dominant-baseline="central">POST-TEST</text>
</svg>

<em>Epistemic Transaction Lifecycle</em>

</div>


## Storage Architecture

Four layers, hot to cold. Active session state lives in memory, structured
data persists in SQLite, semantic retrieval via Qdrant, and archival
in git notes and YAML snapshots.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="761" height="332" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="761" height="332" rx="6"/>
  <defs>
    <clipPath id="d1-bc0"><rect x="20.0" y="20.0" width="212.0" height="112.0" rx="6"/></clipPath>
    <clipPath id="d1-bc1"><rect x="252.0" y="20.0" width="266.0" height="144.0" rx="6"/></clipPath>
    <clipPath id="d1-bc2"><rect x="538.0" y="20.0" width="203.0" height="128.0" rx="6"/></clipPath>
    <clipPath id="d1-bc3"><rect x="20.0" y="184.0" width="212.0" height="128.0" rx="6"/></clipPath>
  </defs>
  <defs>
    <marker id="d1-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <line class="arrow-line" x1="232.0" y1="76.0" x2="252.0" y2="92.0" marker-end="url(#d1-ah)"/>
  <line class="arrow-line" x1="518.0" y1="92.0" x2="538.0" y2="84.0" marker-end="url(#d1-ah)"/>
  <line class="arrow-line" x1="252.0" y1="92.0" x2="232.0" y2="248.0" marker-end="url(#d1-ah)"/>
  <rect class="box-fill" x="20.0" y="20.0" width="212.0" height="112.0" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="212.0" height="112.0" rx="6"/>
  <g clip-path="url(#d1-bc0)">
    <text class="box-header" x="126.0" y="40.0" text-anchor="middle" dominant-baseline="central">HOT</text>
    <line class="box-separator" x1="20.0" y1="52.0" x2="232.0" y2="52.0"/>
    <text class="box-text" x="32.0" y="74.0">Active session state</text>
    <line class="box-separator" x1="20.0" y1="80.0" x2="232.0" y2="80.0"/>
    <text class="box-text" x="32.0" y="102.0">In-memory</text>
    <text class="box-text" x="32.0" y="118.0">Conversation context</text>
  </g>
  <rect class="box-fill" x="252.0" y="20.0" width="266.0" height="144.0" rx="6"/>
  <rect class="box-border" x="252.0" y="20.0" width="266.0" height="144.0" rx="6"/>
  <g clip-path="url(#d1-bc1)">
    <text class="box-header" x="385.0" y="40.0" text-anchor="middle" dominant-baseline="central">WARM</text>
    <line class="box-separator" x1="252.0" y1="52.0" x2="518.0" y2="52.0"/>
    <text class="box-text" x="264.0" y="74.0">Persistent structured data</text>
    <line class="box-separator" x1="252.0" y1="80.0" x2="518.0" y2="80.0"/>
    <text class="box-text" x="264.0" y="102.0">SQLite</text>
    <text class="box-text" x="264.0" y="118.0">Transactions</text>
    <text class="box-text" x="264.0" y="134.0">Artifacts</text>
    <text class="box-text" x="264.0" y="150.0">Calibration</text>
  </g>
  <rect class="box-fill" x="538.0" y="20.0" width="203.0" height="128.0" rx="6"/>
  <rect class="box-border" x="538.0" y="20.0" width="203.0" height="128.0" rx="6"/>
  <g clip-path="url(#d1-bc2)">
    <text class="box-header" x="639.5" y="40.0" text-anchor="middle" dominant-baseline="central">SEARCH</text>
    <line class="box-separator" x1="538.0" y1="52.0" x2="741.0" y2="52.0"/>
    <text class="box-text" x="550.0" y="74.0">Semantic retrieval</text>
    <line class="box-separator" x1="538.0" y1="80.0" x2="741.0" y2="80.0"/>
    <text class="box-text" x="550.0" y="102.0">Qdrant</text>
    <text class="box-text" x="550.0" y="118.0">Eidetic facts</text>
    <text class="box-text" x="550.0" y="134.0">Episodic narratives</text>
  </g>
  <rect class="box-fill" x="20.0" y="184.0" width="212.0" height="128.0" rx="6"/>
  <rect class="box-border" x="20.0" y="184.0" width="212.0" height="128.0" rx="6"/>
  <g clip-path="url(#d1-bc3)">
    <text class="box-header" x="126.0" y="204.0" text-anchor="middle" dominant-baseline="central">COLD</text>
    <line class="box-separator" x1="20.0" y1="216.0" x2="232.0" y2="216.0"/>
    <text class="box-text" x="32.0" y="238.0">Archival + versioned</text>
    <line class="box-separator" x1="20.0" y1="244.0" x2="232.0" y2="244.0"/>
    <text class="box-text" x="32.0" y="266.0">Git notes</text>
    <text class="box-text" x="32.0" y="282.0">YAML snapshots</text>
    <text class="box-text" x="32.0" y="298.0">.breadcrumbs.yaml</text>
  </g>
  <rect class="arrow-label-bg" x="212.8" y="75.0" width="58.4" height="16" rx="3"/>
  <text class="arrow-label" x="242.0" y="84.0" dominant-baseline="central">persist</text>
  <rect class="arrow-label-bg" x="506.0" y="79.0" width="44.0" height="16" rx="3"/>
  <text class="arrow-label" x="528.0" y="88.0" dominant-baseline="central">embed</text>
  <rect class="arrow-label-bg" x="212.8" y="161.0" width="58.4" height="16" rx="3"/>
  <text class="arrow-label" x="242.0" y="170.0" dominant-baseline="central">archive</text>
</svg>

<em>Four-Layer Storage Architecture</em>

</div>


## Transaction Flow

A typical epistemic transaction from the AI agent's perspective. The CLI
mediates between agent and storage, with the Sentinel gating the
noetic-to-praxic transition.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="940" height="500" style="display:block;margin:auto" class="mdview-diagram">
  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .bg { fill: #1a1b26; }
    .mdview-diagram .actor-box { fill: #24283b; stroke: #7aa2f7; stroke-width: 1.5; }
    .mdview-diagram .actor-text { fill: #9ece6a; font-weight: 600; text-anchor: middle; dominant-baseline: central; }
    .mdview-diagram .lifeline { stroke: #565f89; stroke-width: 1; stroke-dasharray: 6,4; }
    .mdview-diagram .msg-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .msg-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .msg-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .bg { fill: #f8f8fc; }
      .mdview-diagram .actor-box { fill: #e8e8f0; stroke: #2e7de9; }
      .mdview-diagram .actor-text { fill: #587539; }
      .mdview-diagram .lifeline { stroke: #9ca0b0; }
      .mdview-diagram .msg-line { stroke: #7847bd; }
      .mdview-diagram .msg-head { fill: #7847bd; }
      .mdview-diagram .msg-label { fill: #8c6c3e; }
    }
  </style>
  <defs>
    <marker id="d2-sa" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="msg-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="940" height="500" rx="6"/>
  <rect class="actor-box" x="40.0" y="20" width="132.0" height="32" rx="4"/>
  <text class="actor-text" x="106.0" y="36.0">AI Agent</text>
  <rect class="actor-box" x="40.0" y="448" width="132.0" height="32" rx="4"/>
  <text class="actor-text" x="106.0" y="464.0">AI Agent</text>
  <rect class="actor-box" x="222.0" y="20" width="132.0" height="32" rx="4"/>
  <text class="actor-text" x="288.0" y="36.0">Empirica CLI</text>
  <rect class="actor-box" x="222.0" y="448" width="132.0" height="32" rx="4"/>
  <text class="actor-text" x="288.0" y="464.0">Empirica CLI</text>
  <rect class="actor-box" x="404.0" y="20" width="132.0" height="32" rx="4"/>
  <text class="actor-text" x="470.0" y="36.0">Sentinel</text>
  <rect class="actor-box" x="404.0" y="448" width="132.0" height="32" rx="4"/>
  <text class="actor-text" x="470.0" y="464.0">Sentinel</text>
  <rect class="actor-box" x="586.0" y="20" width="132.0" height="32" rx="4"/>
  <text class="actor-text" x="652.0" y="36.0">SQLite</text>
  <rect class="actor-box" x="586.0" y="448" width="132.0" height="32" rx="4"/>
  <text class="actor-text" x="652.0" y="464.0">SQLite</text>
  <rect class="actor-box" x="768.0" y="20" width="132.0" height="32" rx="4"/>
  <text class="actor-text" x="834.0" y="36.0">Qdrant</text>
  <rect class="actor-box" x="768.0" y="448" width="132.0" height="32" rx="4"/>
  <text class="actor-text" x="834.0" y="464.0">Qdrant</text>
  <line class="lifeline" x1="106.0" y1="64" x2="106.0" y2="436"/>
  <line class="lifeline" x1="288.0" y1="64" x2="288.0" y2="436"/>
  <line class="lifeline" x1="470.0" y1="64" x2="470.0" y2="436"/>
  <line class="lifeline" x1="652.0" y1="64" x2="652.0" y2="436"/>
  <line class="lifeline" x1="834.0" y1="64" x2="834.0" y2="436"/>
  <line class="msg-line" x1="106.0" y1="80.0" x2="288.0" y2="80.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="197.0" y="72.0">preflight-submit</text>
  <line class="msg-line" x1="288.0" y1="112.0" x2="652.0" y2="112.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="470.0" y="104.0">store vectors</text>
  <line class="msg-line" x1="106.0" y1="144.0" x2="288.0" y2="144.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="197.0" y="136.0">finding-log</text>
  <line class="msg-line" x1="288.0" y1="176.0" x2="652.0" y2="176.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="470.0" y="168.0">insert artifact</text>
  <line class="msg-line" x1="106.0" y1="208.0" x2="288.0" y2="208.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="197.0" y="200.0">check-submit</text>
  <line class="msg-line" x1="288.0" y1="240.0" x2="470.0" y2="240.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="379.0" y="232.0">assess readiness</text>
  <line class="msg-line" x1="288.0" y1="272.0" x2="470.0" y2="272.0" stroke-dasharray="6,3" marker-start="url(#d2-sa)"/>
  <text class="msg-label" x="379.0" y="264.0">proceed / investigate</text>
  <line class="msg-line" x1="106.0" y1="304.0" x2="288.0" y2="304.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="197.0" y="296.0">postflight-submit</text>
  <line class="msg-line" x1="288.0" y1="336.0" x2="652.0" y2="336.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="470.0" y="328.0">close transaction</text>
  <line class="msg-line" x1="288.0" y1="368.0" x2="834.0" y2="368.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="561.0" y="360.0">embed snapshot</text>
  <line class="msg-line" x1="106.0" y1="400.0" x2="288.0" y2="400.0" stroke-dasharray="6,3" marker-start="url(#d2-sa)"/>
  <text class="msg-label" x="197.0" y="392.0">delta + calibration</text>
</svg>

<em>Transaction Flow: Agent → CLI → Storage</em>

</div>


## Artifact Taxonomy

Five layers of epistemic artifacts. Noetic artifacts come from investigation,
epistemic intent captures beliefs and choices, praxic artifacts record actions,
state measurements track progress, and grounded evidence verifies it all.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="653" height="420" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="653" height="420" rx="6"/>
  <defs>
    <clipPath id="d3-bc0"><rect x="20.0" y="20.0" width="221.0" height="176.0" rx="6"/></clipPath>
    <clipPath id="d3-bc1"><rect x="261.0" y="20.0" width="176.0" height="128.0" rx="6"/></clipPath>
    <clipPath id="d3-bc2"><rect x="457.0" y="20.0" width="176.0" height="128.0" rx="6"/></clipPath>
    <clipPath id="d3-bc3"><rect x="20.0" y="216.0" width="194.0" height="144.0" rx="6"/></clipPath>
    <clipPath id="d3-bc4"><rect x="234.0" y="216.0" width="212.0" height="144.0" rx="6"/></clipPath>
  </defs>
  <defs>
    <marker id="d3-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <line class="arrow-line" x1="241.0" y1="108.0" x2="261.0" y2="84.0" marker-end="url(#d3-ah)"/>
  <line class="arrow-line" x1="437.0" y1="84.0" x2="457.0" y2="84.0" marker-end="url(#d3-ah)"/>
  <path class="arrow-line" d="M 545.0,148.0 L 545.0,380.0 L 117.0,380.0 L 117.0,360.0"  marker-end="url(#d3-ah)"/>
  <line class="arrow-line" x1="214.0" y1="288.0" x2="234.0" y2="288.0" marker-end="url(#d3-ah)"/>
  <rect class="box-fill" x="20.0" y="20.0" width="221.0" height="176.0" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="221.0" height="176.0" rx="6"/>
  <g clip-path="url(#d3-bc0)">
    <text class="box-header" x="130.5" y="40.0" text-anchor="middle" dominant-baseline="central">Noetic Artifacts</text>
    <line class="box-separator" x1="20.0" y1="52.0" x2="241.0" y2="52.0"/>
    <text class="box-text" x="32.0" y="74.0">Investigation outputs</text>
    <line class="box-separator" x1="20.0" y1="80.0" x2="241.0" y2="80.0"/>
    <text class="box-text" x="32.0" y="102.0">findings</text>
    <text class="box-text" x="32.0" y="118.0">unknowns</text>
    <text class="box-text" x="32.0" y="134.0">dead-ends</text>
    <text class="box-text" x="32.0" y="150.0">mistakes</text>
    <text class="box-text" x="32.0" y="166.0">blindspots</text>
    <text class="box-text" x="32.0" y="182.0">lessons</text>
  </g>
  <rect class="box-fill" x="261.0" y="20.0" width="176.0" height="128.0" rx="6"/>
  <rect class="box-border" x="261.0" y="20.0" width="176.0" height="128.0" rx="6"/>
  <g clip-path="url(#d3-bc1)">
    <text class="box-header" x="349.0" y="40.0" text-anchor="middle" dominant-baseline="central">Epistemic Intent</text>
    <line class="box-separator" x1="261.0" y1="52.0" x2="437.0" y2="52.0"/>
    <text class="box-text" x="273.0" y="74.0">Intent layer</text>
    <line class="box-separator" x1="261.0" y1="80.0" x2="437.0" y2="80.0"/>
    <text class="box-text" x="273.0" y="102.0">assumptions</text>
    <text class="box-text" x="273.0" y="118.0">decisions</text>
    <text class="box-text" x="273.0" y="134.0">intent edges</text>
  </g>
  <rect class="box-fill" x="457.0" y="20.0" width="176.0" height="128.0" rx="6"/>
  <rect class="box-border" x="457.0" y="20.0" width="176.0" height="128.0" rx="6"/>
  <g clip-path="url(#d3-bc2)">
    <text class="box-header" x="545.0" y="40.0" text-anchor="middle" dominant-baseline="central">Praxic Artifacts</text>
    <line class="box-separator" x1="457.0" y1="52.0" x2="633.0" y2="52.0"/>
    <text class="box-text" x="469.0" y="74.0">Action outputs</text>
    <line class="box-separator" x1="457.0" y1="80.0" x2="633.0" y2="80.0"/>
    <text class="box-text" x="469.0" y="102.0">goals</text>
    <text class="box-text" x="469.0" y="118.0">subtasks</text>
    <text class="box-text" x="469.0" y="134.0">commits</text>
  </g>
  <rect class="box-fill" x="20.0" y="216.0" width="194.0" height="144.0" rx="6"/>
  <rect class="box-border" x="20.0" y="216.0" width="194.0" height="144.0" rx="6"/>
  <g clip-path="url(#d3-bc3)">
    <text class="box-header" x="117.0" y="236.0" text-anchor="middle" dominant-baseline="central">Epistemic State</text>
    <line class="box-separator" x1="20.0" y1="248.0" x2="214.0" y2="248.0"/>
    <text class="box-text" x="32.0" y="270.0">State measurements</text>
    <line class="box-separator" x1="20.0" y1="276.0" x2="214.0" y2="276.0"/>
    <text class="box-text" x="32.0" y="298.0">vectors</text>
    <text class="box-text" x="32.0" y="314.0">calibration</text>
    <text class="box-text" x="32.0" y="330.0">drift</text>
    <text class="box-text" x="32.0" y="346.0">deltas</text>
  </g>
  <rect class="box-fill" x="234.0" y="216.0" width="212.0" height="144.0" rx="6"/>
  <rect class="box-border" x="234.0" y="216.0" width="212.0" height="144.0" rx="6"/>
  <g clip-path="url(#d3-bc4)">
    <text class="box-header" x="340.0" y="236.0" text-anchor="middle" dominant-baseline="central">Grounded Evidence</text>
    <line class="box-separator" x1="234.0" y1="248.0" x2="446.0" y2="248.0"/>
    <text class="box-text" x="246.0" y="270.0">Verification outputs</text>
    <line class="box-separator" x1="234.0" y1="276.0" x2="446.0" y2="276.0"/>
    <text class="box-text" x="246.0" y="298.0">test results</text>
    <text class="box-text" x="246.0" y="314.0">git metrics</text>
    <text class="box-text" x="246.0" y="330.0">goal completion</text>
    <text class="box-text" x="246.0" y="346.0">artifact ratios</text>
  </g>
  <rect class="arrow-label-bg" x="225.4" y="87.0" width="51.2" height="16" rx="3"/>
  <text class="arrow-label" x="251.0" y="96.0" dominant-baseline="central">inform</text>
  <rect class="arrow-label-bg" x="425.0" y="75.0" width="44.0" height="16" rx="3"/>
  <text class="arrow-label" x="447.0" y="84.0" dominant-baseline="central">drive</text>
  <rect class="arrow-label-bg" x="301.8" y="371.0" width="58.4" height="16" rx="3"/>
  <text class="arrow-label" x="331.0" y="380.0" dominant-baseline="central">measure</text>
  <rect class="arrow-label-bg" x="198.4" y="279.0" width="51.2" height="16" rx="3"/>
  <text class="arrow-label" x="224.0" y="288.0" dominant-baseline="central">verify</text>
</svg>

<em>Artifact Taxonomy</em>

</div>


## Dual-Track Calibration

Two independent tracks measure different things. Track 1 (self-referential)
captures learning trajectory via PREFLIGHT→POSTFLIGHT delta. Track 2
(grounded) compares self-assessment against objective evidence. When they
diverge, Track 2 wins.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="308" height="680" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <defs>
    <marker id="d4-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="308" height="680" rx="6"/>
  <line class="arrow-line" x1="153.8" y1="60.0" x2="153.8" y2="120.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="153.8" y1="160.0" x2="153.8" y2="220.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="153.8" y1="260.0" x2="153.8" y2="320.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="153.8" y1="360.0" x2="153.8" y2="420.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="153.8" y1="360.0" x2="153.8" y2="520.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="153.8" y1="460.0" x2="153.8" y2="620.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="153.8" y1="560.0" x2="153.8" y2="620.0" marker-end="url(#d4-ah)"/>
  <rect class="box-fill" x="58.0" y="20.0" width="191.5" height="40.0" rx="6"/>
  <rect class="box-border" x="58.0" y="20.0" width="191.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="43.8" y="120.0" width="220.0" height="40.0" rx="6"/>
  <rect class="box-border" x="43.8" y="120.0" width="220.0" height="40.0" rx="6"/>
  <rect class="box-fill" x="53.2" y="220.0" width="201.0" height="40.0" rx="6"/>
  <rect class="box-border" x="53.2" y="220.0" width="201.0" height="40.0" rx="6"/>
  <polygon class="box-fill" points="153.75,320.0 206.75,340.0 153.75,360.0 100.75,340.0"/>
  <polygon class="box-border" points="153.75,320.0 206.75,340.0 153.75,360.0 100.75,340.0"/>
  <rect class="box-fill" x="20.0" y="420.0" width="267.5" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="420.0" width="267.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="58.0" y="520.0" width="191.5" height="40.0" rx="6"/>
  <rect class="box-border" x="58.0" y="520.0" width="191.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="58.0" y="620.0" width="191.5" height="40.0" rx="6"/>
  <rect class="box-border" x="58.0" y="620.0" width="191.5" height="40.0" rx="6"/>
  <rect class="arrow-label-bg" x="124.5" y="81.0" width="58.4" height="16.0" rx="3"/>
  <text class="arrow-label" x="153.8" y="90.0" dominant-baseline="central">measure</text>
  <rect class="arrow-label-bg" x="128.2" y="181.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="153.8" y="190.0" dominant-baseline="central">assess</text>
  <rect class="arrow-label-bg" x="131.8" y="381.0" width="44.0" height="16.0" rx="3"/>
  <text class="arrow-label" x="153.8" y="390.0" dominant-baseline="central">delta</text>
  <rect class="arrow-label-bg" x="121.0" y="431.0" width="65.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="153.8" y="440.0" dominant-baseline="central">evidence</text>
  <text class="box-header" x="153.8" y="40.0" text-anchor="middle" dominant-baseline="central">PREFLIGHT Vectors</text>
  <text class="box-text" x="153.8" y="140.0" text-anchor="middle" dominant-baseline="central">Noetic + Praxic Work</text>
  <text class="box-text" x="153.8" y="240.0" text-anchor="middle" dominant-baseline="central">POSTFLIGHT Vectors</text>
  <text class="box-text" x="153.8" y="340.0" text-anchor="middle" dominant-baseline="central">Compare?</text>
  <text class="box-text" x="153.8" y="440.0" text-anchor="middle" dominant-baseline="central">Track 1: Self-Referential</text>
  <text class="box-text" x="153.8" y="540.0" text-anchor="middle" dominant-baseline="central">Track 2: Grounded</text>
  <text class="box-text" x="153.8" y="640.0" text-anchor="middle" dominant-baseline="central">Calibration Score</text>
</svg>

<em>Dual-Track Calibration Pipeline</em>

</div>


## Cognitive Immune System

Lessons are antibodies, findings are antigens. When a new finding arrives,
keywords are extracted and matched against existing lessons. Related lessons
have their confidence reduced — but never below 0.3. Lessons never fully die.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="1019" height="278" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <defs>
    <marker id="d5-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <style>
    .mdview-diagram .state-node { stroke: #7aa2f7; stroke-width: 2; fill: #24283b; rx: 20; }
    .mdview-diagram .state-initial { stroke: #7aa2f7; stroke-width: 2.5; }
    .mdview-diagram .state-text { fill: #9ece6a; font-weight: 600; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .state-node { stroke: #2e7de9; fill: #e8e8f0; }
      .mdview-diagram .state-initial { stroke: #2e7de9; }
      .mdview-diagram .state-text { fill: #587539; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="1019" height="278" rx="6"/>
  <line class="arrow-line" x1="435.6" y1="72.0" x2="495.6" y2="72.0" marker-end="url(#d5-ah)"/>
  <line class="arrow-line" x1="697.1" y1="72.0" x2="757.1" y2="72.0" marker-end="url(#d5-ah)"/>
  <line class="arrow-line" x1="757.1" y1="72.0" x2="435.6" y2="196.0" marker-end="url(#d5-ah)"/>
  <line class="arrow-line" x1="435.6" y1="196.0" x2="495.6" y2="196.0" marker-end="url(#d5-ah)"/>
  <path class="arrow-line" d="M 234.1,196.0 C 40.0,134.0 40.0,134.0 757.1,72.0" marker-end="url(#d5-ah)" stroke-dasharray="6,3"/>
  <rect class="state-node state-initial" x="234.1" y="50.0" width="201.5" height="44.0" rx="20"/>
  <rect class="state-node" x="495.6" y="50.0" width="201.5" height="44.0" rx="20"/>
  <rect class="state-node" x="757.1" y="50.0" width="201.5" height="44.0" rx="20"/>
  <rect class="state-node" x="234.1" y="174.0" width="201.5" height="44.0" rx="20"/>
  <rect class="state-node" x="495.6" y="174.0" width="201.5" height="44.0" rx="20"/>
  <rect class="arrow-label-bg" x="422.0" y="63.0" width="87.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="465.6" y="72.0" dominant-baseline="central">new finding</text>
  <rect class="arrow-label-bg" x="694.3" y="63.0" width="65.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="727.1" y="72.0" dominant-baseline="central">keywords</text>
  <rect class="arrow-label-bg" x="538.4" y="125.0" width="116.0" height="16.0" rx="3"/>
  <text class="arrow-label" x="596.4" y="134.0" dominant-baseline="central">related lessons</text>
  <rect class="arrow-label-bg" x="411.2" y="187.0" width="108.8" height="16.0" rx="3"/>
  <text class="arrow-label" x="465.6" y="196.0" dominant-baseline="central">min confidence</text>
  <rect class="arrow-label-bg" x="110.3" y="125.0" width="87.2" height="16" rx="3"/>
  <text class="arrow-label" x="153.9" y="134.0" dominant-baseline="central">next lesson</text>
  <text class="state-text" x="334.9" y="72.0" text-anchor="middle" dominant-baseline="central">Finding</text>
  <text class="state-text" x="596.4" y="72.0" text-anchor="middle" dominant-baseline="central">Extract Keywords</text>
  <text class="state-text" x="857.9" y="72.0" text-anchor="middle" dominant-baseline="central">Match Lessons</text>
  <text class="state-text" x="334.9" y="196.0" text-anchor="middle" dominant-baseline="central">Reduce Confidence</text>
  <text class="state-text" x="596.4" y="196.0" text-anchor="middle" dominant-baseline="central">Floor: 0.3</text>
</svg>

<em>Cognitive Immune System</em>

</div>


## 13 Epistemic Vectors

The state space. Every PREFLIGHT, CHECK, and POSTFLIGHT submits
these 13 vectors on a 0.0–1.0 scale.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="512" height="460" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <style>
    .mdview-diagram .table-header-bg { fill: #24283b; }
    .mdview-diagram .table-cell-bg { fill: none; }
    .mdview-diagram .table-border { stroke: #7aa2f7; stroke-width: 1; fill: none; }
    .mdview-diagram .table-header-text { fill: #9ece6a; font-weight: 600; white-space: pre; }
    .mdview-diagram .table-cell-text { fill: #a9b1d6; white-space: pre; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .table-header-bg { fill: #e8e8f0; }
      .mdview-diagram .table-border { stroke: #2e7de9; }
      .mdview-diagram .table-header-text { fill: #587539; }
      .mdview-diagram .table-cell-text { fill: #343b58; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="512" height="460" rx="6"/>
  <rect class="table-border" x="20" y="20" width="471.6" height="420.0"/>
  <rect class="table-header-bg" x="20" y="20.0" width="471.6" height="30"/>
  <text class="table-header-text" x="84.6" y="35.0" text-anchor="middle" dominant-baseline="central">Category</text>
  <text class="table-header-text" x="205.4" y="35.0" text-anchor="middle" dominant-baseline="central">Vector</text>
  <text class="table-header-text" x="376.6" y="35.0" text-anchor="middle" dominant-baseline="central">Measures</text>
  <line class="table-border" x1="20" y1="50.0" x2="491.6" y2="50.0"/>
  <text class="table-cell-text" x="84.6" y="65.0" text-anchor="middle" dominant-baseline="central">Foundation</text>
  <text class="table-cell-text" x="205.4" y="65.0" text-anchor="middle" dominant-baseline="central">know</text>
  <text class="table-cell-text" x="376.6" y="65.0" text-anchor="middle" dominant-baseline="central">Domain knowledge depth</text>
  <text class="table-cell-text" x="84.6" y="95.0" text-anchor="middle" dominant-baseline="central">Foundation</text>
  <text class="table-cell-text" x="205.4" y="95.0" text-anchor="middle" dominant-baseline="central">do</text>
  <text class="table-cell-text" x="376.6" y="95.0" text-anchor="middle" dominant-baseline="central">Implementation capability</text>
  <text class="table-cell-text" x="84.6" y="125.0" text-anchor="middle" dominant-baseline="central">Foundation</text>
  <text class="table-cell-text" x="205.4" y="125.0" text-anchor="middle" dominant-baseline="central">context</text>
  <text class="table-cell-text" x="376.6" y="125.0" text-anchor="middle" dominant-baseline="central">Situational awareness</text>
  <text class="table-cell-text" x="84.6" y="155.0" text-anchor="middle" dominant-baseline="central">Comprehension</text>
  <text class="table-cell-text" x="205.4" y="155.0" text-anchor="middle" dominant-baseline="central">clarity</text>
  <text class="table-cell-text" x="376.6" y="155.0" text-anchor="middle" dominant-baseline="central">Understanding precision</text>
  <text class="table-cell-text" x="84.6" y="185.0" text-anchor="middle" dominant-baseline="central">Comprehension</text>
  <text class="table-cell-text" x="205.4" y="185.0" text-anchor="middle" dominant-baseline="central">coherence</text>
  <text class="table-cell-text" x="376.6" y="185.0" text-anchor="middle" dominant-baseline="central">Internal consistency</text>
  <text class="table-cell-text" x="84.6" y="215.0" text-anchor="middle" dominant-baseline="central">Comprehension</text>
  <text class="table-cell-text" x="205.4" y="215.0" text-anchor="middle" dominant-baseline="central">signal</text>
  <text class="table-cell-text" x="376.6" y="215.0" text-anchor="middle" dominant-baseline="central">Information relevance</text>
  <text class="table-cell-text" x="84.6" y="245.0" text-anchor="middle" dominant-baseline="central">Comprehension</text>
  <text class="table-cell-text" x="205.4" y="245.0" text-anchor="middle" dominant-baseline="central">density</text>
  <text class="table-cell-text" x="376.6" y="245.0" text-anchor="middle" dominant-baseline="central">Knowledge compactness</text>
  <text class="table-cell-text" x="84.6" y="275.0" text-anchor="middle" dominant-baseline="central">Execution</text>
  <text class="table-cell-text" x="205.4" y="275.0" text-anchor="middle" dominant-baseline="central">state</text>
  <text class="table-cell-text" x="376.6" y="275.0" text-anchor="middle" dominant-baseline="central">System state awareness</text>
  <text class="table-cell-text" x="84.6" y="305.0" text-anchor="middle" dominant-baseline="central">Execution</text>
  <text class="table-cell-text" x="205.4" y="305.0" text-anchor="middle" dominant-baseline="central">change</text>
  <text class="table-cell-text" x="376.6" y="305.0" text-anchor="middle" dominant-baseline="central">Delta from baseline</text>
  <text class="table-cell-text" x="84.6" y="335.0" text-anchor="middle" dominant-baseline="central">Execution</text>
  <text class="table-cell-text" x="205.4" y="335.0" text-anchor="middle" dominant-baseline="central">completion</text>
  <text class="table-cell-text" x="376.6" y="335.0" text-anchor="middle" dominant-baseline="central">Goal progress</text>
  <text class="table-cell-text" x="84.6" y="365.0" text-anchor="middle" dominant-baseline="central">Execution</text>
  <text class="table-cell-text" x="205.4" y="365.0" text-anchor="middle" dominant-baseline="central">impact</text>
  <text class="table-cell-text" x="376.6" y="365.0" text-anchor="middle" dominant-baseline="central">Consequence significance</text>
  <text class="table-cell-text" x="84.6" y="395.0" text-anchor="middle" dominant-baseline="central">Meta</text>
  <text class="table-cell-text" x="205.4" y="395.0" text-anchor="middle" dominant-baseline="central">engagement</text>
  <text class="table-cell-text" x="376.6" y="395.0" text-anchor="middle" dominant-baseline="central">Active participation</text>
  <text class="table-cell-text" x="84.6" y="425.0" text-anchor="middle" dominant-baseline="central">Meta</text>
  <text class="table-cell-text" x="205.4" y="425.0" text-anchor="middle" dominant-baseline="central">uncertainty</text>
  <text class="table-cell-text" x="376.6" y="425.0" text-anchor="middle" dominant-baseline="central">Epistemic humility</text>
  <line class="table-border" x1="149.2" y1="20" x2="149.2" y2="440.0"/>
  <line class="table-border" x1="261.6" y1="20" x2="261.6" y2="440.0"/>
  <line class="table-border" x1="20" y1="50.0" x2="491.6" y2="50.0"/>
  <line class="table-border" x1="20" y1="80.0" x2="491.6" y2="80.0"/>
  <line class="table-border" x1="20" y1="110.0" x2="491.6" y2="110.0"/>
  <line class="table-border" x1="20" y1="140.0" x2="491.6" y2="140.0"/>
  <line class="table-border" x1="20" y1="170.0" x2="491.6" y2="170.0"/>
  <line class="table-border" x1="20" y1="200.0" x2="491.6" y2="200.0"/>
  <line class="table-border" x1="20" y1="230.0" x2="491.6" y2="230.0"/>
  <line class="table-border" x1="20" y1="260.0" x2="491.6" y2="260.0"/>
  <line class="table-border" x1="20" y1="290.0" x2="491.6" y2="290.0"/>
  <line class="table-border" x1="20" y1="320.0" x2="491.6" y2="320.0"/>
  <line class="table-border" x1="20" y1="350.0" x2="491.6" y2="350.0"/>
  <line class="table-border" x1="20" y1="380.0" x2="491.6" y2="380.0"/>
  <line class="table-border" x1="20" y1="410.0" x2="491.6" y2="410.0"/>
</svg>

<em>13 Epistemic Vectors</em>

</div>


## Noetic Firewall

The Sentinel classifies every tool call as noetic (investigation) or praxic
(action). Noetic tools always pass. Praxic tools require a valid CHECK
with `proceed` — preventing action before sufficient understanding.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="760" height="180" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <defs>
    <marker id="d6-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="760" height="180" rx="6"/>
  <line class="arrow-line" x1="135.5" y1="40.0" x2="195.5" y2="40.0" marker-end="url(#d6-ah)"/>
  <line class="arrow-line" x1="387.0" y1="40.0" x2="447.0" y2="40.0" marker-end="url(#d6-ah)"/>
  <line class="arrow-line" x1="387.0" y1="40.0" x2="587.0" y2="40.0" marker-end="url(#d6-ah)"/>
  <line class="arrow-line" x1="587.0" y1="40.0" x2="256.5" y2="140.0" marker-end="url(#d6-ah)"/>
  <line class="arrow-line" x1="587.0" y1="40.0" x2="100.0" y2="140.0" marker-end="url(#d6-ah)"/>
  <line class="arrow-line" x1="447.0" y1="40.0" x2="256.5" y2="140.0" marker-end="url(#d6-ah)"/>
  <rect class="box-fill" x="20.0" y="20.0" width="115.5" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="115.5" height="40.0" rx="6"/>
  <polygon class="box-fill" points="291.25,20.0 387.0,40.0 291.25,60.0 195.5,40.0"/>
  <polygon class="box-border" points="291.25,20.0 387.0,40.0 291.25,60.0 195.5,40.0"/>
  <rect class="box-fill" x="447.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-border" x="447.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <polygon class="box-fill" points="663.75,20.0 740.5,40.0 663.75,60.0 587.0,40.0"/>
  <polygon class="box-border" points="663.75,20.0 740.5,40.0 663.75,60.0 587.0,40.0"/>
  <rect class="box-fill" x="20.0" y="120.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="120.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-fill" x="160.0" y="120.0" width="96.5" height="40.0" rx="6"/>
  <rect class="box-border" x="160.0" y="120.0" width="96.5" height="40.0" rx="6"/>
  <rect class="arrow-label-bg" x="391.4" y="31.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="417.0" y="40.0" dominant-baseline="central">noetic</text>
  <rect class="arrow-label-bg" x="461.4" y="31.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="487.0" y="40.0" dominant-baseline="central">praxic</text>
  <rect class="arrow-label-bg" x="406.9" y="81.0" width="29.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="421.8" y="90.0" dominant-baseline="central">yes</text>
  <rect class="arrow-label-bg" x="332.3" y="81.0" width="22.4" height="16.0" rx="3"/>
  <text class="arrow-label" x="343.5" y="90.0" dominant-baseline="central">no</text>
  <text class="box-header" x="77.8" y="40.0" text-anchor="middle" dominant-baseline="central">Tool Call</text>
  <text class="box-text" x="291.2" y="40.0" text-anchor="middle" dominant-baseline="central">Noetic or Praxic?</text>
  <text class="box-text" x="487.0" y="40.0" text-anchor="middle" dominant-baseline="central">Allow</text>
  <text class="box-text" x="663.8" y="40.0" text-anchor="middle" dominant-baseline="central">CHECK Passed?</text>
  <text class="box-text" x="60.0" y="140.0" text-anchor="middle" dominant-baseline="central">Block</text>
  <text class="box-text" x="208.2" y="140.0" text-anchor="middle" dominant-baseline="central">Execute</text>
</svg>

<em>Noetic Firewall — Sentinel Gate</em>

</div>


## Platform Integration

Empirica works with any AI platform. Integration depth varies by hook support.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="540" height="280" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <style>
    .mdview-diagram .table-header-bg { fill: #24283b; }
    .mdview-diagram .table-cell-bg { fill: none; }
    .mdview-diagram .table-border { stroke: #7aa2f7; stroke-width: 1; fill: none; }
    .mdview-diagram .table-header-text { fill: #9ece6a; font-weight: 600; white-space: pre; }
    .mdview-diagram .table-cell-text { fill: #a9b1d6; white-space: pre; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .table-header-bg { fill: #e8e8f0; }
      .mdview-diagram .table-border { stroke: #2e7de9; }
      .mdview-diagram .table-header-text { fill: #587539; }
      .mdview-diagram .table-cell-text { fill: #343b58; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="540" height="280" rx="6"/>
  <rect class="table-border" x="20" y="20" width="500.0" height="240.0"/>
  <rect class="table-header-bg" x="20" y="20.0" width="500.0" height="30"/>
  <text class="table-header-text" x="76.2" y="35.0" text-anchor="middle" dominant-baseline="central">Platform</text>
  <text class="table-header-text" x="218.0" y="35.0" text-anchor="middle" dominant-baseline="central">Hooks</text>
  <text class="table-header-text" x="351.4" y="35.0" text-anchor="middle" dominant-baseline="central">Sentinel</text>
  <text class="table-header-text" x="459.6" y="35.0" text-anchor="middle" dominant-baseline="central">Status</text>
  <line class="table-border" x1="20" y1="50.0" x2="520.0" y2="50.0"/>
  <text class="table-cell-text" x="76.2" y="65.0" text-anchor="middle" dominant-baseline="central">Claude Code</text>
  <text class="table-cell-text" x="218.0" y="65.0" text-anchor="middle" dominant-baseline="central">Full (10 events)</text>
  <text class="table-cell-text" x="351.4" y="65.0" text-anchor="middle" dominant-baseline="central">Automatic</text>
  <text class="table-cell-text" x="459.6" y="65.0" text-anchor="middle" dominant-baseline="central">Production</text>
  <text class="table-cell-text" x="76.2" y="95.0" text-anchor="middle" dominant-baseline="central">Gemini CLI</text>
  <text class="table-cell-text" x="218.0" y="95.0" text-anchor="middle" dominant-baseline="central">Full (11 events)</text>
  <text class="table-cell-text" x="351.4" y="95.0" text-anchor="middle" dominant-baseline="central">Possible</text>
  <text class="table-cell-text" x="459.6" y="95.0" text-anchor="middle" dominant-baseline="central">Experimental</text>
  <text class="table-cell-text" x="76.2" y="125.0" text-anchor="middle" dominant-baseline="central">Cline</text>
  <text class="table-cell-text" x="218.0" y="125.0" text-anchor="middle" dominant-baseline="central">Full (5 events)</text>
  <text class="table-cell-text" x="351.4" y="125.0" text-anchor="middle" dominant-baseline="central">Possible</text>
  <text class="table-cell-text" x="459.6" y="125.0" text-anchor="middle" dominant-baseline="central">Experimental</text>
  <text class="table-cell-text" x="76.2" y="155.0" text-anchor="middle" dominant-baseline="central">Copilot CLI</text>
  <text class="table-cell-text" x="218.0" y="155.0" text-anchor="middle" dominant-baseline="central">Full (6 events)</text>
  <text class="table-cell-text" x="351.4" y="155.0" text-anchor="middle" dominant-baseline="central">Possible</text>
  <text class="table-cell-text" x="459.6" y="155.0" text-anchor="middle" dominant-baseline="central">Experimental</text>
  <text class="table-cell-text" x="76.2" y="185.0" text-anchor="middle" dominant-baseline="central">Cursor</text>
  <text class="table-cell-text" x="218.0" y="185.0" text-anchor="middle" dominant-baseline="central">Partial (6 events)</text>
  <text class="table-cell-text" x="351.4" y="185.0" text-anchor="middle" dominant-baseline="central">Possible</text>
  <text class="table-cell-text" x="459.6" y="185.0" text-anchor="middle" dominant-baseline="central">Experimental</text>
  <text class="table-cell-text" x="76.2" y="215.0" text-anchor="middle" dominant-baseline="central">Windsurf</text>
  <text class="table-cell-text" x="218.0" y="215.0" text-anchor="middle" dominant-baseline="central">Limited (2)</text>
  <text class="table-cell-text" x="351.4" y="215.0" text-anchor="middle" dominant-baseline="central">None</text>
  <text class="table-cell-text" x="459.6" y="215.0" text-anchor="middle" dominant-baseline="central">Manual</text>
  <text class="table-cell-text" x="76.2" y="245.0" text-anchor="middle" dominant-baseline="central">Aider</text>
  <text class="table-cell-text" x="218.0" y="245.0" text-anchor="middle" dominant-baseline="central">None</text>
  <text class="table-cell-text" x="351.4" y="245.0" text-anchor="middle" dominant-baseline="central">None</text>
  <text class="table-cell-text" x="459.6" y="245.0" text-anchor="middle" dominant-baseline="central">Manual</text>
  <line class="table-border" x1="132.4" y1="20" x2="132.4" y2="260.0"/>
  <line class="table-border" x1="303.6" y1="20" x2="303.6" y2="260.0"/>
  <line class="table-border" x1="399.2" y1="20" x2="399.2" y2="260.0"/>
  <line class="table-border" x1="20" y1="50.0" x2="520.0" y2="50.0"/>
  <line class="table-border" x1="20" y1="80.0" x2="520.0" y2="80.0"/>
  <line class="table-border" x1="20" y1="110.0" x2="520.0" y2="110.0"/>
  <line class="table-border" x1="20" y1="140.0" x2="520.0" y2="140.0"/>
  <line class="table-border" x1="20" y1="170.0" x2="520.0" y2="170.0"/>
  <line class="table-border" x1="20" y1="200.0" x2="520.0" y2="200.0"/>
  <line class="table-border" x1="20" y1="230.0" x2="520.0" y2="230.0"/>
</svg>

<em>Platform Integration Matrix</em>

</div>


## Remote Control Vision

The end state: empirica-autonomy renders live epistemic state via WebSocket.
mdview provides the diagram rendering layer. A companion Android app sits
alongside Claude Chat for mobile oversight.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="520" height="288" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <style>
    .mdview-diagram .wf-panel { stroke: #7aa2f7; stroke-width: 1.5; fill: none; rx: 4; }
    .mdview-diagram .wf-panel-fill { fill: #24283b; fill-opacity: 0.3; rx: 4; }
    .mdview-diagram .wf-title { fill: #9ece6a; font-weight: 600; font-size: 13px; }
    .mdview-diagram .wf-label { fill: #a9b1d6; font-size: 12px; }
    .mdview-diagram .wf-input { stroke: #565f89; stroke-width: 1; fill: none; rx: 3; }
    .mdview-diagram .wf-input-text { fill: #565f89; font-size: 11px; font-style: italic; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .wf-panel { stroke: #2e7de9; }
      .mdview-diagram .wf-panel-fill { fill: #e8e8f0; }
      .mdview-diagram .wf-title { fill: #587539; }
      .mdview-diagram .wf-label { fill: #343b58; }
      .mdview-diagram .wf-input { stroke: #9ca0b0; }
      .mdview-diagram .wf-input-text { fill: #9ca0b0; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="520" height="288" rx="6"/>
  <rect class="wf-panel-fill" x="20.0" y="20.0" width="480.0" height="248.0" style="fill-opacity:0.15"/>
  <rect class="wf-panel" x="20.0" y="20.0" width="480.0" height="248.0"/>
  <text class="wf-title" x="28.0" y="38.0">Remote Control</text>
  <rect class="wf-panel-fill" x="32.0" y="48.0" width="224.0" height="196.0" style="fill-opacity:0.23"/>
  <rect class="wf-panel" x="32.0" y="48.0" width="224.0" height="196.0"/>
  <text class="wf-title" x="40.0" y="66.0">Sessions</text>
  <rect class="wf-panel-fill" x="268.0" y="48.0" width="220.0" height="196.0" style="fill-opacity:0.23"/>
  <rect class="wf-panel" x="268.0" y="48.0" width="220.0" height="196.0"/>
  <text class="wf-title" x="276.0" y="66.0">Live View</text>
  <rect class="wf-panel" x="44.0" y="76.0" width="200.0" height="56.0"/>
  <text class="wf-title" x="52.0" y="94.0">Filter</text>
  <rect class="wf-input" x="52.0" y="102.0" width="184.0" height="24"/>
  <text class="wf-input-text" x="58.0" y="117.0">Search sessions...</text>
  <rect class="wf-panel-fill" x="44.0" y="144.0" width="200.0" height="40.0" style="fill-opacity:0.31"/>
  <rect class="wf-panel" x="44.0" y="144.0" width="200.0" height="40.0"/>
  <text class="wf-title" x="52.0" y="162.0">Active Agents</text>
  <rect class="wf-panel-fill" x="280.0" y="76.0" width="166.0" height="40.0" style="fill-opacity:0.31"/>
  <rect class="wf-panel" x="280.0" y="76.0" width="166.0" height="40.0"/>
  <text class="wf-title" x="288.0" y="94.0">Epistemic Vectors</text>
  <rect class="wf-panel-fill" x="280.0" y="128.0" width="166.0" height="40.0" style="fill-opacity:0.31"/>
  <rect class="wf-panel" x="280.0" y="128.0" width="166.0" height="40.0"/>
  <text class="wf-title" x="288.0" y="146.0">Architecture Map</text>
  <rect class="wf-panel-fill" x="280.0" y="180.0" width="166.0" height="40.0" style="fill-opacity:0.31"/>
  <rect class="wf-panel" x="280.0" y="180.0" width="166.0" height="40.0"/>
  <text class="wf-title" x="288.0" y="198.0">Artifact Stream</text>
</svg>

<em>empirica-autonomy Remote Control Vision</em>

</div>


## Ecosystem

All roads lead back to Empirica. The core CLI provides measurement.
The plugin integrates with coding agents. mdview renders diagrams.
empirica-autonomy provides remote oversight. Plugins in, knowledge out.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="698" height="372" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="698" height="372" rx="6"/>
  <defs>
    <clipPath id="d7-bc0"><rect x="20.0" y="20.0" width="221.0" height="128.0" rx="6"/></clipPath>
    <clipPath id="d7-bc1"><rect x="261.0" y="20.0" width="212.0" height="144.0" rx="6"/></clipPath>
    <clipPath id="d7-bc2"><rect x="493.0" y="20.0" width="185.0" height="128.0" rx="6"/></clipPath>
    <clipPath id="d7-bc3"><rect x="20.0" y="184.0" width="185.0" height="128.0" rx="6"/></clipPath>
  </defs>
  <defs>
    <marker id="d7-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <line class="arrow-line" x1="241.0" y1="84.0" x2="261.0" y2="92.0" marker-end="url(#d7-ah)"/>
  <path class="arrow-line" d="M 130.5,148.0 L 130.5,332.0 L 585.5,332.0 L 585.5,148.0"  marker-end="url(#d7-ah)"/>
  <path class="arrow-line" d="M 112.5,312.0 L 112.5,332.0 L 585.5,332.0 L 585.5,148.0"  marker-end="url(#d7-ah)"/>
  <path class="arrow-line" d="M 367.0,164.0 L 367.0,332.0 L 112.5,332.0 L 112.5,312.0"  marker-end="url(#d7-ah)"/>
  <rect class="box-fill" x="20.0" y="20.0" width="221.0" height="128.0" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="221.0" height="128.0" rx="6"/>
  <g clip-path="url(#d7-bc0)">
    <text class="box-header" x="130.5" y="40.0" text-anchor="middle" dominant-baseline="central">empirica (core)</text>
    <line class="box-separator" x1="20.0" y1="52.0" x2="241.0" y2="52.0"/>
    <text class="box-text" x="32.0" y="74.0">CLI + SQLite + Qdrant</text>
    <line class="box-separator" x1="20.0" y1="80.0" x2="241.0" y2="80.0"/>
    <text class="box-text" x="32.0" y="102.0">Transactions</text>
    <text class="box-text" x="32.0" y="118.0">Calibration</text>
    <text class="box-text" x="32.0" y="134.0">Sentinel</text>
  </g>
  <rect class="box-fill" x="261.0" y="20.0" width="212.0" height="144.0" rx="6"/>
  <rect class="box-border" x="261.0" y="20.0" width="212.0" height="144.0" rx="6"/>
  <g clip-path="url(#d7-bc1)">
    <text class="box-header" x="367.0" y="40.0" text-anchor="middle" dominant-baseline="central">empirica-integration</text>
    <line class="box-separator" x1="261.0" y1="52.0" x2="473.0" y2="52.0"/>
    <text class="box-text" x="273.0" y="74.0">Claude Code Plugin</text>
    <line class="box-separator" x1="261.0" y1="80.0" x2="473.0" y2="80.0"/>
    <text class="box-text" x="273.0" y="102.0">Hooks</text>
    <text class="box-text" x="273.0" y="118.0">Skills</text>
    <text class="box-text" x="273.0" y="134.0">Agents</text>
    <text class="box-text" x="273.0" y="150.0">Commands</text>
  </g>
  <rect class="box-fill" x="493.0" y="20.0" width="185.0" height="128.0" rx="6"/>
  <rect class="box-border" x="493.0" y="20.0" width="185.0" height="128.0" rx="6"/>
  <g clip-path="url(#d7-bc2)">
    <text class="box-header" x="585.5" y="40.0" text-anchor="middle" dominant-baseline="central">empirica-autonomy</text>
    <line class="box-separator" x1="493.0" y1="52.0" x2="678.0" y2="52.0"/>
    <text class="box-text" x="505.0" y="74.0">Remote Oversight</text>
    <line class="box-separator" x1="493.0" y1="80.0" x2="678.0" y2="80.0"/>
    <text class="box-text" x="505.0" y="102.0">WebSocket</text>
    <text class="box-text" x="505.0" y="118.0">Live Dashboard</text>
    <text class="box-text" x="505.0" y="134.0">Android App</text>
  </g>
  <rect class="box-fill" x="20.0" y="184.0" width="185.0" height="128.0" rx="6"/>
  <rect class="box-border" x="20.0" y="184.0" width="185.0" height="128.0" rx="6"/>
  <g clip-path="url(#d7-bc3)">
    <text class="box-header" x="112.5" y="204.0" text-anchor="middle" dominant-baseline="central">mdview</text>
    <line class="box-separator" x1="20.0" y1="216.0" x2="205.0" y2="216.0"/>
    <text class="box-text" x="32.0" y="238.0">Diagram Rendering</text>
    <line class="box-separator" x1="20.0" y1="244.0" x2="205.0" y2="244.0"/>
    <text class="box-text" x="32.0" y="266.0">DiagramSpec</text>
    <text class="box-text" x="32.0" y="282.0">6 SVG Renderers</text>
    <text class="box-text" x="32.0" y="298.0">Themes</text>
  </g>
  <rect class="arrow-label-bg" x="229.0" y="79.0" width="44.0" height="16" rx="3"/>
  <text class="arrow-label" x="251.0" y="88.0" dominant-baseline="central">hooks</text>
  <rect class="arrow-label-bg" x="339.6" y="323.0" width="36.8" height="16" rx="3"/>
  <text class="arrow-label" x="358.0" y="332.0" dominant-baseline="central">data</text>
  <rect class="arrow-label-bg" x="323.4" y="323.0" width="51.2" height="16" rx="3"/>
  <text class="arrow-label" x="349.0" y="332.0" dominant-baseline="central">render</text>
  <rect class="arrow-label-bg" x="221.3" y="323.0" width="36.8" height="16" rx="3"/>
  <text class="arrow-label" x="239.8" y="332.0" dominant-baseline="central">/map</text>
</svg>

<em>Empirica Ecosystem</em>

</div>


## Roadmap

This plan, rendered as a flow diagram. Each step builds on the last:
dogfood the map, write documentation, generalize to a /map skill,
add live WebSocket updates, build remote control, ship mobile.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="212" height="580" style="display:block;margin:auto" class="mdview-diagram">

  <style>
    .mdview-diagram { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', monospace; font-size: 13px; }
    .mdview-diagram .box-fill { fill: #1a1b26; stroke: none; }
    .mdview-diagram .box-border { stroke: #7aa2f7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .box-separator { stroke: #7aa2f7; stroke-width: 1; }
    .mdview-diagram .box-text { fill: #a9b1d6; white-space: pre; }
    .mdview-diagram .box-header { fill: #9ece6a; font-weight: 600; }
    .mdview-diagram .arrow-line { stroke: #bb9af7; stroke-width: 1.5; fill: none; }
    .mdview-diagram .arrow-head { fill: #bb9af7; stroke: none; }
    .mdview-diagram .arrow-label { fill: #e0af68; font-size: 12px; text-anchor: middle; }
    .mdview-diagram .arrow-label-bg { fill: #1a1b26; fill-opacity: 0.85; rx: 3; }
    .mdview-diagram .bg { fill: #1a1b26; }
    @media (prefers-color-scheme: light) {
      .mdview-diagram .box-fill { fill: #f8f8fc; }
      .mdview-diagram .box-border { stroke: #2e7de9; }
      .mdview-diagram .box-separator { stroke: #2e7de9; }
      .mdview-diagram .box-text { fill: #343b58; }
      .mdview-diagram .box-header { fill: #587539; }
      .mdview-diagram .arrow-line { stroke: #7847bd; }
      .mdview-diagram .arrow-head { fill: #7847bd; }
      .mdview-diagram .arrow-label { fill: #8c6c3e; }
      .mdview-diagram .arrow-label-bg { fill: #f8f8fc; fill-opacity: 0.85; }
      .mdview-diagram .bg { fill: #f8f8fc; }
    }
  </style>
  <defs>
    <marker id="d8-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="212" height="580" rx="6"/>
  <line class="arrow-line" x1="106.2" y1="60.0" x2="106.2" y2="120.0" marker-end="url(#d8-ah)"/>
  <line class="arrow-line" x1="106.2" y1="160.0" x2="106.2" y2="220.0" marker-end="url(#d8-ah)"/>
  <line class="arrow-line" x1="106.2" y1="260.0" x2="106.2" y2="320.0" marker-end="url(#d8-ah)"/>
  <line class="arrow-line" x1="106.2" y1="360.0" x2="106.2" y2="420.0" marker-end="url(#d8-ah)"/>
  <line class="arrow-line" x1="106.2" y1="460.0" x2="106.2" y2="520.0" marker-end="url(#d8-ah)"/>
  <rect class="box-fill" x="34.2" y="20.0" width="144.0" height="40.0" rx="6"/>
  <rect class="box-border" x="34.2" y="20.0" width="144.0" height="40.0" rx="6"/>
  <rect class="box-fill" x="29.5" y="120.0" width="153.5" height="40.0" rx="6"/>
  <rect class="box-border" x="29.5" y="120.0" width="153.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="43.8" y="220.0" width="125.0" height="40.0" rx="6"/>
  <rect class="box-border" x="43.8" y="220.0" width="125.0" height="40.0" rx="6"/>
  <rect class="box-fill" x="20.0" y="320.0" width="172.5" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="320.0" width="172.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="20.0" y="420.0" width="172.5" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="420.0" width="172.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="39.0" y="520.0" width="134.5" height="40.0" rx="6"/>
  <rect class="box-border" x="39.0" y="520.0" width="134.5" height="40.0" rx="6"/>
  <rect class="arrow-label-bg" x="77.0" y="81.0" width="58.4" height="16.0" rx="3"/>
  <text class="arrow-label" x="106.2" y="90.0" dominant-baseline="central">dogfood</text>
  <rect class="arrow-label-bg" x="66.2" y="181.0" width="80.0" height="16.0" rx="3"/>
  <text class="arrow-label" x="106.2" y="190.0" dominant-baseline="central">generalize</text>
  <rect class="arrow-label-bg" x="59.0" y="281.0" width="94.4" height="16.0" rx="3"/>
  <text class="arrow-label" x="106.2" y="290.0" dominant-baseline="central">live updates</text>
  <rect class="arrow-label-bg" x="69.8" y="381.0" width="72.8" height="16.0" rx="3"/>
  <text class="arrow-label" x="106.2" y="390.0" dominant-baseline="central">oversight</text>
  <rect class="arrow-label-bg" x="80.7" y="481.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="106.2" y="490.0" dominant-baseline="central">mobile</text>
  <text class="box-header" x="106.2" y="40.0" text-anchor="middle" dominant-baseline="central">Empirica Map</text>
  <text class="box-text" x="106.2" y="140.0" text-anchor="middle" dominant-baseline="central">Documentation</text>
  <text class="box-text" x="106.2" y="240.0" text-anchor="middle" dominant-baseline="central">/map Skill</text>
  <text class="box-text" x="106.2" y="340.0" text-anchor="middle" dominant-baseline="central">WebSocket Layer</text>
  <text class="box-text" x="106.2" y="440.0" text-anchor="middle" dominant-baseline="central">/remote-control</text>
  <text class="box-text" x="106.2" y="540.0" text-anchor="middle" dominant-baseline="central">Android App</text>
</svg>

<em>This Plan — Epistemic Map of mdview Roadmap</em>

</div>


---

*Every diagram in this document is rendered by mdview's spec-based pipeline.
This is the system documenting itself — epistemic infrastructure all the way down.*
