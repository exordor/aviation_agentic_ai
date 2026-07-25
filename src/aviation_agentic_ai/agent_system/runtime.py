"""Runtime: model invoker, run directory, and manifest for the agent system.

Builds the DeepSeek model invoker (records provider/model/usage/latency), the
versioned run directory, and the run manifest that records schema-slice id +
checksum, provider calls, tokens, cost, and the materialization summary.

The invoker assembles the frozen 6-message prompt from the catalog for the
requested role (design §16) and records a per-call ledger entry: agent role,
prompt_set_id, prompt_version, provider/model/usage/latency, and the attempt
index. Per-run state isolation: a fresh invoker holds its own attempt counter
and provider binding; nothing is shared across runs.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import UTC, datetime
from itertools import count
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
from aviation_agentic_ai.agent_system.materialize import GraphPatchMaterialization
from aviation_agentic_ai.agent_system.prompts import (
    DEFAULT_PROMPT_CATALOG,
    assemble_prompt,
)
from aviation_agentic_ai.config import resolve_project_path

# A model invoker takes (agent_role, template_variables) and returns a
# ModelCallRecord. The invoker is the sole caller of the provider and the sole
# assembler of the frozen prompt (design §16).
ModelInvoker = Callable[[str, dict[str, Any]], ModelCallRecord]

# Frozen DeepSeek config for the system mainline (design §16).
FROZEN_PROVIDER = "deepseek"
FROZEN_MODEL = "deepseek-v4-pro"
FROZEN_TEMPERATURE = 0.0
FROZEN_MAX_OUTPUT_TOKENS = 512
FROZEN_TIMEOUT = 120.0
MAX_PROVIDER_CALLS = 8

# Catalog metadata re-exported for the manifest's top-level prompt_version.
PROMPT_CATALOG = DEFAULT_PROMPT_CATALOG


def _extract_usage(result: Any) -> tuple[int, int, str | None, str | None, str | None]:
    """Extract (input_tokens, output_tokens, provider, model, fingerprint)."""

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
    provider = FROZEN_PROVIDER if (fingerprint or metadata.get("finish_reason")) else None
    return input_tokens, output_tokens, provider, model, fingerprint


def make_live_model_invoker(
    *,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> ModelInvoker:
    """Build a DeepSeek model invoker that records full audit metadata.

    Per-run isolation: each invoker holds its own attempt counter and provider
    binding. The frozen prompt is assembled from the catalog for the requested
    role; no caller can inject or rewrite the prompt text.
    """

    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    from aviation_agentic_ai.llm.providers import get_deepseek_mve_llm

    chat = get_deepseek_mve_llm(
        model=FROZEN_MODEL,
        temperature=FROZEN_TEMPERATURE,
        max_tokens=FROZEN_MAX_OUTPUT_TOKENS,
        timeout=FROZEN_TIMEOUT,
        max_retries=0,
    )

    attempt_counter = count(1)
    role_overrides: dict[str, int] = {}

    def _invoke(agent_role: str, template_vars: dict[str, Any]) -> ModelCallRecord:
        assembled = assemble_prompt(agent_role, template_vars, catalog_path=catalog_path)
        # Per-attempt index: global across the run, plus a per-role counter so
        # the ledger can disambiguate retries of the same role.
        global_attempt = next(attempt_counter)
        role_attempt = role_overrides.get(agent_role, 0) + 1
        role_overrides[agent_role] = role_attempt
        messages: list[Any] = []
        for msg_role, content in assembled.messages:
            if msg_role == "system":
                messages.append(SystemMessage(content=content))
            elif msg_role == "assistant":
                messages.append(AIMessage(content=content))
            else:
                messages.append(HumanMessage(content=content))
        started = time.perf_counter()
        try:
            result = chat.invoke(messages)
        except Exception as exc:  # provider/auth/timeout — record, do not fake
            return ModelCallRecord(
                agent=agent_role,
                raw_response="",
                prompt_set_id=assembled.prompt_set_id,
                prompt_version=assembled.prompt_version,
                attempt=role_attempt,
                error=f"{type(exc).__name__}: {exc}",
            )
        latency = (time.perf_counter() - started) * 1000.0
        content = getattr(result, "content", "")
        if isinstance(content, list):
            content = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content)
        raw = str(content or "")
        input_tokens, output_tokens, provider, model_, fingerprint = _extract_usage(result)
        _ = global_attempt  # recorded for completeness; role_attempt is the ledger key
        return ModelCallRecord(
            agent=agent_role,
            raw_response=raw,
            prompt_set_id=assembled.prompt_set_id,
            prompt_version=assembled.prompt_version,
            provider=provider,
            model=model_ or FROZEN_MODEL,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency,
            system_fingerprint=fingerprint,
            attempt=role_attempt,
        )

    return _invoke


def new_run_directory(base_root: str | Path, source_id: str) -> Path:
    """Create a versioned run directory for one ingest."""

    base = Path(base_root)
    base.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S") + f"{datetime.now(UTC).microsecond // 1000:03d}"
    safe = source_id.replace("/", "_").replace(":", "_")
    run_dir = base / f"{safe}_{stamp}Z"
    counter = 1
    while run_dir.exists() and any(run_dir.iterdir()):
        run_dir = base / f"{safe}_{stamp}_{counter:03d}Z"
        counter += 1
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_run_manifest(
    *,
    run_dir: Path,
    source_id: str,
    model_calls: list[ModelCallRecord],
    materialization: GraphPatchMaterialization | None,
    schema_slice_id: str,
    schema_checksum: str,
    evidence_cards: list[Any],
    graph_patch_raw: str | None,
    prompt_set_id: str,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> Path:
    """Write the run manifest (audit memory, design §15).

    Records the per-call ledger: each entry carries the agent role that issued
    the call, the frozen prompt_set_id + prompt_version, the attempt index, and
    provider/model/usage/latency (or the recorded error for failed attempts).
    """

    provider_calls = sum(1 for c in model_calls if c.error is None)
    input_tokens = sum(c.input_tokens for c in model_calls)
    output_tokens = sum(c.output_tokens for c in model_calls)
    manifest = {
        "run_id": run_dir.name,
        "source_id": source_id,
        "created_at": datetime.now(UTC).isoformat(),
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
        "provider_calls": provider_calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "model_calls": [c.model_dump(mode="json") for c in model_calls],
        "materialization": _materialization_summary(materialization),
        "evidence_cards": [c.model_dump(mode="json") for c in evidence_cards],
        "graph_patch_raw": graph_patch_raw,
    }
    path = run_dir / "run_manifest.json"
    path.write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")
    return path


def _materialization_summary(mat: GraphPatchMaterialization | None) -> dict[str, Any]:
    if mat is None:
        return {"materialized": False}
    return {
        "materialized": True,
        "valid_count": mat.valid_count,
        "schema_violation_count": mat.schema_violation_count,
        "profile_gap_count": mat.profile_gap_count,
        "parse_error_count": mat.parse_error_count,
        "parse_rate": mat.parse_rate,
        "schema_slice_id": mat.schema_slice_id,
        "schema_checksum": mat.schema_checksum,
        "triples_written": len(mat.triples),
        "artifacts": {
            "kg_jsonl": mat.jsonl_path,
            "kg_ttl": mat.ttl_path,
            "neo4j_nodes": mat.nodes_path,
            "neo4j_relationships": mat.relationships_path,
        },
    }


def resolve_run_dir(run_dir: str | Path) -> Path:
    return resolve_project_path(run_dir) if not Path(run_dir).is_absolute() else Path(run_dir)
