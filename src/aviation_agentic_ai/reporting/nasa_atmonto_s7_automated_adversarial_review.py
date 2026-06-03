from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report

DEFAULT_REPORT_NAME = "nasa_atmonto_s7_automated_adversarial_review"
DEFAULT_PACKET_PATH = Path("reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json")

ROLE_IDS = (
    "evidence_verifier",
    "citation_auditor",
    "cq_contract_validator",
    "ontology_profile_validator",
    "consistency_critic",
)


def build_nasa_atmonto_s7_automated_adversarial_review(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    packet_path: str | Path = DEFAULT_PACKET_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source = _resolve(root, packet_path)
    packet = read_json_object_or_empty(source)
    cases = packet.get("cases", []) if isinstance(packet.get("cases"), list) else []
    reviewed_cases = [_review_case(case) for case in cases if isinstance(case, dict)]
    verdict_counts = Counter(item["automated_verdict"] for item in reviewed_cases)
    role_fail_counts = _role_fail_counts(reviewed_cases)
    case_count = len(reviewed_cases)
    expected_case_count = packet.get("metadata", {}).get("case_count", case_count)
    completed = bool(case_count) and case_count == expected_case_count
    return {
        "source_family": "nasa_atmonto_s7_automated_adversarial_review",
        "status": (
            "automated_consistency_diagnostic_completed"
            if completed
            else "automated_consistency_diagnostic_incomplete"
        ),
        "metadata": {
            "packet_path": project_relative_path(source, root),
            "expected_case_count": expected_case_count,
            "reviewed_case_count": case_count,
            "automated_review_completed": completed,
            "automated_consistency_diagnostic_completed": completed,
            "role_count": len(ROLE_IDS),
            "role_ids": list(ROLE_IDS),
            "human_review_completed": False,
            "external_expert_certified": False,
            "unresolved_conflict_count": 0,
            "accepted_case_count": verdict_counts.get("accepted", 0),
            "flagged_case_count": verdict_counts.get("flagged", 0),
            "rejected_case_count": verdict_counts.get("rejected", 0),
            "verdict_counts": dict(sorted(verdict_counts.items())),
            "role_fail_counts": role_fail_counts,
        },
        "case_reviews": reviewed_cases,
        "claim_boundary": (
            "This is an automated multi-angle consistency diagnostic over the S7 "
            "answer-review packet. It is useful as an internal error-discovery and "
            "claim-boundary check, but it cannot replace human answer review, "
            "external expert certification, or operational decision support."
        ),
    }


def write_nasa_atmonto_s7_automated_adversarial_review_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_atmonto_s7_automated_adversarial_review_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = result["metadata"]
    lines = [
        "# NASA ATMONTO S7 Automated Consistency Diagnostic",
        "",
        "## Boundary",
        "",
        result["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Status: `{result['status']}`",
        f"- Packet: `{metadata['packet_path']}`",
        f"- Expected cases: {metadata['expected_case_count']}",
        f"- Reviewed cases: {metadata['reviewed_case_count']}",
        f"- Automated review completed: `{metadata['automated_review_completed']}`",
        (
            "- Automated consistency diagnostic completed: "
            f"`{metadata['automated_consistency_diagnostic_completed']}`"
        ),
        f"- Diagnostic check modules: `{metadata['role_ids']}`",
        f"- Human review completed: `{metadata['human_review_completed']}`",
        f"- External expert certified: `{metadata['external_expert_certified']}`",
        f"- Unresolved conflicts: {metadata['unresolved_conflict_count']}",
        f"- Accepted cases: {metadata['accepted_case_count']}",
        f"- Flagged cases: {metadata['flagged_case_count']}",
        f"- Rejected cases: {metadata['rejected_case_count']}",
        f"- Verdict counts: `{metadata['verdict_counts']}`",
        f"- Role fail counts: `{metadata['role_fail_counts']}`",
        "",
        "## Diagnostic Checks",
        "",
        "| Check module | Rule |",
        "| --- | --- |",
        "| `evidence_verifier` | Evidence faithfulness is true and unsupported claim rate is zero. |",
        "| `citation_auditor` | Citation precision is exact and at least one valid citation is detected. |",
        "| `cq_contract_validator` | Answer values match the CQ expected answer set and abstention is correct. |",
        "| `ontology_profile_validator` | Returned predicates stay inside the expected profile predicate set. |",
        "| `consistency_critic` | Flags any case rejected by a preceding module. |",
        "",
        "## Flagged Or Rejected Cases",
        "",
        "| Review ID | Verdict | Failed roles | Notes |",
        "| --- | --- | --- | --- |",
    ]
    for item in result["case_reviews"]:
        if item["automated_verdict"] == "accepted":
            continue
        failed_roles = ", ".join(
            role["role"] for role in item["role_reviews"] if role["verdict"] != "pass"
        )
        notes = "; ".join(item["notes"]) if item["notes"] else "n/a"
        lines.append(
            f"| `{item['review_id']}` | `{item['automated_verdict']}` | "
            f"{failed_roles} | {notes} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_atmonto_s7_automated_adversarial_review(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    report_name: str = DEFAULT_REPORT_NAME,
    packet_path: str | Path = DEFAULT_PACKET_PATH,
) -> tuple[Path, Path, dict[str, Any]]:
    output = Path(output_dir)
    result = build_nasa_atmonto_s7_automated_adversarial_review(
        repo_root=repo_root,
        packet_path=packet_path,
    )
    json_path = write_nasa_atmonto_s7_automated_adversarial_review_json(
        result,
        output / f"{report_name}.json",
    )
    md_path = write_nasa_atmonto_s7_automated_adversarial_review_markdown(
        result,
        output / f"{report_name}.md",
    )
    return json_path, md_path, result


def _review_case(case: dict[str, Any]) -> dict[str, Any]:
    role_reviews = [
        _evidence_review(case),
        _citation_review(case),
        _cq_contract_review(case),
        _ontology_profile_review(case),
    ]
    role_reviews.append(_critic_review(role_reviews))
    failed = [role for role in role_reviews if role["verdict"] == "fail"]
    flagged = [role for role in role_reviews if role["verdict"] == "flag"]
    verdict = "rejected" if failed else "flagged" if flagged else "accepted"
    return {
        "review_id": str(case.get("review_id") or ""),
        "source_id": str(case.get("source_id") or ""),
        "template_id": str(case.get("template_id") or ""),
        "priority": str(case.get("priority") or ""),
        "automated_verdict": verdict,
        "role_reviews": role_reviews,
        "notes": [
            role["reason"]
            for role in role_reviews
            if role["verdict"] != "pass" and role.get("reason")
        ],
    }


def _evidence_review(case: dict[str, Any]) -> dict[str, Any]:
    metrics = _metrics(case)
    unsupported = _float(metrics.get("unsupported_claim_rate"), default=1.0)
    passed = metrics.get("evidence_faithfulness") is True and unsupported == 0.0
    return _role_result(
        "evidence_verifier",
        passed,
        "answer is faithful to supplied source chunks and graph triples",
        (
            "evidence_faithfulness is false or unsupported_claim_rate is non-zero "
            f"({unsupported})"
        ),
    )


def _citation_review(case: dict[str, Any]) -> dict[str, Any]:
    metrics = _metrics(case)
    precision = _float(metrics.get("citation_precision"), default=0.0)
    detected = metrics.get("detected_citations", [])
    valid = metrics.get("valid_citations", [])
    passed = precision >= 0.999 and bool(detected) and set(detected).issubset(set(valid))
    return _role_result(
        "citation_auditor",
        passed,
        "detected citations are valid and citation precision is exact",
        (
            "citations are missing, invalid, or imprecise "
            f"(precision={precision}, detected={detected}, valid={valid})"
        ),
    )


def _cq_contract_review(case: dict[str, Any]) -> dict[str, Any]:
    metrics = _metrics(case)
    passed = (
        metrics.get("answer_correctness") is True
        and metrics.get("abstention_correctness") is True
    )
    return _role_result(
        "cq_contract_validator",
        passed,
        "answer values satisfy the CQ expected answer set and abstention contract",
        "answer values do not satisfy the CQ expected answer set or abstention contract",
    )


def _ontology_profile_review(case: dict[str, Any]) -> dict[str, Any]:
    expected_predicates = _expected_predicates(case.get("expected_answer_set", []))
    actual_predicates = {
        str(item.get("predicate") or "")
        for item in case.get("answer_values", [])
        if isinstance(item, dict)
    }
    if case.get("expected_abstention") is True:
        passed = not actual_predicates
    else:
        passed = bool(expected_predicates) and actual_predicates.issubset(expected_predicates)
    return _role_result(
        "ontology_profile_validator",
        passed,
        "answer predicates stay within the expected ontology/profile predicate set",
        (
            "answer predicates exceed the expected profile predicate set "
            f"(actual={sorted(actual_predicates)}, expected={sorted(expected_predicates)})"
        ),
    )


def _critic_review(role_reviews: list[dict[str, Any]]) -> dict[str, Any]:
    failed_roles = [role["role"] for role in role_reviews if role["verdict"] != "pass"]
    return {
        "role": "consistency_critic",
        "verdict": "fail" if failed_roles else "pass",
        "reason": (
            f"critic escalated failed roles: {failed_roles}"
            if failed_roles
            else "critic found no role-level failures"
        ),
    }


def _role_result(role: str, passed: bool, pass_reason: str, fail_reason: str) -> dict[str, Any]:
    return {
        "role": role,
        "verdict": "pass" if passed else "fail",
        "reason": pass_reason if passed else fail_reason,
    }


def _role_fail_counts(case_reviews: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for case in case_reviews:
        for role in case["role_reviews"]:
            if role["verdict"] != "pass":
                counts[role["role"]] += 1
    return dict(sorted(counts.items()))


def _metrics(case: dict[str, Any]) -> dict[str, Any]:
    metrics = case.get("metrics", {})
    return metrics if isinstance(metrics, dict) else {}


def _float(value: Any, *, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _expected_predicates(expected_answer_set: Any) -> set[str]:
    if not isinstance(expected_answer_set, list):
        return set()
    predicates = set()
    for item in expected_answer_set:
        if not isinstance(item, str) or "=" not in item:
            continue
        predicate, _value = item.split("=", 1)
        predicates.add(predicate)
    return predicates


def _resolve(root: Path, path: str | Path) -> Path:
    source = Path(path)
    return source if source.is_absolute() else root / source
