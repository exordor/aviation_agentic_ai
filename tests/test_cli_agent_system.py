"""CLI contracts for the active native tool-using Query Agent."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from langchain_core.messages import AIMessage

import aviation_agentic_ai.cli_agent_system as cli_module
from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    ModelToolCall,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.query_tool_graph import (
    DECLARED_REASON_QUESTION,
    REGISTERED_COMPETENCY_QUESTION,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn

EVENT_ID = "urn:aviation-agentic-ai:event:cli-test"
SOURCE_ID = "2026-05-19:123"


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
            "source_document": SOURCE_ID,
        }
        for fact_id, predicate, value, object_class in values
    ]
    (run_dir / "kg.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


class _SuccessfulModel:
    def __init__(self) -> None:
        self.attempt = 0

    def invoke(self, messages, *, phase):
        self.attempt += 1
        if phase == "select_tool":
            message = AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "call:cli",
                        "name": "get_event_facts",
                        "args": {
                            "event_id": EVENT_ID,
                            "predicates": [
                                "rdf:type",
                                "atm:controlledNASelement",
                                "atm:effectiveStartTime",
                                "atm:effectiveEndTime",
                            ],
                        },
                        "type": "tool_call",
                    }
                ],
            )
        else:
            message = AIMessage(
                content=(
                    "ANSWER\n"
                    "MEASURE: Ground Stop (GS)\n"
                    "AIRPORT: KJFK\n"
                    "START: 2026-05-19T21:00:00Z\n"
                    "END: 2026-05-19T22:45:00Z\n"
                    f"SOURCES\n- {SOURCE_ID}"
                )
            )
        return ToolModelTurn(
            message=message,
            record=ModelCallRecord(
                agent="query",
                raw_response=str(message.content or "") if not message.tool_calls else "",
                attempt=self.attempt,
                tool_calls=[
                    ModelToolCall(
                        call_id=str(call["id"]),
                        name=str(call["name"]),
                        arguments=dict(call["args"]),
                    )
                    for call in message.tool_calls
                ],
            ),
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


def test_supported_cli_question_requires_live_authorization(tmp_path):
    _write_graph(tmp_path)
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
    assert result.exit_code != 0
    assert "requires --allow-live-model" in result.output


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


def test_supported_cli_question_runs_native_tool_loop(tmp_path, monkeypatch):
    _write_graph(tmp_path)
    model = _SuccessfulModel()
    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        lambda *, tools: model,
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
    assert "model_calls: 2" in result.output
    assert "tool_calls: 1" in result.output


def test_ingest_wires_deterministic_context_loaders_without_extra_model_calls(
    tmp_path,
    monkeypatch,
):
    captured = {}
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
    monkeypatch.setattr(cli_module, "load_advisory_source", lambda config, source_id: advisory)
    monkeypatch.setattr(cli_module, "facility_candidates", lambda config: [])
    monkeypatch.setattr(cli_module, "term_candidates", lambda config: [])
    monkeypatch.setattr(cli_module, "load_weather_sources", lambda config: [weather])
    monkeypatch.setattr(cli_module, "load_bts_context_source", lambda config: (bts, []))
    monkeypatch.setattr(cli_module, "new_run_directory", lambda root, source_id: tmp_path)
    monkeypatch.setattr(cli_module, "make_live_model_invoker", lambda **kwargs: object())
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
            "kg_result": None,
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
    assert captured["ctx"].weather_sources == [weather]
    assert captured["ctx"].bts_source == bts
    assert captured["ctx"].weather_failure_reason == ""
    assert captured["ctx"].bts_failure_reason == ""


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
    monkeypatch.setattr(cli_module, "facility_candidates", lambda config: [])
    monkeypatch.setattr(cli_module, "term_candidates", lambda config: [])
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
    monkeypatch.setattr(cli_module, "new_run_directory", lambda root, source_id: tmp_path)
    monkeypatch.setattr(cli_module, "make_live_model_invoker", lambda **kwargs: object())
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
            "kg_result": None,
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
    monkeypatch.setattr(cli_module, "facility_candidates", lambda config: [])
    monkeypatch.setattr(cli_module, "term_candidates", lambda config: [])
    monkeypatch.setattr(
        cli_module,
        "load_bts_context_source",
        lambda config: (_ for _ in ()).throw(ValueError("BTS unavailable")),
    )
    monkeypatch.setattr(cli_module, "new_run_directory", lambda root, source_id: tmp_path)
    monkeypatch.setattr(cli_module, "make_live_model_invoker", lambda **kwargs: object())
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
            "kg_result": None,
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
