from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report
from aviation_agentic_ai.reporting.atmonto.s7.llm_answer_generation import (
    DEFAULT_S7_ANSWER_REPORT_PATH,
)

DEFAULT_S7_LLM_REPORT_PATH = Path("reports/stages/nasa_atmonto_s7_llm_answer_generation.json")


def build_nasa_atmonto_s7_human_review_candidates(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    s7_answer_report_path: str | Path = DEFAULT_S7_ANSWER_REPORT_PATH,
    s7_llm_report_path: str | Path = DEFAULT_S7_LLM_REPORT_PATH,
    max_success_per_template: int = 1,
) -> dict[str, Any]:
    root = Path(repo_root)
    s7_path = resolve_report_path(root, s7_answer_report_path)
    llm_path = resolve_report_path(root, s7_llm_report_path)
    s7_report = read_json_object_or_empty(s7_path)
    llm_report = read_json_object_or_empty(llm_path)
    contexts = s7_context_index(s7_report)
    llm_records = [record for record in llm_report.get("records", []) if isinstance(record, dict)]
    failures = [record for record in llm_records if needs_human_review(record)]
    successes = balanced_success_examples(
        llm_records,
        max_success_per_template=max_success_per_template,
    )
    selected = failures + successes
    candidates = [
        review_candidate(index, record, contexts)
        for index, record in enumerate(selected, start=1)
    ]
    return {
        "source_family": "nasa_atmonto_s7_human_review_candidates",
        "status": "candidate_package_created",
        "metadata": {
            "s7_answer_report_path": project_relative_path(s7_path, root),
            "s7_llm_report_path": project_relative_path(llm_path, root),
            "source_llm_selected_cases": llm_report.get("metadata", {}).get(
                "selected_case_count"
            ),
            "failure_candidate_count": len(failures),
            "coverage_candidate_count": len(successes),
            "candidate_count": len(candidates),
            "boundary": (
                "This is a candidate package for human or supervisor review. "
                "It is not human-reviewed evidence until an external reviewer records decisions."
            ),
        },
        "aggregate_by_mode": llm_report.get("answer_quality", {}).get("aggregate_by_mode", {}),
        "candidates": candidates,
        "claim_boundary": (
            "Use this package to inspect source support, over-answer behavior, citation quality, "
            "and ontology/profile boundary cases. Do not cite it as expert certification."
        ),
    }


def resolve_report_path(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def s7_context_index(s7_report: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for record in s7_report.get("records", []):
        if not isinstance(record, dict):
            continue
        cq_id = str(record.get("cq_id") or "")
        for mode, result in (record.get("results") or {}).items():
            if isinstance(result, dict):
                index[(cq_id, str(mode))] = {
                    "question": record.get("question"),
                    "answer_set": list(record.get("answer_set", [])),
                    "expected_abstention": bool(record.get("expected_abstention")),
                    "fused_chunks": result.get("fused_chunks", []),
                    "graph_triples": result.get("graph_triples", []),
                }
    return index


def needs_human_review(record: dict[str, Any]) -> bool:
    metrics = record.get("metrics")
    if not isinstance(metrics, dict):
        return True
    return (
        metrics.get("answer_correctness") is not True
        or metrics.get("evidence_faithfulness") is not True
        or float(metrics.get("unsupported_claim_rate") or 0.0) > 0.0
    )


def balanced_success_examples(
    records: list[dict[str, Any]],
    *,
    max_success_per_template: int,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    counts: dict[str, int] = defaultdict(int)
    for record in records:
        if needs_human_review(record):
            continue
        template_id = str(record.get("template_id") or "")
        if counts[template_id] >= max_success_per_template:
            continue
        selected.append(record)
        counts[template_id] += 1
    return selected


def review_candidate(
    index: int,
    record: dict[str, Any],
    contexts: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    cq_id = str(record.get("cq_id") or "")
    mode = str(record.get("mode") or "")
    context = contexts.get((cq_id, mode), {})
    return {
        "review_id": f"S7-HR-{index:03d}",
        "review_status": "candidate_not_reviewed",
        "priority": "failure" if needs_human_review(record) else "coverage_success",
        "template_id": record.get("template_id"),
        "cq_id": cq_id,
        "source_id": record.get("source_id"),
        "mode": mode,
        "question": context.get("question"),
        "expected_answer_set": context.get("answer_set", list(record.get("answer_set", []))),
        "expected_abstention": context.get("expected_abstention", record.get("expected_abstention")),
        "answer": record.get("answer"),
        "answer_values": record.get("answer_values", []),
        "abstain": bool(record.get("abstain")),
        "metrics": record.get("metrics", {}),
        "evidence": {
            "source_chunks": compact_chunks(context.get("fused_chunks", [])),
            "graph_triples": compact_triples(context.get("graph_triples", [])),
        },
        "review_questions": review_questions_for_record(record),
        "raw_response": record.get("raw_response"),
    }


def compact_chunks(chunks: Any, limit: int = 2) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for item in chunks if isinstance(chunks, list) else []:
        if not isinstance(item, dict):
            continue
        compact.append(
            {
                "chunk_id": item.get("chunk_id"),
                "source_id": item.get("source_id"),
                "text": trim_text(item.get("text")),
            }
        )
        if len(compact) >= limit:
            break
    return compact


def compact_triples(triples: Any, limit: int = 4) -> list[dict[str, Any]]:
    compact: list[dict[str, Any]] = []
    for item in triples if isinstance(triples, list) else []:
        if not isinstance(item, dict):
            continue
        compact.append(
            {
                "triple_id": item.get("triple_id"),
                "predicate": item.get("predicate"),
                "object": item.get("object"),
                "evidence_text": trim_text(item.get("evidence_text")),
            }
        )
        if len(compact) >= limit:
            break
    return compact


def trim_text(value: Any, limit: int = 360) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def review_questions_for_record(record: dict[str, Any]) -> list[str]:
    metrics = record.get("metrics") if isinstance(record.get("metrics"), dict) else {}
    questions = [
        "Does each answer value appear directly supported by the cited source span or graph triple?",
        "Does the answer include only predicates required by the CQ template and current profile?",
        "Are citations sufficient to trace the answer back to source evidence?",
    ]
    if metrics.get("answer_correctness") is not True:
        questions.append("If incorrect, is the issue model over-answer, retrieval context, or label/profile design?")
    if float(metrics.get("unsupported_claim_rate") or 0.0) > 0.0:
        questions.append("Which returned predicate/value pair is unsupported or out of profile?")
    if bool(record.get("expected_abstention")):
        questions.append("Should this case abstain, or is there enough evidence for a bounded partial answer?")
    return questions


def write_nasa_atmonto_s7_human_review_candidates_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S7 Human Review Candidate Package",
        "",
        "## Boundary",
        "",
        result["metadata"]["boundary"],
        "",
        "## Summary",
        "",
        f"- Source LLM cases: {result['metadata']['source_llm_selected_cases']}",
        f"- Failure candidates: {result['metadata']['failure_candidate_count']}",
        f"- Coverage success candidates: {result['metadata']['coverage_candidate_count']}",
        f"- Candidate total: {result['metadata']['candidate_count']}",
        "",
        "## Candidate Index",
        "",
        "| Review ID | Priority | Template | Mode | Source | Correct | Unsupported |",
        "| --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for item in result["candidates"]:
        metrics = item.get("metrics", {})
        lines.append(
            f"| `{item['review_id']}` | {item['priority']} | `{item['template_id']}` | "
            f"`{item['mode']}` | `{item['source_id']}` | "
            f"{metrics.get('answer_correctness')} | {metrics.get('unsupported_claim_rate')} |"
        )
    lines.extend(["", "## Candidate Details", ""])
    for item in result["candidates"]:
        lines.extend(candidate_markdown(item))
    lines.extend(["", "## Claim Boundary", "", result["claim_boundary"]])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def candidate_markdown(item: dict[str, Any]) -> list[str]:
    metrics = item.get("metrics", {})
    lines = [
        f"### {item['review_id']} - {item['priority']}",
        "",
        f"- Template: `{item['template_id']}`",
        f"- Mode: `{item['mode']}`",
        f"- Source: `{item['source_id']}`",
        f"- Question: {item.get('question') or 'n/a'}",
        f"- Expected: `{', '.join(item.get('expected_answer_set') or [])}`",
        f"- Answer values: `{item.get('answer_values')}`",
        f"- Metrics: correctness={metrics.get('answer_correctness')}, "
        f"faithfulness={metrics.get('evidence_faithfulness')}, "
        f"unsupported={metrics.get('unsupported_claim_rate')}",
        "",
        "**Evidence Chunks**",
        "",
    ]
    chunks = item.get("evidence", {}).get("source_chunks", [])
    if chunks:
        for chunk in chunks:
            lines.append(f"- `{chunk.get('chunk_id')}`: {chunk.get('text')}")
    else:
        lines.append("- none")
    lines.extend(["", "**Graph Triples**", ""])
    triples = item.get("evidence", {}).get("graph_triples", [])
    if triples:
        for triple in triples:
            lines.append(
                f"- `{triple.get('triple_id')}` {triple.get('predicate')}="
                f"{triple.get('object')} | {triple.get('evidence_text')}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "**Review Questions**", ""])
    lines.extend(f"- {question}" for question in item.get("review_questions", []))
    lines.append("")
    return lines


def write_nasa_atmonto_s7_human_review_candidates(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    report_name: str = "nasa_atmonto_s7_human_review_candidates",
    max_success_per_template: int = 1,
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_human_review_candidates(
        repo_root=repo_root,
        max_success_per_template=max_success_per_template,
    )
    output = Path(output_dir)
    json_path = write_json_report(result, output / f"{report_name}.json")
    md_path = write_nasa_atmonto_s7_human_review_candidates_markdown(
        result,
        output / f"{report_name}.md",
    )
    return json_path, md_path, result
