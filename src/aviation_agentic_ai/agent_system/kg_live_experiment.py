"""Raw/parsed artifacts for a real-provider ontology KG build."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import ModelCallRecord, StrictModel
from aviation_agentic_ai.agent_system.runtime import (
    FROZEN_MODEL,
    FROZEN_MAX_OUTPUT_TOKENS,
    FROZEN_PROVIDER,
    FROZEN_TEMPERATURE,
)
from aviation_agentic_ai.agent_system.tool_model import (
    ToolPhase,
    capture_tool_model_calls,
)
from aviation_agentic_ai.utils.identifiers import stable_id


ExperimentMode = Literal["offline_software_test", "live_experiment"]
ExtractionStage = Literal["ner", "re"]
DEFAULT_KG_LIVE_EXPERIMENT_DIR = "data/evaluation_runs/agent_system/ontology-kg-live-v1"


class KGProviderCall(StrictModel):
    call_id: str = Field(min_length=1)
    trial_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    stage: ExtractionStage
    phase: str = Field(min_length=1)
    recorded_at: str = Field(min_length=1)
    role: str = Field(min_length=1)
    provider: str | None = None
    model: str | None = None
    prompt_set_id: str | None = None
    prompt_version: str | None = None
    temperature: float | None = None
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cache_read_tokens: int = Field(default=0, ge=0)
    cache_creation_tokens: int = Field(default=0, ge=0)
    latency_ms: float = Field(default=0.0, ge=0.0)
    error: str | None = None
    raw_response: str = ""
    native_response: dict[str, Any] | None = None
    response_sha256: str = Field(min_length=64, max_length=64)

    def is_successful(
        self,
        *,
        provider: str,
        model: str,
        temperature: float,
    ) -> bool:
        return (
            self.native_response is not None
            and self.error is None
            and self.provider == provider
            and self.model == model
            and self.temperature == temperature
        )


class KGParsedOutput(StrictModel):
    trial_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    source_unit_id: str = Field(min_length=1)
    stage: ExtractionStage
    status: str = Field(min_length=1)
    provider_call_ids: tuple[str, ...]
    payload: dict[str, Any]


class KGLiveExperimentManifest(StrictModel):
    manifest_version: Literal["ontology-kg-live-v1"] = "ontology-kg-live-v1"
    mode: ExperimentMode
    runner_status: Literal["completed", "incomplete"]
    provider: str = FROZEN_PROVIDER
    model: str = FROZEN_MODEL
    temperature: float = FROZEN_TEMPERATURE
    thinking: str = "disabled"
    maximum_output_tokens: int = FROZEN_MAX_OUTPUT_TOKENS
    automatic_retry_count: int = 0
    response_cache_enabled: bool = False
    source_version_id: str = Field(min_length=1)
    knowledge_revision: int = Field(ge=0)
    publication_count: int = Field(ge=0)
    construction_status: Literal["ok", "insufficient", "blocked"]
    entity_candidate_count: int = Field(ge=0)
    resolved_entity_count: int = Field(ge=0)
    unmapped_mention_count: int = Field(ge=0)
    relation_candidate_count: int = Field(ge=0)
    validated_relation_count: int = Field(ge=0)
    abstained_chunk_count: int = Field(ge=0)
    blocked_chunk_count: int = Field(ge=0)
    published_fact_count: int = Field(ge=0)
    published_evidence_link_count: int = Field(ge=0)
    expected_ner_chunk_count: int = Field(ge=0)
    eligible_re_chunk_count: int = Field(ge=0)
    ner_call_count: int = Field(ge=0)
    re_call_count: int = Field(ge=0)
    attempted_real_calls: int = Field(ge=0)
    returned_real_calls: int = Field(ge=0)
    successful_real_calls: int = Field(ge=0)
    failed_real_calls: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cache_read_tokens: int = Field(ge=0)
    cache_creation_tokens: int = Field(ge=0)
    provider_latency_ms: float = Field(ge=0.0)
    minimum_successful_calls: int = Field(ge=1)
    missing_ner_chunk_ids: tuple[str, ...] = ()
    missing_re_chunk_ids: tuple[str, ...] = ()
    raw_response_artifact: str = Field(min_length=1)
    raw_response_sha256: str = Field(min_length=64, max_length=64)
    parsed_output_artifact: str = Field(min_length=1)
    parsed_output_sha256: str = Field(min_length=64, max_length=64)
    integrity_status: Literal["verified", "failed"]
    detail_codes: tuple[str, ...] = ()


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _jsonl_bytes(rows: Sequence[dict[str, Any]]) -> bytes:
    if not rows:
        return b""
    return ("\n".join(_canonical_json(row) for row in rows) + "\n").encode("utf-8")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(_canonical_json(row) + "\n")
        stream.flush()


def _cache_tokens(native_response: dict[str, Any] | None) -> tuple[int, int]:
    if native_response is None:
        return 0, 0
    usage = native_response.get("usage_metadata")
    if not isinstance(usage, dict):
        usage = native_response.get("response_metadata", {}).get("token_usage", {})
    details = usage.get("input_token_details", {}) if isinstance(usage, dict) else {}
    if not isinstance(details, dict):
        return 0, 0
    return (
        int(details.get("cache_read") or details.get("cached_tokens") or 0),
        int(details.get("cache_creation") or 0),
    )


class KGLiveExperimentRecorder:
    """Bind each provider response to one parsed ontology KG trial."""

    def __init__(
        self,
        *,
        output_dir: str | Path,
        source_version_id: str,
        expected_ner_chunk_ids: Sequence[str],
        mode: ExperimentMode = "live_experiment",
        minimum_successful_calls: int = 100,
        provider: str = FROZEN_PROVIDER,
        model: str = FROZEN_MODEL,
        temperature: float = FROZEN_TEMPERATURE,
        thinking: str = "disabled",
        maximum_output_tokens: int = FROZEN_MAX_OUTPUT_TOKENS,
        automatic_retry_count: int = 0,
        response_cache_enabled: bool = False,
    ) -> None:
        self.output_dir = Path(output_dir).resolve()
        self.source_version_id = source_version_id
        self.expected_ner_chunk_ids = tuple(sorted(set(expected_ner_chunk_ids)))
        self.mode = mode
        self.minimum_successful_calls = minimum_successful_calls
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.thinking = thinking
        self.maximum_output_tokens = maximum_output_tokens
        self.automatic_retry_count = automatic_retry_count
        self.response_cache_enabled = response_cache_enabled
        self.calls: list[KGProviderCall] = []
        self.parsed_outputs: list[KGParsedOutput] = []
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.raw_path = self.output_dir / "raw_provider_responses.jsonl"
        self.parsed_path = self.output_dir / "parsed_extraction_outputs.jsonl"
        self.manifest_path = self.output_dir / "experiment_manifest.json"
        for path in (self.raw_path, self.parsed_path, self.manifest_path):
            path.unlink(missing_ok=True)

    def record_provider_call(
        self,
        *,
        trial_id: str,
        chunk_id: str,
        stage: ExtractionStage,
        phase: ToolPhase,
        record: ModelCallRecord,
        native_response: dict[str, Any] | None,
    ) -> str:
        response_sha = hashlib.sha256(
            _canonical_json({"native_response": native_response, "error": record.error}).encode(
                "utf-8"
            )
        ).hexdigest()
        call_id = stable_id(
            "ontology-kg-provider-call",
            self.source_version_id,
            trial_id,
            len(self.calls) + 1,
            response_sha,
        )
        cache_read, cache_creation = _cache_tokens(native_response)
        call = KGProviderCall(
            call_id=call_id,
            trial_id=trial_id,
            chunk_id=chunk_id,
            stage=stage,
            phase=phase,
            recorded_at=datetime.now(UTC).isoformat(),
            role=record.agent,
            provider=record.provider,
            model=record.model,
            prompt_set_id=record.prompt_set_id,
            prompt_version=record.prompt_version,
            temperature=record.temperature,
            input_tokens=record.input_tokens,
            output_tokens=record.output_tokens,
            cache_read_tokens=cache_read,
            cache_creation_tokens=cache_creation,
            latency_ms=record.latency_ms,
            error=record.error,
            raw_response=record.raw_response,
            native_response=native_response,
            response_sha256=response_sha,
        )
        self.calls.append(call)
        _append_jsonl(self.raw_path, call.model_dump(mode="json"))
        return call_id

    @contextmanager
    def capture_trial(
        self,
        *,
        trial_id: str,
        chunk_id: str,
        stage: ExtractionStage,
    ) -> Iterator[list[str]]:
        call_ids: list[str] = []

        def observe(
            phase: ToolPhase,
            record: ModelCallRecord,
            native_response: dict[str, Any] | None,
        ) -> None:
            call_ids.append(
                self.record_provider_call(
                    trial_id=trial_id,
                    chunk_id=chunk_id,
                    stage=stage,
                    phase=phase,
                    record=record,
                    native_response=native_response,
                )
            )

        with capture_tool_model_calls(observe):
            yield call_ids

    def record_parsed_output(
        self,
        *,
        trial_id: str,
        chunk_id: str,
        source_unit_id: str,
        stage: ExtractionStage,
        status: str,
        provider_call_ids: Sequence[str],
        payload: dict[str, Any],
    ) -> None:
        parsed = KGParsedOutput(
            trial_id=trial_id,
            chunk_id=chunk_id,
            source_unit_id=source_unit_id,
            stage=stage,
            status=status,
            provider_call_ids=tuple(provider_call_ids),
            payload=payload,
        )
        self.parsed_outputs.append(parsed)
        _append_jsonl(self.parsed_path, parsed.model_dump(mode="json"))

    def finalize(
        self,
        *,
        eligible_re_chunk_ids: Sequence[str],
        knowledge_revision: int,
        publication_count: int,
        construction_status: Literal["ok", "insufficient", "blocked"],
        entity_candidate_count: int,
        resolved_entity_count: int,
        unmapped_mention_count: int,
        relation_candidate_count: int,
        validated_relation_count: int,
        abstained_chunk_count: int,
        blocked_chunk_count: int,
        published_fact_count: int,
        published_evidence_link_count: int,
    ) -> KGLiveExperimentManifest:
        raw_path = self.raw_path
        parsed_path = self.parsed_path
        raw_bytes = _jsonl_bytes([call.model_dump(mode="json") for call in self.calls])
        parsed_bytes = _jsonl_bytes([row.model_dump(mode="json") for row in self.parsed_outputs])
        raw_path.write_bytes(raw_bytes)
        parsed_path.write_bytes(parsed_bytes)
        raw_sha = hashlib.sha256(raw_bytes).hexdigest()
        parsed_sha = hashlib.sha256(parsed_bytes).hexdigest()
        integrity = (
            "verified"
            if hashlib.sha256(raw_path.read_bytes()).hexdigest() == raw_sha
            and hashlib.sha256(parsed_path.read_bytes()).hexdigest() == parsed_sha
            else "failed"
        )
        called_ner = {call.chunk_id for call in self.calls if call.stage == "ner"}
        called_re = {call.chunk_id for call in self.calls if call.stage == "re"}
        missing_ner = tuple(sorted(set(self.expected_ner_chunk_ids).difference(called_ner)))
        eligible_re = set(eligible_re_chunk_ids)
        missing_re = tuple(sorted(eligible_re.difference(called_re)))
        successful = sum(
            call.is_successful(
                provider=self.provider,
                model=self.model,
                temperature=self.temperature,
            )
            for call in self.calls
        )
        detail_codes: list[str] = []
        if missing_ner:
            detail_codes.append("ner_chunk_coverage_incomplete")
        if missing_re:
            detail_codes.append("re_chunk_coverage_incomplete")
        if successful < self.minimum_successful_calls:
            detail_codes.append("successful_call_threshold_not_met")
        if any(
            not call.is_successful(
                provider=self.provider,
                model=self.model,
                temperature=self.temperature,
            )
            for call in self.calls
        ):
            detail_codes.append("provider_call_failure_observed")
        if integrity != "verified":
            detail_codes.append("artifact_integrity_failed")
        runner_status = "completed" if not detail_codes else "incomplete"
        manifest = KGLiveExperimentManifest(
            mode=self.mode,
            runner_status=runner_status,
            provider=self.provider,
            model=self.model,
            temperature=self.temperature,
            thinking=self.thinking,
            maximum_output_tokens=self.maximum_output_tokens,
            automatic_retry_count=self.automatic_retry_count,
            response_cache_enabled=self.response_cache_enabled,
            source_version_id=self.source_version_id,
            knowledge_revision=knowledge_revision,
            publication_count=publication_count,
            construction_status=construction_status,
            entity_candidate_count=entity_candidate_count,
            resolved_entity_count=resolved_entity_count,
            unmapped_mention_count=unmapped_mention_count,
            relation_candidate_count=relation_candidate_count,
            validated_relation_count=validated_relation_count,
            abstained_chunk_count=abstained_chunk_count,
            blocked_chunk_count=blocked_chunk_count,
            published_fact_count=published_fact_count,
            published_evidence_link_count=published_evidence_link_count,
            expected_ner_chunk_count=len(self.expected_ner_chunk_ids),
            eligible_re_chunk_count=len(eligible_re),
            ner_call_count=sum(call.stage == "ner" for call in self.calls),
            re_call_count=sum(call.stage == "re" for call in self.calls),
            attempted_real_calls=len(self.calls),
            returned_real_calls=sum(call.native_response is not None for call in self.calls),
            successful_real_calls=successful,
            failed_real_calls=len(self.calls) - successful,
            input_tokens=sum(call.input_tokens for call in self.calls),
            output_tokens=sum(call.output_tokens for call in self.calls),
            cache_read_tokens=sum(call.cache_read_tokens for call in self.calls),
            cache_creation_tokens=sum(call.cache_creation_tokens for call in self.calls),
            provider_latency_ms=sum(call.latency_ms for call in self.calls),
            minimum_successful_calls=self.minimum_successful_calls,
            missing_ner_chunk_ids=missing_ner,
            missing_re_chunk_ids=missing_re,
            raw_response_artifact=str(raw_path),
            raw_response_sha256=raw_sha,
            parsed_output_artifact=str(parsed_path),
            parsed_output_sha256=parsed_sha,
            integrity_status=integrity,
            detail_codes=tuple(detail_codes),
        )
        manifest_path = self.manifest_path
        manifest_path.write_text(
            json.dumps(
                manifest.model_dump(mode="json"),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return manifest


__all__ = [
    "DEFAULT_KG_LIVE_EXPERIMENT_DIR",
    "KGParsedOutput",
    "KGProviderCall",
    "KGLiveExperimentManifest",
    "KGLiveExperimentRecorder",
]
