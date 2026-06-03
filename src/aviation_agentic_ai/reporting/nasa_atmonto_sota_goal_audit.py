from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report

DEFAULT_REPORT_NAME = "nasa_atmonto_sota_goal_audit"


SOTA_REQUIREMENTS: tuple[dict[str, Any], ...] = (
    {
        "id": "R1",
        "requirement": "Literature-derived SOTA criteria are consolidated.",
        "status": "satisfied",
        "evidence": [
            "reports/stages/agentic_ontology_graphrag_mainline_literature_search.md",
            "reports/stages/sota_comparison_matrix.md",
            "reports/stages/domain_agnostic_ontology_kg_graphrag_methodology_roadmap.md",
        ],
        "limitation": "The mapping is thesis-scoped and should not be treated as a full systematic review.",
    },
    {
        "id": "R2",
        "requirement": "The ATCSCC data source and event-centric extraction target are explicit.",
        "status": "satisfied",
        "evidence": [
            "reports/stages/atcscc_data_format_and_processing_flow.md",
            "reports/stages/atcscc_event_centric_extraction_framing.md",
            "reports/stages/atcscc_source_brief.md",
        ],
        "limitation": "The source family is retrospective ATCSCC advisories, not live operations.",
    },
    {
        "id": "R3",
        "requirement": "NASA ATMONTO is used as an application-profile constraint, not full truth.",
        "status": "satisfied",
        "evidence": [
            "reports/stages/atcscc_ontology_profile_overview.md",
            "data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json",
            "reports/stages/nasa_atmonto_rejection_adjudication.md",
        ],
        "limitation": "Completeness and correctness are profile-relative and CQ-relative.",
    },
    {
        "id": "R4",
        "requirement": "Ontology-guided KG extraction is scored with schema and semantic layers separated.",
        "status": "satisfied",
        "evidence": [
            "reports/stages/nasa_atmonto_formal_experiment_scoring.json",
            "reports/stages/nasa_atmonto_prediction_output_validation.json",
            "reports/stages/nasa_atmonto_cq_evaluation.md",
        ],
        "limitation": "S4 is the current strongest scored extraction system; not all LLM systems perform well.",
    },
    {
        "id": "R5",
        "requirement": "Multi-agent artifact contract is executable enough to drive S5/S6 diagnostics.",
        "status": "satisfied",
        "evidence": [
            "reports/stages/atcscc_agentic_artifact_contract.md",
            "reports/stages/nasa_atmonto_agentic_loop.md",
            "reports/stages/nasa_atmonto_s5_s6_agentic_loop.md",
            "reports/stages/nasa_atmonto_s5_s6_independent_agentic_run.md",
            "reports/stages/nasa_atmonto_s5_s6_live_agentic_pilot.md",
            "reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md",
        ],
        "limitation": (
            "Live S5/S6 evidence is still extraction-layer evidence; answer-layer "
            "review and cross-domain transfer remain separate claims."
        ),
    },
    {
        "id": "R6",
        "requirement": "Graph-use gate, token-matched retrieval, and graph health are evaluated.",
        "status": "mostly_satisfied",
        "evidence": [
            "reports/stages/atcscc_graph_use_plan.md",
            "reports/stages/nasa_atmonto_s7_retrieval.md",
            "reports/stages/nasa_atmonto_s7_graph_health.md",
        ],
        "limitation": "Graph health is diagnostic evidence, not certification of semantic truth.",
    },
    {
        "id": "R7",
        "requirement": "Answer generation and failure analysis are source-bounded and reported.",
        "status": "mostly_satisfied",
        "evidence": [
            "reports/stages/nasa_atmonto_s7_answer_generation.md",
            "reports/stages/nasa_atmonto_s7_llm_answer_generation.md",
            "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.md",
            "reports/stages/nasa_atmonto_s7_answer_review_worksheet.html",
            "reports/stages/nasa_atmonto_s7_answer_review_protocol.md",
            "reports/stages/nasa_atmonto_s7_answer_review_import.md",
            "reports/stages/nasa_atmonto_s7_answer_review_decisions.md",
            "reports/stages/nasa_atmonto_s7_candidate_adjudication.md",
            "reports/stages/nasa_atmonto_s7_profile_decision.md",
        ],
        "limitation": (
            "A broad 60-case reviewer packet, worksheet, protocol, import status, "
            "and decision-status report exist, but external human/expert decisions "
            "must be recorded before this layer is complete."
        ),
    },
    {
        "id": "R8",
        "requirement": "Completeness, correctness, limitations, and story claims are thesis-ready.",
        "status": "mostly_satisfied",
        "evidence": [
            "reports/stages/current_pipeline_sota_gap_audit.md",
            "reports/stages/thesis_experiment_dashboard.md",
            "reports/stages/nasa_atmonto_experiment_chapter_draft.md",
        ],
        "limitation": "The final thesis should keep the claim wording profile-relative and retrospective.",
    },
    {
        "id": "R9",
        "requirement": "The method can be described as domain-independent and transferable.",
        "status": "mostly_satisfied",
        "evidence": [
            "reports/stages/domain_agnostic_ontology_kg_graphrag_methodology_roadmap.md",
            "reports/stages/nasa_bga_domain_transfer_pilot.md",
            "templates/agentic_artifact_contract.md",
        ],
        "limitation": (
            "A bounded NASA BGA second-source-family pilot exists, but it is "
            "concept-centric, seed-labelled, and not a full cross-domain "
            "GraphRAG answer-generation benchmark."
        ),
    },
)


def build_nasa_atmonto_sota_goal_audit(
    *,
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    root = Path(repo_root)
    requirements = [_requirement_status(root, item) for item in SOTA_REQUIREMENTS]
    scoring = read_json_object_or_empty(root / "reports/stages/nasa_atmonto_formal_experiment_scoring.json")
    s5_s6 = read_json_object_or_empty(root / "reports/stages/nasa_atmonto_s5_s6_agentic_loop.json")
    s5_s6_independent = read_json_object_or_empty(
        root / "reports/stages/nasa_atmonto_s5_s6_independent_agentic_run.json"
    )
    s5_s6_live = read_json_object_or_empty(
        root / "reports/stages/nasa_atmonto_s5_s6_live_agentic_pilot.json"
    )
    s5_s6_live_full = read_json_object_or_empty(
        root / "reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.json"
    )
    s7_llm = read_json_object_or_empty(root / "reports/stages/nasa_atmonto_s7_llm_answer_generation.json")
    s7_broad_review = read_json_object_or_empty(
        root / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json"
    )
    s7_review_decisions = read_json_object_or_empty(
        root / "reports/stages/nasa_atmonto_s7_answer_review_decisions.json"
    )
    second_domain_transfer = read_json_object_or_empty(
        root / "reports/stages/nasa_bga_domain_transfer_pilot.json"
    )
    status_counts: dict[str, int] = {}
    for item in requirements:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
    remaining_blockers = _remaining_blockers(
        s5_s6_live_full,
        s7_review_decisions,
        second_domain_transfer,
    )
    metadata = {
        "requirement_count": len(requirements),
        "status_counts": dict(sorted(status_counts.items())),
        "formal_scoring_status": scoring.get("status"),
        "s5_s6_status": s5_s6.get("status"),
        "s5_s6_independent_status": s5_s6_independent.get("status"),
        "s5_s6_live_pilot_status": s5_s6_live.get("status"),
        "s5_s6_live_full_run_status": s5_s6_live_full.get("status"),
        "s7_llm_status": s7_llm.get("status"),
        "s7_broad_review_packet_status": s7_broad_review.get("status"),
        "s7_broad_review_case_count": s7_broad_review.get("metadata", {}).get("case_count"),
        "s7_answer_review_decision_status": s7_review_decisions.get("status"),
        "s7_answer_review_completed_case_count": s7_review_decisions.get("metadata", {}).get(
            "completed_case_count"
        ),
        "s7_answer_review_human_completed": s7_review_decisions.get("metadata", {}).get(
            "human_review_completed"
        ),
        "second_domain_transfer_status": second_domain_transfer.get("status"),
        "second_domain_transfer_domain": second_domain_transfer.get("metadata", {}).get(
            "transfer_domain"
        ),
    }
    completion_gate = _completion_gate(requirements, metadata, remaining_blockers)
    return {
        "source_family": "nasa_atmonto_sota_goal_audit",
        "status": "sota_goal_audit_created",
        "completion_claim": (
            "sota_goal_completed" if completion_gate["passed"] else "active_not_complete"
        ),
        "metadata": metadata,
        "requirements": requirements,
        "remaining_blockers": remaining_blockers,
        "completion_gate": completion_gate,
        "claim_safe_summary": (
            "The current project is SOTA-comparable as a layered retrospective ATCSCC "
            "case study, but it is not complete enough for claims of universal GraphRAG "
            "superiority, full ATMONTO coverage, operational readiness, or domain-general "
            "validation."
        ),
    }


def write_nasa_atmonto_sota_goal_audit_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_atmonto_sota_goal_audit_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO SOTA Goal Completion Audit",
        "",
        "## Completion Claim",
        "",
        f"- Goal status: `{result['completion_claim']}`",
        f"- Requirement count: {result['metadata']['requirement_count']}",
        f"- Status counts: {_format_status_counts(result['metadata']['status_counts'])}",
        f"- Formal scoring status: `{result['metadata']['formal_scoring_status']}`",
        f"- S5/S6 status: `{result['metadata']['s5_s6_status']}`",
        f"- Independent S5/S6 status: `{result['metadata']['s5_s6_independent_status']}`",
        f"- Live S5/S6 pilot status: `{result['metadata']['s5_s6_live_pilot_status']}`",
        f"- Live S5/S6 full-run status: `{result['metadata']['s5_s6_live_full_run_status']}`",
        f"- S7 LLM status: `{result['metadata']['s7_llm_status']}`",
        f"- S7 broad review packet status: `{result['metadata']['s7_broad_review_packet_status']}`",
        f"- S7 broad review packet cases: {result['metadata']['s7_broad_review_case_count']}",
        f"- S7 answer review decision status: `{result['metadata']['s7_answer_review_decision_status']}`",
        f"- S7 answer review completed cases: {result['metadata']['s7_answer_review_completed_case_count']}",
        f"- S7 answer review human completed: `{result['metadata']['s7_answer_review_human_completed']}`",
        f"- Second-domain transfer status: `{result['metadata']['second_domain_transfer_status']}`",
        f"- Second-domain transfer domain: {result['metadata']['second_domain_transfer_domain']}",
        f"- Completion gate passed: `{result['completion_gate']['passed']}`",
        "",
        "## Requirement Evidence",
        "",
        "| ID | Status | Requirement | Evidence coverage | Limitation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in result["requirements"]:
        coverage = f"{item['present_evidence_count']}/{item['evidence_count']}"
        lines.append(
            f"| `{item['id']}` | `{item['status']}` | {item['requirement']} | "
            f"{coverage} | {item['limitation']} |"
        )
    lines.extend(["", "## Evidence Index", ""])
    for item in result["requirements"]:
        lines.append(f"### {item['id']}: {item['requirement']}")
        for entry in item["evidence"]:
            marker = "present" if entry["present"] else "missing"
            lines.append(f"- `{marker}` `{entry['path']}`")
        if item["missing_evidence"]:
            missing = ", ".join(f"`{path}`" for path in item["missing_evidence"])
            lines.append(f"- Missing evidence: {missing}")
        lines.append("")
    lines.extend(["", "## Completion Gate", ""])
    lines.extend(
        [
            "| Criterion | Passed | Expected | Observed |",
            "| --- | --- | --- | --- |",
        ]
    )
    for criterion in result["completion_gate"]["criteria"]:
        lines.append(
            f"| `{criterion['id']}` | `{criterion['passed']}` | "
            f"{criterion['expected']} | {criterion['observed']} |"
        )
    lines.append("")
    if result["completion_gate"]["failed_criteria"]:
        failed = ", ".join(
            f"`{criterion}`" for criterion in result["completion_gate"]["failed_criteria"]
        )
        lines.append(f"- Failed criteria: {failed}")
    else:
        lines.append("- Failed criteria: none")
    lines.extend(["", "## Remaining Blockers", ""])
    lines.extend(f"- {blocker}" for blocker in result["remaining_blockers"])
    lines.extend(["", "## Claim-Safe Summary", "", result["claim_safe_summary"], ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_atmonto_sota_goal_audit(
    *,
    output_dir: str | Path,
    report_name: str = DEFAULT_REPORT_NAME,
    repo_root: str | Path = PROJECT_ROOT,
) -> tuple[Path, Path, dict[str, Any]]:
    output = Path(output_dir)
    result = build_nasa_atmonto_sota_goal_audit(repo_root=repo_root)
    json_path = write_nasa_atmonto_sota_goal_audit_json(result, output / f"{report_name}.json")
    md_path = write_nasa_atmonto_sota_goal_audit_markdown(result, output / f"{report_name}.md")
    return json_path, md_path, result


def _requirement_status(root: Path, item: dict[str, Any]) -> dict[str, Any]:
    evidence = [
        {
            "path": path,
            "present": (root / path).exists(),
        }
        for path in item["evidence"]
    ]
    return {
        **item,
        "evidence": evidence,
        "evidence_count": len(evidence),
        "present_evidence_count": sum(1 for entry in evidence if entry["present"]),
        "missing_evidence": [entry["path"] for entry in evidence if not entry["present"]],
    }


def _remaining_blockers(
    s5_s6_live_full: dict[str, Any],
    s7_review_decisions: dict[str, Any],
    second_domain_transfer: dict[str, Any],
) -> list[str]:
    blockers = []
    if s5_s6_live_full.get("status") != "s5_s6_live_agentic_full_run_scored":
        blockers.append(
            "A full 100-record live LLM extractor/validator/critic/refiner S5/S6 run is not yet complete."
        )
    if s7_review_decisions.get("metadata", {}).get("human_review_completed") is not True:
        blockers.append("External human/expert answer-review decisions are not yet complete.")
    if second_domain_transfer.get("status") != "second_domain_transfer_pilot_created":
        blockers.append("Second-domain transfer is not yet executed.")
    return blockers


def _completion_gate(
    requirements: list[dict[str, Any]],
    metadata: dict[str, Any],
    remaining_blockers: list[str],
) -> dict[str, Any]:
    missing_evidence = [
        path
        for requirement in requirements
        for path in requirement["missing_evidence"]
    ]
    criteria = [
        _criterion("all_evidence_present", not missing_evidence, "no missing evidence", missing_evidence),
        _criterion("no_remaining_blockers", not remaining_blockers, "[]", remaining_blockers),
        _criterion(
            "formal_scoring_scored",
            metadata.get("formal_scoring_status") == "scored",
            "`scored`",
            metadata.get("formal_scoring_status"),
        ),
        _criterion(
            "live_s5_s6_full_run_scored",
            metadata.get("s5_s6_live_full_run_status") == "s5_s6_live_agentic_full_run_scored",
            "`s5_s6_live_agentic_full_run_scored`",
            metadata.get("s5_s6_live_full_run_status"),
        ),
        _criterion(
            "s7_llm_answer_generation_evaluated",
            metadata.get("s7_llm_status") == "s7_llm_answer_generation_evaluated",
            "`s7_llm_answer_generation_evaluated`",
            metadata.get("s7_llm_status"),
        ),
        _criterion(
            "s7_broad_review_packet_60_cases",
            metadata.get("s7_broad_review_packet_status") == "broad_answer_review_packet_created"
            and metadata.get("s7_broad_review_case_count") == 60,
            "`broad_answer_review_packet_created` with 60 cases",
            {
                "status": metadata.get("s7_broad_review_packet_status"),
                "case_count": metadata.get("s7_broad_review_case_count"),
            },
        ),
        _criterion(
            "s7_answer_review_completed",
            metadata.get("s7_answer_review_decision_status") == "s7_answer_review_decisions_completed"
            and metadata.get("s7_answer_review_completed_case_count") == 60
            and metadata.get("s7_answer_review_human_completed") is True,
            "`s7_answer_review_decisions_completed` with 60 human-reviewed cases",
            {
                "status": metadata.get("s7_answer_review_decision_status"),
                "completed_case_count": metadata.get("s7_answer_review_completed_case_count"),
                "human_review_completed": metadata.get("s7_answer_review_human_completed"),
            },
        ),
        _criterion(
            "second_domain_transfer_pilot_created",
            metadata.get("second_domain_transfer_status") == "second_domain_transfer_pilot_created",
            "`second_domain_transfer_pilot_created`",
            metadata.get("second_domain_transfer_status"),
        ),
    ]
    return {
        "passed": all(criterion["passed"] for criterion in criteria),
        "failed_criteria": [
            criterion["id"] for criterion in criteria if not criterion["passed"]
        ],
        "criteria": criteria,
    }


def _criterion(id_: str, passed: bool, expected: Any, observed: Any) -> dict[str, Any]:
    return {
        "id": id_,
        "passed": bool(passed),
        "expected": _compact(expected),
        "observed": _compact(observed),
    }


def _compact(value: Any) -> str:
    if value in (None, ""):
        return "n/a"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "[]"
    if isinstance(value, dict):
        return ", ".join(f"{key}={item}" for key, item in value.items())
    return str(value)


def _format_status_counts(status_counts: dict[str, int]) -> str:
    return ", ".join(f"`{status}`={count}" for status, count in status_counts.items())
