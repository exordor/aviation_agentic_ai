"""Persistence adapter for normalized wigolo Web Evidence results.

This module is deliberately small: the wigolo sidecar owns transport and
fetching, while this project owns identity, evidence anchors, and SQLite
registration.  A successful response is first validated in memory and only
then registered as an immutable source version.  Blocked or insufficient
responses therefore cannot remove a previously accepted version.
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import SplitResult, urlsplit, urlunsplit

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.source_retrieval import (
    build_source_record_chunk,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    SourceAnchorRecord,
    SourceAssetRecord,
    SourceVersionRecord,
)
from aviation_agentic_ai.agent_system.web_evidence_client import (
    HttpWigoloWebClient,
    WebEvidenceClient,
    normalize_evidence_span,
)
from aviation_agentic_ai.agent_system.web_evidence_contracts import (
    WebCollectionResult,
    WebEvidenceConfig,
    WebFetchRequest,
    WebFetchResult,
    WebSourceSeed,
)
from aviation_agentic_ai.config import validate_web_evidence_config
from aviation_agentic_ai.utils.identifiers import stable_id


DEFAULT_WEB_ADAPTER_VERSION = "wigolo-web-evidence-v1"
WEB_REPRESENTATION = "normalized_markdown"


@dataclass(frozen=True, slots=True)
class WebIngestionSummary:
    """Aggregate status for the explicitly opt-in Web Evidence domain."""

    discovered_count: int
    selected_count: int
    attempted_count: int
    skipped_count: int
    ok_count: int
    insufficient_count: int
    blocked_count: int
    results: tuple[WebCollectionResult, ...] = ()
    status: str = "not_configured"
    reason: str | None = None


def _empty_web_summary(
    *,
    status: str,
    reason: str | None = None,
) -> WebIngestionSummary:
    """Return a no-op outcome that cannot affect direct source domains."""

    return WebIngestionSummary(
        discovered_count=0,
        selected_count=0,
        attempted_count=0,
        skipped_count=0,
        ok_count=0,
        insufficient_count=0,
        blocked_count=0,
        status=status,
        reason=reason,
    )


def run_web_evidence_ingestion(
    config: Mapping[str, object],
    store: AviationEvidenceStore,
    *,
    allow_live_web: bool = False,
    client: WebEvidenceClient | None = None,
    client_factory: Callable[[WebEvidenceConfig], WebEvidenceClient] | None = None,
    now: datetime | None = None,
) -> WebIngestionSummary:
    """Ingest configured web seeds through the existing evidence store.

    The explicit ``allow_live_web`` gate is checked before constructing a
    transport client.  Thus a disabled or unauthorized run performs zero web
    calls, including no health check or token lookup.  Seed failures are
    isolated and returned as typed outcomes so TMI and Flight/Airspace
    ingestion remain committed independently.
    """

    settings = validate_web_evidence_config(config)
    if not settings.enabled:
        return _empty_web_summary(status="disabled")
    if not allow_live_web:
        return _empty_web_summary(
            status="unauthorized",
            reason="--allow-live-web is required for web ingestion",
        )
    if not settings.seeds:
        return _empty_web_summary(status="not_configured")

    selected_client = client
    if selected_client is None:
        if client_factory is not None:
            selected_client = client_factory(settings)
        else:
            token = os.environ.get(settings.token_env) or None
            selected_client = HttpWigoloWebClient(
                settings.base_url,
                token,
                settings.timeout_seconds,
            )

    effective_now = now or datetime.now(UTC)
    raw_config = settings.model_dump(mode="python")
    results: list[WebCollectionResult] = []
    for seed in settings.seeds:
        results.append(
            collect_web_seed(
                raw_config,
                seed,
                selected_client,
                store,
                now=effective_now,
            )
        )
    ordered = tuple(sorted(results, key=lambda row: row.seed_id))
    return WebIngestionSummary(
        discovered_count=len(ordered),
        selected_count=len(ordered),
        attempted_count=len(ordered),
        skipped_count=0,
        ok_count=sum(row.status == "ok" for row in ordered),
        insufficient_count=sum(row.status == "insufficient" for row in ordered),
        blocked_count=sum(row.status == "blocked" for row in ordered),
        results=ordered,
        status="completed",
    )


def canonicalize_web_url(url: str) -> str:
    """Return a stable URL identity suitable for source IDs.

    URL fragments are client-side presentation state and are intentionally
    excluded.  Scheme and host are case-insensitive, default ports are
    removed, and an empty path is represented as ``/``.  Query parameters are
    retained because they can select different source documents.
    """

    parsed = urlsplit(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("web URL must use http or https")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("web URL must include a host")
    try:
        hostname = hostname.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError as exc:
        raise ValueError("web URL host is not valid IDNA") from exc
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("web URL port is invalid") from exc
    netloc = hostname
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("web URL must not include credentials")
    if ":" in hostname and not hostname.startswith("["):
        netloc = f"[{hostname}]"
    if port is not None and not (
        (parsed.scheme == "http" and port == 80)
        or (parsed.scheme == "https" and port == 443)
    ):
        netloc = f"{netloc}:{port}"
    path = parsed.path or "/"
    return urlunsplit(
        SplitResult(
            parsed.scheme.lower(),
            netloc,
            path,
            parsed.query,
            "",
        )
    )


def _domain_matches(hostname: str, domain: str) -> bool:
    normalized_domain = domain.strip().lower().rstrip(".")
    normalized_host = hostname.lower().rstrip(".")
    return bool(normalized_domain) and (
        normalized_host == normalized_domain
        or normalized_host.endswith("." + normalized_domain)
    )


def validate_web_url_allowlist(
    url: str,
    allowed_domains: tuple[str, ...],
) -> str:
    """Canonicalize a URL and require its host to be explicitly allowlisted."""

    canonical = canonicalize_web_url(url)
    hostname = urlsplit(canonical).hostname
    if hostname is None or not any(
        _domain_matches(hostname, domain) for domain in allowed_domains
    ):
        raise ValueError(f"web URL host is outside allowlist: {hostname or '<none>'}")
    return canonical


def _config_mapping(config: Mapping[str, object]) -> Mapping[str, object]:
    """Accept either the web block or the whole source configuration."""

    nested = config.get("web_evidence")
    if not isinstance(nested, Mapping):
        sources = config.get("sources")
        if isinstance(sources, Mapping):
            nested = sources.get("web_evidence")
    return nested if isinstance(nested, Mapping) else config


def _configured_domains(
    config: Mapping[str, object],
    seed: WebSourceSeed,
) -> tuple[str, ...]:
    web_config = _config_mapping(config)
    configured = web_config.get("allowed_domains")
    domains = (
        tuple(str(item) for item in configured if str(item).strip())
        if isinstance(configured, (list, tuple, set))
        else ()
    )
    # A global list is an additional restriction, not a replacement for the
    # narrower seed list.  The URL itself is checked against both policies.
    if domains:
        return tuple(domain for domain in domains if domain.strip())
    return seed.allowed_domains


def _validate_configured_url(
    config: Mapping[str, object],
    seed: WebSourceSeed,
    url: str,
) -> str:
    """Require a URL to satisfy both seed and operator-wide policies."""

    canonical = validate_web_url_allowlist(url, seed.allowed_domains)
    configured_domains = _configured_domains(config, seed)
    if configured_domains != seed.allowed_domains:
        canonical = validate_web_url_allowlist(canonical, configured_domains)
    return canonical


def _limit_from_config(config: Mapping[str, object], name: str, default: int) -> int:
    web_config = _config_mapping(config)
    limits = web_config.get("limits")
    if isinstance(limits, Mapping):
        value = limits.get(name)
        if isinstance(value, int) and value > 0:
            return value
    return default


def _retrieved_at(result: WebFetchResult, fallback: datetime) -> str:
    value = result.retrieved_at
    if value.tzinfo is None or value.utcoffset() is None:
        value = fallback
    return value.astimezone(UTC).isoformat()


def _safe_metadata(
    result: WebFetchResult,
    seed: WebSourceSeed,
    *,
    canonical_url: str,
    adapter_version: str,
    fallback_now: datetime,
    content_sha256: str,
) -> dict[str, object]:
    """Select only stable, non-sensitive metadata from a sidecar result."""

    metadata: dict[str, object] = {
        "authority": seed.authority,
        "document_role": seed.document_role,
        "parser_profile": seed.parser_profile,
        "canonical_url": canonical_url,
        "retrieved_at": _retrieved_at(result, fallback_now),
        "media_type": result.media_type or "text/markdown",
        "representation": WEB_REPRESENTATION,
        "content_sha256": content_sha256,
        "span_normalization": "character_offsets_utf8",
        "adapter_version": adapter_version,
    }
    if result.title:
        metadata["title"] = result.title
    requested_url = canonicalize_web_url(result.url)
    if requested_url != canonical_url:
        metadata["redirect_url"] = requested_url
    if result.cache_status:
        metadata["cache_status"] = result.cache_status
    if result.warning:
        metadata["warning"] = result.warning
    return metadata


def normalize_web_fetch(
    result: WebFetchResult,
    seed: WebSourceSeed,
    *,
    adapter_version: str = DEFAULT_WEB_ADAPTER_VERSION,
) -> tuple[SourceVersionRecord, tuple[SourceAnchorRecord, ...]]:
    """Validate and map one successful fetch into immutable store records."""

    if result.status != "ok":
        raise ValueError("only successful web fetches can be normalized")
    validate_web_url_allowlist(result.url, seed.allowed_domains)
    canonical_url = validate_web_url_allowlist(result.canonical_url, seed.allowed_domains)
    if not result.markdown:
        raise ValueError("web fetch content is empty")
    calculated_hash = hashlib.sha256(result.markdown.encode("utf-8")).hexdigest()
    if result.content_hash is not None and result.content_hash.lower() != calculated_hash:
        raise ValueError("web fetch content checksum does not match markdown")

    normalized_spans = tuple(
        normalize_evidence_span(result.markdown, span) for span in result.spans
    )
    source_id = stable_id("web-document", canonical_url)
    source_version_id = stable_id("source-version", source_id, calculated_hash)
    metadata = _safe_metadata(
        result,
        seed,
        canonical_url=canonical_url,
        adapter_version=adapter_version,
        fallback_now=result.retrieved_at,
        content_sha256=calculated_hash,
    )
    version = SourceVersionRecord(
        source_version_id=source_version_id,
        source_id=source_id,
        family=SourceFamily.WEB_DOCUMENT,
        asset_id=None,
        content=result.markdown,
        content_sha256=calculated_hash,
        source_url=canonical_url,
        logical_time=None,
        metadata=metadata,
    )

    anchors: dict[tuple[int, int], SourceAnchorRecord] = {}
    full_start, full_end = 0, len(result.markdown)
    anchors[(full_start, full_end)] = SourceAnchorRecord(
        source_anchor_id=stable_id(
            "source-anchor", source_version_id, full_start, full_end
        ),
        source_version_id=source_version_id,
        char_start=full_start,
        char_end=full_end,
        anchor_kind="full_record",
    )
    for span in normalized_spans:
        anchors[(span.start, span.end)] = SourceAnchorRecord(
            source_anchor_id=stable_id(
                "source-anchor", source_version_id, span.start, span.end
            ),
            source_version_id=source_version_id,
            char_start=span.start,
            char_end=span.end,
            anchor_kind=(
                "full_record"
                if span.start == full_start and span.end == full_end
                else "text_span"
            ),
        )
    return version, tuple(
        sorted(anchors.values(), key=lambda anchor: anchor.source_anchor_id)
    )


def _build_web_source_asset(
    version: SourceVersionRecord,
) -> SourceAssetRecord:
    """Create a checksum-pinned remote asset record without raw payloads."""

    asset_key = version.source_id
    return SourceAssetRecord(
        asset_id=stable_id("source-asset", asset_key, version.content_sha256),
        asset_key=asset_key,
        family=SourceFamily.WEB_DOCUMENT,
        local_path=f"web://{version.source_id}",
        source_url=version.source_url,
        media_type=str(version.metadata.get("media_type", "text/markdown")),
        content_sha256=version.content_sha256,
        byte_count=len(version.content.encode("utf-8")),
        effective_start=None,
        effective_end=None,
    )


def collect_web_seed(
    config: Mapping[str, object],
    seed: WebSourceSeed,
    client: WebEvidenceClient,
    store: AviationEvidenceStore,
    *,
    now: datetime,
) -> WebCollectionResult:
    """Fetch, validate, and persist one configured Web Evidence seed.

    Failed observations return a typed result and do not touch the store.  A
    successful changed fetch is appended as a new immutable source version;
    earlier versions remain queryable through the normal store APIs.
    """

    try:
        requested_url = _validate_configured_url(config, seed, seed.url)
    except ValueError as exc:
        return WebCollectionResult(
            seed_id=seed.seed_id,
            status="blocked",
            fetched_urls=(),
            error_reason=f"policy:{exc}",
        )

    max_chars = _limit_from_config(config, "max_content_chars", 120_000)
    request = WebFetchRequest(
        url=requested_url,
        max_content_chars=max_chars,
    )
    try:
        result = client.fetch(request)
    except Exception as exc:  # transport implementations must not break direct ingest
        return WebCollectionResult(
            seed_id=seed.seed_id,
            status="blocked",
            fetched_urls=(requested_url,),
            error_reason=f"client:{type(exc).__name__}",
        )
    if result.status != "ok":
        return WebCollectionResult(
            seed_id=seed.seed_id,
            status=result.status,
            fetched_urls=(requested_url,),
            warnings=((result.warning,) if result.warning else ()),
            error_reason=result.error_reason,
        )

    try:
        _validate_configured_url(config, seed, result.canonical_url)
        version, anchors = normalize_web_fetch(
            result,
            seed,
            adapter_version=str(
                _config_mapping(config).get(
                    "adapter_version", DEFAULT_WEB_ADAPTER_VERSION
                )
            ),
        )
        previous = store.get_latest_source_version(version.source_id)
        asset = _build_web_source_asset(version)
        version = version.model_copy(update={"asset_id": asset.asset_id})
        existing = store.get_source_version(version.source_version_id)
        if existing is None:
            store.register_source_asset(asset)
            store.register_source_version(version)
        else:
            if store.get_source_asset(asset.asset_id) is None:
                # Recover a partially completed first registration without
                # mutating an already immutable source version.
                store.register_source_asset(asset)
            # Repeated fetches may have a newer retrieval timestamp while
            # representing the same immutable content.  Reuse the stored
            # version so derived chunk metadata remains byte-stable.
            version = existing
        for anchor in anchors:
            store.register_source_anchor(
                anchor.source_version_id,
                char_start=anchor.char_start,
                char_end=anchor.char_end,
            )
        chunk = build_source_record_chunk(version)
        if chunk is not None:
            store.upsert_source_chunks((chunk,))
    except (TypeError, ValueError) as exc:
        return WebCollectionResult(
            seed_id=seed.seed_id,
            status="blocked",
            fetched_urls=(requested_url,),
            error_reason=f"normalize:{exc}",
        )

    changed = previous is None or previous.source_version_id != version.source_version_id
    return WebCollectionResult(
        seed_id=seed.seed_id,
        status="ok",
        source_version_ids=(version.source_version_id,),
        fetched_urls=(version.source_url or requested_url,),
        changed_urls=((version.source_url or requested_url,) if changed else ()),
    )


__all__ = [
    "DEFAULT_WEB_ADAPTER_VERSION",
    "WebIngestionSummary",
    "canonicalize_web_url",
    "collect_web_seed",
    "normalize_web_fetch",
    "run_web_evidence_ingestion",
    "validate_web_url_allowlist",
]
