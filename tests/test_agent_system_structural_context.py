"""Structural-context regressions for the compatibility resolution paths."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace

from aviation_agentic_ai.agent_system.agents import (
    FacilityCandidates,
    TermCandidates,
    _facility_ontology_type,
    parse_structured_fields,
    run_facility_agent,
    run_terminology_agent,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentResult,
    AgentStatus,
    AgentTask,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.workflow import (
    IngestContext,
    _facility_candidates_for_mention,
    _facility_node,
    _term_candidates_for_mention,
    _terminology_node,
)


class _EntityType(Enum):
    AIRPORT = "airport"
    ARTCC = "artcc"
    UNKNOWN = "unknown_facility"


@dataclass
class _Code:
    value: str


@dataclass
class _Facility:
    entity_id: str
    preferred_label: str
    entity_type: _EntityType
    codes: list[_Code]
    aliases: list[str]


class _TermCategory(Enum):
    TMI = "traffic_management_initiative"
    PROCEDURE = "operational_procedure"


@dataclass
class _Term:
    term_id: str
    preferred_label: str
    abbreviation: str
    term_category: _TermCategory


def _advisory(content: str) -> SourceRecord:
    return SourceRecord(
        source_id="2026-05-19:123",
        family=SourceFamily.ATCSCC_ADVISORY,
        content=content,
    )


def _resolution_task(role: str) -> AgentTask:
    allowed_tools = (
        ["lookup_nasr_facility", "lookup_artcc", "resolve_facility_alias"]
        if role == "facility"
        else [
            "lookup_faa_glossary",
            "lookup_pcg_term",
            "resolve_term_registry",
            "resolve_schema_event_class",
        ]
    )
    return AgentTask(
        run_id="run",
        source_id="2026-05-19:123",
        objective=f"resolve {role}",
        allowed_tools=allowed_tools,
    )


def test_structured_parser_preserves_controlled_element_slot_and_apt_type() -> None:
    mentions = parse_structured_fields(
        "ATCSCC ADVZY 123 JFK 05/19/2026 CDM GROUND STOP\n"
        "CTL ELEMENT: JFK ELEMENT TYPE: APT\n"
    )

    assert mentions.element_type_code == "APT"
    assert mentions.facility_structural_slot == "controlled_nas_element"
    assert mentions.facility_expected_entity_type == "airport"
    assert mentions.term_structural_slot == "traffic_management_initiative_type"
    assert mentions.term_expected_entity_type == "traffic_management_initiative"


def test_structured_parser_preserves_unknown_element_type_without_generic_mapping() -> None:
    mentions = parse_structured_fields(
        "ATCSCC ADVZY 138 JFK 05/19/2026 CDM GDP\n"
        "CTL ELEMENT: JFK ELEMENT TYPE: UNKNOWN\n"
    )

    assert mentions.element_type_code == "UNKNOWN"
    assert mentions.facility_structural_slot == "controlled_nas_element"
    assert mentions.facility_expected_entity_type is None


def test_workflow_propagates_known_facility_slot_and_expected_type(monkeypatch) -> None:
    import aviation_agentic_ai.agent_system.workflow as workflow

    observed: list[FacilityCandidates] = []

    def capture(*, task, candidates):
        del task
        observed.append(candidates)
        return SimpleNamespace(
            agent_result=AgentResult(status=AgentStatus.ABSTAIN),
            domain_outcome=None,
            authority_source_records=(),
        )

    monkeypatch.setattr(workflow, "_resolve_facility_compatibility", capture)
    monkeypatch.setattr(
        workflow,
        "_CTX_HOLDER",
        IngestContext(advisory=_advisory("CTL ELEMENT: JFK ELEMENT TYPE: APT")),
    )
    mentions = parse_structured_fields(
        "ATCSCC ADVZY 123 JFK 05/19/2026 CDM GROUND STOP\n"
        "CTL ELEMENT: JFK ELEMENT TYPE: APT\n"
    )

    _facility_node({"mentions": mentions})

    assert observed[0].structural_slot == "controlled_nas_element"
    assert observed[0].expected_entity_type == "airport"


def test_workflow_propagates_known_term_slot_and_expected_type(monkeypatch) -> None:
    import aviation_agentic_ai.agent_system.workflow as workflow

    observed: list[TermCandidates] = []

    def capture(*, task, candidates):
        del task
        observed.append(candidates)
        return SimpleNamespace(
            agent_result=AgentResult(status=AgentStatus.ABSTAIN),
            domain_outcome=None,
            authority_source_records=(),
        )

    monkeypatch.setattr(workflow, "_resolve_terminology_compatibility", capture)
    monkeypatch.setattr(
        workflow,
        "_CTX_HOLDER",
        IngestContext(advisory=_advisory("GROUND STOP")),
    )
    mentions = parse_structured_fields(
        "ATCSCC ADVZY 123 JFK 05/19/2026 CDM GROUND STOP\n"
        "CTL ELEMENT: JFK ELEMENT TYPE: APT\n"
    )

    _terminology_node({"mentions": mentions})

    assert observed[0].structural_slot == "traffic_management_initiative_type"
    assert observed[0].expected_entity_type == "traffic_management_initiative"


def test_facility_candidates_are_preserved_for_candidate_level_type_audit() -> None:
    airport = _Facility(
        "urn:facility:z-airport",
        "Airport",
        _EntityType.AIRPORT,
        [_Code("JFK")],
        [],
    )
    artcc = _Facility(
        "urn:facility:a-artcc",
        "Center",
        _EntityType.ARTCC,
        [],
        ["JFK"],
    )

    matches = _facility_candidates_for_mention(
        [airport, artcc],
        "JFK",
        expected_entity_type="airport",
    )

    assert [candidate.entity_id for candidate in matches] == [
        "urn:facility:a-artcc",
        "urn:facility:z-airport",
    ]


def test_unknown_facility_type_does_not_default_to_nas_facility() -> None:
    entity = _Facility(
        "urn:facility:unknown",
        "Unknown facility",
        _EntityType.UNKNOWN,
        [_Code("JFK")],
        [],
    )

    assert _facility_ontology_type(entity) is None
    result = run_facility_agent(
        task=_resolution_task("facility"),
        candidates=FacilityCandidates(
            mention="JFK",
            candidates=[entity],
            source_id="2026-05-19:123",
            structural_slot="controlled_nas_element",
            expected_entity_type="airport",
            advisory_evidence="CTL ELEMENT: JFK",
        ),
    )
    assert result.status is AgentStatus.ABSTAIN
    assert result.evidence_card.claims == []


def test_missing_known_structural_context_makes_zero_provider_calls() -> None:
    candidates = [
        _Facility(
            f"urn:facility:{suffix}",
            suffix,
            entity_type,
            [_Code("JFK")],
            [],
        )
        for suffix, entity_type in (
            ("airport", _EntityType.AIRPORT),
            ("center", _EntityType.ARTCC),
        )
    ]
    calls: list[str] = []

    def provider(role, variables):
        del variables
        calls.append(role)
        raise AssertionError("provider must not be constructed")

    result = run_facility_agent(
        task=_resolution_task("facility"),
        candidates=FacilityCandidates(
            mention="JFK",
            candidates=candidates,
            source_id="2026-05-19:123",
            advisory_evidence="CTL ELEMENT: JFK",
        ),
        model_invoker=provider,
    )

    assert result.status is AgentStatus.ABSTAIN
    assert result.model_calls == []
    assert calls == []


def test_gs_lookup_preserves_both_meanings_before_candidate_compatibility() -> None:
    terms = [
        _Term("urn:term:ground-stop", "Ground Stop", "GS", _TermCategory.TMI),
        _Term("urn:term:glide-slope", "Glide Slope", "GS", _TermCategory.PROCEDURE),
    ]

    matches = _term_candidates_for_mention(terms, "GS")

    assert [candidate.term_id for candidate in matches] == [
        "urn:term:glide-slope",
        "urn:term:ground-stop",
    ]
    provider_calls: list[str] = []

    def provider(role, variables):
        del variables
        provider_calls.append(role)
        raise AssertionError("ambiguous terminology must not call the provider")

    result = run_terminology_agent(
        task=_resolution_task("terminology"),
        candidates=TermCandidates(
            mention="GS",
            candidates=matches,
            source_id="2026-05-19:123",
            structural_slot="traffic_management_initiative_type",
            expected_entity_type="traffic_management_initiative",
            advisory_evidence="GROUND STOP",
        ),
        model_invoker=provider,
    )
    assert result.status is AgentStatus.ABSTAIN
    assert result.model_calls == []
    assert result.evidence_card.uncertainties == ["2 unresolved term candidates"]
    assert provider_calls == []
