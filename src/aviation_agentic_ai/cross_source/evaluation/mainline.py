from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from aviation_agentic_ai.cross_source.alignment.pipeline import align_records
from aviation_agentic_ai.cross_source.contracts import (
    AlignmentStatus,
    CrossSourceAnswer,
    EvidenceLayer,
)
from aviation_agentic_ai.cross_source.qa.answering import AnswerEvidenceCritic
from aviation_agentic_ai.cross_source.supervisor import CrossSourceBuild, answer_from_build


SYSTEM_MODES = ("B0_source_only", "B1_linked_text", "S_cross_source_kg")
SYSTEM_LABELS = {
    "B0_source_only": "Source only",
    "B1_linked_text": "Linked text",
    "S_cross_source_kg": "Cross-source KG",
}
DEFAULT_REQUIRED_LAYERS = {layer.value for layer in EvidenceLayer}


def _answer_for_mode(answer: CrossSourceAnswer, mode: str) -> CrossSourceAnswer:
    if mode == "S_cross_source_kg":
        return answer
    if mode == "B0_source_only":
        retained_layers = {EvidenceLayer.SOURCE_ASSERTION}
        return answer.model_copy(
            update={
                "observation_evidence": [],
                "forecast_evidence": [],
                "system_associations": [],
                "alignment_explanations": [],
                "citations": [
                    item for item in answer.citations if item.layer in retained_layers
                ],
                "rationale": "Matched source-only component baseline.",
            }
        )
    if mode == "B1_linked_text":
        return answer.model_copy(
            update={
                "system_associations": [],
                "alignment_explanations": [],
                "citations": [
                    item
                    for item in answer.citations
                    if item.layer is not EvidenceLayer.SYSTEM_ASSOCIATION
                ],
                "rationale": (
                    "Matched linked-text component baseline using the same accepted links "
                    "without typed graph associations."
                ),
            }
        )
    raise ValueError(f"Unknown answer baseline mode: {mode}")


def _present_layers(answer: CrossSourceAnswer) -> set[str]:
    present: set[str] = set()
    for layer, statements in (
        (EvidenceLayer.SOURCE_ASSERTION, answer.source_assertions),
        (EvidenceLayer.OBSERVATION, answer.observation_evidence),
        (EvidenceLayer.FORECAST, answer.forecast_evidence),
        (EvidenceLayer.SYSTEM_ASSOCIATION, answer.system_associations),
    ):
        if statements:
            present.add(layer.value)
    return present


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def evaluate_answer_baselines(
    rows: Iterable[dict[str, Any]],
    *,
    build: CrossSourceBuild,
) -> dict[str, Any]:
    accumulators: dict[str, dict[str, int]] = {
        mode: defaultdict(int) for mode in SYSTEM_MODES
    }
    cases: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        source_id = str(row.get("source_id") or "")
        question = str(row.get("question") or "")
        if not source_id or not question:
            raise ValueError(f"Benchmark row {index} requires source_id and question")
        required = set(row.get("required_evidence_layers") or DEFAULT_REQUIRED_LAYERS)
        expected_abstain = row.get("expected_abstain")
        expected_alignment = row.get("expected_alignment")
        full = answer_from_build(build, source_id=source_id, question=question)
        case_systems: dict[str, Any] = {}
        for mode in SYSTEM_MODES:
            answer = _answer_for_mode(full, mode)
            present = _present_layers(answer)
            cited = {item.layer.value for item in answer.citations}
            evidence_hits = len(required & present)
            citation_hits = len(required & cited)
            critic_errors = AnswerEvidenceCritic().validate(answer)
            causal_errors = [error for error in critic_errors if "causal" in error]
            alignment_match: bool | None = None
            if isinstance(expected_alignment, str):
                selected = {
                    item.selected_target_label
                    for item in answer.alignment_explanations
                    if item.decision_status is AlignmentStatus.ACCEPTED
                }
                alignment_match = expected_alignment in selected
            abstain_match = (
                answer.abstain is expected_abstain
                if isinstance(expected_abstain, bool)
                else None
            )
            acc = accumulators[mode]
            acc["cases"] += 1
            acc["required_layers"] += len(required)
            acc["evidence_layer_hits"] += evidence_hits
            acc["citation_layer_hits"] += citation_hits
            acc["critic_failures"] += int(bool(critic_errors))
            acc["causal_overstatements"] += len(causal_errors)
            if abstain_match is not None:
                acc["abstain_cases"] += 1
                acc["abstain_matches"] += int(abstain_match)
            if alignment_match is not None:
                acc["alignment_cases"] += 1
                acc["alignment_matches"] += int(alignment_match)
            case_systems[mode] = {
                "abstain": answer.abstain,
                "present_layers": sorted(present),
                "cited_layers": sorted(cited),
                "required_evidence_layer_coverage": _ratio(evidence_hits, len(required)),
                "required_citation_layer_coverage": _ratio(citation_hits, len(required)),
                "expected_abstain_match": abstain_match,
                "expected_alignment_match": alignment_match,
                "evidence_critic_errors": critic_errors,
            }
        cases.append(
            {
                "case_id": row.get("case_id") or f"case-{index:03d}",
                "source_id": source_id,
                "question": question,
                "required_evidence_layers": sorted(required),
                "systems": case_systems,
            }
        )

    systems: dict[str, Any] = {}
    for mode, acc in accumulators.items():
        systems[mode] = {
            "cases": acc["cases"],
            "required_evidence_layer_coverage": _ratio(
                acc["evidence_layer_hits"], acc["required_layers"]
            ),
            "required_citation_layer_coverage": _ratio(
                acc["citation_layer_hits"], acc["required_layers"]
            ),
            "expected_abstain_accuracy": _ratio(
                acc["abstain_matches"], acc["abstain_cases"]
            ),
            "alignment_explanation_accuracy": _ratio(
                acc["alignment_matches"], acc["alignment_cases"]
            ),
            "evidence_critic_failures": acc["critic_failures"],
            "causal_overstatement_count": acc["causal_overstatements"],
        }
    return {
        "snapshot_set_id": build.config["snapshot_set_id"],
        "benchmark_role": "matched component evaluation, not independent semantic gold",
        "systems": systems,
        "cases": cases,
    }


def evaluate_independent_answer_audit(
    rows: Iterable[dict[str, Any]],
    *,
    build: CrossSourceBuild,
) -> dict[str, Any]:
    """Audit generated answers through an evidence-only path independent of generation."""
    weather_ids = set(build.linking.weather_records)
    link_ids = {item.link_id for item in build.linking.links}
    cases: list[dict[str, Any]] = []
    passed = 0
    for index, row in enumerate(rows, start=1):
        source_id = str(row.get("source_id") or "")
        question = str(row.get("question") or "")
        if not source_id or not question:
            raise ValueError(f"Audit row {index} requires source_id and question")
        advisory = build.advisories_by_id[source_id]
        advisory_text = str(advisory.get("text") or "")
        answer = answer_from_build(build, source_id=source_id, question=question)
        statements = [
            *answer.source_assertions,
            *answer.observation_evidence,
            *answer.forecast_evidence,
            *answer.system_associations,
        ]
        citation_keys = {
            (item.source_id, item.layer, item.evidence_text) for item in answer.citations
        }
        expected_abstain = row.get("expected_abstain")
        expected_alignment = row.get("expected_alignment")
        selected_labels = {
            item.selected_target_label
            for item in answer.alignment_explanations
            if item.decision_status is AlignmentStatus.ACCEPTED
        }
        checks: dict[str, bool] = {
            "source_evidence_exact": bool(answer.source_assertions)
            and all(item.evidence_text in advisory_text for item in answer.source_assertions),
            "all_statements_cited": all(
                (item.source_id, item.layer, item.evidence_text) in citation_keys
                for item in statements
            ),
            "weather_sources_registered": all(
                item.source_id in weather_ids
                for item in [*answer.observation_evidence, *answer.forecast_evidence]
            ),
            "system_links_registered": all(
                item.source_id in link_ids for item in answer.system_associations
            ),
            "layer_separation": all(
                item.layer is expected_layer
                for expected_layer, layer_items in (
                    (EvidenceLayer.SOURCE_ASSERTION, answer.source_assertions),
                    (EvidenceLayer.OBSERVATION, answer.observation_evidence),
                    (EvidenceLayer.FORECAST, answer.forecast_evidence),
                    (EvidenceLayer.SYSTEM_ASSOCIATION, answer.system_associations),
                )
                for item in layer_items
            ),
            "evidence_critic_pass": not AnswerEvidenceCritic().validate(answer),
            "expected_abstain_match": (
                answer.abstain is expected_abstain
                if isinstance(expected_abstain, bool)
                else True
            ),
            "expected_alignment_match": (
                expected_alignment in selected_labels
                if isinstance(expected_alignment, str)
                else True
            ),
        }
        verdict = "pass" if all(checks.values()) else "fail"
        passed += int(verdict == "pass")
        cases.append(
            {
                "case_id": row.get("case_id") or f"case-{index:03d}",
                "source_id": source_id,
                "verdict": verdict,
                "checks": checks,
            }
        )
    return {
        "snapshot_set_id": build.config["snapshot_set_id"],
        "evaluator": "independent deterministic Evaluation Agent",
        "review_boundary": (
            "Independent evidence and policy audit; not external aviation-expert certification."
        ),
        "summary": {
            "cases": len(cases),
            "passed": passed,
            "failed": len(cases) - passed,
            "pass_rate": _ratio(passed, len(cases)),
        },
        "cases": cases,
    }


def evaluate_ambiguity_challenge(
    rows: Iterable[dict[str, Any]],
    *,
    build: CrossSourceBuild,
) -> dict[str, Any]:
    challenge_rows = list(rows)
    records = [
        {
            "source_id": str(row["case_id"]),
            "source_family": "cross_source_ambiguity_challenge",
            "text": str(row["text"]),
        }
        for row in challenge_rows
    ]
    run = align_records(
        records,
        facilities=build.facilities,
        terms=build.terms,
        config=build.config,
    )
    mentions = {item.mention_id: item for item in run.mentions}
    candidates_by_mention: dict[str, list[Any]] = defaultdict(list)
    for candidate in run.candidates:
        candidates_by_mention[candidate.mention_id].append(candidate)
    decisions_by_source: dict[str, list[Any]] = defaultdict(list)
    for decision in run.decisions:
        mention = mentions[decision.mention_id]
        if mention.normalized_form == "GS":
            decisions_by_source[mention.source_id].append(decision)
    registry_targets = {term.term_id for term in build.terms}
    accepted_cases = target_matches = 0
    quarantine_cases = quarantine_matches = 0
    out_of_registry = 0
    cases: list[dict[str, Any]] = []
    for row in challenge_rows:
        case_id = str(row["case_id"])
        decisions = decisions_by_source.get(case_id, [])
        if len(decisions) != 1:
            raise ValueError(f"Challenge case {case_id} must produce exactly one GS decision")
        decision = decisions[0]
        candidates = candidates_by_mention[decision.mention_id]
        selected = next(
            (item for item in candidates if item.target_id == decision.target_id), None
        )
        expected_status = str(row["expected_status"])
        expected_target = row.get("expected_target_label")
        status_match = decision.status.value == expected_status
        target_match: bool | None = None
        if expected_status == AlignmentStatus.ACCEPTED.value:
            accepted_cases += 1
            target_match = bool(selected and selected.target_label == expected_target)
            target_matches += int(target_match)
        elif expected_status == AlignmentStatus.QUARANTINED.value:
            quarantine_cases += 1
            quarantine_matches += int(status_match)
        if decision.status is AlignmentStatus.ACCEPTED and decision.target_id not in registry_targets:
            out_of_registry += 1
        cases.append(
            {
                "case_id": case_id,
                "category": row.get("category"),
                "text": row["text"],
                "expected_status": expected_status,
                "expected_target_label": expected_target,
                "actual_status": decision.status.value,
                "actual_target_label": selected.target_label if selected else None,
                "gate_score": decision.gate_score,
                "candidate_margin": decision.candidate_margin,
                "status_match": status_match,
                "target_match": target_match,
                "candidates": [item.model_dump(mode="json") for item in candidates],
            }
        )
    return {
        "snapshot_set_id": build.config["snapshot_set_id"],
        "challenge_role": "authored hard-case evaluation, not external expert gold",
        "summary": {
            "cases": len(cases),
            "accepted_target_cases": accepted_cases,
            "accepted_target_accuracy": _ratio(target_matches, accepted_cases),
            "quarantine_cases": quarantine_cases,
            "quarantine_accuracy": _ratio(quarantine_matches, quarantine_cases),
            "out_of_registry_acceptance_count": out_of_registry,
        },
        "cases": cases,
    }


def render_mainline_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Cross-Source Mainline Evaluation",
        "",
        f"Snapshot set: `{report['snapshot_set_id']}`.",
        "",
        "## Hard Ambiguity Challenge",
        "",
    ]
    challenge = report["ambiguity_challenge"]["summary"]
    lines.extend(
        [
            f"- Cases: {challenge['cases']}",
            f"- Accepted-target accuracy: {challenge['accepted_target_accuracy']:.4f}",
            f"- Quarantine accuracy: {challenge['quarantine_accuracy']:.4f}",
            f"- Out-of-registry acceptances: {challenge['out_of_registry_acceptance_count']}",
            "",
            "This is an authored hard-case challenge, not external aviation-expert gold.",
            "",
            "## Matched Answer Baselines",
            "",
            "| System | Evidence layers | Citation layers | Abstention | Alignment | Critic failures | Causal overstatements |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for mode in SYSTEM_MODES:
        item = report["answer_baselines"]["systems"][mode]
        alignment = item["alignment_explanation_accuracy"]
        lines.append(
            f"| {SYSTEM_LABELS[mode]} | {item['required_evidence_layer_coverage']:.4f} | "
            f"{item['required_citation_layer_coverage']:.4f} | "
            f"{item['expected_abstain_accuracy']:.4f} | "
            f"{'n/a' if alignment is None else f'{alignment:.4f}'} | "
            f"{item['evidence_critic_failures']} | {item['causal_overstatement_count']} |"
        )
    lines.extend(
        [
            "",
            "The linked-text baseline shares accepted record links with the KG system and "
            "therefore isolates typed graph evidence and answer-contract behavior.",
            "Automated policy conformance is not independent semantic answer correctness.",
            "",
        ]
    )
    audit = report["independent_answer_audit"]["summary"]
    lines.extend(
        [
            "## Independent Evaluation Agent Audit",
            "",
            f"- Audited answers: {audit['cases']}",
            f"- Passed: {audit['passed']}",
            f"- Failed: {audit['failed']}",
            f"- Pass rate: {audit['pass_rate']:.4f}",
            "",
            "The evaluator checks exact advisory evidence, statement citations, registered "
            "weather records and graph links, layer separation, alignment expectations, "
            "abstention, and the Evidence Critic through a path separate from answer generation.",
            "It removes human review as a runtime dependency but is not external "
            "aviation-expert certification.",
            "",
        ]
    )
    return "\n".join(lines)
