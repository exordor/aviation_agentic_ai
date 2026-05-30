from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.ontology.cq import (
    load_cq_artifact,
    normalize_cq_artifact,
    validate_cq_artifact,
)
from aviation_agentic_ai.utils.pdf import extract_pages
from aviation_agentic_ai.utils.text import SOURCE_SCOPE_STOPWORDS, normalize_text, tokenize_terms


@dataclass(frozen=True)
class SourceTopic:
    topic_id: str
    title: str
    summary: str
    ontology_question: str
    boundary_question: str
    expected_answer: str
    key_entities: tuple[str, ...]
    odp_hint: str
    relation_candidates: tuple[str, ...]
    keywords: tuple[str, ...]
    expected_pages: tuple[int, ...]


SOURCE_TOPICS: tuple[SourceTopic, ...] = (
    SourceTopic(
        topic_id="atmosphere_air_composition",
        title="Atmosphere and air composition",
        summary=(
            "The atmosphere is modeled as air surrounding Earth, with air treated as a "
            "gas mixture composed primarily of nitrogen, oxygen, and trace gases."
        ),
        ontology_question=(
            "How should the ontology represent atmosphere, air, constituent gases, "
            "and composition percentages?"
        ),
        boundary_question=(
            "How should atmosphere, air, and constituent gases be modeled as a "
            "composition structure?"
        ),
        expected_answer=(
            "Atmosphere and Air should be material or physical classes connected to "
            "Gas constituents such as Nitrogen, Oxygen, and TraceGas by composition "
            "relations, with percentage values represented as quantities."
        ),
        key_entities=("atmosphere", "air", "nitrogen", "oxygen", "trace gases"),
        odp_hint="Material composition and part-whole",
        relation_candidates=("has constituent gas", "has composition percentage"),
        keywords=("atmosphere", "air", "nitrogen", "oxygen", "argon", "helium"),
        expected_pages=(0,),
    ),
    SourceTopic(
        topic_id="fluid_viscosity_boundary_layer",
        title="Fluid behavior, viscosity, friction, and boundary layer",
        summary=(
            "Air is treated as a fluid that flows, resists deformation through "
            "viscosity, and forms a friction-driven boundary layer on a wing surface."
        ),
        ontology_question=(
            "How should fluid behavior connect air, viscosity, friction, wing surface, "
            "and boundary layer?"
        ),
        boundary_question=(
            "What classes and relations represent air as a fluid with viscosity, "
            "friction, and a boundary layer on a wing?"
        ),
        expected_answer=(
            "Air should be a Fluid with viscosity and flow behavior; friction between "
            "air and wing surface should be modeled as causing or maintaining a "
            "BoundaryLayer adjacent to the surface."
        ),
        key_entities=("air", "fluid", "viscosity", "friction", "boundary layer", "wing"),
        odp_hint="Flow interaction and causal relation",
        relation_candidates=("has viscosity", "adheres to surface", "forms boundary layer"),
        keywords=("fluid", "viscosity", "friction", "boundary layer", "wing", "flow"),
        expected_pages=(1, 2),
    ),
    SourceTopic(
        topic_id="pressure_standard_atmosphere",
        title="Pressure and standard atmosphere",
        summary=(
            "Atmospheric pressure, temperature, density, and standard sea-level values "
            "provide reference conditions for aircraft instruments and performance."
        ),
        ontology_question=(
            "How should atmospheric pressure and standard atmosphere reference values "
            "be represented?"
        ),
        boundary_question=(
            "How should standard atmosphere values for pressure, temperature, and "
            "density be modeled?"
        ),
        expected_answer=(
            "StandardAtmosphere should be a reference situation with pressure, "
            "temperature, density, altitude, and unit-bearing measurements such as "
            "inches of mercury and millibars."
        ),
        key_entities=("standard atmosphere", "atmospheric pressure", "temperature", "density"),
        odp_hint="Quantity and situation",
        relation_candidates=("has pressure", "has temperature", "has density", "defined at altitude"),
        keywords=(
            "atmospheric pressure",
            "standard atmosphere",
            "sea level pressure",
            "temperature",
            "density",
            "inches of mercury",
            "millibars",
        ),
        expected_pages=(2, 3),
    ),
    SourceTopic(
        topic_id="pressure_density_altitude_humidity_performance",
        title="Pressure altitude, density altitude, humidity, and performance",
        summary=(
            "Pressure altitude and density altitude are performance reference "
            "quantities; nonstandard temperature, pressure, and humidity change air "
            "density and aircraft performance."
        ),
        ontology_question=(
            "How should pressure altitude, density altitude, humidity, air density, "
            "and aircraft performance effects be connected?"
        ),
        boundary_question=(
            "What causal schema links pressure altitude, density altitude, humidity, "
            "air density, and aircraft performance?"
        ),
        expected_answer=(
            "PressureAltitude and DensityAltitude should be altitude quantities; "
            "temperature, pressure, and humidity conditions affect AirDensity, and "
            "changed AirDensity affects AircraftPerformance."
        ),
        key_entities=(
            "pressure altitude",
            "density altitude",
            "humidity",
            "air density",
            "aircraft performance",
        ),
        odp_hint="Causal relation and quantity",
        relation_candidates=("affects air density", "increases density altitude", "affects performance"),
        keywords=(
            "pressure altitude",
            "density altitude",
            "humidity",
            "water vapor",
            "performance",
            "air density",
        ),
        expected_pages=(3, 4),
    ),
    SourceTopic(
        topic_id="newton_laws",
        title="Newton laws",
        summary=(
            "Newton's laws are used to relate force, mass, acceleration, action, and "
            "reaction to aircraft motion and propulsion."
        ),
        ontology_question=(
            "How should Newtonian laws connect force, mass, acceleration, and "
            "action-reaction effects?"
        ),
        boundary_question=(
            "How should Newton's laws be represented as force and motion relations "
            "for aircraft?"
        ),
        expected_answer=(
            "NewtonLaw concepts should relate Force, Mass, Acceleration, Action, and "
            "Reaction, including propulsion examples where rearward gas or air motion "
            "produces forward aircraft force."
        ),
        key_entities=("Newton's laws", "force", "mass", "acceleration", "action", "reaction"),
        odp_hint="Force relation and causal relation",
        relation_candidates=("causes acceleration", "has equal opposite reaction"),
        keywords=("newton", "force", "mass", "acceleration", "action", "reaction"),
        expected_pages=(5,),
    ),
    SourceTopic(
        topic_id="bernoulli_venturi",
        title="Bernoulli principle and venturi",
        summary=(
            "Bernoulli's principle and venturi flow are used to relate increased "
            "fluid velocity to decreased pressure."
        ),
        ontology_question=(
            "How should the ontology represent the inverse relation between airflow "
            "velocity and pressure in Bernoulli and venturi contexts?"
        ),
        boundary_question=(
            "What relation captures Bernoulli and venturi pressure decrease as air "
            "velocity increases?"
        ),
        expected_answer=(
            "BernoulliPrinciple or VenturiFlow should connect FlowVelocity and "
            "Pressure with an inverse qualitative relation: increasing velocity "
            "corresponds to decreasing static pressure."
        ),
        key_entities=("Bernoulli principle", "venturi", "velocity", "pressure", "airflow"),
        odp_hint="Flow interaction and quantity",
        relation_candidates=("increases velocity", "decreases pressure", "inversely related to"),
        keywords=("bernoulli", "venturi", "velocity", "pressure", "airflow"),
        expected_pages=(5,),
    ),
    SourceTopic(
        topic_id="airfoil_structure",
        title="Airfoil structure",
        summary=(
            "Airfoils are described through structural features including leading "
            "edge, trailing edge, chord line, mean camber line, and upper and lower "
            "surfaces."
        ),
        ontology_question=(
            "What part-whole structure is needed for airfoil sections and surfaces?"
        ),
        boundary_question=(
            "What partonomy should represent airfoil structure and section geometry?"
        ),
        expected_answer=(
            "Airfoil should have parts or geometric features such as LeadingEdge, "
            "TrailingEdge, ChordLine, MeanCamberLine, UpperSurface, and LowerSurface."
        ),
        key_entities=(
            "airfoil",
            "leading edge",
            "trailing edge",
            "chord line",
            "mean camber line",
            "upper surface",
            "lower surface",
        ),
        odp_hint="Part-whole structure",
        relation_candidates=("has leading edge", "has trailing edge", "has chord line"),
        keywords=(
            "airfoil",
            "leading edge",
            "trailing edge",
            "chord line",
            "mean camber line",
            "upper surface",
            "lower surface",
        ),
        expected_pages=(6,),
    ),
    SourceTopic(
        topic_id="lift_mechanisms",
        title="Lift mechanisms",
        summary=(
            "Lift is explained through multiple mechanisms: positive pressure below "
            "the wing, lowered pressure above it, downwash, flow turning, and "
            "Newtonian reaction."
        ),
        ontology_question=(
            "How should lift mechanisms connect pressure differences, flow turning, "
            "downwash, and reaction forces?"
        ),
        boundary_question=(
            "How should lift be modeled as an aerodynamic force produced by pressure "
            "differences and flow turning?"
        ),
        expected_answer=(
            "Lift should be an AerodynamicForce caused by pressure distribution, "
            "positive pressure below, lower pressure above, downwash, and flow turning "
            "around an airfoil."
        ),
        key_entities=("lift", "pressure difference", "downwash", "flow turning", "airfoil"),
        odp_hint="Force relation and flow interaction",
        relation_candidates=("produces lift", "causes downwash", "turns airflow"),
        keywords=("lift", "pressure", "downwash", "flow turning", "airfoil", "reaction"),
        expected_pages=(7, 8),
    ),
    SourceTopic(
        topic_id="aoa_pressure_distribution_cp",
        title="Angle of attack, pressure distribution, and center of pressure",
        summary=(
            "Changing angle of attack changes pressure distribution over an airfoil "
            "and shifts the center of pressure."
        ),
        ontology_question=(
            "How should angle of attack relate to pressure distribution and center of "
            "pressure changes?"
        ),
        boundary_question=(
            "What schema links angle of attack to airfoil pressure distribution and "
            "center of pressure movement?"
        ),
        expected_answer=(
            "AngleOfAttack should be an angular quantity of an Airfoil relative to "
            "airflow, affecting PressureDistribution and CenterOfPressure location."
        ),
        key_entities=("angle of attack", "pressure distribution", "center of pressure", "airfoil"),
        odp_hint="Quantity and causal relation",
        relation_candidates=("affects pressure distribution", "moves center of pressure"),
        keywords=("angle of attack", "pressure distribution", "center of pressure", "cp", "airfoil"),
        expected_pages=(7,),
    ),
    SourceTopic(
        topic_id="wingtip_vortex_winglets",
        title="Wingtip vortex and winglets",
        summary=(
            "Finite wings create wingtip vortices as high-pressure air curls around "
            "the tip toward lower pressure, and winglets are relevant structures for "
            "reducing vortex effects."
        ),
        ontology_question=(
            "How should wingtip vortices and winglets be related to pressure "
            "differences and induced effects?"
        ),
        boundary_question=(
            "How should wingtip vortex formation and winglet mitigation be modeled?"
        ),
        expected_answer=(
            "WingtipVortex should be a flow phenomenon caused by pressure difference "
            "around a wing tip; Winglet should be a wing component that mitigates or "
            "reduces vortex-related induced effects."
        ),
        key_entities=("wingtip vortex", "wing tip", "winglet", "pressure difference", "induced drag"),
        odp_hint="Flow interaction and causal relation",
        relation_candidates=("forms wingtip vortex", "mitigates vortex", "causes induced drag"),
        keywords=("wingtip", "wing tip", "vortex", "winglet", "induced drag", "pressure"),
        expected_pages=(8,),
    ),
)

def _write_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(lines: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _norm_text(value: str) -> str:
    return normalize_text(value)


def _tokens(value: str) -> set[str]:
    return tokenize_terms(
        value,
        stopwords=SOURCE_SCOPE_STOPWORDS,
        normalize_apostrophes=True,
    )


def _score_keywords(text: str, keywords: tuple[str, ...]) -> int:
    normalized = _norm_text(text)
    return sum(1 for keyword in keywords if _norm_text(keyword) in normalized)


def _page_evidence(pages: list[dict[str, Any]], topic: SourceTopic) -> list[int]:
    scored = [
        (page["page_number"], _score_keywords(str(page["text"]), topic.keywords))
        for page in pages
    ]
    expected_hits = [
        page
        for page, score in scored
        if page in topic.expected_pages and score > 0
    ]
    if expected_hits:
        return expected_hits
    hits = sorted(
        ((page, score) for page, score in scored if score > 0),
        key=lambda item: (-item[1], item[0]),
    )
    if not hits:
        return []
    return [page for page, _ in hits[:2]]


def read_pdf_pages(pdf_path: str | Path) -> list[dict[str, Any]]:
    """Read PDF text through the shared extractor and preserve stable page numbers."""
    return [
        {
            "page_number": page.page_number,
            "char_count": len(page.text),
            "text": page.text,
        }
        for page in extract_pages(pdf_path)
    ]


def build_source_scope(pdf_path: str | Path) -> dict[str, Any]:
    """Build deterministic source scope metadata for the PHAK Chapter 4 excerpt."""
    pdf = Path(pdf_path)
    pages = read_pdf_pages(pdf)
    topic_entries: list[dict[str, Any]] = []
    page_topic_map: dict[int, list[str]] = {int(page["page_number"]): [] for page in pages}

    for topic in SOURCE_TOPICS:
        evidence_pages = _page_evidence(pages, topic)
        if evidence_pages:
            for page_number in evidence_pages:
                page_topic_map.setdefault(page_number, []).append(topic.title)
            topic_entries.append(
                {
                    "id": topic.topic_id,
                    "title": topic.title,
                    "source_pages": evidence_pages,
                    "summary": topic.summary,
                    "ontology_question": topic.ontology_question,
                    "key_concepts": list(topic.key_entities),
                    "relation_candidates": list(topic.relation_candidates),
                }
            )

    page_summaries = []
    for page in pages:
        page_number = int(page["page_number"])
        topics = page_topic_map.get(page_number, [])
        if topics:
            summary = "Covers " + "; ".join(topics) + "."
        else:
            summary = "Contains no scoped ontology topic beyond document pagination."
        page_summaries.append(
            {
                "page": page_number,
                "char_count": page["char_count"],
                "matched_topics": topics,
                "summary": summary,
            }
        )

    key_concepts = sorted({concept for topic in topic_entries for concept in topic["key_concepts"]})
    relation_candidates = sorted(
        {relation for topic in topic_entries for relation in topic["relation_candidates"]}
    )

    return {
        "source_document": pdf.stem,
        "source_path": project_relative_path(pdf),
        "method": "deterministic lexical PDF scope from extract_pages; no LLM",
        "page_count": len(pages),
        "page_summaries": page_summaries,
        "core_themes": topic_entries,
        "in_scope_ontology_questions": [
            topic["ontology_question"] for topic in topic_entries
        ],
        "out_of_scope_notes": [
            "Do not model pilot procedures, training advice, or instrument operating steps as core ontology classes.",
            "Do not encode full numeric performance calculations or lookup-table interpolation from this excerpt.",
            "Do not create individual aircraft, flight, or weather observations unless later source material requires them.",
        ],
        "key_concepts": key_concepts,
        "relation_candidates": relation_candidates,
    }


def build_boundary_cq_artifact(pdf_path: str | Path) -> dict[str, Any]:
    """Build normalized boundary CQs linked to source pages found in the PDF."""
    pdf = Path(pdf_path)
    pages = read_pdf_pages(pdf)
    raw: dict[str, dict[str, list[dict[str, Any]]]] = {pdf.stem: {}}

    for topic in SOURCE_TOPICS:
        evidence_pages = _page_evidence(pages, topic)
        if not evidence_pages:
            continue
        page = str(evidence_pages[0])
        raw[pdf.stem].setdefault(page, []).append(
            {
                "competency_question": topic.boundary_question,
                "key_entities": list(topic.key_entities),
                "odp_hint": topic.odp_hint,
                "expected_answer": topic.expected_answer,
            }
        )

    normalized = normalize_cq_artifact(raw)
    validate_cq_artifact(normalized)
    return normalized


def _iter_cq_items(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for document_id, pages in artifact.items():
        if not isinstance(pages, dict):
            continue
        for page, cqs in pages.items():
            if not isinstance(cqs, list):
                continue
            for cq in cqs:
                if isinstance(cq, dict):
                    item = dict(cq)
                    item["_document_id"] = document_id
                    item["_page"] = page
                    items.append(item)
    return items


def _cq_text(item: dict[str, Any]) -> str:
    parts = [
        str(item.get("competency_question", "")),
        str(item.get("expected_answer", "")),
        " ".join(str(entity) for entity in item.get("key_entities", [])),
    ]
    return " ".join(parts)


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def build_cq_gap_review(
    existing_cq_path: str | Path,
    boundary_cq_path: str | Path,
) -> dict[str, Any]:
    """Compare existing CQs to boundary CQs with deterministic lexical matching."""
    existing = load_cq_artifact(existing_cq_path)
    boundary = load_cq_artifact(boundary_cq_path)
    existing_items = _iter_cq_items(existing)
    boundary_items = _iter_cq_items(boundary)
    existing_tokens = [(item, _tokens(_cq_text(item))) for item in existing_items]
    boundary_terms = set().union(*(_tokens(_cq_text(item)) for item in boundary_items))

    boundary_matches = []
    for boundary_item in boundary_items:
        target_tokens = _tokens(_cq_text(boundary_item))
        scored = [
            (candidate, _jaccard(target_tokens, candidate_tokens))
            for candidate, candidate_tokens in existing_tokens
        ]
        best_item, best_score = max(scored, key=lambda pair: pair[1]) if scored else ({}, 0.0)
        if best_score < 0.16:
            status = "missing"
        elif best_score < 0.28:
            status = "weak"
        else:
            status = "covered"
        boundary_matches.append(
            {
                "boundary_id": boundary_item.get("id"),
                "boundary_question": boundary_item.get("competency_question"),
                "source_page": boundary_item.get("source_page"),
                "status": status,
                "best_existing_id": best_item.get("id"),
                "best_existing_question": best_item.get("competency_question"),
                "lexical_score": round(best_score, 3),
            }
        )

    duplicate_pairs = []
    for index, (left_item, left_tokens) in enumerate(existing_tokens):
        for right_item, right_tokens in existing_tokens[index + 1 :]:
            score = _jaccard(left_tokens, right_tokens)
            if score >= 0.72:
                duplicate_pairs.append(
                    {
                        "left_id": left_item.get("id"),
                        "right_id": right_item.get("id"),
                        "lexical_score": round(score, 3),
                    }
                )

    out_of_scope = []
    for item, item_tokens in existing_tokens:
        overlap = len(item_tokens & boundary_terms) / len(item_tokens) if item_tokens else 0.0
        if overlap < 0.12:
            out_of_scope.append(
                {
                    "id": item.get("id"),
                    "question": item.get("competency_question"),
                    "source_page": item.get("source_page"),
                    "boundary_term_overlap": round(overlap, 3),
                }
            )

    counts = Counter(match["status"] for match in boundary_matches)
    return {
        "method": "deterministic token Jaccard comparison against boundary CQs",
        "existing_cq_count": len(existing_items),
        "boundary_cq_count": len(boundary_items),
        "summary": {
            "covered": counts.get("covered", 0),
            "weak": counts.get("weak", 0),
            "missing": counts.get("missing", 0),
            "duplicate_pairs": len(duplicate_pairs),
            "out_of_scope_signals": len(out_of_scope),
        },
        "boundary_matches": boundary_matches,
        "missing_or_weak": [
            match for match in boundary_matches if match["status"] in {"missing", "weak"}
        ],
        "duplicate_signals": duplicate_pairs[:50],
        "out_of_scope_signals": out_of_scope[:50],
    }


def source_scope_markdown(scope: dict[str, Any]) -> str:
    lines = [
        f"# Source Scope: {scope['source_document']}",
        "",
        f"Method: {scope['method']}",
        "",
        "## Page summaries",
    ]
    for page in scope["page_summaries"]:
        lines.append(f"- Page {page['page']}: {page['summary']}")
    lines.extend(["", "## Core themes"])
    for theme in scope["core_themes"]:
        pages = ", ".join(str(page) for page in theme["source_pages"])
        lines.append(f"- {theme['title']} (pages {pages}): {theme['summary']}")
    lines.extend(["", "## In-scope ontology questions"])
    lines.extend(f"- {question}" for question in scope["in_scope_ontology_questions"])
    lines.extend(["", "## Out-of-scope notes"])
    lines.extend(f"- {note}" for note in scope["out_of_scope_notes"])
    return "\n".join(lines) + "\n"


def gap_review_markdown(review: dict[str, Any]) -> str:
    summary = review["summary"]
    lines = [
        "# CQ Gap Review",
        "",
        f"Method: {review['method']}",
        "",
        "## Summary",
        f"- Existing CQs: {review['existing_cq_count']}",
        f"- Boundary CQs: {review['boundary_cq_count']}",
        f"- Covered boundary CQs: {summary['covered']}",
        f"- Weak boundary CQs: {summary['weak']}",
        f"- Missing boundary CQs: {summary['missing']}",
        f"- Duplicate signals: {summary['duplicate_pairs']}",
        f"- Out-of-scope signals: {summary['out_of_scope_signals']}",
        "",
        "## Missing or weak boundary coverage",
    ]
    if review["missing_or_weak"]:
        for match in review["missing_or_weak"]:
            lines.append(
                "- "
                f"{match['status']}: {match['boundary_question']} "
                f"(page {match['source_page']}, best score {match['lexical_score']})"
            )
    else:
        lines.append("- None.")
    return "\n".join(lines) + "\n"


def write_source_scope_reports(
    pdf_path: str | Path,
    existing_cq_path: str | Path,
    boundary_cq_path: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Write source scope, boundary CQs, and CQ gap review artifacts."""
    output = Path(output_dir)
    boundary_path = Path(boundary_cq_path)

    scope = build_source_scope(pdf_path)
    boundary = build_boundary_cq_artifact(pdf_path)
    _write_json(boundary, boundary_path)

    review = build_cq_gap_review(existing_cq_path, boundary_path)
    paths = {
        "source_scope_json": output / "source_scope.json",
        "source_scope_md": output / "source_scope.md",
        "cq_gap_review_json": output / "cq_gap_review.json",
        "cq_gap_review_md": output / "cq_gap_review.md",
        "boundary_cq_json": boundary_path,
    }
    _write_json(scope, paths["source_scope_json"])
    _write_markdown(source_scope_markdown(scope).splitlines(), paths["source_scope_md"])
    _write_json(review, paths["cq_gap_review_json"])
    _write_markdown(gap_review_markdown(review).splitlines(), paths["cq_gap_review_md"])
    return {
        "source_scope": scope,
        "boundary_cqs": boundary,
        "gap_review": review,
        "paths": {name: project_relative_path(path) for name, path in paths.items()},
    }
