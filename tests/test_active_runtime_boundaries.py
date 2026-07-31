"""Repository-boundary checks for the active ingestion-first runtime."""

from __future__ import annotations

import ast
import json
import tomllib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
AGENT_SYSTEM = ROOT / "src/aviation_agentic_ai/agent_system"


def test_active_runtime_has_a_dedicated_dependency_extra() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    extras = project["project"]["optional-dependencies"]

    assert extras["agent-system"] == [
        "langchain>=0.2",
        "langchain-openai>=0.1",
        "langgraph>=0.2",
    ]
    assert "web" not in extras


def _imports_under(path: Path) -> set[str]:
    imports: set[str] = set()
    for source_path in sorted(path.rglob("*.py")):
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
            elif isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
    return imports


def test_active_runtime_does_not_import_historical_cross_source_modules() -> None:
    imports = _imports_under(AGENT_SYSTEM)

    assert not {
        module
        for module in imports
        if module == "aviation_agentic_ai.cross_source"
        or module.startswith("aviation_agentic_ai.cross_source.")
    }


@pytest.mark.parametrize(
    ("prefix", "parts", "expected"),
    (
        (
            "event",
            ("run:1", "source:1", "atm:GroundStopTMI"),
            "event:70d47f345be0cd47",
        ),
        (
            "source-version",
            ("2026-05-19:123", "abc"),
            "source-version:650fd7627094513f",
        ),
        ("fact", ("s", "p", "o"), "fact:59dbbcf012d9d2b3"),
    ),
)
def test_neutral_stable_id_preserves_existing_ids(
    prefix: str,
    parts: tuple[str, ...],
    expected: str,
) -> None:
    from aviation_agentic_ai.utils.identifiers import stable_id

    assert stable_id(prefix, *parts) == expected


def test_neutral_jsonl_reader_preserves_object_contract(tmp_path: Path) -> None:
    from aviation_agentic_ai.utils.io import read_jsonl_objects

    source = tmp_path / "records.jsonl"
    source.write_text('{"b": 2}\n\n{"a": 1}\n', encoding="utf-8")

    assert read_jsonl_objects(source) == [{"b": 2}, {"a": 1}]

    source.write_text(json.dumps(["not", "an", "object"]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"Expected JSON object at .*records.jsonl:1"):
        read_jsonl_objects(source)


def test_neutral_jsonl_reader_reports_path_and_line(tmp_path: Path) -> None:
    from aviation_agentic_ai.utils.io import read_jsonl_objects

    source = tmp_path / "records.jsonl"
    source.write_text('{"ok": true}\n{broken}\n', encoding="utf-8")

    with pytest.raises(ValueError, match=r"Invalid JSONL at .*records.jsonl:2"):
        read_jsonl_objects(source)
