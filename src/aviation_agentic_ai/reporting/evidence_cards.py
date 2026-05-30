from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.accessors import nested_value as _metric
from aviation_agentic_ai.reporting.io import (
    normalize_report_text as _normalize,
    read_json_object,
    write_json_report,
)


FAILURE_CATEGORIES = (
    "success",
    "retrieval miss",
    "chunk boundary problem",
    "KG sparsity",
    "graph noise",
    "hybrid fusion dilution",
    "citation mismatch",
    "abstention failure",
)


def _load_json(path: str | Path) -> dict[str, Any]:
    return read_json_object(path)


def _truthy(value: Any) -> bool:
    return bool(value) if value is not None else False


def _excerpt(text: Any, limit: int = 180) -> str:
    normalized = " ".join(str(text or "").split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _span_dicts(gold: dict[str, Any]) -> list[dict[str, Any]]:
    spans = gold.get("evidence_spans", [])
    return [span for span in spans if isinstance(span, dict)]


def _expected_abstention(gold: dict[str, Any]) -> bool:
    level = str(gold.get("gold_level", "")).strip().lower()
    return bool(gold.get("expected_abstention")) or level in {
        "no_answer",
        "none",
        "unsupported",
        "insufficient_evidence",
    }


def _chunk_summary(chunks: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for index, chunk in enumerate(chunks[:top_k], start=1):
        summaries.append(
            {
                "rank": chunk.get("rank", index),
                "chunk_id": str(chunk.get("chunk_id", "")),
                "page": chunk.get("page"),
                "source": chunk.get("source"),
                "score": chunk.get("score"),
                "excerpt": _excerpt(chunk.get("text", "")),
            }
        )
    return summaries


def _triple_summary(triples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": triple.get("rank"),
            "triple_id": str(triple.get("triple_id", "")),
            "chunk_id": str(triple.get("chunk_id", "")),
            "page": triple.get("page"),
            "subject": triple.get("subject"),
            "predicate": triple.get("predicate"),
            "object": triple.get("object"),
            "evidence_excerpt": _excerpt(triple.get("evidence_text", "")),
        }
        for triple in triples
    ]


def _mode_result(record: dict[str, Any], mode: str) -> dict[str, Any]:
    result = _metric(record, "results", mode, default={})
    return result if isinstance(result, dict) else {}


def _retrieval_metrics(result: dict[str, Any]) -> dict[str, Any]:
    metrics = _metric(result, "metrics", "retrieval", default={})
    return metrics if isinstance(metrics, dict) else {}


def _kg_metrics(result: dict[str, Any]) -> dict[str, Any]:
    metrics = _metric(result, "metrics", "kg_evidence", default={})
    return metrics if isinstance(metrics, dict) else {}


def _answer_metrics(result: dict[str, Any]) -> dict[str, Any]:
    metrics = _metric(result, "metrics", "llm_answer", default={})
    return metrics if isinstance(metrics, dict) else {}


def _retrieval_hit(result: dict[str, Any]) -> bool:
    return _truthy(_retrieval_metrics(result).get("recall_at_5"))


def _first_rank(result: dict[str, Any]) -> int | None:
    rank = _retrieval_metrics(result).get("first_relevant_rank")
    return int(rank) if rank is not None else None


def _retrieved_pages(result: dict[str, Any], top_k: int) -> list[int]:
    pages = _retrieval_metrics(result).get("retrieved_source_pages")
    if isinstance(pages, list):
        return [int(page) for page in pages[:top_k] if page is not None]
    return [
        int(chunk["page"])
        for chunk in result.get("fused_chunks", [])[:top_k]
        if chunk.get("page") is not None
    ]


def _triple_covers_entity(triple: dict[str, Any], key_entities: list[str]) -> bool:
    haystack = _normalize(" ".join(str(value) for value in triple.values()))
    return any(_normalize(entity) and _normalize(entity) in haystack for entity in key_entities)


def _triple_contains_span(triple: dict[str, Any], spans: list[dict[str, Any]]) -> bool:
    haystack = _normalize(
        " ".join(
            str(triple.get(field, ""))
            for field in ("subject", "predicate", "object", "evidence_text")
        )
    )
    for span in spans:
        text = _normalize(span.get("text", ""))
        if text and text in haystack:
            return True
    return False


def _triple_is_useful(triple: dict[str, Any], gold: dict[str, Any]) -> bool:
    expected_chunks = {str(chunk_id) for chunk_id in gold.get("expected_chunk_ids", [])}
    expected_page = gold.get("source_page")
    key_entities = [str(entity) for entity in gold.get("key_entities", [])]
    if str(triple.get("chunk_id", "")) in expected_chunks:
        return True
    if expected_page is not None and int(triple.get("page", -9999)) == int(expected_page):
        return True
    if _triple_covers_entity(triple, key_entities):
        return True
    return _triple_contains_span(triple, _span_dicts(gold))


def _partition_triples(
    triples: list[dict[str, Any]],
    gold: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    useful: list[dict[str, Any]] = []
    noisy: list[dict[str, Any]] = []
    for triple in triples:
        if _triple_is_useful(triple, gold):
            useful.append(triple)
        else:
            noisy.append(triple)
    return useful, noisy


def _retrieval_summary(result: dict[str, Any], top_k: int) -> dict[str, Any]:
    metrics = _retrieval_metrics(result)
    return {
        "top_5_chunks": _chunk_summary(result.get("fused_chunks", []), top_k),
        "hit": bool(metrics.get("recall_at_5", False)),
        "first_relevant_rank": metrics.get("first_relevant_rank"),
    }


def _graph_effect(vector_result: dict[str, Any], hybrid_result: dict[str, Any]) -> str:
    vector_hit = _retrieval_hit(vector_result)
    hybrid_hit = _retrieval_hit(hybrid_result)
    vector_rank = _first_rank(vector_result)
    hybrid_rank = _first_rank(hybrid_result)
    if hybrid_hit and not vector_hit:
        return "helped"
    if vector_hit and not hybrid_hit:
        return "hurt"
    if vector_hit and hybrid_hit and vector_rank is not None and hybrid_rank is not None:
        if hybrid_rank < vector_rank:
            return "helped"
        if hybrid_rank > vector_rank:
            return "hurt"
    return "neutral"


def _citation_status(result: dict[str, Any]) -> dict[str, Any]:
    answer = _answer_metrics(result)
    return {
        "citation_completeness": bool(answer.get("citation_completeness", False)),
        "valid_chunk_citation": bool(answer.get("valid_chunk_citation", False)),
        "valid_page_citation": bool(answer.get("valid_page_citation", False)),
        "valid_triple_citation": bool(answer.get("valid_triple_citation", False)),
        "valid_citations": list(answer.get("valid_citations", [])),
        "insufficient_evidence_abstention": bool(
            answer.get("insufficient_evidence_abstention", False)
        ),
        "answer_present": bool(answer.get("answer_present", bool(result.get("answer", "")))),
    }


def _gold_evidence(record: dict[str, Any]) -> dict[str, Any]:
    gold = record.get("gold", {}) if isinstance(record.get("gold", {}), dict) else {}
    return {
        "expected_page": gold.get("source_page", record.get("source_page")),
        "expected_chunk_ids": [str(chunk_id) for chunk_id in gold.get("expected_chunk_ids", [])],
        "expected_spans": [
            {
                "page": span.get("page"),
                "text": span.get("text", ""),
                "char_start": span.get("char_start"),
                "char_end": span.get("char_end"),
            }
            for span in _span_dicts(gold)
        ],
        "key_entities": [str(entity) for entity in gold.get("key_entities", record.get("key_entities", []))],
        "gold_level": gold.get("gold_level", "page"),
        "expected_abstention": _expected_abstention(gold),
    }


def _failure_category(
    *,
    gold: dict[str, Any],
    vector_result: dict[str, Any],
    graph_result: dict[str, Any],
    hybrid_result: dict[str, Any],
    useful_triples: list[dict[str, Any]],
    noisy_triples: list[dict[str, Any]],
    graph_effect: str,
    top_k: int,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    expected_abstention = _expected_abstention(gold)
    actual_abstention = _citation_status(hybrid_result)["insufficient_evidence_abstention"]
    if expected_abstention != actual_abstention:
        return "abstention failure", ["expected abstention did not match the final answer"]

    vector_hit = _retrieval_hit(vector_result)
    graph_hit = _retrieval_hit(graph_result)
    hybrid_hit = _retrieval_hit(hybrid_result)
    expected_page = gold.get("source_page")
    retrieved_pages = (
        _retrieved_pages(vector_result, top_k)
        + _retrieved_pages(graph_result, top_k)
        + _retrieved_pages(hybrid_result, top_k)
    )
    has_expected_page = (
        expected_page is not None
        and int(expected_page) >= 0
        and int(expected_page) in retrieved_pages
    )
    if not (vector_hit or graph_hit or hybrid_hit) and not has_expected_page:
        return "retrieval miss", ["no retrieval mode recovered the gold evidence"]
    if not (vector_hit or graph_hit or hybrid_hit) and has_expected_page:
        return "chunk boundary problem", [
            "retrieval reached the expected page but missed the expected chunk or span"
        ]
    if graph_effect == "hurt":
        return "hybrid fusion dilution", ["hybrid fusion degraded vector retrieval"]

    graph_coverage = bool(_kg_metrics(graph_result).get("evidence_coverage", False))
    if hybrid_hit and not useful_triples and not graph_coverage:
        return "KG sparsity", ["retrieval found text evidence but graph evidence was sparse"]
    if noisy_triples and len(noisy_triples) > len(useful_triples):
        return "graph noise", ["noisy graph triples outnumbered useful graph triples"]

    citation = _citation_status(hybrid_result)
    if hybrid_hit and not citation["citation_completeness"]:
        return "citation mismatch", ["hybrid retrieved evidence but final citations were incomplete"]

    if reasons:
        return "success", reasons
    return "success", []


def _build_card(record: dict[str, Any], top_k: int) -> dict[str, Any]:
    gold = record.get("gold", {}) if isinstance(record.get("gold", {}), dict) else {}
    vector_result = _mode_result(record, "vector")
    graph_result = _mode_result(record, "graph")
    hybrid_result = _mode_result(record, "hybrid")
    graph_triples = graph_result.get("graph_triples", [])
    useful_triples, noisy_triples = _partition_triples(graph_triples, gold)
    effect = _graph_effect(vector_result, hybrid_result)
    category, reasons = _failure_category(
        gold=gold,
        vector_result=vector_result,
        graph_result=graph_result,
        hybrid_result=hybrid_result,
        useful_triples=useful_triples,
        noisy_triples=noisy_triples,
        graph_effect=effect,
        top_k=top_k,
    )
    graph_metrics = _kg_metrics(graph_result)
    return {
        "cq_id": str(record.get("cq_id", "")),
        "question": str(record.get("question", "")),
        "gold_evidence": _gold_evidence(record),
        "vector_retrieval": _retrieval_summary(vector_result, top_k),
        "graph_retrieval": {
            "retrieved_triples": _triple_summary(graph_triples),
            "entity_coverage": {
                "covered": bool(graph_metrics.get("key_entity_coverage", graph_metrics.get("evidence_coverage", False))),
                "covered_entities": list(graph_metrics.get("key_entities_covered", [])),
            },
            "useful_triples": _triple_summary(useful_triples),
            "noisy_triples": _triple_summary(noisy_triples),
        },
        "hybrid_retrieval": {
            "fused_top_5_chunks": _chunk_summary(hybrid_result.get("fused_chunks", []), top_k),
            "hit": _retrieval_hit(hybrid_result),
            "first_relevant_rank": _first_rank(hybrid_result),
            "graph_effect": effect,
            "citation_status": _citation_status(hybrid_result),
        },
        "failure_category": category,
        "failure_reasons": reasons,
    }


def build_evidence_cards(experiment: dict[str, Any], top_k: int = 5) -> dict[str, Any]:
    cards = [
        _build_card(record, top_k)
        for record in experiment.get("records", [])
        if isinstance(record, dict)
    ]
    return {
        "metadata": {
            "source_report": experiment.get("metadata", {}).get("run_manifest", {}).get("run_id"),
            "top_k": top_k,
            "cards_total": len(cards),
            "failure_categories": list(FAILURE_CATEGORIES),
        },
        "cards": cards,
    }


def write_evidence_cards_json(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(result, output_path)


def evidence_cards_markdown_lines(result: dict[str, Any], heading_level: int = 2) -> list[str]:
    heading = "#" * heading_level
    lines = [
        f"{heading} Per-Question Evidence Cards",
        "",
        f"- Cards: {result['metadata']['cards_total']}",
        f"- Top K: {result['metadata']['top_k']}",
        "",
    ]
    for card in result["cards"]:
        gold = card["gold_evidence"]
        vector = card["vector_retrieval"]
        graph = card["graph_retrieval"]
        hybrid = card["hybrid_retrieval"]
        citation = hybrid["citation_status"]
        lines.extend(
            [
                f"{heading}# {card['cq_id']}",
                "",
                f"- Question: {card['question']}",
                f"- Failure category: {card['failure_category']}",
                f"- Expected page: {gold['expected_page']}",
                f"- Expected chunks: {', '.join(gold['expected_chunk_ids']) or 'none'}",
                f"- Key entities: {', '.join(gold['key_entities']) or 'none'}",
                f"- Vector top-5 chunks: {_format_chunk_ids(vector['top_5_chunks'])}",
                f"- Vector hit/miss: {'hit' if vector['hit'] else 'miss'}",
                f"- Vector first relevant rank: {vector['first_relevant_rank']}",
                f"- Graph retrieved triples: {len(graph['retrieved_triples'])}",
                f"- Graph entity coverage: {graph['entity_coverage']['covered']}",
                f"- Useful / noisy triples: {len(graph['useful_triples'])} / {len(graph['noisy_triples'])}",
                f"- Hybrid fused top-5 chunks: {_format_chunk_ids(hybrid['fused_top_5_chunks'])}",
                f"- Graph helped or hurt: {hybrid['graph_effect']}",
                f"- Final answer citation status: {citation['citation_completeness']}",
                "",
            ]
        )
        if card["failure_reasons"]:
            lines.extend(
                [
                    "- Failure reasons: "
                    + "; ".join(str(reason) for reason in card["failure_reasons"]),
                    "",
                ]
            )
    return lines


def _format_chunk_ids(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "none"
    return ", ".join(
        f"{chunk['rank']}:{chunk['chunk_id']}@p{chunk['page']}" for chunk in chunks
    )


def write_evidence_cards_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Evidence Cards", ""] + evidence_cards_markdown_lines(result)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_evidence_cards(
    output_dir: str | Path,
    *,
    hybrid_report_path: str | Path,
    report_name: str = "evidence_cards",
    top_k: int = 5,
) -> tuple[Path, Path, dict[str, Any]]:
    experiment = _load_json(hybrid_report_path)
    result = build_evidence_cards(experiment, top_k=top_k)
    result["metadata"]["hybrid_report_path"] = project_relative_path(hybrid_report_path)
    output = Path(output_dir)
    stem = Path(report_name).stem or "evidence_cards"
    json_path = write_evidence_cards_json(result, output / f"{stem}.json")
    md_path = write_evidence_cards_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
