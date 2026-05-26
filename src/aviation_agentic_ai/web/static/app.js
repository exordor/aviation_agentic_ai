const state = {
  experiment: "structure_aware",
  mode: "hybrid",
  questions: [],
  status: null,
  explanation: null,
  detail: null,
  kgGraph: null,
  selectedEdgeId: null,
  cy: null,
  kgNodePositions: {},
  sidebarCollapsed: false,
  pipelineExpanded: false,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));
const SIDEBAR_STORAGE_KEY = "aviation-demo-sidebar-collapsed";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "TBD";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(4);
  if (typeof value === "boolean") return value ? "yes" : "no";
  return String(value);
}

function readSidebarPreference() {
  try {
    return window.localStorage?.getItem(SIDEBAR_STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

function writeSidebarPreference(collapsed) {
  try {
    window.localStorage?.setItem(SIDEBAR_STORAGE_KEY, String(collapsed));
  } catch {
    // Local storage can be unavailable in restrictive browser contexts.
  }
}

function applySidebarState() {
  const shell = $(".app-shell");
  const button = $("#sidebar-toggle");
  if (!shell || !button) return;

  shell.classList.toggle("sidebar-collapsed", state.sidebarCollapsed);
  button.setAttribute("aria-expanded", String(!state.sidebarCollapsed));
  button.setAttribute(
    "aria-label",
    state.sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"
  );
  button.setAttribute("title", state.sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar");
  button.textContent = state.sidebarCollapsed ? "\u203a" : "\u2039";

  if (state.cy) {
    requestAnimationFrame(() => {
      state.cy.resize();
      state.cy.fit(undefined, 26);
    });
  }
}

function toggleSidebar() {
  state.sidebarCollapsed = !state.sidebarCollapsed;
  writeSidebarPreference(state.sidebarCollapsed);
  applySidebarState();
}

function applyPipelineState() {
  const panel = $(".pipeline-panel");
  const steps = $("#pipeline-steps");
  const button = $("#pipeline-toggle");
  if (!panel || !steps || !button) return;

  panel.classList.toggle("collapsed", !state.pipelineExpanded);
  steps.hidden = !state.pipelineExpanded;
  button.setAttribute("aria-expanded", String(state.pipelineExpanded));
  button.setAttribute(
    "aria-label",
    state.pipelineExpanded ? "Hide pipeline details" : "Show pipeline details"
  );
  button.setAttribute(
    "title",
    state.pipelineExpanded ? "Hide pipeline details" : "Show pipeline details"
  );
  button.textContent = state.pipelineExpanded ? "-" : "+";
}

function togglePipelineDetails() {
  state.pipelineExpanded = !state.pipelineExpanded;
  applyPipelineState();
}

function renderInlineMarkdown(value) {
  const codePlaceholders = [];
  const html = escapeHtml(value).replace(/`([^`]+)`/g, (_match, code) => {
    const index = codePlaceholders.length;
    codePlaceholders.push(`<code>${code}</code>`);
    return `\u0000CODE${index}\u0000`;
  });

  return html
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\u0000CODE(\d+)\u0000/g, (_match, index) => codePlaceholders[Number(index)] || "");
}

function answerListTemplate(lines) {
  let html = '<ul class="answer-list">';
  let itemOpen = false;
  let nestedOpen = false;

  lines.forEach((line) => {
    const match = line.match(/^(\s*)-\s+(.*)$/);
    if (!match) return;
    const depth = match[1].replaceAll("\t", "  ").length >= 2 ? 1 : 0;
    const content = renderInlineMarkdown(match[2].trim());

    if (depth === 0 || !itemOpen) {
      if (nestedOpen) {
        html += "</ul>";
        nestedOpen = false;
      }
      if (itemOpen) html += "</li>";
      html += `<li>${content}`;
      itemOpen = true;
      return;
    }

    if (!nestedOpen) {
      html += '<ul class="answer-sublist">';
      nestedOpen = true;
    }
    html += `<li>${content}</li>`;
  });

  if (nestedOpen) html += "</ul>";
  if (itemOpen) html += "</li>";
  return `${html}</ul>`;
}

function answerParagraphTemplate(lines) {
  return `<p>${lines.map((line) => renderInlineMarkdown(line.trim())).join("<br />")}</p>`;
}

function renderAnswerMarkdown(value) {
  const text = String(value ?? "").replace(/\r\n?/g, "\n").trim();
  if (!text) return "<p>No answer available for this mode.</p>";

  return text
    .split(/\n{2,}/)
    .map((block) => block.split("\n").filter((line) => line.trim()))
    .filter((lines) => lines.length)
    .map((lines) =>
      lines.every((line) => /^(\s*)-\s+/.test(line))
        ? answerListTemplate(lines)
        : answerParagraphTemplate(lines)
    )
    .join("");
}

async function fetchJson(path, options) {
  const response = await fetch(path, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `Request failed: ${response.status}`);
  }
  return payload;
}

function renderStatus() {
  const status = state.status || {};
  $("#advisory-boundary").textContent = status.advisory_boundary || "Not loaded";
  $("#live-status").textContent = status.live_query_enabled ? "Live enabled" : "Live disabled";
  $("#live-status").className = status.live_query_enabled
    ? "status-pill supported"
    : "status-pill partial";
  const ready = status.ready ? "ready" : "missing";
  const rows = [
    ["Default", status.default_strategy],
    ["Artifacts", ready],
    ["Live query", status.live_query_enabled ? "enabled" : "disabled"],
    ["Collection", status.live_query_default?.collection_name],
  ];
  $("#status-grid").innerHTML = rows
    .map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(formatValue(value))}</dd>`)
    .join("");
}

function renderQuestions() {
  const list = $("#question-list");
  list.innerHTML = state.questions
    .map(
      (question) => `
        <button
          class="question-row${state.detail?.cq_id === question.cq_id ? " active" : ""}"
          data-cq-id="${escapeHtml(question.cq_id)}"
          role="option"
          aria-selected="${state.detail?.cq_id === question.cq_id ? "true" : "false"}"
        >
          <strong>${escapeHtml(question.cq_id)}</strong>
          <span>page ${escapeHtml(question.source_page)} · ${escapeHtml(question.gold_level)}</span>
        </button>
      `
    )
    .join("");
}

function selectedModePayload() {
  return state.detail?.experiments?.[state.experiment]?.modes?.[state.mode] || {};
}

function modeLabel(mode = state.mode) {
  return state.explanation?.mode_explanations?.[mode]?.label || mode;
}

function truncate(value, length = 28) {
  const text = String(value ?? "");
  return text.length > length ? `${text.slice(0, length - 1)}...` : text;
}

function renderDemoNarrative() {
  const narrative = state.explanation?.narrative || {};
  $("#demo-narrative-title").textContent = narrative.headline || "Demo narrative unavailable";
  $("#demo-claim").textContent = narrative.claim || "";
  $("#demo-default-path").textContent = narrative.default_path || "Default TBD";
  $("#demo-boundary").textContent = narrative.advisory_boundary || state.status?.advisory_boundary || "";
}

function pipelineStepTemplate(step) {
  return `
    <div class="pipeline-step${step.present ? "" : " missing"}">
      <div class="pipeline-marker" aria-hidden="true"></div>
      <div class="pipeline-body">
        <div class="pipeline-title">
          <span>${escapeHtml(step.title)}</span>
          <span class="status-pill ${step.present ? "supported" : "partial"}">${step.present ? "ready" : "missing"}</span>
        </div>
        <p>${escapeHtml(step.why)}</p>
        <code>${escapeHtml(step.path)}</code>
      </div>
    </div>
  `;
}

function renderPipelineExplanation() {
  const steps = state.explanation?.pipeline_steps || [];
  const ready = steps.filter((step) => step.present).length;
  $("#pipeline-ready-count").textContent = `${ready}/${steps.length}`;
  $("#pipeline-steps").innerHTML = steps.length
    ? steps.map(pipelineStepTemplate).join("")
    : "<p class='evidence-text'>No pipeline explanation loaded.</p>";
  applyPipelineState();
}

function modeExplanationTemplate(mode, explanation) {
  return `
    <div class="mode-explanation${state.mode === mode ? " active" : ""}" data-mode-summary="${escapeHtml(mode)}">
      <div class="mode-title">
        <span>${escapeHtml(explanation.label || mode)}</span>
        <span>${state.mode === mode ? "selected" : "available"}</span>
      </div>
      <p>${escapeHtml(explanation.purpose || "")}</p>
      <p><strong>Strength:</strong> ${escapeHtml(explanation.strength || "")}</p>
      <p><strong>Tradeoff:</strong> ${escapeHtml(explanation.tradeoff || "")}</p>
    </div>
  `;
}

function renderModeComparison() {
  const explanations = state.explanation?.mode_explanations || {};
  $("#active-mode-label").textContent = modeLabel();
  $("#mode-explanations").innerHTML = ["vector", "graph", "hybrid"]
    .filter((mode) => explanations[mode])
    .map((mode) => modeExplanationTemplate(mode, explanations[mode]))
    .join("");
}

function renderStrategyDecision() {
  const decision = state.explanation?.strategy_decision || {};
  const recommended = decision.recommended || "TBD";
  const baseline = decision.baseline || "TBD";
  const rationale = decision.rationale || [];
  return [
    `Recommended strategy: ${recommended}`,
    `Baseline kept visible: ${baseline}`,
    ...rationale,
  ].join(" ");
}

function resultExplanationRows() {
  const payload = selectedModePayload();
  const evalData = payload.evidence_eval || {};
  const chunks = payload.fused_chunks || [];
  const triples = payload.graph_triples || [];
  const support = evalData.answer_support || "no data";
  const citation = evalData.citation?.citation_completeness;
  const span = evalData.span?.span_hit;
  const chunkRecall = evalData.chunk?.chunk_recall_at_5;
  const graphText =
    state.mode === "vector"
      ? "Vector mode intentionally has no KG graph; inspect retrieved chunks instead."
      : `${triples.length} KG triples are available for graph-level provenance.`;
  const interpretation = {
    vector: "This mode answers from semantically similar chunks. It is useful as the retrieval baseline.",
    graph: "This mode foregrounds ontology-constrained relationships. Its value is explainable evidence structure.",
    hybrid: "This mode combines chunk evidence with KG triples, so it is the recommended demo path.",
  };
  return [
    ["Mode purpose", interpretation[state.mode] || "No explanation for this mode."],
    ["Evidence shape", `${chunks.length} retrieved chunks; ${graphText}`],
    ["Metric signal", `Chunk Recall@5=${formatValue(chunkRecall)}, Span hit=${formatValue(span)}, Citation=${formatValue(citation)}`],
    ["Answer support", support.replaceAll("_", " ")],
    ["Strategy note", renderStrategyDecision()],
  ];
}

function renderResultExplanation() {
  $("#why-mode-label").textContent = modeLabel();
  $("#result-explanation").innerHTML = resultExplanationRows()
    .map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(formatValue(value))}</dd>`)
    .join("");
}

function renderDemoExplanation() {
  renderDemoNarrative();
  renderPipelineExplanation();
  renderModeComparison();
  renderResultExplanation();
}

function renderMetrics() {
  const payload = selectedModePayload();
  const evalData = payload.evidence_eval || {};
  const kg = payload.metrics?.kg_evidence || {};
  const metrics = [
    ["Chunk Recall@5", evalData.chunk?.chunk_recall_at_5],
    ["Span hit", evalData.span?.span_hit],
    ["KG coverage", kg.evidence_coverage ?? evalData.kg_evidence?.evidence_coverage],
    ["Citation", evalData.citation?.citation_completeness],
  ];
  $("#metrics-strip").innerHTML = metrics
    .map(
      ([label, value]) => `
        <div class="metric">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(formatValue(value))}</strong>
        </div>
      `
    )
    .join("");
}

function renderGold() {
  const gold = state.detail?.gold || {};
  const rows = [
    ["Gold level", gold.gold_level],
    ["Source page", gold.source_page],
    ["Key entities", (gold.key_entities || []).join(", ")],
    ["Expected chunks", (gold.expected_chunk_ids || []).length],
    ["Evidence spans", (gold.evidence_spans || []).length],
  ];
  $("#gold-grid").innerHTML = rows
    .map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(formatValue(value))}</dd>`)
    .join("");
}

function renderAnswer() {
  const payload = selectedModePayload();
  const support = payload.evidence_eval?.answer_support || "no data";
  const badge = $("#support-badge");
  badge.textContent = support.replaceAll("_", " ");
  badge.className = support === "supported" ? "status-pill supported" : "status-pill partial";
  $("#answer-content").innerHTML = renderAnswerMarkdown(payload.answer);
}

function chunkTemplate(chunk) {
  return `
    <div class="evidence-row">
      <div class="evidence-title">
        <span>${escapeHtml(chunk.chunk_id || "unknown chunk")}</span>
        <span>page ${escapeHtml(formatValue(chunk.page))}</span>
      </div>
      <div class="evidence-meta">rank ${escapeHtml(formatValue(chunk.rank))} · ${escapeHtml(formatValue(chunk.source))} · score ${escapeHtml(formatValue(chunk.score))}</div>
      <p class="evidence-text">${escapeHtml(chunk.text_preview || "")}</p>
    </div>
  `;
}

function tripleTemplate(triple) {
  return `
    <div class="evidence-row">
      <div class="evidence-title">
        <span>${escapeHtml(triple.subject || "subject")} → ${escapeHtml(triple.predicate || "predicate")} → ${escapeHtml(triple.object || "object")}</span>
        <span>page ${escapeHtml(formatValue(triple.page))}</span>
      </div>
      <div class="evidence-meta">${escapeHtml(triple.triple_id || "")}</div>
      <p class="evidence-text">${escapeHtml(triple.evidence_text || "")}</p>
    </div>
  `;
}

function renderEvidence() {
  const payload = selectedModePayload();
  const chunks = payload.fused_chunks || [];
  const triples = payload.graph_triples || [];
  $("#chunk-count").textContent = chunks.length;
  $("#triple-count").textContent = triples.length;
  $("#chunks-list").innerHTML = chunks.length
    ? chunks.map(chunkTemplate).join("")
    : "<p class='evidence-text'>No chunks.</p>";
  $("#triples-list").innerHTML = triples.length
    ? triples.map(tripleTemplate).join("")
    : "<p class='evidence-text'>No KG triples.</p>";
}

function graphDetailRows(edge) {
  if (!edge) {
    return `
      <dt>Selection</dt>
      <dd>No edge selected.</dd>
      <dd class="detail-wide">Select a KG edge to inspect its source chunk, page, and evidence text.</dd>
    `;
  }
  const rows = [
    ["Triple", edge.triple_id],
    ["Subject", edge.subject],
    ["Predicate", edge.predicate],
    ["Object", edge.object],
    ["Chunk", edge.chunk_id],
    ["Page", edge.page],
    ["Confidence", edge.confidence ?? edge.score],
  ];
  return (
    rows
      .map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(formatValue(value))}</dd>`)
      .join("") +
    `<dd class="detail-wide">${escapeHtml(edge.evidence_text || "No evidence text in this report.")}</dd>`
  );
}

function nodePositionMap(nodes) {
  const positions = new Map();
  if (!nodes.length) return positions;
  if (nodes.length === 1) {
    positions.set(nodes[0].id, { x: 360, y: 160 });
    return positions;
  }
  if (nodes.length === 2) {
    positions.set(nodes[0].id, { x: 240, y: 160 });
    positions.set(nodes[1].id, { x: 480, y: 160 });
    return positions;
  }

  const [center, ...outer] = nodes;
  positions.set(center.id, { x: 360, y: 160 });
  outer.forEach((node, index) => {
    const angle = -Math.PI / 2 + (Math.PI * 2 * index) / outer.length;
    positions.set(node.id, {
      x: 360 + Math.cos(angle) * 250,
      y: 160 + Math.sin(angle) * 104,
    });
  });
  return positions;
}

function kgGraphLayoutKey() {
  return [state.detail?.cq_id || "none", state.experiment, state.mode].join(":");
}

function ensureNodePositions(nodes) {
  const key = kgGraphLayoutKey();
  const existing = state.kgNodePositions[key] || {};
  const defaults = nodePositionMap(nodes);
  const positions = {};
  nodes.forEach((node) => {
    const stored = existing[node.id];
    const fallback = defaults.get(node.id) || { x: 360, y: 160 };
    positions[node.id] = stored || fallback;
  });
  state.kgNodePositions[key] = positions;
  return positions;
}

function persistCytoscapePositions() {
  if (!state.cy) return;
  const positions = {};
  state.cy.nodes().forEach((node) => {
    positions[node.id()] = node.position();
  });
  state.kgNodePositions[kgGraphLayoutKey()] = positions;
}

function destroyKgGraph() {
  if (state.cy) {
    state.cy.destroy();
    state.cy = null;
  }
}

function renderKgGraph() {
  const graph = state.kgGraph || { nodes: [], edges: [], metadata: {} };
  const nodes = graph.nodes || [];
  const edges = graph.edges || [];
  const container = $("#kg-graph-canvas");
  const canvas = container.closest(".graph-canvas");
  $("#kg-node-count").textContent = `${nodes.length} nodes`;
  $("#kg-edge-count").textContent = `${edges.length} edges`;

  if (!nodes.length || !edges.length) {
    destroyKgGraph();
    canvas.classList.add("empty");
    $("#kg-graph-detail").innerHTML = graphDetailRows(null);
    return;
  }

  if (!window.cytoscape) {
    destroyKgGraph();
    canvas.classList.add("empty");
    $("#kg-graph-empty").textContent = "Graph library unavailable.";
    $("#kg-graph-detail").innerHTML = graphDetailRows({
      evidence_text: "Cytoscape.js did not load. Check /static/vendor/cytoscape.min.js.",
    });
    return;
  }

  destroyKgGraph();
  canvas.classList.remove("empty");
  $("#kg-graph-empty").textContent = "No KG triples for this mode.";
  if (!edges.some((edge) => edge.id === state.selectedEdgeId)) {
    state.selectedEdgeId = edges[0].id;
  }

  const positions = ensureNodePositions(nodes);
  const elements = [
    ...nodes.map((node) => ({
      data: {
        id: node.id,
        label: truncate(node.label, 18),
        classLabel: truncate(node.class, 18),
        displayLabel: `${truncate(node.label, 18)}\n${truncate(node.class, 18)}`,
        degree: Number(node.degree || 0),
      },
      position: positions[node.id],
      grabbable: true,
    })),
    ...edges.map((edge) => ({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: truncate(edge.predicate, 24),
        record: edge,
      },
      classes: edge.id === state.selectedEdgeId ? "selected" : "",
    })),
  ];

  state.cy = cytoscape({
    container,
    elements,
    autoungrabify: false,
    autolock: false,
    boxSelectionEnabled: false,
    minZoom: 0.4,
    maxZoom: 2.5,
    wheelSensitivity: 0.18,
    layout: { name: "preset", fit: true, padding: 26 },
    style: [
      {
        selector: "node",
        style: {
          width: "58px",
          height: "58px",
          "background-color": "rgba(255, 255, 255, 0.96)",
          "border-color": "rgba(0, 122, 255, 0.60)",
          "border-width": 2,
          color: "#1d1d1f",
          content: "data(displayLabel)",
          "font-size": 10,
          "font-weight": 700,
          "line-height": 1.1,
          "text-halign": "center",
          "text-valign": "center",
          "text-wrap": "wrap",
          "text-max-width": "72px",
          "text-outline-color": "rgba(255, 255, 255, 0.86)",
          "text-outline-width": 2,
        },
      },
      {
        selector: "edge",
        style: {
          width: 1.8,
          "line-color": "rgba(0, 122, 255, 0.45)",
          "target-arrow-color": "rgba(0, 122, 255, 0.55)",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          label: "data(label)",
          color: "rgba(60, 60, 67, 0.82)",
          "font-size": 10,
          "font-weight": 650,
          "text-background-color": "rgba(255, 255, 255, 0.82)",
          "text-background-opacity": 1,
          "text-background-padding": 2,
          "text-rotation": "autorotate",
          "z-index": 1,
        },
      },
      {
        selector: "edge.selected",
        style: {
          width: 3,
          "line-color": "#0057b8",
          "target-arrow-color": "#0057b8",
          "z-index": 3,
        },
      },
      {
        selector: "node:grabbed",
        style: {
          "border-color": "#0057b8",
          "border-width": 3,
          "overlay-color": "rgba(0, 122, 255, 0.16)",
          "overlay-opacity": 1,
        },
      },
    ],
  });

  state.cy.nodes().grabify();
  state.cy.on("dragfree", "node", persistCytoscapePositions);
  state.cy.on("tap", "edge", (event) => {
    const edge = event.target;
    state.selectedEdgeId = edge.id();
    state.cy.edges().removeClass("selected");
    edge.addClass("selected");
    $("#kg-graph-detail").innerHTML = graphDetailRows(edge.data("record"));
  });

  const selectedEdge = edges.find((edge) => edge.id === state.selectedEdgeId) || edges[0];
  $("#kg-graph-detail").innerHTML = graphDetailRows(selectedEdge);
}

function renderQuestionContext() {
  const gold = state.detail?.gold || {};
  const cqId = state.detail?.cq_id || "No CQ";
  const sourcePage = gold.source_page ?? "TBD";
  const goldLevel = gold.gold_level || "TBD";
  $("#question-meta").textContent = `${cqId} · page ${sourcePage} · ${goldLevel} gold`;
  const entities = gold.key_entities || [];
  $("#entity-strip").innerHTML = entities
    .map((entity) => `<span class="entity-pill">${escapeHtml(entity)}</span>`)
    .join("");
}

function renderDetail() {
  $("#question-title").textContent = state.detail?.question || "Select a question";
  renderQuestions();
  renderDemoExplanation();
  renderQuestionContext();
  renderMetrics();
  renderGold();
  renderAnswer();
  renderEvidence();
}

async function loadQuestion(cqId) {
  state.detail = await fetchJson(`/api/questions/${encodeURIComponent(cqId)}`);
  state.selectedEdgeId = null;
  renderDetail();
  await loadKgGraph();
}

async function loadKgGraph() {
  if (!state.detail?.cq_id) {
    state.kgGraph = null;
    renderKgGraph();
    return;
  }
  const cqId = state.detail.cq_id;
  const experiment = state.experiment;
  const mode = state.mode;
  const graph = await fetchJson(
    `/api/questions/${encodeURIComponent(cqId)}/kg-graph?experiment=${encodeURIComponent(experiment)}&mode=${encodeURIComponent(mode)}`
  );
  if (
    state.detail?.cq_id !== cqId ||
    state.experiment !== experiment ||
    state.mode !== mode
  ) {
    return;
  }
  state.kgGraph = graph;
  renderKgGraph();
}

function bindControls() {
  $("#sidebar-toggle").addEventListener("click", toggleSidebar);
  $("#pipeline-toggle").addEventListener("click", togglePipelineDetails);
  $("#question-list").addEventListener("click", (event) => {
    const row = event.target.closest(".question-row");
    if (!row) return;
    loadQuestion(row.dataset.cqId);
  });
  $$(".segmented").forEach((button) => {
    button.addEventListener("click", () => {
      state.experiment = button.dataset.experiment;
      state.selectedEdgeId = null;
      $$(".segmented").forEach((item) => item.classList.toggle("active", item === button));
      renderDetail();
      loadKgGraph().catch((error) => {
        $("#kg-graph-detail").innerHTML = graphDetailRows({ evidence_text: error.message });
      });
    });
  });
  $$(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      state.selectedEdgeId = null;
      $$(".tab").forEach((item) => item.classList.toggle("active", item === button));
      renderDetail();
      loadKgGraph().catch((error) => {
        $("#kg-graph-detail").innerHTML = graphDetailRows({ evidence_text: error.message });
      });
    });
  });
  $("#live-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const question = $("#live-question").value.trim();
    if (!question) return;
    $("#live-output").textContent = "Running...";
    try {
      const result = await fetchJson("/api/query", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question, mode: "hybrid" }),
      });
      $("#live-output").textContent = result.answer || JSON.stringify(result, null, 2);
    } catch (error) {
      $("#live-output").textContent = error.message;
    }
  });
}

async function init() {
  state.sidebarCollapsed = readSidebarPreference();
  applySidebarState();
  applyPipelineState();
  bindControls();
  state.status = await fetchJson("/api/status");
  state.explanation = await fetchJson("/api/demo/explanation");
  renderStatus();
  renderDemoExplanation();
  const questionsPayload = await fetchJson("/api/questions");
  state.questions = questionsPayload.questions || [];
  renderQuestions();
  if (state.questions.length) {
    await loadQuestion(state.questions[0].cq_id);
  }
}

init().catch((error) => {
  $("#answer-content").textContent = error.message;
});
