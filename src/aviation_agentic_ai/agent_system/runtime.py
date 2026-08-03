"""Frozen provider settings and model-response metadata extraction."""

from __future__ import annotations

from typing import Any


# Frozen DeepSeek config for the system mainline.
FROZEN_PROVIDER = "deepseek"
FROZEN_MODEL = "deepseek-v4-flash"
FROZEN_TEMPERATURE = 0.0
FROZEN_MAX_OUTPUT_TOKENS = 10_000
FROZEN_TIMEOUT = 120.0
MAX_PROVIDER_CALLS = 8


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
            usage.get("input_tokens")
            or usage.get("prompt_tokens")
            or usage.get("inputTokens")
            or 0
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
