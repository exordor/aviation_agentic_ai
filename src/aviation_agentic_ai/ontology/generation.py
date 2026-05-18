from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, TypeVar
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from rdflib import Graph, OWL, RDF, RDFS, URIRef

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.ontology.evaluation import (
    ONTOLOGY_NAMESPACE,
    collect_semantic_smells,
    local_name,
)
from aviation_agentic_ai.ontology.cq import load_cq_artifact
from aviation_agentic_ai.ontology.profiles import DomainProfile, get_domain_profile
from aviation_agentic_ai.ontology.validation import verify_turtle_text
from aviation_agentic_ai.utils.pdf import extract_pages


@dataclass(frozen=True)
class OntologyGenerationResult:
    output_path: Path
    pages_processed: int
    rdf_valid: bool
    validation_message: str


class SRDArtifact(BaseModel):
    """Structured Semantic Requirements Document generated for a source page."""

    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    cq_ids: list[str] = Field(min_length=1)
    source_page: int = Field(ge=0)
    evidence_quotes: list[str] = Field(min_length=1)
    key_concepts: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)
    rules_principles: list[str] = Field(default_factory=list)
    quantities: list[str] = Field(default_factory=list)
    situations: list[str] = Field(default_factory=list)

    @field_validator("cq_ids", "evidence_quotes")
    @classmethod
    def _non_empty_strings(cls, values: list[str]) -> list[str]:
        if any(not item.strip() for item in values):
            raise ValueError("must not contain empty strings")
        return values


class TIPArtifact(BaseModel):
    """Structured Technical Implementation Plan generated from an SRD."""

    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    classes: list[str] = Field(min_length=1)
    properties: list[str] = Field(min_length=1)
    axiom_plan: list[str] = Field(min_length=1)
    domain_range_plan: list[str] = Field(min_length=1)
    risk_flags: list[str] = Field(default_factory=list)
    cq_ids: list[str] = Field(default_factory=list)

    @field_validator("classes", "properties", "axiom_plan", "domain_range_plan", "risk_flags", "cq_ids")
    @classmethod
    def _non_empty_strings(cls, values: list[str]) -> list[str]:
        if any(not item.strip() for item in values):
            raise ValueError("must not contain empty strings")
        return values


ArtifactModel = TypeVar("ArtifactModel", bound=BaseModel)


def build_initial_ttl_content(domain_profile: str | DomainProfile = "aviation_phak") -> str:
    profile = get_domain_profile(domain_profile)
    prefixes = (
        f"@prefix : <{profile.namespace}> .\n"
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "@prefix dcterms: <http://purl.org/dc/terms/> .\n\n"
    )
    body = profile.initial_ttl_body.strip()
    return prefixes if not body else f"{prefixes}{body}\n"


def _load_cqs(cq_path: str | Path) -> dict[str, list[dict[str, Any]]]:
    raw = load_cq_artifact(cq_path)
    if isinstance(raw, dict) and len(raw) == 1 and isinstance(next(iter(raw.values())), dict):
        raw = next(iter(raw.values()))
    if not isinstance(raw, dict):
        raise ValueError(f"Expected CQ page mapping in {cq_path}")
    cqs_by_page: dict[str, list[dict[str, Any]]] = {}
    for page, items in raw.items():
        if not isinstance(items, list):
            raise ValueError(f"Expected CQ list for page {page} in {cq_path}")
        cqs_by_page[str(page)] = items
    return cqs_by_page


def _invoke_text(llm: Any, prompt: str) -> str:
    try:
        from langchain_core.messages import HumanMessage
    except ImportError as exc:
        raise RuntimeError(
            "Ontology generation requires optional ontology-generation dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    response = llm.invoke([HumanMessage(content=prompt)])
    return str(getattr(response, "content", response)).strip()


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


def _parse_validated_artifact(
    text: str,
    model_cls: type[ArtifactModel],
    artifact_name: str,
) -> ArtifactModel:
    payload = _extract_json_payload(text)
    try:
        return model_cls.model_validate_json(payload)
    except (ValueError, ValidationError) as exc:
        raise ValueError(f"Invalid {artifact_name} JSON: {exc}") from exc


def _invoke_validated_artifact(
    llm: Any,
    prompt: str,
    model_cls: type[ArtifactModel],
    artifact_name: str,
    max_qa_cycles: int,
) -> ArtifactModel:
    current_prompt = prompt
    last_error = ""
    for _ in range(max_qa_cycles + 1):
        raw = _invoke_text(llm, current_prompt)
        try:
            return _parse_validated_artifact(raw, model_cls, artifact_name)
        except ValueError as exc:
            last_error = str(exc)
            current_prompt = (
                f"{prompt}\n\nYour previous {artifact_name} response failed schema validation:\n"
                f"{last_error}\nReturn corrected JSON only, with all required fields present."
            )
    raise ValueError(last_error)


def _json_dump(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def _write_json(path: Path, data: Any) -> None:
    path.write_text(f"{_json_dump(data)}\n", encoding="utf-8")


def _sha256_file(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _host_only(url: str) -> str:
    parsed = urlparse(url)
    return parsed.hostname or ""


def _llm_manifest_metadata() -> dict[str, str]:
    try:
        from dotenv import load_dotenv
    except ImportError:
        load_dotenv = None
    if load_dotenv is not None:
        load_dotenv()

    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "deepseek":
        model = os.getenv("MODEL_NAME", "deepseek-chat")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    elif provider == "vllm":
        model = os.getenv("MODEL_NAME", "Qwen/Qwen3-30B-A3B-Instruct-2507-FP8")
        base_url = f"http://localhost:{os.getenv('VLLM_PORT', '8000')}/v1"
    else:
        model = os.getenv("MODEL_NAME", "gpt-4o-mini")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return {"provider": provider, "model": model, "base_url_host": _host_only(base_url)}


def _build_manifest(
    *,
    run_id: str,
    pdf_path: str | Path,
    cq_path: str | Path,
    output_path: Path,
    profile: DomainProfile,
    max_page_chars: int,
    max_pages: int | None,
    max_qa_cycles: int,
    dry_run: bool,
    temperature: float,
    max_tokens: int,
    accepted_pages: list[int],
    failed_pages: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "created_at": datetime.now(UTC).isoformat(),
        "llm": _llm_manifest_metadata(),
        "settings": {
            "domain_profile": profile.name,
            "max_page_chars": max_page_chars,
            "max_pages": max_pages,
            "max_qa_cycles": max_qa_cycles,
            "dry_run": dry_run,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        "inputs": {
            "pdf_path": project_relative_path(pdf_path),
            "pdf_sha256": _sha256_file(pdf_path),
            "cq_path": project_relative_path(cq_path),
            "cq_sha256": _sha256_file(cq_path),
        },
        "output_path": project_relative_path(output_path),
        "accepted_pages": accepted_pages,
        "failed_pages": failed_pages,
    }


def _parse_turtle_text(ttl_text: str) -> Graph:
    graph = Graph()
    graph.parse(data=ttl_text, format="turtle")
    return graph


def _schema_terms(graph: Graph) -> set[URIRef]:
    return {
        subject
        for rdf_type in (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.Ontology)
        for subject in graph.subjects(RDF.type, rdf_type)
        if isinstance(subject, URIRef)
    }


def verify_generated_candidate_quality(
    candidate_ttl: str,
    previous_ttl: str,
    missing_domain_range_threshold: float = 0.3,
) -> tuple[bool, str]:
    """Apply deterministic ontology-quality gates after Turtle syntax validation."""
    candidate_graph = _parse_turtle_text(candidate_ttl)
    previous_graph = _parse_turtle_text(previous_ttl)

    candidate_terms = _schema_terms(candidate_graph)
    previous_terms = _schema_terms(previous_graph)
    deleted_terms = sorted(previous_terms - candidate_terms, key=local_name)
    if deleted_terms:
        names = ", ".join(local_name(item) for item in deleted_terms[:20])
        return False, f"Candidate deleted existing schema terms: {names}"

    out_of_namespace_terms = sorted(
        (
            term
            for term in candidate_terms
            if not str(term).startswith(ONTOLOGY_NAMESPACE)
            and not str(term).startswith("http://www.w3.org/")
        ),
        key=local_name,
    )
    if out_of_namespace_terms:
        names = ", ".join(local_name(item) for item in out_of_namespace_terms[:20])
        return False, f"Candidate introduced out-of-namespace schema terms: {names}"

    declared_named_individuals = set(candidate_graph.subjects(RDF.type, OWL.NamedIndividual))
    typed_uri_subjects = {
        subject
        for subject in candidate_graph.subjects(RDF.type, None)
        if isinstance(subject, URIRef)
    }
    non_schema_typed_resources = typed_uri_subjects - candidate_terms - declared_named_individuals
    if declared_named_individuals or non_schema_typed_resources:
        return (
            False,
            "Candidate contains ABox-like typed resources or declared named individuals.",
        )

    properties = {
        subject
        for rdf_type in (OWL.ObjectProperty, OWL.DatatypeProperty)
        for subject in candidate_graph.subjects(RDF.type, rdf_type)
        if isinstance(subject, URIRef)
    }
    if properties:
        properties_missing_domain = {
            prop for prop in properties if not list(candidate_graph.objects(prop, RDFS.domain))
        }
        properties_missing_range = {
            prop for prop in properties if not list(candidate_graph.objects(prop, RDFS.range))
        }
        missing_domain_ratio = len(properties_missing_domain) / len(properties)
        missing_range_ratio = len(properties_missing_range) / len(properties)
        if (
            missing_domain_ratio > missing_domain_range_threshold
            or missing_range_ratio > missing_domain_range_threshold
        ):
            return (
                False,
                "Candidate failed property domain/range threshold: "
                f"missing domain ratio {missing_domain_ratio:.2f}, "
                f"missing range ratio {missing_range_ratio:.2f}.",
            )

    high_smells = [
        item for item in collect_semantic_smells(candidate_graph) if item["severity"] == "high"
    ]
    if high_smells:
        return False, f"Candidate has high-severity semantic smells: {high_smells[0]['id']}"

    return True, "Candidate passed deterministic ontology quality gates."


def _build_srd_prompt(profile: DomainProfile, page_text: str, cqs: list[dict[str, Any]]) -> str:
    return (
        f"{profile.srd_role}\n\n"
        "Extract a concise Semantic Requirements Document (SRD) from this aviation text. "
        "Return JSON only matching this schema. Do not invent facts beyond the text.\n\n"
        "Required JSON fields:\n"
        "- cq_ids: non-empty string array of CQ identifiers or stable CQ labels from the provided CQs\n"
        "- source_page: zero-based integer source page number\n"
        "- evidence_quotes: non-empty string array of exact short quotes from the source text\n"
        "Recommended JSON fields: key_concepts, relationships, rules_principles, quantities, "
        "situations.\n\n"
        f"Canonical terms: {profile.canonical_terms}\n\n"
        f"CQs:\n{json.dumps(cqs, indent=2)}\n\n"
        f"Text:\n---\n{page_text}\n---\n"
    )


def _build_tip_prompt(profile: DomainProfile, srd: str, cqs: list[dict[str, Any]]) -> str:
    return (
        f"{profile.manager_role}\n\n"
        "Translate the SRD into a precise Technical Implementation Plan (TIP) for OWL/Turtle. "
        "Return JSON only matching this schema. Be concise and include concrete names and "
        "patterns. Do not create ABox individuals.\n\n"
        "Required JSON fields:\n"
        "- classes: non-empty string array of class names to add or reuse\n"
        "- properties: non-empty string array of object/datatype property names to add or reuse\n"
        "- axiom_plan: non-empty string array covering subclass/restriction/equivalence plans\n"
        "- domain_range_plan: non-empty string array covering property domain/range plans\n"
        "- risk_flags: string array of modeling risks, or []\n\n"
        f"CQs:\n{json.dumps(cqs, indent=2)}\n\n"
        f"SRD:\n{srd}\n"
    )


def _build_coder_prompt(profile: DomainProfile, current_ttl: str, tip: str, page_text: str) -> str:
    return (
        f"{profile.coder_domain_guidance}\n\n"
        "Update the ontology and return the COMPLETE Turtle document only. "
        "Do not wrap it in markdown fences. Preserve valid prefixes. Prefer reusable TBox "
        "classes/properties/restrictions over individuals. Ensure RDF/Turtle syntax is valid.\n\n"
        f"Current Turtle ontology:\n---\n{current_ttl}\n---\n\n"
        f"Implementation plan:\n---\n{tip}\n---\n\n"
        f"Source text:\n---\n{page_text}\n---\n"
    )


def generate_ontology(
    pdf_path: str | Path,
    cq_path: str | Path,
    output_path: str | Path,
    domain_profile: str | DomainProfile = "aviation_phak",
    max_page_chars: int = 8000,
    max_pages: int | None = None,
    max_qa_cycles: int = 2,
    dry_run: bool = False,
    temperature: float = 0.0,
    max_tokens: int = 8192,
    artifact_dir: str | Path | None = None,
    run_id: str | None = None,
) -> OntologyGenerationResult:
    """Generate an ontology using the CQ -> SRD -> TIP -> TTL method."""
    profile = get_domain_profile(domain_profile)
    output = Path(output_path)
    ttl = build_initial_ttl_content(profile)
    cqs_by_page = _load_cqs(cq_path)
    artifacts = Path(artifact_dir) if artifact_dir is not None else None
    effective_run_id = run_id or "run"
    accepted_pages: list[int] = []
    failed_pages: list[dict[str, Any]] = []
    if artifacts is not None:
        artifacts.mkdir(parents=True, exist_ok=True)

    pages_processed = 0
    if dry_run:
        valid, message = verify_turtle_text(ttl)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(ttl, encoding="utf-8")
        if artifacts is not None:
            _write_json(
                artifacts / "manifest.json",
                _build_manifest(
                    run_id=effective_run_id,
                    pdf_path=pdf_path,
                    cq_path=cq_path,
                    output_path=output,
                    profile=profile,
                    max_page_chars=max_page_chars,
                    max_pages=max_pages,
                    max_qa_cycles=max_qa_cycles,
                    dry_run=dry_run,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    accepted_pages=accepted_pages,
                    failed_pages=failed_pages,
                ),
            )
        return OntologyGenerationResult(output, pages_processed, valid, message)

    from aviation_agentic_ai.llm.providers import get_llm

    llm = get_llm(temperature=temperature, max_tokens=max_tokens)

    for page in extract_pages(pdf_path, max_pages=max_pages):
        cqs = cqs_by_page.get(str(page.page_number), [])
        if not cqs:
            continue

        page_text = page.text[:max_page_chars]
        try:
            srd_artifact = _invoke_validated_artifact(
                llm,
                _build_srd_prompt(profile, page_text, cqs),
                SRDArtifact,
                "SRD",
                max_qa_cycles,
            )
            srd = _json_dump(srd_artifact.model_dump())
            tip_artifact = _invoke_validated_artifact(
                llm,
                _build_tip_prompt(profile, srd, cqs),
                TIPArtifact,
                "TIP",
                max_qa_cycles,
            )
            tip = _json_dump(tip_artifact.model_dump())
        except Exception as exc:
            failure = {
                "page": page.page_number,
                "stage": "srd_tip_validation",
                "message": str(exc),
            }
            failed_pages.append(failure)
            if artifacts is not None:
                _write_json(
                    artifacts / "manifest.json",
                    _build_manifest(
                        run_id=effective_run_id,
                        pdf_path=pdf_path,
                        cq_path=cq_path,
                        output_path=output,
                        profile=profile,
                        max_page_chars=max_page_chars,
                        max_pages=max_pages,
                        max_qa_cycles=max_qa_cycles,
                        dry_run=dry_run,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        accepted_pages=accepted_pages,
                        failed_pages=failed_pages,
                    ),
                )
            raise RuntimeError(
                f"Failed to generate validated SRD/TIP for page {page.page_number}: {exc}"
            ) from exc

        if artifacts is not None:
            page_prefix = f"page_{page.page_number:02d}"
            _write_json(artifacts / f"{page_prefix}_srd.json", srd_artifact.model_dump())
            _write_json(artifacts / f"{page_prefix}_tip.json", tip_artifact.model_dump())

        last_error = ""
        last_validation: dict[str, Any] = {}
        candidate = ""
        for _ in range(max_qa_cycles + 1):
            try:
                candidate = _invoke_text(llm, _build_coder_prompt(profile, ttl, tip, page_text))
            except Exception as exc:
                failure = {
                    "page": page.page_number,
                    "stage": "candidate_generation",
                    "message": str(exc),
                }
                failed_pages.append(failure)
                last_validation = {
                    "rdf_valid": False,
                    "rdf_message": "",
                    "quality_valid": False,
                    "quality_message": str(exc),
                    "accepted": False,
                }
                if artifacts is not None:
                    page_prefix = f"page_{page.page_number:02d}"
                    (artifacts / f"{page_prefix}_candidate.ttl").write_text(
                        candidate, encoding="utf-8"
                    )
                    _write_json(artifacts / f"{page_prefix}_validation.json", last_validation)
                    _write_json(
                        artifacts / "manifest.json",
                        _build_manifest(
                            run_id=effective_run_id,
                            pdf_path=pdf_path,
                            cq_path=cq_path,
                            output_path=output,
                            profile=profile,
                            max_page_chars=max_page_chars,
                            max_pages=max_pages,
                            max_qa_cycles=max_qa_cycles,
                            dry_run=dry_run,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            accepted_pages=accepted_pages,
                            failed_pages=failed_pages,
                        ),
                    )
                raise RuntimeError(
                    f"Failed to generate Turtle candidate for page {page.page_number}: {exc}"
                ) from exc
            valid, message = verify_turtle_text(candidate)
            quality_valid = False
            quality_message = ""
            if valid:
                quality_valid, quality_message = verify_generated_candidate_quality(candidate, ttl)
                if quality_valid:
                    ttl = candidate if candidate.endswith("\n") else f"{candidate}\n"
                    last_error = quality_message
                    last_validation = {
                        "rdf_valid": valid,
                        "rdf_message": message,
                        "quality_valid": quality_valid,
                        "quality_message": quality_message,
                        "accepted": True,
                    }
                    break
                message = quality_message
            last_error = message
            last_validation = {
                "rdf_valid": valid,
                "rdf_message": message,
                "quality_valid": quality_valid,
                "quality_message": quality_message,
                "accepted": False,
            }
            tip = (
                f"{tip}\n\nTurtle validation or ontology quality gates failed with this error:\n"
                f"{message}\nRevise the Turtle carefully and return a complete valid Turtle "
                "document that preserves existing schema terms and remains TBox-only."
            )
        else:
            failure = {"page": page.page_number, "stage": "candidate_validation", "message": last_error}
            failed_pages.append(failure)
            if artifacts is not None:
                page_prefix = f"page_{page.page_number:02d}"
                (artifacts / f"{page_prefix}_candidate.ttl").write_text(candidate, encoding="utf-8")
                _write_json(artifacts / f"{page_prefix}_validation.json", last_validation)
                _write_json(
                    artifacts / "manifest.json",
                    _build_manifest(
                        run_id=effective_run_id,
                        pdf_path=pdf_path,
                        cq_path=cq_path,
                        output_path=output,
                        profile=profile,
                        max_page_chars=max_page_chars,
                        max_pages=max_pages,
                        max_qa_cycles=max_qa_cycles,
                        dry_run=dry_run,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        accepted_pages=accepted_pages,
                        failed_pages=failed_pages,
                    ),
                )
            raise RuntimeError(f"Failed to generate valid Turtle for page {page.page_number}: {last_error}")

        pages_processed += 1
        accepted_pages.append(page.page_number)
        if artifacts is not None:
            page_prefix = f"page_{page.page_number:02d}"
            (artifacts / f"{page_prefix}_candidate.ttl").write_text(ttl, encoding="utf-8")
            _write_json(artifacts / f"{page_prefix}_validation.json", last_validation)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(ttl, encoding="utf-8")
    valid, message = verify_turtle_text(ttl)
    if artifacts is not None:
        _write_json(
            artifacts / "manifest.json",
            _build_manifest(
                run_id=effective_run_id,
                pdf_path=pdf_path,
                cq_path=cq_path,
                output_path=output,
                profile=profile,
                max_page_chars=max_page_chars,
                max_pages=max_pages,
                max_qa_cycles=max_qa_cycles,
                dry_run=dry_run,
                temperature=temperature,
                max_tokens=max_tokens,
                accepted_pages=accepted_pages,
                failed_pages=failed_pages,
            ),
        )
    return OntologyGenerationResult(output, pages_processed, valid, message)
