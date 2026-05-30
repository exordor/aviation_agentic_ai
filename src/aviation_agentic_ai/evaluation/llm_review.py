from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict, Field, field_validator

from aviation_agentic_ai.config import load_environment
from aviation_agentic_ai.evaluation.protocol import safe_llm_metadata
from aviation_agentic_ai.utils.json import extract_json_object as _extract_json_object_text


LLM_REVIEWER_TYPE = "llm_judge"
LLM_REVIEW_STATUS = "llm_reviewed_not_human_certified"
LLM_REVIEW_NOT_RUN_STATUS = "llm_review_not_run"
LLM_SCORE_METHOD = "llm_judge"
DEFAULT_LLM_REVIEW_ROLES = (
    "strict_evidence_reviewer",
    "skeptical_aviation_boundary_reviewer",
)
DEFAULT_LLM_REVIEW_LIMITATIONS = (
    "Model-based review is not human review.",
    "Model-based review is not external aviation expert certification.",
    "LLM judges can be biased, inconsistent, or overconfident.",
    "Outputs support internal error discovery and cautious thesis wording only.",
)

ReviewRunner = Callable[[str, float, int], str]


class LLMReviewRubricScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    score: int | float | str | bool | None = None
    scale: str = ""
    rationale: str = ""


class LLMReviewEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cited_source_fields: list[str] = Field(default_factory=list)
    source_excerpt: str = ""


class LLMReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: str = "not_run"
    confidence: float = 0.0
    recommended_action: str = "not_run"
    rationale: str = ""
    uncertainty_flags: list[str] = Field(default_factory=list)
    requires_human_review: bool = False

    @field_validator("confidence")
    @classmethod
    def _confidence_in_range(cls, value: float) -> float:
        return max(0.0, min(1.0, float(value)))


class LLMReviewMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewer_type: str = LLM_REVIEWER_TYPE
    reviewer_model: str
    prompt_version: str
    input_hash: str
    review_run_id: str
    temperature: float
    reviewer_role: str
    human_review: bool = False
    external_expert_certified: bool = False
    aviation_expert_certified: bool = False
    review_status: str = LLM_REVIEW_STATUS
    score_method: str = LLM_SCORE_METHOD
    limitations: list[str] = Field(default_factory=lambda: list(DEFAULT_LLM_REVIEW_LIMITATIONS))

    @field_validator("reviewer_type")
    @classmethod
    def _reviewer_type_is_llm(cls, value: str) -> str:
        if value != LLM_REVIEWER_TYPE:
            raise ValueError("LLM review metadata must use reviewer_type='llm_judge'.")
        return value

    @field_validator("human_review", "external_expert_certified", "aviation_expert_certified")
    @classmethod
    def _certification_flags_are_false(cls, value: bool) -> bool:
        if bool(value):
            raise ValueError("LLM review artifacts cannot mark human/expert certification true.")
        return False


class LLMReviewResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    item_type: str
    reviewer_type: str = LLM_REVIEWER_TYPE
    reviewer_model: str
    prompt_version: str
    decision: LLMReviewDecision
    confidence: float = 0.0
    scores: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""
    output_fields: dict[str, Any] = Field(default_factory=dict)
    evidence: LLMReviewEvidence = Field(default_factory=LLMReviewEvidence)
    cited_source_fields: list[str] = Field(default_factory=list)
    uncertainty_flags: list[str] = Field(default_factory=list)
    requires_human_review: bool = False
    human_review: bool = False
    external_expert_certified: bool = False
    aviation_expert_certified: bool = False
    metadata: LLMReviewMetadata
    raw_response: str = ""
    error: str = ""

    @field_validator("reviewer_type")
    @classmethod
    def _result_reviewer_type_is_llm(cls, value: str) -> str:
        if value != LLM_REVIEWER_TYPE:
            raise ValueError("LLM review result must use reviewer_type='llm_judge'.")
        return value

    @field_validator("human_review", "external_expert_certified", "aviation_expert_certified")
    @classmethod
    def _result_certification_flags_are_false(cls, value: bool) -> bool:
        if bool(value):
            raise ValueError("LLM review results cannot mark human/expert certification true.")
        return False


def stable_json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def input_hash(payload: Any) -> str:
    return hashlib.sha256(stable_json_dumps(payload).encode("utf-8")).hexdigest()


def reviewer_model_name() -> str:
    return safe_llm_metadata().get("model", "unknown")


def llm_runtime_available() -> bool:
    load_environment()
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider not in {"openai", "deepseek", "vllm"}:
        return False
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        return False
    if provider == "deepseek" and not os.getenv("DEEPSEEK_API_KEY"):
        return False
    try:
        import langchain_core.messages  # noqa: F401
        import langchain_openai  # noqa: F401
    except ImportError:
        return False
    return True


def review_run_id(prefix: str, *, created_at: datetime | None = None) -> str:
    timestamp = created_at or datetime.now(UTC)
    return f"{prefix}-{timestamp.strftime('%Y%m%dT%H%M%SZ')}"


def build_review_metadata(
    *,
    review_kind: str,
    prompt_version: str,
    input_payload: Any,
    reviewer_role: str,
    temperature: float,
    review_status: str = LLM_REVIEW_STATUS,
) -> LLMReviewMetadata:
    return LLMReviewMetadata(
        reviewer_model=reviewer_model_name(),
        prompt_version=prompt_version,
        input_hash=input_hash(input_payload),
        review_run_id=review_run_id(review_kind),
        temperature=temperature,
        reviewer_role=reviewer_role,
        review_status=review_status,
    )


def extract_json_object(text: str) -> dict[str, Any]:
    try:
        return _extract_json_object_text(text)
    except ValueError as exc:
        raise ValueError("LLM review response must be a JSON object.") from exc


def invoke_llm_text(prompt: str, temperature: float, max_tokens: int) -> str:
    from langchain_core.messages import HumanMessage

    from aviation_agentic_ai.llm.providers import get_llm

    response = get_llm(temperature=temperature, max_tokens=max_tokens).invoke(
        [HumanMessage(content=prompt)]
    )
    return str(getattr(response, "content", response)).strip()


def _coerce_scores(raw_scores: Any) -> dict[str, Any]:
    if isinstance(raw_scores, dict):
        return raw_scores
    if isinstance(raw_scores, list):
        scores: dict[str, Any] = {}
        for item in raw_scores:
            if isinstance(item, dict) and "name" in item:
                scores[str(item["name"])] = item.get("score")
        return scores
    return {}


def result_from_payload(
    payload: dict[str, Any],
    *,
    item_id: str,
    item_type: str,
    metadata: LLMReviewMetadata,
    raw_response: str = "",
) -> LLMReviewResult:
    scores = _coerce_scores(payload.get("scores", {}))
    rationale = str(payload.get("rationale", payload.get("decision_rationale", "")))
    uncertainty_flags = [str(item) for item in payload.get("uncertainty_flags", [])]
    cited_source_fields = [str(item) for item in payload.get("cited_source_fields", [])]
    confidence = float(payload.get("confidence", 0.0) or 0.0)
    recommended_action = str(payload.get("recommended_action", payload.get("decision", "keep")))
    reserved = {
        "decision",
        "confidence",
        "recommended_action",
        "rationale",
        "decision_rationale",
        "uncertainty_flags",
        "requires_human_review",
        "scores",
        "cited_source_fields",
        "source_excerpt",
    }
    output_fields = {key: value for key, value in payload.items() if key not in reserved}
    decision = LLMReviewDecision(
        decision=str(payload.get("decision", recommended_action)),
        confidence=confidence,
        recommended_action=recommended_action,
        rationale=rationale,
        uncertainty_flags=uncertainty_flags,
        requires_human_review=bool(payload.get("requires_human_review", False)),
    )
    evidence = LLMReviewEvidence(
        cited_source_fields=cited_source_fields,
        source_excerpt=str(payload.get("source_excerpt", ""))[:1000],
    )
    return LLMReviewResult(
        item_id=item_id,
        item_type=item_type,
        reviewer_model=metadata.reviewer_model,
        prompt_version=metadata.prompt_version,
        decision=decision,
        confidence=confidence,
        scores=scores,
        rationale=rationale,
        output_fields=output_fields,
        evidence=evidence,
        cited_source_fields=cited_source_fields,
        uncertainty_flags=uncertainty_flags,
        requires_human_review=decision.requires_human_review,
        metadata=metadata,
        raw_response=raw_response,
    )


def not_run_result(
    *,
    item_id: str,
    item_type: str,
    review_kind: str,
    prompt_version: str,
    input_payload: Any,
    reviewer_role: str,
    reason: str,
    temperature: float = 0.0,
) -> LLMReviewResult:
    metadata = build_review_metadata(
        review_kind=review_kind,
        prompt_version=prompt_version,
        input_payload=input_payload,
        reviewer_role=reviewer_role,
        temperature=temperature,
        review_status=LLM_REVIEW_NOT_RUN_STATUS,
    )
    decision = LLMReviewDecision(
        decision="not_run",
        confidence=0.0,
        recommended_action="not_run",
        rationale=reason,
        uncertainty_flags=["llm_review_not_run"],
        requires_human_review=False,
    )
    return LLMReviewResult(
        item_id=item_id,
        item_type=item_type,
        reviewer_model=metadata.reviewer_model,
        prompt_version=metadata.prompt_version,
        decision=decision,
        confidence=0.0,
        scores={},
        rationale=reason,
        cited_source_fields=[],
        uncertainty_flags=["llm_review_not_run"],
        requires_human_review=False,
        metadata=metadata,
        error=reason,
    )


def review_item(
    *,
    prompt: str,
    item_id: str,
    item_type: str,
    review_kind: str,
    prompt_version: str,
    input_payload: Any,
    reviewer_role: str,
    temperature: float = 0.0,
    max_tokens: int = 1200,
    runner: ReviewRunner | None = None,
    run_llm: bool = True,
) -> LLMReviewResult:
    if not run_llm:
        return not_run_result(
            item_id=item_id,
            item_type=item_type,
            review_kind=review_kind,
            prompt_version=prompt_version,
            input_payload=input_payload,
            reviewer_role=reviewer_role,
            reason="LLM execution disabled by command option.",
            temperature=temperature,
        )
    if runner is None and not llm_runtime_available():
        return not_run_result(
            item_id=item_id,
            item_type=item_type,
            review_kind=review_kind,
            prompt_version=prompt_version,
            input_payload=input_payload,
            reviewer_role=reviewer_role,
            reason="LLM runtime or credentials are unavailable.",
            temperature=temperature,
        )
    metadata = build_review_metadata(
        review_kind=review_kind,
        prompt_version=prompt_version,
        input_payload=input_payload,
        reviewer_role=reviewer_role,
        temperature=temperature,
    )
    try:
        raw_response = (runner or invoke_llm_text)(prompt, temperature, max_tokens)
        payload = extract_json_object(raw_response)
        return result_from_payload(
            payload,
            item_id=item_id,
            item_type=item_type,
            metadata=metadata,
            raw_response=raw_response,
        )
    except Exception as exc:  # pragma: no cover - exercised through integration smoke.
        return not_run_result(
            item_id=item_id,
            item_type=item_type,
            review_kind=review_kind,
            prompt_version=prompt_version,
            input_payload=input_payload,
            reviewer_role=reviewer_role,
            reason=f"LLM review failed: {exc}",
            temperature=temperature,
        )


def result_to_dict(result: LLMReviewResult) -> dict[str, Any]:
    return result.model_dump(mode="json")


def aggregate_review_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    reviewed = [
        item
        for item in results
        if item.get("metadata", {}).get("review_status") == LLM_REVIEW_STATUS
    ]
    not_run = len(results) - len(reviewed)
    uncertain = [
        item
        for item in reviewed
        if item.get("uncertainty_flags") or "uncertain" in stable_json_dumps(item).lower()
    ]
    recommended_actions: dict[str, int] = {}
    for item in reviewed:
        action = str(item.get("decision", {}).get("recommended_action", "<missing>"))
        recommended_actions[action] = recommended_actions.get(action, 0) + 1
    return {
        "items_total": len(results),
        "llm_reviewed_total": len(reviewed),
        "llm_review_not_run_total": not_run,
        "uncertain_total": len(uncertain),
        "uncertain_rate": round(len(uncertain) / max(len(reviewed), 1), 4) if reviewed else None,
        "human_review": False,
        "external_expert_certified": False,
        "aviation_expert_certified": False,
        "score_method": LLM_SCORE_METHOD,
        "review_status": LLM_REVIEW_STATUS if reviewed else LLM_REVIEW_NOT_RUN_STATUS,
        "recommended_action_counts": dict(sorted(recommended_actions.items())),
    }


def agreement_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        grouped.setdefault(str(result.get("item_id")), []).append(result)
    comparable = 0
    agreements = 0
    contradictions = 0
    high_confidence_disagreements = 0
    items_requiring_human_review = 0
    items_not_safe_for_strong_claims = 0
    for item_results in grouped.values():
        reviewed = [
            item
            for item in item_results
            if item.get("metadata", {}).get("review_status") == LLM_REVIEW_STATUS
        ]
        if any(item.get("requires_human_review") for item in item_results):
            items_requiring_human_review += 1
        if not reviewed:
            items_not_safe_for_strong_claims += 1
            continue
        if len(reviewed) < 2:
            items_not_safe_for_strong_claims += 1
            continue
        comparable += 1
        actions = {
            str(item.get("decision", {}).get("recommended_action", ""))
            for item in reviewed
        }
        if len(actions) == 1:
            agreements += 1
        else:
            contradictions += 1
            if any(float(item.get("confidence", 0.0) or 0.0) >= 0.8 for item in reviewed):
                high_confidence_disagreements += 1
            items_not_safe_for_strong_claims += 1
    return {
        "reviewed_item_groups": len(grouped),
        "comparable_item_groups": comparable,
        "agreement_rate": round(agreements / max(comparable, 1), 4) if comparable else None,
        "contradiction_count": contradictions,
        "high_confidence_disagreement_count": high_confidence_disagreements,
        "items_requiring_human_review_even_if_no_human_available": items_requiring_human_review,
        "items_not_safe_for_strong_claims": items_not_safe_for_strong_claims,
        "consistency_not_measured": comparable == 0,
        "human_review": False,
        "external_expert_certified": False,
        "aviation_expert_certified": False,
    }
