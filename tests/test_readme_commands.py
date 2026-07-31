from __future__ import annotations

from pathlib import Path


def test_readme_lists_current_agent_system_commands() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for command in [
        "aviation-ai agent-system ingest",
        "aviation-ai agent-system reindex",
        "aviation-ai agent-system ask",
        "aviation-ai agent-system neo4j-export",
        "aviation-ai agent-system export-event",
    ]:
        assert command in readme

    assert "aviation-ai agent-system " + "build" + "-corpus" not in readme
    assert "aviation-ai agent-system " + "index" + "-events" not in readme
    assert "aviation-ai agent-system ask-corpus" not in readme
    assert "--corpus" + "-dir" not in readme
    assert "docs/multi_agent_kg_system_design.md" in readme
    assert "does not provide live ATC support" in readme
