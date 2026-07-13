from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.cross_source.alignment.pipeline import AlignmentRun, align_records
from aviation_agentic_ai.cross_source.alignment.registry import (
    build_facility_registry,
    build_term_registry,
)
from aviation_agentic_ai.cross_source.artifacts import read_jsonl, write_json, write_jsonl
from aviation_agentic_ai.cross_source.config import load_cross_source_config
from aviation_agentic_ai.cross_source.contracts import (
    AlignmentExplanation,
    AlignmentMethod,
    AlignmentStatus,
    AnswerCitation,
    CanonicalEntity,
    CrossSourceAnswer,
    EvidenceLayer,
    EvidenceStatement,
    SnapshotSet,
    TermConcept,
)
from aviation_agentic_ai.cross_source.evaluation.cohort import CohortSelection, select_cross_source_cohort
from aviation_agentic_ai.cross_source.graph.materialize import GraphArtifacts, materialize_graphs
from aviation_agentic_ai.cross_source.identifiers import stable_id
from aviation_agentic_ai.cross_source.linking.temporal import LinkingRun, link_weather_records
from aviation_agentic_ai.cross_source.qa.answering import build_cross_source_answer
from aviation_agentic_ai.cross_source.snapshots.registry import (
    activate_snapshot_set,
    build_local_snapshot_set,
)


@dataclass
class CrossSourceBuild:
    config: dict[str, Any]
    snapshot_set: SnapshotSet
    facilities: list[CanonicalEntity]
    terms: list[TermConcept]
    alignment: AlignmentRun
    cohort: CohortSelection
    linking: LinkingRun
    graph_artifacts: GraphArtifacts | None = None

    @property
    def advisories_by_id(self) -> dict[str, dict[str, Any]]:
        return {str(record["source_id"]): record for record in self.cohort.records}


def _quarantine_rows(alignment: AlignmentRun) -> list[dict[str, Any]]:
    candidates_by_mention: dict[str, list[dict[str, Any]]] = {}
    for candidate in alignment.candidates:
        candidates_by_mention.setdefault(candidate.mention_id, []).append(
            candidate.model_dump(mode="json")
        )
    mentions = {mention.mention_id: mention for mention in alignment.mentions}
    rows: list[dict[str, Any]] = []
    for decision in alignment.decisions:
        if decision.status is not AlignmentStatus.QUARANTINED:
            continue
        rows.append(
            {
                "mention": mentions[decision.mention_id].model_dump(mode="json"),
                "candidates": candidates_by_mention.get(decision.mention_id, []),
                "decision": decision.model_dump(mode="json"),
                "autonomous_disposition": {
                    "status": "quarantined",
                    "retry_on_snapshot_refresh": True,
                    "write_to_formal_kg": False,
                },
            }
        )
    return rows


def _write_build_artifacts(build: CrossSourceBuild) -> None:
    processed_root = resolve_project_path(build.config["paths"]["processed_root"])
    kg_root = resolve_project_path(build.config["paths"]["kg_root"])
    processed_root.mkdir(parents=True, exist_ok=True)
    kg_root.mkdir(parents=True, exist_ok=True)

    write_json(processed_root / "snapshot_set.json", build.snapshot_set)
    write_jsonl(processed_root / "facility_registry.jsonl", build.facilities)
    write_jsonl(processed_root / "term_registry.jsonl", build.terms)
    write_jsonl(processed_root / "mentions.jsonl", build.alignment.mentions)
    write_jsonl(processed_root / "alignment_candidates.jsonl", build.alignment.candidates)
    write_jsonl(processed_root / "alignment_decisions.jsonl", build.alignment.decisions)
    write_jsonl(processed_root / "alignment_quarantine.jsonl", _quarantine_rows(build.alignment))
    write_jsonl(processed_root / "legacy_uri_bridge.jsonl", build.alignment.legacy_bridge)
    write_jsonl(processed_root / "trace_events.jsonl", build.alignment.trace_events)
    write_jsonl(processed_root / "cohort_68.jsonl", build.cohort.records)
    write_json(
        processed_root / "cohort_manifest.json",
        {
            "snapshot_set_id": build.config["snapshot_set_id"],
            "record_count": len(build.cohort.records),
            "source_ids": build.cohort.source_ids,
            "matched_codes_by_source": build.cohort.matched_codes_by_source,
        },
    )
    write_jsonl(processed_root / "cross_source_links.jsonl", build.linking.links)
    write_jsonl(
        processed_root / "linked_weather_records.jsonl",
        (
            {"cross_source_id": source_id, **row}
            for source_id, row in sorted(build.linking.weather_records.items())
        ),
    )
    build.graph_artifacts = materialize_graphs(
        facilities=build.facilities,
        terms=build.terms,
        mentions=build.alignment.mentions,
        candidates=build.alignment.candidates,
        decisions=build.alignment.decisions,
        links=build.linking.links,
        canonical_path=kg_root / "canonical.ttl",
        audit_path=kg_root / "audit.ttl",
    )
    status_counts: dict[str, int] = {}
    for decision in build.alignment.decisions:
        status_counts[decision.status.value] = status_counts.get(decision.status.value, 0) + 1
    write_json(
        processed_root / "build_manifest.json",
        {
            "snapshot_set_id": build.config["snapshot_set_id"],
            "advisory_records_scanned": sum(
                1 for _ in read_jsonl(resolve_project_path(build.config["cohort"]["advisory_input"]))
            ),
            "cohort_records": len(build.cohort.records),
            "facility_entities": len(build.facilities),
            "term_concepts": len(build.terms),
            "mentions": len(build.alignment.mentions),
            "alignment_status_counts": status_counts,
            "cross_source_links": len(build.linking.links),
            "canonical_triples": build.graph_artifacts.canonical_triples,
            "audit_triples": build.graph_artifacts.audit_triples,
            "neo4j_nodes": build.graph_artifacts.neo4j.node_count,
            "neo4j_relationships": build.graph_artifacts.neo4j.relationship_count,
        },
    )


def build_cross_source(
    config_path: str | Path = "configs/cross_source_v1.yaml",
    *,
    write_artifacts: bool = True,
) -> CrossSourceBuild:
    config = load_cross_source_config(config_path)
    snapshot_set = activate_snapshot_set(build_local_snapshot_set(config))
    advisories = read_jsonl(resolve_project_path(config["cohort"]["advisory_input"]))
    facilities = build_facility_registry(config)
    terms = build_term_registry(config)
    alignment = align_records(
        advisories,
        facilities=facilities,
        terms=terms,
        config=config,
        invoker=None,
    )
    cohort = select_cross_source_cohort(
        advisories,
        airport_codes=config["cohort"]["airport_codes"],
        expected_count=int(config["cohort"]["expected_record_count"]),
    )
    linking = link_weather_records(
        cohort.records,
        mentions=alignment.mentions,
        decisions=alignment.decisions,
        facilities=facilities,
        metar_rows=read_jsonl(resolve_project_path(config["sources"]["metar"])),
        taf_rows=read_jsonl(resolve_project_path(config["sources"]["taf"])),
        config=config,
    )
    build = CrossSourceBuild(
        config=config,
        snapshot_set=snapshot_set,
        facilities=facilities,
        terms=terms,
        alignment=alignment,
        cohort=cohort,
        linking=linking,
    )
    if write_artifacts:
        _write_build_artifacts(build)
    return build


def answer_from_build(
    build: CrossSourceBuild,
    *,
    source_id: str,
    question: str,
) -> CrossSourceAnswer:
    advisory = build.advisories_by_id.get(source_id)
    if advisory is None:
        raise ValueError(f"source_id is not in the frozen 68-record cohort: {source_id}")
    mention_by_id = {mention.mention_id: mention for mention in build.alignment.mentions}
    requested_decisions: dict[str, tuple[Any, Any]] = {}
    for decision in build.alignment.decisions:
        mention = mention_by_id[decision.mention_id]
        if (
            mention.source_id == source_id
            and re.search(
                rf"(?<![A-Z0-9]){re.escape(mention.normalized_form)}(?![A-Z0-9])",
                question.upper(),
            )
            and (
                decision.status is not AlignmentStatus.ACCEPTED
                or decision.method is AlignmentMethod.CONTEXT_AGENT
            )
        ):
            requested_decisions.setdefault(mention.normalized_form, (mention, decision))
    candidates_by_mention: dict[str, dict[str, Any]] = {}
    for candidate in build.alignment.candidates:
        candidates_by_mention.setdefault(candidate.mention_id, {})[candidate.target_id] = candidate

    explanations: list[AlignmentExplanation] = []
    for term in sorted(requested_decisions):
        mention, decision = requested_decisions[term]
        candidates = sorted(
            candidates_by_mention.get(mention.mention_id, {}).values(),
            key=lambda item: (-item.gate_score, item.target_id),
        )
        selected = next(
            (candidate for candidate in candidates if candidate.target_id == decision.target_id),
            None,
        )
        explanations.append(
            AlignmentExplanation(
                mention_id=mention.mention_id,
                source_id=mention.source_id,
                surface_form=mention.surface_form,
                evidence_text=mention.evidence_text,
                candidates=candidates,
                decision_status=decision.status,
                mapping_confidence=decision.gate_score,
                confidence_basis=(
                    "Autonomous Context Alignment Agent score and candidate margin."
                    if decision.method is AlignmentMethod.CONTEXT_AGENT
                    else "Registry and alignment critic decision."
                ),
                candidate_margin=decision.candidate_margin,
                decision_reason=decision.decision_reason,
                selected_target_id=decision.target_id,
                selected_target_label=selected.target_label if selected else None,
                autonomous_action=decision.status.value,
                write_to_formal_kg=decision.status is AlignmentStatus.ACCEPTED,
            )
        )

    blocked = [
        item for item in explanations if item.decision_status is not AlignmentStatus.ACCEPTED
    ]
    if blocked:
        source_assertions = []
        citations = []
        for explanation in blocked:
            source_assertions.append(
                EvidenceStatement(
                    layer=EvidenceLayer.SOURCE_ASSERTION,
                    text=(
                        f"ATCSCC context for quarantined {explanation.surface_form}: "
                        f"{explanation.evidence_text}"
                    ),
                    source_id=explanation.source_id,
                    evidence_text=explanation.evidence_text,
                )
            )
            citations.append(
                AnswerCitation(
                    source_id=explanation.source_id,
                    evidence_text=explanation.evidence_text,
                    layer=EvidenceLayer.SOURCE_ASSERTION,
                )
            )
        return CrossSourceAnswer(
            question=question,
            source_assertions=source_assertions,
            alignment_explanations=explanations,
            citations=citations,
            limitations=[
                "Retrospective source-bounded analysis; not live ATC decision support.",
                "The requested acronym did not pass autonomous alignment gates.",
                "Quarantined or rejected acronym mappings are excluded from the formal KG.",
            ],
            abstain=True,
            rationale=(
                "Requested acronym mapping was autonomously quarantined or rejected: "
                + ", ".join(item.surface_form for item in blocked)
            ),
            snapshot_set_id=build.config["snapshot_set_id"],
            trace_id=stable_id(
                "answer-trace", source_id, question, build.config["snapshot_set_id"]
            ),
        )
    answer = build_cross_source_answer(
        question,
        advisory=advisory,
        links=build.linking.links,
        weather_records=build.linking.weather_records,
        snapshot_set_id=build.config["snapshot_set_id"],
    )
    return answer.model_copy(update={"alignment_explanations": explanations})
