from __future__ import annotations

from click.testing import CliRunner

from aviation_agentic_ai.cli_demo import demo


def test_demo_traces_default_advisory_offline(tmp_path, monkeypatch) -> None:
    """The demo runs offline on precomputed artifacts and threads all four stages."""
    runner = CliRunner()

    result = runner.invoke(demo, [])

    assert result.exit_code == 0, result.output
    out = result.output
    # All four pipeline stages are present.
    assert "ATCSCC advisory end-to-end demo" in out
    assert "[1] Advisory source text" in out
    assert "[2] S0 rule-only deterministic backbone" in out
    assert "[3] S4 hybrid enrichment -> advisory event graph" in out
    assert "[4] KG-RAG vs vector-only retrieval and grounded answer" in out
    # The default demo advisory is ADVZY 032.
    assert "2026-05-19:032" in out
    # Both retrieval arms are shown.
    assert "KG-RAG" in out
    assert "Vector-only" in out
    # The claim boundary footer is present.
    assert "retrospective, source-bounded" in out


def test_demo_rejects_unknown_source_id() -> None:
    """An unknown source_id produces a clear error, not a traceback."""
    runner = CliRunner()
    result = runner.invoke(demo, ["--source-id", "9999-99-99:999"])

    assert result.exit_code != 0
    assert "No input record" in result.output
