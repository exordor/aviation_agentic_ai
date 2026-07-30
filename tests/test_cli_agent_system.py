"""Small public-surface checks for the corpus-first Agent CLI."""

from __future__ import annotations

from click.testing import CliRunner

import aviation_agentic_ai.cli as top_cli
import aviation_agentic_ai.cli_agent_system as cli_module


def test_public_agent_system_surface_is_corpus_first() -> None:
    assert set(cli_module.agent_system.commands) == {
        "build-corpus",
        "ask",
        "index-cases",
        "neo4j-export",
        "export-case",
    }
    specification = next(
        row
        for row in top_cli.TOP_LEVEL_COMMANDS
        if row["name"] == "agent-system"
    )
    assert specification["subcommands"] == (
        "build-corpus",
        "ask",
        "index-cases",
        "neo4j-export",
        "export-case",
    )


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
