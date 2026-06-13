from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty
from aviation_agentic_ai.reporting.atmonto.s7.answer_review_decisions import (
    ALLOWED_CITATION_SUFFICIENCY,
    ALLOWED_EVIDENCE_SUPPORT,
    ALLOWED_PROFILE_BOUNDARY,
    ALLOWED_REVIEW_DECISIONS,
    ALLOWED_REVIEWER_ROLES,
    DEFAULT_PACKET_PATH,
    DEFAULT_REVIEW_CSV_PATH,
)
from aviation_agentic_ai.reporting.atmonto.s7.broad_answer_review_packet import (
    review_csv_rows,
)

DEFAULT_REPORT_NAME = "nasa_atmonto_s7_answer_review_worksheet"


def build_nasa_atmonto_s7_answer_review_worksheet(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    packet_path: str | Path = DEFAULT_PACKET_PATH,
    review_csv_path: str | Path = DEFAULT_REVIEW_CSV_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    packet_source = _resolve(root, packet_path)
    csv_source = _resolve(root, review_csv_path)
    packet = read_json_object_or_empty(packet_source)
    base_rows = {
        str(row.get("review_id") or ""): row
        for row in review_csv_rows(packet)
        if row.get("review_id")
    }
    existing_rows = {
        str(row.get("review_id") or ""): row
        for row in _read_csv_rows(csv_source)
        if row.get("review_id")
    }
    cases = []
    for case in packet.get("cases", []) if isinstance(packet.get("cases"), list) else []:
        if not isinstance(case, dict):
            continue
        review_id = str(case.get("review_id") or "")
        csv_row = dict(base_rows.get(review_id, {}))
        csv_row.update(existing_rows.get(review_id, {}))
        cases.append(_worksheet_case(case, csv_row))
    return {
        "source_family": "nasa_atmonto_s7_answer_review_worksheet",
        "status": "answer_review_worksheet_created",
        "metadata": {
            "packet_path": project_relative_path(packet_source, root),
            "review_csv_path": project_relative_path(csv_source, root),
            "case_count": len(cases),
            "failure_case_count": sum(1 for case in cases if case["priority"] == "failure"),
            "coverage_success_case_count": sum(
                1 for case in cases if case["priority"] != "failure"
            ),
            "human_review": False,
            "human_review_completed": False,
            "boundary": (
                "This worksheet is a reviewer work aid. It preloads automatic S7 answer "
                "metrics and any existing CSV decisions, but exported decisions must still "
                "be validated by the S7 answer review decision report."
            ),
        },
        "review_fields": review_fields(),
        "csv_columns": _csv_columns(cases),
        "cases": cases,
        "claim_boundary": (
            "The worksheet does not certify answer correctness. It only makes human or "
            "expert answer review easier to perform and audit."
        ),
    }


def review_fields() -> list[dict[str, Any]]:
    return [
        {
            "field": "review_decision",
            "label": "Review decision",
            "allowed_values": sorted(ALLOWED_REVIEW_DECISIONS),
        },
        {
            "field": "evidence_support",
            "label": "Evidence support",
            "allowed_values": sorted(ALLOWED_EVIDENCE_SUPPORT),
        },
        {
            "field": "citation_sufficiency",
            "label": "Citation sufficiency",
            "allowed_values": sorted(ALLOWED_CITATION_SUFFICIENCY),
        },
        {
            "field": "profile_boundary",
            "label": "Profile boundary",
            "allowed_values": sorted(ALLOWED_PROFILE_BOUNDARY),
        },
        {
            "field": "reviewer_role",
            "label": "Reviewer role",
            "allowed_values": sorted(ALLOWED_REVIEWER_ROLES),
        },
    ]


def write_nasa_atmonto_s7_answer_review_worksheet_html(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_nasa_atmonto_s7_answer_review_worksheet_html(result), encoding="utf-8")
    return path


def write_nasa_atmonto_s7_answer_review_worksheet(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    report_name: str = DEFAULT_REPORT_NAME,
) -> tuple[Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_answer_review_worksheet(repo_root=repo_root)
    output = Path(output_dir)
    html_path = write_nasa_atmonto_s7_answer_review_worksheet_html(
        result,
        output / f"{report_name}.html",
    )
    return html_path, result


def render_nasa_atmonto_s7_answer_review_worksheet_html(result: dict[str, Any]) -> str:
    cases = result["cases"]
    csv_rows_json = _json_script([case["csv_row"] for case in cases])
    csv_columns_json = _json_script(result["csv_columns"])
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>NASA ATMONTO S7 Answer Review Worksheet</title>",
            f"<style>{_stylesheet()}</style>",
            "</head>",
            "<body>",
            "<header>",
            "<h1>NASA ATMONTO S7 Answer Review Worksheet</h1>",
            f"<p>{_e(result['metadata']['boundary'])}</p>",
            '<div class="summary">',
            _summary_item("Cases", result["metadata"]["case_count"]),
            _summary_item("Failure priority", result["metadata"]["failure_case_count"]),
            _summary_item("Coverage success", result["metadata"]["coverage_success_case_count"]),
            "</div>",
            "</header>",
            "<main>",
            '<section class="controls" aria-label="Worksheet controls">',
            '<input id="search" type="search" placeholder="Search review ID, source, template, question">',
            '<select id="priority-filter">',
            '<option value="">All priorities</option>',
            '<option value="failure">Failure priority</option>',
            '<option value="coverage_success">Coverage success</option>',
            "</select>",
            '<button id="export-csv" type="button">Download reviewed CSV</button>',
            '<button id="clear-draft" type="button">Clear browser draft</button>',
            "</section>",
            '<p class="boundary">',
            _e(result["claim_boundary"]),
            "</p>",
            '<section id="case-list" class="case-list">',
            *[_render_case(case, result["review_fields"]) for case in cases],
            "</section>",
            "</main>",
            f'<script id="csv-rows-data" type="application/json">{csv_rows_json}</script>',
            f'<script id="csv-columns-data" type="application/json">{csv_columns_json}</script>',
            f"<script>{_script()}</script>",
            "</body>",
            "</html>",
        ]
    )


def _worksheet_case(case: dict[str, Any], csv_row: dict[str, Any]) -> dict[str, Any]:
    evidence = case.get("evidence") if isinstance(case.get("evidence"), dict) else {}
    metrics = case.get("metrics") if isinstance(case.get("metrics"), dict) else {}
    return {
        "review_id": str(case.get("review_id") or ""),
        "priority": str(case.get("priority") or ""),
        "template_id": str(case.get("template_id") or ""),
        "source_id": str(case.get("source_id") or ""),
        "mode": str(case.get("mode") or ""),
        "question": str(case.get("question") or ""),
        "answer": str(case.get("answer") or ""),
        "raw_response": str(case.get("raw_response") or ""),
        "expected_answer_set": case.get("expected_answer_set", []),
        "answer_values": case.get("answer_values", []),
        "metrics": metrics,
        "source_chunks": evidence.get("source_chunks", []),
        "graph_triples": evidence.get("graph_triples", []),
        "review_questions": case.get("review_questions", []),
        "csv_row": csv_row,
    }


def _render_case(case: dict[str, Any], fields: list[dict[str, Any]]) -> str:
    search_text = " ".join(
        [
            case["review_id"],
            case["priority"],
            case["template_id"],
            case["source_id"],
            case["question"],
            case["answer"],
        ]
    ).lower()
    return "\n".join(
        [
            (
                f'<article class="case" data-priority="{_attr(case["priority"])}" '
                f'data-search="{_attr(search_text)}">'
            ),
            "<header>",
            f"<h2>{_e(case['review_id'])} - {_e(case['template_id'])}</h2>",
            '<div class="meta">',
            _pill(case["priority"]),
            _pill(case["source_id"]),
            _pill(case["mode"]),
            "</div>",
            "</header>",
            '<section class="question-answer">',
            "<h3>Question</h3>",
            f"<p>{_e(case['question'])}</p>",
            "<h3>Answer</h3>",
            f"<p>{_e(case['answer'])}</p>",
            "</section>",
            '<section class="grid">',
            _render_json_panel("Expected answer set", case["expected_answer_set"]),
            _render_json_panel("Answer values", case["answer_values"]),
            _render_json_panel("Automatic metrics", case["metrics"]),
            _render_review_questions(case["review_questions"]),
            "</section>",
            '<section class="evidence">',
            "<h3>Source chunks</h3>",
            _render_source_chunks(case["source_chunks"]),
            "<h3>Graph triples</h3>",
            _render_graph_triples(case["graph_triples"]),
            "</section>",
            '<section class="review-form">',
            "<h3>Reviewer fields</h3>",
            _render_review_fields(case, fields),
            _render_text_input(case, "reviewer_id_or_initials", "Reviewer ID or initials"),
            _render_text_input(case, "reviewed_at", "Reviewed at"),
            _render_notes(case),
            "</section>",
            '<details class="raw-response">',
            "<summary>Raw LLM response</summary>",
            f"<pre>{_e(case['raw_response'])}</pre>",
            "</details>",
            "</article>",
        ]
    )


def _render_review_fields(case: dict[str, Any], fields: list[dict[str, Any]]) -> str:
    return "\n".join(_render_select(case, field) for field in fields)


def _render_select(case: dict[str, Any], field: dict[str, Any]) -> str:
    value = str(case["csv_row"].get(field["field"]) or "")
    options = ['<option value=""></option>']
    options.extend(
        (
            f'<option value="{_attr(option)}"'
            f'{" selected" if option == value else ""}>{_e(option)}</option>'
        )
        for option in field["allowed_values"]
    )
    return (
        f'<label>{_e(field["label"])}'
        f'<select data-review-id="{_attr(case["review_id"])}" '
        f'data-field="{_attr(field["field"])}">'
        f'{"".join(options)}</select></label>'
    )


def _render_text_input(case: dict[str, Any], field: str, label: str) -> str:
    value = str(case["csv_row"].get(field) or "")
    return (
        f"<label>{_e(label)}"
        f'<input type="text" data-review-id="{_attr(case["review_id"])}" '
        f'data-field="{_attr(field)}" value="{_attr(value)}"></label>'
    )


def _render_notes(case: dict[str, Any]) -> str:
    value = str(case["csv_row"].get("reviewer_notes") or "")
    return (
        "<label>Reviewer notes"
        f'<textarea data-review-id="{_attr(case["review_id"])}" '
        f'data-field="reviewer_notes">{_e(value)}</textarea></label>'
    )


def _render_source_chunks(chunks: Any) -> str:
    if not isinstance(chunks, list) or not chunks:
        return '<p class="muted">No source chunks.</p>'
    items = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        chunk_id = str(chunk.get("chunk_id") or "")
        text = str(chunk.get("text") or "")
        items.append(f"<li><strong>{_e(chunk_id)}</strong><pre>{_e(text)}</pre></li>")
    return f"<ul>{''.join(items)}</ul>" if items else '<p class="muted">No source chunks.</p>'


def _render_graph_triples(triples: Any) -> str:
    if not isinstance(triples, list) or not triples:
        return '<p class="muted">No graph triples.</p>'
    items = []
    for triple in triples:
        if not isinstance(triple, dict):
            continue
        triple_id = str(triple.get("triple_id") or "")
        predicate = str(triple.get("predicate") or "")
        obj = str(triple.get("object") or "")
        evidence_text = str(triple.get("evidence_text") or "")
        items.append(
            "<li>"
            f"<strong>{_e(triple_id)}</strong> "
            f"{_e(predicate)} = {_e(obj)}"
            f"<pre>{_e(evidence_text)}</pre>"
            "</li>"
        )
    return f"<ul>{''.join(items)}</ul>" if items else '<p class="muted">No graph triples.</p>'


def _render_review_questions(questions: Any) -> str:
    if not isinstance(questions, list) or not questions:
        return '<div class="panel"><h3>Review questions</h3><p class="muted">None.</p></div>'
    items = "".join(f"<li>{_e(str(question))}</li>" for question in questions)
    return f'<div class="panel"><h3>Review questions</h3><ul>{items}</ul></div>'


def _render_json_panel(title: str, payload: Any) -> str:
    return (
        '<div class="panel">'
        f"<h3>{_e(title)}</h3>"
        f"<pre>{_e(json.dumps(payload, indent=2, ensure_ascii=False))}</pre>"
        "</div>"
    )


def _summary_item(label: str, value: Any) -> str:
    return f'<span class="summary-item"><strong>{_e(str(value))}</strong>{_e(label)}</span>'


def _pill(value: str) -> str:
    return f'<span class="pill">{_e(value)}</span>'


def _csv_columns(cases: list[dict[str, Any]]) -> list[str]:
    if not cases:
        return []
    return list(cases[0]["csv_row"].keys())


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _resolve(root: Path, path: str | Path) -> Path:
    source = Path(path)
    return source if source.is_absolute() else root / source


def _json_script(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")


def _e(value: str) -> str:
    return html.escape(value, quote=False)


def _attr(value: str) -> str:
    return html.escape(value, quote=True)


def _stylesheet() -> str:
    return """
:root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
body { margin: 0; background: #f7f9fc; color: #172033; }
header, main { max-width: 1180px; margin: 0 auto; padding: 24px; }
h1 { margin: 0 0 8px; font-size: 28px; }
h2 { margin: 0; font-size: 18px; }
h3 { margin: 16px 0 8px; font-size: 13px; text-transform: uppercase; letter-spacing: .04em; }
p { line-height: 1.5; }
.summary { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
.summary-item { background: #fff; border: 1px solid #d9e2ef; border-radius: 6px; padding: 10px 12px; }
.summary-item strong { display: block; font-size: 20px; }
.controls { position: sticky; top: 0; z-index: 1; display: flex; gap: 10px; flex-wrap: wrap; padding: 12px; background: #eef4ff; border: 1px solid #c9d8f2; border-radius: 8px; }
input, select, textarea, button { font: inherit; border: 1px solid #b9c7dc; border-radius: 6px; padding: 8px; background: #fff; }
button { cursor: pointer; background: #1f5fbf; color: #fff; border-color: #1f5fbf; }
#clear-draft { background: #fff; color: #1f365d; }
#search { min-width: 320px; flex: 1; }
.boundary { color: #47566f; }
.case-list { display: grid; gap: 16px; margin-top: 18px; }
.case { background: #fff; border: 1px solid #d9e2ef; border-radius: 8px; padding: 18px; }
.case > header { padding: 0; display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.meta { display: flex; gap: 6px; flex-wrap: wrap; }
.pill { background: #eaf1ff; color: #1f4f98; border-radius: 999px; padding: 4px 8px; font-size: 12px; }
.question-answer { border-top: 1px solid #edf1f7; margin-top: 14px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.panel { background: #f8fafc; border: 1px solid #e3eaf5; border-radius: 6px; padding: 10px; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f3f6fb; padding: 10px; border-radius: 6px; }
.evidence ul, .panel ul { margin-top: 6px; padding-left: 18px; }
.review-form { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; border-top: 1px solid #edf1f7; margin-top: 14px; padding-top: 12px; }
.review-form h3 { grid-column: 1 / -1; margin-top: 0; }
label { display: grid; gap: 4px; color: #2d3b51; }
textarea { min-height: 86px; resize: vertical; }
.raw-response summary { cursor: pointer; margin-top: 12px; }
.muted { color: #708096; }
.hidden { display: none; }
""".strip()


def _script() -> str:
    return r"""
const storageKey = "nasa-atmonto-s7-answer-review-worksheet-v1";
const rows = JSON.parse(document.getElementById("csv-rows-data").textContent);
const columns = JSON.parse(document.getElementById("csv-columns-data").textContent);

function controls() {
  return Array.from(document.querySelectorAll("[data-review-id][data-field]"));
}

function draftKey(input) {
  return `${input.dataset.reviewId}:${input.dataset.field}`;
}

function restoreDraft() {
  const draft = JSON.parse(localStorage.getItem(storageKey) || "{}");
  for (const input of controls()) {
    const value = draft[draftKey(input)];
    if (value !== undefined) input.value = value;
  }
}

function saveDraft() {
  const draft = {};
  for (const input of controls()) draft[draftKey(input)] = input.value;
  localStorage.setItem(storageKey, JSON.stringify(draft));
}

function collectRows() {
  const byId = new Map(rows.map(row => [row.review_id, {...row}]));
  for (const input of controls()) {
    const row = byId.get(input.dataset.reviewId);
    if (row) row[input.dataset.field] = input.value;
  }
  return rows.map(row => byId.get(row.review_id));
}

function csvEscape(value) {
  const text = String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function downloadCsv() {
  const reviewedRows = collectRows();
  const lines = [columns.map(csvEscape).join(",")];
  for (const row of reviewedRows) {
    lines.push(columns.map(column => csvEscape(row[column])).join(","));
  }
  const blob = new Blob([lines.join("\n") + "\n"], {type: "text/csv;charset=utf-8"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv";
  link.click();
  URL.revokeObjectURL(url);
}

function applyFilters() {
  const search = document.getElementById("search").value.trim().toLowerCase();
  const priority = document.getElementById("priority-filter").value;
  for (const item of document.querySelectorAll(".case")) {
    const searchOk = !search || item.dataset.search.includes(search);
    const priorityOk = !priority || item.dataset.priority === priority;
    item.classList.toggle("hidden", !(searchOk && priorityOk));
  }
}

for (const input of controls()) input.addEventListener("input", saveDraft);
document.getElementById("export-csv").addEventListener("click", downloadCsv);
document.getElementById("search").addEventListener("input", applyFilters);
document.getElementById("priority-filter").addEventListener("change", applyFilters);
document.getElementById("clear-draft").addEventListener("click", () => {
  localStorage.removeItem(storageKey);
  location.reload();
});
restoreDraft();
applyFilters();
""".strip()
