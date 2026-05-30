from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

from aviation_agentic_ai.chunking.chunks import (
    DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    SourceChunk,
    build_nasa_chunk_file,
    read_chunks_jsonl,
)
from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.kg.extraction import validate_kg_file
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.sources.nasa_web import (
    NASA_SOURCE_TYPE,
    load_normalized_nasa_pages,
    read_nasa_source_manifest,
)
from aviation_agentic_ai.utils.io import read_json_document, write_json_document
from aviation_agentic_ai.utils.text import tokenize_terms


NASA_CHUNKING_STRATEGIES = (
    "structure_aware_large",
    "recursive_medium",
    "fixed_large",
    "embedding_semantic",
)

NASA_REVIEW_STATUS = "llm_or_project_seed_not_expert_certified"

BOUNDARY_LAYERS: dict[str, list[str]] = {
    "A_current_core_should_cover": [
        "Atmosphere",
        "Air",
        "AirDensity",
        "Pressure",
        "DynamicPressure",
        "Velocity",
        "Airfoil",
        "Wing",
        "Lift",
        "Drag",
        "Thrust",
        "Weight",
        "AngleOfAttack",
        "Inclination",
        "BoundaryLayer",
        "CenterOfPressure",
        "AerodynamicForce",
        "NewtonLaw",
        "BernoulliPrinciple",
    ],
    "B_nasa_extension_candidates": [
        "LiftEquation",
        "DragEquation",
        "LiftCoefficient",
        "DragCoefficient",
        "ReynoldsNumber",
        "AerodynamicCenter",
        "Streamline",
        "MassFlowRate",
        "Winglet",
        "InducedDrag",
        "Vorticity",
        "Downwash",
        "Compressibility",
        "Viscosity",
        "SurfaceArea",
        "ReferenceArea",
        "EquationVariable",
    ],
    "C_out_of_scope_current_thesis": [
        "aircraft-specific POH/AFM procedures",
        "emergency checklists",
        "current weather and NOTAMs",
        "ATC clearance",
        "legal flight decisions",
        "maintenance airworthiness decisions",
        "aircraft-specific performance calculations for real flights",
    ],
    "D_deferred_operational_procedure_concepts": [
        "runway performance",
        "weight and balance for a real aircraft",
        "aircraft limitations",
        "emergency procedures",
        "route fuel planning",
        "current density altitude for a real airport",
    ],
}

CONCEPT_ALIASES: dict[str, str] = {
    "AirDensity": "Density",
    "Inclination": "AngleOfAttack",
    "Vorticity": "WingtipVortex",
    "ReferenceArea": "PressureDistribution",
}

CONCEPT_TERMS: dict[str, tuple[str, ...]] = {
    "AirDensity": ("air density", "density"),
    "DynamicPressure": ("dynamic pressure",),
    "Velocity": ("velocity", "speed"),
    "AngleOfAttack": ("angle of attack", "inclination"),
    "BoundaryLayer": ("boundary layer",),
    "CenterOfPressure": ("center of pressure",),
    "AerodynamicForce": ("aerodynamic force", "aerodynamic forces"),
    "NewtonLaw": ("newton", "newton's law"),
    "BernoulliPrinciple": ("bernoulli", "bernoulli principle"),
    "LiftEquation": ("lift equation",),
    "DragEquation": ("drag equation",),
    "LiftCoefficient": ("lift coefficient",),
    "DragCoefficient": ("drag coefficient",),
    "ReynoldsNumber": ("reynolds number",),
    "AerodynamicCenter": ("aerodynamic center",),
    "MassFlowRate": ("mass flow", "mass flow rate"),
    "Winglet": ("winglet", "winglets"),
    "InducedDrag": ("induced drag",),
    "Vorticity": ("vorticity", "vortex", "vortices"),
    "Downwash": ("downwash",),
    "Compressibility": ("compressibility",),
    "Viscosity": ("viscosity", "viscous"),
    "SurfaceArea": ("surface area",),
    "ReferenceArea": ("reference area", "wing area"),
    "EquationVariable": ("equation", "variable"),
}

RELATION_CANDIDATE_TERMS = {
    "dependsOn": ("depends on", "depends upon", "function of"),
    "increasesWith": ("increases with", "increase in"),
    "decreasesWith": ("decreases with", "decrease in"),
    "hasEquation": ("equation", "equals"),
    "hasCoefficient": ("coefficient",),
    "explains": ("explains", "describes"),
    "describesEffect": ("effect", "affect", "causes", "results in"),
}

HIGH_RISK_OPERATIONAL_TERMS = (
    "notam",
    "atc clearance",
    "emergency checklist",
    "poh",
    "afm",
    "current weather",
    "route fuel planning",
)


def _percentile(values: list[int], percentile: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((len(ordered) - 1) * percentile)))
    return ordered[index]


def _safe_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _page_snippet(page: dict[str, Any], terms: tuple[str, ...] = ()) -> tuple[int, str]:
    text = str(page.get("cleaned_text", ""))
    sections = page.get("sections", []) if isinstance(page.get("sections"), list) else []
    lowered = text.lower()
    start = 0
    for term in terms:
        index = lowered.find(term.lower())
        if index >= 0:
            start = max(0, index - 80)
            break
    section_order = 0
    for section in sections:
        if not isinstance(section, dict):
            continue
        if int(section.get("text_start", 0)) <= start < int(section.get("text_end", len(text))):
            section_order = int(section.get("order", 0))
            break
    snippet = _safe_text(text[start : start + 260])
    if len(snippet) < 80:
        snippet = _safe_text(text[:260])
    return section_order, snippet


def _concept_terms(concept: str) -> tuple[str, ...]:
    if concept in CONCEPT_TERMS:
        return CONCEPT_TERMS[concept]
    words = re.sub(r"([a-z])([A-Z])", r"\1 \2", concept).lower()
    return (words,)


def _term_hits(pages: list[dict[str, Any]], terms: tuple[str, ...]) -> list[dict[str, str]]:
    hits = []
    for page in pages:
        text = str(page.get("cleaned_text", "")).lower()
        matched_terms = [term for term in terms if term.lower() in text]
        if matched_terms:
            hits.append(
                {
                    "document_id": str(page.get("document_id", "")),
                    "title": str(page.get("title", "")),
                    "url": str(page.get("url", "")),
                    "matched_terms": ", ".join(matched_terms),
                }
            )
    return hits


def _ontology_names(ontology_path: str | Path) -> set[str]:
    path = Path(ontology_path)
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    names = set(re.findall(r":Cl_([A-Za-z0-9]+)\s+a\s+owl:Class", text))
    names.update(re.findall(r":([A-Za-z][A-Za-z0-9]+)\s+a\s+owl:ObjectProperty", text))
    return names


def _chunk_stats(chunks: list[SourceChunk]) -> dict[str, Any]:
    lengths = [len(chunk.text) for chunk in chunks]
    tokens = [chunk.token_count or len(chunk.text.split()) for chunk in chunks]
    by_source = {chunk.source_document for chunk in chunks}
    by_section = {
        (chunk.source_document, chunk.metadata.get("section_id", ""))
        for chunk in chunks
        if chunk.metadata.get("section_id")
    }
    duplicate_text = sum(count - 1 for count in Counter(chunk.text for chunk in chunks).values() if count > 1)
    source_url_count = sum(1 for chunk in chunks if chunk.metadata.get("source_url"))
    return {
        "chunks_total": len(chunks),
        "avg_chars": round(mean(lengths), 2) if lengths else 0.0,
        "p95_chars": _percentile(lengths, 0.95),
        "avg_tokens": round(mean(tokens), 2) if tokens else 0.0,
        "source_documents_covered": len(by_source),
        "sections_covered": len(by_section),
        "empty_chunk_count": sum(1 for chunk in chunks if not chunk.text.strip()),
        "duplicate_chunk_text_count": duplicate_text,
        "source_url_coverage": round(source_url_count / len(chunks), 4) if chunks else 0.0,
    }


def write_nasa_chunking_summary(
    raw_dir: str | Path,
    chunks_dir: str | Path,
    output_dir: str | Path,
    *,
    strategies: tuple[str, ...] = NASA_CHUNKING_STRATEGIES,
    embedding_model: str = DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    semantic_download: bool = True,
    report_name: str = "nasa_chunking_summary",
) -> tuple[Path, Path, dict[str, Any]]:
    corpus_pages = load_normalized_nasa_pages(raw_dir)
    pages = load_normalized_nasa_pages(raw_dir, experiment_only=True)
    expected_sections = sum(len(page.get("sections", [])) for page in pages)
    output_chunks = Path(chunks_dir)
    strategy_results: dict[str, Any] = {}
    all_chunks: list[SourceChunk] = []
    for strategy in strategies:
        chunks_path = output_chunks / f"nasa_bga_aerodynamics.{strategy}.jsonl"
        path, chunks = build_nasa_chunk_file(
            raw_dir,
            chunks_path,
            strategy=strategy,
            experiment_only=True,
            embedding_model=embedding_model,
            semantic_download=semantic_download,
        )
        all_chunks.extend(chunks)
        stats = _chunk_stats(chunks)
        stats["section_coverage"] = (
            round(stats["sections_covered"] / expected_sections, 4) if expected_sections else 0.0
        )
        strategy_results[strategy] = {
            "chunks_path": project_relative_path(path),
            "strategy": strategy,
            **stats,
            "implementation_metadata": chunks[0].metadata if chunks else {},
        }
    result = {
        "metadata": {
            "corpus_id": "nasa_bga_aerodynamics",
            "source_type": NASA_SOURCE_TYPE,
            "corpus_pages_total": len(corpus_pages),
            "experiment_pages_total": len(pages),
            "experiment_subset": "Lessons in Aerodynamics",
            "expected_sections_total": expected_sections,
            "strategies": list(strategies),
            "human_review": False,
            "external_aviation_expert_certified": False,
            "operational_readiness_claimed": False,
        },
        "strategies": strategy_results,
        "chunk_strategy_distribution": {
            strategy: data["chunks_total"] for strategy, data in strategy_results.items()
        },
        "aggregate": _chunk_stats(all_chunks),
        "claim_policy": (
            "NASA chunking summary measures deterministic web-source chunk production only; "
            "it does not select a universal chunker or operationally validate answers."
        ),
    }
    json_path = Path(output_dir) / f"{report_name}.json"
    md_path = Path(output_dir) / f"{report_name}.md"
    write_json_document(result, json_path)
    lines = [
        "# NASA Chunking Summary",
        "",
        f"- Corpus pages collected: {len(corpus_pages)}",
        f"- Experiment pages chunked: {len(pages)}",
        "- Experiment subset: Lessons in Aerodynamics",
        f"- Strategies: {', '.join(strategies)}",
        "- Claim policy: deterministic chunk production only; no universal chunking claim.",
        "",
        "| Strategy | Chunks | Avg chars | P95 chars | Section coverage | URL coverage |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for strategy, data in strategy_results.items():
        lines.append(
            f"| `{strategy}` | {data['chunks_total']} | {data['avg_chars']} | "
            f"{data['p95_chars']} | {data['section_coverage']} | {data['source_url_coverage']} |"
        )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, md_path, result


def build_ontology_boundary_nasa(
    ontology_path: str | Path,
    raw_dir: str | Path,
    manifest_path: str | Path,
    extraction_profile_path: str | Path,
) -> dict[str, Any]:
    corpus_pages = load_normalized_nasa_pages(raw_dir)
    pages = load_normalized_nasa_pages(raw_dir, experiment_only=True)
    manifest = read_nasa_source_manifest(manifest_path)
    ontology_names = _ontology_names(ontology_path)
    concept_records: list[dict[str, Any]] = []
    for layer, concepts in BOUNDARY_LAYERS.items():
        include_now = layer.startswith("A_")
        out_of_scope = layer.startswith("C_") or layer.startswith("D_")
        for concept in concepts:
            normalized = re.sub(r"[^A-Za-z0-9]", "", concept)
            alias_target = CONCEPT_ALIASES.get(normalized, "")
            terms = _concept_terms(normalized)
            hits = _term_hits(pages, terms)
            exact_covered = normalized in ontology_names
            alias_covered = bool(alias_target and alias_target in ontology_names)
            requires_change = include_now and not (exact_covered or alias_covered)
            if out_of_scope:
                status = "intentionally_out_of_scope"
            elif exact_covered:
                status = "covered_existing_ontology"
            elif alias_covered:
                status = "candidate_alias_mapping"
            else:
                status = "candidate_new_class"
            concept_records.append(
                {
                    "concept": concept,
                    "layer": layer,
                    "include_now": include_now and not out_of_scope,
                    "class_or_entity_candidate": normalized,
                    "relation_candidates": [
                        name for name, relation_terms in RELATION_CANDIDATE_TERMS.items() if _term_hits(pages, relation_terms)
                    ],
                    "rationale": (
                        "Covered or candidate because it appears in NASA aerodynamics learning pages."
                        if hits
                        else "Boundary-listed concept with no deterministic NASA term hit in the current corpus."
                    ),
                    "source_examples": hits[:3],
                    "risk_level": "learning" if not out_of_scope else "operational_boundary",
                    "ontology_change_required": requires_change or (status == "candidate_new_class" and bool(hits)),
                    "status": status,
                    "alias_target": alias_target,
                }
            )
    unsupported_relation_patterns = [
        {
            "property_candidate": name,
            "matched_pages": _term_hits(pages, terms)[:5],
            "status": "candidate_property_not_auto_added",
        }
        for name, terms in RELATION_CANDIDATE_TERMS.items()
        if _term_hits(pages, terms) and name not in ontology_names
    ]
    operational_hits = [
        {"term": term, "matched_pages": _term_hits(pages, (term,))}
        for term in HIGH_RISK_OPERATIONAL_TERMS
        if _term_hits(pages, (term,))
    ]
    return {
        "metadata": {
            "corpus_id": "nasa_bga_aerodynamics",
            "ontology_path": project_relative_path(ontology_path),
            "manifest_path": project_relative_path(manifest_path),
            "extraction_profile_path": project_relative_path(extraction_profile_path),
            "pages_total": len(pages),
            "corpus_pages_total": len(corpus_pages),
            "experiment_pages_total": len(pages),
            "experiment_subset": "Lessons in Aerodynamics",
            "manifest_sources_total": len(manifest.get("sources", [])),
            "source_type": NASA_SOURCE_TYPE,
            "human_review": False,
            "external_aviation_expert_certified": False,
            "operational_readiness_claimed": False,
        },
        "existing_ontology_coverage": [
            item for item in concept_records if item["status"] == "covered_existing_ontology"
        ],
        "nasa_extension_candidates": [
            item for item in concept_records if item["status"] == "candidate_new_class"
        ],
        "alias_candidates": [
            item for item in concept_records if item["status"] == "candidate_alias_mapping"
        ],
        "out_of_scope_detections": [
            item for item in concept_records if item["status"] == "intentionally_out_of_scope"
        ],
        "recommended_class_additions": [
            item for item in concept_records if item["ontology_change_required"] and item["status"] == "candidate_new_class"
        ],
        "recommended_property_additions": unsupported_relation_patterns,
        "rejected_deferred_concepts": [
            item for item in concept_records if item["layer"].startswith(("C_", "D_"))
        ],
        "unsupported_relation_patterns": unsupported_relation_patterns,
        "high_risk_operational_concepts_detected": operational_hits,
        "concept_records": concept_records,
        "claim_safety_notes": [
            "This is deterministic boundary validation, not automatic ontology expansion.",
            "All new NASA terms are candidates until separately reviewed and accepted.",
            "NASA educational pages do not create operational readiness or expert certification.",
        ],
    }


def write_ontology_extension_proposal(
    boundary_result: dict[str, Any],
    proposal_path: str | Path,
    output_dir: str | Path,
    *,
    report_name: str = "nasa_ontology_extension_proposal",
) -> tuple[Path, Path, Path, dict[str, Any]]:
    class_candidates = boundary_result.get("recommended_class_additions", [])
    property_candidates = boundary_result.get("recommended_property_additions", [])
    ttl_lines = [
        "@prefix : <http://www.example.org/aviation/phak#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "",
        "# Proposal only. Do not import automatically into the curated ontology.",
    ]
    for item in class_candidates:
        name = item["class_or_entity_candidate"]
        label = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
        ttl_lines.extend(
            [
                "",
                f":Cl_{name} a owl:Class ;",
                f'    rdfs:label "{label}" ;',
                '    rdfs:comment "NASA BGA aerodynamics extension candidate; status=proposed." .',
            ]
        )
    for item in property_candidates:
        name = item["property_candidate"]
        ttl_lines.extend(
            [
                "",
                f":{name} a owl:ObjectProperty ;",
                f'    rdfs:label "{name}" ;',
                '    rdfs:comment "NASA BGA relation candidate; status=proposed." .',
            ]
        )
    proposal_output = Path(proposal_path)
    proposal_output.parent.mkdir(parents=True, exist_ok=True)
    proposal_output.write_text("\n".join(ttl_lines).rstrip() + "\n", encoding="utf-8")
    result = {
        "metadata": {
            "status": "proposed_only",
            "proposal_path": project_relative_path(proposal_output),
            "classes_total": len(class_candidates),
            "properties_total": len(property_candidates),
            "active_ontology_modified": False,
            "human_review": False,
            "external_aviation_expert_certified": False,
        },
        "classes": class_candidates,
        "properties": property_candidates,
        "claim_policy": "Proposal artifact only; curated ontology is not replaced automatically.",
    }
    json_path = Path(output_dir) / f"{report_name}.json"
    md_path = Path(output_dir) / f"{report_name}.md"
    write_json_document(result, json_path)
    lines = [
        "# NASA Ontology Extension Proposal",
        "",
        "- Status: proposed only",
        "- Active ontology modified: false",
        f"- Proposed classes: {len(class_candidates)}",
        f"- Proposed properties: {len(property_candidates)}",
        f"- TTL proposal: `{project_relative_path(proposal_output)}`",
    ]
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return proposal_output, json_path, md_path, result


def write_ontology_boundary_nasa_report(
    ontology_path: str | Path,
    raw_dir: str | Path,
    manifest_path: str | Path,
    extraction_profile_path: str | Path,
    output_dir: str | Path,
    *,
    proposal_path: str | Path | None = None,
    report_name: str = "ontology_boundary_nasa",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_ontology_boundary_nasa(
        ontology_path,
        raw_dir,
        manifest_path,
        extraction_profile_path,
    )
    json_path = Path(output_dir) / f"{report_name}.json"
    md_path = Path(output_dir) / f"{report_name}.md"
    write_json_document(result, json_path)
    lines = [
        "# Ontology Boundary Validation Against NASA BGA",
        "",
        "- Status: deterministic candidate analysis",
        f"- Existing coverage: {len(result['existing_ontology_coverage'])}",
        f"- Alias candidates: {len(result['alias_candidates'])}",
        f"- Recommended class candidates: {len(result['recommended_class_additions'])}",
        f"- Recommended property candidates: {len(result['recommended_property_additions'])}",
        f"- High-risk operational detections: {len(result['high_risk_operational_concepts_detected'])}",
        "- Claim policy: boundary validation only; no automatic ontology expansion.",
        "",
        "## Existing Ontology Coverage",
        "",
    ]
    lines.extend(f"- `{item['concept']}`" for item in result["existing_ontology_coverage"][:20])
    lines.extend(["", "## NASA Extension Candidates", ""])
    lines.extend(
        f"- `{item['concept']}` status=`{item['status']}` change_required={item['ontology_change_required']}"
        for item in result["nasa_extension_candidates"][:30]
    )
    lines.extend(["", "## Alias Candidates", ""])
    lines.extend(
        f"- `{item['concept']}` -> `{item['alias_target']}`"
        for item in result["alias_candidates"]
    )
    lines.extend(["", "## Out-of-Scope Detections", ""])
    lines.extend(f"- `{item['concept']}`" for item in result["out_of_scope_detections"])
    lines.extend(["", "## Claim Safety Notes", ""])
    lines.extend(f"- {note}" for note in result["claim_safety_notes"])
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    if proposal_path is not None:
        write_ontology_extension_proposal(result, proposal_path, output_dir)
    return json_path, md_path, result


def _review_metadata() -> dict[str, Any]:
    return {
        "status": NASA_REVIEW_STATUS,
        "human_review": False,
        "external_aviation_expert_certified": False,
        "aviation_expert_certified": False,
        "notes": "Deterministic seed label; not expert-certified.",
    }


def _label(
    cq_id: str,
    question: str,
    question_type: str,
    page: dict[str, Any],
    entities: list[str],
    answer_key: str,
    *,
    expected_abstention: bool = False,
) -> dict[str, Any]:
    if expected_abstention:
        return {
            "cq_id": cq_id,
            "question": question,
            "question_type": question_type,
            "source_document": "",
            "source_page": -1,
            "source_url": "",
            "expected_source_type": NASA_SOURCE_TYPE,
            "evidence_spans": [],
            "expected_chunk_ids": [],
            "key_entities": entities,
            "answer_key": answer_key,
            "expected_abstention": True,
            "gold_level": "no_answer",
            "review_status": NASA_REVIEW_STATUS,
            "review": _review_metadata(),
        }
    section_order, snippet = _page_snippet(page, tuple(entities))
    return {
        "cq_id": cq_id,
        "question": question,
        "question_type": question_type,
        "source_document": page["document_id"],
        "source_page": section_order,
        "source_url": page["url"],
        "expected_source_type": NASA_SOURCE_TYPE,
        "evidence_spans": [
            {
                "page": section_order,
                "text": snippet,
                "source_document": page["document_id"],
                "source_url": page["url"],
            }
        ],
        "expected_chunk_ids": [
            f"{page['document_id']}-structure_aware_large-s{section_order:02d}-c00"
        ],
        "key_entities": entities,
        "answer_key": answer_key,
        "expected_abstention": False,
        "gold_level": "span",
        "review_status": NASA_REVIEW_STATUS,
        "review": _review_metadata(),
    }


def build_nasa_benchmark_seed(pages: list[dict[str, Any]]) -> dict[str, Any]:
    if not pages:
        return {
            "label_set": "nasa_bga_aerodynamics_seed",
            "review_status": NASA_REVIEW_STATUS,
            "labels": [],
        }
    ordered = sorted(pages, key=lambda item: str(item.get("document_id", "")))
    labels: list[dict[str, Any]] = []
    concept_terms = [
        "lift",
        "drag",
        "dynamic pressure",
        "center of pressure",
        "aerodynamic center",
        "boundary layer",
        "winglet",
        "airfoil",
        "velocity",
        "pressure",
        "density",
        "angle of attack",
        "bernoulli",
        "newton",
        "downwash",
    ]
    for index in range(25):
        page = ordered[index % len(ordered)]
        entity = concept_terms[index % len(concept_terms)]
        labels.append(
            _label(
                f"nasa-concept-{index + 1:03d}",
                f"What does the NASA Glenn page say about {entity}?",
                "concept_factual",
                page,
                [entity],
                f"Use the cited NASA Glenn educational evidence to explain {entity}.",
            )
        )
    for index in range(10):
        page = ordered[(index + 3) % len(ordered)]
        entity = concept_terms[(index + 4) % len(concept_terms)]
        labels.append(
            _label(
                f"nasa-relation-{index + 1:03d}",
                f"How is {entity} related to aerodynamic behavior in the NASA material?",
                "relation_causal",
                page,
                [entity, "aerodynamic"],
                f"Describe the source-backed relation for {entity} without operational advice.",
            )
        )
    equation_pages = [
        page
        for page in ordered
        if "equation" in str(page.get("title", "")).lower()
        or "coefficient" in str(page.get("title", "")).lower()
        or page.get("equations")
    ] or ordered
    for index in range(5):
        page = equation_pages[index % len(equation_pages)]
        labels.append(
            _label(
                f"nasa-equation-{index + 1:03d}",
                f"What equation or coefficient idea is explained on '{page['title']}'?",
                "equation_formula",
                page,
                ["equation", "coefficient"],
                "Report the equation concept as educational source evidence only.",
            )
        )
    for index in range(5):
        page = ordered[(index + 7) % len(ordered)]
        labels.append(
            _label(
                f"nasa-paraphrase-{index + 1:03d}",
                f"Which NASA evidence would help explain this idea in different words: {page['title']}?",
                "paraphrase_terminology",
                page,
                [str(page.get("title", ""))],
                "Map the paraphrased wording to the cited NASA educational page.",
            )
        )
    no_answer_questions = [
        "What is the current NOTAM status for a planned flight based on NASA BGA pages?",
        "What ATC clearance should a pilot accept for today's departure?",
        "Which aircraft-specific emergency checklist step should be performed now?",
        "What exact POH performance number applies to a real aircraft on this runway today?",
        "Is this aircraft legally airworthy for a specific flight?",
    ]
    for index, question in enumerate(no_answer_questions):
        labels.append(
            _label(
                f"nasa-no-answer-{index + 1:03d}",
                question,
                "insufficient_evidence",
                ordered[0],
                ["operational boundary"],
                "Insufficient evidence in NASA BGA educational pages; defer to approved operational sources.",
                expected_abstention=True,
            )
        )
    distribution = Counter(label["question_type"] for label in labels)
    return {
        "label_set": "nasa_bga_aerodynamics_seed",
        "review_status": NASA_REVIEW_STATUS,
        "human_review": False,
        "external_aviation_expert_certified": False,
        "aviation_expert_certified": False,
        "notes": "Deterministic seed benchmark for NASA BGA educational-source experiments.",
        "label_distribution": dict(sorted(distribution.items())),
        "labels": labels,
    }


def write_nasa_benchmark_summary(
    raw_dir: str | Path,
    seed_path: str | Path,
    output_dir: str | Path,
    *,
    report_name: str = "nasa_benchmark_summary",
) -> tuple[Path, Path, dict[str, Any]]:
    pages = load_normalized_nasa_pages(raw_dir, experiment_only=True)
    seed = build_nasa_benchmark_seed(pages)
    seed_output = write_json_document(seed, seed_path)
    labels = seed.get("labels", [])
    supported_total = sum(1 for label in labels if not label.get("expected_abstention"))
    no_answer_total = sum(1 for label in labels if label.get("expected_abstention"))
    result = {
        "metadata": {
            "seed_path": project_relative_path(seed_output),
            "labels_total": len(labels),
            "supported_total": supported_total,
            "no_answer_total": no_answer_total,
            "review_status": NASA_REVIEW_STATUS,
            "human_review": False,
            "external_aviation_expert_certified": False,
            "aviation_expert_certified": False,
        },
        "label_distribution": seed.get("label_distribution", {}),
        "validation": {
            "expected_50_labels": len(labels) == 50,
            "expected_no_answer_5": no_answer_total == 5,
            "source_type": NASA_SOURCE_TYPE,
        },
        "claim_policy": "Seed benchmark is internal thesis scaffolding, not expert gold labels.",
    }
    json_path = Path(output_dir) / f"{report_name}.json"
    md_path = Path(output_dir) / f"{report_name}.md"
    write_json_document(result, json_path)
    lines = [
        "# NASA Benchmark Seed Summary",
        "",
        f"- Labels: {len(labels)}",
        f"- Supported labels: {supported_total}",
        f"- Insufficient-evidence labels: {no_answer_total}",
        f"- Review status: `{NASA_REVIEW_STATUS}`",
        "- External aviation expert certified: false",
        "",
        "| Question type | Count |",
        "| --- | ---: |",
    ]
    for question_type, count in result["label_distribution"].items():
        lines.append(f"| `{question_type}` | {count} |")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, md_path, result


def build_cross_source_seed(
    nasa_pages: list[dict[str, Any]],
    nasa_seed: dict[str, Any],
) -> dict[str, Any]:
    labels: list[dict[str, Any]] = []
    source_labels = [label for label in nasa_seed.get("labels", []) if not label.get("expected_abstention")]
    themes = ["lift", "drag", "angle of attack", "boundary layer", "winglet", "pressure"]
    for index in range(30):
        no_answer = index >= 25
        nasa_label = source_labels[index % len(source_labels)] if source_labels else {}
        theme = themes[index % len(themes)]
        cq_id = f"cross-source-{index + 1:03d}"
        if no_answer:
            labels.append(
                {
                    "cq_id": cq_id,
                    "question": f"Can FAA PHAK and NASA BGA determine a real-time {theme} operational decision?",
                    "question_type": "no_answer_operational_boundary",
                    "expected_source_documents": [],
                    "expected_source_urls": [],
                    "multi_source_required": False,
                    "source_agreement_expected": False,
                    "expected_abstention": True,
                    "gold_level": "no_answer",
                    "evidence_spans_by_source": {},
                    "key_entities": [theme, "operational boundary"],
                    "answer_key": "Insufficient evidence; use POH/AFM, regulations, ATC, and instructor guidance.",
                    "review_status": NASA_REVIEW_STATUS,
                }
            )
            continue
        source_kind = (
            "both_support_concept"
            if index % 5 == 0
            else "nasa_richer_formula_explanation"
            if index % 5 == 1
            else "faa_pilot_training_framing"
            if index % 5 == 2
            else "source_comparison"
        )
        labels.append(
            {
                "cq_id": cq_id,
                "question": f"Compare FAA PHAK and NASA BGA evidence for {theme}.",
                "question_type": source_kind,
                "expected_source_documents": ["06_phak_ch4_0", nasa_label.get("source_document", "")],
                "expected_source_urls": [
                    "FAA PHAK Chapter 4 excerpt",
                    nasa_label.get("source_url", ""),
                ],
                "multi_source_required": source_kind == "source_comparison",
                "source_agreement_expected": source_kind != "nasa_richer_formula_explanation",
                "expected_abstention": False,
                "gold_level": "span",
                "evidence_spans_by_source": {
                    "nasa": nasa_label.get("evidence_spans", []),
                    "faa": [],
                },
                "key_entities": [theme],
                "answer_key": "Compare source-scoped educational evidence without operational advice.",
                "review_status": NASA_REVIEW_STATUS,
            }
        )
    distribution = Counter(label["question_type"] for label in labels)
    return {
        "label_set": "faa_phak_nasa_cross_source_seed",
        "review_status": NASA_REVIEW_STATUS,
        "human_review": False,
        "external_aviation_expert_certified": False,
        "labels_total": len(labels),
        "label_distribution": dict(sorted(distribution.items())),
        "labels": labels,
        "source_pages_total": len(nasa_pages),
    }


def write_cross_source_ontology_validation(
    raw_dir: str | Path,
    nasa_seed_path: str | Path,
    cross_seed_path: str | Path,
    output_dir: str | Path,
    *,
    report_name: str = "cross_source_ontology_validation",
) -> tuple[Path, Path, dict[str, Any]]:
    nasa_pages = load_normalized_nasa_pages(raw_dir, experiment_only=True)
    nasa_seed = read_json_document(nasa_seed_path) if Path(nasa_seed_path).exists() else build_nasa_benchmark_seed(nasa_pages)
    cross_seed = build_cross_source_seed(nasa_pages, nasa_seed)
    cross_output = write_json_document(cross_seed, cross_seed_path)
    nasa_terms = {
        term
        for page in nasa_pages
        for term in tokenize_terms(str(page.get("cleaned_text", "")), stopwords=None)
    }
    overlap_concepts = sorted(term for term in ("lift", "drag", "pressure", "airfoil", "wing") if term in nasa_terms)
    source_specific = sorted(term for term in ("winglet", "equation", "coefficient") if term in nasa_terms)
    result = {
        "metadata": {
            "cross_seed_path": project_relative_path(cross_output),
            "labels_total": len(cross_seed["labels"]),
            "review_status": NASA_REVIEW_STATUS,
            "human_review": False,
            "external_aviation_expert_certified": False,
        },
        "source_overlap_concepts": overlap_concepts,
        "source_specific_concepts": {"nasa": source_specific, "faa_phak": ["pilot training framing"]},
        "ontology_coverage_by_source": {
            "nasa": "candidate_boundary_report_required",
            "faa_phak": "existing_curated_ontology_baseline",
        },
        "cross_source_alias_coverage": {
            "angle of attack/inclination": "candidate_alias_mapping",
            "density/air density": "candidate_alias_mapping",
        },
        "source_agreement_candidates": overlap_concepts,
        "source_conflict_gap_candidates": [],
        "document_routing_targets": ["06_phak_ch4_0", "nasa_bga_aerodynamics"],
        "claim_policy": "Cross-source validation is seed/scaffold evidence, not final thesis evidence.",
    }
    json_path = Path(output_dir) / f"{report_name}.json"
    md_path = Path(output_dir) / f"{report_name}.md"
    write_json_document(result, json_path)
    lines = [
        "# Cross-Source Ontology Validation",
        "",
        f"- Labels: {len(cross_seed['labels'])}",
        f"- Source overlap concepts: {', '.join(overlap_concepts) or 'none'}",
        "- Claim policy: seed/scaffold evidence only.",
    ]
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, md_path, result


def write_nasa_kg_validation_report(
    kg_path: str | Path,
    chunks_path: str | Path,
    profile_path: str | Path,
    ontology_path: str | Path,
    output_dir: str | Path,
    *,
    report_name: str = "nasa_kg_validation",
) -> tuple[Path, Path, dict[str, Any]]:
    validation = validate_kg_file(
        kg_path,
        chunks_path,
        profile_path,
        ontology_path=ontology_path,
    )
    triples_total = int(validation.get("triples_total", 0))
    errors = [error for error in validation.get("errors", []) if isinstance(error, dict)]
    errored_triples = {str(error.get("triple_id", "")) for error in errors if error.get("triple_id")}
    unsupported_class_errors = [
        error for error in errors if "class" in str(error.get("error", "")) and "unsupported" in str(error.get("error", ""))
    ]
    unsupported_property_errors = [
        error
        for error in errors
        if "predicate" in str(error.get("field", ""))
        and "unsupported" in str(error.get("error", ""))
    ]
    provenance_errors = [
        error for error in errors if str(error.get("error", "")) == "missing"
    ]
    evidence_errors = [
        error for error in errors if str(error.get("field", "")) == "evidence_text"
    ]
    valid_triples = max(0, triples_total - len(errored_triples))
    result = {
        **validation,
        "valid_triples": valid_triples,
        "unsupported_class_count": len(unsupported_class_errors),
        "unsupported_property_count": len(unsupported_property_errors),
        "provenance_completeness": (
            round(1 - (len(provenance_errors) / triples_total), 4)
            if triples_total
            else 0.0
        ),
        "evidence_in_source_rate": (
            round(1 - (len(evidence_errors) / triples_total), 4)
            if triples_total
            else 0.0
        ),
        "rejected_triple_count": len(errored_triples),
        "frequent_new_entity_candidates": [],
        "frequent_unsupported_relation_candidates": [
            {"predicate": predicate, "count": count}
            for predicate, count in Counter(
                str(error.get("error", "")).removeprefix("unsupported predicate ")
                for error in unsupported_property_errors
            ).most_common(10)
        ],
        "metadata": {
            "corpus_id": "nasa_bga_aerodynamics",
            "source_type": NASA_SOURCE_TYPE,
            "kg_path": project_relative_path(kg_path),
            "chunks_path": project_relative_path(chunks_path),
            "dry_run_or_existing_kg": True,
            "human_review": False,
            "external_aviation_expert_certified": False,
            "operational_readiness_claimed": False,
        },
        "claim_policy": (
            "NASA KG validation is deterministic schema/provenance validation. "
            "It does not prove semantic correctness or operational readiness."
        ),
    }
    json_path = Path(output_dir) / f"{report_name}.json"
    md_path = Path(output_dir) / f"{report_name}.md"
    write_json_document(result, json_path)
    lines = [
        "# NASA KG Validation",
        "",
        f"- Status: {'valid' if result['valid'] else 'invalid'}",
        f"- Triples total: {triples_total}",
        f"- Valid triples: {valid_triples}",
        f"- Unsupported class count: {result['unsupported_class_count']}",
        f"- Unsupported property count: {result['unsupported_property_count']}",
        f"- Provenance completeness: {result['provenance_completeness']}",
        f"- Evidence in source rate: {result['evidence_in_source_rate']}",
        f"- Rejected triple count: {result['rejected_triple_count']}",
        "- Human review: false",
        "- External aviation expert certified: false",
        "- Claim policy: deterministic validation only; no semantic correctness certification.",
    ]
    if errors:
        lines.extend(["", "## First Errors", ""])
        for error in errors[:10]:
            lines.append(f"- `{error.get('triple_id')}` {error.get('field')}: {error.get('error')}")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, md_path, result


def _load_chunks_if_present(path: str | Path) -> list[SourceChunk]:
    source = Path(path)
    return read_chunks_jsonl(source) if source.exists() else []


def _lexical_hits(question: str, chunks: list[SourceChunk], top_k: int = 10) -> list[SourceChunk]:
    query_terms = tokenize_terms(question, stopwords=None)
    scored = []
    for chunk in chunks:
        score = len(query_terms & tokenize_terms(chunk.text, stopwords=None))
        if score:
            scored.append((score, chunk))
    return [chunk for _score, chunk in sorted(scored, key=lambda item: (-item[0], item[1].chunk_id))[:top_k]]


def _smoke_metrics(labels: list[dict[str, Any]], chunks: list[SourceChunk]) -> dict[str, Any]:
    if not labels:
        return {
            "labels_total": 0,
            "recall_at_5": 0.0,
            "recall_at_10": 0.0,
            "mrr_at_5": 0.0,
            "source_document_recall_at_5": 0.0,
            "source_routing_accuracy": 0.0,
            "multi_source_evidence_rate": 0.0,
            "misrouted_source_rate": 0.0,
            "no_answer_false_evidence_rate": 0.0,
        }
    supported = [label for label in labels if not label.get("expected_abstention")]
    no_answer = [label for label in labels if label.get("expected_abstention")]
    recall5 = []
    recall10 = []
    rr5 = []
    route = []
    multisource = []
    misroute = []
    false_evidence = []
    for label in supported:
        expected_docs = set(label.get("expected_source_documents") or [label.get("source_document")])
        expected_docs.discard("")
        hits = _lexical_hits(str(label.get("question", "")), chunks, top_k=10)
        hit_docs = [chunk.source_document for chunk in hits]
        recall5.append(float(bool(expected_docs & set(hit_docs[:5]))))
        recall10.append(float(bool(expected_docs & set(hit_docs[:10]))))
        first_rank = next(
            (rank for rank, doc in enumerate(hit_docs[:5], start=1) if doc in expected_docs),
            0,
        )
        rr5.append(1 / first_rank if first_rank else 0.0)
        route.append(float(hit_docs[0] in expected_docs) if hit_docs else 0.0)
        multisource.append(float(len(set(hit_docs[:5]) & expected_docs) >= min(2, len(expected_docs))))
        misroute.append(float(bool(hit_docs[:5]) and not (set(hit_docs[:5]) & expected_docs)))
    for label in no_answer:
        hits = _lexical_hits(str(label.get("question", "")), chunks, top_k=5)
        false_evidence.append(float(bool(hits)))
    return {
        "labels_total": len(labels),
        "supported_total": len(supported),
        "no_answer_total": len(no_answer),
        "recall_at_5": round(mean(recall5), 4) if recall5 else 0.0,
        "recall_at_10": round(mean(recall10), 4) if recall10 else 0.0,
        "mrr_at_5": round(mean(rr5), 4) if rr5 else 0.0,
        "source_document_recall_at_5": round(mean(recall5), 4) if recall5 else 0.0,
        "source_routing_accuracy": round(mean(route), 4) if route else 0.0,
        "multi_source_evidence_rate": round(mean(multisource), 4) if multisource else 0.0,
        "misrouted_source_rate": round(mean(misroute), 4) if misroute else 0.0,
        "no_answer_false_evidence_rate": round(mean(false_evidence), 4) if false_evidence else 0.0,
    }


def write_multisource_retrieval_smoke(
    nasa_seed_path: str | Path,
    cross_seed_path: str | Path,
    nasa_chunks_path: str | Path,
    faa_chunks_path: str | Path,
    output_dir: str | Path,
    *,
    report_name: str = "multisource_retrieval_smoke",
) -> tuple[Path, Path, dict[str, Any]]:
    nasa_seed = read_json_document(nasa_seed_path) if Path(nasa_seed_path).exists() else {"labels": []}
    cross_seed = read_json_document(cross_seed_path) if Path(cross_seed_path).exists() else {"labels": []}
    nasa_labels = list(nasa_seed.get("labels", []))[:10]
    cross_labels = list(cross_seed.get("labels", []))[:15]
    labels = nasa_labels + cross_labels
    nasa_chunks = _load_chunks_if_present(nasa_chunks_path)
    faa_chunks = _load_chunks_if_present(faa_chunks_path)
    result = {
        "metadata": {
            "status": "smoke_experiment",
            "labels_total": len(labels),
            "nasa_chunks_path": project_relative_path(nasa_chunks_path),
            "faa_chunks_path": project_relative_path(faa_chunks_path),
            "human_review": False,
            "external_aviation_expert_certified": False,
            "operational_readiness_claimed": False,
        },
        "scenarios": {
            "faa_only": _smoke_metrics(labels, faa_chunks),
            "nasa_only": _smoke_metrics(labels, nasa_chunks),
            "faa_plus_nasa": _smoke_metrics(labels, faa_chunks + nasa_chunks),
        },
        "claim_policy": "Small lexical smoke experiment; not final thesis retrieval evidence.",
    }
    json_path = Path(output_dir) / f"{report_name}.json"
    md_path = Path(output_dir) / f"{report_name}.md"
    write_json_document(result, json_path)
    lines = [
        "# Multi-Source Retrieval Smoke",
        "",
        "- Status: small deterministic lexical smoke experiment",
        "- Claim policy: not final thesis retrieval evidence.",
        "",
        "| Scenario | Recall@5 | Recall@10 | MRR@5 | Source routing | No-answer false evidence |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for scenario, metrics in result["scenarios"].items():
        lines.append(
            f"| `{scenario}` | {metrics['recall_at_5']} | {metrics['recall_at_10']} | "
            f"{metrics['mrr_at_5']} | {metrics['source_routing_accuracy']} | "
            f"{metrics['no_answer_false_evidence_rate']} |"
        )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, md_path, result


def default_nasa_raw_dir() -> Path:
    return resolve_project_path("data/raw/nasa_bga_aerodynamics")


def default_nasa_chunks_dir() -> Path:
    return resolve_project_path("data/chunks")
