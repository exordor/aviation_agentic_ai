"""Structural-context regressions for the current authority-resolution paths."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace

from langgraph.runtime import Runtime

from aviation_agentic_ai.agent_system.agents import parse_structured_fields
from aviation_agentic_ai.agent_system.authority_resolution import (
    FacilityAuthorityResolutionInput,
    TerminologyAuthorityResolutionInput,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentTask,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.workflow import (
    IngestContext,
    _facility_candidates_for_mention,
    _facility_authority_node,
    _term_candidates_for_mention,
    _terminology_authority_node,
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
        "ATCSCC ADVZY 123 JFK 05/19/2026 CDM GROUND STOP\nCTL ELEMENT: JFK ELEMENT TYPE: APT\n"
    )

    assert mentions.element_type_code == "APT"
    assert mentions.facility_structural_slot == "controlled_nas_element"
    assert mentions.facility_expected_entity_type == "airport"
    assert mentions.term_structural_slot == "traffic_management_initiative_type"
    assert mentions.term_expected_entity_type == "traffic_management_initiative"


def test_structured_parser_preserves_unknown_element_type_without_generic_mapping() -> None:
    mentions = parse_structured_fields(
        "ATCSCC ADVZY 138 JFK 05/19/2026 CDM GDP\nCTL ELEMENT: JFK ELEMENT TYPE: UNKNOWN\n"
    )

    assert mentions.element_type_code == "UNKNOWN"
    assert mentions.facility_structural_slot == "controlled_nas_element"
    assert mentions.facility_expected_entity_type is None


def test_workflow_propagates_known_facility_slot_and_expected_type(monkeypatch) -> None:
    import aviation_agentic_ai.agent_system.workflow as workflow

    observed: list[FacilityAuthorityResolutionInput] = []

    def capture(*, task, request):
        del task
        observed.append(request)
        return SimpleNamespace(
            evidence_card=None,
            domain_outcome=None,
            authority_source_records=(),
            resolution_task=None,
            resolution_proposal=None,
            resolution_tool_traces=(),
            model_calls=(),
        )

    monkeypatch.setattr(workflow, "resolve_facility_authority", capture)
    context = IngestContext(advisory=_advisory("CTL ELEMENT: JFK ELEMENT TYPE: APT"))
    mentions = parse_structured_fields(
        "ATCSCC ADVZY 123 JFK 05/19/2026 CDM GROUND STOP\nCTL ELEMENT: JFK ELEMENT TYPE: APT\n"
    )

    _facility_authority_node({"mentions": mentions}, Runtime(context=context))

    assert observed[0].structural_slot == "controlled_nas_element"
    assert observed[0].expected_entity_type == "airport"


def test_workflow_propagates_known_term_slot_and_expected_type(monkeypatch) -> None:
    import aviation_agentic_ai.agent_system.workflow as workflow

    observed: list[TerminologyAuthorityResolutionInput] = []

    def capture(*, task, request):
        del task
        observed.append(request)
        return SimpleNamespace(
            evidence_card=None,
            domain_outcome=None,
            authority_source_records=(),
            resolution_task=None,
            resolution_proposal=None,
            resolution_tool_traces=(),
            model_calls=(),
        )

    monkeypatch.setattr(workflow, "resolve_terminology_authority", capture)
    context = IngestContext(advisory=_advisory("GROUND STOP"))
    mentions = parse_structured_fields(
        "ATCSCC ADVZY 123 JFK 05/19/2026 CDM GROUND STOP\nCTL ELEMENT: JFK ELEMENT TYPE: APT\n"
    )

    _terminology_authority_node({"mentions": mentions}, Runtime(context=context))

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


def test_gs_lookup_preserves_both_meanings_before_authority_resolution() -> None:
    terms = [
        _Term("urn:term:ground-stop", "Ground Stop", "GS", _TermCategory.TMI),
        _Term("urn:term:glide-slope", "Glide Slope", "GS", _TermCategory.PROCEDURE),
    ]

    matches = _term_candidates_for_mention(terms, "GS")

    assert [candidate.term_id for candidate in matches] == [
        "urn:term:glide-slope",
        "urn:term:ground-stop",
    ]
