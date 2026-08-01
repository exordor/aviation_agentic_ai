"""Public-surface tests for the ingestion-first Agent-system CLI."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner

import aviation_agentic_ai.cli as top_cli
import aviation_agentic_ai.cli_agent_system as cli_module
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryStatement,
    QueryToolOutcome,
)


class _Store:
    root = Path("/tmp/test-store")
    dataset_id = "dataset:test"

    def get_knowledge_revision(self) -> int:
        return 7

    def get_source_version(self, source_version_id: str):  # type: ignore[no-untyped-def]
        assert source_version_id in {
            "source-version:123",
            "source-version:candidate",
        }
        if source_version_id == "source-version:candidate":
            return SimpleNamespace(
                source_id="candidate:unverified",
                family=SimpleNamespace(value="faa_term"),
                metadata={"title": "Unverified Search Candidate"},
                logical_time=None,
                source_url=None,
            )
        return SimpleNamespace(
            source_id="2026-05-19:123",
            family=SimpleNamespace(value="atcscc_advisory"),
            metadata={
                "title": "ATCSCC Advisory",
                "advisory_number": 123,
                "advisory_date": "2026-05-19",
            },
            logical_time=None,
            source_url="https://www.fly.faa.gov/example/123",
        )

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


def test_root_cli_exposes_only_the_current_runtime() -> None:
    assert set(top_cli.main.commands) == {"agent-system"}


def test_active_commands_default_to_the_cohort_free_configuration() -> None:
    result = CliRunner().invoke(cli_module.agent_system, ["ingest", "--help"])

    assert result.exit_code == 0, result.output
    assert "configs/aviation_knowledge_v1.yaml" in result.output
    assert "configs/cross_source_v1.yaml" not in result.output


def test_ingest_routes_selected_domain_and_external_source_root(
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
        index_status="updated",
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

    monkeypatch.setattr(cli_module, "run_configured_ingestion", run)
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ingest",
            "--config",
            "configs/aviation_knowledge_v1.yaml",
            "--store-dir",
            str(tmp_path / "store"),
            "--domain",
            "tmi",
            "--source-root",
            str(tmp_path),
            "--advisory-id",
            "2026-05-19:123",
            "--allow-live-model",
        ],
    )

    assert result.exit_code == 0, result.output
    assert observed["advisory_ids"] == ("2026-05-19:123",)
    assert observed["domain"] == "tmi"
    assert observed["source_root"] == tmp_path
    assert observed["allow_live_model"] is True
    assert "selected: 1" in result.output
    assert "retrieval_indexes: updated" in result.output
    assert "knowledge_revision: 7" in result.output
    assert "resolved_config_sha256:" in result.output
    assert "--selection" not in result.output
    assert "--resume" not in result.output


def test_ingest_defaults_to_all_domains_and_rejects_ambiguous_backfill(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        cli_module,
        "_load_config",
        lambda _path: {"agent_system": {}},
    )
    monkeypatch.setattr(
        cli_module,
        "_open_store",
        lambda config, store_dir, create: _Store(),
    )

    result = CliRunner().invoke(
        cli_module.agent_system,
        ["ingest", "--advisory-id", "2026-05-19:123"],
    )

    assert result.exit_code != 0
    assert "--advisory-id requires --domain tmi" in result.output


def test_ingest_help_exposes_full_domain_as_the_default() -> None:
    result = CliRunner().invoke(cli_module.agent_system, ["ingest", "--help"])

    assert result.exit_code == 0, result.output
    assert "--domain [all|tmi|flight-airspace]" in result.output
    assert "[default: all]" in result.output
    assert "--source-root DIRECTORY" in result.output


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
            retrieved_source_version_ids=[
                "source-version:123",
                "source-version:candidate",
            ],
            answer_statements=[
                HybridQueryStatement(
                    kind="source_record",
                    text="Source-backed answer.",
                    support_event_ids=("urn:event:123",),
                    support_source_ids=("2026-05-19:123",),
                    support_source_version_ids=("source-version:123",),
                    support_source_anchor_ids=("source-anchor:123",),
                )
            ],
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
    assert scope.source_ids == ()
    assert tuple(family.value for family in scope.source_families) == (
        "atcscc_advisory",
    )
    assert "answer: Source-backed answer." in result.output
    assert "evidence_sources:" in result.output
    assert "ATCSCC Advisory 123 (2026-05-19) — FAA ATCSCC" in result.output
    assert "Unverified Search Candidate" not in result.output
    assert "sources: 2026-05-19:123" not in result.output
    assert "events_retrieved: 1" in result.output
    assert "urn:event:123" not in result.output


def test_ask_does_not_expose_internal_source_id_as_a_user_option() -> None:
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--config",
            "configs/aviation_knowledge_v1.yaml",
            "--question",
            "What did Advisory 138 say?",
            "--source-id",
            "2026-05-19:138",
        ],
    )

    assert result.exit_code == 2
    assert "No such option" in result.output
    assert "--source-id" in result.output


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


def test_export_event_reads_the_authoritative_store(
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
