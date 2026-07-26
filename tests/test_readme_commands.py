from __future__ import annotations

from pathlib import Path


def test_readme_lists_current_agent_system_commands() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for command in [
        "aviation-ai agent-system ingest",
        "aviation-ai agent-system ask",
        "aviation-ai agent-system neo4j-export",
    ]:
        assert command in readme

    assert "docs/multi_agent_kg_system_design.md" in readme
    assert "not live aviation operations" in readme
