const state = {
  experiment: "structure_aware",
  mode: "hybrid",
  questions: [],
  status: null,
  detail: null,
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
  renderQuestionContext();
  renderMetrics();
  renderGold();
  renderAnswer();
  renderEvidence();
}

async function loadQuestion(cqId) {
  state.detail = await fetchJson(`/api/questions/${encodeURIComponent(cqId)}`);
  renderDetail();
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
      $$(".segmented").forEach((item) => item.classList.toggle("active", item === button));
      renderDetail();
    });
  });
  $$(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      $$(".tab").forEach((item) => item.classList.toggle("active", item === button));
      renderDetail();
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
  bindControls();
  state.status = await fetchJson("/api/status");
  renderStatus();
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
