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
