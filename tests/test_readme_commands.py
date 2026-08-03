from __future__ import annotations

from pathlib import Path


def test_readme_lists_current_agent_system_commands() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for command in [
        "aviation-ai agent-system ingest",
        "aviation-ai agent-system reindex",
        "aviation-ai agent-system ask",
        "aviation-ai agent-system build-kg",
        "aviation-ai agent-system neo4j-export",
        "aviation-ai agent-system export-event",
    ]:
        assert command in readme

    assert "aviation-ai agent-system " + "build" + "-corpus" not in readme
    assert "aviation-ai agent-system " + "index" + "-events" not in readme
    assert "aviation-ai agent-system ask-corpus" not in readme
    assert "--corpus" + "-dir" not in readme
    assert "data/corpus/agent_system" not in readme
    assert "Canonical semantic store" in readme
    assert "docs/system_architecture.md" in readme
    assert "does not provide live ATC support" in readme


def test_readme_is_concise_and_research_facing() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    assert len(readme.splitlines()) <= 220
    assert "SQLite is authoritative." not in readme
    assert "## Regression Semantics" not in readme
    assert "2026-05-19:123" not in readme
    assert "2026-05-20:020" not in readme
    assert "Canonical semantic store" in readme
    assert "docs/system_architecture.md" in readme
    assert "REPRODUCIBILITY.md" in readme
    assert "RESEARCH_AUDIT.md" in readme
