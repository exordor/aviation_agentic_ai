from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from aviation_agentic_ai.paths import PROJECT_ROOT

_ENVIRONMENT_LOADED = False
_ENV_LOCK = threading.Lock()


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = resolve_project_path(path).resolve()
    return _load_yaml_with_includes(config_path, stack=())


def _load_yaml_with_includes(
    config_path: Path,
    *,
    stack: tuple[Path, ...],
) -> dict[str, Any]:
    if config_path in stack:
        cycle_start = stack.index(config_path)
        cycle = (*stack[cycle_start:], config_path)
        chain = " -> ".join(str(candidate) for candidate in cycle)
        raise ValueError(f"YAML include cycle detected: {chain}")

    with config_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in YAML config: {config_path}")

    local_values = dict(data)
    includes = local_values.pop("includes", [])
    if not isinstance(includes, list):
        raise ValueError(
            f"Expected includes to be a list in YAML config: {config_path}"
        )

    merged: dict[str, Any] = {}
    next_stack = (*stack, config_path)
    for include in includes:
        if not isinstance(include, str) or not include.strip():
            raise ValueError(
                "Expected every YAML include to be a non-empty path in "
                f"config: {config_path}"
            )
        include_path = Path(include)
        if not include_path.is_absolute():
            include_path = config_path.parent / include_path
        included_values = _load_yaml_with_includes(
            include_path.resolve(),
            stack=next_stack,
        )
        merged = _deep_merge_mappings(merged, included_values)

    return _deep_merge_mappings(merged, local_values)


def _deep_merge_mappings(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        existing = merged.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            merged[key] = _deep_merge_mappings(existing, value)
        else:
            merged[key] = value
    return merged


def resolved_config_checksum(config: dict[str, Any]) -> str:
    """Return a stable checksum for one fully composed configuration."""

    payload = json.dumps(
        config,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_web_evidence_config(
    config: Mapping[str, Any],
) -> Any:
    """Validate and return the optional Web Evidence sidecar settings.

    The active source configuration keeps the sidecar under
    ``sources.web_evidence``.  Accepting a top-level ``web_evidence`` block as
    well keeps small programmatic configurations convenient while preserving a
    single validation boundary for the ingestion pipeline.  An omitted block
    is the safe, disabled configuration and never creates a network client.
    """

    from aviation_agentic_ai.agent_system.web_evidence_client import (
        validate_ingestion_tools,
    )
    from aviation_agentic_ai.agent_system.web_evidence_contracts import (
        WebEvidenceConfig,
    )

    raw: object = config.get("web_evidence")
    if raw is None:
        sources = config.get("sources")
        if isinstance(sources, Mapping):
            raw = sources.get("web_evidence")
    if raw is None:
        return WebEvidenceConfig()
    if not isinstance(raw, Mapping):
        raise ValueError("config.sources.web_evidence must be a mapping")
    try:
        settings = WebEvidenceConfig.model_validate(dict(raw))
        validate_ingestion_tools(settings.tools)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid web evidence configuration: {exc}") from exc
    seed_ids = [seed.seed_id for seed in settings.seeds]
    if len(seed_ids) != len(set(seed_ids)):
        raise ValueError("invalid web evidence configuration: seed_id values must be unique")
    if settings.allowed_domains:
        configured_domains = set(settings.allowed_domains)
        for seed in settings.seeds:
            if not configured_domains.intersection(seed.allowed_domains):
                raise ValueError(
                    "invalid web evidence configuration: global allowed_domains "
                    f"exclude seed {seed.seed_id}"
                )
    return settings


def configured_dataset_id(config: dict[str, Any]) -> str:
    """Return the persistent evidence-store dataset identity."""

    agent_system = config.get("agent_system")
    configured = agent_system if isinstance(agent_system, dict) else {}
    dataset_id = configured.get("dataset_id")
    if not isinstance(dataset_id, str) or not dataset_id:
        raise ValueError(
            "config.agent_system.dataset_id must be a non-empty string"
        )
    return dataset_id


def configured_store_root(config: dict[str, Any]) -> Path:
    """Return the configured project-local evidence-store root."""

    agent_system = config.get("agent_system")
    configured = agent_system if isinstance(agent_system, dict) else {}
    storage = configured.get("storage")
    storage_config = storage if isinstance(storage, dict) else {}
    store_root = storage_config.get("root")
    if not isinstance(store_root, str) or not store_root:
        raise ValueError(
            "config.agent_system.storage.root must be a non-empty path"
        )
    return resolve_project_path(store_root)


def load_environment(*, force: bool = False) -> bool:
    """Load `.env` once from the configuration layer.

    Returns true when python-dotenv was available and asked to load environment
    variables. Callers should still read `os.environ` directly so tests can use
    monkeypatching without resetting this loader.
    """
    with _ENV_LOCK:
        global _ENVIRONMENT_LOADED
        if _ENVIRONMENT_LOADED and not force:
            return False

        try:
            from dotenv import load_dotenv
        except ImportError:
            _ENVIRONMENT_LOADED = True
            return False

        load_dotenv(PROJECT_ROOT / ".env")
        _ENVIRONMENT_LOADED = True
        return True
