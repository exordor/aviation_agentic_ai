from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha1
from pathlib import Path
from typing import Any

from rdflib import Graph, OWL, RDF, URIRef

from aviation_agentic_ai.chunking.chunks import SourceChunk, read_chunks_jsonl
from aviation_agentic_ai.config import load_yaml
from aviation_agentic_ai.ontology.evaluation import local_name
from aviation_agentic_ai.paths import project_relative_path


@dataclass(frozen=True)
class ExtractionProfile:
    name: str
    namespace: str
    instantiable_classes: tuple[str, ...]
    relation_properties: tuple[str, ...]
    provenance_fields: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExtractionProfile":
        return cls(
            name=str(data["name"]),
            namespace=str(data["namespace"]),
            instantiable_classes=tuple(str(item) for item in data["instantiable_classes"]),
            relation_properties=tuple(str(item) for item in data["relation_properties"]),
            provenance_fields=tuple(str(item) for item in data["provenance_fields"]),
        )


@dataclass(frozen=True)
class KGTriple:
    triple_id: str
    subject: str
    predicate: str
    object: str
    subject_class: str
    object_class: str
    source_document: str
    page: int
    section: str
    chunk_id: str
    evidence_text: str
    model: str
    confidence: float
    extracted_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class KGValidationError(ValueError):
    """Raised when a KG artifact fails deterministic validation."""


def load_extraction_profile(path: str | Path) -> ExtractionProfile:
    return ExtractionProfile.from_dict(load_yaml(path))


def _class_label(class_name: str) -> str:
    text = class_name.removeprefix("Cl_")
    text = re.sub(r"(?<!^)([A-Z])", r" \1", text)
    return text.lower()


def _normalize_for_contains(text: str) -> str:
    return " ".join(text.lower().split())


def _extract_json_payload(text: str) -> str:
    stripped = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        stripped = fenced.group(1).strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return stripped[start : end + 1]
    return stripped


def _stable_triple_id(chunk_id: str, index: int, triple: dict[str, Any]) -> str:
    material = json.dumps(triple, sort_keys=True)
    digest = sha1(material.encode("utf-8")).hexdigest()[:10]
    return f"{chunk_id}-kg{index:02d}-{digest}"


def _evidence_sentence(chunk: SourceChunk, labels: list[str]) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", chunk.text)
    for sentence in sentences:
        normalized = _normalize_for_contains(sentence)
        if all(label in normalized for label in labels):
            return sentence.strip()
    return chunk.text[:350].strip()


def _predicate_for_text(text: str) -> str:
    normalized = _normalize_for_contains(text)
    if "cause" in normalized or "produces" in normalized:
        return "causes"
    if "part" in normalized or "component" in normalized or "consist" in normalized:
        return "hasComponent"
    if "affect" in normalized or "change" in normalized:
        return "affects"
    return "hasCondition"


def _deterministic_triples_for_chunk(
    chunk: SourceChunk,
    profile: ExtractionProfile,
    extracted_at: str,
) -> list[KGTriple]:
    normalized = _normalize_for_contains(chunk.text)
    matches = [
        (class_name, label)
        for class_name in profile.instantiable_classes
        for label in [_class_label(class_name)]
        if label in normalized
    ]
    triples: list[KGTriple] = []
    for index, ((subject_class, subject_label), (object_class, object_label)) in enumerate(
        zip(matches, matches[1:])
    ):
        predicate = _predicate_for_text(chunk.text)
        evidence = _evidence_sentence(chunk, [subject_label, object_label])
        raw = {
            "subject": subject_label,
            "predicate": predicate,
            "object": object_label,
            "subject_class": subject_class,
            "object_class": object_class,
        }
        triples.append(
            KGTriple(
                triple_id=_stable_triple_id(chunk.chunk_id, index, raw),
                subject=subject_label,
                predicate=predicate,
                object=object_label,
                subject_class=subject_class,
                object_class=object_class,
                source_document=chunk.source_document,
                page=chunk.page,
                section=f"page-{chunk.page}",
                chunk_id=chunk.chunk_id,
                evidence_text=evidence,
                model="deterministic-profile-seed",
                confidence=0.5,
                extracted_at=extracted_at,
            )
        )
    return triples


def _build_extraction_prompt(chunk: SourceChunk, profile: ExtractionProfile) -> str:
    return (
        "Extract focused aviation knowledge graph triples from the source chunk. "
        "Return JSON only with a top-level 'triples' array. Use only the allowed "
        "classes and predicates. Evidence text must be an exact short quote from "
        "the chunk. Do not invent facts beyond the chunk.\n\n"
        f"Allowed classes: {list(profile.instantiable_classes)}\n"
        f"Allowed predicates: {list(profile.relation_properties)}\n\n"
        "Each triple must include: subject, predicate, object, subject_class, "
        "object_class, evidence_text, confidence.\n\n"
        f"Chunk metadata: chunk_id={chunk.chunk_id}, page={chunk.page}, "
        f"source_document={chunk.source_document}\n\n"
        f"Chunk text:\n---\n{chunk.text}\n---\n"
    )


def _invoke_llm_text(prompt: str, temperature: float, max_tokens: int) -> str:
    try:
        from langchain_core.messages import HumanMessage
    except ImportError as exc:
        raise RuntimeError(
            "KG extraction requires optional ontology-generation dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    from aviation_agentic_ai.llm.providers import get_llm

    response = get_llm(temperature=temperature, max_tokens=max_tokens).invoke(
        [HumanMessage(content=prompt)]
    )
    return str(getattr(response, "content", response)).strip()


def _llm_triples_for_chunk(
    chunk: SourceChunk,
    profile: ExtractionProfile,
    extracted_at: str,
    temperature: float,
    max_tokens: int,
) -> list[KGTriple]:
    payload = json.loads(
        _extract_json_payload(
            _invoke_llm_text(
                _build_extraction_prompt(chunk, profile),
                temperature=temperature,
                max_tokens=max_tokens,
            )
        )
    )
    raw_triples = payload.get("triples", [])
    if not isinstance(raw_triples, list):
        raise ValueError("Expected top-level 'triples' array from KG extraction LLM.")

    triples: list[KGTriple] = []
    for index, raw in enumerate(raw_triples):
        if not isinstance(raw, dict):
            continue
        confidence = float(raw.get("confidence", 0.0))
        normalized = {
            "subject": str(raw.get("subject", "")),
            "predicate": str(raw.get("predicate", "")),
            "object": str(raw.get("object", "")),
            "subject_class": str(raw.get("subject_class", "")),
            "object_class": str(raw.get("object_class", "")),
        }
        triples.append(
            KGTriple(
                triple_id=_stable_triple_id(chunk.chunk_id, index, normalized),
                subject=normalized["subject"],
                predicate=normalized["predicate"],
                object=normalized["object"],
                subject_class=normalized["subject_class"],
                object_class=normalized["object_class"],
                source_document=chunk.source_document,
                page=chunk.page,
                section=str(raw.get("section") or f"page-{chunk.page}"),
                chunk_id=chunk.chunk_id,
                evidence_text=str(raw.get("evidence_text", "")),
                model="llm-structured-kg-extraction",
                confidence=max(0.0, min(confidence, 1.0)),
                extracted_at=extracted_at,
            )
        )
    return triples


def write_kg_jsonl(triples: list[KGTriple], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(triple.to_dict(), sort_keys=True) for triple in triples]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return path


def read_kg_jsonl(path: str | Path) -> list[KGTriple]:
    triples: list[KGTriple] = []
    kg_path = Path(path)
    if not kg_path.exists():
        return []
    for line in kg_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        triples.append(KGTriple(**json.loads(line)))
    return triples


def _ontology_terms(ontology_path: str | Path) -> tuple[set[str], set[str]]:
    graph = Graph()
    graph.parse(str(ontology_path))
    classes = {
        local_name(subject)
        for subject in graph.subjects(RDF.type, OWL.Class)
        if isinstance(subject, URIRef)
    }
    properties = {
        local_name(subject)
        for subject in graph.subjects(RDF.type, OWL.ObjectProperty)
        if isinstance(subject, URIRef)
    } | {
        local_name(subject)
        for subject in graph.subjects(RDF.type, OWL.DatatypeProperty)
        if isinstance(subject, URIRef)
    }
    return classes, properties


def validate_kg_triples(
    triples: list[KGTriple],
    chunks: list[SourceChunk],
    profile: ExtractionProfile,
    ontology_path: str | Path | None = None,
) -> dict[str, Any]:
    chunk_index = {chunk.chunk_id: chunk for chunk in chunks}
    ontology_classes: set[str] | None = None
    ontology_properties: set[str] | None = None
    if ontology_path is not None:
        ontology_classes, ontology_properties = _ontology_terms(ontology_path)

    errors: list[dict[str, str]] = []
    profile_classes = set(profile.instantiable_classes)
    profile_properties = set(profile.relation_properties)
    required_fields = set(profile.provenance_fields)
    for triple in triples:
        data = triple.to_dict()
        for field in required_fields:
            value = data.get(field)
            if value in (None, ""):
                errors.append({"triple_id": triple.triple_id, "field": field, "error": "missing"})
        if triple.subject_class not in profile_classes:
            errors.append(
                {
                    "triple_id": triple.triple_id,
                    "field": "subject_class",
                    "error": f"unsupported class {triple.subject_class}",
                }
            )
        if triple.object_class not in profile_classes:
            errors.append(
                {
                    "triple_id": triple.triple_id,
                    "field": "object_class",
                    "error": f"unsupported class {triple.object_class}",
                }
            )
        if triple.predicate not in profile_properties:
            errors.append(
                {
                    "triple_id": triple.triple_id,
                    "field": "predicate",
                    "error": f"unsupported predicate {triple.predicate}",
                }
            )
        if ontology_classes is not None and triple.subject_class not in ontology_classes:
            errors.append(
                {
                    "triple_id": triple.triple_id,
                    "field": "subject_class",
                    "error": f"class not declared in ontology {triple.subject_class}",
                }
            )
        if ontology_classes is not None and triple.object_class not in ontology_classes:
            errors.append(
                {
                    "triple_id": triple.triple_id,
                    "field": "object_class",
                    "error": f"class not declared in ontology {triple.object_class}",
                }
            )
        if ontology_properties is not None and triple.predicate not in ontology_properties:
            errors.append(
                {
                    "triple_id": triple.triple_id,
                    "field": "predicate",
                    "error": f"predicate not declared in ontology {triple.predicate}",
                }
            )
        chunk = chunk_index.get(triple.chunk_id)
        if chunk is None:
            errors.append(
                {
                    "triple_id": triple.triple_id,
                    "field": "chunk_id",
                    "error": f"unknown chunk {triple.chunk_id}",
                }
            )
        elif _normalize_for_contains(triple.evidence_text) not in _normalize_for_contains(chunk.text):
            errors.append(
                {
                    "triple_id": triple.triple_id,
                    "field": "evidence_text",
                    "error": "evidence text is not contained in source chunk",
                }
            )
    return {
        "valid": not errors,
        "triples_total": len(triples),
        "errors_total": len(errors),
        "errors": errors,
    }


def validate_kg_file(
    kg_path: str | Path,
    chunks_path: str | Path,
    profile_path: str | Path,
    ontology_path: str | Path | None = None,
) -> dict[str, Any]:
    profile = load_extraction_profile(profile_path)
    triples = read_kg_jsonl(kg_path)
    chunks = read_chunks_jsonl(chunks_path)
    return {
        "kg_path": project_relative_path(kg_path),
        "chunks_path": project_relative_path(chunks_path),
        "profile_path": project_relative_path(profile_path),
        **validate_kg_triples(triples, chunks, profile, ontology_path=ontology_path),
    }


def extract_kg_file(
    chunks_path: str | Path,
    output_path: str | Path,
    profile_path: str | Path,
    ontology_path: str | Path | None = None,
    max_chunks: int | None = None,
    dry_run: bool = False,
    temperature: float = 0.0,
    max_tokens: int = 4096,
) -> tuple[Path, list[KGTriple], dict[str, Any]]:
    profile = load_extraction_profile(profile_path)
    chunks = read_chunks_jsonl(chunks_path)
    selected_chunks = chunks[:max_chunks] if max_chunks is not None else chunks
    extracted_at = datetime.now(UTC).isoformat()
    triples: list[KGTriple] = []
    for chunk in selected_chunks:
        if dry_run:
            triples.extend(_deterministic_triples_for_chunk(chunk, profile, extracted_at))
        else:
            triples.extend(
                _llm_triples_for_chunk(
                    chunk,
                    profile,
                    extracted_at,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )
    report = validate_kg_triples(triples, chunks, profile, ontology_path=ontology_path)
    if not report["valid"]:
        raise KGValidationError(json.dumps(report["errors"][:10], indent=2))
    path = write_kg_jsonl(triples, output_path)
    return path, triples, report
