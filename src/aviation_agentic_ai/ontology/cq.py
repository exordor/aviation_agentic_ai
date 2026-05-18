from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from aviation_agentic_ai.ontology.profiles import DomainProfile, get_domain_profile
from aviation_agentic_ai.utils.pdf import extract_pages


class CompetencyQuestion(BaseModel):
    competency_question: str = Field(description="A fine-grained competency question")
    key_entities: list[str] = Field(description="Key entities mentioned in the question")
    odp_hint: str = Field(description="Ontology Design Pattern targeted by the question")
    expected_answer: str = Field(description="Expected schema-level answer")


class CQList(BaseModel):
    questions: list[CompetencyQuestion] = Field(description="Generated competency questions")


class CQValidationError(ValueError):
    """Raised when a CQ artifact is malformed or not normalized."""


BASE_CQ_FIELDS = {"competency_question", "key_entities", "odp_hint", "expected_answer"}
NORMALIZED_CQ_FIELDS = {
    "id",
    "source_document",
    "source_page",
    "canonical_entities",
    "cq_type",
    "odp_id",
    "status",
}

ODP_VOCABULARY: dict[str, str] = {
    "causal_relation": "Causal relations, effects, influences, and causal flight-physics outcomes.",
    "event_reification": "Events, processes, participants, triggers, conditions, and outcomes.",
    "quantity": "Quantities, numeric values, units, measurements, and reference scales.",
    "partonomy": "Part-whole, component, surface, section, and structural composition patterns.",
    "situation": "Situations, states, conditions, contexts, and flight/atmospheric states.",
    "taxonomy": "Class hierarchy, subclass, type, classification, and schema taxonomy patterns.",
    "material_composition": "Material, constituent, composition, and atmospheric element patterns.",
    "spatial_relation": "Containment, location, adjacency, orientation, and spatial relation patterns.",
    "force_relation": "Force, aerodynamic force, pressure/lift/drag force relation patterns.",
    "property_relation": "General object/datatype property and relational property patterns.",
    "flow_interaction": "Airflow, fluid flow, boundary layer, circulation, and flow interaction patterns.",
    "other": "Other ontology requirement patterns that need later review.",
}


ODP_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("partonomy", ("part", "whole", "component", "surface", "section", "structure")),
    ("quantity", ("quantity", "unit", "measurement", "numeric", "value", "reference system", "scale")),
    ("event_reification", ("event", "process", "participant", "trigger", "reification")),
    ("causal_relation", ("causal", "cause", "effect", "affect", "influence", "outcome")),
    ("situation", ("situation", "state", "condition", "context")),
    ("taxonomy", ("taxonomy", "subclass", "hierarchy", "classification", "class hierarchy")),
    ("material_composition", ("material", "composition", "constituent", "element")),
    ("spatial_relation", ("spatial", "containment", "location", "adjacency", "orientation")),
    ("force_relation", ("force", "aerodynamic force", "pressure difference")),
    ("flow_interaction", ("flow", "airflow", "fluid", "boundary layer", "circulation")),
    ("property_relation", ("property", "relation", "relationship", "domain", "range")),
)


def _normalize_text(value: str) -> str:
    return " ".join(value.replace("’", "'").lower().split())


def _slug(value: str) -> str:
    chars = [char.lower() if char.isalnum() else "-" for char in value.replace("’", "'")]
    return "-".join(part for part in "".join(chars).split("-") if part)


def normalize_entity(entity: str) -> str:
    normalized = _normalize_text(entity)
    replacements = {
        "gasses": "gases",
        "bernoulli’s principle": "bernoulli's principle",
        "bernoulli's principle": "bernoulli principle",
        "newton’s third law": "newton's third law",
        "newton's third law": "newton third law",
    }
    return replacements.get(normalized, normalized)


def normalize_odp_hint(odp_hint: str) -> str:
    text = _normalize_text(odp_hint)
    for odp_id, keywords in ODP_KEYWORDS:
        if any(keyword in text for keyword in keywords):
            return odp_id
    return "other"


def infer_cq_type(question: str, odp_id: str) -> str:
    text = _normalize_text(question)
    if "what class" in text or "class hierarchy" in text or odp_id == "taxonomy":
        return "class_schema"
    if "what property" in text or "what relation" in text or "relationship" in text:
        return "property_schema"
    if odp_id == "quantity":
        return "quantity_schema"
    if odp_id in {"causal_relation", "event_reification"}:
        return "causal_schema"
    return "schema_requirement"


def stable_cq_id(
    document_id: str, page: str | int, question: str, expected_answer: str
) -> str:
    digest_input = "|".join(
        [
            str(document_id),
            str(page),
            _normalize_text(question),
            _normalize_text(expected_answer),
        ]
    )
    digest = hashlib.sha1(digest_input.encode("utf-8")).hexdigest()[:10]
    return f"{_slug(document_id)}-p{int(page):02d}-{digest}" if str(page).isdigit() else f"{_slug(document_id)}-{digest}"


def enrich_cq_item(document_id: str, page: str | int, item: dict[str, Any]) -> dict[str, Any]:
    question = str(item.get("competency_question", ""))
    expected_answer = str(item.get("expected_answer", ""))
    key_entities = [str(entity) for entity in item.get("key_entities", [])]
    odp_hint = str(item.get("odp_hint", ""))
    odp_id = str(item.get("odp_id") or normalize_odp_hint(odp_hint))
    enriched = dict(item)
    enriched.setdefault("id", stable_cq_id(document_id, page, question, expected_answer))
    enriched.setdefault("source_document", str(document_id))
    enriched.setdefault("source_page", int(page) if str(page).isdigit() else str(page))
    enriched.setdefault("canonical_entities", [normalize_entity(entity) for entity in key_entities])
    enriched.setdefault("cq_type", infer_cq_type(question, odp_id))
    enriched.setdefault("odp_id", odp_id)
    enriched.setdefault("status", "silver")
    return enriched


def normalize_cq_artifact(data: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for document_id, pages in data.items():
        if not isinstance(pages, dict):
            normalized[document_id] = pages
            continue
        normalized_pages: dict[str, Any] = {}
        for page, items in pages.items():
            if not isinstance(items, list):
                normalized_pages[str(page)] = items
                continue
            normalized_pages[str(page)] = [
                enrich_cq_item(str(document_id), str(page), item)
                if isinstance(item, dict)
                else item
                for item in items
            ]
        normalized[str(document_id)] = normalized_pages
    return normalized


def validate_cq_artifact(data: dict[str, Any], require_normalized: bool = True) -> None:
    errors: list[str] = []
    seen_ids: set[str] = set()
    if not isinstance(data, dict) or not data:
        raise CQValidationError("CQ artifact must be a non-empty JSON object.")
    for document_id, pages in data.items():
        if not isinstance(pages, dict) or not pages:
            errors.append(f"{document_id}: expected non-empty page mapping")
            continue
        for page, items in pages.items():
            if not isinstance(items, list):
                errors.append(f"{document_id}/{page}: expected list of CQs")
                continue
            if not items:
                errors.append(f"{document_id}/{page}: page has no CQs")
            for index, item in enumerate(items):
                location = f"{document_id}/{page}/{index}"
                if not isinstance(item, dict):
                    errors.append(f"{location}: expected CQ object")
                    continue
                missing_base = BASE_CQ_FIELDS - item.keys()
                if missing_base:
                    errors.append(f"{location}: missing fields {sorted(missing_base)}")
                    continue
                if require_normalized:
                    missing_normalized = NORMALIZED_CQ_FIELDS - item.keys()
                    if missing_normalized:
                        errors.append(
                            f"{location}: missing normalized fields {sorted(missing_normalized)}"
                        )
                question = str(item.get("competency_question", "")).strip()
                answer = str(item.get("expected_answer", "")).strip()
                entities = item.get("key_entities", [])
                if not question:
                    errors.append(f"{location}: empty competency_question")
                if not answer:
                    errors.append(f"{location}: empty expected_answer")
                if (
                    not isinstance(entities, list)
                    or not entities
                    or not all(str(e).strip() for e in entities)
                ):
                    errors.append(f"{location}: key_entities must be a non-empty list of strings")
                if require_normalized:
                    cq_id = str(item.get("id", "")).strip()
                    odp_id = str(item.get("odp_id", "")).strip()
                    source_document = str(item.get("source_document", "")).strip()
                    source_page = item.get("source_page")
                    canonical_entities = item.get("canonical_entities", [])
                    cq_type = str(item.get("cq_type", "")).strip()
                    status = str(item.get("status", "")).strip()
                    if not cq_id:
                        errors.append(f"{location}: empty id")
                    elif cq_id in seen_ids:
                        errors.append(f"{location}: duplicate id {cq_id}")
                    seen_ids.add(cq_id)
                    if source_document != str(document_id):
                        errors.append(f"{location}: source_document must be {document_id}")
                    if str(source_page) != str(int(page) if str(page).isdigit() else page):
                        errors.append(f"{location}: source_page must be {page}")
                    if (
                        not isinstance(canonical_entities, list)
                        or not canonical_entities
                        or not all(str(e).strip() for e in canonical_entities)
                    ):
                        errors.append(
                            f"{location}: canonical_entities must be a non-empty list of strings"
                        )
                    if not cq_type:
                        errors.append(f"{location}: empty cq_type")
                    if not status:
                        errors.append(f"{location}: empty status")
                    if odp_id not in ODP_VOCABULARY:
                        errors.append(f"{location}: unknown odp_id {odp_id}")
    if errors:
        preview = "\n".join(errors[:20])
        suffix = f"\n... and {len(errors) - 20} more errors" if len(errors) > 20 else ""
        raise CQValidationError(f"Invalid CQ artifact:\n{preview}{suffix}")


def load_cq_artifact(path: str | Path, require_normalized: bool = True) -> dict[str, Any]:
    cq_path = Path(path)
    data = json.loads(cq_path.read_text(encoding="utf-8"))
    validate_cq_artifact(data, require_normalized=require_normalized)
    return data


def build_cq_prompt(page_text: str, profile: DomainProfile) -> str:
    schema = json.dumps(CQList.model_json_schema(), indent=2)
    return (
        f"{profile.cq_domain_role}\n\n"
        "Generate atomic Competency Questions (CQs) that will drive construction of a "
        "well-designed OWL ontology. Return only JSON that follows the schema.\n\n"
        f"Domain focus:\n{profile.cq_domain_guidance}\n\n"
        f"ODP guidance:\n{profile.cq_odp_guidance}\n\n"
        "Rules:\n"
        "- Prefer TBox/schema CQs over page-specific fact questions.\n"
        "- Include classes, properties, hierarchies, domain/range constraints, and ODP patterns.\n"
        "- Avoid creating individual facts or provenance CQs at this ontology stage.\n"
        "- Fill every field for every question.\n\n"
        f"JSON schema:\n{schema}\n\n"
        f"Document text:\n---\n{page_text}\n---\n"
    )


def _dump_json(data: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def generate_cqs(
    pdf_path: str | Path,
    output_path: str | Path,
    domain_profile: str | DomainProfile = "aviation_phak",
    max_page_chars: int = 8000,
    max_pages: int | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Generate or preview ontology CQs for a PDF."""
    profile = get_domain_profile(domain_profile)
    pdf = Path(pdf_path)
    output = Path(output_path)
    document_id = pdf.stem
    results: dict[str, Any] = {document_id: {}}

    if dry_run:
        for page in extract_pages(pdf, max_pages=max_pages):
            prompt = build_cq_prompt(page.text[:max_page_chars], profile)
            results[document_id][str(page.page_number)] = {
                "dry_run": True,
                "page_chars": len(page.text),
                "prompt_preview": prompt[:2000],
            }
        _dump_json(results, output)
        return results

    try:
        from langchain_core.messages import HumanMessage
    except ImportError as exc:
        raise RuntimeError(
            "CQ generation requires optional ontology-generation dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    from aviation_agentic_ai.llm.providers import get_llm

    llm = get_llm()
    structured_llm = llm.with_structured_output(schema=CQList, method="json_mode")

    for page in extract_pages(pdf, max_pages=max_pages):
        prompt = build_cq_prompt(page.text[:max_page_chars], profile)
        cq_list = structured_llm.invoke([HumanMessage(content=prompt)])
        results[document_id][str(page.page_number)] = [
            enrich_cq_item(document_id, str(page.page_number), item.model_dump())
            for item in cq_list.questions
        ]

    _dump_json(results, output)
    return results
