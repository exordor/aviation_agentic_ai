"""CLI contracts for deterministic reads and bounded Agent execution."""

from __future__ import annotations

import json
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from langchain_core.messages import AIMessage

import aviation_agentic_ai.cli_agent_system as cli_module
from aviation_agentic_ai.agent_system.authority_evidence import AuthorityBuildStatus
from aviation_agentic_ai.agent_system.contracts import (
    BTSManifestBinding,
    ModelCallRecord,
    ModelToolCall,
    SourceFamily,
    SourceRecord,
    SourceSnapshot,
    SourceSnapshotRegistry,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
from aviation_agentic_ai.agent_system.query_tool_graph import (
    DECLARED_REASON_QUESTION,
    FORECAST_CONTEXT_QUESTION,
    HISTORICAL_SIMILARITY_ANALYSIS_QUESTION,
    OBSERVED_WEATHER_CONTEXT_QUESTION,
    OPERATIONAL_SITUATION_ANALYSIS_QUESTION,
    PUBLIC_OUTCOME_QUESTION,
    RECONSTRUCTED_CASE_QUESTION,
    REGISTERED_COMPETENCY_QUESTION,
)
from aviation_agentic_ai.agent_system.runtime import RunBinding
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)

EVENT_ID = "urn:aviation-agentic-ai:event:cli-test"
SOURCE_ID = "2026-05-19:123"
RUN_STARTED_AT = datetime(2026, 5, 19, 20, 30, tzinfo=UTC)
ADVISORY_CONTENT = "SIGNATURE:\n26/05/19 20:30\nGROUND STOP\n"


def _run_binding(run_dir: Path) -> RunBinding:
    return RunBinding(
        run_id=run_dir.name,
        run_dir=run_dir,
        run_started_at=RUN_STARTED_AT,
    )


def _authority_catalog(
    *,
    facility_status: AuthorityBuildStatus = AuthorityBuildStatus.OK,
    facility_entities: tuple[object, ...] = (),
    terminology_status: AuthorityBuildStatus = AuthorityBuildStatus.OK,
    registry_terms: tuple[object, ...] = (),
):
    return SimpleNamespace(
        facility=SimpleNamespace(
            status=facility_status,
            entities=facility_entities,
        ),
        terminology=SimpleNamespace(
            status=terminology_status,
            registry_terms=registry_terms,
        ),
    )


def _write_graph(run_dir: Path) -> None:
    values = [
        ("fact:type", "rdf:type", "atm:GroundStopTMI", "atm:GroundStopTMI"),
        (
            "fact:facility",
            "atm:controlledNASelement",
            "urn:aviation-agentic-ai:facility:airport:KJFK",
            "nas:Airport",
        ),
        (
            "fact:start",
            "atm:effectiveStartTime",
            "2026-05-19T21:00:00Z",
            "",
        ),
        (
            "fact:end",
            "atm:effectiveEndTime",
            "2026-05-19T22:45:00Z",
            "",
        ),
    ]
    rows = [
        {
            "triple_id": fact_id,
            "subject": EVENT_ID,
            "predicate": predicate,
            "object": value,
            "subject_class": "atm:GroundStopTMI",
            "object_class": object_class,
            "object_kind": "iri" if object_class else "literal",
            "source_document": SOURCE_ID,
            "evidence_text": "GROUND STOP",
            "datatype_iri": (
                "http://www.w3.org/2001/XMLSchema#dateTime"
                if predicate
                in {
                    "atm:effectiveStartTime",
                    "atm:effectiveEndTime",
                }
                else ""
            ),
        }
        for fact_id, predicate, value, object_class in values
    ]
    profile_registry = load_validation_profile_registry(
        decision_guide=load_schema_guide()
    )
    profiles = {
        profile.ref.layer: profile.ref
        for profile in profile_registry.profiles
    }
    decision_profile = profiles["decision"]
    snapshot = SourceSnapshot(
        source_id=SOURCE_ID,
        family=SourceFamily.ATCSCC_ADVISORY,
        content=ADVISORY_CONTENT,
        content_sha256=hashlib.sha256(
            ADVISORY_CONTENT.encode()
        ).hexdigest(),
        snapshot_timestamp=RUN_STARTED_AT.isoformat(),
    )
    registry_path = SourceSnapshotRegistry(
        snapshots=(snapshot,)
    ).write_jsonl(run_dir)
    for row in rows:
        row.update(
            {
                "profile_id": decision_profile.profile_id,
                "profile_checksum": decision_profile.profile_checksum,
                "validation_layer": "decision",
                "evidence_mode": "source_text",
                "evidence_ref": row["triple_id"],
                "source_ids": [SOURCE_ID],
                "source_snapshot_checksums": {
                    SOURCE_ID: snapshot.content_sha256,
                },
            }
        )
    (run_dir / "kg.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )
    context_artifacts: dict[str, dict[str, object]] = {}
    registry_data = registry_path.read_bytes()
    context_artifacts["source_snapshots"] = {
        "path": "source_snapshots.jsonl",
        "count": 1,
        "sha256": hashlib.sha256(registry_data).hexdigest(),
        "status": "ok",
    }
    trace_rows = [
        json.dumps(
            {
                "fact_id": row["triple_id"],
                "graph_patch_line": "",
                "source_id": SOURCE_ID,
                "evidence_text": row["evidence_text"],
                "evidence_agent_role": "advisory",
                "source_snapshot_sha256": snapshot.content_sha256,
            }
        )
        for row in rows
    ]
    trace_path = run_dir / "fact_trace.jsonl"
    trace_data = "".join(row + "\n" for row in trace_rows).encode("utf-8")
    trace_path.write_bytes(trace_data)
    context_artifacts["fact_trace"] = {
        "path": trace_path.name,
        "count": len(trace_rows),
        "sha256": hashlib.sha256(trace_data).hexdigest(),
        "status": "ok",
    }
    for key, filename in (
        ("context_associations", "context_associations.jsonl"),
        ("outcome_summaries", "outcome_summaries.jsonl"),
        ("weather_fact_trace", "weather_fact_trace.jsonl"),
        ("observation_derivations", "observation_derivations.jsonl"),
        ("observation_fact_trace", "observation_fact_trace.jsonl"),
        ("reconstruction_trace", "reconstruction_trace.json"),
    ):
        path = run_dir / filename
        path.write_text("", encoding="utf-8")
        context_artifacts[key] = {
            "path": filename,
            "count": 0,
            "sha256": hashlib.sha256(b"").hexdigest(),
            "status": "insufficient",
        }
    profile_gap_path = run_dir / "profile_gaps.jsonl"
    profile_gap_path.write_text("", encoding="utf-8")
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "manifest_version": "decision-case-run-v1",
                "run_id": run_dir.name,
                "source_id": SOURCE_ID,
                "materialization": {
                    "materialized": True,
                    "fact_count": len(rows),
                    "profile_refs": [
                        decision_profile.model_dump(mode="json")
                    ],
                    "layer_fact_counts": {"decision": len(rows)},
                    "artifacts": {
                        "kg_jsonl": str(run_dir / "kg.jsonl"),
                    },
                },
                "formal_layers": {
                    layer: {
                        "status": (
                            "ok" if layer == "decision" else "insufficient"
                        ),
                        "profile_id": profile.profile_id,
                        "profile_checksum": profile.profile_checksum,
                        "formal_fact_count": (
                            len(rows) if layer == "decision" else 0
                        ),
                    }
                    for layer, profile in profiles.items()
                },
                "context_artifacts": context_artifacts,
                "profile_gaps": {
                    "path": profile_gap_path.name,
                    "count": 0,
                    "sha256": hashlib.sha256(b"").hexdigest(),
                    "status": "ok",
                },
            }
        ),
        encoding="utf-8",
    )


def test_unsupported_cli_question_needs_no_live_authorization(tmp_path, monkeypatch):
    _write_graph(tmp_path)

    def forbidden_factory(*args, **kwargs):
        raise AssertionError("unsupported question constructed a live model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_factory,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            "What is the runway surface at LAX?",
        ],
    )
    assert result.exit_code == 0
    assert "status: insufficient" in result.output
    assert "model_calls: 0" in result.output
    assert "tool_calls: 0" in result.output


def test_combined_record_cli_question_is_zero_call_without_authorization(
    tmp_path,
    monkeypatch,
):
    _write_graph(tmp_path)

    def forbidden_live_model(*args, **kwargs):
        raise AssertionError("combined-record query constructed a live model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_live_model,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            REGISTERED_COMPETENCY_QUESTION,
        ],
    )
    assert result.exit_code == 0
    assert "status: ok" in result.output
    assert "model_calls: 0" in result.output


def test_missing_reason_question_needs_no_live_authorization(
    tmp_path,
    monkeypatch,
):
    _write_graph(tmp_path)

    def forbidden_factory(*args, **kwargs):
        raise AssertionError("missing reason constructed a live model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_factory,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            DECLARED_REASON_QUESTION,
        ],
    )
    assert result.exit_code == 0
    assert "status: insufficient" in result.output
    assert "model_calls: 0" in result.output


@pytest.mark.parametrize(
    "question",
    [
        FORECAST_CONTEXT_QUESTION,
        OBSERVED_WEATHER_CONTEXT_QUESTION,
        PUBLIC_OUTCOME_QUESTION,
        RECONSTRUCTED_CASE_QUESTION,
    ],
)
def test_context_questions_need_no_live_authorization(
    tmp_path,
    monkeypatch,
    question,
):
    _write_graph(tmp_path)

    def forbidden_factory(*args, **kwargs):
        raise AssertionError("deterministic context question constructed a live model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_factory,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            question,
        ],
    )

    assert result.exit_code == 0
    assert "status: insufficient" in result.output
    assert "model_calls: 0" in result.output


def test_combined_record_remains_zero_call_when_live_flag_is_present(
    tmp_path,
    monkeypatch,
):
    _write_graph(tmp_path)

    def forbidden_live_model(*args, **kwargs):
        raise AssertionError("combined-record query constructed a live model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_live_model,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            REGISTERED_COMPETENCY_QUESTION,
            "--allow-live-model",
        ],
    )
    assert result.exit_code == 0
    assert "status: ok" in result.output
    assert f"sources: {SOURCE_ID}" in result.output
    assert "graph_facts_seen: 4" in result.output
    assert "model_calls: 0" in result.output
    assert "tool_calls: 1" in result.output
    assert "analysis_artifact_dir:" not in result.output


def test_analysis_cli_requires_explicit_live_authorization(tmp_path, monkeypatch):
    """An exact model-bound analysis question must not construct a provider by default."""

    _write_graph(tmp_path)

    def forbidden_live_model(*args, **kwargs):
        raise AssertionError("unauthorized analysis constructed a live model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_live_model,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            OPERATIONAL_SITUATION_ANALYSIS_QUESTION,
        ],
    )

    assert result.exit_code != 0
    assert "requires --allow-live-model" in result.output
    assert not (tmp_path / "analysis").exists()


def test_similarity_cli_is_zero_call_without_authorization(tmp_path, monkeypatch):
    """The deterministic corpus gate must remain usable without credentials."""

    _write_graph(tmp_path)

    def forbidden_live_model(*args, **kwargs):
        raise AssertionError("similarity corpus gate constructed a live model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_live_model,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            HISTORICAL_SIMILARITY_ANALYSIS_QUESTION,
        ],
    )

    assert result.exit_code == 0
    assert "status: insufficient" in result.output
    assert "model_calls: 0" in result.output
    assert "analysis_artifact_dir:" not in result.output


def test_authorized_analysis_cli_reports_only_its_artifact_directory(
    tmp_path,
    monkeypatch,
):
    """Omitting the analysis path would make the sealed result undiscoverable."""

    _write_graph(tmp_path)
    call = {
        "id": "call:analysis:cli",
        "name": "execute_bound_query_step",
        "args": {"step_id": "step:operational_situation:1"},
        "type": "tool_call",
    }

    class OneTurnAnalysisModel:
        def invoke(self, messages, *, phase):
            del messages
            assert phase == "select_tool"
            return ToolModelTurn(
                message=AIMessage(content="", tool_calls=[call]),
                record=ModelCallRecord(
                    agent="decision_case_analysis",
                    raw_response="",
                    prompt_version="decision-case-analysis-v1",
                    provider="scripted",
                    model="scripted",
                    tool_calls=[
                        ModelToolCall(
                            call_id=call["id"],
                            name=call["name"],
                            arguments=call["args"],
                        )
                    ],
                ),
            )

    def scripted_model_factory(*, tools, role):
        assert [tool.name for tool in tools] == ["execute_bound_query_step"]
        assert role == "decision_case_analysis"
        return OneTurnAnalysisModel()

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        scripted_model_factory,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            OPERATIONAL_SITUATION_ANALYSIS_QUESTION,
            "--allow-live-model",
        ],
    )

    assert result.exit_code == 0
    assert "status: insufficient" in result.output
    assert "model_calls: 1" in result.output
    artifact_line = next(
        line
        for line in result.output.splitlines()
        if line.startswith("analysis_artifact_dir: ")
    )
    assert Path(artifact_line.removeprefix("analysis_artifact_dir: ")).is_dir()


def test_cli_preserves_domain_isolation_when_one_authority_file_is_missing(
    tmp_path,
    monkeypatch,
):
    captured = {}
    tool_factory_calls = []
    authority_load_calls = []
    advisory = SourceRecord(
        source_id=SOURCE_ID,
        family=SourceFamily.ATCSCC_ADVISORY,
        content="SIGNATURE:\n26/05/19 21:38\n",
    )
    weather = SourceRecord(
        source_id="weather-source:metar:KJFK:test",
        family=SourceFamily.METAR,
        content='{"icaoId":"KJFK","rawOb":"METAR KJFK","reportTime":"2026-05-19T21:30:00Z"}',
    )
    bts = SourceRecord(
        source_id="bts_on_time:2026-05:nyc",
        family=SourceFamily.BTS_ON_TIME,
        content="{}\n",
    )
    term_candidate = object()
    authority_catalog = _authority_catalog(
        facility_status=AuthorityBuildStatus.BLOCKED,
        registry_terms=(term_candidate,),
    )
    monkeypatch.setattr(cli_module, "load_advisory_source", lambda config, source_id: advisory)
    monkeypatch.setattr(
        cli_module,
        "facility_candidates",
        lambda config: (_ for _ in ()).throw(
            AssertionError("legacy facility loader must not run")
        ),
        raising=False,
    )
    monkeypatch.setattr(
        cli_module,
        "term_candidates",
        lambda config: (_ for _ in ()).throw(
            AssertionError("legacy terminology loader must not run")
        ),
        raising=False,
    )
    monkeypatch.setattr(cli_module, "load_weather_sources", lambda config: [weather])
    monkeypatch.setattr(
        cli_module,
        "load_bts_context_source",
        lambda config: (
            bts,
            [],
            BTSManifestBinding(
                source_id=bts.source_id,
                archive_sha256="a" * 64,
                normalized_snapshot_sha256="b" * 64,
            ),
        ),
    )
    monkeypatch.setattr(
        cli_module,
        "create_run_binding",
        lambda root, source_id: _run_binding(tmp_path),
    )
    monkeypatch.setattr(
        cli_module,
        "load_authority_catalog",
        lambda *args, **kwargs: authority_load_calls.append((args, kwargs))
        or authority_catalog,
        raising=False,
    )
    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        lambda **kwargs: tool_factory_calls.append(kwargs) or object(),
    )

    def fake_run(ctx):
        captured["ctx"] = ctx
        return {
            "model_calls": [],
            "materialization": None,
            "validation": None,
            "assembly_graph_patch": None,
            "context_artifacts": {},
            "formal_layers": {
                "decision": {
                    "status": "ok",
                    "profile_id": "decision-profile",
                    "profile_checksum": "d" * 64,
                    "formal_fact_count": 4,
                }
            },
            "public_observation_publication": {
                "status": "insufficient",
            },
        }

    monkeypatch.setattr(cli_module, "run_ingest", fake_run)
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ingest",
            "--source-id",
            SOURCE_ID,
            "--config",
            "configs/cross_source_v1.yaml",
            "--allow-live-model",
        ],
    )

    assert result.exit_code == 0, result.output
    assert captured["ctx"].weather_sources == [weather]
    assert captured["ctx"].bts_source == bts
    assert captured["ctx"].bts_manifest_binding is not None
    assert captured["ctx"].weather_failure_reason == ""
    assert captured["ctx"].bts_failure_reason == ""
    assert captured["ctx"].authority_catalog is authority_catalog
    assert captured["ctx"].facility_candidates == []
    assert captured["ctx"].term_candidates == [term_candidate]
    assert captured["ctx"].authority_catalog.facility.status is AuthorityBuildStatus.BLOCKED
    assert captured["ctx"].authority_catalog.terminology.status is AuthorityBuildStatus.OK
    assert callable(captured["ctx"].semantic_resolution_tool_model_factory)
    assert callable(captured["ctx"].case_assembly_model_factory)
    assert tool_factory_calls == []
    captured["ctx"].semantic_resolution_tool_model_factory([])
    captured["ctx"].case_assembly_model_factory([])
    assert [call["role"] for call in tool_factory_calls] == [
        "semantic_resolution",
        "decision_case_assembly",
    ]
    assert len(authority_load_calls) == 1
    assert authority_load_calls[0][1]["created_at"] == RUN_STARTED_AT
    assert captured["ctx"].run_started_at == RUN_STARTED_AT
    manifest = json.loads((tmp_path / "run_manifest.json").read_text())
    assert manifest["created_at"] == RUN_STARTED_AT.isoformat()
    assert manifest["formal_layers"]["decision"]["formal_fact_count"] == 4
    assert manifest["public_observation_publication"] == {
        "status": "insufficient"
    }


def test_ingest_records_optional_loader_failures_for_the_context_layer(
    tmp_path,
    monkeypatch,
):
    captured = {}
    advisory = SourceRecord(
        source_id=SOURCE_ID,
        family=SourceFamily.ATCSCC_ADVISORY,
        content="SIGNATURE:\n26/05/19 21:38\n",
    )
    monkeypatch.setattr(cli_module, "load_advisory_source", lambda config, source_id: advisory)
    monkeypatch.setattr(
        cli_module,
        "load_weather_sources",
        lambda config: (_ for _ in ()).throw(ValueError("weather checksum mismatch")),
    )
    monkeypatch.setattr(
        cli_module,
        "load_bts_context_source",
        lambda config: (_ for _ in ()).throw(ValueError("BTS checksum mismatch")),
    )
    monkeypatch.setattr(
        cli_module,
        "create_run_binding",
        lambda root, source_id: _run_binding(tmp_path),
    )
    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        lambda **kwargs: object(),
    )

    def fake_run(ctx):
        captured["ctx"] = ctx
        return {
            "model_calls": [],
            "materialization": None,
            "validation": None,
            "assembly_graph_patch": None,
            "context_artifacts": {},
        }

    monkeypatch.setattr(cli_module, "run_ingest", fake_run)
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ingest",
            "--source-id",
            SOURCE_ID,
            "--config",
            "configs/cross_source_v1.yaml",
            "--allow-live-model",
        ],
    )

    assert result.exit_code == 0, result.output
    assert captured["ctx"].weather_sources == []
    assert captured["ctx"].bts_source is None
    assert captured["ctx"].weather_failure_reason == "weather checksum mismatch"
    assert captured["ctx"].bts_failure_reason == "BTS checksum mismatch"


def test_ingest_provider_limit_counts_failed_attempts(tmp_path, monkeypatch):
    advisory = SourceRecord(
        source_id=SOURCE_ID,
        family=SourceFamily.ATCSCC_ADVISORY,
        content="SIGNATURE:\n26/05/19 21:38\n",
    )
    failed_attempts = [
        ModelCallRecord(
            agent="semantic_resolution",
            raw_response="",
            attempt=attempt,
            error="TimeoutError: upstream unavailable",
        )
        for attempt in (1, 2)
    ]
    monkeypatch.setattr(cli_module, "MAX_PROVIDER_CALLS", 1)
    monkeypatch.setattr(
        cli_module,
        "load_advisory_source",
        lambda config, source_id: advisory,
    )
    monkeypatch.setattr(cli_module, "load_weather_sources", lambda config: [])
    monkeypatch.setattr(
        cli_module,
        "load_bts_context_source",
        lambda config: (None, [], None),
    )
    monkeypatch.setattr(
        cli_module,
        "create_run_binding",
        lambda root, source_id: _run_binding(tmp_path),
    )
    monkeypatch.setattr(
        cli_module,
        "load_authority_catalog",
        lambda *args, **kwargs: _authority_catalog(),
    )
    monkeypatch.setattr(
        cli_module,
        "run_ingest",
        lambda ctx: {
            "model_calls": failed_attempts,
            "materialization": None,
            "validation": None,
            "assembly_graph_patch": None,
            "context_artifacts": {},
        },
    )

    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ingest",
            "--source-id",
            SOURCE_ID,
            "--config",
            "configs/cross_source_v1.yaml",
            "--allow-live-model",
        ],
    )

    assert result.exit_code != 0
    assert "provider calls exceeded hard maximum 1" in result.output
    assert not (tmp_path / "run_manifest.json").exists()


def test_ingest_treats_missing_legacy_weather_config_as_an_optional_layer_failure(
    tmp_path,
    monkeypatch,
):
    captured = {}
    advisory = SourceRecord(
        source_id=SOURCE_ID,
        family=SourceFamily.ATCSCC_ADVISORY,
        content="SIGNATURE:\n26/05/19 21:38\n",
    )
    legacy_config = {
        "sources": {
            "atcscc_advisories": "data/sources/atcscc_advisories.jsonl",
        },
        "paths": {"agent_system_runs_root": str(tmp_path)},
    }
    config_path = tmp_path / "legacy.yaml"
    config_path.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(cli_module, "load_yaml", lambda path: legacy_config)
    monkeypatch.setattr(cli_module, "load_advisory_source", lambda config, source_id: advisory)
    monkeypatch.setattr(
        cli_module,
        "load_bts_context_source",
        lambda config: (_ for _ in ()).throw(ValueError("BTS unavailable")),
    )
    monkeypatch.setattr(
        cli_module,
        "create_run_binding",
        lambda root, source_id: _run_binding(tmp_path),
    )
    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        lambda **kwargs: object(),
    )

    def fake_run(ctx):
        captured["ctx"] = ctx
        return {
            "model_calls": [],
            "materialization": None,
            "validation": None,
            "assembly_graph_patch": None,
            "context_artifacts": {},
        }

    monkeypatch.setattr(cli_module, "run_ingest", fake_run)
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ingest",
            "--source-id",
            SOURCE_ID,
            "--config",
            str(config_path),
            "--allow-live-model",
        ],
    )

    assert result.exit_code == 0, result.output
    assert captured["ctx"].weather_sources == []
    assert (
        captured["ctx"].weather_failure_reason
        == "optional weather source paths are not configured: metar, taf"
    )
