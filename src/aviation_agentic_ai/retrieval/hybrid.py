from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.chunking.chunks import read_chunks_jsonl
from aviation_agentic_ai.kg.extraction import KGTriple, read_kg_jsonl
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME, query_chroma_index
from aviation_agentic_ai.utils.io import write_json_document
from aviation_agentic_ai.utils.text import tokenize_terms


SOURCE_DELIMITER = "+"
UNKNOWN_SOURCE = "unknown"


def tokenize(text: str) -> set[str]:
    return tokenize_terms(text)


def graph_search(
    question: str,
    kg_path: str | Path,
    chunks_path: str | Path,
    top_k: int = 8,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Search KG triples lexically and return associated chunk evidence.

    This lexical search scores individual triples and does not traverse graph hops.
    Hop-bounded traversal is implemented by ``graph_search_traversal``.
    """
    query_terms = tokenize(question)
    chunks = {chunk.chunk_id: chunk for chunk in read_chunks_jsonl(chunks_path)}
    scored_triples: list[tuple[int, KGTriple]] = []
    for triple in read_kg_jsonl(kg_path):
        haystack = " ".join(
            [
                triple.subject,
                triple.predicate,
                triple.object,
                triple.subject_class,
                triple.object_class,
                triple.evidence_text,
            ]
        )
        score = len(query_terms & tokenize(haystack))
        if score > 0:
            scored_triples.append((score, triple))
    scored_triples.sort(key=lambda item: (-item[0], item[1].triple_id))

    triples: list[dict[str, Any]] = []
    chunk_scores: dict[str, float] = {}
    for rank, (score, triple) in enumerate(scored_triples[:top_k], start=1):
        triples.append({**triple.to_dict(), "rank": rank, "score": score})
        chunk_scores[triple.chunk_id] = max(chunk_scores.get(triple.chunk_id, 0.0), float(score))

    chunk_hits: list[dict[str, Any]] = []
    for rank, (chunk_id, score) in enumerate(
        sorted(chunk_scores.items(), key=lambda item: (-item[1], item[0])),
        start=1,
    ):
        chunk = chunks.get(chunk_id)
        if chunk is None:
            continue
        chunk_hits.append(
            {
                "chunk_id": chunk.chunk_id,
                "rank": rank,
                "score": score,
                "source": "graph",
                "page": chunk.page,
                "text": chunk.text,
                "metadata": {
                    "source_document": chunk.source_document,
                    "chunk_index": chunk.chunk_index,
                },
            }
        )
    return chunk_hits[:top_k], triples


def reciprocal_rank_fusion(
    ranked_lists: list[list[dict[str, Any]]],
    top_k: int,
    k: int = 60,
) -> list[dict[str, Any]]:
    scores: dict[str, float] = {}
    merged: dict[str, dict[str, Any]] = {}
    sources: dict[str, set[str]] = {}
    for ranked in ranked_lists:
        for rank, item in enumerate(ranked, start=1):
            chunk_id = str(item["chunk_id"])
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
            merged.setdefault(chunk_id, dict(item))
            sources.setdefault(chunk_id, set()).update(_source_set(item.get("source", "")))
    fused: list[dict[str, Any]] = []
    for rank, (chunk_id, score) in enumerate(
        sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:top_k],
        start=1,
    ):
        item = dict(merged[chunk_id])
        item["rank"] = rank
        item["score"] = score
        item["source"] = _format_source_set(sources[chunk_id])
        fused.append(item)
    return fused


def _source_set(value: Any) -> set[str]:
    return {
        source.strip()
        for source in str(value or "").split(SOURCE_DELIMITER)
        if source.strip() and source.strip() != UNKNOWN_SOURCE
    }


def _format_source_set(sources: set[str]) -> str:
    return SOURCE_DELIMITER.join(sorted(sources)) or UNKNOWN_SOURCE


def _merged_source(left: Any, right: Any) -> str:
    return _format_source_set(_source_set(left) | _source_set(right))


def _score(item: dict[str, Any]) -> float:
    """Return numeric retrieval score, treating missing or invalid values as zero."""
    try:
        return float(item.get("score", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _merge_duplicate_hit(
    existing: dict[str, Any],
    candidate: dict[str, Any],
    *,
    prefer_existing: bool = False,
) -> dict[str, Any]:
    winner = existing if prefer_existing or _score(existing) >= _score(candidate) else candidate
    merged = dict(winner)
    merged["source"] = _merged_source(existing.get("source"), candidate.get("source"))
    return merged


def _strong_graph_overlap(
    question: str,
    triples: list[dict[str, Any]],
    paths: list[dict[str, Any]],
) -> bool:
    question_terms = tokenize(question)
    if not question_terms or not (triples or paths):
        return False
    graph_text_parts: list[str] = []
    for triple in triples:
        graph_text_parts.extend(
            [
                str(triple.get("subject", "")),
                str(triple.get("predicate", "")),
                str(triple.get("object", "")),
                str(triple.get("evidence_text", "")),
            ]
        )
    for path in paths:
        for node in path.get("nodes", []):
            graph_text_parts.append(str(node.get("label") or node.get("node_id") or ""))
        for edge in path.get("edges", []):
            graph_text_parts.extend(
                [
                    str(edge.get("predicate", "")),
                    str(edge.get("evidence_text", "")),
                    str(edge.get("subject", "")),
                    str(edge.get("object", "")),
                ]
            )
    graph_terms = tokenize(" ".join(graph_text_parts))
    overlap = question_terms & graph_terms
    return len(overlap) >= 2


def vector_first_guarded_fusion(
    question: str,
    vector_hits: list[dict[str, Any]],
    graph_hits: list[dict[str, Any]],
    graph_triples: list[dict[str, Any]],
    graph_paths: list[dict[str, Any]],
    top_k: int,
    preserve_top_n: int = 2,
) -> list[dict[str, Any]]:
    """Fuse while preserving the strongest vector evidence unless graph overlap is strong."""
    protected = [dict(item) for item in vector_hits[:preserve_top_n]]
    fused_tail_source = (
        reciprocal_rank_fusion([vector_hits, graph_hits], top_k=top_k + preserve_top_n)
        if _strong_graph_overlap(question, graph_triples, graph_paths)
        else [*vector_hits, *graph_hits]
    )
    fused: list[dict[str, Any]] = []
    positions: dict[str, int] = {}
    protected_ids = {str(item["chunk_id"]) for item in protected}
    for item in [*protected, *fused_tail_source]:
        chunk_id = str(item["chunk_id"])
        if chunk_id in positions:
            fused[positions[chunk_id]] = _merge_duplicate_hit(
                fused[positions[chunk_id]],
                item,
                prefer_existing=chunk_id in protected_ids,
            )
            continue
        output = dict(item)
        output["source"] = str(output.get("source") or "unknown")
        fused.append(output)
        positions[chunk_id] = len(fused) - 1
    fused = fused[:top_k]
    for rank, item in enumerate(fused, start=1):
        item["rank"] = rank
    return fused


def build_answer_prompt(
    question: str,
    chunks: list[dict[str, Any]],
    triples: list[dict[str, Any]],
) -> str:
    chunk_context = "\n\n".join(
        (
            f"[chunk_id={item['chunk_id']} page={item.get('page')} source={item.get('source')}]\n"
            f"{item.get('text', '')[:1200]}"
        )
        for item in chunks
    )
    triple_context = "\n".join(
        (
            f"[triple_id={item['triple_id']} chunk_id={item['chunk_id']} page={item['page']}] "
            f"{item['subject']} ({item['subject_class']}) -{item['predicate']}-> "
            f"{item['object']} ({item['object_class']}); evidence: {item['evidence_text']}"
        )
        for item in triples
    )
    return (
        f"{ADVISORY_BOUNDARY} Answer only from the retrieved evidence below. Cite chunk "
        "ids, pages, and KG triple ids where used. If the evidence is insufficient, say "
        "that the current PHAK Chapter 4 materials do not support a grounded answer.\n\n"
        f"Question:\n{question}\n\n"
        f"Retrieved chunks:\n{chunk_context or 'None'}\n\n"
        f"KG evidence:\n{triple_context or 'None'}\n\n"
        "Return a concise answer with a 'Citations' line."
    )


def generate_grounded_answer(
    question: str,
    chunks: list[dict[str, Any]],
    triples: list[dict[str, Any]],
    temperature: float = 0.0,
    max_tokens: int = 1200,
) -> tuple[str, str]:
    prompt = build_answer_prompt(question, chunks, triples)
    if not chunks and not triples:
        return (
            "Insufficient evidence to generate a grounded answer because retrieval "
            "returned no chunks or KG triples for this question.\n\nCitations: none",
            prompt,
        )

    try:
        from langchain_core.messages import HumanMessage
    except ImportError as exc:
        raise RuntimeError(
            "Hybrid RAG answering requires optional ontology-generation dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    from aviation_agentic_ai.llm.providers import get_llm

    try:
        response = get_llm(temperature=temperature, max_tokens=max_tokens).invoke(
            [HumanMessage(content=prompt)]
        )
    except Exception as exc:
        return (
            "Insufficient evidence to generate an LLM answer because answer generation "
            f"failed with {type(exc).__name__}. Use the retrieved evidence directly "
            "instead of treating this as a generated answer.\n\nCitations: none",
            prompt,
        )
    return str(getattr(response, "content", response)).strip(), prompt


def run_retrieval(
    question: str,
    mode: str,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    graph_hops: int = 2,
    graph_method: str = "lexical",
    graph_fusion_policy: str = "rrf",
    aliases_path: str | Path | None = None,
    vector_top_k: int = 5,
    hybrid_top_k: int = 8,
) -> dict[str, Any]:
    if mode not in {"graph", "vector", "hybrid"}:
        raise ValueError(f"Unsupported retrieval mode: {mode}")
    if graph_method not in {"lexical", "traversal"}:
        raise ValueError(f"Unsupported graph retrieval method: {graph_method}")
    if graph_fusion_policy not in {"rrf", "vector_first_guarded"}:
        raise ValueError(f"Unsupported graph fusion policy: {graph_fusion_policy}")
    vector_hits: list[dict[str, Any]] = []
    graph_hits: list[dict[str, Any]] = []
    graph_triples: list[dict[str, Any]] = []
    graph_paths: list[dict[str, Any]] = []
    if mode in {"vector", "hybrid"}:
        vector_hits = query_chroma_index(
            question,
            index_dir=index_dir,
            collection_name=collection_name,
            top_k=vector_top_k,
        )
    if mode in {"graph", "hybrid"}:
        if graph_method == "lexical":
            graph_hits, graph_triples = graph_search(
                question,
                kg_path=kg_path,
                chunks_path=chunks_path,
                top_k=hybrid_top_k,
            )
        else:
            from aviation_agentic_ai.retrieval.graph_traversal import (
                graph_search_traversal,
            )

            graph_hits, graph_triples, graph_paths = graph_search_traversal(
                question,
                kg_path=kg_path,
                chunks_path=chunks_path,
                top_k=hybrid_top_k,
                graph_hops=graph_hops,
                aliases_path=aliases_path,
            )
    if mode == "vector":
        fused = vector_hits[:hybrid_top_k]
    elif mode == "graph":
        fused = graph_hits[:hybrid_top_k]
    elif graph_fusion_policy == "vector_first_guarded":
        fused = vector_first_guarded_fusion(
            question,
            vector_hits,
            graph_hits,
            graph_triples,
            graph_paths,
            top_k=hybrid_top_k,
        )
    else:
        fused = reciprocal_rank_fusion([vector_hits, graph_hits], top_k=hybrid_top_k)
    return {
        "question": question,
        "mode": mode,
        "graph_method": graph_method,
        "graph_fusion_policy": graph_fusion_policy,
        "graph_hops_requested": graph_hops,
        "graph_hops_effective": graph_hops if graph_method == "traversal" else None,
        "graph_hops_note": (
            "graph_hops applies only to traversal graph search; lexical graph search "
            "scores triples without hop expansion."
        )
        if graph_method == "lexical"
        else "",
        "vector_hits": vector_hits,
        "graph_hits": graph_hits,
        "graph_triples": graph_triples,
        "graph_paths": graph_paths,
        "fused_chunks": fused,
    }


def run_query(
    question: str,
    mode: str,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    graph_hops: int = 2,
    graph_method: str = "lexical",
    graph_fusion_policy: str = "rrf",
    aliases_path: str | Path | None = None,
    vector_top_k: int = 5,
    hybrid_top_k: int = 8,
    temperature: float = 0.0,
    max_tokens: int = 1200,
) -> dict[str, Any]:
    retrieval = run_retrieval(
        question,
        mode,
        chunks_path,
        kg_path,
        index_dir,
        collection_name=collection_name,
        graph_hops=graph_hops,
        graph_method=graph_method,
        graph_fusion_policy=graph_fusion_policy,
        aliases_path=aliases_path,
        vector_top_k=vector_top_k,
        hybrid_top_k=hybrid_top_k,
    )
    answer, prompt = generate_grounded_answer(
        question,
        retrieval["fused_chunks"],
        retrieval["graph_triples"],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return {**retrieval, "answer": answer, "answer_prompt": prompt}


def write_query_result(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_document(result, output_path)
