from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.overnight import build_overnight_summary, write_overnight_summary


def test_overnight_summary_handles_partial_stage_outputs(tmp_path: Path) -> None:
    (tmp_path / "ontology_evaluation.json").write_text(
        json.dumps(
            {
                "judgment": {
                    "rdf_valid_tbox_extraction_prototype": True,
                    "valid_tbox_prototype": False,
                    "publication_ready_ontology": False,
                },
                "quality_gates": [
                    {"id": "annotation_coverage", "passed": False, "severity": "high"}
                ],
                "semantic_smells": [{"id": "self-quantity-Cl_Pressure"}],
                "cq_coverage": {
                    "entity_mention_coverage_ratio": 0.8,
                    "unique_entity_coverage_ratio": 0.7,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    summary = build_overnight_summary(tmp_path)

    assert summary["inputs_present"]["ontology_evaluation"]
    assert not summary["inputs_present"]["source_scope"]
    assert summary["ontology_evaluation"]["failed_quality_gates"][0]["id"] == "annotation_coverage"


def test_write_overnight_summary_outputs_json_and_markdown(tmp_path: Path) -> None:
    (tmp_path / "review_progress.json").write_text(
        json.dumps(
            {
                "finding_status_counts": {"open": 1},
                "action_status_counts": {"planned": 1},
                "open_findings": [{"id": "F-1"}],
                "open_actions": [{"id": "A-1"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    json_path, md_path, summary = write_overnight_summary(tmp_path)

    assert json_path.exists()
    assert md_path.exists()
    assert summary["review_progress"]["finding_status_counts"] == {"open": 1}
    assert "Overnight Ontology Optimization Report" in md_path.read_text(encoding="utf-8")


def test_overnight_summary_includes_latest_live_evaluations(tmp_path: Path) -> None:
    evaluation = {
        "judgment": {
            "rdf_valid_tbox_extraction_prototype": True,
            "valid_tbox_prototype": True,
            "publication_ready_ontology": False,
        },
        "quality_gates": [{"id": "cq_unique_lexical_coverage", "passed": False}],
        "semantic_smells": [],
        "cq_coverage": {
            "entity_mention_coverage_ratio": 0.6,
            "unique_entity_coverage_ratio": 0.5,
            "answerability_metrics": {"support_score": 0.4},
        },
    }
    (tmp_path / "live_page1_ontology_evaluation.json").write_text(
        json.dumps(evaluation) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "live_page1_boundary_evaluation.json").write_text(
        json.dumps(
            {
                **evaluation,
                "cq_coverage": {
                    "entity_mention_coverage_ratio": 0.7,
                    "answerability_metrics": {"support_score": 0.8},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    json_path, md_path, summary = write_overnight_summary(tmp_path)

    assert json_path.exists()
    assert summary["latest_live_ontology_evaluation"]["report_name"] == (
        "live_page1_ontology_evaluation"
    )
    assert summary["latest_live_boundary_evaluation"]["answerability_support_score"] == 0.8
    markdown = md_path.read_text(encoding="utf-8")
    assert "Latest Live Generation Evaluation" in markdown
    assert "Latest Live Boundary-CQ Evaluation" in markdown


def test_cli_report_overnight_writes_summary(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        [
            "report",
            "overnight",
            "--stage-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "overnight_optimization_report.json").exists()
    assert (tmp_path / "overnight_optimization_report.md").exists()


def test_cli_report_stages_writes_available_stage_reports(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "reports" / "reviews").mkdir(parents=True)
    (tmp_path / "reports" / "stages").mkdir(parents=True)
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "default.yaml").write_text(
        "paths:\n  stage_report_dir: reports/stages\n",
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        main,
        [
            "report",
            "stages",
            "--reviews-dir",
            str(tmp_path / "reports" / "reviews"),
            "--output-dir",
            str(tmp_path / "reports" / "stages"),
        ],
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / "reports" / "stages" / "review_progress.json").exists()
    assert (tmp_path / "reports" / "stages" / "overnight_optimization_report.json").exists()
