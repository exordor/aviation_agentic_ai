from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.hygiene import build_hygiene_plan, run_report_hygiene


def _write_stage_fixture(stage_dir: Path, reviews_dir: Path) -> None:
    stage_dir.mkdir(parents=True)
    reviews_dir.mkdir(parents=True)
    (stage_dir / "ontology_evaluation.json").write_text("{}\n", encoding="utf-8")
    (stage_dir / "ontology_evaluation.md").write_text("# Eval\n", encoding="utf-8")
    (stage_dir / "source_scope.json").write_text("{}\n", encoding="utf-8")
    (stage_dir / "retrieval_ablation.json").write_text("{}\n", encoding="utf-8")
    (stage_dir / "generation_runs").mkdir()
    (stage_dir / "generation_runs" / "run-a").mkdir()
    (stage_dir / "generation_runs" / "run-a" / "manifest.json").write_text(
        "{}\n",
        encoding="utf-8",
    )
    (reviews_dir / "review.json").write_text("{}\n", encoding="utf-8")
    (reviews_dir / "review.md").write_text("# Review\n", encoding="utf-8")


def test_hygiene_plan_classifies_stage_and_review_artifacts(tmp_path: Path) -> None:
    stage_dir = tmp_path / "reports" / "stages"
    reviews_dir = tmp_path / "reports" / "reviews"
    archive_root = tmp_path / "reports" / "archive"
    _write_stage_fixture(stage_dir, reviews_dir)

    plan = build_hygiene_plan(
        stage_dir,
        archive_root,
        reviews_dir,
        archive_date=date(2026, 5, 18),
        base=tmp_path,
    )

    assert plan["archive_items_total"] == 5
    assert plan["review_items_total"] == 2
    assert len(plan["categories"]["ontology_evaluation"]) == 2
    assert len(plan["categories"]["source_scope"]) == 1
    assert len(plan["categories"]["generation_runs"]) == 1
    assert len(plan["categories"]["rag_experiments"]) == 1
    assert len(plan["categories"]["reviews"]) == 2
    assert plan["archive_dir"] == "reports/archive/stages/2026-05-18"


def test_report_hygiene_dry_run_does_not_move_files(tmp_path: Path) -> None:
    stage_dir = tmp_path / "reports" / "stages"
    reviews_dir = tmp_path / "reports" / "reviews"
    archive_root = tmp_path / "reports" / "archive"
    _write_stage_fixture(stage_dir, reviews_dir)

    json_path, md_path, plan = run_report_hygiene(
        stage_dir,
        archive_root,
        reviews_dir,
        archive_date=date(2026, 5, 18),
        base=tmp_path,
    )

    assert json_path is None
    assert md_path is None
    assert not plan["applied"]
    assert (stage_dir / "ontology_evaluation.json").exists()
    assert not (stage_dir / "index.json").exists()


def test_report_hygiene_apply_archives_and_writes_index(tmp_path: Path) -> None:
    stage_dir = tmp_path / "reports" / "stages"
    reviews_dir = tmp_path / "reports" / "reviews"
    archive_root = tmp_path / "reports" / "archive"
    _write_stage_fixture(stage_dir, reviews_dir)

    json_path, md_path, plan = run_report_hygiene(
        stage_dir,
        archive_root,
        reviews_dir,
        apply=True,
        archive_date=date(2026, 5, 18),
        base=tmp_path,
    )

    assert json_path == stage_dir / "index.json"
    assert md_path == stage_dir / "index.md"
    assert (stage_dir / "index.json").exists()
    assert (stage_dir / "index.md").exists()
    assert not (stage_dir / "ontology_evaluation.json").exists()
    assert (archive_root / "stages" / "2026-05-18" / "ontology_evaluation.json").exists()
    assert (archive_root / "stages" / "2026-05-18" / "generation_runs").is_dir()
    assert (reviews_dir / "review.json").exists()
    assert len(plan["moved_items"]) == 5
    index = json.loads((stage_dir / "index.json").read_text(encoding="utf-8"))
    assert index["categories"]["reviews"]


def test_cli_report_hygiene_dry_run_does_not_move_files(tmp_path: Path) -> None:
    stage_dir = tmp_path / "reports" / "stages"
    reviews_dir = tmp_path / "reports" / "reviews"
    archive_root = tmp_path / "reports" / "archive"
    _write_stage_fixture(stage_dir, reviews_dir)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "hygiene",
            "--dry-run",
            "--stage-dir",
            str(stage_dir),
            "--archive-root",
            str(archive_root),
            "--reviews-dir",
            str(reviews_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Dry run" in result.output
    assert (stage_dir / "ontology_evaluation.json").exists()
    assert not (stage_dir / "index.json").exists()


def test_cli_report_hygiene_apply_writes_index(tmp_path: Path) -> None:
    stage_dir = tmp_path / "reports" / "stages"
    reviews_dir = tmp_path / "reports" / "reviews"
    archive_root = tmp_path / "reports" / "archive"
    _write_stage_fixture(stage_dir, reviews_dir)

    result = CliRunner().invoke(
        main,
        [
            "report",
            "hygiene",
            "--apply",
            "--stage-dir",
            str(stage_dir),
            "--archive-root",
            str(archive_root),
            "--reviews-dir",
            str(reviews_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Archived" in result.output
    assert (stage_dir / "index.json").exists()
    assert (stage_dir / "index.md").exists()
