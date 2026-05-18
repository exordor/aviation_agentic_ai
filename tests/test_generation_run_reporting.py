from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.generation_runs import (
    build_generation_run_summary,
    write_generation_run_summary,
)


def write_manifest(path: Path, run_id: str, created_at: str = "2026-05-18T00:00:00+00:00") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "created_at": created_at,
                "output_path": f"data/ontology/generated/{run_id}.ttl",
                "accepted_pages": [0, 1],
                "failed_pages": [{"page": 2, "error": "failed"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_generation_run_summary_aggregates_manifests(tmp_path: Path) -> None:
    write_manifest(tmp_path / "run-a" / "manifest.json", "run-a")
    write_manifest(tmp_path / "run-b" / "manifest.json", "run-b")

    summary = build_generation_run_summary(tmp_path)

    assert summary["runs_total"] == 2
    assert summary["accepted_pages_total"] == 4
    assert summary["failed_pages_total"] == 2
    assert summary["latest_run"]["run_id"] == "run-b"


def test_generation_run_summary_uses_created_at_for_latest(tmp_path: Path) -> None:
    write_manifest(
        tmp_path / "zz-old" / "manifest.json",
        "zz-old",
        created_at="2026-05-18T00:00:00+00:00",
    )
    write_manifest(
        tmp_path / "aa-new" / "manifest.json",
        "aa-new",
        created_at="2026-05-18T01:00:00+00:00",
    )

    summary = build_generation_run_summary(tmp_path)

    assert summary["latest_run"]["run_id"] == "aa-new"


def test_write_generation_run_summary_outputs_reports(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"
    out_dir = tmp_path / "out"
    write_manifest(runs_dir / "run-a" / "manifest.json", "run-a")

    json_path, md_path, summary = write_generation_run_summary(runs_dir, out_dir)

    assert summary["runs_total"] == 1
    assert not Path(summary["runs_dir"]).is_absolute()
    assert not Path(summary["latest_run"]["manifest_path"]).is_absolute()
    assert json_path.exists()
    assert md_path.exists()
    assert "Generation Run Summary" in md_path.read_text(encoding="utf-8")


def test_cli_report_generation_runs(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"
    out_dir = tmp_path / "out"
    write_manifest(runs_dir / "run-a" / "manifest.json", "run-a")

    result = CliRunner().invoke(
        main,
        [
            "report",
            "generation-runs",
            "--runs-dir",
            str(runs_dir),
            "--output-dir",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert (out_dir / "generation_run_summary.json").exists()
    assert "Aggregated 1 generation runs" in result.output
