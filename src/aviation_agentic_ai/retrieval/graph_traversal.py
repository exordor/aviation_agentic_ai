from __future__ import annotations

import logging
import re
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import networkx as nx

from aviation_agentic_ai.chunking.chunks import read_chunks_jsonl
from aviation_agentic_ai.config import load_yaml, resolve_project_path
from aviation_agentic_ai.kg.extraction import KGTriple, read_kg_jsonl
from aviation_agentic_ai.utils.text import GRAPH_TRAVERSAL_STOPWORDS, tokenize_terms

logger = logging.getLogger(__name__)

DEFAULT_ENTITY_ALIASES_PATH = "configs/entity_aliases.yaml"

RELATION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "affects": ("affect", "influence", "change", "impact"),
    "causes": ("cause", "produce", "lead", "result"),
    "hasComponent": ("component", "part", "consist"),
    "partOf": ("part", "belong"),
    "appliesTo": ("apply", "use", "relevant"),
    "hasCondition": ("condition", "when", "under"),
    "hasOutcome": ("outcome", "result", "consequence"),
}


@dataclass(frozen=True)
class GraphPathEdge:
    source: str
    target: str
    original_source: str
    original_target: str
    predicate: str
    triple_id: str
    chunk_id: str
    page: int | None
    evidence_text: str
    confidence: float
    subject: str
    object: str
    subject_class: str
    object_class: str
    source_document: str
    section: str
    model: str
    extracted_at: str
    traversal_direction: str = "forward"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_triple_dict(self) -> dict[str, Any]:
        return {
            "triple_id": self.triple_id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "subject_class": self.subject_class,
            "object_class": self.object_class,
            "source_document": self.source_document,
            "page": self.page,
            "section": self.section,
            "chunk_id": self.chunk_id,
            "evidence_text": self.evidence_text,
            "model": self.model,
            "confidence": self.confidence,
            "extracted_at": self.extracted_at,
        }


@dataclass(frozen=True)
class GraphPath:
    seed_node: str
    nodes: tuple[str, ...]
    edges: tuple[GraphPathEdge, ...]

    @property
    def hops(self) -> int:
        return len(self.edges)

    @property
    def chunk_ids(self) -> list[str]:
        return _unique_ordered(edge.chunk_id for edge in self.edges if edge.chunk_id)

    @property
    def pages(self) -> list[int]:
        return _unique_ordered(edge.page for edge in self.edges if edge.page is not None)


def normalize_entity_label(text: str) -> str:
    """Normalize labels for stable graph node ids and phrase matching."""
    normalized = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return " ".join(normalized.split())


def _tokenize(text: str) -> set[str]:
    return tokenize_terms(text, stopwords=GRAPH_TRAVERSAL_STOPWORDS)


def _phrase_position(needle: str, haystack: str) -> int | None:
    if not needle:
        return None
    match = re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", haystack)
    return match.start() if match else None


def _unique_ordered(values: Any) -> list[Any]:
    seen: set[Any] = set()
    ordered: list[Any] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _add_or_update_node(
    graph: nx.MultiDiGraph,
    node_id: str,
    label: str,
    class_name: str,
) -> None:
    if not graph.has_node(node_id):
        graph.add_node(
            node_id,
            label=label,
            class_=class_name,
            **{"class": class_name},
            class_name=class_name,
            classes=[class_name] if class_name else [],
        )
        return

    classes = list(graph.nodes[node_id].get("classes", []))
    if class_name and class_name not in classes:
        classes.append(class_name)
    graph.nodes[node_id]["classes"] = sorted(classes)
    if not graph.nodes[node_id].get("class_name") and class_name:
        graph.nodes[node_id]["class_name"] = class_name
        graph.nodes[node_id]["class"] = class_name
        graph.nodes[node_id]["class_"] = class_name


def build_kg_graph(triples: list[KGTriple]) -> nx.MultiDiGraph:
    """Build a directed multi-graph from extracted KG triples."""
    graph = nx.MultiDiGraph()
    for triple in triples:
        subject_id = normalize_entity_label(triple.subject)
        object_id = normalize_entity_label(triple.object)
        if not subject_id or not object_id:
            continue
        _add_or_update_node(graph, subject_id, triple.subject, triple.subject_class)
        _add_or_update_node(graph, object_id, triple.object, triple.object_class)
        graph.add_edge(
            subject_id,
            object_id,
            key=triple.triple_id,
            predicate=triple.predicate,
            triple_id=triple.triple_id,
            chunk_id=triple.chunk_id,
            page=triple.page,
            evidence_text=triple.evidence_text,
            confidence=triple.confidence,
            subject=triple.subject,
            object=triple.object,
            subject_class=triple.subject_class,
            object_class=triple.object_class,
            source_document=triple.source_document,
            section=triple.section,
            model=triple.model,
            extracted_at=triple.extracted_at,
            original_source=subject_id,
            original_target=object_id,
        )
    return graph


def _normalize_aliases(aliases: dict[str, Any] | None) -> dict[str, str]:
    normalized: dict[str, str] = {}
    if not aliases:
        return normalized
    raw_aliases = aliases.get("aliases", aliases) if isinstance(aliases, dict) else {}
    for label, values in raw_aliases.items():
        canonical = normalize_entity_label(str(label))
        if not canonical:
            continue
        normalized[canonical] = canonical
        if isinstance(values, str):
            alias_values = [values]
        elif isinstance(values, list | tuple | set):
            alias_values = list(values)
        else:
            alias_values = []
        for alias in alias_values:
            alias_id = normalize_entity_label(str(alias))
            if alias_id:
                normalized[alias_id] = canonical
    return normalized


def load_entity_aliases(path: str | Path | None = None) -> dict[str, Any]:
    alias_path = resolve_project_path(path or DEFAULT_ENTITY_ALIASES_PATH)
    if not alias_path.exists():
        return {}
    try:
        return load_yaml(alias_path)
    except Exception:
        logger.warning(
            "Failed to load entity aliases from %s, continuing with empty aliases",
            alias_path, exc_info=True
        )
        return {}


def link_question_entities(
    question: str,
    graph: nx.MultiDiGraph,
    aliases: dict[str, Any] | None = None,
) -> list[str]:
    """Link question text to stable graph node ids."""
    normalized_question = normalize_entity_label(question)
    seed_matches: dict[str, tuple[int, str]] = {}

    for node_id in graph.nodes:
        position = _phrase_position(str(node_id), normalized_question)
        if position is not None:
            seed_matches[str(node_id)] = (position, "label")

    alias_map = _normalize_aliases(aliases)
    for alias, canonical in alias_map.items():
        if canonical not in graph:
            continue
        position = _phrase_position(alias, normalized_question)
        if position is None:
            continue
        previous = seed_matches.get(canonical)
        if previous is None or position < previous[0] or previous[1] == "fallback":
            seed_matches[canonical] = (position, "alias" if alias != canonical else "label")

    if not seed_matches:
        question_terms = _tokenize(question)
        scored: list[tuple[int, str]] = []
        for node_id, node_data in graph.nodes(data=True):
            label = str(node_data.get("label") or node_id)
            score = len(question_terms & _tokenize(label))
            if score > 0:
                scored.append((score, str(node_id)))
        for rank, (score, node_id) in enumerate(
            sorted(scored, key=lambda item: (-item[0], item[1]))[:3],
            start=1,
        ):
            seed_matches[node_id] = (rank, "fallback")

    ordered = [
        node_id
        for node_id, (_position, _source) in sorted(
            seed_matches.items(), key=lambda item: (item[1][0], item[0])
        )
    ]
    graph.graph["last_seed_sources"] = {
        node_id: source for node_id, (_position, source) in seed_matches.items()
    }
    return ordered


def _edge_from_data(
    source: str,
    target: str,
    data: dict[str, Any],
    traversal_direction: str,
) -> GraphPathEdge:
    return GraphPathEdge(
        source=source,
        target=target,
        original_source=str(data.get("original_source") or source),
        original_target=str(data.get("original_target") or target),
        predicate=str(data.get("predicate", "")),
        triple_id=str(data.get("triple_id", "")),
        chunk_id=str(data.get("chunk_id", "")),
        page=data.get("page"),
        evidence_text=str(data.get("evidence_text", "")),
        confidence=float(data.get("confidence", 0.0) or 0.0),
        subject=str(data.get("subject", "")),
        object=str(data.get("object", "")),
        subject_class=str(data.get("subject_class", "")),
        object_class=str(data.get("object_class", "")),
        source_document=str(data.get("source_document", "")),
        section=str(data.get("section", "")),
        model=str(data.get("model", "")),
        extracted_at=str(data.get("extracted_at", "")),
        traversal_direction=traversal_direction,
    )


def _iter_traversal_edges(
    graph: nx.MultiDiGraph,
    node_id: str,
    allow_reverse: bool,
) -> list[tuple[str, GraphPathEdge]]:
    edges: list[tuple[str, GraphPathEdge]] = []
    for source, target, _key, data in graph.out_edges(node_id, keys=True, data=True):
        edges.append(
            (
                str(target),
                _edge_from_data(str(source), str(target), data, "forward"),
            )
        )
    if allow_reverse:
        for source, target, _key, data in graph.in_edges(node_id, keys=True, data=True):
            edges.append(
                (
                    str(source),
                    _edge_from_data(str(target), str(source), data, "reverse"),
                )
            )
    return sorted(
        edges,
        key=lambda item: (
            item[0],
            item[1].predicate,
            item[1].triple_id,
            item[1].traversal_direction,
        ),
    )


def traverse_paths(
    graph: nx.MultiDiGraph,
    seed_nodes: list[str],
    max_hops: int = 2,
    max_paths: int = 100,
    allow_reverse: bool = False,
) -> list[GraphPath]:
    """Return bounded BFS paths from seed nodes."""
    if max_hops <= 0 or max_paths <= 0:
        return []

    paths: list[GraphPath] = []
    queue: deque[tuple[str, tuple[str, ...], tuple[GraphPathEdge, ...]]] = deque()
    for seed in seed_nodes:
        if seed in graph:
            queue.append((seed, (seed,), ()))

    while queue and len(paths) < max_paths:
        seed, nodes, edges = queue.popleft()
        if len(edges) >= max_hops:
            continue
        current = nodes[-1]
        for neighbor, edge in _iter_traversal_edges(graph, current, allow_reverse):
            if neighbor in nodes:
                continue
            next_nodes = (*nodes, neighbor)
            next_edges = (*edges, edge)
            path = GraphPath(seed_node=seed, nodes=next_nodes, edges=next_edges)
            paths.append(path)
            if len(paths) >= max_paths:
                break
            if len(next_edges) < max_hops:
                queue.append((seed, next_nodes, next_edges))
    return paths


def _relation_intent_score(question_terms: set[str], predicate: str) -> float:
    keywords = RELATION_KEYWORDS.get(predicate, ())
    if not keywords:
        return 0.0
    keyword_terms = {term for keyword in keywords for term in _tokenize(keyword)}
    return 1.0 if question_terms & keyword_terms else 0.0


def score_path(question: str, path: GraphPath) -> float:
    """Score a traversal path by entity, relation, evidence, confidence, and length."""
    question_terms = _tokenize(question)
    if not question_terms:
        return 0.0

    entity_terms = {term for node_id in path.nodes for term in _tokenize(node_id)}
    entity_overlap = len(question_terms & entity_terms) / max(len(question_terms), 1)

    predicate_scores = [
        _relation_intent_score(question_terms, edge.predicate)
        or len(question_terms & _tokenize(edge.predicate)) / max(len(question_terms), 1)
        for edge in path.edges
    ]
    predicate_overlap = sum(predicate_scores) / max(len(predicate_scores), 1)

    evidence_terms = {
        term for edge in path.edges for term in _tokenize(edge.evidence_text)
    }
    evidence_overlap = len(question_terms & evidence_terms) / max(len(question_terms), 1)

    confidence = sum(edge.confidence for edge in path.edges) / max(path.hops, 1)
    length_penalty = max(path.hops - 1, 0) * 0.05
    score = (
        2.0 * entity_overlap
        + 1.25 * predicate_overlap
        + evidence_overlap
        + 0.5 * confidence
        - length_penalty
    )
    return round(max(score, 0.0), 6)


def _node_dict(graph: nx.MultiDiGraph, node_id: str) -> dict[str, Any]:
    node = graph.nodes[node_id]
    return {
        "node_id": node_id,
        "label": node.get("label", node_id),
        "class": node.get("class", ""),
        "class_name": node.get("class_name", ""),
        "classes": node.get("classes", []),
    }


def _path_to_dict(
    graph: nx.MultiDiGraph,
    path: GraphPath,
    path_id: str,
    score: float,
    seed_sources: dict[str, str],
) -> dict[str, Any]:
    return {
        "path_id": path_id,
        "hops": path.hops,
        "score": score,
        "seed_nodes": [path.seed_node],
        "seed_node_sources": {path.seed_node: seed_sources.get(path.seed_node, "unknown")},
        "nodes": [_node_dict(graph, node_id) for node_id in path.nodes],
        "edges": [edge.to_dict() for edge in path.edges],
        "chunk_ids": path.chunk_ids,
        "pages": path.pages,
    }


def _chunk_hit_from_path(
    chunk_id: str,
    score: float,
    path_id: str,
    path: GraphPath,
    chunks: dict[str, Any],
) -> dict[str, Any] | None:
    chunk = chunks.get(chunk_id)
    edge_pages = [edge.page for edge in path.edges if edge.chunk_id == chunk_id]
    page = edge_pages[0] if edge_pages else None
    if chunk is None:
        evidence = " ".join(
            edge.evidence_text for edge in path.edges if edge.chunk_id == chunk_id
        ).strip()
        if not evidence:
            return None
        return {
            "chunk_id": chunk_id,
            "rank": 0,
            "score": score,
            "source": "graph_traversal",
            "page": page,
            "text": evidence,
            "metadata": {"path_id": path_id, "source_document": None},
        }

    return {
        "chunk_id": chunk.chunk_id,
        "rank": 0,
        "score": score,
        "source": "graph_traversal",
        "page": chunk.page,
        "text": chunk.text,
        "metadata": {
            "source_document": chunk.source_document,
            "chunk_index": chunk.chunk_index,
            "path_id": path_id,
        },
    }


def graph_search_traversal(
    question: str,
    kg_path: str | Path,
    chunks_path: str | Path,
    top_k: int = 8,
    graph_hops: int = 2,
    aliases_path: str | Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Search KG evidence using ontology-guided bounded graph traversal."""
    triples = read_kg_jsonl(kg_path)
    chunks = {chunk.chunk_id: chunk for chunk in read_chunks_jsonl(chunks_path)}
    graph = build_kg_graph(triples)
    aliases = load_entity_aliases(aliases_path)
    seed_nodes = link_question_entities(question, graph, aliases=aliases)
    seed_sources = graph.graph.get("last_seed_sources", {})
    candidate_limit = max(top_k * 5, 25)
    paths = traverse_paths(
        graph,
        seed_nodes,
        max_hops=graph_hops,
        max_paths=candidate_limit,
        allow_reverse=False,
    )
    scored_paths = sorted(
        ((score_path(question, path), index, path) for index, path in enumerate(paths)),
        key=lambda item: (-item[0], item[2].hops, item[1]),
    )

    graph_paths: list[dict[str, Any]] = []
    path_ids: dict[int, str] = {}
    for rank, (score, _index, path) in enumerate(scored_paths, start=1):
        path_id = f"path-{rank:03d}"
        path_ids[id(path)] = path_id
        graph_paths.append(_path_to_dict(graph, path, path_id, score, seed_sources))

    best_chunk_hits: dict[str, dict[str, Any]] = {}
    best_triples: dict[str, dict[str, Any]] = {}
    for path_rank, (score, _index, path) in enumerate(scored_paths, start=1):
        path_id = path_ids[id(path)]
        for edge in path.edges:
            if edge.chunk_id:
                hit = _chunk_hit_from_path(edge.chunk_id, score, path_id, path, chunks)
                if hit is not None and (
                    edge.chunk_id not in best_chunk_hits
                    or score > float(best_chunk_hits[edge.chunk_id]["score"])
                ):
                    best_chunk_hits[edge.chunk_id] = hit
            triple = {
                **edge.to_triple_dict(),
                "score": score,
                "path_id": path_id,
                "path_rank": path_rank,
                "traversal_direction": edge.traversal_direction,
            }
            previous = best_triples.get(edge.triple_id)
            if previous is None or score > float(previous["score"]):
                best_triples[edge.triple_id] = triple

    chunk_hits = sorted(
        best_chunk_hits.values(),
        key=lambda item: (-float(item["score"]), str(item["chunk_id"])),
    )[:top_k]
    for rank, hit in enumerate(chunk_hits, start=1):
        hit["rank"] = rank

    graph_triples = sorted(
        best_triples.values(),
        key=lambda item: (-float(item["score"]), int(item["path_rank"]), str(item["triple_id"])),
    )[:top_k]
    for rank, triple in enumerate(graph_triples, start=1):
        triple["rank"] = rank

    return chunk_hits, graph_triples, graph_paths
