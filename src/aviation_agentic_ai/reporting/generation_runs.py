from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_none, write_json_report


PATH_FIELDS = {"manifest_path", "output_path", "runs_dir", "pdf_path", "cq_path"}


def _relative_path_fields(value: Any) -> Any:
    if isinstance(value, dict):
        normalized = {}
        for key, item in value.items():
            if key in PATH_FIELDS and isinstance(item, str):
                normalized[key] = project_relative_path(item)
            else:
                normalized[key] = _relative_path_fields(item)
        return normalized
    if isinstance(value, list):
        return [_relative_path_fields(item) for item in value]
    return value


def load_generation_manifests(runs_dir: str | Path) -> list[dict[str, Any]]:
    directory = Path(runs_dir)
    if not directory.exists():
        return []
    manifests: list[dict[str, Any]] = []
    for path in sorted(directory.glob("**/manifest.json")):
        data = read_json_object_or_none(path, wrap_non_object=False)
        if data is not None:
            manifests.append(_relative_path_fields({**data, "manifest_path": str(path)}))
    return manifests


def build_generation_run_summary(runs_dir: str | Path) -> dict[str, Any]:
    manifests = load_generation_manifests(runs_dir)
    manifests = sorted(
        manifests,
        key=lambda item: (str(item.get("created_at", "")), str(item.get("run_id", ""))),
    )
    accepted_pages = sum(len(item.get("accepted_pages", [])) for item in manifests)
    failed_pages = [
        {**failed_page, "run_id": item.get("run_id", "")}
        for item in manifests
        for failed_page in item.get("failed_pages", [])
    ]
    latest = manifests[-1] if manifests else {}
    return {
        "runs_dir": project_relative_path(runs_dir),
        "runs_total": len(manifests),
        "accepted_pages_total": accepted_pages,
        "failed_pages_total": len(failed_pages),
        "failed_pages": failed_pages,
        "latest_run": {
            "run_id": latest.get("run_id", ""),
            "created_at": latest.get("created_at", ""),
            "output_path": latest.get("output_path", ""),
            "accepted_pages": latest.get("accepted_pages", []),
            "failed_pages": latest.get("failed_pages", []),
            "manifest_path": latest.get("manifest_path", ""),
        },
        "runs": [
            {
                "run_id": item.get("run_id", ""),
                "created_at": item.get("created_at", ""),
                "output_path": item.get("output_path", ""),
                "accepted_pages": item.get("accepted_pages", []),
                "failed_pages": item.get("failed_pages", []),
                "manifest_path": item.get("manifest_path", ""),
            }
            for item in manifests
        ],
    }


def write_generation_run_summary_json(summary: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(summary, output_path, sort_keys=False)


def write_generation_run_summary_markdown(summary: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    latest = summary["latest_run"]
    lines = [
        "# Generation Run Summary",
        "",
        f"- Runs: {summary['runs_total']}",
        f"- Accepted pages: {summary['accepted_pages_total']}",
        f"- Failed pages: {summary['failed_pages_total']}",
        f"- Latest run: {latest.get('run_id') or 'None'}",
        f"- Latest output: {latest.get('output_path') or 'None'}",
        "",
        "## Runs",
        "",
    ]
    if summary["runs"]:
        lines.append("| Run ID | Accepted Pages | Failed Pages | Output |")
        lines.append("| --- | ---: | ---: | --- |")
        for item in summary["runs"]:
            lines.append(
                f"| {item['run_id']} | {len(item['accepted_pages'])} | "
                f"{len(item['failed_pages'])} | {item['output_path']} |"
            )
    else:
        lines.append("No generation run manifests found.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_generation_run_summary(
    runs_dir: str | Path, output_dir: str | Path
) -> tuple[Path, Path, dict[str, Any]]:
    summary = build_generation_run_summary(runs_dir)
    output = Path(output_dir)
    json_path = write_generation_run_summary_json(summary, output / "generation_run_summary.json")
    md_path = write_generation_run_summary_markdown(summary, output / "generation_run_summary.md")
    return json_path, md_path, summary
