from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REQUIRED_FINDING_FIELDS = {
    "id",
    "area",
    "severity",
    "title",
    "evidence",
    "impact",
    "recommendation",
    "status",
}
REQUIRED_ACTION_FIELDS = {"id", "finding_ids", "priority", "title", "target", "status"}
VALID_SEVERITIES = {"high", "medium", "low"}
VALID_PRIORITIES = {"P0", "P1", "P2"}
ADVERSARIAL_REQUIRED_FIELDS = {
    "round",
    "subagent_findings",
    "must_fix",
    "should_fix",
    "nice_to_have",
    "unsafe_claims",
    "manual_review_dependencies",
    "recommended_iterations",
    "acceptance_criteria",
}


def validate_adversarial_review_report(report: dict[str, Any]) -> dict[str, Any]:
    """Validate the thesis adversarial-review schema without mixing it into action progress."""
    missing = ADVERSARIAL_REQUIRED_FIELDS - report.keys()
    if missing:
        raise ValueError(f"Adversarial review missing required fields: {sorted(missing)}")
    if not isinstance(report["subagent_findings"], list):
        raise ValueError("Adversarial review `subagent_findings` must be a list.")
    if not report["subagent_findings"]:
        raise ValueError("Adversarial review must contain at least one subagent finding.")
    for index, finding in enumerate(report["subagent_findings"], start=1):
        if not isinstance(finding, dict):
            raise ValueError(f"Subagent finding {index} must be an object.")
        for key in ("subagent", "role", "must_fix", "should_fix", "nice_to_have"):
            if key not in finding:
                raise ValueError(f"Subagent finding {index} missing `{key}`.")
    return report


def load_adversarial_review_report(path: str | Path) -> dict[str, Any]:
    report_path = Path(path)
    data = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected adversarial review object: {report_path}")
    return validate_adversarial_review_report(data)


def load_review_report(path: str | Path) -> dict[str, Any]:
    report_path = Path(path)
    data = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected review report object: {report_path}")
    for key in ("review_id", "title", "findings", "actions"):
        if key not in data:
            raise ValueError(f"Missing required review report field '{key}': {report_path}")
    if not isinstance(data["findings"], list):
        raise ValueError(f"Expected findings list: {report_path}")
    if not isinstance(data["actions"], list):
        raise ValueError(f"Expected actions list: {report_path}")

    for finding in data["findings"]:
        if not isinstance(finding, dict):
            raise ValueError(f"Expected finding object: {report_path}")
        missing = REQUIRED_FINDING_FIELDS - finding.keys()
        if missing:
            raise ValueError(f"Finding {finding.get('id', '<unknown>')} missing {sorted(missing)}")
        if finding["severity"] not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity for finding {finding['id']}: {finding['severity']}")

    for action in data["actions"]:
        if not isinstance(action, dict):
            raise ValueError(f"Expected action object: {report_path}")
        missing = REQUIRED_ACTION_FIELDS - action.keys()
        if missing:
            raise ValueError(f"Action {action.get('id', '<unknown>')} missing {sorted(missing)}")
        if action["priority"] not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority for action {action['id']}: {action['priority']}")
    return data


def load_review_reports(reviews_dir: str | Path) -> list[dict[str, Any]]:
    directory = Path(reviews_dir)
    if not directory.exists():
        return []
    reports: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        if path.name == "review_progress.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and ADVERSARIAL_REQUIRED_FIELDS <= data.keys():
            validate_adversarial_review_report(data)
            continue
        reports.append(load_review_report(path))
    return reports


def aggregate_review_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    for report in reports:
        review_id = report["review_id"]
        for finding in report["findings"]:
            findings.append({**finding, "review_id": review_id})
        for action in report["actions"]:
            actions.append({**action, "review_id": review_id})

    severity_counts = Counter(finding["severity"] for finding in findings)
    finding_status_counts = Counter(finding["status"] for finding in findings)
    action_status_counts = Counter(action["status"] for action in actions)
    area_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for finding in findings:
        area_counts[finding["area"]][finding["severity"]] += 1
        area_counts[finding["area"]]["total"] += 1

    open_findings = [finding for finding in findings if finding["status"] != "closed"]
    open_actions = [action for action in actions if action["status"] != "done"]
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    open_actions.sort(key=lambda item: (priority_order.get(item["priority"], 9), item["id"]))

    return {
        "reviews_total": len(reports),
        "findings_total": len(findings),
        "actions_total": len(actions),
        "severity_counts": dict(sorted(severity_counts.items())),
        "finding_status_counts": dict(sorted(finding_status_counts.items())),
        "action_status_counts": dict(sorted(action_status_counts.items())),
        "area_counts": {
            area: dict(sorted(counter.items())) for area, counter in sorted(area_counts.items())
        },
        "open_findings": open_findings,
        "open_actions": open_actions,
    }


def write_review_progress_json(progress: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(progress, indent=2) + "\n", encoding="utf-8")
    return path


def write_review_progress_markdown(progress: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Review Progress",
        "",
        f"- Review reports: {progress['reviews_total']}",
        f"- Findings: {progress['findings_total']}",
        f"- Actions: {progress['actions_total']}",
        "",
        "## Severity Counts",
        "",
    ]
    if progress["severity_counts"]:
        for severity in ("high", "medium", "low"):
            lines.append(f"- {severity}: {progress['severity_counts'].get(severity, 0)}")
    else:
        lines.append("- No findings recorded.")

    lines.extend(["", "## Area Summary", ""])
    if progress["area_counts"]:
        lines.append("| Area | High | Medium | Low | Total |")
        lines.append("| --- | ---: | ---: | ---: | ---: |")
        for area, counts in progress["area_counts"].items():
            lines.append(
                f"| {area} | {counts.get('high', 0)} | {counts.get('medium', 0)} | "
                f"{counts.get('low', 0)} | {counts.get('total', 0)} |"
            )
    else:
        lines.append("No review areas recorded.")

    lines.extend(["", "## Open Actions", ""])
    if progress["open_actions"]:
        lines.append("| Priority | Action | Target | Status | Review |")
        lines.append("| --- | --- | --- | --- | --- |")
        for action in progress["open_actions"]:
            lines.append(
                f"| {action['priority']} | {action['title']} | {action['target']} | "
                f"{action['status']} | {action['review_id']} |"
            )
    else:
        lines.append("No open actions.")

    lines.extend(["", "## Open Findings", ""])
    if progress["open_findings"]:
        lines.append("| Severity | Area | Finding | Status | Review |")
        lines.append("| --- | --- | --- | --- | --- |")
        for finding in progress["open_findings"]:
            lines.append(
                f"| {finding['severity']} | {finding['area']} | {finding['title']} | "
                f"{finding['status']} | {finding['review_id']} |"
            )
    else:
        lines.append("No open findings.")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_review_progress(
    reviews_dir: str | Path, output_dir: str | Path
) -> tuple[Path, Path, dict[str, Any]]:
    reports = load_review_reports(reviews_dir)
    progress = aggregate_review_reports(reports)
    output = Path(output_dir)
    json_path = write_review_progress_json(progress, output / "review_progress.json")
    md_path = write_review_progress_markdown(progress, output / "review_progress.md")
    return json_path, md_path, progress
