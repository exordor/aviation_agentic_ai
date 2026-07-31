"""Small public-surface checks for the corpus-first Agent CLI."""

from __future__ import annotations

from click.testing import CliRunner

import aviation_agentic_ai.cli as top_cli
import aviation_agentic_ai.cli_agent_system as cli_module


def test_public_agent_system_surface_is_corpus_first() -> None:
    assert set(cli_module.agent_system.commands) == {
        "build-corpus",
        "ask",
        "index-events",
        "neo4j-export",
        "export-event",
    }
    specification = next(
        row
        for row in top_cli.TOP_LEVEL_COMMANDS
        if row["name"] == "agent-system"
    )
    assert specification["subcommands"] == (
        "build-corpus",
        "ask",
        "index-events",
        "neo4j-export",
        "export-event",
    )


def test_retired_case_commands_are_unknown() -> None:
    runner = CliRunner()

    for command in ("index-cases", "export-case"):
        result = runner.invoke(cli_module.agent_system, [command])
        assert result.exit_code == 2
        assert f"No such command '{command}'" in result.output


def test_removed_single_run_options_stay_out_of_the_public_cli() -> None:
    runner = CliRunner()
    ask = runner.invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            "obsolete",
            "--question",
            "What happened?",
        ],
    )
    neo4j = runner.invoke(
        cli_module.agent_system,
        ["neo4j-export", "--run-dir", "obsolete"],
    )

    assert ask.exit_code == 2
    assert "No such option '--run-dir'" in ask.output
    assert neo4j.exit_code == 2
    assert "No such option '--run-dir'" in neo4j.output


def test_neo4j_export_requires_a_published_tmi_event_corpus(tmp_path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        cli_module.agent_system,
        ["neo4j-export", "--corpus-dir", str(tmp_path)],
    )

    assert result.exit_code == 1
    assert "a published tmi-event-corpus-v3 manifest is required" in result.output


def test_build_corpus_allows_zero_call_deterministic_event_without_live_authorization(
    tmp_path,
) -> None:
    runner = CliRunner()
    output_dir = tmp_path / "corpus"

    result = runner.invoke(
        cli_module.agent_system,
        [
            "build-corpus",
            "--config",
            "configs/cross_source_v1.yaml",
            "--output-dir",
            str(output_dir),
            "--source-id",
            "2026-05-19:123",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "selected: 1" in result.output
    assert "ok: 1" in result.output
    assert "agent_calls: provider=0 tool=0" in result.output
