"""Corpus-first public CLI and bounded analysis contracts."""

from __future__ import annotations

import importlib.util
import importlib
import builtins
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from click.testing import CliRunner
from langchain_core.messages import AIMessage
import pytest

import aviation_agentic_ai.cli as top_cli
import aviation_agentic_ai.cli_agent_system as cli_module
from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    SourceFamily,
)
from aviation_agentic_ai.agent_system.corpus_query import (
    CorpusAnalysisStoreAdapter,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusQueryStore,
    build_corpus,
)
from aviation_agentic_ai.agent_system.query_tool_graph import (
    APPLICABILITY_ANALYSIS_QUESTION,
    DECLARED_REASON_QUESTION,
    EPISODE_ANALYSIS_QUESTION,
    FORECAST_CONTEXT_QUESTION,
    HISTORICAL_SIMILARITY_ANALYSIS_QUESTION,
    OBSERVED_WEATHER_CONTEXT_QUESTION,
    OPERATIONAL_SITUATION_ANALYSIS_QUESTION,
    PUBLIC_OUTCOME_QUESTION,
    RECONSTRUCTED_CASE_QUESTION,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn


def _load_fixture(name: str, filename: str) -> Any:
    spec = importlib.util.spec_from_file_location(
        name,
        Path(__file__).with_name(filename),
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_corpus_fixture = _load_fixture(
    "corpus_cli_store_fixture",
    "test_agent_system_corpus_store.py",
)
_query_fixture = _load_fixture(
    "corpus_cli_query_fixture",
    "test_agent_system_query_tool_graph.py",
)
ANALYSIS_EVENT_ID = _corpus_fixture._fixture_module.EVENT_ID


def _minimal_corpus(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run"
    _corpus_fixture._write_run(
        run_dir,
        event_id="urn:event:cli-corpus",
        suffix="cli-corpus",
    )
    corpus_dir = tmp_path / "corpus"
    build_corpus([run_dir], corpus_dir)
    return corpus_dir


def _analysis_corpus(tmp_path: Path) -> Path:
    run_dir = tmp_path / "analysis-run"
    module = _corpus_fixture._fixture_module
    module._write_graph(run_dir)
    module._write_formal_observation_layer(run_dir)
    _query_fixture.EVENT_ID = ANALYSIS_EVENT_ID
    _query_fixture._append_qualifying_weather_relation(
        run_dir,
        family=SourceFamily.METAR,
        logical_time=datetime(2026, 5, 19, 20, 15, tzinfo=UTC),
        raw="METAR KJFK TEST",
    )
    context_path = run_dir / "context_associations.jsonl"
    context_data = context_path.read_bytes()
    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["context_artifacts"]["context_associations"] = {
        "path": context_path.name,
        "count": len(context_data.splitlines()),
        "sha256": hashlib.sha256(context_data).hexdigest(),
        "status": "ok",
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    corpus_dir = tmp_path / "analysis-corpus"
    build_corpus([run_dir], corpus_dir)
    return corpus_dir


class _EvidenceBoundAnalysisModel:
    """Return one statement supported by the actual preflight observation."""

    def invoke(self, messages: list[Any], *, phase: str) -> ToolModelTurn:
        assert phase == "final_answer"
        content = str(messages[-1].content)
        serialized = content.split(
            "PREFLIGHT_REQUIRED_OBSERVATIONS:", 1
        )[1].split("\nSEALED_CASE_ANALYSIS_TASK:", 1)[0]
        observations = json.loads(serialized)
        item = next(
            item
            for observation in observations
            for item in observation["items"]
            if item.get("fact_id") and item.get("source_ids")
        )
        payload = {
            "statements": [
                {
                    "kind": "source_fact",
                    "text": (
                        "The corpus contains a source-qualified operational "
                        "situation."
                    ),
                    "support_fact_ids": [item["fact_id"]],
                    "support_source_ids": [item["source_ids"][0]],
                }
            ],
            "limitations": [],
        }
        raw = json.dumps(payload)
        return ToolModelTurn(
            message=AIMessage(content=raw),
            record=ModelCallRecord(
                agent="decision_case_analysis",
                raw_response=raw,
                prompt_version="decision-case-analysis-v1",
                provider="scripted",
                model="scripted",
            ),
        )


def test_public_agent_system_surface_is_exactly_corpus_first() -> None:
    """Reintroducing a persistent single-case command would reopen dual-track IO."""

    assert set(cli_module.agent_system.commands) == {
        "build-corpus",
        "ask",
        "index-cases",
        "neo4j-export",
        "export-case",
    }
    spec = next(
        row for row in top_cli.TOP_LEVEL_COMMANDS if row["name"] == "agent-system"
    )
    assert spec["subcommands"] == (
        "build-corpus",
        "ask",
        "index-cases",
        "neo4j-export",
        "export-case",
    )


def test_index_cases_cli_reports_persistent_index(
    tmp_path: Path,
    monkeypatch,
) -> None:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    captured: dict[str, object] = {}

    class FakeEncoder:
        model_id = "test/model"

        def __init__(self, model_name: str, *, allow_download: bool) -> None:
            captured["model_name"] = model_name
            captured["allow_download"] = allow_download

    def fake_build(corpus_dir, *, encoder):  # type: ignore[no-untyped-def]
        captured["corpus_dir"] = corpus_dir
        captured["encoder"] = encoder
        return SimpleNamespace(
            document_count=2,
            vector_backend="chromadb",
            collection_name="decision_cases",
            embedding_model_id=encoder.model_id,
            embedding_dimension=4,
        )

    monkeypatch.setattr(
        cli_module,
        "SentenceTransformerCaseEncoder",
        FakeEncoder,
    )
    monkeypatch.setattr(
        cli_module,
        "build_case_retrieval_index",
        fake_build,
    )

    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "index-cases",
            "--corpus-dir",
            str(corpus_dir),
            "--model-name",
            "test/model",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "indexed_cases: 2" in result.output
    assert "vector_backend: chromadb" in result.output
    assert "collection_name: decision_cases" in result.output
    assert "embedding_model: test/model" in result.output
    assert "embedding_dimension: 4" in result.output
    assert captured["allow_download"] is False


def test_index_cases_cli_explains_missing_optional_dependencies(
    tmp_path: Path,
    monkeypatch,
) -> None:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()

    def fail_encoder(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise ImportError("sentence_transformers")

    monkeypatch.setattr(
        cli_module,
        "SentenceTransformerCaseEncoder",
        fail_encoder,
    )

    result = CliRunner().invoke(
        cli_module.agent_system,
        ["index-cases", "--corpus-dir", str(corpus_dir)],
    )

    assert result.exit_code != 0
    assert (
        "Install case retrieval dependencies with "
        "uv sync --extra case-retrieval."
    ) in result.output


def test_index_cases_cli_reports_index_build_failure(
    tmp_path: Path,
    monkeypatch,
) -> None:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()

    class FakeEncoder:
        model_id = "test/model"

        def __init__(self, *_args, **_kwargs) -> None:  # type: ignore[no-untyped-def]
            pass

    def fail_build(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise ValueError("corpus has no accepted cases to index")

    monkeypatch.setattr(
        cli_module,
        "SentenceTransformerCaseEncoder",
        FakeEncoder,
    )
    monkeypatch.setattr(
        cli_module,
        "build_case_retrieval_index",
        fail_build,
    )

    result = CliRunner().invoke(
        cli_module.agent_system,
        ["index-cases", "--corpus-dir", str(corpus_dir)],
    )

    assert result.exit_code != 0
    assert (
        "index-cases BLOCKED: corpus has no accepted cases to index"
        in result.output
    )
    assert "embedding model is not cached" not in result.output


def test_existing_cli_import_does_not_load_case_retrieval_dependencies(
    monkeypatch,
) -> None:
    real_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name in {"chromadb", "sentence_transformers"}:
            raise AssertionError(f"unexpected eager import: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    reloaded = importlib.reload(cli_module)

    assert "build-corpus" in reloaded.agent_system.commands


def test_build_corpus_cli_wires_the_resumable_batch_contract(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Routing via runs-root would bypass cohort preflight and recovery."""

    config_path = tmp_path / "config.yaml"
    config_path.write_text("{}\n", encoding="utf-8")
    output_dir = tmp_path / "corpus"
    config = {"sources": {"atcscc_advisories": "fixture.jsonl"}}
    captured: dict[str, object] = {}

    def fake_batch(config_value, *, output_dir, **kwargs):  # type: ignore[no-untyped-def]
        captured.update(
            config=config_value,
            output_dir=output_dir,
            **kwargs,
        )
        return SimpleNamespace(
            selected_count=2,
            ok_count=1,
            insufficient_count=1,
            blocked_count=0,
            manifest=SimpleNamespace(corpus_id="corpus:test"),
        )

    monkeypatch.setattr(cli_module, "_load_config", lambda path: config)
    monkeypatch.setattr(
        cli_module,
        "build_corpus_batch",
        fake_batch,
        raising=False,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "build-corpus",
            "--config",
            str(config_path),
            "--output-dir",
            str(output_dir),
            "--selection",
            "all",
            "--source-id",
            "2026-05-19:123",
            "--source-id",
            "2026-05-19:138",
            "--allow-live-model",
            "--resume",
        ],
    )

    assert result.exit_code == 0, result.output
    assert captured == {
        "config": config,
        "output_dir": output_dir,
        "selection": "all",
        "source_ids": ("2026-05-19:123", "2026-05-19:138"),
        "allow_live_model": True,
        "resume": True,
    }
    assert "selected: 2" in result.output
    assert "blocked: 0" in result.output
    assert "corpus_id: corpus:test" in result.output


def test_removed_run_options_are_rejected_by_the_public_cli(tmp_path: Path) -> None:
    """Accepting either old option would preserve a second persisted backend."""

    runs_root = tmp_path / "runs"
    runs_root.mkdir()
    build = CliRunner().invoke(
        cli_module.agent_system,
        [
            "build-corpus",
            "--runs-root",
            str(runs_root),
            "--output-dir",
            str(tmp_path / "corpus"),
        ],
    )
    ask = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(runs_root),
            "--question",
            "What traffic management measure was published?",
        ],
    )

    assert "No such option '--runs-root'" in build.output
    assert "No such option '--run-dir'" in ask.output


@pytest.mark.parametrize(
    ("corruption", "expected_error"),
    [
        ("missing_manifest", "published decision-case-corpus-v2 manifest"),
        ("registered_path", "missing Neo4j projection artifact"),
        ("registered_count", "row-count mismatch"),
        ("registered_checksum", "checksum mismatch"),
    ],
)
def test_neo4j_export_validates_published_projection_before_loading(
    tmp_path: Path,
    monkeypatch,
    corruption: str,
    expected_error: str,
) -> None:
    corpus_dir = _minimal_corpus(tmp_path)
    manifest_path = corpus_dir / "corpus_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if corruption == "missing_manifest":
        manifest_path.unlink()
    elif corruption == "registered_path":
        manifest["artifacts"]["neo4j_nodes"]["path"] = "missing-nodes.jsonl"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    elif corruption == "registered_count":
        manifest["artifacts"]["neo4j_relationships"]["count"] += 1
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    else:
        nodes_path = corpus_dir / "neo4j_nodes.jsonl"
        nodes_path.write_text(
            nodes_path.read_text(encoding="utf-8").rstrip("\n") + " \n",
            encoding="utf-8",
        )

    def forbidden_loader(**kwargs):
        raise AssertionError(f"Neo4j loader was called with {kwargs}")

    monkeypatch.setattr(
        cli_module,
        "load_validated_facts_neo4j",
        forbidden_loader,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "neo4j-export",
            "--corpus-dir",
            str(corpus_dir),
            "--uri",
            "bolt://example.invalid",
            "--username",
            "neo4j",
            "--password",
            "password",
        ],
    )

    assert result.exit_code != 0
    assert expected_error in result.output
    assert not (corpus_dir / "neo4j_load.json").exists()


def test_registered_analysis_requires_explicit_live_authorization(
    tmp_path: Path,
) -> None:
    """A registered model-bound analysis may not run on an implicit grant."""

    corpus_dir = _analysis_corpus(tmp_path)
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--corpus-dir",
            str(corpus_dir),
            "--event-id",
            ANALYSIS_EVENT_ID,
            "--question",
            OPERATIONAL_SITUATION_ANALYSIS_QUESTION,
        ],
    )

    assert result.exit_code != 0
    assert "requires --allow-live-model" in result.output
    assert not (corpus_dir / "analysis").exists()


def test_analysis_adapter_is_scoped_to_the_selected_case_source_version(
    tmp_path: Path,
) -> None:
    """A shared logical source ID must not leak another case's artifact."""

    event_a = "urn:event:analysis-a"
    event_b = "urn:event:analysis-b"
    run_a = tmp_path / "run-a"
    run_b = tmp_path / "run-b"
    _corpus_fixture._write_run(run_a, event_id=event_a, suffix="a")
    _corpus_fixture._write_run(run_b, event_id=event_b, suffix="b")
    revised_content = (
        _corpus_fixture._fixture_module.ADVISORY_CONTENT
        + "REVISION: CASE B\n"
    )
    revised_sha256 = _corpus_fixture._set_snapshot_content(
        run_b,
        revised_content,
    )
    corpus_dir = tmp_path / "versioned-corpus"
    build_corpus([run_a, run_b], corpus_dir)
    store = CorpusQueryStore(corpus_dir)

    adapter_a = CorpusAnalysisStoreAdapter(store, event_id=event_a)
    adapter_b = CorpusAnalysisStoreAdapter(store, event_id=event_b)
    source_id = _corpus_fixture._fixture_module.SOURCE_ID

    assert adapter_a.event_ids == [event_a]
    assert adapter_b.event_ids == [event_b]
    assert adapter_a.source_snapshots.get(source_id).content_sha256 != (
        revised_sha256
    )
    assert adapter_b.source_snapshots.get(source_id).content_sha256 == (
        revised_sha256
    )


def test_authorized_analysis_uses_corpus_evidence_and_bounded_agent(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Discarding the live flag or reopening a run bundle breaks this route."""

    corpus_dir = _analysis_corpus(tmp_path)

    def model_factory(*, tools, role):  # type: ignore[no-untyped-def]
        assert [tool.name for tool in tools] == ["execute_bound_query_step"]
        assert role == "decision_case_analysis"
        return _EvidenceBoundAnalysisModel()

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        model_factory,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--corpus-dir",
            str(corpus_dir),
            "--event-id",
            ANALYSIS_EVENT_ID,
            "--question",
            OPERATIONAL_SITUATION_ANALYSIS_QUESTION,
            "--allow-live-model",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "status: ok" in result.output
    assert "model_calls: 1" in result.output
    artifact_line = next(
        line
        for line in result.output.splitlines()
        if line.startswith("analysis_artifact_dir: ")
    )
    assert Path(artifact_line.removeprefix("analysis_artifact_dir: ")).parent == (
        corpus_dir / "analysis"
    )


def test_zero_model_registered_analyses_still_use_corpus_bound_plans(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Episode and applicability gates must not fall through as unregistered."""

    corpus_dir = _analysis_corpus(tmp_path)

    def forbidden_factory(*args, **kwargs):
        raise AssertionError("preflight-only analysis constructed a model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_factory,
    )
    expected = (
        (EPISODE_ANALYSIS_QUESTION, "status: ok", "tool_calls: 1"),
        (
            APPLICABILITY_ANALYSIS_QUESTION,
            "status: insufficient",
            "tool_calls: 2",
        ),
    )
    for question, status, tool_calls in expected:
        result = CliRunner().invoke(
            cli_module.agent_system,
            [
                "ask",
                "--corpus-dir",
                str(corpus_dir),
                "--event-id",
                ANALYSIS_EVENT_ID,
                "--question",
                question,
                "--allow-live-model",
            ],
        )

        assert result.exit_code == 0, result.output
        assert status in result.output
        assert tool_calls in result.output
        assert "model_calls: 0" in result.output
        assert "analysis_artifact_dir: " in result.output


def test_similarity_remains_an_explicit_zero_model_s3_gate(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Storage alone must not activate ranking or a provider."""

    corpus_dir = _minimal_corpus(tmp_path)

    def forbidden_factory(*args, **kwargs):
        raise AssertionError("similarity gate constructed a model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_factory,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--corpus-dir",
            str(corpus_dir),
            "--question",
            HISTORICAL_SIMILARITY_ANALYSIS_QUESTION,
            "--allow-live-model",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "status: insufficient" in result.output
    assert "S3" in result.output
    assert "comparison cohort and ranking contract" in result.output
    assert "model_calls: 0" in result.output


def test_corpus_cli_preserves_all_three_declared_reason_states(
    tmp_path: Path,
) -> None:
    """Weather and BTS context must never fill a missing advisory reason."""

    ground_stop = tmp_path / "ground-stop"
    gdp = tmp_path / "gdp"
    cancellation = tmp_path / "cancellation"
    _corpus_fixture._write_run(
        ground_stop,
        event_id="urn:event:ground-stop",
        suffix="ground-stop",
    )
    _corpus_fixture._write_reason_profile_gap(
        ground_stop,
        event_id="urn:event:ground-stop",
    )
    _corpus_fixture._write_run(
        gdp,
        event_id="urn:event:gdp",
        suffix="gdp",
        event_type="atm:GroundDelayProgramTMI",
        formal_reason="weather",
    )
    _corpus_fixture._write_run(
        cancellation,
        event_id="urn:event:cancellation",
        suffix="cancellation",
        event_type="atm:GroundDelayProgramTMI",
    )
    corpus_dir = tmp_path / "reason-corpus"
    build_corpus([ground_stop, gdp, cancellation], corpus_dir)

    outputs = {}
    for name in ("ground-stop", "gdp", "cancellation"):
        result = CliRunner().invoke(
            cli_module.agent_system,
            [
                "ask",
                "--corpus-dir",
                str(corpus_dir),
                "--event-id",
                f"urn:event:{name}",
                "--question",
                DECLARED_REASON_QUESTION,
            ],
        )
        assert result.exit_code == 0, result.output
        outputs[name] = result.output

    assert "profile-gap metadata" in outputs["ground-stop"]
    assert "IMPACTING CONDITION: WEATHER / THUNDERSTORMS" in outputs["ground-stop"]
    assert "status: ok" in outputs["gdp"]
    assert "records weather" in outputs["gdp"]
    assert "status: insufficient" in outputs["cancellation"]
    assert "No declared reason" in outputs["cancellation"]
    assert all("model_calls: 0" in output for output in outputs.values())


def test_four_corpus_question_families_need_no_run_directory_or_model(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """All deterministic case families must read only the normalized corpus."""

    corpus_dir = _analysis_corpus(tmp_path)

    def forbidden_factory(*args, **kwargs):
        raise AssertionError("deterministic corpus question constructed a model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_factory,
    )
    for question in (
        FORECAST_CONTEXT_QUESTION,
        OBSERVED_WEATHER_CONTEXT_QUESTION,
        PUBLIC_OUTCOME_QUESTION,
        RECONSTRUCTED_CASE_QUESTION,
    ):
        result = CliRunner().invoke(
            cli_module.agent_system,
            [
                "ask",
                "--corpus-dir",
                str(corpus_dir),
                "--event-id",
                ANALYSIS_EVENT_ID,
                "--question",
                question,
            ],
        )
        assert result.exit_code == 0, result.output
        assert "status: ok" in result.output, question
        assert "model_calls: 0" in result.output
