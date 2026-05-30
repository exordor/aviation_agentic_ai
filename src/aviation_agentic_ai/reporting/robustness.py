from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from aviation_agentic_ai.evaluation.cost_latency import cost_latency_block
from aviation_agentic_ai.evaluation.metrics import answer_metrics
from aviation_agentic_ai.evaluation.protocol import build_run_manifest, embedding_metadata
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.retrieval.sufficiency import (
    detect_risk_category,
    evaluate_evidence_sufficiency,
)
from aviation_agentic_ai.retrieval.hybrid import run_retrieval
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME


QueryRunner = Callable[..., dict[str, Any]]


def _run_retrieval_with_deterministic_answer(*args: Any, **kwargs: Any) -> dict[str, Any]:
    result = run_retrieval(*args, **kwargs)
    question = str(args[0]) if args else str(kwargs.get("question", ""))
    decision = evaluate_evidence_sufficiency(question, result)
    result["sufficiency_decision"] = decision
    if decision["decision"] == "abstain":
        result["answer"] = (
            "The retrieved evidence is insufficient for a grounded answer. "
            f"Reason: {decision['reason']}"
        )
        return result
    chunk_ids = [str(item.get("chunk_id", "")) for item in result.get("fused_chunks", [])[:3]]
    triple_ids = [str(item.get("triple_id", "")) for item in result.get("graph_triples", [])[:3]]
    if chunk_ids or triple_ids:
        result["answer"] = "Retrieved supporting evidence. Citations: " + ", ".join(
            chunk_ids + triple_ids
        )
    else:
        result["answer"] = "The retrieved evidence is insufficient for a grounded answer."
    return result


def _load_cases(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    payload = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        cases = payload.get("cases", [])
        return [case for case in cases if isinstance(case, dict)]
    if isinstance(payload, list):
        return [case for case in payload if isinstance(case, dict)]
    return []


def _evaluate_case(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    expected_chunks = {str(item) for item in case.get("expected_chunk_ids", [])}
    retrieved_chunks = {
        str(item.get("chunk_id", "")) for item in result.get("fused_chunks", [])[:5]
    }
    expected_abstention = bool(case.get("expected_abstention", False))
    answer = answer_metrics(result)
    retrieval_stable = bool(expected_chunks & retrieved_chunks) if expected_chunks else True
    citation_stable = (
        bool(set(answer["valid_citations"]) & expected_chunks)
        if expected_chunks
        else bool(answer["citation_completeness"]) or expected_abstention
    )
    abstention_correct = (
        bool(answer["insufficient_evidence_abstention"]) if expected_abstention else True
    )
    actual_abstention = bool(answer["insufficient_evidence_abstention"])
    false_answer = expected_abstention and not actual_abstention
    false_abstention = not expected_abstention and actual_abstention
    risk_category = detect_risk_category(str(case.get("question", "")))[0]
    expected_risk_category = str(case.get("expected_risk_category") or risk_category)
    return {
        "retrieval_stability": retrieval_stable,
        "citation_stability": citation_stable,
        "kg_evidence_stability": bool(result.get("graph_triples")) or expected_abstention,
        "answer_stability": bool(result.get("answer", "").strip()),
        "abstention_correctness": abstention_correct,
        "abstention_accuracy": abstention_correct,
        "false_answer": false_answer,
        "false_abstention": false_abstention,
        "advisory_boundary_violation": false_answer,
        "risk_category": risk_category,
        "expected_risk_category": expected_risk_category,
        "risk_category_correct": risk_category == expected_risk_category,
        "retrieved_chunk_ids": sorted(retrieved_chunks),
        "valid_citations": answer["valid_citations"],
    }


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    denominator = len(records) or 1
    keys = (
        "retrieval_stability",
        "citation_stability",
        "kg_evidence_stability",
        "answer_stability",
        "abstention_correctness",
    )
    aggregate = {
        key: round(sum(int(record["metrics"][key]) for record in records) / denominator, 4)
        for key in keys
    }
    no_answer = [record for record in records if record["expected_abstention"]]
    supported = [record for record in records if not record["expected_abstention"]]
    aggregate.update(
        {
            "abstention_accuracy": aggregate["abstention_correctness"],
            "false_answer_rate": round(
                sum(int(record["metrics"]["false_answer"]) for record in no_answer)
                / max(len(no_answer), 1),
                4,
            ),
            "false_abstention_rate": round(
                sum(int(record["metrics"]["false_abstention"]) for record in supported)
                / max(len(supported), 1),
                4,
            ),
            "advisory_boundary_violation_count": sum(
                int(record["metrics"]["advisory_boundary_violation"])
                for record in records
            ),
            "risk_category_accuracy": round(
                sum(int(record["metrics"]["risk_category_correct"]) for record in records)
                / denominator,
                4,
            ),
            "cases_total": len(records),
        }
    )
    return aggregate


def build_robustness_evaluation(
    robustness_path: str | Path,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    mode: str = "hybrid",
    graph_hops: int = 2,
    vector_top_k: int = 5,
    hybrid_top_k: int = 8,
    query_runner: QueryRunner = _run_retrieval_with_deterministic_answer,
    command: str = "aviation-ai report robustness",
) -> dict[str, Any]:
    started = perf_counter()
    cases = _load_cases(robustness_path)
    records: list[dict[str, Any]] = []
    for case in cases:
        result = query_runner(
            case["question"],
            mode,
            chunks_path,
            kg_path,
            index_dir,
            collection_name=collection_name,
            graph_hops=graph_hops,
            vector_top_k=vector_top_k,
            hybrid_top_k=hybrid_top_k,
        )
        records.append(
            {
                "case_id": case.get("case_id"),
                "base_cq_id": case.get("base_cq_id"),
                "case_type": case.get("case_type", "unknown"),
                "question": case.get("question", ""),
                "expected_abstention": bool(case.get("expected_abstention", False)),
                "metrics": _evaluate_case(case, result),
                "result": {
                    "fused_chunks": result.get("fused_chunks", []),
                    "graph_triples": result.get("graph_triples", []),
                    "answer": result.get("answer", ""),
                },
            }
        )

    run_manifest = build_run_manifest(
        "robustness_evaluation",
        parameters={
            "mode": mode,
            "graph_hops": graph_hops,
            "vector_top_k": vector_top_k,
            "hybrid_top_k": hybrid_top_k,
        },
        artifacts={
            "robustness_path": robustness_path,
            "chunks_path": chunks_path,
            "kg_path": kg_path,
            "index_dir": index_dir,
        },
        rebuild_policy={"chunks": False, "indexes": False, "kg": False},
        collection_name=collection_name,
        chunking_strategy="structure_aware",
        command=command,
        llm={"provider": "none", "model": "not_used"},
        embedding=embedding_metadata(index_dir, collection_name),
    )
    return {
        "metadata": {
            "run_manifest": run_manifest,
            "robustness_path": project_relative_path(robustness_path),
            "chunks_path": project_relative_path(chunks_path),
            "kg_path": project_relative_path(kg_path),
            "index_dir": project_relative_path(index_dir),
            "collection_name": collection_name,
            "mode": mode,
            "cases_total": len(records),
            "cost_latency": cost_latency_block(
                elapsed_seconds=perf_counter() - started,
                cases_total=len(records),
                chunks_path=chunks_path,
                kg_path=kg_path,
                index_dir=index_dir,
            ),
        },
        "aggregate": _aggregate(records),
        "records": records,
    }


def write_robustness_evaluation_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_robustness_evaluation_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    aggregate = result["aggregate"]
    lines = [
        "# Robustness Evaluation",
        "",
        f"- Run ID: `{result['metadata']['run_manifest']['run_id']}`",
        f"- Cases: {result['metadata']['cases_total']}",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Retrieval stability | {aggregate['retrieval_stability']} |",
        f"| Citation stability | {aggregate['citation_stability']} |",
        f"| KG evidence stability | {aggregate['kg_evidence_stability']} |",
        f"| Answer stability | {aggregate['answer_stability']} |",
        f"| Abstention correctness | {aggregate['abstention_correctness']} |",
        f"| False answer rate | {aggregate['false_answer_rate']} |",
        f"| False abstention rate | {aggregate['false_abstention_rate']} |",
        f"| Advisory boundary violation count | {aggregate['advisory_boundary_violation_count']} |",
        f"| Risk category accuracy | {aggregate['risk_category_accuracy']} |",
        "",
        "## Cases",
        "",
    ]
    for record in result["records"]:
        lines.extend(
            [
                f"### {record['case_id']}",
                "",
                f"- Type: {record['case_type']}",
                f"- Base CQ: {record['base_cq_id']}",
                f"- Retrieval stable: {record['metrics']['retrieval_stability']}",
                f"- Abstention correct: {record['metrics']['abstention_correctness']}",
                "",
            ]
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_robustness_evaluation(
    robustness_path: str | Path,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    output_dir: str | Path,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    mode: str = "hybrid",
    graph_hops: int = 2,
    vector_top_k: int = 5,
    hybrid_top_k: int = 8,
    query_runner: QueryRunner = _run_retrieval_with_deterministic_answer,
    report_name: str = "robustness_evaluation",
    command: str = "aviation-ai report robustness",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_robustness_evaluation(
        robustness_path,
        chunks_path,
        kg_path,
        index_dir,
        collection_name=collection_name,
        mode=mode,
        graph_hops=graph_hops,
        vector_top_k=vector_top_k,
        hybrid_top_k=hybrid_top_k,
        query_runner=query_runner,
        command=command,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "robustness_evaluation"
    json_path = write_robustness_evaluation_json(result, output / f"{stem}.json")
    md_path = write_robustness_evaluation_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
