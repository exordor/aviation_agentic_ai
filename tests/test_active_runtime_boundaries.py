"""Repository-boundary checks for the active ingestion-first runtime."""

from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_active_runtime_has_a_dedicated_dependency_extra() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    extras = project["project"]["optional-dependencies"]

    assert extras["agent-system"] == [
        "langchain>=0.2",
        "langchain-openai>=0.1",
        "langgraph>=0.2",
    ]
    assert "web" not in extras
