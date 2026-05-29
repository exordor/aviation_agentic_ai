from __future__ import annotations

import json
import re
from pathlib import Path
from time import perf_counter
from typing import Any

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.evaluation.cost_latency import cost_latency_block
from aviation_agentic_ai.evaluation.gold import GoldLabel, load_gold_labels
from aviation_agentic_ai.evaluation.metrics import answer_metrics
from aviation_agentic_ai.evaluation.protocol import build_run_manifest
from aviation_agentic_ai.paths import project_relative_path


def _load_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        return {}
    payload = json.loads(source.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _normalize(text: str) -> str:
    return " ".join(str(text).lower().split())


def _citation_correct(result: dict[str, Any], gold: GoldLabel) -> bool:
    metrics = answer_metrics(result)
    if gold.expected_abstention:
        return bool(metrics["insufficient_evidence_abstention"])
    answer_lower = _normalize(result.get("answer", ""))
    expected_chunks = [chunk_id.lower() for chunk_id in gold.expected_chunk_ids]
    if expected_chunks and any(chunk_id in answer_lower for chunk_id in expected_chunks):
        return True
    if gold.source_page >= 0 and re.search(rf"\bpage\s*[=:]?\s*{gold.source_page}\b", answer_lower):
        return True
    return bool(metrics["citation_completeness"]) and not expected_chunks


def _advisory_boundary_violation(answer: str) -> bool:
    normalized = _normalize(answer)
    forbidden_patterns = (
        "replace poh",
        "replace the poh",
        "replace checklist",
        "ignore atc",
        "instead of pilot judgment",
        "safe for flight without",
        "certified cockpit",
    )
    return any(pattern in normalized for pattern in forbidden_patterns)


def _evaluate_answer(result: dict[str, Any], gold: GoldLabel) -> dict[str, Any]:
    metrics = answer_metrics(result)
    citation_correct = _citation_correct(result, gold)
    abstained = bool(metrics["insufficient_evidence_abstention"])
    abstention_correct = abstained if gold.expected_abstention else not abstained
    answer = str(result.get("answer", ""))
    answer_lower = _normalize(answer)
    answer_key_terms = [
        term
        for term in re.findall(r"[a-z0-9']+", gold.answer_key.lower())
        if len(term) > 4
    ]
    relevance = (
        True
        if gold.expected_abstention and abstained
        else bool(answer_key_terms)
        and sum(int(term in answer_lower) for term in set(answer_key_terms))
        >= min(2, len(set(answer_key_terms)))
    )
    faithfulness = citation_correct and abstention_correct
    answer_correctness = relevance and faithfulness
    return {
        "citation_completeness": bool(metrics["citation_completeness"]),
        "citation_precision": metrics["citation_precision"],
        "citation_recall": metrics["citation_recall"],
        "citation_correctness": citation_correct,
        "answer_faithfulness": faithfulness,
        "faithfulness": faithfulness,
        "answer_correctness": answer_correctness,
        "answer_relevance": relevance,
        "abstention_correctness": abstention_correct,
        "expected_abstention": gold.expected_abstention,
        "actual_abstention": abstained,
        "advisory_boundary_violation": _advisory_boundary_violation(answer),
        "valid_citations": metrics["valid_citations"],
        "detected_citations": metrics["detected_citations"],
        "available_citation_units": metrics["available_citation_units"],
        "score_methods": {
            "faithfulness": "deterministic_heuristic",
            "answer_correctness": "deterministic_heuristic",
            "answer_relevance": "deterministic_heuristic",
            "citation_precision": "deterministic_heuristic",
            "citation_recall": "deterministic_heuristic",
            "llm_as_judge": "not_run",
            "manual_review": "not_run",
        },
        "llm_judge": {
            "enabled": False,
            "faithfulness": None,
            "answer_correctness": None,
            "answer_relevance": None,
        },
    }


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    denominator = len(records) or 1
    return {
        "answers_total": len(records),
        "citation_completeness": round(
            sum(int(item["metrics"]["citation_completeness"]) for item in records) / denominator,
            4,
        ),
        "citation_correctness": round(
            sum(int(item["metrics"]["citation_correctness"]) for item in records) / denominator,
            4,
        ),
        "citation_precision": round(
            sum(float(item["metrics"]["citation_precision"]) for item in records)
            / denominator,
            4,
        ),
        "citation_recall": round(
            sum(float(item["metrics"]["citation_recall"]) for item in records)
            / denominator,
            4,
        ),
        "answer_faithfulness": round(
            sum(int(item["metrics"]["answer_faithfulness"]) for item in records) / denominator,
            4,
        ),
        "faithfulness": round(
            sum(int(item["metrics"]["faithfulness"]) for item in records) / denominator,
            4,
        ),
        "answer_correctness": round(
            sum(int(item["metrics"]["answer_correctness"]) for item in records) / denominator,
            4,
        ),
        "answer_relevance": round(
            sum(int(item["metrics"]["answer_relevance"]) for item in records) / denominator,
            4,
        ),
        "abstention_correctness": round(
            sum(int(item["metrics"]["abstention_correctness"]) for item in records)
            / denominator,
            4,
        ),
        "advisory_boundary_violation_count": sum(
            int(item["metrics"]["advisory_boundary_violation"]) for item in records
        ),
    }


def build_answer_evaluation(
    *,
    gold_labels_path: str | Path,
    hybrid_report_path: str | Path,
    command: str = "aviation-ai report answer-eval",
) -> dict[str, Any]:
    started = perf_counter()
    gold_labels = load_gold_labels(gold_labels_path)
    report = _load_json(hybrid_report_path)
    mode_records: dict[str, list[dict[str, Any]]] = {"vector": [], "graph": [], "hybrid": []}

    for record in report.get("records", []):
        gold = gold_labels.get(str(record.get("cq_id")))
        if gold is None:
            continue
        for mode, result in record.get("results", {}).items():
            if mode not in mode_records:
                mode_records[mode] = []
            mode_records[mode].append(
                {
                    "cq_id": record.get("cq_id"),
                    "question": record.get("question", gold.question),
                    "mode": mode,
                    "gold": gold.to_dict(),
                    "answer": result.get("answer", ""),
                    "metrics": _evaluate_answer(result, gold),
                }
            )

    aggregate = {mode: _aggregate(records) for mode, records in mode_records.items()}
    answers_total = sum(len(records) for records in mode_records.values())
    run_manifest = build_run_manifest(
        "answer_evaluation",
        parameters={"gold_labels_path": project_relative_path(gold_labels_path)},
        artifacts={"hybrid_report_path": hybrid_report_path},
        rebuild_policy={"chunks": False, "indexes": False, "kg": False},
        collection_name="not_used",
        chunking_strategy="report_artifact",
        command=command,
        llm={"provider": "none", "model": "not_used"},
        embedding={"backend": "not_used", "collection_name": "not_used"},
    )
    return {
        "metadata": {
            "run_manifest": run_manifest,
            "advisory_boundary": ADVISORY_BOUNDARY,
            "gold_labels_path": project_relative_path(gold_labels_path),
            "hybrid_report_path": project_relative_path(hybrid_report_path),
            "answers_total": answers_total,
            "scoring_policy": "answer_metrics_no_mixed_overall_score",
            "cost_latency": cost_latency_block(
                elapsed_seconds=perf_counter() - started,
                questions_total=len(gold_labels),
            ),
        },
        "aggregate": aggregate,
        "records": mode_records,
    }


def write_answer_evaluation_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_answer_evaluation_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Answer Evaluation",
        "",
        f"- Run ID: `{result['metadata']['run_manifest']['run_id']}`",
        f"- Answers: {result['metadata']['answers_total']}",
        "- Scoring: answer layer only; no retrieval/KG mixed total score.",
        "- Score method: deterministic heuristic unless an optional LLM/manual field is explicitly populated.",
        "",
        "| Mode | Answers | Citation complete | Citation precision | Citation recall | Citation correct | Faithfulness | Answer correctness | Relevance | Abstention correct | Boundary violations |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode, aggregate in result["aggregate"].items():
        lines.append(
            f"| {mode} | {aggregate['answers_total']} | {aggregate['citation_completeness']} | "
            f"{aggregate['citation_precision']} | {aggregate['citation_recall']} | "
            f"{aggregate['citation_correctness']} | {aggregate['faithfulness']} | "
            f"{aggregate['answer_correctness']} | {aggregate['answer_relevance']} | "
            f"{aggregate['abstention_correctness']} | "
            f"{aggregate['advisory_boundary_violation_count']} |"
        )
    lines.extend(["", "## Advisory Boundary", "", result["metadata"]["advisory_boundary"], ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_answer_evaluation(
    output_dir: str | Path,
    *,
    gold_labels_path: str | Path,
    hybrid_report_path: str | Path,
    report_name: str = "answer_evaluation",
    command: str = "aviation-ai report answer-eval",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_answer_evaluation(
        gold_labels_path=gold_labels_path,
        hybrid_report_path=hybrid_report_path,
        command=command,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "answer_evaluation"
    json_path = write_answer_evaluation_json(result, output / f"{stem}.json")
    md_path = write_answer_evaluation_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
