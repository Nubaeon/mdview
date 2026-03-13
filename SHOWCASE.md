# mdview Diagram Showcase

> Demonstrating all 6 diagram types with realistic engineering scenarios.
> Every diagram is a `DiagramSpec` rendered to themed SVG with dark/light support.

---

## 1. CI/CD Pipeline

A typical GitHub Actions pipeline with lint, test, build gates and manual approval.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="680" height="180" style="display:block;margin:auto" class="mdview-diagram">

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
  <rect class="bg" x="0" y="0" width="680" height="180" rx="6"/>
  <line class="arrow-line" x1="100.0" y1="40.0" x2="160.0" y2="40.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="240.0" y1="40.0" x2="300.0" y2="40.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="380.0" y1="40.0" x2="440.0" y2="40.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="520.0" y1="40.0" x2="580.0" y2="40.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="580.0" y1="40.0" x2="116.5" y2="140.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="116.5" y1="140.0" x2="176.5" y2="140.0" marker-end="url(#d0-ah)"/>
  <line class="arrow-line" x1="282.5" y1="140.0" x2="342.5" y2="140.0" marker-end="url(#d0-ah)"/>
  <rect class="box-fill" x="20.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-fill" x="160.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-border" x="160.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-fill" x="300.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-border" x="300.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-fill" x="440.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <rect class="box-border" x="440.0" y="20.0" width="80.0" height="40.0" rx="6"/>
  <polygon class="box-fill" points="620.0,20.0 660.0,40.0 620.0,60.0 580.0,40.0"/>
  <polygon class="box-border" points="620.0,20.0 660.0,40.0 620.0,60.0 580.0,40.0"/>
  <rect class="box-fill" x="20.0" y="120.0" width="96.5" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="120.0" width="96.5" height="40.0" rx="6"/>
  <polygon class="box-fill" points="229.5,120.0 282.5,140.0 229.5,160.0 176.5,140.0"/>
  <polygon class="box-border" points="229.5,120.0 282.5,140.0 229.5,160.0 176.5,140.0"/>
  <rect class="box-fill" x="342.5" y="120.0" width="125.0" height="40.0" rx="6"/>
  <rect class="box-border" x="342.5" y="120.0" width="125.0" height="40.0" rx="6"/>
  <rect class="arrow-label-bg" x="88.8" y="31.0" width="58.4" height="16.0" rx="3"/>
  <text class="arrow-label" x="118.0" y="40.0" dominant-baseline="central">trigger</text>
  <rect class="arrow-label-bg" x="426.2" y="61.0" width="29.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="441.0" y="70.0" dominant-baseline="central">yes</text>
  <rect class="arrow-label-bg" x="285.7" y="131.0" width="29.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="300.5" y="140.0" dominant-baseline="central">yes</text>
  <text class="box-header" x="60.0" y="40.0" text-anchor="middle" dominant-baseline="central">Push</text>
  <text class="box-text" x="200.0" y="40.0" text-anchor="middle" dominant-baseline="central">Lint</text>
  <text class="box-text" x="340.0" y="40.0" text-anchor="middle" dominant-baseline="central">Test</text>
  <text class="box-text" x="480.0" y="40.0" text-anchor="middle" dominant-baseline="central">Build</text>
  <text class="box-text" x="620.0" y="40.0" text-anchor="middle" dominant-baseline="central">Pass?</text>
  <text class="box-text" x="68.2" y="140.0" text-anchor="middle" dominant-baseline="central">Staging</text>
  <text class="box-text" x="229.5" y="140.0" text-anchor="middle" dominant-baseline="central">Approve?</text>
  <text class="box-text" x="405.0" y="140.0" text-anchor="middle" dominant-baseline="central">Production</text>
</svg>

<em>GitHub Actions CI/CD Pipeline</em>

</div>


## 2. RAG Pipeline

Retrieval-Augmented Generation flow — from user query to LLM response.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="194" height="680" style="display:block;margin:auto" class="mdview-diagram">

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
    <marker id="d1-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <rect class="bg" x="0" y="0" width="194" height="680" rx="6"/>
  <line class="arrow-line" x1="96.8" y1="60.0" x2="96.8" y2="120.0" marker-end="url(#d1-ah)"/>
  <line class="arrow-line" x1="96.8" y1="160.0" x2="96.8" y2="220.0" marker-end="url(#d1-ah)"/>
  <line class="arrow-line" x1="96.8" y1="260.0" x2="96.8" y2="320.0" marker-end="url(#d1-ah)"/>
  <line class="arrow-line" x1="96.8" y1="360.0" x2="96.8" y2="420.0" marker-end="url(#d1-ah)"/>
  <line class="arrow-line" x1="96.8" y1="460.0" x2="96.8" y2="520.0" marker-end="url(#d1-ah)"/>
  <line class="arrow-line" x1="96.8" y1="560.0" x2="96.8" y2="620.0" marker-end="url(#d1-ah)"/>
  <rect class="box-fill" x="34.2" y="20.0" width="125.0" height="40.0" rx="6"/>
  <rect class="box-border" x="34.2" y="20.0" width="125.0" height="40.0" rx="6"/>
  <rect class="box-fill" x="29.5" y="120.0" width="134.5" height="40.0" rx="6"/>
  <rect class="box-border" x="29.5" y="120.0" width="134.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="20.0" y="220.0" width="153.5" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="220.0" width="153.5" height="40.0" rx="6"/>
  <polygon class="box-fill" points="96.75,320.0 140.25,340.0 96.75,360.0 53.25,340.0"/>
  <polygon class="box-border" points="96.75,320.0 140.25,340.0 96.75,360.0 53.25,340.0"/>
  <rect class="box-fill" x="20.0" y="420.0" width="153.5" height="40.0" rx="6"/>
  <rect class="box-border" x="20.0" y="420.0" width="153.5" height="40.0" rx="6"/>
  <rect class="box-fill" x="24.8" y="520.0" width="144.0" height="40.0" rx="6"/>
  <rect class="box-border" x="24.8" y="520.0" width="144.0" height="40.0" rx="6"/>
  <rect class="box-fill" x="43.8" y="620.0" width="106.0" height="40.0" rx="6"/>
  <rect class="box-border" x="43.8" y="620.0" width="106.0" height="40.0" rx="6"/>
  <rect class="arrow-label-bg" x="78.3" y="169.0" width="36.8" height="16.0" rx="3"/>
  <text class="arrow-label" x="96.8" y="178.0" dominant-baseline="central">k-NN</text>
  <rect class="arrow-label-bg" x="74.8" y="369.0" width="44.0" height="16.0" rx="3"/>
  <text class="arrow-label" x="96.8" y="378.0" dominant-baseline="central">top-k</text>
  <rect class="arrow-label-bg" x="71.2" y="469.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="96.8" y="478.0" dominant-baseline="central">prompt</text>
  <text class="box-header" x="96.8" y="40.0" text-anchor="middle" dominant-baseline="central">User Query</text>
  <text class="box-text" x="96.8" y="140.0" text-anchor="middle" dominant-baseline="central">Embed Query</text>
  <text class="box-text" x="96.8" y="240.0" text-anchor="middle" dominant-baseline="central">Vector Search</text>
  <text class="box-text" x="96.8" y="340.0" text-anchor="middle" dominant-baseline="central">Rerank</text>
  <text class="box-text" x="96.8" y="440.0" text-anchor="middle" dominant-baseline="central">Build Context</text>
  <text class="box-text" x="96.8" y="540.0" text-anchor="middle" dominant-baseline="central">LLM Generate</text>
  <text class="box-text" x="96.8" y="640.0" text-anchor="middle" dominant-baseline="central">Response</text>
</svg>

<em>RAG Pipeline</em>

</div>


## 3. OAuth2 Authorization Flow

Full OAuth2 authorization code flow with browser, app server, auth provider, and resource API.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="794" height="468" style="display:block;margin:auto" class="mdview-diagram">
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
  <rect class="bg" x="0" y="0" width="794" height="468" rx="6"/>
  <rect class="actor-box" x="40.0" y="20" width="141.0" height="32" rx="4"/>
  <text class="actor-text" x="110.5" y="36.0">Browser</text>
  <rect class="actor-box" x="40.0" y="416" width="141.0" height="32" rx="4"/>
  <text class="actor-text" x="110.5" y="432.0">Browser</text>
  <rect class="actor-box" x="231.0" y="20" width="141.0" height="32" rx="4"/>
  <text class="actor-text" x="301.5" y="36.0">App Server</text>
  <rect class="actor-box" x="231.0" y="416" width="141.0" height="32" rx="4"/>
  <text class="actor-text" x="301.5" y="432.0">App Server</text>
  <rect class="actor-box" x="422.0" y="20" width="141.0" height="32" rx="4"/>
  <text class="actor-text" x="492.5" y="36.0">Auth Provider</text>
  <rect class="actor-box" x="422.0" y="416" width="141.0" height="32" rx="4"/>
  <text class="actor-text" x="492.5" y="432.0">Auth Provider</text>
  <rect class="actor-box" x="613.0" y="20" width="141.0" height="32" rx="4"/>
  <text class="actor-text" x="683.5" y="36.0">Resource API</text>
  <rect class="actor-box" x="613.0" y="416" width="141.0" height="32" rx="4"/>
  <text class="actor-text" x="683.5" y="432.0">Resource API</text>
  <line class="lifeline" x1="110.5" y1="64" x2="110.5" y2="404"/>
  <line class="lifeline" x1="301.5" y1="64" x2="301.5" y2="404"/>
  <line class="lifeline" x1="492.5" y1="64" x2="492.5" y2="404"/>
  <line class="lifeline" x1="683.5" y1="64" x2="683.5" y2="404"/>
  <line class="msg-line" x1="110.5" y1="80.0" x2="301.5" y2="80.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="206.0" y="72.0">GET /login</text>
  <line class="msg-line" x1="110.5" y1="112.0" x2="301.5" y2="112.0" stroke-dasharray="6,3" marker-start="url(#d2-sa)"/>
  <text class="msg-label" x="206.0" y="104.0">redirect to auth</text>
  <line class="msg-line" x1="110.5" y1="144.0" x2="492.5" y2="144.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="301.5" y="136.0">authorize</text>
  <line class="msg-line" x1="110.5" y1="176.0" x2="492.5" y2="176.0" stroke-dasharray="6,3" marker-start="url(#d2-sa)"/>
  <text class="msg-label" x="301.5" y="168.0">code</text>
  <line class="msg-line" x1="110.5" y1="208.0" x2="301.5" y2="208.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="206.0" y="200.0">callback + code</text>
  <line class="msg-line" x1="301.5" y1="240.0" x2="492.5" y2="240.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="397.0" y="232.0">exchange code</text>
  <line class="msg-line" x1="301.5" y1="272.0" x2="492.5" y2="272.0" stroke-dasharray="6,3" marker-start="url(#d2-sa)"/>
  <text class="msg-label" x="397.0" y="264.0">access_token</text>
  <line class="msg-line" x1="301.5" y1="304.0" x2="683.5" y2="304.0" marker-end="url(#d2-sa)"/>
  <text class="msg-label" x="492.5" y="296.0">GET /data + token</text>
  <line class="msg-line" x1="301.5" y1="336.0" x2="683.5" y2="336.0" stroke-dasharray="6,3" marker-start="url(#d2-sa)"/>
  <text class="msg-label" x="492.5" y="328.0">JSON response</text>
  <line class="msg-line" x1="110.5" y1="368.0" x2="301.5" y2="368.0" stroke-dasharray="6,3" marker-start="url(#d2-sa)"/>
  <text class="msg-label" x="206.0" y="360.0">render page</text>
</svg>

<em>OAuth2 Authorization Code Flow</em>

</div>


## 4. Admin Dashboard Wireframe

Nested UI wireframe with sidebar navigation, toolbar, and content areas.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="548" height="356" style="display:block;margin:auto" class="mdview-diagram">

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
  <rect class="bg" x="0" y="0" width="548" height="356" rx="6"/>
  <rect class="wf-panel-fill" x="20.0" y="20.0" width="508.0" height="316.0" style="fill-opacity:0.15"/>
  <rect class="wf-panel" x="20.0" y="20.0" width="508.0" height="316.0"/>
  <text class="wf-title" x="28.0" y="38.0">Dashboard</text>
  <rect class="wf-panel-fill" x="32.0" y="48.0" width="224.0" height="264.0" style="fill-opacity:0.23"/>
  <rect class="wf-panel" x="32.0" y="48.0" width="224.0" height="264.0"/>
  <text class="wf-title" x="40.0" y="66.0">Navigation</text>
  <rect class="wf-panel-fill" x="268.0" y="48.0" width="248.0" height="264.0" style="fill-opacity:0.23"/>
  <rect class="wf-panel" x="268.0" y="48.0" width="248.0" height="264.0"/>
  <text class="wf-title" x="276.0" y="66.0">Content</text>
  <rect class="wf-panel" x="44.0" y="76.0" width="200.0" height="56.0"/>
  <text class="wf-title" x="52.0" y="94.0">Search</text>
  <rect class="wf-input" x="52.0" y="102.0" width="184.0" height="24"/>
  <text class="wf-input-text" x="58.0" y="117.0">Search...</text>
  <rect class="wf-panel-fill" x="44.0" y="144.0" width="200.0" height="40.0" style="fill-opacity:0.31"/>
  <rect class="wf-panel" x="44.0" y="144.0" width="200.0" height="40.0"/>
  <text class="wf-title" x="52.0" y="162.0">Menu Items</text>
  <rect class="wf-panel-fill" x="280.0" y="76.0" width="224.0" height="108.0" style="fill-opacity:0.31"/>
  <rect class="wf-panel" x="280.0" y="76.0" width="224.0" height="108.0"/>
  <text class="wf-title" x="288.0" y="94.0">Actions</text>
  <rect class="wf-panel-fill" x="280.0" y="196.0" width="224.0" height="40.0" style="fill-opacity:0.31"/>
  <rect class="wf-panel" x="280.0" y="196.0" width="224.0" height="40.0"/>
  <text class="wf-title" x="288.0" y="214.0">Metrics</text>
  <rect class="wf-panel-fill" x="280.0" y="248.0" width="224.0" height="40.0" style="fill-opacity:0.31"/>
  <rect class="wf-panel" x="280.0" y="248.0" width="224.0" height="40.0"/>
  <text class="wf-title" x="288.0" y="266.0">Data Table</text>
  <rect class="wf-panel" x="292.0" y="104.0" width="200.0" height="56.0"/>
  <text class="wf-title" x="300.0" y="122.0">Filter</text>
  <rect class="wf-input" x="300.0" y="130.0" width="184.0" height="24"/>
  <text class="wf-input-text" x="306.0" y="145.0">Filter results...</text>
</svg>

<em>Admin Dashboard Wireframe</em>

</div>


## 5. Microservice Architecture

Service decomposition with API gateway, domain services, and data stores.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="572" height="356" style="display:block;margin:auto" class="mdview-diagram">

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
  <rect class="bg" x="0" y="0" width="572" height="356" rx="6"/>
  <defs>
    <clipPath id="d3-bc0"><rect x="20.0" y="20.0" width="167.0" height="100.0" rx="6"/></clipPath>
    <clipPath id="d3-bc1"><rect x="207.0" y="20.0" width="158.0" height="128.0" rx="6"/></clipPath>
    <clipPath id="d3-bc2"><rect x="385.0" y="20.0" width="167.0" height="112.0" rx="6"/></clipPath>
    <clipPath id="d3-bc3"><rect x="20.0" y="168.0" width="212.0" height="128.0" rx="6"/></clipPath>
  </defs>
  <defs>
    <marker id="d3-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <line class="arrow-line" x1="187.0" y1="70.0" x2="207.0" y2="84.0" marker-end="url(#d3-ah)"/>
  <path class="arrow-line" d="M 103.5,120.0 L 103.5,316.0 L 468.5,316.0 L 468.5,132.0"  marker-end="url(#d3-ah)"/>
  <path class="arrow-line" d="M 468.5,132.0 L 468.5,316.0 L 126.0,316.0 L 126.0,296.0"  marker-end="url(#d3-ah)"/>
  <rect class="box-fill" x="20.0" y="20.0" width="167.0" height="100.0" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="167.0" height="100.0" rx="6"/>
  <g clip-path="url(#d3-bc0)">
    <text class="box-header" x="103.5" y="40.0" text-anchor="middle" dominant-baseline="central">API Gateway</text>
    <line class="box-separator" x1="20.0" y1="52.0" x2="187.0" y2="52.0"/>
    <text class="box-text" x="32.0" y="74.0">Rate limiting</text>
    <text class="box-text" x="32.0" y="90.0">Auth middleware</text>
    <text class="box-text" x="32.0" y="106.0">Request routing</text>
  </g>
  <rect class="box-fill" x="207.0" y="20.0" width="158.0" height="128.0" rx="6"/>
  <rect class="box-border" x="207.0" y="20.0" width="158.0" height="128.0" rx="6"/>
  <g clip-path="url(#d3-bc1)">
    <text class="box-header" x="286.0" y="40.0" text-anchor="middle" dominant-baseline="central">User Service</text>
    <line class="box-separator" x1="207.0" y1="52.0" x2="365.0" y2="52.0"/>
    <text class="box-text" x="219.0" y="74.0">GET /users</text>
    <text class="box-text" x="219.0" y="90.0">POST /users</text>
    <text class="box-text" x="219.0" y="106.0">PUT /users/:id</text>
    <line class="box-separator" x1="207.0" y1="112.0" x2="365.0" y2="112.0"/>
    <text class="box-text" x="219.0" y="134.0">PostgreSQL</text>
  </g>
  <rect class="box-fill" x="385.0" y="20.0" width="167.0" height="112.0" rx="6"/>
  <rect class="box-border" x="385.0" y="20.0" width="167.0" height="112.0" rx="6"/>
  <g clip-path="url(#d3-bc2)">
    <text class="box-header" x="468.5" y="40.0" text-anchor="middle" dominant-baseline="central">Order Service</text>
    <line class="box-separator" x1="385.0" y1="52.0" x2="552.0" y2="52.0"/>
    <text class="box-text" x="397.0" y="74.0">POST /orders</text>
    <text class="box-text" x="397.0" y="90.0">GET /orders/:id</text>
    <line class="box-separator" x1="385.0" y1="96.0" x2="552.0" y2="96.0"/>
    <text class="box-text" x="397.0" y="118.0">MongoDB</text>
  </g>
  <rect class="box-fill" x="20.0" y="168.0" width="212.0" height="128.0" rx="6"/>
  <rect class="box-border" x="20.0" y="168.0" width="212.0" height="128.0" rx="6"/>
  <g clip-path="url(#d3-bc3)">
    <text class="box-header" x="126.0" y="188.0" text-anchor="middle" dominant-baseline="central">Notification Service</text>
    <line class="box-separator" x1="20.0" y1="200.0" x2="232.0" y2="200.0"/>
    <text class="box-text" x="32.0" y="222.0">Email</text>
    <text class="box-text" x="32.0" y="238.0">SMS</text>
    <text class="box-text" x="32.0" y="254.0">Push</text>
    <line class="box-separator" x1="20.0" y1="260.0" x2="232.0" y2="260.0"/>
    <text class="box-text" x="32.0" y="282.0">Redis queue</text>
  </g>
  <rect class="arrow-label-bg" x="178.6" y="68.0" width="36.8" height="16" rx="3"/>
  <text class="arrow-label" x="197.0" y="77.0" dominant-baseline="central">REST</text>
  <rect class="arrow-label-bg" x="267.6" y="293.0" width="36.8" height="16" rx="3"/>
  <text class="arrow-label" x="286.0" y="302.0" dominant-baseline="central">REST</text>
  <rect class="arrow-label-bg" x="271.6" y="293.0" width="51.2" height="16" rx="3"/>
  <text class="arrow-label" x="297.2" y="302.0" dominant-baseline="central">events</text>
</svg>

<em>Microservice Architecture</em>

</div>


## 6. Deployment Lifecycle

State machine showing deployment progression with rollback and retry paths.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="887" height="278" style="display:block;margin:auto" class="mdview-diagram">

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
  <rect class="bg" x="0" y="0" width="887" height="278" rx="6"/>
  <line class="arrow-line" x1="298.8" y1="72.0" x2="358.8" y2="72.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="474.8" y1="72.0" x2="534.8" y2="72.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="650.8" y1="72.0" x2="710.8" y2="72.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="592.8" y1="94.0" x2="592.8" y2="174.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="710.8" y1="72.0" x2="298.8" y2="196.0" marker-end="url(#d4-ah)"/>
  <line class="arrow-line" x1="298.8" y1="196.0" x2="358.8" y2="196.0" marker-end="url(#d4-ah)"/>
  <path class="arrow-line" d="M 358.8,196.0 C 216.0,134.0 216.0,134.0 710.8,72.0" marker-end="url(#d4-ah)" stroke-dasharray="6,3"/>
  <path class="arrow-line" d="M 534.8,196.0 C 40.0,134.0 40.0,134.0 182.8,72.0" marker-end="url(#d4-ah)" stroke-dasharray="6,3"/>
  <rect class="state-node state-initial" x="182.8" y="50.0" width="116.0" height="44.0" rx="20"/>
  <rect class="state-node" x="358.8" y="50.0" width="116.0" height="44.0" rx="20"/>
  <rect class="state-node" x="534.8" y="50.0" width="116.0" height="44.0" rx="20"/>
  <rect class="state-node" x="710.8" y="50.0" width="116.0" height="44.0" rx="20"/>
  <rect class="state-node" x="182.8" y="174.0" width="116.0" height="44.0" rx="20"/>
  <rect class="state-node" x="358.8" y="174.0" width="116.0" height="44.0" rx="20"/>
  <rect class="state-node" x="534.8" y="174.0" width="116.0" height="44.0" rx="20"/>
  <rect class="arrow-label-bg" x="294.8" y="63.0" width="44.0" height="16.0" rx="3"/>
  <text class="arrow-label" x="316.8" y="72.0" dominant-baseline="central">start</text>
  <rect class="arrow-label-bg" x="470.8" y="63.0" width="44.0" height="16.0" rx="3"/>
  <text class="arrow-label" x="492.8" y="72.0" dominant-baseline="central">built</text>
  <rect class="arrow-label-bg" x="643.2" y="63.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="668.8" y="72.0" dominant-baseline="central">passed</text>
  <rect class="arrow-label-bg" x="567.2" y="109.0" width="51.2" height="16.0" rx="3"/>
  <text class="arrow-label" x="592.8" y="118.0" dominant-baseline="central">failed</text>
  <rect class="arrow-label-bg" x="558.0" y="100.2" width="58.4" height="16.0" rx="3"/>
  <text class="arrow-label" x="587.2" y="109.2" dominant-baseline="central">promote</text>
  <rect class="arrow-label-bg" x="294.8" y="187.0" width="44.0" height="16.0" rx="3"/>
  <text class="arrow-label" x="316.8" y="196.0" dominant-baseline="central">issue</text>
  <rect class="arrow-label-bg" x="262.9" y="125.0" width="65.6" height="16" rx="3"/>
  <text class="arrow-label" x="295.7" y="134.0" dominant-baseline="central">reverted</text>
  <rect class="arrow-label-bg" x="97.7" y="125.0" width="44.0" height="16" rx="3"/>
  <text class="arrow-label" x="119.7" y="134.0" dominant-baseline="central">retry</text>
  <text class="state-text" x="240.8" y="72.0" text-anchor="middle" dominant-baseline="central">Pending</text>
  <text class="state-text" x="416.8" y="72.0" text-anchor="middle" dominant-baseline="central">Building</text>
  <text class="state-text" x="592.8" y="72.0" text-anchor="middle" dominant-baseline="central">Testing</text>
  <text class="state-text" x="768.8" y="72.0" text-anchor="middle" dominant-baseline="central">Staging</text>
  <text class="state-text" x="240.8" y="196.0" text-anchor="middle" dominant-baseline="central">Live</text>
  <text class="state-text" x="416.8" y="196.0" text-anchor="middle" dominant-baseline="central">Rollback</text>
  <text class="state-text" x="592.8" y="196.0" text-anchor="middle" dominant-baseline="central">Failed</text>
</svg>

<em>Deployment Lifecycle</em>

</div>


## 7. REST API Reference

API endpoint documentation as a styled table.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="456" height="220" style="display:block;margin:auto" class="mdview-diagram">

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
  <rect class="bg" x="0" y="0" width="456" height="220" rx="6"/>
  <rect class="table-border" x="20" y="20" width="416.0" height="180.0"/>
  <rect class="table-header-bg" x="20" y="20.0" width="416.0" height="30"/>
  <text class="table-header-text" x="55.2" y="35.0" text-anchor="middle" dominant-baseline="central">Method</text>
  <text class="table-header-text" x="163.4" y="35.0" text-anchor="middle" dominant-baseline="central">Endpoint</text>
  <text class="table-header-text" x="267.4" y="35.0" text-anchor="middle" dominant-baseline="central">Auth</text>
  <text class="table-header-text" x="367.2" y="35.0" text-anchor="middle" dominant-baseline="central">Description</text>
  <line class="table-border" x1="20" y1="50.0" x2="436.0" y2="50.0"/>
  <text class="table-cell-text" x="55.2" y="65.0" text-anchor="middle" dominant-baseline="central">GET</text>
  <text class="table-cell-text" x="163.4" y="65.0" text-anchor="middle" dominant-baseline="central">/api/users</text>
  <text class="table-cell-text" x="267.4" y="65.0" text-anchor="middle" dominant-baseline="central">JWT</text>
  <text class="table-cell-text" x="367.2" y="65.0" text-anchor="middle" dominant-baseline="central">List all users</text>
  <text class="table-cell-text" x="55.2" y="95.0" text-anchor="middle" dominant-baseline="central">POST</text>
  <text class="table-cell-text" x="163.4" y="95.0" text-anchor="middle" dominant-baseline="central">/api/users</text>
  <text class="table-cell-text" x="267.4" y="95.0" text-anchor="middle" dominant-baseline="central">Admin</text>
  <text class="table-cell-text" x="367.2" y="95.0" text-anchor="middle" dominant-baseline="central">Create user</text>
  <text class="table-cell-text" x="55.2" y="125.0" text-anchor="middle" dominant-baseline="central">GET</text>
  <text class="table-cell-text" x="163.4" y="125.0" text-anchor="middle" dominant-baseline="central">/api/orders</text>
  <text class="table-cell-text" x="267.4" y="125.0" text-anchor="middle" dominant-baseline="central">JWT</text>
  <text class="table-cell-text" x="367.2" y="125.0" text-anchor="middle" dominant-baseline="central">List orders</text>
  <text class="table-cell-text" x="55.2" y="155.0" text-anchor="middle" dominant-baseline="central">POST</text>
  <text class="table-cell-text" x="163.4" y="155.0" text-anchor="middle" dominant-baseline="central">/api/orders</text>
  <text class="table-cell-text" x="267.4" y="155.0" text-anchor="middle" dominant-baseline="central">JWT</text>
  <text class="table-cell-text" x="367.2" y="155.0" text-anchor="middle" dominant-baseline="central">Create order</text>
  <text class="table-cell-text" x="55.2" y="185.0" text-anchor="middle" dominant-baseline="central">DELETE</text>
  <text class="table-cell-text" x="163.4" y="185.0" text-anchor="middle" dominant-baseline="central">/api/orders/:id</text>
  <text class="table-cell-text" x="267.4" y="185.0" text-anchor="middle" dominant-baseline="central">Admin</text>
  <text class="table-cell-text" x="367.2" y="185.0" text-anchor="middle" dominant-baseline="central">Cancel order</text>
  <line class="table-border" x1="90.4" y1="20" x2="90.4" y2="200.0"/>
  <line class="table-border" x1="236.4" y1="20" x2="236.4" y2="200.0"/>
  <line class="table-border" x1="298.4" y1="20" x2="298.4" y2="200.0"/>
  <line class="table-border" x1="20" y1="50.0" x2="436.0" y2="50.0"/>
  <line class="table-border" x1="20" y1="80.0" x2="436.0" y2="80.0"/>
  <line class="table-border" x1="20" y1="110.0" x2="436.0" y2="110.0"/>
  <line class="table-border" x1="20" y1="140.0" x2="436.0" y2="140.0"/>
  <line class="table-border" x1="20" y1="170.0" x2="436.0" y2="170.0"/>
</svg>

<em>REST API Endpoints</em>

</div>


## 8. LLM Agent Loop

Think-Act-Observe cycle with self-loop reasoning and iteration back-edges.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="716" height="278" style="display:block;margin:auto" class="mdview-diagram">

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
  <rect class="bg" x="0" y="0" width="716" height="278" rx="6"/>
  <line class="arrow-line" x1="156.5" y1="72.0" x2="216.5" y2="72.0" marker-end="url(#d5-ah)"/>
  <line class="arrow-line" x1="323.0" y1="72.0" x2="383.0" y2="72.0" marker-end="url(#d5-ah)"/>
  <line class="arrow-line" x1="489.5" y1="72.0" x2="549.5" y2="72.0" marker-end="url(#d5-ah)"/>
  <path class="arrow-line" d="M 602.8,94.0 C 602.8,144.0 269.8,144.0 269.8,94.0" marker-end="url(#d5-ah)" stroke-dasharray="6,3"/>
  <line class="arrow-line" x1="549.5" y1="72.0" x2="156.5" y2="196.0" marker-end="url(#d5-ah)"/>
  <path class="arrow-line" d="M 254.8,50.0 C 254.8,20.0 284.8,20.0 284.8,50.0" marker-end="url(#d5-ah)"/>
  <rect class="state-node state-initial" x="50.0" y="50.0" width="106.5" height="44.0" rx="20"/>
  <rect class="state-node" x="216.5" y="50.0" width="106.5" height="44.0" rx="20"/>
  <rect class="state-node" x="383.0" y="50.0" width="106.5" height="44.0" rx="20"/>
  <rect class="state-node" x="549.5" y="50.0" width="106.5" height="44.0" rx="20"/>
  <rect class="state-node" x="50.0" y="174.0" width="106.5" height="44.0" rx="20"/>
  <rect class="arrow-label-bg" x="156.1" y="63.0" width="36.8" height="16.0" rx="3"/>
  <text class="arrow-label" x="174.5" y="72.0" dominant-baseline="central">task</text>
  <rect class="arrow-label-bg" x="322.6" y="63.0" width="36.8" height="16.0" rx="3"/>
  <text class="arrow-label" x="341.0" y="72.0" dominant-baseline="central">plan</text>
  <rect class="arrow-label-bg" x="478.3" y="63.0" width="58.4" height="16.0" rx="3"/>
  <text class="arrow-label" x="507.5" y="72.0" dominant-baseline="central">execute</text>
  <rect class="arrow-label-bg" x="407.1" y="122.5" width="58.4" height="16" rx="3"/>
  <text class="arrow-label" x="436.2" y="131.5" dominant-baseline="central">iterate</text>
  <rect class="arrow-label-bg" x="398.8" y="100.2" width="65.6" height="16.0" rx="3"/>
  <text class="arrow-label" x="431.6" y="109.2" dominant-baseline="central">complete</text>
  <rect class="arrow-label-bg" x="244.2" y="8.0" width="51.2" height="16" rx="3"/>
  <text class="arrow-label" x="269.8" y="16.0" dominant-baseline="central">reason</text>
  <text class="state-text" x="103.2" y="72.0" text-anchor="middle" dominant-baseline="central">Idle</text>
  <text class="state-text" x="269.8" y="72.0" text-anchor="middle" dominant-baseline="central">Think</text>
  <text class="state-text" x="436.2" y="72.0" text-anchor="middle" dominant-baseline="central">Act</text>
  <text class="state-text" x="602.8" y="72.0" text-anchor="middle" dominant-baseline="central">Observe</text>
  <text class="state-text" x="103.2" y="196.0" text-anchor="middle" dominant-baseline="central">Done</text>
</svg>

<em>LLM Agent Loop</em>

</div>


## 9. Login Page Wireframe

Simple login form wireframe with email, password, and submit button.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="288" height="388" style="display:block;margin:auto" class="mdview-diagram">

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
  <rect class="bg" x="0" y="0" width="288" height="388" rx="6"/>
  <rect class="wf-panel-fill" x="20.0" y="20.0" width="248.0" height="348.0" style="fill-opacity:0.15"/>
  <rect class="wf-panel" x="20.0" y="20.0" width="248.0" height="348.0"/>
  <text class="wf-title" x="28.0" y="38.0">Login</text>
  <rect class="wf-panel-fill" x="32.0" y="48.0" width="224.0" height="40.0" style="fill-opacity:0.23"/>
  <rect class="wf-panel" x="32.0" y="48.0" width="224.0" height="40.0"/>
  <text class="wf-title" x="40.0" y="66.0">App Logo</text>
  <rect class="wf-panel-fill" x="32.0" y="100.0" width="224.0" height="244.0" style="fill-opacity:0.23"/>
  <rect class="wf-panel" x="32.0" y="100.0" width="224.0" height="244.0"/>
  <text class="wf-title" x="40.0" y="118.0">Credentials</text>
  <rect class="wf-panel" x="44.0" y="128.0" width="200.0" height="56.0"/>
  <text class="wf-title" x="52.0" y="146.0">Email</text>
  <rect class="wf-input" x="52.0" y="154.0" width="184.0" height="24"/>
  <text class="wf-input-text" x="58.0" y="169.0">user@example.com</text>
  <rect class="wf-panel" x="44.0" y="196.0" width="200.0" height="56.0"/>
  <text class="wf-title" x="52.0" y="214.0">Password</text>
  <rect class="wf-input" x="52.0" y="222.0" width="184.0" height="24"/>
  <text class="wf-input-text" x="58.0" y="237.0">********</text>
  <rect class="wf-panel" x="44.0" y="264.0" width="200.0" height="56.0"/>
  <text class="wf-title" x="52.0" y="282.0">Sign In</text>
  <rect class="wf-input" x="52.0" y="292.0" width="184.0" height="24"/>
</svg>

<em>Login Page Wireframe</em>

</div>


## 10. Kubernetes Deployment

Infrastructure as boxes showing ingress, services, and data layer with replicas.


<div align="center">

<svg xmlns="http://www.w3.org/2000/svg" width="687" height="208" style="display:block;margin:auto" class="mdview-diagram">

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
  <rect class="bg" x="0" y="0" width="687" height="208" rx="6"/>
  <defs>
    <clipPath id="d6-bc0"><rect x="20.0" y="20.0" width="176.0" height="112.0" rx="6"/></clipPath>
    <clipPath id="d6-bc1"><rect x="216.0" y="20.0" width="122.0" height="112.0" rx="6"/></clipPath>
    <clipPath id="d6-bc2"><rect x="358.0" y="20.0" width="131.0" height="112.0" rx="6"/></clipPath>
    <clipPath id="d6-bc3"><rect x="509.0" y="20.0" width="158.0" height="128.0" rx="6"/></clipPath>
  </defs>
  <defs>
    <marker id="d6-ah" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" class="arrow-head"/>
    </marker>
  </defs>
  <line class="arrow-line" x1="196.0" y1="76.0" x2="216.0" y2="76.0" marker-end="url(#d6-ah)"/>
  <path class="arrow-line" d="M 108.0,132.0 L 108.0,168.0 L 423.5,168.0 L 423.5,132.0"  marker-end="url(#d6-ah)"/>
  <line class="arrow-line" x1="489.0" y1="76.0" x2="509.0" y2="84.0" marker-end="url(#d6-ah)"/>
  <rect class="box-fill" x="20.0" y="20.0" width="176.0" height="112.0" rx="6"/>
  <rect class="box-border" x="20.0" y="20.0" width="176.0" height="112.0" rx="6"/>
  <g clip-path="url(#d6-bc0)">
    <text class="box-header" x="108.0" y="40.0" text-anchor="middle" dominant-baseline="central">Ingress</text>
    <line class="box-separator" x1="20.0" y1="52.0" x2="196.0" y2="52.0"/>
    <text class="box-text" x="32.0" y="74.0">nginx controller</text>
    <line class="box-separator" x1="20.0" y1="80.0" x2="196.0" y2="80.0"/>
    <text class="box-text" x="32.0" y="102.0">TLS termination</text>
    <text class="box-text" x="32.0" y="118.0">Path routing</text>
  </g>
  <rect class="box-fill" x="216.0" y="20.0" width="122.0" height="112.0" rx="6"/>
  <rect class="box-border" x="216.0" y="20.0" width="122.0" height="112.0" rx="6"/>
  <g clip-path="url(#d6-bc1)">
    <text class="box-header" x="277.0" y="40.0" text-anchor="middle" dominant-baseline="central">Frontend</text>
    <line class="box-separator" x1="216.0" y1="52.0" x2="338.0" y2="52.0"/>
    <text class="box-text" x="228.0" y="74.0">React SPA</text>
    <line class="box-separator" x1="216.0" y1="80.0" x2="338.0" y2="80.0"/>
    <text class="box-text" x="228.0" y="102.0">3 replicas</text>
    <text class="box-text" x="228.0" y="118.0">HPA: 2-10</text>
  </g>
  <rect class="box-fill" x="358.0" y="20.0" width="131.0" height="112.0" rx="6"/>
  <rect class="box-border" x="358.0" y="20.0" width="131.0" height="112.0" rx="6"/>
  <g clip-path="url(#d6-bc2)">
    <text class="box-header" x="423.5" y="40.0" text-anchor="middle" dominant-baseline="central">Backend API</text>
    <line class="box-separator" x1="358.0" y1="52.0" x2="489.0" y2="52.0"/>
    <text class="box-text" x="370.0" y="74.0">FastAPI</text>
    <line class="box-separator" x1="358.0" y1="80.0" x2="489.0" y2="80.0"/>
    <text class="box-text" x="370.0" y="102.0">5 replicas</text>
    <text class="box-text" x="370.0" y="118.0">HPA: 3-20</text>
  </g>
  <rect class="box-fill" x="509.0" y="20.0" width="158.0" height="128.0" rx="6"/>
  <rect class="box-border" x="509.0" y="20.0" width="158.0" height="128.0" rx="6"/>
  <g clip-path="url(#d6-bc3)">
    <text class="box-header" x="588.0" y="40.0" text-anchor="middle" dominant-baseline="central">Data Layer</text>
    <line class="box-separator" x1="509.0" y1="52.0" x2="667.0" y2="52.0"/>
    <text class="box-text" x="521.0" y="74.0">PostgreSQL 15</text>
    <text class="box-text" x="521.0" y="90.0">Redis 7</text>
    <line class="box-separator" x1="509.0" y1="96.0" x2="667.0" y2="96.0"/>
    <text class="box-text" x="521.0" y="118.0">PVC: 100Gi</text>
    <text class="box-text" x="521.0" y="134.0">Backup: hourly</text>
  </g>
  <rect class="arrow-label-bg" x="247.3" y="145.0" width="36.8" height="16" rx="3"/>
  <text class="arrow-label" x="265.8" y="154.0" dominant-baseline="central">/api</text>
</svg>

<em>Kubernetes Deployment</em>

</div>


---

*All diagrams rendered by mdview's spec-based pipeline. Zero external dependencies.*
