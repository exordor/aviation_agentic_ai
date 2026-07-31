"""Public-surface tests for the ingestion-first Agent-system CLI."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner

import aviation_agentic_ai.cli as top_cli
import aviation_agentic_ai.cli_agent_system as cli_module
from aviation_agentic_ai.agent_system.contracts import QueryToolOutcome


class _Store:
    root = Path("/tmp/test-store")
    dataset_id = "dataset:test"

    def get_knowledge_revision(self) -> int:
        return 7

    def close(self) -> None:
        pass


def test_public_agent_system_surface_is_ingestion_first() -> None:
    assert set(cli_module.agent_system.commands) == {
        "ingest",
        "reindex",
        "ask",
        "neo4j-export",
        "export-event",
    }
    specification = next(
        row
        for row in top_cli.TOP_LEVEL_COMMANDS
        if row["name"] == "agent-system"
    )
    assert specification["subcommands"] == (
        "ingest",
        "reindex",
        "ask",
        "neo4j-export",
        "export-event",
    )


def test_root_cli_exposes_only_current_runtime_and_research_utilities() -> None:
    assert set(top_cli.main.commands) == {
        "agent-system",
        "cqs",
        "ontology",
        "report",
        "source",
    }
    assert not {
        "agent",
        "chunk",
        "cross-source",
        "demo",
        "index",
        "kg",
        "query",
    } & set(top_cli.main.commands)


def test_active_commands_default_to_the_cohort_free_configuration() -> None:
    result = CliRunner().invoke(cli_module.agent_system, ["ingest", "--help"])

    assert result.exit_code == 0, result.output
    assert "configs/aviation_knowledge_v1.yaml" in result.output
    assert "configs/cross_source_v1.yaml" not in result.output


def test_ingest_uses_store_and_has_no_selection_or_resume(
    monkeypatch,
    tmp_path: Path,
) -> None:
    observed: dict[str, object] = {}
    store = _Store()
    summary = SimpleNamespace(
        discovered_count=718,
        selected_count=1,
        attempted_count=1,
        skipped_count=0,
        ok_count=1,
        insufficient_count=0,
        blocked_count=0,
    )
    monkeypatch.setattr(
        cli_module,
        "_load_config",
        lambda _path: {"agent_system": {}},
    )
    monkeypatch.setattr(
        cli_module,
        "_open_store",
        lambda config, store_dir, create: store,
    )

    def run(config, selected_store, **kwargs):
        observed.update(kwargs)
        assert selected_store is store
        return summary

    monkeypatch.setattr(cli_module, "run_ingestion_pipeline", run)
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ingest",
            "--config",
            "configs/aviation_knowledge_v1.yaml",
            "--store-dir",
            str(tmp_path / "store"),
            "--source-id",
            "2026-05-19:123",
            "--allow-live-model",
        ],
    )

    assert result.exit_code == 0, result.output
    assert observed["source_ids"] == ("2026-05-19:123",)
    assert observed["allow_live_model"] is True
    assert "selected: 1" in result.output
    assert "knowledge_revision: 7" in result.output
    assert "--selection" not in result.output
    assert "--resume" not in result.output


def test_ask_always_uses_query_agent_and_preserves_source_scope(
    monkeypatch,
) -> None:
    store = _Store()
    runtime = SimpleNamespace(
        store=store,
        source_index=None,
        event_index=None,
    )
    observed: dict[str, object] = {}
    monkeypatch.setattr(
        cli_module,
        "_load_config",
        lambda _path: {"agent_system": {}},
    )
    monkeypatch.setattr(
        cli_module,
        "open_query_runtime",
        lambda *args, **kwargs: runtime,
    )
    monkeypatch.setattr(cli_module, "load_environment", lambda: None)

    def answer(*, runtime, question, scope, model_factory):
        observed.update(
            runtime=runtime,
            question=question,
            scope=scope,
            model_factory=model_factory,
        )
        return QueryToolOutcome(
            status="ok",
            answer="Source-backed answer.",
            retrieved_event_ids=["urn:event:123"],
            source_ids=["2026-05-19:123"],
        )

    monkeypatch.setattr(cli_module, "answer_question", answer)
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--config",
            "configs/aviation_knowledge_v1.yaml",
            "--question",
            "What did the advisory say?",
            "--event-id",
            "urn:event:123",
            "--source-family",
            "atcscc_advisory",
        ],
    )

    assert result.exit_code == 0, result.output
    assert observed["runtime"] is runtime
    assert observed["model_factory"] is not None
    scope = observed["scope"]
    assert scope.event_id == "urn:event:123"
    assert tuple(family.value for family in scope.source_families) == (
        "atcscc_advisory",
    )
    assert "answer: Source-backed answer." in result.output


def test_reindex_rebuilds_both_derived_indexes(monkeypatch) -> None:
    store = _Store()
    monkeypatch.setattr(
        cli_module,
        "_load_config",
        lambda _path: {
            "agent_system": {
                "storage": {
                    "embedding_model": "test/encoder",
                    "chroma": "chroma",
                }
            }
        },
    )
    monkeypatch.setattr(
        cli_module,
        "_open_store",
        lambda config, store_dir, create: store,
    )
    monkeypatch.setattr(
        cli_module,
        "SentenceTransformerTMIEventEncoder",
        lambda model, allow_download: SimpleNamespace(model_id=model),
    )
    states = (
        SimpleNamespace(
            collection_name="tmi_events_v1",
            status="current",
            document_count=2,
            vector_count=2,
        ),
        SimpleNamespace(
            collection_name="aviation_source_chunks_v1",
            status="current",
            document_count=5,
            vector_count=5,
        ),
    )
    monkeypatch.setattr(
        cli_module,
        "reindex_store",
        lambda *args, **kwargs: states,
    )

    result = CliRunner().invoke(
        cli_module.agent_system,
        ["reindex", "--config", "configs/aviation_knowledge_v1.yaml"],
    )

    assert result.exit_code == 0, result.output
    assert "tmi_events_v1" in result.output
    assert "aviation_source_chunks_v1" in result.output


def test_export_event_reads_store_not_a_corpus(
    monkeypatch,
    tmp_path: Path,
) -> None:
    store = _Store()
    manifest = tmp_path / "event_export_manifest.json"
    monkeypatch.setattr(
        cli_module,
        "_load_config",
        lambda _path: {"agent_system": {}},
    )
    monkeypatch.setattr(
        cli_module,
        "_open_store",
        lambda config, store_dir, create: store,
    )
    monkeypatch.setattr(
        cli_module,
        "export_event",
        lambda selected_store, event_id, output_dir: manifest,
    )

    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "export-event",
            "--config",
            "configs/aviation_knowledge_v1.yaml",
            "--event-id",
            "urn:event:123",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert str(manifest) in result.output
