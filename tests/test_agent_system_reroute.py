"""Cross-type regression tests for the first non-GS/GDP event profile."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.agents import parse_structured_fields
from aviation_agentic_ai.agent_system.authority_evidence import NASRAuthorityRecord
from aviation_agentic_ai.agent_system.contracts import SourceFamily, SourceRecord
from aviation_agentic_ai.agent_system.corpus_batch import _preflight
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusQueryStore,
    build_corpus,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.sources import load_advisory_source
from aviation_agentic_ai.agent_system.tmi_event_retrieval_documents import (
    build_tmi_event_retrieval_documents,
)
from aviation_agentic_ai.agent_system.runtime import write_run_manifest
from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
from aviation_agentic_ai.cross_source.contracts import (
    CanonicalEntity,
    CodeValue,
    EntityType,
)
from test_agent_system_authority_evidence import _catalog, _test_inputs


_ADVISORY_PATH = Path(
    "data/processed/nasa_atmonto/aligned/2026-05-14/"
    "atcscc_advisories.jsonl"
)


def _source(source_id: str) -> SourceRecord:
    rows = (
        json.loads(line)
        for line in _ADVISORY_PATH.read_text(encoding="utf-8").splitlines()
        if line
    )
    row = next(record for record in rows if record["source_id"] == source_id)
    return SourceRecord(
        source_id=source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        content=str(row["text"]),
    )


def test_route_rqd_parses_as_reroute_with_atmonto_fields() -> None:
    source = _source("2026-05-19:108")

    mentions = parse_structured_fields(source.content)

    assert mentions.event_type == "REROUTE"
    assert mentions.operational_term == "RR"
    assert mentions.controlled_facility == "ZBW"
    assert mentions.facility_expected_entity_type == "artcc"
    assert mentions.effective_start == "2026-05-19T21:15:00Z"
    assert mentions.effective_end == "2026-05-20T00:00:00Z"
    assert mentions.issued_time == "2026-05-19T21:06:00Z"
    assert mentions.implementation_status == "RQD"
    assert mentions.re_route_type == "ROUTE"
    assert mentions.re_route_reason == "WEATHER"
    assert mentions.re_route_time_type == "ETD"
    assert mentions.extension_probability == "MEDIUM"
    for field in (
        "event_type",
        "operational_term",
        "controlled_facility",
        "effective_start",
        "effective_end",
        "issued_time",
        "implementation_status",
        "re_route_type",
        "re_route_reason",
        "re_route_time_type",
        "extension_probability",
    ):
        assert mentions.evidence_spans[field] in source.content


def test_active_reroute_passes_family_specific_preflight() -> None:
    assert _preflight(_source("2026-05-19:108")) is None
    assert _preflight(_source("2026-05-20:137")) is None


def test_reroute_cancellation_remains_a_deferred_lifecycle_record() -> None:
    result = _preflight(_source("2026-05-20:098"))

    assert result is not None
    assert result.status == "insufficient"
    assert result.reason == "deferred traffic-management lifecycle event"
    assert result.tmi_family == "REROUTE_CANCELLATION"
    assert result.preflight_eligible is False


def test_informational_boundary_is_not_forced_into_tmi_publication() -> None:
    result = _preflight(_source("2026-05-14:059"))

    assert result is not None
    assert result.status == "insufficient"
    assert result.reason == "recognized advisory family outside active publication profile"
    assert result.tmi_family == "ARRIVAL_DELAY"
    assert result.preflight_eligible is False


@pytest.mark.parametrize(
    ("source_id", "artcc", "center_name", "issued_time"),
    [
        ("2026-05-19:108", "ZBW", "BOSTON CENTER", "2026-05-19T21:06:00Z"),
        ("2026-05-20:137", "ZNY", "NEW YORK CENTER", "2026-05-20T20:38:00Z"),
    ],
)
def test_reroute_publishes_atmonto_facts_without_model_or_invalid_artcc_edge(
    tmp_path: Path,
    source_id: str,
    artcc: str,
    center_name: str,
    issued_time: str,
) -> None:
    catalog = _catalog(tmp_path)
    config, _ = _test_inputs(tmp_path)
    guide = load_schema_guide()
    entity = CanonicalEntity(
        entity_id=f"urn:aviation-agentic-ai:facility:artcc:{artcc}",
        entity_type=EntityType.ARTCC,
        preferred_label=center_name,
        codes=[
            CodeValue(scheme="FAA_ARTCC", value=artcc),
            CodeValue(scheme="ICAO_ARTCC", value=f"K{artcc}"),
        ],
    )
    raw_record = f"ARTCC|{artcc}|{center_name}"
    authority_record = NASRAuthorityRecord(
        candidate_id=entity.entity_id,
        member_name="AFF.txt",
        record_locator="AFF.txt:1",
        normalized_raw_record=raw_record,
        raw_record_sha256=sha256(raw_record.encode()).hexdigest(),
        authority_source_ref="faa_nasr:AFF.txt:1",
    )
    catalog = replace(
        catalog,
        facility=replace(
            catalog.facility,
            entities=(*catalog.facility.entities, entity),
            records=(*catalog.facility.records, authority_record),
        ),
    )

    class NoModel:
        def __call__(self, tools):
            raise AssertionError(f"unexpected model activation: {len(tools)} tools")

    run_id = f"run:test-reroute-{source_id.rsplit(':', 1)[-1]}"
    run_dir = tmp_path / f"reroute-run-{source_id.rsplit(':', 1)[-1]}"
    state = run_ingest(
        IngestContext(
            advisory=load_advisory_source(config, source_id),
            facility_candidates=list(catalog.facility.entities),
            term_candidates=list(catalog.terminology.registry_terms),
            authority_catalog=catalog,
            guide=guide,
            run_id=run_id,
            run_started_at=datetime(2026, 5, 20, tzinfo=UTC),
            output_dir=str(run_dir),
            semantic_resolution_tool_model_factory=NoModel(),
            event_evidence_integration_model_factory=NoModel(),
        )
    )

    assert state["resolution_preflight_status"] == "resolved"
    assert state["model_calls"] == []
    assert state["validation"].publishable
    assert state["materialization"] is not None
    facts = {
        (fact.predicate_iri, fact.object_value)
        for fact in state["validation"].accepted
    }
    atm = "https://data.nasa.gov/ontologies/atmonto/ATM#"
    assert {
        ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "atm:ReRouteTMI"),
        (atm + "implementationStatus", "RQD"),
        (atm + "reRouteType", "ROUTE"),
        (atm + "reRouteReason", "WEATHER"),
        (atm + "reRouteTimeType", "ETD"),
        (atm + "extensionProbability", "MEDIUM"),
        (atm + "issuedTime", issued_time),
    }.issubset(facts)
    assert not any(
        predicate == atm + "controlledNASelement"
        for predicate, _ in facts
    )
    assert [
        (gap.field, gap.value, gap.reason)
        for gap in state["validation"].profile_gaps
    ] == [("constrained_area", artcc, "range_not_admitted")]

    write_run_manifest(
        run_dir=run_dir,
        source_id=source_id,
        model_calls=state["model_calls"],
        materialization=state["materialization"],
        schema_slice_id=guide.schema_slice_id,
        schema_checksum=guide.checksum,
        evidence_cards=[
            getattr(result, "evidence_card", result)
            for result in (
                state["advisory_evidence"],
                state["facility_authority_result"],
                state["terminology_authority_result"],
            )
        ],
        graph_patch_raw=state["integration_graph_patch"].raw,
        prompt_set_id="aviation-tmi-event-agents-v1",
        profile_gap_count=len(state["validation"].profile_gaps),
        context_artifacts=state["context_artifacts"],
        formal_layers=state["formal_layers"],
        public_observation_publication=state[
            "public_observation_publication"
        ],
        created_at=datetime(2026, 5, 20, tzinfo=UTC),
    )
    corpus_dir = tmp_path / f"reroute-corpus-{source_id.rsplit(':', 1)[-1]}"
    build_corpus([run_dir], corpus_dir)
    store = CorpusQueryStore(corpus_dir)
    event = store.events[0]
    assert event.reason_status == "formal"
    assert event.reason_value == "WEATHER"
    assert event.facility_ids == []

    document = build_tmi_event_retrieval_documents(store)[0]
    assert document.tmi_type_iri == atm + "ReRouteTMI"
    assert document.facility_ids == ()
    assert document.reason_status == "formal"
    assert document.reason_value == "WEATHER"
    assert "Traffic management measure: Required Reroute." in document.text
    assert (
        "Controlled scope: not represented by a formal facility edge "
        "in the active profile."
        in document.text
    )
