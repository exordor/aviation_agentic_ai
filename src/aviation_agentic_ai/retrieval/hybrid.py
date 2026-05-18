from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.chunking.chunks import read_chunks_jsonl
from aviation_agentic_ai.kg.extraction import KGTriple, read_kg_jsonl
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME, query_chroma_index


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "of",
    "on",
    "or",
    "should",
    "that",
    "the",
    "to",
    "what",
    "with",
}


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9']+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def graph_search(
    question: str,
    kg_path: str | Path,
    chunks_path: str | Path,
    top_k: int = 8,
    graph_hops: int = 2,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Search KG triples lexically and return associated chunk evidence."""
    _ = graph_hops
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
            sources.setdefault(chunk_id, set()).add(str(item.get("source", "")))
    fused: list[dict[str, Any]] = []
    for rank, (chunk_id, score) in enumerate(
        sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:top_k],
        start=1,
    ):
        item = dict(merged[chunk_id])
        item["rank"] = rank
        item["score"] = score
        item["source"] = "+".join(sorted(source for source in sources[chunk_id] if source))
        fused.append(item)
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
    try:
        from langchain_core.messages import HumanMessage
    except ImportError as exc:
        raise RuntimeError(
            "Hybrid RAG answering requires optional ontology-generation dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    from aviation_agentic_ai.llm.providers import get_llm

    prompt = build_answer_prompt(question, chunks, triples)
    response = get_llm(temperature=temperature, max_tokens=max_tokens).invoke(
        [HumanMessage(content=prompt)]
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
    vector_top_k: int = 5,
    hybrid_top_k: int = 8,
) -> dict[str, Any]:
    if mode not in {"graph", "vector", "hybrid"}:
        raise ValueError(f"Unsupported retrieval mode: {mode}")
    vector_hits: list[dict[str, Any]] = []
    graph_hits: list[dict[str, Any]] = []
    graph_triples: list[dict[str, Any]] = []
    if mode in {"vector", "hybrid"}:
        vector_hits = query_chroma_index(
            question,
            index_dir=index_dir,
            collection_name=collection_name,
            top_k=vector_top_k,
        )
    if mode in {"graph", "hybrid"}:
        graph_hits, graph_triples = graph_search(
            question,
            kg_path=kg_path,
            chunks_path=chunks_path,
            top_k=hybrid_top_k,
            graph_hops=graph_hops,
        )
    if mode == "vector":
        fused = vector_hits[:hybrid_top_k]
    elif mode == "graph":
        fused = graph_hits[:hybrid_top_k]
    else:
        fused = reciprocal_rank_fusion([vector_hits, graph_hits], top_k=hybrid_top_k)
    return {
        "question": question,
        "mode": mode,
        "vector_hits": vector_hits,
        "graph_hits": graph_hits,
        "graph_triples": graph_triples,
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
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
