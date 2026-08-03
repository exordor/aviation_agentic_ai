"""Generic ontology-constrained KG build orchestration.

The public entry point is domain-neutral.  Domain adapters own source parsing
and task construction; every adapter must use the same write-free candidate
generator and deterministic publication boundary.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.faa_order_document import (
    load_faa_order_source_package,
)
from aviation_agentic_ai.agent_system.faa_order_ingestion import (
    configured_faa_order_document_options,
    run_faa_order_ingestion,
)
from aviation_agentic_ai.agent_system.faa_order_kg import run_faa_order_kg
from aviation_agentic_ai.agent_system.kg_live_experiment import (
    DEFAULT_KG_LIVE_EXPERIMENT_DIR,
    KGLiveExperimentRecorder,
)
from aviation_agentic_ai.agent_system.source_path_resolver import resolve_source_path
from aviation_agentic_ai.config import resolve_project_path


@dataclass(frozen=True)
class OntologyKGBuildSummary:
    """Common result contract for one ontology KG build adapter."""

    domain: str
    status: Literal["ok", "insufficient", "blocked"]
    task_count: int
    attempted_count: int
    accepted_count: int
    abstained_count: int
    blocked_count: int
    provider_call_count: int
    input_token_count: int = 0
    output_token_count: int = 0
    provider_latency_ms: float = 0.0
    publication_ids: tuple[str, ...] = ()
    source_version_id: str | None = None
    reasons: tuple[str, ...] = ()
    experiment_manifest_path: str | None = None
    raw_response_artifact: str | None = None
    raw_response_sha256: str | None = None
    parsed_output_artifact: str | None = None
    parsed_output_sha256: str | None = None
    successful_real_calls: int = 0
    failed_real_calls: int = 0

    @property
    def publication_count(self) -> int:
        return len(self.publication_ids)


def _blocked(domain: str, reason: str) -> OntologyKGBuildSummary:
    return OntologyKGBuildSummary(
        domain=domain,
        status="blocked",
        task_count=0,
        attempted_count=0,
        accepted_count=0,
        abstained_count=0,
        blocked_count=1,
        provider_call_count=0,
        input_token_count=0,
        output_token_count=0,
        provider_latency_ms=0.0,
        reasons=(reason,),
    )


def _build_document_domain(
    config: dict[str, object],
    store: AviationEvidenceStore,
    *,
    allow_live_model: bool,
    source_root: str | Path | None,
    max_items: int | None,
) -> OntologyKGBuildSummary:
    configured = config.get("sources")
    sources = configured if isinstance(configured, dict) else {}
    configured_path = sources.get("faa_order_7210_3ee")
    if not isinstance(configured_path, str) or not configured_path:
        return _blocked(
            "document",
            "configured document KG adapter has no source artifact",
        )
    ingestion = run_faa_order_ingestion(
        config,
        store,
        source_root=source_root,
    )
    if ingestion.status != "ok":
        return OntologyKGBuildSummary(
            domain="document",
            status="blocked" if ingestion.status == "blocked" else "insufficient",
            task_count=0,
            attempted_count=0,
            accepted_count=0,
            abstained_count=0,
            blocked_count=1 if ingestion.status == "blocked" else 0,
            provider_call_count=0,
            input_token_count=0,
            output_token_count=0,
            provider_latency_ms=0.0,
            source_version_id=ingestion.source_version_id,
            reasons=(
                ingestion.reason or "document source ingestion was insufficient"
            ),
        )
    resolved = resolve_source_path(
        configured_path,
        source_root=source_root,
        project_root=resolve_project_path("."),
    )
    package = load_faa_order_source_package(
        resolved.resolved_path,
        **configured_faa_order_document_options(config),
    )
    selected_chunks = (
        package.extraction_chunks[:max_items]
        if max_items is not None
        else package.extraction_chunks
    )
    experiment_dir = resolve_project_path(DEFAULT_KG_LIVE_EXPERIMENT_DIR)
    if max_items is not None:
        experiment_dir = experiment_dir / f"smoke-max-{max_items}"
    recorder = KGLiveExperimentRecorder(
        output_dir=experiment_dir,
        source_version_id=package.source_version_id,
        expected_ner_chunk_ids=tuple(chunk.chunk_id for chunk in selected_chunks),
    )
    result = run_faa_order_kg(
        package,
        store,
        allow_live_model=allow_live_model,
        max_chunks=max_items,
        experiment_recorder=recorder,
    )
    return OntologyKGBuildSummary(
        domain="document",
        status=result.status,
        task_count=result.task_count,
        attempted_count=result.attempted_count,
        accepted_count=result.accepted_count,
        abstained_count=result.abstained_count,
        blocked_count=result.blocked_count,
        provider_call_count=result.provider_call_count,
        input_token_count=result.input_token_count,
        output_token_count=result.output_token_count,
        provider_latency_ms=result.provider_latency_ms,
        publication_ids=result.publication_ids,
        source_version_id=package.source_version_id,
        reasons=result.reasons,
        experiment_manifest_path=result.experiment_manifest_path,
        raw_response_artifact=result.raw_response_artifact,
        raw_response_sha256=result.raw_response_sha256,
        parsed_output_artifact=result.parsed_output_artifact,
        parsed_output_sha256=result.parsed_output_sha256,
        successful_real_calls=result.successful_real_calls,
        failed_real_calls=result.failed_real_calls,
    )


_DOMAIN_BUILDERS: dict[
    str,
    Callable[..., OntologyKGBuildSummary],
] = {"document": _build_document_domain}


def run_ontology_kg_build(
    config: dict[str, object],
    store: AviationEvidenceStore,
    *,
    domain: str,
    allow_live_model: bool,
    source_root: str | Path | None = None,
    max_items: int | None = None,
) -> OntologyKGBuildSummary:
    """Build one configured ontology domain using the real provider only."""

    if not allow_live_model:
        return _blocked(
            domain,
            "--allow-live-model is required for ontology KG generation",
        )
    builder = _DOMAIN_BUILDERS.get(domain)
    if builder is None:
        supported = ", ".join(sorted(_DOMAIN_BUILDERS))
        return _blocked(
            domain,
            f"unsupported ontology KG domain {domain!r}; configured domains: {supported}",
        )
    return builder(
        config,
        store,
        allow_live_model=True,
        source_root=source_root,
        max_items=max_items,
    )


__all__ = ["OntologyKGBuildSummary", "run_ontology_kg_build"]
