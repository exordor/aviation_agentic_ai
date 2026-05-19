from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from aviation_agentic_ai.evaluation.cost_latency import cost_latency_block
from aviation_agentic_ai.evaluation.metrics import answer_metrics
from aviation_agentic_ai.evaluation.protocol import build_run_manifest, embedding_metadata
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.retrieval.hybrid import run_retrieval
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME


QueryRunner = Callable[..., dict[str, Any]]


def _run_retrieval_with_deterministic_answer(*args: Any, **kwargs: Any) -> dict[str, Any]:
    result = run_retrieval(*args, **kwargs)
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
    return {
        "retrieval_stability": retrieval_stable,
        "citation_stability": citation_stable,
        "kg_evidence_stability": bool(result.get("graph_triples")) or expected_abstention,
        "answer_stability": bool(result.get("answer", "").strip()),
        "abstention_correctness": abstention_correct,
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
    return {
        key: round(sum(int(record["metrics"][key]) for record in records) / denominator, 4)
        for key in keys
    } | {"cases_total": len(records)}


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
