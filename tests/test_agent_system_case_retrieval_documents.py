"""Deterministic documents used by historical decision-record retrieval."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.case_retrieval_documents import (
    build_case_retrieval_documents,
)
from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusArtifactMetadata,
    CorpusBuildManifest,
    CorpusCase,
    CorpusQueryStore,
)


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
PROV_ENTITY = "http://www.w3.org/ns/prov#Entity"
KJFK = "urn:aviation-agentic-ai:facility:airport:KJFK"
KEWR = "urn:aviation-agentic-ai:facility:airport:KEWR"


def _write_jsonl(
    path: Path,
    rows: list[StrictModel],
) -> CorpusArtifactMetadata:
    data = "".join(
        row.model_dump_json() + "\n"
        for row in rows
    ).encode()
    path.write_bytes(data)
    return CorpusArtifactMetadata(
        path=path.name,
        count=len(rows),
        sha256=hashlib.sha256(data).hexdigest(),
    )


@pytest.fixture
def corpus_store(tmp_path: Path) -> CorpusQueryStore:
    cases = [
        CorpusCase(
            case_id="case:formal",
            case_iri="urn:decision-case:formal",
            reconstruction_iri="urn:decision-case-reconstruction:formal",
            event_id="urn:event:formal",
            run_ids=["run:formal"],
            advisory_source_id="2026-05-19:138",
            event_type_iris=[
                PROV_ENTITY,
                f"{ATM}GroundDelayProgramTMI",
            ],
            facility_ids=[KJFK],
            operational_start="2026-05-19T22:05:00+00:00",
            operational_end="2026-05-20T02:59:00+00:00",
            reason_status="formal",
            reason_value="weather",
        ),
        CorpusCase(
            case_id="case:profile-gap",
            case_iri="urn:decision-case:profile-gap",
            reconstruction_iri=(
                "urn:decision-case-reconstruction:profile-gap"
            ),
            event_id="urn:event:profile-gap",
            run_ids=["run:profile-gap"],
            advisory_source_id="2026-05-19:123",
            event_type_iris=[
                f"{ATM}GroundStopTMI",
                PROV_ENTITY,
            ],
            facility_ids=[KJFK],
            operational_start="2026-05-19T21:00:00+00:00",
            operational_end="2026-05-19T21:30:00+00:00",
            reason_status="profile_gap",
            reason_value="weather",
        ),
        CorpusCase(
            case_id="case:missing",
            case_iri="urn:decision-case:missing",
            reconstruction_iri="urn:decision-case-reconstruction:missing",
            event_id="urn:event:missing",
            run_ids=["run:missing"],
            advisory_source_id="2026-05-20:020",
            event_type_iris=[f"{ATM}GroundDelayProgramTMI"],
            facility_ids=[KEWR],
            operational_start="2026-05-20T12:00:00+00:00",
            operational_end="2026-05-20T13:30:00+00:00",
            reason_status="missing",
            reason_value=None,
        ),
    ]
    artifacts = {
        "cases": _write_jsonl(tmp_path / "cases.jsonl", cases),
        "facts": _write_jsonl(tmp_path / "facts.jsonl", []),
        "case_facts": _write_jsonl(tmp_path / "case_facts.jsonl", []),
        "source_bindings": _write_jsonl(
            tmp_path / "source_bindings.jsonl",
            [],
        ),
    }
    manifest = CorpusBuildManifest(
        corpus_id="corpus:test",
        run_count=3,
        case_count=3,
        fact_count=0,
        source_binding_count=0,
        source_object_count=0,
        artifacts=artifacts,
    )
    (tmp_path / "corpus_manifest.json").write_text(
        manifest.model_dump_json() + "\n",
        encoding="utf-8",
    )
    return CorpusQueryStore(tmp_path)


def test_three_reason_states_have_distinct_canonical_documents(
    corpus_store: CorpusQueryStore,
) -> None:
    documents = {
        row.advisory_source_id: row
        for row in build_case_retrieval_documents(corpus_store)
    }

    assert "Declared reason status: profile gap." in documents[
        "2026-05-19:123"
    ].text
    assert "Source-supported reason category: weather." in documents[
        "2026-05-19:123"
    ].text
    assert documents["2026-05-19:138"].text == (
        "Traffic management measure: Ground Delay Program.\n"
        "Controlled facility: KJFK.\n"
        "Declared reason status: formal.\n"
        "Declared reason category: weather.\n"
        "Operational start time (UTC): 22:05.\n"
        "Operational end time (UTC): 02:59.\n"
        "Operational duration category: 4 to 8 hours."
    )
    assert "Declared reason status: missing." in documents[
        "2026-05-20:020"
    ].text
    assert "Declared reason category:" not in documents[
        "2026-05-20:020"
    ].text
    assert "Source-supported reason category:" not in documents[
        "2026-05-20:020"
    ].text


def test_decision_record_document_excludes_non_record_context(
    corpus_store: CorpusQueryStore,
) -> None:
    document = next(iter(build_case_retrieval_documents(corpus_store)))
    forbidden = (
        document.case_id,
        document.event_id,
        document.advisory_source_id,
        "METAR",
        "TAF",
        "scheduled_arrival_count",
        "cancelled_count",
        "2026-05",
    )

    assert all(value not in document.text for value in forbidden)


@pytest.mark.parametrize(
    ("start", "end", "expected_bucket", "expected_text"),
    [
        (
            "2026-05-19T10:00:00+00:00",
            "2026-05-19T10:59:00+00:00",
            "under_1_hour",
            "under 1 hour",
        ),
        (
            "2026-05-19T10:00:00+00:00",
            "2026-05-19T11:00:00+00:00",
            "1_to_2_hours",
            "1 to 2 hours",
        ),
        (
            "2026-05-19T10:00:00+00:00",
            "2026-05-19T12:00:00+00:00",
            "2_to_4_hours",
            "2 to 4 hours",
        ),
        (
            "2026-05-19T10:00:00+00:00",
            "2026-05-19T14:00:00+00:00",
            "4_to_8_hours",
            "4 to 8 hours",
        ),
        (
            "2026-05-19T10:00:00+00:00",
            "2026-05-19T18:00:00+00:00",
            "8_hours_or_more",
            "8 hours or more",
        ),
    ],
)
def test_duration_boundaries_are_canonical(
    corpus_store: CorpusQueryStore,
    start: str,
    end: str,
    expected_bucket: str,
    expected_text: str,
) -> None:
    case = corpus_store.cases[0].model_copy(
        update={
            "operational_start": start,
            "operational_end": end,
        }
    )
    corpus_store.cases = (case,)

    document = build_case_retrieval_documents(corpus_store)[0]

    assert document.duration_bucket == expected_bucket
    assert (
        f"Operational duration category: {expected_text}."
        in document.text
    )


def test_document_identity_and_facilities_are_stable(
    corpus_store: CorpusQueryStore,
) -> None:
    case = corpus_store.cases[0].model_copy(
        update={"facility_ids": [KJFK, KEWR]}
    )
    corpus_store.cases = (case,)

    first = build_case_retrieval_documents(corpus_store)[0]
    second = build_case_retrieval_documents(corpus_store)[0]

    assert first == second
    assert first.document_id.startswith("case-retrieval-document:")
    assert first.facility_ids == (KEWR, KJFK)
    assert "Controlled facility: KEWR, KJFK." in first.text


@pytest.mark.parametrize(
    "updates",
    [
        {"event_type_iris": [PROV_ENTITY]},
        {"operational_start": None},
        {"operational_end": None},
    ],
)
def test_incomplete_accepted_case_does_not_publish_a_partial_document(
    corpus_store: CorpusQueryStore,
    updates: dict[str, object],
) -> None:
    corpus_store.cases = (
        corpus_store.cases[0].model_copy(update=updates),
    )

    with pytest.raises(ValueError):
        build_case_retrieval_documents(corpus_store)


def test_case_without_formal_facility_edge_remains_retrievable(
    corpus_store: CorpusQueryStore,
) -> None:
    corpus_store.cases = (
        corpus_store.cases[0].model_copy(update={"facility_ids": []}),
    )

    document = build_case_retrieval_documents(corpus_store)[0]

    assert document.facility_ids == ()
    assert (
        "Controlled scope: not represented by a formal facility edge "
        "in the active profile."
        in document.text
    )
