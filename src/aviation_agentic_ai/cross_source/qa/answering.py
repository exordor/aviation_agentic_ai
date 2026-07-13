from __future__ import annotations

import re
from collections import defaultdict
from typing import Any, Iterable

from aviation_agentic_ai.cross_source.contracts import (
    AnswerCitation,
    CrossSourceAnswer,
    CrossSourceLink,
    EvidenceLayer,
    EvidenceStatement,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


_AIRPORT_SECTION = re.compile(
    r"(?<![A-Z0-9])([A-Z]{3}(?:/[A-Z]{3})*):(?=\s+IF\b)"
)


def _raw_text_evidence(text: str, question: str) -> str:
    sections = list(_AIRPORT_SECTION.finditer(text))
    requested_indexes = [
        index
        for index, match in enumerate(sections)
        if any(
            re.search(rf"(?<![A-Z0-9]){re.escape(code)}(?![A-Z0-9])", question.upper())
            for code in match.group(1).split("/")
        )
    ]
    if not requested_indexes:
        return text
    first = min(requested_indexes)
    last = max(requested_indexes)
    end = sections[last + 1].start() if last + 1 < len(sections) else len(text)
    return text[sections[first].start() : end].strip()


def _advisory_evidence(record: dict[str, Any], question: str) -> str:
    lines = [line.strip() for line in str(record.get("text") or "").splitlines() if line.strip()]
    for marker in ("IMPACTING CONDITION:", "MESSAGE:", "RAW TEXT:"):
        for index, line in enumerate(lines):
            if marker in line and line != marker:
                evidence = line[line.index(marker) :]
                return _raw_text_evidence(evidence, question) if marker == "RAW TEXT:" else evidence
            if line == marker and index + 1 < len(lines):
                evidence = lines[index + 1]
                return _raw_text_evidence(evidence, question) if marker == "RAW TEXT:" else evidence
    substantive = [line for line in lines if "ATCSCC ADVZY" in line]
    return substantive[0] if substantive else ""


def _is_live_operational_request(question: str) -> bool:
    lowered = question.lower()
    markers = (
        "right now",
        "currently active",
        "live traffic",
        "should we depart",
        "should the flight",
        "现在是否",
        "当前是否",
        "实时",
        "是否应该起飞",
    )
    return any(marker in lowered for marker in markers)


def _facility_tokens(facility_id: str) -> set[str]:
    authority_code = facility_id.rsplit(":", maxsplit=1)[-1].upper()
    tokens = {authority_code}
    if len(authority_code) == 4 and authority_code.startswith("K"):
        tokens.add(authority_code[1:])
    return tokens


def _question_facilities(question: str, links: list[CrossSourceLink]) -> set[str]:
    text = question.upper()
    selected: set[str] = set()
    for link in links:
        if any(
            re.search(rf"(?<![A-Z0-9]){re.escape(token)}(?![A-Z0-9])", text)
            for token in _facility_tokens(link.facility_id)
        ):
            selected.add(link.facility_id)
    return selected


def _select_evidence_links(
    links: list[CrossSourceLink],
    *,
    limit: int,
) -> list[CrossSourceLink]:
    by_facility: dict[str, list[CrossSourceLink]] = defaultdict(list)
    for link in links:
        by_facility[link.facility_id].append(link)
    for facility_links in by_facility.values():
        facility_links.sort(
            key=lambda item: (
                abs((item.evidence_interval.start - item.advisory_interval.start).total_seconds()),
                item.object_id,
            )
        )
    selected = [by_facility[key][0] for key in sorted(by_facility)]
    if len(selected) >= limit:
        return selected[:limit]
    selected_ids = {item.link_id for item in selected}
    remainder = sorted(
        (item for item in links if item.link_id not in selected_ids),
        key=lambda item: (
            abs((item.evidence_interval.start - item.advisory_interval.start).total_seconds()),
            item.object_id,
        ),
    )
    return [*selected, *remainder[: limit - len(selected)]]


class AnswerEvidenceCritic:
    """Fail closed when an answer loses evidence layers or implies causal certainty."""

    causal_phrases = ("caused by the metar", "caused by the taf", "weather caused the advisory")

    def validate(self, answer: CrossSourceAnswer) -> list[str]:
        errors: list[str] = []
        citations = {(item.source_id, item.layer) for item in answer.citations}
        statements = [
            *answer.source_assertions,
            *answer.observation_evidence,
            *answer.forecast_evidence,
            *answer.system_associations,
        ]
        for statement in statements:
            if (statement.source_id, statement.layer) not in citations:
                errors.append(
                    f"missing citation for {statement.layer.value}:{statement.source_id}"
                )
        for statement in answer.system_associations:
            lowered = statement.text.lower()
            if any(phrase in lowered for phrase in self.causal_phrases):
                errors.append("system association contains an inferred causal claim")
            if "does not establish causation" not in lowered:
                errors.append("system association is missing the causality disclaimer")
        for explanation in answer.alignment_explanations:
            if len(explanation.candidates) < 2:
                errors.append("context alignment explanation is missing candidates")
            if any(not candidate.authority_sources for candidate in explanation.candidates):
                errors.append("alignment candidate is missing authority sources")
            if explanation.candidate_margin is None:
                errors.append("alignment explanation is missing candidate margin")
            if explanation.decision_status.value == "accepted":
                if not explanation.selected_target_id or not explanation.selected_target_label:
                    errors.append("accepted context alignment is missing its selected target")
                if not explanation.write_to_formal_kg:
                    errors.append("accepted context alignment must authorize the formal KG write")
            else:
                if not answer.abstain:
                    errors.append("quarantined or rejected alignment requires answer abstention")
                if explanation.write_to_formal_kg:
                    errors.append("quarantined or rejected alignment cannot enter the formal KG")
        if not answer.abstain and not answer.source_assertions:
            errors.append("non-abstaining answer is missing the source assertion layer")
        if not answer.abstain and not (
            answer.observation_evidence or answer.forecast_evidence
        ):
            errors.append("non-abstaining answer is missing observation/forecast evidence")
        return errors


def build_cross_source_answer(
    question: str,
    *,
    advisory: dict[str, Any],
    links: Iterable[CrossSourceLink],
    weather_records: dict[str, dict[str, Any]],
    snapshot_set_id: str,
    max_evidence_per_layer: int = 3,
) -> CrossSourceAnswer:
    advisory_id = str(advisory["source_id"])
    trace_id = stable_id("answer-trace", advisory_id, question, snapshot_set_id)
    common_limitations = [
        "Retrospective source-bounded analysis; not live ATC decision support.",
        "Temporal and facility association does not prove that weather caused an advisory.",
        "Quarantined or rejected acronym mappings are excluded from the formal KG.",
    ]
    if _is_live_operational_request(question):
        return CrossSourceAnswer(
            question=question,
            limitations=common_limitations,
            abstain=True,
            rationale="The request requires live operational decision support outside this system boundary.",
            snapshot_set_id=snapshot_set_id,
            trace_id=trace_id,
        )
    relevant_links = [link for link in links if link.subject_id == advisory_id]
    requested_facilities = _question_facilities(question, relevant_links)
    if requested_facilities:
        relevant_links = [
            link for link in relevant_links if link.facility_id in requested_facilities
        ]
    by_predicate: dict[str, list[CrossSourceLink]] = defaultdict(list)
    for link in relevant_links:
        by_predicate[link.predicate].append(link)

    source_text = _advisory_evidence(advisory, question)
    source_statements: list[EvidenceStatement] = []
    if source_text:
        source_statements.append(
            EvidenceStatement(
                layer=EvidenceLayer.SOURCE_ASSERTION,
                text=f"ATCSCC source assertion: {source_text}",
                source_id=advisory_id,
                evidence_text=source_text,
            )
        )

    observations: list[EvidenceStatement] = []
    forecasts: list[EvidenceStatement] = []
    associations: list[EvidenceStatement] = []
    for predicate, layer, target in (
        ("hasContemporaneousObservation", EvidenceLayer.OBSERVATION, observations),
        ("hasOverlappingForecast", EvidenceLayer.FORECAST, forecasts),
    ):
        ordered = _select_evidence_links(
            by_predicate.get(predicate, []),
            limit=max_evidence_per_layer,
        )
        for link in ordered:
            row = weather_records[link.object_id]
            station = str(row.get("icaoId") or link.facility_id)
            label = "METAR/SPECI observation" if layer is EvidenceLayer.OBSERVATION else "TAF forecast"
            target.append(
                EvidenceStatement(
                    layer=layer,
                    text=f"{label} for {station}: {link.evidence_text}",
                    source_id=link.object_id,
                    evidence_text=link.evidence_text,
                    facility_id=link.facility_id,
                    interval=link.evidence_interval,
                )
            )
            association_text = (
                f"System association: {link.object_id} is linked to {advisory_id} through "
                f"an accepted facility alignment and {link.link_method}; this does not "
                "establish causation."
            )
            associations.append(
                EvidenceStatement(
                    layer=EvidenceLayer.SYSTEM_ASSOCIATION,
                    text=association_text,
                    source_id=link.link_id,
                    evidence_text=link.evidence_text,
                    facility_id=link.facility_id,
                    interval=link.evidence_interval,
                )
            )

    citations = [
        AnswerCitation(
            source_id=statement.source_id,
            evidence_text=statement.evidence_text,
            layer=statement.layer,
        )
        for statement in [*source_statements, *observations, *forecasts, *associations]
    ]
    abstain = not source_statements or not (observations or forecasts)
    rationale = (
        "Answer is separated into source assertion, contemporaneous observation/forecast, "
        "and non-causal system-association layers."
        if not abstain
        else "Insufficient accepted, temporally linked cross-source evidence."
    )
    answer = CrossSourceAnswer(
        question=question,
        source_assertions=source_statements,
        observation_evidence=observations,
        forecast_evidence=forecasts,
        system_associations=associations,
        citations=citations,
        limitations=common_limitations,
        abstain=abstain,
        rationale=rationale,
        snapshot_set_id=snapshot_set_id,
        trace_id=trace_id,
    )
    errors = AnswerEvidenceCritic().validate(answer)
    if errors:
        return answer.model_copy(
            update={
                "abstain": True,
                "rationale": "Evidence critic rejected the answer: " + "; ".join(errors),
            }
        )
    return answer
