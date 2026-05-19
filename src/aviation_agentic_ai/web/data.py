from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path


STRUCTURE_AWARE_CHUNKS = "data/chunks/06_phak_ch4_0.structure_aware.jsonl"
STRUCTURE_AWARE_KG = "data/kg/06_phak_ch4_0.structure_aware.kg.jsonl"
STRUCTURE_AWARE_COLLECTION = "phak_ch4_chunks_structure_aware"
SUPPORTED_EXPERIMENTS = {"fixed_window", "structure_aware"}
SUPPORTED_MODES = {"vector", "graph", "hybrid"}


ARTIFACTS = {
    "gold_labels": "data/cqs/06_phak_ch4_0.gold.json",
    "fixed_hybrid": "reports/stages/hybrid_rag_experiment.json",
    "structure_aware_hybrid": "reports/stages/hybrid_rag_structure_aware.json",
    "evidence_level_evaluation": "reports/stages/evidence_level_evaluation.json",
    "graphrag_review": "reports/stages/graphrag_review.json",
    "structure_aware_kg": STRUCTURE_AWARE_KG,
    "structure_aware_chunks": STRUCTURE_AWARE_CHUNKS,
}


def _root(project_root: str | Path = PROJECT_ROOT) -> Path:
    return Path(project_root)


def _artifact_path(project_root: str | Path, key: str) -> Path:
    return _root(project_root) / ARTIFACTS[key]


def _read_json(path: str | Path) -> dict[str, Any] | None:
    source = Path(path)
    if not source.exists():
        return None
    data = json.loads(source.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"value": data}


def artifact_status(project_root: str | Path = PROJECT_ROOT) -> dict[str, dict[str, Any]]:
    root = _root(project_root)
    return {
        key: {
            "path": rel_path,
            "present": (root / rel_path).exists(),
        }
        for key, rel_path in ARTIFACTS.items()
    }


def _load_artifacts(project_root: str | Path) -> dict[str, Any]:
    return {
        key: _read_json(_artifact_path(project_root, key))
        for key in (
            "gold_labels",
            "fixed_hybrid",
            "structure_aware_hybrid",
            "evidence_level_evaluation",
            "graphrag_review",
        )
    }


def _gold_by_id(gold_payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not gold_payload:
        return {}
    labels = gold_payload.get("labels", [])
    return {
        str(label.get("cq_id")): label
        for label in labels
        if isinstance(label, dict) and label.get("cq_id")
    }


def _records_by_id(report: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not report:
        return {}
    return {
        str(record.get("cq_id")): record
        for record in report.get("records", [])
        if isinstance(record, dict) and record.get("cq_id")
    }


def _metric_value(data: dict[str, Any] | None, *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _compact_chunk(chunk: dict[str, Any]) -> dict[str, Any]:
    text = str(chunk.get("text", ""))
    return {
        "chunk_id": chunk.get("chunk_id"),
        "page": chunk.get("page"),
        "rank": chunk.get("rank"),
        "score": chunk.get("score"),
        "source": chunk.get("source"),
        "text": text,
        "text_preview": text[:600],
        "metadata": chunk.get("metadata", {}),
    }


def _compact_triple(triple: dict[str, Any]) -> dict[str, Any]:
    return {
        "triple_id": triple.get("triple_id"),
        "subject": triple.get("subject"),
        "subject_class": triple.get("subject_class"),
        "predicate": triple.get("predicate"),
        "object": triple.get("object"),
        "object_class": triple.get("object_class"),
        "chunk_id": triple.get("chunk_id"),
        "page": triple.get("page"),
        "rank": triple.get("rank"),
        "score": triple.get("score"),
        "evidence_text": triple.get("evidence_text"),
        "confidence": triple.get("confidence"),
    }


def _mode_payload(result: dict[str, Any] | None, eval_mode: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(result, dict):
        return {"present": False}
    return {
        "present": True,
        "answer": result.get("answer", ""),
        "metrics": result.get("metrics", {}),
        "evidence_eval": eval_mode or {},
        "fused_chunks": [
            _compact_chunk(chunk)
            for chunk in result.get("fused_chunks", [])
            if isinstance(chunk, dict)
        ],
        "graph_triples": [
            _compact_triple(triple)
            for triple in result.get("graph_triples", [])
            if isinstance(triple, dict)
        ],
        "vector_hits": [
            _compact_chunk(chunk)
            for chunk in result.get("vector_hits", [])
            if isinstance(chunk, dict)
        ],
        "graph_hits": [
            _compact_chunk(chunk)
            for chunk in result.get("graph_hits", [])
            if isinstance(chunk, dict)
        ],
    }


def _experiment_question_payload(
    record: dict[str, Any] | None,
    eval_record: dict[str, Any] | None,
) -> dict[str, Any]:
    if not record:
        return {"present": False}
    eval_modes = eval_record.get("modes", {}) if isinstance(eval_record, dict) else {}
    return {
        "present": True,
        "source_page": record.get("source_page"),
        "key_entities": record.get("key_entities", []),
        "modes": {
            mode: _mode_payload(record.get("results", {}).get(mode), eval_modes.get(mode))
            for mode in ("vector", "graph", "hybrid")
        },
    }


def _eval_records_by_id(
    evidence_eval: dict[str, Any] | None,
    experiment_name: str,
) -> dict[str, dict[str, Any]]:
    records = _metric_value(evidence_eval, "experiments", experiment_name, "records", default=[])
    return {
        str(record.get("cq_id")): record
        for record in records
        if isinstance(record, dict) and record.get("cq_id")
    }


def build_demo_status(
    project_root: str | Path = PROJECT_ROOT,
    *,
    live_query_enabled: bool = False,
) -> dict[str, Any]:
    status = artifact_status(project_root)
    fixed_present = status["fixed_hybrid"]["present"]
    structure_present = status["structure_aware_hybrid"]["present"]
    evidence_present = status["evidence_level_evaluation"]["present"]
    selected_default = "structure_aware" if structure_present and evidence_present else "fixed_window"
    return {
        "project": "aviation_agentic_ai",
        "ready": all(item["present"] for item in status.values()),
        "default_strategy": selected_default,
        "baseline_strategy": "fixed_window",
        "live_query_enabled": live_query_enabled,
        "live_query_default": {
            "mode": "hybrid",
            "chunks_path": STRUCTURE_AWARE_CHUNKS,
            "kg_path": STRUCTURE_AWARE_KG,
            "collection_name": STRUCTURE_AWARE_COLLECTION,
        },
        "artifacts": status,
        "advisory_boundary": ADVISORY_BOUNDARY,
        "summary": build_experiment_summary(project_root),
        "fixed_window_present": fixed_present,
        "structure_aware_present": structure_present,
    }


def build_questions(project_root: str | Path = PROJECT_ROOT) -> list[dict[str, Any]]:
    artifacts = _load_artifacts(project_root)
    gold = _gold_by_id(artifacts["gold_labels"])
    fixed_records = _records_by_id(artifacts["fixed_hybrid"])
    structure_records = _records_by_id(artifacts["structure_aware_hybrid"])
    cq_ids = sorted(set(gold) | set(fixed_records) | set(structure_records))
    questions: list[dict[str, Any]] = []
    for cq_id in cq_ids:
        record = structure_records.get(cq_id) or fixed_records.get(cq_id) or {}
        label = gold.get(cq_id, {})
        questions.append(
            {
                "cq_id": cq_id,
                "question": record.get("question", label.get("answer_key", "")),
                "source_page": label.get("source_page", record.get("source_page")),
                "gold_level": label.get("gold_level", "page"),
                "key_entities": label.get("key_entities", record.get("key_entities", [])),
            }
        )
    return questions


def build_question_detail(
    cq_id: str,
    project_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any] | None:
    artifacts = _load_artifacts(project_root)
    gold = _gold_by_id(artifacts["gold_labels"])
    fixed_records = _records_by_id(artifacts["fixed_hybrid"])
    structure_records = _records_by_id(artifacts["structure_aware_hybrid"])
    fixed_eval = _eval_records_by_id(artifacts["evidence_level_evaluation"], "fixed_window")
    structure_eval = _eval_records_by_id(artifacts["evidence_level_evaluation"], "structure_aware")
    if cq_id not in gold and cq_id not in fixed_records and cq_id not in structure_records:
        return None
    label = gold.get(cq_id, {})
    record = structure_records.get(cq_id) or fixed_records.get(cq_id) or {}
    return {
        "cq_id": cq_id,
        "question": record.get("question", label.get("answer_key", "")),
        "gold": label,
        "experiments": {
            "fixed_window": _experiment_question_payload(
                fixed_records.get(cq_id),
                fixed_eval.get(cq_id),
            ),
            "structure_aware": _experiment_question_payload(
                structure_records.get(cq_id),
                structure_eval.get(cq_id),
            ),
        },
    }


def _node_label(node_id: str) -> str:
    label = node_id.removeprefix("Cl_").removeprefix("Kg_")
    return label.replace("_", " ")


def _sorted_values(values: set[Any]) -> list[Any]:
    return sorted(values, key=lambda value: str(value))


def build_question_kg_graph(
    cq_id: str,
    project_root: str | Path = PROJECT_ROOT,
    *,
    experiment: str = "structure_aware",
    mode: str = "hybrid",
) -> dict[str, Any] | None:
    if experiment not in SUPPORTED_EXPERIMENTS:
        raise ValueError(f"Unsupported experiment: {experiment}")
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported retrieval mode: {mode}")

    detail = build_question_detail(cq_id, project_root)
    if detail is None:
        return None

    payload = (
        detail.get("experiments", {})
        .get(experiment, {})
        .get("modes", {})
        .get(mode, {})
    )
    triples = payload.get("graph_triples", []) if isinstance(payload, dict) else []
    nodes: dict[str, dict[str, Any]] = {}
    node_pages: dict[str, set[Any]] = {}
    edges: list[dict[str, Any]] = []

    def ensure_node(node_id: str, class_name: Any, page: Any) -> None:
        if node_id not in nodes:
            nodes[node_id] = {
                "id": node_id,
                "label": _node_label(node_id),
                "class": class_name or "Concept",
                "degree": 0,
                "source_pages": [],
            }
            node_pages[node_id] = set()
        if page is not None:
            node_pages[node_id].add(page)

    for index, triple in enumerate(triples):
        if not isinstance(triple, dict):
            continue
        subject = str(triple.get("subject") or "").strip()
        object_ = str(triple.get("object") or "").strip()
        predicate = str(triple.get("predicate") or "").strip()
        if not subject or not object_:
            continue
        page = triple.get("page")
        ensure_node(subject, triple.get("subject_class"), page)
        ensure_node(object_, triple.get("object_class"), page)
        nodes[subject]["degree"] += 1
        nodes[object_]["degree"] += 1
        triple_id = triple.get("triple_id") or f"{cq_id}-{mode}-triple-{index + 1}"
        edges.append(
            {
                "id": triple_id,
                "source": subject,
                "target": object_,
                "subject": subject,
                "object": object_,
                "predicate": predicate,
                "triple_id": triple_id,
                "chunk_id": triple.get("chunk_id"),
                "page": page,
                "evidence_text": triple.get("evidence_text"),
                "confidence": triple.get("confidence"),
                "score": triple.get("score"),
                "rank": triple.get("rank"),
            }
        )

    for node_id, node in nodes.items():
        node["source_pages"] = _sorted_values(node_pages[node_id])

    ordered_nodes = sorted(nodes.values(), key=lambda node: (-node["degree"], node["label"]))
    return {
        "metadata": {
            "cq_id": cq_id,
            "experiment": experiment,
            "mode": mode,
            "graph_scope": "question_scoped_retrieved_evidence",
            "triple_count": len(edges),
            "edge_count": len(edges),
            "node_count": len(ordered_nodes),
        },
        "nodes": ordered_nodes,
        "edges": edges,
    }


def _summary_for_experiment(evidence_eval: dict[str, Any] | None, name: str) -> dict[str, Any]:
    aggregate = _metric_value(evidence_eval, "experiments", name, "aggregate", default={})
    return {
        mode: aggregate.get(mode, {})
        for mode in ("vector", "graph", "hybrid")
        if isinstance(aggregate, dict)
    }


def build_experiment_summary(project_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    artifacts = _load_artifacts(project_root)
    evidence_eval = artifacts["evidence_level_evaluation"]
    fixed_hybrid = _metric_value(
        artifacts["fixed_hybrid"],
        "aggregate",
        "hybrid",
        default={},
    )
    structure_hybrid = _metric_value(
        artifacts["structure_aware_hybrid"],
        "aggregate",
        "hybrid",
        default={},
    )
    return {
        "scoring_policy": _metric_value(
            evidence_eval,
            "metadata",
            "scoring_policy",
            default="layered_metrics_no_mixed_overall_score",
        ),
        "selected_default_strategy": "structure_aware"
        if artifacts["structure_aware_hybrid"] and evidence_eval
        else "fixed_window",
        "hybrid_reports": {
            "fixed_window": fixed_hybrid,
            "structure_aware": structure_hybrid,
        },
        "evidence_level": {
            "fixed_window": _summary_for_experiment(evidence_eval, "fixed_window"),
            "structure_aware": _summary_for_experiment(evidence_eval, "structure_aware"),
        },
        "review_recommendations": _metric_value(
            artifacts["graphrag_review"],
            "recommendations",
            default=[],
        ),
    }


def project_path(path: str | Path, project_root: str | Path = PROJECT_ROOT) -> str:
    return project_relative_path(_root(project_root) / path, base=project_root)
