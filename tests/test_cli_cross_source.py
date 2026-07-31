from click.testing import CliRunner

from aviation_agentic_ai.cli_cross_source import cross_source_group


def test_cross_source_cli_exposes_approved_commands() -> None:
    runner = CliRunner()

    result = runner.invoke(cross_source_group, ["--help"])

    assert result.exit_code == 0
    for command in (
        "refresh",
        "align",
        "build",
        "neo4j-export",
        "neo4j-load",
        "answer",
        "evaluate",
    ):
        assert command in result.output


def test_provider_context_mode_fails_closed_until_provider_is_configured() -> None:
    runner = CliRunner()

    result = runner.invoke(
        cross_source_group, ["align", "--context-mode", "provider"]
    )

    assert result.exit_code != 0
    assert "No context-agent provider is configured" in result.output
