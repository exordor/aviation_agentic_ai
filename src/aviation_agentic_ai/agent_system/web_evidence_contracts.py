"""Transport contracts for the optional wigolo Web Evidence sidecar.

The project deliberately owns these contracts instead of importing the
upstream wigolo package.  The current wire contract is the wigolo ``0.2.1``
REST surface: JSON ``POST /v1/{tool}`` routes for ``search``, ``fetch``,
``extract`` and ``diff``.  Upstream responses are mapped into these strict,
small models before they cross the adapter boundary.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import ConfigDict, Field, field_validator, model_validator

from aviation_agentic_ai.agent_system.contracts import StrictModel


WIGOLO_UPSTREAM_VERSION = "0.2.1"
WIGOLO_REST_CONTRACT = "POST /v1/{tool} JSON; GET /health"


def _require_http_url(value: str) -> str:
    if not value.startswith(("http://", "https://")):
        raise ValueError("web URL must use http or https")
    return value


class WebSourceSeed(StrictModel):
    """A configured, operator-approved web document seed."""

    seed_id: str = Field(min_length=1)
    url: str = Field(min_length=1)
    authority: str = Field(min_length=1)
    document_role: str = Field(min_length=1)
    parser_profile: str = Field(min_length=1)
    allowed_domains: tuple[str, ...] = Field(min_length=1)
    max_pages: int = Field(default=1, ge=1, le=200)

    _validate_url = field_validator("url")(_require_http_url)


class WebFetchRequest(StrictModel):
    """The project subset of wigolo's ``fetch`` request."""

    url: str = Field(min_length=1)
    render_js: Literal["auto", "always", "never"] = "auto"
    mode: Literal["cache", "default", "stealth"] = "default"
    section: str | None = None
    max_content_chars: int = Field(default=120_000, ge=1, le=2_000_000)
    force_refresh: bool = False

    _validate_url = field_validator("url")(_require_http_url)


class WebEvidenceSpan(StrictModel):
    """A citation span as returned by wigolo or normalized by this adapter."""

    start: int = Field(ge=0)
    end: int = Field(ge=0)
    unit: Literal["character", "byte"]
    text: str = Field(min_length=1)
    citation_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_extent(self) -> WebEvidenceSpan:
        if self.end <= self.start:
            raise ValueError("web evidence span end must be after start")
        return self


class WebFetchResult(StrictModel):
    """A normalized, non-synthetic result from a wigolo fetch."""

    status: Literal["ok", "insufficient", "blocked"]
    url: str = Field(min_length=1)
    canonical_url: str = Field(min_length=1)
    title: str | None = None
    media_type: str | None = None
    markdown: str = ""
    spans: tuple[WebEvidenceSpan, ...] = ()
    retrieved_at: datetime
    content_hash: str | None = Field(default=None, min_length=64, max_length=64)
    cache_status: str | None = None
    warning: str | None = None
    error_reason: str | None = None

    _validate_urls = field_validator("url", "canonical_url")(_require_http_url)


class WebSearchRequest(StrictModel):
    """The candidate-discovery subset of wigolo's ``search`` request."""

    query: str | tuple[str, ...] = Field(min_length=1)
    allowed_domains: tuple[str, ...] = ()
    time_range: Literal["day", "week", "month", "year"] | None = None
    max_results: int = Field(default=5, ge=1, le=20)


class WebSearchCandidate(StrictModel):
    """One search candidate; it is not exact evidence until fetched."""

    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    snippet: str = ""
    relevance_score: float | None = None

    _validate_url = field_validator("url")(_require_http_url)


class WebSearchResponse(StrictModel):
    """Search candidates and transport status, without synthesized answers."""

    status: Literal["ok", "insufficient", "blocked"]
    candidates: tuple[WebSearchCandidate, ...] = ()
    warnings: tuple[str, ...] = ()
    error_reason: str | None = None


class WebExtractRequest(StrictModel):
    """The bounded deterministic ``extract`` request used by ingestion."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    url: str = Field(min_length=1)
    schema_: str | dict[str, Any] | None = Field(default=None, alias="schema")
    mode: Literal["cache", "default", "stealth"] = "default"
    max_content_chars: int = Field(default=120_000, ge=1, le=2_000_000)

    _validate_url = field_validator("url")(_require_http_url)


class WebExtractResponse(StrictModel):
    """Structured fields plus exact spans returned by wigolo extract."""

    status: Literal["ok", "insufficient", "blocked"]
    fields: dict[str, Any] = Field(default_factory=dict)
    spans: tuple[WebEvidenceSpan, ...] = ()
    warnings: tuple[str, ...] = ()
    error_reason: str | None = None


class WebDiffRequest(StrictModel):
    """A content-change probe for one previously observed URL."""

    url: str = Field(min_length=1)
    known_content_hash: str | None = Field(default=None, min_length=64, max_length=64)
    force_refresh: bool = False

    _validate_url = field_validator("url")(_require_http_url)


class WebDiffResponse(StrictModel):
    """A normalized content revision observation."""

    status: Literal["ok", "insufficient", "blocked"]
    changed: bool | None = None
    current_content_hash: str | None = Field(default=None, min_length=64, max_length=64)
    previous_content_hash: str | None = Field(default=None, min_length=64, max_length=64)
    warnings: tuple[str, ...] = ()
    error_reason: str | None = None


class WebCollectionResult(StrictModel):
    """Aggregate status for one configured seed (used by later ingestion)."""

    seed_id: str = Field(min_length=1)
    status: Literal["ok", "insufficient", "blocked"]
    source_version_ids: tuple[str, ...] = ()
    fetched_urls: tuple[str, ...] = ()
    changed_urls: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    error_reason: str | None = None
