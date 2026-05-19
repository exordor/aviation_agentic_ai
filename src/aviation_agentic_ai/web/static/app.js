const state = {
  experiment: "structure_aware",
  mode: "hybrid",
  questions: [],
  status: null,
  explanation: null,
  detail: null,
  kgGraph: null,
  selectedEdgeId: null,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

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
  $("#answer-content").textContent = payload.answer || "No answer available for this mode.";
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

function renderKgGraph() {
  const graph = state.kgGraph || { nodes: [], edges: [], metadata: {} };
  const nodes = graph.nodes || [];
  const edges = graph.edges || [];
  const svg = $("#kg-graph-svg");
  const canvas = svg.closest(".graph-canvas");
  $("#kg-node-count").textContent = `${nodes.length} nodes`;
  $("#kg-edge-count").textContent = `${edges.length} edges`;

  if (!nodes.length || !edges.length) {
    canvas.classList.add("empty");
    svg.innerHTML = "";
    $("#kg-graph-detail").innerHTML = graphDetailRows(null);
    return;
  }

  canvas.classList.remove("empty");
  if (!edges.some((edge) => edge.id === state.selectedEdgeId)) {
    state.selectedEdgeId = edges[0].id;
  }

  const positions = nodePositionMap(nodes);
  const edgeMarkup = edges
    .map((edge) => {
      const source = positions.get(edge.source);
      const target = positions.get(edge.target);
      if (!source || !target) return "";
      const selected = edge.id === state.selectedEdgeId ? " selected" : "";
      const midX = (source.x + target.x) / 2;
      const midY = (source.y + target.y) / 2 - 8;
      return `
        <g>
          <line class="kg-edge${selected}" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" marker-end="url(#kg-arrow)" data-edge-id="${escapeHtml(edge.id)}"></line>
          <text class="kg-edge-label" x="${midX}" y="${midY}" data-edge-id="${escapeHtml(edge.id)}">${escapeHtml(truncate(edge.predicate, 24))}</text>
        </g>
      `;
    })
    .join("");

  const nodeMarkup = nodes
    .map((node) => {
      const position = positions.get(node.id);
      if (!position) return "";
      const radius = Math.min(34, 22 + Number(node.degree || 0) * 3);
      return `
        <g class="kg-node">
          <circle class="kg-node-circle" cx="${position.x}" cy="${position.y}" r="${radius}"></circle>
          <text class="kg-node-label" x="${position.x}" y="${position.y - 2}">${escapeHtml(truncate(node.label, 18))}</text>
          <text class="kg-node-class" x="${position.x}" y="${position.y + 13}">${escapeHtml(truncate(node.class, 18))}</text>
        </g>
      `;
    })
    .join("");

  svg.innerHTML = `
    <defs>
      <marker id="kg-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(0, 122, 255, 0.55)"></path>
      </marker>
    </defs>
    ${edgeMarkup}
    ${nodeMarkup}
  `;
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
  $("#kg-graph-svg").addEventListener("click", (event) => {
    const edge = event.target.closest("[data-edge-id]");
    if (!edge) return;
    state.selectedEdgeId = edge.dataset.edgeId;
    renderKgGraph();
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
