from __future__ import annotations

from click.testing import CliRunner

from aviation_agentic_ai.cli import main


def test_cli_agent_demo_runs_l2_agent_with_artifact_replay() -> None:
    result = CliRunner().invoke(
        main,
        [
            "agent",
            "demo",
            "--source-id",
            "2026-05-19:032",
            "--question",
            "Which NAS elements are affected by this ATCSCC advisory?",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ATCSCC L2 Agent demo" in result.output
    assert "source_id: 2026-05-19:032" in result.output
    assert "template_id: QT-Q01-AFFECTED-NAS-ELEMENTS" in result.output
    assert "answer_values:" in result.output
    assert "citations:" in result.output
    assert "l1_iterations:" in result.output
    assert "Boundary: retrospective, source-bounded" in result.output


def test_cli_agent_demo_abstains_for_live_operational_question() -> None:
    result = CliRunner().invoke(
        main,
        [
            "agent",
            "demo",
            "--source-id",
            "2026-05-19:032",
            "--question",
            "Should I reroute aircraft around ZNY right now?",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "abstain: true" in result.output
    assert "live operational decision support" in result.output
