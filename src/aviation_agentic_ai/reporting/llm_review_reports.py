from __future__ import annotations

import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.evaluation.benchmark_validation import read_benchmark_payload
from aviation_agentic_ai.evaluation.cost_latency import cost_latency_block
from aviation_agentic_ai.evaluation.gold import GoldLabel, load_gold_labels
from aviation_agentic_ai.evaluation.llm_review import (
    DEFAULT_LLM_REVIEW_ROLES,
    LLM_REVIEW_NOT_RUN_STATUS,
    LLM_REVIEW_STATUS,
    ReviewRunner,
    aggregate_review_results,
    agreement_summary,
    llm_runtime_available,
    result_to_dict,
    review_item,
    reviewer_model_name,
)
from aviation_agentic_ai.evaluation.metrics import answer_metrics
from aviation_agentic_ai.evaluation.protocol import build_run_manifest
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.retrieval.hybrid import run_query
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME
from aviation_agentic_ai.retrieval.sufficiency import evaluate_evidence_sufficiency
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report


PROMPT_VERSIONS = {
    "benchmark": "benchmark_llm_review_v1",
    "triple": "triple_semantic_llm_review_v1",
    "graph_path": "graph_path_llm_review_v1",
    "answer_judge": "answer_llm_judge_v1",
}

QueryRunner = Callable[..., dict[str, Any]]


def _read_json(path: str | Path) -> dict[str, Any]:
    return read_json_object_or_empty(path, wrap_non_object=True)


def _write_json(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(result, output_path)


def _write_md(lines: list[str], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def _label_id(label: dict[str, Any]) -> str:
    return str(label.get("cq_id") or label.get("id") or "<missing>")


def _limited(items: list[Any], max_items: int | None) -> list[Any]:
    if max_items is None:
        return items
    return items[: max(0, max_items)]


def _review_metadata_block(
    *,
    command: str,
    max_items: int | None,
    run_llm: bool,
    started: float,
    items_total: int,
) -> dict[str, Any]:
    return {
        "reviewer_type": "llm_judge",
        "reviewer_model": reviewer_model_name(),
        "human_review": False,
        "external_expert_certified": False,
        "aviation_expert_certified": False,
        "score_method": "llm_judge",
        "run_llm_requested": bool(run_llm),
        "llm_runtime_available": llm_runtime_available(),
        "max_items": max_items,
        "items_total": items_total,
        "advisory_boundary": ADVISORY_BOUNDARY,
        "command": command,
        "cost_latency": cost_latency_block(
            elapsed_seconds=perf_counter() - started,
            questions_total=items_total,
        ),
    }


def _benchmark_prompt(label: dict[str, Any], role: str) -> str:
    return (
        "You are reviewing an aviation training benchmark label. You are not a human "
        "reviewer and not an external aviation expert. Use only the supplied fields.\n\n"
        f"Reviewer role: {role}\n"
        "Return strict JSON with keys: decision, confidence, scores, "
        "natural_question_wording, aviation_training_relevance, "
        "answerability_from_phak_ch4, evidence_span_supports_answer_key, ambiguity, "
        "category_correctness, safety_boundary_correctness, recommended_action, "
        "rewritten_question, cited_source_fields, uncertainty_flags, "
        "requires_human_review, rationale.\n\n"
        "Scores must use 0/1/2 where applicable. recommended_action must be one of "
        "keep, rewrite_question, revise_answer_key, revise_evidence_span, "
        "revise_category, remove.\n\n"
        f"Label JSON:\n{json.dumps(label, indent=2, sort_keys=True)}"
    )


def build_benchmark_llm_review(
    gold_labels_path: str | Path,
    *,
    subset_labels_path: str | Path | None = None,
    max_items: int | None = 60,
    roles: tuple[str, ...] = DEFAULT_LLM_REVIEW_ROLES,
    run_llm: bool = True,
    temperature: float = 0.0,
    max_tokens: int = 1200,
    runner: ReviewRunner | None = None,
    command: str = "aviation-ai report benchmark-llm-review",
) -> dict[str, Any]:
    started = perf_counter()
    source_path = subset_labels_path if subset_labels_path and Path(subset_labels_path).exists() else gold_labels_path
    payload = read_benchmark_payload(source_path)
    labels = _limited([item for item in payload.get("labels", []) if isinstance(item, dict)], max_items)
    records: list[dict[str, Any]] = []
    for label in labels:
        item_payload = {
            "label": label,
            "source_path": project_relative_path(source_path),
        }
        for role in roles:
            result = review_item(
                prompt=_benchmark_prompt(label, role),
                item_id=_label_id(label),
                item_type="benchmark_label",
                review_kind="benchmark_llm_review",
                prompt_version=PROMPT_VERSIONS["benchmark"],
                input_payload=item_payload,
                reviewer_role=role,
                temperature=temperature,
                max_tokens=max_tokens,
                runner=runner,
                run_llm=run_llm,
            )
            record = result_to_dict(result)
            record["label"] = label
            records.append(record)
    summary = aggregate_review_results(records)
    consistency = agreement_summary(records)
    return {
        "metadata": {
            **_review_metadata_block(
                command=command,
                max_items=max_items,
                run_llm=run_llm,
                started=started,
                items_total=len(labels),
            ),
            "gold_labels_path": project_relative_path(gold_labels_path),
            "review_input_path": project_relative_path(source_path),
            "roles": list(roles),
            "review_status": summary["review_status"],
        },
        "summary": summary,
        "consistency": consistency,
        "records": records,
    }


def write_benchmark_llm_review_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    summary = result["summary"]
    lines = [
        "# Benchmark LLM Review",
        "",
        "- Review type: model-based LLM judge review, not human review.",
        f"- Reviewer model: `{result['metadata']['reviewer_model']}`",
        f"- Review status: `{result['metadata']['review_status']}`",
        "- Human review: false",
        "- External aviation expert certified: false",
        "- Aviation expert certified: false",
        "",
        "## Summary",
        "",
        f"- Items selected: {result['metadata']['items_total']}",
        f"- Review records: {summary['items_total']}",
        f"- LLM-reviewed records: {summary['llm_reviewed_total']}",
        f"- Not-run records: {summary['llm_review_not_run_total']}",
        f"- Uncertain records: {summary['uncertain_total']}",
        f"- Recommended actions: {summary['recommended_action_counts']}",
        "",
        "## Consistency",
        "",
        f"- Agreement rate: {result['consistency']['agreement_rate']}",
        f"- Contradictions: {result['consistency']['contradiction_count']}",
        f"- Consistency not measured: {result['consistency']['consistency_not_measured']}",
        "",
        "## Notes",
        "",
        "These findings support internal benchmark cleanup and cautious thesis wording. "
        "They do not certify the labels as expert gold.",
    ]
    return _write_md(lines, output_path)


def write_benchmark_llm_review(
    gold_labels_path: str | Path,
    output_dir: str | Path,
    *,
    subset_labels_path: str | Path | None = None,
    max_items: int | None = 60,
    roles: tuple[str, ...] = DEFAULT_LLM_REVIEW_ROLES,
    run_llm: bool = True,
    report_name: str = "benchmark_llm_review",
    runner: ReviewRunner | None = None,
    command: str = "aviation-ai report benchmark-llm-review",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_benchmark_llm_review(
        gold_labels_path,
        subset_labels_path=subset_labels_path,
        max_items=max_items,
        roles=roles,
        run_llm=run_llm,
        runner=runner,
        command=command,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "benchmark_llm_review"
    json_path = _write_json(result, output / f"{stem}.json")
    md_path = write_benchmark_llm_review_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result


def build_benchmark_llm_rewrite_proposals(
    review_path: str | Path,
    *,
    source_gold_path: str | Path | None = None,
) -> dict[str, Any]:
    review = _read_json(review_path)
    proposals = []
    seen: set[str] = set()
    for record in review.get("records", []):
        if not isinstance(record, dict):
            continue
        item_id = str(record.get("item_id"))
        action = str(record.get("decision", {}).get("recommended_action", "keep"))
        if action in {"keep", "not_run"} or item_id in seen:
            continue
        label = record.get("label", {})
        output_fields = record.get("output_fields", {})
        proposals.append(
            {
                "cq_id": item_id,
                "proposal_only": True,
                "recommended_action": action,
                "original_question": label.get("question"),
                "rewritten_question": output_fields.get("rewritten_question")
                or label.get("question"),
                "answer_key": label.get("answer_key"),
                "evidence_spans": deepcopy(label.get("evidence_spans", [])),
                "human_review": False,
                "external_expert_certified": False,
                "aviation_expert_certified": False,
                "use_for_main_claims": False,
                "rationale": record.get("rationale", ""),
            }
        )
        seen.add(item_id)
    return {
        "metadata": {
            "source_review_path": project_relative_path(review_path),
            "source_gold_path": project_relative_path(source_gold_path)
            if source_gold_path
            else None,
            "reviewer_type": "llm_judge",
            "reviewer_model": review.get("metadata", {}).get("reviewer_model", reviewer_model_name()),
            "human_review": False,
            "external_expert_certified": False,
            "aviation_expert_certified": False,
            "proposal_only": True,
            "use_for_main_claims": False,
            "proposals_total": len(proposals),
        },
        "proposals": proposals,
    }


def write_benchmark_llm_rewrite_proposals_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    lines = [
        "# Benchmark LLM Rewrite Proposals",
        "",
        "- Proposal only: true",
        "- Human review: false",
        "- External aviation expert certified: false",
        "- Use for main claims: false unless promoted later.",
        f"- Proposals: {result['metadata']['proposals_total']}",
        "",
    ]
    for proposal in result["proposals"][:50]:
        lines.append(
            f"- `{proposal['cq_id']}` {proposal['recommended_action']}: "
            f"{proposal['rewritten_question']}"
        )
    return _write_md(lines, output_path)


def write_benchmark_llm_rewrite_proposals(
    review_path: str | Path,
    output_dir: str | Path,
    *,
    source_gold_path: str | Path | None = None,
    write_candidate: bool = False,
    candidate_output_path: str | Path | None = None,
    report_name: str = "benchmark_llm_rewrite_proposals",
) -> tuple[Path, Path, Path | None, dict[str, Any]]:
    result = build_benchmark_llm_rewrite_proposals(review_path, source_gold_path=source_gold_path)
    output = Path(output_dir)
    stem = Path(report_name).stem or "benchmark_llm_rewrite_proposals"
    json_path = _write_json(result, output / f"{stem}.json")
    md_path = write_benchmark_llm_rewrite_proposals_markdown(result, output / f"{stem}.md")
    candidate_path = None
    if write_candidate:
        if source_gold_path is None:
            raise ValueError("--write-candidate requires a source gold label file.")
        payload = read_benchmark_payload(source_gold_path)
        proposals_by_id = {proposal["cq_id"]: proposal for proposal in result["proposals"]}
        candidate = deepcopy(payload)
        for label in candidate.get("labels", []):
            proposal = proposals_by_id.get(_label_id(label))
            if proposal and proposal.get("rewritten_question"):
                label["question"] = proposal["rewritten_question"]
                label["llm_rewrite_proposal"] = proposal
        candidate.update(
            {
                "generated_by": f"{result['metadata']['reviewer_model']} model-based rewrite",
                "reviewer_model": result["metadata"]["reviewer_model"],
                "human_review": False,
                "external_expert_certified": False,
                "aviation_expert_certified": False,
                "use_for_main_claims": False,
            }
        )
        candidate_path = _write_json(
            candidate,
            candidate_output_path
            or Path("data/cqs/06_phak_ch4_0.benchmark_v2.llm_rewrite_candidate.gold.json"),
        )
    return json_path, md_path, candidate_path, result


def _triple_prompt(record: dict[str, Any], role: str, chunk_text: str = "") -> str:
    return (
        "Review this KG triple using only the triple, evidence_text, and source chunk. "
        "You are an LLM judge, not a human aviation expert.\n\n"
        f"Reviewer role: {role}\n"
        "Return strict JSON with keys: decision, confidence, scores, subject_correct, "
        "predicate_correct, object_correct, direction_correct, evidence_supports_triple, "
        "relation_too_strong, entity_too_generic, duplicate_or_near_duplicate, "
        "recommended_action, cited_source_fields, uncertainty_flags, "
        "requires_human_review, rationale.\n\n"
        "Use 1/0/uncertain for correctness fields. recommended_action must be one of "
        "keep, revise_predicate, revise_subject, revise_object, reverse_direction, "
        "remove, needs_human_expert.\n\n"
        f"Triple record:\n{json.dumps(record, indent=2, sort_keys=True)}\n\n"
        f"Source chunk excerpt:\n{chunk_text[:2000]}"
    )


def _truthy_score(value: Any) -> bool | None:
    if value in {1, 2, "1", "2", True, "true", "True"}:
        return True
    if value in {0, "0", False, "false", "False"}:
        return False
    return None


def _rate(records: list[dict[str, Any]], key: str) -> float | None:
    values = [
        _truthy_score(record.get("scores", {}).get(key) or record.get("output_fields", {}).get(key))
        for record in records
        if record.get("metadata", {}).get("review_status") == LLM_REVIEW_STATUS
    ]
    known = [value for value in values if value is not None]
    if not known:
        return None
    return round(sum(int(value) for value in known) / len(known), 4)


def _llm_rate_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    reviewed = [
        record
        for record in records
        if record.get("metadata", {}).get("review_status") == LLM_REVIEW_STATUS
    ]
    uncertain = [
        record
        for record in reviewed
        if record.get("uncertainty_flags") or "uncertain" in json.dumps(record).lower()
    ]
    return {
        "llm_subject_correct_rate": _rate(reviewed, "subject_correct"),
        "llm_predicate_correct_rate": _rate(reviewed, "predicate_correct"),
        "llm_object_correct_rate": _rate(reviewed, "object_correct"),
        "llm_direction_correct_rate": _rate(reviewed, "direction_correct"),
        "llm_evidence_support_rate": _rate(reviewed, "evidence_supports_triple"),
        "uncertain_rate": round(len(uncertain) / max(len(reviewed), 1), 4) if reviewed else None,
        "llm_reviewed_total": len(reviewed),
        "human_review": False,
        "external_expert_certified": False,
        "aviation_expert_certified": False,
    }


def build_triple_semantic_llm_review(
    triple_review_sample_path: str | Path,
    *,
    max_items: int | None = 50,
    roles: tuple[str, ...] = DEFAULT_LLM_REVIEW_ROLES,
    run_llm: bool = True,
    runner: ReviewRunner | None = None,
    command: str = "aviation-ai report triple-semantic-llm-review",
) -> dict[str, Any]:
    started = perf_counter()
    sample = _read_json(triple_review_sample_path)
    items = _limited([item for item in sample.get("records", []) if isinstance(item, dict)], max_items)
    records: list[dict[str, Any]] = []
    for item in items:
        triple = item.get("triple", {})
        item_id = str(triple.get("triple_id", ""))
        for role in roles:
            result = review_item(
                prompt=_triple_prompt(item, role),
                item_id=item_id,
                item_type="kg_triple",
                review_kind="triple_semantic_llm_review",
                prompt_version=PROMPT_VERSIONS["triple"],
                input_payload=item,
                reviewer_role=role,
                runner=runner,
                run_llm=run_llm,
            )
            record = result_to_dict(result)
            record["triple"] = triple
            records.append(record)
    return {
        "metadata": {
            **_review_metadata_block(
                command=command,
                max_items=max_items,
                run_llm=run_llm,
                started=started,
                items_total=len(items),
            ),
            "source_review_sample_path": project_relative_path(triple_review_sample_path),
            "roles": list(roles),
            "semantic_correctness_wording": "LLM-estimated semantic correctness",
        },
        "summary": {**aggregate_review_results(records), **_llm_rate_summary(records)},
        "consistency": agreement_summary(records),
        "records": records,
    }


def write_triple_semantic_llm_review_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    summary = result["summary"]
    lines = [
        "# Triple Semantic LLM Review",
        "",
        "- Review type: LLM-estimated semantic correctness, not manual semantic correctness.",
        f"- Reviewer model: `{result['metadata']['reviewer_model']}`",
        "- Human review: false",
        "- External aviation expert certified: false",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| LLM-reviewed records | {summary['llm_reviewed_total']} |",
        f"| Subject correct rate | {summary['llm_subject_correct_rate']} |",
        f"| Predicate correct rate | {summary['llm_predicate_correct_rate']} |",
        f"| Object correct rate | {summary['llm_object_correct_rate']} |",
        f"| Direction correct rate | {summary['llm_direction_correct_rate']} |",
        f"| Evidence support rate | {summary['llm_evidence_support_rate']} |",
        f"| Uncertain rate | {summary['uncertain_rate']} |",
        "",
        "These rates are model estimates and do not make triples expert-verified.",
    ]
    return _write_md(lines, output_path)


def write_triple_semantic_llm_review(
    triple_review_sample_path: str | Path,
    output_dir: str | Path,
    *,
    max_items: int | None = 50,
    run_llm: bool = True,
    report_name: str = "triple_semantic_llm_review",
    runner: ReviewRunner | None = None,
    command: str = "aviation-ai report triple-semantic-llm-review",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_triple_semantic_llm_review(
        triple_review_sample_path,
        max_items=max_items,
        run_llm=run_llm,
        runner=runner,
        command=command,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "triple_semantic_llm_review"
    json_path = _write_json(result, output / f"{stem}.json")
    md_path = write_triple_semantic_llm_review_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result


def _select_graph_path_items(report: dict[str, Any], max_items: int | None) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for scenario_name, scenario in report.get("scenarios", {}).items():
        if not isinstance(scenario, dict):
            continue
        failures_by_cq = {
            str(item.get("cq_id")): item
            for item in scenario.get("failure_cases", [])
            if isinstance(item, dict)
        }
        for record in scenario.get("records", []):
            if not isinstance(record, dict):
                continue
            failure = failures_by_cq.get(str(record.get("cq_id")), {})
            categories = failure.get("failure_categories", [])
            question_type = str(record.get("gold", {}).get("question_type", ""))
            path_metrics = record.get("metrics", {}).get("graph_paths", {})
            if (
                question_type == "relation_causal"
                or "path_recall_at_5" in path_metrics
                or "path_found_but_wrong_chunk" in categories
                or "graph_fusion_dilution" in categories
            ):
                selected.append(
                    {
                        "scenario": scenario_name,
                        "cq_id": record.get("cq_id"),
                        "question": record.get("question"),
                        "question_type": question_type,
                        "failure_categories": categories,
                        "graph_paths": record.get("graph_paths", [])[:5],
                        "retrieved_chunks": record.get("hits", [])[:5],
                        "metrics": record.get("metrics", {}),
                    }
                )
            if max_items is not None and len(selected) >= max_items:
                return selected
    return _limited(selected, max_items)


def _graph_path_prompt(item: dict[str, Any], role: str) -> str:
    return (
        "Review whether these graph paths are relevant and explanatory for the "
        "question. You are an LLM judge, not a human aviation expert.\n\n"
        f"Reviewer role: {role}\n"
        "Return strict JSON with keys: decision, confidence, scores, "
        "path_relevant_to_question, entities_match_question, "
        "relation_chain_supports_answer, evidence_chunks_support_path, "
        "path_is_explanatory, path_is_misleading, recommended_action, "
        "cited_source_fields, uncertainty_flags, requires_human_review, rationale. "
        "Use 1/0/uncertain for path fields. recommended_action must be one of "
        "keep_as_explanation, downweight, remove, needs_human_expert.\n\n"
        f"Graph path item:\n{json.dumps(item, indent=2, sort_keys=True)}"
    )


def build_graph_path_llm_review(
    graph_traversal_report_path: str | Path,
    *,
    max_items: int | None = 50,
    roles: tuple[str, ...] = DEFAULT_LLM_REVIEW_ROLES,
    run_llm: bool = True,
    runner: ReviewRunner | None = None,
    command: str = "aviation-ai report graph-path-llm-review",
) -> dict[str, Any]:
    started = perf_counter()
    report = _read_json(graph_traversal_report_path)
    items = _select_graph_path_items(report, max_items)
    records: list[dict[str, Any]] = []
    for item in items:
        item_id = f"{item['scenario']}::{item['cq_id']}"
        for role in roles:
            result = review_item(
                prompt=_graph_path_prompt(item, role),
                item_id=item_id,
                item_type="graph_path",
                review_kind="graph_path_llm_review",
                prompt_version=PROMPT_VERSIONS["graph_path"],
                input_payload=item,
                reviewer_role=role,
                runner=runner,
                run_llm=run_llm,
            )
            record = result_to_dict(result)
            record["graph_path_item"] = item
            records.append(record)
    reviewed = [
        record
        for record in records
        if record.get("metadata", {}).get("review_status") == LLM_REVIEW_STATUS
    ]
    summary = aggregate_review_results(records)
    summary.update(
        {
            "llm_path_relevance_rate": _rate(reviewed, "path_relevant_to_question"),
            "llm_explanatory_path_rate": _rate(reviewed, "path_is_explanatory"),
            "llm_misleading_path_rate": _rate(reviewed, "path_is_misleading"),
            "by_failure_category": _graph_path_failure_summary(records),
        }
    )
    return {
        "metadata": {
            **_review_metadata_block(
                command=command,
                max_items=max_items,
                run_llm=run_llm,
                started=started,
                items_total=len(items),
            ),
            "graph_traversal_report_path": project_relative_path(graph_traversal_report_path),
            "roles": list(roles),
        },
        "summary": summary,
        "consistency": agreement_summary(records),
        "records": records,
    }


def _graph_path_failure_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        categories = record.get("graph_path_item", {}).get("failure_categories", [])
        if not categories:
            categories = ["no_failure_category"]
        status = record.get("metadata", {}).get("review_status", LLM_REVIEW_NOT_RUN_STATUS)
        for category in categories:
            counts[str(category)][status] += 1
    return {key: dict(value) for key, value in sorted(counts.items())}


def write_graph_path_llm_review_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    summary = result["summary"]
    lines = [
        "# Graph Path LLM Review",
        "",
        "- Review type: model-based graph path relevance review, not final path truth.",
        f"- Reviewer model: `{result['metadata']['reviewer_model']}`",
        "- Human review: false",
        "- External aviation expert certified: false",
        "",
        f"- LLM path relevance rate: {summary['llm_path_relevance_rate']}",
        f"- LLM explanatory path rate: {summary['llm_explanatory_path_rate']}",
        f"- LLM misleading path rate: {summary['llm_misleading_path_rate']}",
        f"- Uncertain rate: {summary['uncertain_rate']}",
        "",
        "## Failure Categories",
        "",
        f"`{json.dumps(summary['by_failure_category'], sort_keys=True)}`",
    ]
    return _write_md(lines, output_path)


def write_graph_path_llm_review(
    graph_traversal_report_path: str | Path,
    output_dir: str | Path,
    *,
    max_items: int | None = 50,
    run_llm: bool = True,
    report_name: str = "graph_path_llm_review",
    runner: ReviewRunner | None = None,
    command: str = "aviation-ai report graph-path-llm-review",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_graph_path_llm_review(
        graph_traversal_report_path,
        max_items=max_items,
        run_llm=run_llm,
        runner=runner,
        command=command,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "graph_path_llm_review"
    json_path = _write_json(result, output / f"{stem}.json")
    md_path = write_graph_path_llm_review_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result


ANSWER_GENERATION_METHODS = (
    ("vector_only", "vector"),
    ("lexical_hybrid", "hybrid"),
    ("sufficiency_aware_hybrid", "hybrid"),
)


def _default_answer_eval_subset_path() -> Path:
    return Path("data/cqs/06_phak_ch4_0.answer_eval_subset.gold.json")


def _questions_from_gold(gold_labels_path: str | Path, max_questions: int | None) -> list[GoldLabel]:
    labels = list(load_gold_labels(gold_labels_path).values())
    return _limited(labels, max_questions)


def _not_run_answer_record(gold: GoldLabel, method: str, reason: str) -> dict[str, Any]:
    return {
        "cq_id": gold.cq_id,
        "question": gold.question,
        "question_type": gold.question_type,
        "method": method,
        "answer_status": "not_run",
        "answer": "",
        "retrieval": {},
        "gold": gold.to_dict(),
        "metrics": {},
        "reason": reason,
    }


def build_answer_generation_benchmark_subset(
    gold_labels_path: str | Path,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    max_questions: int | None = 45,
    run_llm: bool = True,
    query_runner: QueryRunner | None = None,
    command: str = "aviation-ai report answer-generation-benchmark-subset",
) -> dict[str, Any]:
    started = perf_counter()
    labels = _questions_from_gold(gold_labels_path, max_questions)
    records: list[dict[str, Any]] = []
    can_run = run_llm and (query_runner is not None or llm_runtime_available())
    for gold in labels:
        for method, mode in ANSWER_GENERATION_METHODS:
            if not can_run:
                records.append(
                    _not_run_answer_record(
                        gold,
                        method,
                        "LLM runtime or credentials are unavailable.",
                    )
                )
                continue
            try:
                runner = query_runner or run_query
                result = runner(
                    gold.question,
                    mode,
                    chunks_path,
                    kg_path,
                    index_dir,
                    collection_name=collection_name,
                )
                if method == "sufficiency_aware_hybrid":
                    sufficiency = evaluate_evidence_sufficiency(gold.question, result, gold)
                    if sufficiency["decision"] == "abstain":
                        result = {
                            **result,
                            "answer": (
                                "The retrieved PHAK Chapter 4 evidence is insufficient for "
                                "a grounded answer. Use official sources and qualified "
                                "instruction for operational decisions."
                            ),
                            "sufficiency_decision": sufficiency,
                        }
                    else:
                        result = {**result, "sufficiency_decision": sufficiency}
                records.append(
                    {
                        "cq_id": gold.cq_id,
                        "question": gold.question,
                        "question_type": gold.question_type,
                        "method": method,
                        "answer_status": "generated",
                        "answer": result.get("answer", ""),
                        "retrieval": {
                            "fused_chunks": result.get("fused_chunks", []),
                            "graph_triples": result.get("graph_triples", []),
                            "graph_paths": result.get("graph_paths", []),
                        },
                        "gold": gold.to_dict(),
                        "metrics": answer_metrics(result),
                    }
                )
            except Exception as exc:  # pragma: no cover - integration fallback.
                records.append(_not_run_answer_record(gold, method, f"Answer generation failed: {exc}"))
    generated_total = sum(1 for record in records if record["answer_status"] == "generated")
    run_manifest = build_run_manifest(
        "answer_generation_benchmark_subset",
        parameters={"max_questions": max_questions},
        artifacts={
            "gold_labels_path": gold_labels_path,
            "chunks_path": chunks_path,
            "kg_path": kg_path,
            "index_dir": index_dir,
        },
        rebuild_policy={"chunks": False, "indexes": False, "kg": False},
        collection_name=collection_name,
        chunking_strategy="structure_aware",
        command=command,
        llm={"provider": "configured", "model": reviewer_model_name()},
    )
    return {
        "metadata": {
            "run_manifest": run_manifest,
            "gold_labels_path": project_relative_path(gold_labels_path),
            "questions_total": len(labels),
            "methods": [method for method, _mode in ANSWER_GENERATION_METHODS],
            "answers_total": generated_total,
            "records_total": len(records),
            "evaluation_status": "complete" if generated_total else "not_run",
            "human_review": False,
            "external_expert_certified": False,
            "aviation_expert_certified": False,
            "cost_latency": cost_latency_block(
                elapsed_seconds=perf_counter() - started,
                questions_total=len(labels),
                chunks_path=chunks_path,
                kg_path=kg_path,
                index_dir=index_dir,
            ),
        },
        "records": records,
    }


def write_answer_generation_benchmark_subset_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    metadata = result["metadata"]
    generated = Counter(record["method"] for record in result["records"] if record["answer_status"] == "generated")
    lines = [
        "# Answer Generation Benchmark Subset",
        "",
        f"- Questions: {metadata['questions_total']}",
        f"- Generated answers: {metadata['answers_total']}",
        f"- Status: `{metadata['evaluation_status']}`",
        "- Human review: false",
        "- External aviation expert certified: false",
        "",
        "## Generated By Method",
        "",
        f"`{json.dumps(dict(sorted(generated.items())), sort_keys=True)}`",
    ]
    return _write_md(lines, output_path)


def write_answer_generation_benchmark_subset(
    gold_labels_path: str | Path,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    output_dir: str | Path,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    max_questions: int | None = 45,
    run_llm: bool = True,
    report_name: str = "answer_generation_benchmark_subset",
    query_runner: QueryRunner | None = None,
    command: str = "aviation-ai report answer-generation-benchmark-subset",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_answer_generation_benchmark_subset(
        gold_labels_path,
        chunks_path,
        kg_path,
        index_dir,
        collection_name=collection_name,
        max_questions=max_questions,
        run_llm=run_llm,
        query_runner=query_runner,
        command=command,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "answer_generation_benchmark_subset"
    json_path = _write_json(result, output / f"{stem}.json")
    md_path = write_answer_generation_benchmark_subset_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result


def _answer_judge_prompt(record: dict[str, Any], role: str) -> str:
    return (
        "Judge this generated answer against the reference answer and supplied evidence. "
        "You are an LLM judge, not a human aviation expert.\n\n"
        f"Reviewer role: {role}\n"
        "Return strict JSON with keys: decision, confidence, scores, answer_correctness, "
        "answer_relevance, faithfulness_to_retrieved_context, citation_support, "
        "citation_precision, citation_recall, unsafe_operational_advice, "
        "correct_abstention, hallucinated_claims, recommended_action, "
        "cited_source_fields, uncertainty_flags, requires_human_review, rationale.\n\n"
        f"Answer record:\n{json.dumps(record, indent=2, sort_keys=True)[:7000]}"
    )


def build_answer_llm_judge(
    answer_generation_path: str | Path,
    *,
    max_items: int | None = 60,
    roles: tuple[str, ...] = DEFAULT_LLM_REVIEW_ROLES,
    run_llm: bool = True,
    runner: ReviewRunner | None = None,
    command: str = "aviation-ai report answer-llm-judge",
) -> dict[str, Any]:
    started = perf_counter()
    generated = _read_json(answer_generation_path)
    items = _limited(
        [
            item
            for item in generated.get("records", [])
            if isinstance(item, dict) and item.get("answer_status") == "generated"
        ],
        max_items,
    )
    records: list[dict[str, Any]] = []
    for item in items:
        item_id = f"{item['method']}::{item['cq_id']}"
        for role in roles:
            result = review_item(
                prompt=_answer_judge_prompt(item, role),
                item_id=item_id,
                item_type="generated_answer",
                review_kind="answer_llm_judge",
                prompt_version=PROMPT_VERSIONS["answer_judge"],
                input_payload=item,
                reviewer_role=role,
                runner=runner,
                run_llm=run_llm,
            )
            record = result_to_dict(result)
            record["answer_record"] = item
            records.append(record)
    summary = aggregate_review_results(records)
    summary.update(
        {
            "llm_answer_correctness_rate": _rate(records, "answer_correctness"),
            "llm_answer_relevance_rate": _rate(records, "answer_relevance"),
            "llm_faithfulness_rate": _rate(records, "faithfulness_to_retrieved_context"),
            "llm_citation_support_rate": _rate(records, "citation_support"),
        }
    )
    return {
        "metadata": {
            **_review_metadata_block(
                command=command,
                max_items=max_items,
                run_llm=run_llm,
                started=started,
                items_total=len(items),
            ),
            "answer_generation_path": project_relative_path(answer_generation_path),
            "roles": list(roles),
        },
        "summary": summary,
        "consistency": agreement_summary(records),
        "records": records,
    }


def write_answer_llm_judge_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    summary = result["summary"]
    lines = [
        "# Answer LLM Judge",
        "",
        "- Score method: llm_judge",
        "- Human review: false",
        "- External aviation expert certified: false",
        f"- LLM-reviewed records: {summary['llm_reviewed_total']}",
        f"- Answer correctness rate: {summary['llm_answer_correctness_rate']}",
        f"- Answer relevance rate: {summary['llm_answer_relevance_rate']}",
        f"- Faithfulness rate: {summary['llm_faithfulness_rate']}",
        f"- Citation support rate: {summary['llm_citation_support_rate']}",
        "",
        "Model-judge scores are reported separately from deterministic heuristics.",
    ]
    return _write_md(lines, output_path)


def write_answer_llm_judge(
    answer_generation_path: str | Path,
    output_dir: str | Path,
    *,
    max_items: int | None = 60,
    run_llm: bool = True,
    report_name: str = "answer_llm_judge",
    runner: ReviewRunner | None = None,
    command: str = "aviation-ai report answer-llm-judge",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_answer_llm_judge(
        answer_generation_path,
        max_items=max_items,
        run_llm=run_llm,
        runner=runner,
        command=command,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "answer_llm_judge"
    json_path = _write_json(result, output / f"{stem}.json")
    md_path = write_answer_llm_judge_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result


def build_llm_review_consistency(
    *,
    benchmark_review_path: str | Path,
    triple_review_path: str | Path,
    graph_path_review_path: str | Path,
    answer_judge_path: str | Path,
) -> dict[str, Any]:
    reports = {
        "benchmark_llm_review": _read_json(benchmark_review_path),
        "triple_semantic_llm_review": _read_json(triple_review_path),
        "graph_path_llm_review": _read_json(graph_path_review_path),
        "answer_llm_judge": _read_json(answer_judge_path),
    }
    records = [
        {**record, "source_report": name}
        for name, report in reports.items()
        for record in report.get("records", [])
        if isinstance(record, dict)
    ]
    consistency = agreement_summary(records)
    uncertain_total = sum(
        1
        for record in records
        if record.get("uncertainty_flags") or "uncertain" in json.dumps(record).lower()
    )
    consistency.update(
        {
            "records_total": len(records),
            "uncertain_rate": round(uncertain_total / max(len(records), 1), 4)
            if records
            else None,
            "human_review": False,
            "external_expert_certified": False,
            "aviation_expert_certified": False,
        }
    )
    return {
        "metadata": {
            "reviewer_type": "llm_judge",
            "reviewer_model": reviewer_model_name(),
            "human_review": False,
            "external_expert_certified": False,
            "aviation_expert_certified": False,
            "score_method": "llm_judge",
            "source_reports": {
                "benchmark_llm_review": project_relative_path(benchmark_review_path),
                "triple_semantic_llm_review": project_relative_path(triple_review_path),
                "graph_path_llm_review": project_relative_path(graph_path_review_path),
                "answer_llm_judge": project_relative_path(answer_judge_path),
            },
        },
        "summary": consistency,
    }


def write_llm_review_consistency_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    summary = result["summary"]
    lines = [
        "# LLM Review Consistency",
        "",
        "- Review type: role-based model consistency check, not human review.",
        f"- Reviewer model: `{result['metadata']['reviewer_model']}`",
        "- Human review: false",
        "- External aviation expert certified: false",
        "",
        f"- Agreement rate: {summary['agreement_rate']}",
        f"- Contradictions: {summary['contradiction_count']}",
        f"- Uncertain rate: {summary['uncertain_rate']}",
        f"- High-confidence disagreements: {summary['high_confidence_disagreement_count']}",
        f"- Consistency not measured: {summary['consistency_not_measured']}",
        f"- Items not safe for strong claims: {summary['items_not_safe_for_strong_claims']}",
    ]
    return _write_md(lines, output_path)


def write_llm_review_consistency(
    output_dir: str | Path,
    *,
    benchmark_review_path: str | Path,
    triple_review_path: str | Path,
    graph_path_review_path: str | Path,
    answer_judge_path: str | Path,
    report_name: str = "llm_review_consistency",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_llm_review_consistency(
        benchmark_review_path=benchmark_review_path,
        triple_review_path=triple_review_path,
        graph_path_review_path=graph_path_review_path,
        answer_judge_path=answer_judge_path,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "llm_review_consistency"
    json_path = _write_json(result, output / f"{stem}.json")
    md_path = write_llm_review_consistency_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
