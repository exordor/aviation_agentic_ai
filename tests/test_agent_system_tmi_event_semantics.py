"""Construct-validity contracts for ATMONTO TMI event publication."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusQueryStore,
    build_corpus,
)


ROOT = Path(__file__).resolve().parents[1]
ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"

_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "tmi_event_query_tools_fixture",
    Path(__file__).with_name("test_agent_system_query_tools.py"),
)
assert _FIXTURE_SPEC is not None and _FIXTURE_SPEC.loader is not None
_fixture = importlib.util.module_from_spec(_FIXTURE_SPEC)
_FIXTURE_SPEC.loader.exec_module(_fixture)


def _write_event_run(
    run_dir: Path,
    *,
    event_id: str,
    event_type: str,
) -> None:
    rows = []
    for source_row in _fixture._rows():
        row = dict(source_row)
        row["subject"] = event_id
        row["subject_class"] = event_type
        if row["predicate"] == "rdf:type":
            row["object"] = event_type
            row["object_class"] = event_type
        row["triple_id"] = f"{row['triple_id']}:{run_dir.name}"
        rows.append(row)
    _fixture._write_graph(run_dir, rows)


def test_project_has_no_formal_decision_case_profile() -> None:
    """Reintroducing a project DecisionCase wrapper would invalidate the model."""

    assert not (
        ROOT / "data/ontology/curated/decision_case_core_slice.json"
    ).exists()


@pytest.mark.parametrize(
    ("suffix", "event_type"),
    (
        ("gdp", "atm:GroundDelayProgramTMI"),
        ("gs", "atm:GroundStopTMI"),
        ("reroute", "atm:ReRouteTMI"),
    ),
)
def test_active_atmonto_tmi_event_is_the_corpus_identity(
    tmp_path: Path,
    suffix: str,
    event_type: str,
) -> None:
    """An admitted TMI must not need a synthetic DecisionCase identity."""

    event_id = f"urn:aviation-agentic-ai:event:{suffix}"
    run_dir = tmp_path / f"run-{suffix}"
    _write_event_run(run_dir, event_id=event_id, event_type=event_type)

    corpus_dir = tmp_path / f"corpus-{suffix}"
    manifest = build_corpus([run_dir], corpus_dir)
    store = CorpusQueryStore(corpus_dir)

    assert manifest.manifest_version == "tmi-event-corpus-v3"
    assert manifest.event_count == 1
    assert store.event_ids == (event_id,)
    event = store.get_event(event_id)
    assert event is not None
    assert event.event_id == event_id
    assert event_type.replace("atm:", ATM) in event.event_type_iris
    assert (corpus_dir / "events.jsonl").is_file()
    assert (corpus_dir / "event_facts.jsonl").is_file()
    assert not (corpus_dir / "cases.jsonl").exists()
    assert not (corpus_dir / "case_facts.jsonl").exists()
    assert all(
        "DecisionCase" not in fact.object_value
        and "decision-case-schema" not in fact.subject_iri
        for fact in store.get_event_facts(event_id)
    )


def test_v2_corpus_is_rejected_with_rebuild_instruction(tmp_path: Path) -> None:
    """A v2 corpus must never be silently interpreted or migrated as v3."""

    corpus_dir = tmp_path / "v2"
    corpus_dir.mkdir()
    (corpus_dir / "corpus_manifest.json").write_text(
        json.dumps(
            {
                "manifest_version": "decision-case-corpus-v2",
                "corpus_id": "old",
                "run_count": 0,
                "case_count": 0,
                "fact_count": 0,
                "source_binding_count": 0,
                "source_object_count": 0,
                "artifacts": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="rebuild"):
        CorpusQueryStore(corpus_dir)
