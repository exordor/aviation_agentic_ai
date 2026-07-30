"""Transient run bindings and manifests used during corpus construction."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
from aviation_agentic_ai.agent_system.materialize import (
    FactMaterialization,
)
from aviation_agentic_ai.agent_system.prompts import DEFAULT_PROMPT_CATALOG

# Frozen DeepSeek config for the system mainline (design §16).
FROZEN_PROVIDER = "deepseek"
FROZEN_MODEL = "deepseek-v4-pro"
FROZEN_TEMPERATURE = 0.0
FROZEN_MAX_OUTPUT_TOKENS = 10_000
FROZEN_TIMEOUT = 120.0
MAX_PROVIDER_CALLS = 8

RUN_MANIFEST_VERSION = "decision-case-run-v1"


@dataclass(frozen=True)
class RunBinding:
    """One immutable identity and timestamp shared by a complete ingest run."""

    run_id: str
    run_dir: Path
    run_started_at: datetime


def extract_model_metadata(
    result: Any,
) -> tuple[int, int, str | None, str | None, str | None, str | None]:
    """Extract usage plus provider, model, fingerprint, and finish reason."""

    usage = (
        getattr(result, "usage_metadata", None)
        or (getattr(result, "response_metadata", None) or {}).get("token_usage")
        or (getattr(result, "response_metadata", None) or {}).get("usage")
    )
    input_tokens = output_tokens = 0
    if usage:
        input_tokens = int(
            usage.get("input_tokens") or usage.get("prompt_tokens") or usage.get("inputTokens") or 0
        )
        output_tokens = int(
            usage.get("output_tokens")
            or usage.get("completion_tokens")
            or usage.get("outputTokens")
            or 0
        )
        output_tokens += int(usage.get("reasoning_tokens") or 0)
    metadata = getattr(result, "response_metadata", None) or {}
    model = metadata.get("model_name") or metadata.get("model")
    fingerprint = metadata.get("system_fingerprint")
    finish_reason = metadata.get("finish_reason")
    provider = FROZEN_PROVIDER if (fingerprint or finish_reason) else None
    return (
        input_tokens,
        output_tokens,
        provider,
        model,
        fingerprint,
        str(finish_reason) if finish_reason is not None else None,
    )


def create_run_binding(
    base_root: str | Path,
    source_id: str,
    *,
    started_at: datetime | None = None,
) -> RunBinding:
    """Create a run directory after sampling and normalizing one UTC timestamp."""

    sampled = started_at if started_at is not None else datetime.now(UTC)
    if sampled.tzinfo is None or sampled.utcoffset() is None:
        raise ValueError("run started_at must be timezone-aware")
    run_started_at = sampled.astimezone(UTC)
    base = Path(base_root)
    base.mkdir(parents=True, exist_ok=True)
    stamp = run_started_at.strftime("%Y%m%dT%H%M%S%f")[:18]
    safe = source_id.replace("/", "_").replace(":", "_")
    run_dir = base / f"{safe}_{stamp}Z"
    counter = 1
    while run_dir.exists() and any(run_dir.iterdir()):
        run_dir = base / f"{safe}_{stamp}_{counter:03d}Z"
        counter += 1
    run_dir.mkdir(parents=True, exist_ok=True)
    return RunBinding(
        run_id=run_dir.name,
        run_dir=run_dir,
        run_started_at=run_started_at,
    )


def write_run_manifest(
    *,
    run_dir: Path,
    source_id: str,
    model_calls: list[ModelCallRecord],
    materialization: FactMaterialization | None,
    schema_slice_id: str,
    schema_checksum: str,
    evidence_cards: list[Any],
    graph_patch_raw: str | None,
    prompt_set_id: str,
    profile_gap_count: int,
    context_artifacts: dict[str, dict[str, Any]] | None = None,
    formal_layers: dict[str, dict[str, Any]] | None = None,
    public_observation_publication: dict[str, Any] | None = None,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
    created_at: datetime | None = None,
) -> Path:
    """Write the run manifest (audit memory, design §15).

    Records the per-call ledger: each entry carries the agent role that issued
    the call, the frozen prompt_set_id + prompt_version, the attempt index, and
    provider/model/usage/latency (or the recorded error for failed attempts).
    """

    provider_attempts = len(model_calls)
    provider_successes = sum(1 for c in model_calls if c.error is None)
    input_tokens = sum(c.input_tokens for c in model_calls)
    output_tokens = sum(c.output_tokens for c in model_calls)
    frozen_created_at = created_at if created_at is not None else datetime.now(UTC)
    if frozen_created_at.tzinfo is None or frozen_created_at.utcoffset() is None:
        raise ValueError("manifest created_at must be timezone-aware")
    decision_layer = (formal_layers or {}).get("decision", {})
    profile_gap_status = decision_layer.get(
        "status",
        "ok" if materialization is not None else "insufficient",
    )
    if profile_gap_status not in {"ok", "insufficient", "blocked"}:
        raise ValueError("profile-gap artifact status is invalid")
    profile_gap_path = run_dir / "profile_gaps.jsonl"
    if not profile_gap_path.exists():
        if profile_gap_count:
            raise ValueError("profile-gap artifact is missing")
        profile_gap_path.write_text("", encoding="utf-8")
    profile_gap_data = profile_gap_path.read_bytes()
    actual_profile_gap_count = sum(
        1 for line in profile_gap_data.splitlines() if line.strip()
    )
    if actual_profile_gap_count != profile_gap_count:
        raise ValueError("profile-gap artifact row count does not match validation")
    if profile_gap_status != "ok" and actual_profile_gap_count:
        raise ValueError("non-ok profile-gap artifact must be empty")
    manifest = {
        "manifest_version": RUN_MANIFEST_VERSION,
        "run_id": run_dir.name,
        "source_id": source_id,
        "created_at": frozen_created_at.astimezone(UTC).isoformat(),
        "prompt_set_id": prompt_set_id,
        "prompt_catalog": catalog_path,
        "frozen_model": {
            "provider": FROZEN_PROVIDER,
            "model": FROZEN_MODEL,
            "temperature": FROZEN_TEMPERATURE,
            "thinking": "disabled",
            "max_retries": 0,
        },
        "schema_slice_id": schema_slice_id,
        "schema_checksum": schema_checksum,
        "provider_attempts": provider_attempts,
        "provider_successes": provider_successes,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "model_calls": [c.model_dump(mode="json") for c in model_calls],
        "materialization": _materialization_summary(materialization),
        "profile_gaps": {
            "path": "profile_gaps.jsonl",
            "count": profile_gap_count,
            "sha256": hashlib.sha256(profile_gap_data).hexdigest(),
            "status": profile_gap_status,
        },
        "context_artifacts": context_artifacts or {},
        "formal_layers": formal_layers or {},
        "public_observation_publication": (
            public_observation_publication or {}
        ),
        "evidence_cards": [c.model_dump(mode="json") for c in evidence_cards],
        "graph_patch_raw": graph_patch_raw,
    }
    path = run_dir / "run_manifest.json"
    path.write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")
    return path


def _materialization_summary(
    mat: FactMaterialization | None,
) -> dict[str, Any]:
    if mat is None:
        return {"materialized": False}
    return {
        "materialized": True,
        "fact_count": mat.fact_count,
        "schema_slice_id": mat.schema_slice_id,
        "schema_checksum": mat.schema_checksum,
        "profile_refs": [
            ref.model_dump(mode="json") for ref in mat.profile_refs
        ],
        "layer_fact_counts": mat.layer_fact_counts,
        "artifacts": {
            "kg_jsonl": mat.jsonl_path,
            "kg_ttl": mat.ttl_path,
            "neo4j_nodes": mat.nodes_path,
            "neo4j_relationships": mat.relationships_path,
        },
    }
