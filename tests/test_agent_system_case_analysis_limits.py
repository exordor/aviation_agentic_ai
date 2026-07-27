"""Limits for applicability, flight outcome, and historical similarity reads."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.query_tools import QueryGraphStore


EVENT_ID = "event:2026-05-19:138"
OTHER_EVENT_IDS = (
    "event:2026-05-19:123",
    "event:2026-05-19:020",
)
ADVISORY_SOURCE_ID = "source:advisory:138"
BTS_SOURCE_ID = "source:bts:aggregate:nyc"


@pytest.fixture
def store() -> QueryGraphStore:
    """A sealed three-record view that includes a BTS aggregate observation."""

    view = object.__new__(QueryGraphStore)
    view.run_dir = Path("/tmp/case-analysis-limits")
    view.manifest = {"run_id": "case-analysis-limits"}
    view.event_ids = [EVENT_ID, *OTHER_EVENT_IDS]
    view.rows = [
        {
            "fact_id": "fact:type",
            "subject": EVENT_ID,
            "predicate": "rdf:type",
            "object": "atm:GroundDelayProgram",
            "source_ids": [ADVISORY_SOURCE_ID],
        },
        {
            "fact_id": "fact:facility",
            "subject": EVENT_ID,
            "predicate": "atm:controlledNASelement",
            "object": "urn:aviation-agentic-ai:facility:airport:KEWR",
            "source_ids": [ADVISORY_SOURCE_ID],
        },
        {
            "fact_id": "fact:start",
            "subject": EVENT_ID,
            "predicate": "atm:effectiveStartTime",
            "object": "2026-05-19T21:00:00Z",
            "source_ids": [ADVISORY_SOURCE_ID],
        },
        {
            "fact_id": "fact:end",
            "subject": EVENT_ID,
            "predicate": "atm:effectiveEndTime",
            "object": "2026-05-20T02:00:00Z",
            "source_ids": [ADVISORY_SOURCE_ID],
        },
        {
            "fact_id": "fact:bts-aggregate",
            "subject": EVENT_ID,
            "predicate": "atm:hasPublicOperationalObservation",
            "object": "bts:aggregate:nyc:active-window",
            "source_ids": [BTS_SOURCE_ID],
        },
    ]
    view.fact_by_id = {row["fact_id"]: row for row in view.rows}
    return view


def _store_snapshot(store: QueryGraphStore) -> str:
    """Produce a value-only snapshot that detects any reader-side mutation."""

    return json.dumps(
        {
            "event_ids": copy.deepcopy(store.event_ids),
            "rows": copy.deepcopy(store.rows),
            "fact_by_id": copy.deepcopy(store.fact_by_id),
        },
        sort_keys=True,
    )


def test_applicability_exposes_only_controlled_facility_and_effective_interval(
    store: QueryGraphStore,
) -> None:
    """Returning type or inferred eligibility would overstate applicability."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import read_applicability

    result = read_applicability(store, event_id=EVENT_ID)

    assert result.status == "partial"
    assert {item["predicate"] for item in result.items} == {
        "atm:controlledNASelement",
        "atm:effectiveStartTime",
        "atm:effectiveEndTime",
    }
    assert result.fact_ids == ("fact:end", "fact:facility", "fact:start")
    assert result.limitation == (
        "no explicit applicability scope beyond controlled facility and effective interval"
    )


def test_observed_flight_outcome_rejects_aggregate_bts_as_flight_evidence(
    store: QueryGraphStore,
) -> None:
    """Using a BTS aggregate as a flight outcome would be an invalid inference."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        read_observed_flight_outcome,
    )

    result = read_observed_flight_outcome(store, event_id=EVENT_ID)

    assert result.status == "insufficient"
    assert result.fact_ids == ()
    assert result.source_ids == ()
    assert result.items == ()
    assert (
        "BTS aggregate observations do not establish an individual-flight outcome"
        in result.limitation
    )


def test_similarity_gate_never_ranks_three_case_fixture(
    store: QueryGraphStore,
) -> None:
    """A fixture-sized set must not be converted into nearest-neighbor advice."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        read_similarity_corpus_gate,
    )

    result = read_similarity_corpus_gate(store, event_ids=tuple(store.event_ids))

    assert result.status == "insufficient"
    assert result.fact_ids == ()
    assert result.source_ids == ()
    assert result.items == ()
    assert result.limitation == (
        "historical similarity requires an approved corpus and comparison profile"
    )


@pytest.mark.parametrize(
    ("reader_name", "arguments"),
    (
        ("read_applicability", {"event_id": "event:unknown"}),
        ("read_observed_flight_outcome", {"event_id": "event:unknown"}),
        ("read_similarity_corpus_gate", {"event_ids": (EVENT_ID, "event:unknown")}),
    ),
)
def test_limit_readers_block_unknown_events(
    store: QueryGraphStore,
    reader_name: str,
    arguments: dict[str, object],
) -> None:
    """Accepting an unknown ID would let a closed plan escape the current run."""

    from aviation_agentic_ai.agent_system import case_analysis_tools

    result = getattr(case_analysis_tools, reader_name)(store, **arguments)

    assert result.status == "blocked"
    assert result.fact_ids == ()
    assert result.source_ids == ()
    assert result.items == ()


def test_limit_readers_do_not_mutate_the_current_store(store: QueryGraphStore) -> None:
    """Any reader-side write would violate the read-only gateway contract."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        read_applicability,
        read_observed_flight_outcome,
        read_similarity_corpus_gate,
    )

    before = _store_snapshot(store)

    read_applicability(store, event_id=EVENT_ID)
    read_observed_flight_outcome(store, event_id=EVENT_ID)
    read_similarity_corpus_gate(store, event_ids=tuple(store.event_ids))

    assert _store_snapshot(store) == before


def test_profile_gap_cannot_become_an_observed_flight_source_fact() -> None:
    """A profile gap is a limitation, never source evidence for flight impact."""

    from aviation_agentic_ai.agent_system.decision_case_contracts import (
        AnswerStatement,
        AnswerStatementKind,
    )

    with pytest.raises(ValidationError, match="source fact statement requires fact"):
        AnswerStatement(
            statement_id="statement:flight-outcome",
            statement_kind=AnswerStatementKind.SOURCE_FACT,
            text="The flight was delayed.",
            support_profile_gap_ids=("gap:observed-flight-outcome",),
            support_source_ids=(BTS_SOURCE_ID,),
        )
