from __future__ import annotations

from typing import Any, Iterable

from aviation_agentic_ai.cross_source.qa.answering import AnswerEvidenceCritic
from aviation_agentic_ai.cross_source.supervisor import CrossSourceBuild, answer_from_build


def evaluate_benchmark(
    rows: Iterable[dict[str, Any]],
    *,
    build: CrossSourceBuild,
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    scored = 0
    abstain_matches = 0
    scored_abstain_cases = 0
    critic_failures = 0
    alignment_matches = 0
    scored_alignment_cases = 0

    for index, row in enumerate(rows, start=1):
        source_id = str(row.get("source_id") or "")
        question = str(row.get("question") or "")
        if not source_id or not question:
            raise ValueError(f"Benchmark row {index} requires source_id and question")
        answer = answer_from_build(build, source_id=source_id, question=question)
        critic_errors = AnswerEvidenceCritic().validate(answer)
        critic_failures += int(bool(critic_errors))
        evaluation_status = str(row.get("evaluation_status") or "unscored")
        is_scored = evaluation_status == "automated_regression"
        scored += int(is_scored)
        expected_abstain = row.get("expected_abstain")
        abstain_match: bool | None = None
        if is_scored and isinstance(expected_abstain, bool):
            scored_abstain_cases += 1
            abstain_match = answer.abstain is expected_abstain
            abstain_matches += int(abstain_match)
        expected_alignment = row.get("expected_alignment")
        alignment_match: bool | None = None
        if is_scored and isinstance(expected_alignment, str):
            scored_alignment_cases += 1
            selected_labels = {
                item.selected_target_label
                for item in answer.alignment_explanations
                if item.decision_status.value == "accepted"
            }
            alignment_match = expected_alignment in selected_labels
            alignment_matches += int(alignment_match)
        cases.append(
            {
                "case_id": row.get("case_id") or f"case-{index:03d}",
                "source_id": source_id,
                "question": question,
                "evaluation_status": evaluation_status,
                "answer": answer.model_dump(mode="json"),
                "checks": {
                    "evidence_critic_errors": critic_errors,
                    "expected_abstain_match": abstain_match,
                    "expected_alignment_match": alignment_match,
                },
            }
        )

    total = len(cases)
    return {
        "snapshot_set_id": build.config["snapshot_set_id"],
        "summary": {
            "cases": total,
            "scored_cases": scored,
            "unscored_cases": total - scored,
            "evidence_critic_failures": critic_failures,
            "scored_abstain_cases": scored_abstain_cases,
            "expected_abstain_accuracy": (
                abstain_matches / scored_abstain_cases if scored_abstain_cases else None
            ),
            "scored_alignment_cases": scored_alignment_cases,
            "expected_alignment_accuracy": (
                alignment_matches / scored_alignment_cases
                if scored_alignment_cases
                else None
            ),
        },
        "cases": cases,
    }
