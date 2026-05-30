from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.reviews import (
    aggregate_review_reports,
    load_adversarial_review_report,
    load_review_report,
    write_review_progress,
)


def write_review(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "review_id": "test-review",
                "title": "Test Review",
                "findings": [
                    {
                        "id": "F-1",
                        "area": "cqs",
                        "severity": "high",
                        "title": "Missing CQ validation",
                        "evidence": ["CQ file accepts malformed entries."],
                        "impact": "Evaluation can undercount broken records.",
                        "recommendation": "Add strict validation.",
                        "status": "open",
                    },
                    {
                        "id": "F-2",
                        "area": "pipeline",
                        "severity": "medium",
                        "title": "Missing manifest",
                        "evidence": ["Generated runs lack config hashes."],
                        "impact": "Runs are hard to reproduce.",
                        "recommendation": "Write a run manifest.",
                        "status": "closed",
                    },
                ],
                "actions": [
                    {
                        "id": "A-1",
                        "finding_ids": ["F-1"],
                        "priority": "P0",
                        "title": "Add CQ validator",
                        "target": "CQs",
                        "status": "planned",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_load_review_report_validates_schema(tmp_path: Path) -> None:
    path = tmp_path / "review.json"
    write_review(path)

    report = load_review_report(path)

    assert report["review_id"] == "test-review"
    assert report["findings"][0]["severity"] == "high"


def test_aggregate_review_reports_tracks_open_items(tmp_path: Path) -> None:
    path = tmp_path / "review.json"
    write_review(path)
    report = load_review_report(path)

    progress = aggregate_review_reports([report])

    assert progress["reviews_total"] == 1
    assert progress["findings_total"] == 2
    assert progress["severity_counts"]["high"] == 1
    assert progress["area_counts"]["cqs"]["total"] == 1
    assert len(progress["open_findings"]) == 1
    assert progress["open_actions"][0]["priority"] == "P0"


def test_adversarial_review_schema_is_validated_and_skipped_by_progress(
    tmp_path: Path,
) -> None:
    reviews_dir = tmp_path / "reviews"
    reviews_dir.mkdir()
    write_review(reviews_dir / "legacy-review.json")
    adversarial_path = reviews_dir / "adversarial_experiment_review_round_1.json"
    adversarial_path.write_text(
        json.dumps(
            {
                "round": 1,
                "subagent_findings": [
                    {
                        "subagent": "A",
                        "role": "Thesis Methodologist",
                        "must_fix": ["Keep manual review pending."],
                        "should_fix": [],
                        "nice_to_have": [],
                        "unsafe_claims": [],
                        "manual_review_dependencies": [],
                        "acceptance_criteria": [],
                    }
                ],
                "must_fix": ["Do not overclaim."],
                "should_fix": [],
                "nice_to_have": [],
                "unsafe_claims": [],
                "manual_review_dependencies": [],
                "recommended_iterations": [],
                "acceptance_criteria": ["Schema validates."],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    adversarial = load_adversarial_review_report(adversarial_path)
    _, _, progress = write_review_progress(reviews_dir, tmp_path / "stages")

    assert adversarial["round"] == 1
    assert progress["reviews_total"] == 1


def test_deepseek_implementation_triage_and_remediation_artifacts_have_required_shape() -> None:
    root = Path(__file__).resolve().parents[1]
    triage = json.loads(
        (root / "reports/reviews/deepseek_v4pro_implementation_triage.json").read_text(
            encoding="utf-8",
        )
    )
    remediation = json.loads(
        (
            root / "reports/reviews/deepseek_v4pro_implementation_remediation.json"
        ).read_text(encoding="utf-8")
    )

    required_triage_fields = {
        "finding_id",
        "severity",
        "current_status",
        "files_inspected",
        "evidence",
        "planned_action",
        "risk_if_unfixed",
        "tests_required",
        "documentation_report_impact",
    }
    assert triage["policy"]["do_not_trust_report_blindly"] is True
    assert triage["policy"]["code_changes_before_triage"] is False
    assert {finding["finding_id"] for finding in triage["findings"]} >= {"C1", "C2", "NF5"}
    assert all(required_triage_fields <= set(finding) for finding in triage["findings"])

    assert remediation["policy"]["scientific_metrics_changed"] is False
    assert remediation["policy"]["human_review_claimed"] is False
    assert remediation["policy"]["external_aviation_expert_certified"] is False
    assert {"I6", "NF3"} <= set(remediation["deferred_items"])
    implemented = {
        item["finding_id"]
        for item in remediation["items"]
        if item["remediation_status"] == "implemented"
    }
    assert {"C1", "C2", "NF1", "NF2", "NF4", "NF5"} <= implemented


def test_write_review_progress_handles_empty_directory(tmp_path: Path) -> None:
    reviews_dir = tmp_path / "reviews"
    output_dir = tmp_path / "stages"

    json_path, md_path, progress = write_review_progress(reviews_dir, output_dir)

    assert progress["reviews_total"] == 0
    assert json_path.exists()
    assert md_path.exists()
    assert "No findings recorded." in md_path.read_text(encoding="utf-8")


def test_cli_report_reviews_writes_progress(tmp_path: Path) -> None:
    reviews_dir = tmp_path / "reviews"
    output_dir = tmp_path / "stages"
    reviews_dir.mkdir()
    write_review(reviews_dir / "review.json")

    result = CliRunner().invoke(
        main,
        [
            "report",
            "reviews",
            "--reviews-dir",
            str(reviews_dir),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert (output_dir / "review_progress.json").exists()
    assert (output_dir / "review_progress.md").exists()
    assert "Aggregated 1 review reports" in result.output
