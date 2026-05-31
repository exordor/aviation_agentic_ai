from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import write_json_report


STAGE_INDEX_FILES = {"index.json", "index.md"}


@dataclass(frozen=True)
class ReportArtifact:
    path: Path
    category: str
    artifact_type: str
    format: str
    archived_to: Path | None = None

    def to_dict(self, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
        return {
            "path": project_relative_path(self.path, base=base),
            "category": self.category,
            "artifact_type": self.artifact_type,
            "format": self.format,
            "archived_to": project_relative_path(self.archived_to, base=base)
            if self.archived_to is not None
            else None,
        }


def _classify_report(path: Path) -> str:
    name = path.name
    stem = path.stem
    if name == "generation_runs" or stem == "generation_run_summary":
        return "generation_runs"
    if stem in {"source_scope", "cq_gap_review"}:
        return "source_scope"
    if (
        "chunking_comparison" in stem
        or "hybrid_rag" in stem
        or stem
        in {
            "retrieval_ablation",
            "kg_extraction_comparison",
            "answer_evaluation",
            "robustness_evaluation",
        }
    ):
        return "rag_experiments"
    if "ontology_evaluation" in stem or "boundary_evaluation" in stem:
        return "ontology_evaluation"
    if stem in {"ontology_report", "ontology_stats"}:
        return "ontology_stats"
    if stem == "review_progress":
        return "reviews"
    if stem == "overnight_optimization_report":
        return "stage_summaries"
    return "other"


def _artifact_type(path: Path) -> str:
    if path.is_dir():
        return "directory"
    if path.suffix == ".md":
        return "human_report"
    if path.suffix == ".json":
        return "machine_artifact"
    return "artifact"


def _format(path: Path) -> str:
    return "directory" if path.is_dir() else path.suffix.removeprefix(".") or "unknown"


def _archive_destination(source: Path, stage_dir: Path, archive_dir: Path) -> Path:
    return archive_dir / source.relative_to(stage_dir)


def _unique_destination(destination: Path) -> Path:
    if not destination.exists():
        return destination
    for index in range(1, 1000):
        if destination.is_dir() or not destination.suffix:
            candidate = destination.with_name(f"{destination.name}-{index}")
        else:
            candidate = destination.with_name(
                f"{destination.stem}-{index}{destination.suffix}"
            )
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find a unique archive path for {destination}")


def _direct_stage_artifacts(stage_dir: Path) -> list[Path]:
    if not stage_dir.exists():
        return []
    return [
        path
        for path in sorted(stage_dir.iterdir(), key=lambda item: item.name)
        if path.name not in STAGE_INDEX_FILES and not path.name.startswith(".")
    ]


def _review_artifacts(reviews_dir: Path) -> list[ReportArtifact]:
    if not reviews_dir.exists():
        return []
    artifacts: list[ReportArtifact] = []
    for path in sorted(reviews_dir.glob("*")):
        if path.is_file() and path.suffix in {".json", ".md"}:
            artifacts.append(
                ReportArtifact(
                    path=path,
                    category="reviews",
                    artifact_type=_artifact_type(path),
                    format=_format(path),
                )
            )
    return artifacts


def build_hygiene_plan(
    stage_dir: str | Path,
    archive_root: str | Path,
    reviews_dir: str | Path,
    *,
    archive_date: date | None = None,
    base: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    stage_path = Path(stage_dir)
    archive_day = archive_date or datetime.now(UTC).date()
    archive_path = Path(archive_root) / "stages" / archive_day.isoformat()
    archive_items: list[ReportArtifact] = []
    for source in _direct_stage_artifacts(stage_path):
        destination = _archive_destination(source, stage_path, archive_path)
        archive_items.append(
            ReportArtifact(
                path=source,
                category=_classify_report(source),
                artifact_type=_artifact_type(source),
                format=_format(source),
                archived_to=destination,
            )
        )
    review_items = _review_artifacts(Path(reviews_dir))
    categories: dict[str, list[dict[str, Any]]] = {}
    for item in archive_items + review_items:
        categories.setdefault(item.category, []).append(item.to_dict(base=base))
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "policy": "archive_without_delete",
        "stage_dir": project_relative_path(stage_path, base=base),
        "archive_dir": project_relative_path(archive_path, base=base),
        "reviews_dir": project_relative_path(reviews_dir, base=base),
        "archive_items_total": len(archive_items),
        "review_items_total": len(review_items),
        "archive_items": [item.to_dict(base=base) for item in archive_items],
        "review_items": [item.to_dict(base=base) for item in review_items],
        "categories": categories,
        "final_report_readiness": {
            "stage_index": project_relative_path(stage_path / "index.json", base=base),
            "project_report": project_relative_path(
                Path("reports/final/project_report.md"), base=base
            ),
            "sources": project_relative_path(
                Path("reports/final/project_report_sources.json"), base=base
            ),
            "ready": True,
        },
    }


def _plan_item_paths(item: dict[str, Any], base: Path) -> tuple[Path, Path]:
    source = Path(item["path"])
    destination = Path(item["archived_to"])
    if not source.is_absolute():
        source = base / source
    if not destination.is_absolute():
        destination = base / destination
    return source, destination


def apply_hygiene_plan(plan: dict[str, Any], *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    base_path = Path(base)
    moved: list[dict[str, str]] = []
    for item in plan.get("archive_items", []):
        source, destination = _plan_item_paths(item, base_path)
        if not source.exists():
            continue
        target = _unique_destination(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(source), str(target))
        except FileExistsError:
            # Race: target appeared between _unique_destination and move.
            target = _unique_destination(destination)
            try:
                shutil.move(str(source), str(target))
            except OSError as exc:
                import logging
                logging.getLogger(__name__).warning(
                    "Failed to move %s to %s: %s",
                    project_relative_path(source, base=base_path),
                    project_relative_path(target, base=base_path),
                    exc,
                )
                continue
        except OSError as exc:
            import logging
            logging.getLogger(__name__).warning(
                "Failed to move %s to %s: %s",
                project_relative_path(source, base=base_path),
                project_relative_path(target, base=base_path),
                exc,
            )
            continue
        moved.append(
            {
                "from": project_relative_path(source, base=base_path),
                "to": project_relative_path(target, base=base_path),
            }
        )
    return {**plan, "applied": True, "moved_items": moved}


def write_stage_index_json(index: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(index, output_path)


def write_stage_index_markdown(index: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Stage Report Index",
        "",
        "This directory is the current report dashboard. Detailed stage artifacts are "
        f"archived under `{index['archive_dir']}`.",
        "",
        "## Summary",
        "",
        f"- Archived stage artifacts: {index['archive_items_total']}",
        f"- Review source artifacts: {index['review_items_total']}",
        f"- Archive policy: {index['policy']}",
        "",
        "## Categories",
        "",
    ]
    categories = index.get("categories", {})
    if categories:
        lines.extend(["| Category | Items |", "| --- | ---: |"])
        for category, items in sorted(categories.items()):
            lines.append(f"| {category} | {len(items)} |")
    else:
        lines.append("No stage artifacts found.")
    lines.extend(
        [
            "",
            "## Final Report",
            "",
            f"- Draft: `{index['final_report_readiness']['project_report']}`",
            f"- Sources: `{index['final_report_readiness']['sources']}`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def run_report_hygiene(
    stage_dir: str | Path,
    archive_root: str | Path,
    reviews_dir: str | Path,
    *,
    apply: bool = False,
    archive_date: date | None = None,
    base: str | Path = PROJECT_ROOT,
) -> tuple[Path | None, Path | None, dict[str, Any]]:
    plan = build_hygiene_plan(
        stage_dir,
        archive_root,
        reviews_dir,
        archive_date=archive_date,
        base=base,
    )
    if not apply:
        return None, None, {**plan, "applied": False}
    applied = apply_hygiene_plan(plan, base=base)
    stage_path = Path(stage_dir)
    json_path = write_stage_index_json(applied, stage_path / "index.json")
    md_path = write_stage_index_markdown(applied, stage_path / "index.md")
    return json_path, md_path, applied
