from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.paths import PROJECT_ROOT
from aviation_agentic_ai.reporting.academic_outputs import (
    write_academic_report,
    write_defense_deck_outline,
    write_defense_notes,
    write_visual_assets,
)


STAGE_INDEX = PROJECT_ROOT / "reports" / "stages" / "index.json"


def test_academic_report_contains_required_sections_and_sources(tmp_path: Path) -> None:
    md_path, sources_path, result = write_academic_report(
        tmp_path,
        stage_index_path=STAGE_INDEX,
    )

    markdown = md_path.read_text(encoding="utf-8")
    sources = json.loads(sources_path.read_text(encoding="utf-8"))

    assert "## Abstract" in markdown
    assert "## 4. Explainable Ontology Design" in markdown
    assert "## 7. Hybrid RAG and GraphRAG Evaluation" in markdown
    assert "## 11. Advisory Boundary" in markdown
    assert "reports/stages/chunking_comparison.json" in markdown
    assert sources["source_policy"]["env_files_read"] is False
    assert sources["source_policy"]["secrets_allowed"] is False
    assert len(result["summary"]["source_paths"]) >= 5


def test_defense_notes_include_core_qa_and_advisory_boundary(tmp_path: Path) -> None:
    md_path, json_path, notes = write_defense_notes(
        tmp_path,
        stage_index_path=STAGE_INDEX,
    )

    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    questions = [pair["question"] for pair in notes["qa_pairs"]]

    assert "## Likely Questions" in markdown
    assert any("ontology" in question.lower() for question in questions)
    assert any("GraphRAG" in pair["question"] for pair in notes["qa_pairs"])
    assert "POH" in markdown
    assert payload["source_policy"]["secrets_allowed"] is False


def test_defense_deck_outline_is_academic_structured_argument(tmp_path: Path) -> None:
    md_path, json_path, outline = write_defense_deck_outline(
        tmp_path,
        stage_index_path=STAGE_INDEX,
    )

    markdown = md_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert outline["presentation_type"] == "structured_argument"
    assert outline["deck_profile"] == "engineering-platform"
    assert len(outline["slides"]) == 13
    assert all(slide["title"] and slide["claim"] for slide in outline["slides"])
    assert all(slide["evidence_sources"] for slide in outline["slides"])
    assert outline["slides"][-1]["role"] == "appendix"
    assert "## Academic QA Checklist" in markdown
    assert payload["metrics_snapshot"]["hybrid_rag"]


def test_visual_assets_are_local_svg_without_gateway(tmp_path: Path) -> None:
    paths, manifest = write_visual_assets(tmp_path)

    assert manifest["generation_method"] == "local_deterministic_svg_fallbacks"
    assert manifest["uses_gateway_or_api"] is False
    assert all(path.exists() for path in paths)
    assert all(
        asset["fallback_exists"]
        for asset in manifest["assets"]
        if asset["fallback_path"]
    )
    assert (tmp_path / "assets" / "project_cover.svg").read_text(
        encoding="utf-8"
    ).startswith("<svg")


def test_cli_academic_outputs_write_expected_files(tmp_path: Path) -> None:
    runner = CliRunner()
    commands = [
        ["report", "visual-assets", "--output-dir", str(tmp_path)],
        [
            "report",
            "academic-paper",
            "--no-ai",
            "--output-dir",
            str(tmp_path),
            "--stage-index",
            str(STAGE_INDEX),
        ],
        [
            "report",
            "defense-notes",
            "--output-dir",
            str(tmp_path),
            "--stage-index",
            str(STAGE_INDEX),
        ],
        [
            "report",
            "defense-deck-outline",
            "--output-dir",
            str(tmp_path),
            "--stage-index",
            str(STAGE_INDEX),
        ],
    ]

    for command in commands:
        result = runner.invoke(main, command)
        assert result.exit_code == 0, result.output

    assert (tmp_path / "project_academic_report.md").exists()
    assert (tmp_path / "project_defense_notes.json").exists()
    assert (tmp_path / "aviation_graphrag_defense_deck_sources.json").exists()
    assert (tmp_path / "assets" / "visual_assets_manifest.json").exists()
