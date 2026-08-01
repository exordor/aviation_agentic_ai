"""Small stdlib REST adapter for the optional wigolo web sidecar.

The adapter targets wigolo ``0.2.1``'s documented REST API.  It exposes only
the non-synthesizing ``search``, ``fetch``, ``extract`` and ``diff`` routes;
``research`` and ``agent`` are intentionally not part of the ingestion
surface.  All upstream payloads are reduced to project-owned Pydantic models
before they are returned.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from aviation_agentic_ai.agent_system.web_evidence_contracts import (
    WebDiffRequest,
    WebDiffResponse,
    WebEvidenceSpan,
    WebExtractRequest,
    WebExtractResponse,
    WebFetchRequest,
    WebFetchResult,
    WebSearchCandidate,
    WebSearchRequest,
    WebSearchResponse,
)


INGESTION_TOOLS = frozenset({"fetch", "extract", "diff"})
FORBIDDEN_INGESTION_TOOLS = frozenset({"research", "agent", "answer", "stream_answer"})


class WebEvidenceClient(Protocol):
    """Transport boundary used by both ingestion and optional query tools."""

    def fetch(self, request: WebFetchRequest) -> WebFetchResult: ...

    def search(self, request: WebSearchRequest) -> WebSearchResponse: ...

    def extract(self, request: WebExtractRequest) -> WebExtractResponse: ...

    def diff(self, request: WebDiffRequest) -> WebDiffResponse: ...


def validate_ingestion_tools(tools: Iterable[str]) -> tuple[str, ...]:
    """Validate that a configured ingestion surface cannot synthesize prose."""

    normalized = tuple(str(tool) for tool in tools)
    forbidden = sorted(set(normalized) - INGESTION_TOOLS)
    if forbidden:
        raise ValueError(
            "wigolo tools not permitted for ingestion: " + ", ".join(forbidden)
        )
    return normalized


def normalize_evidence_span(content: str, span: WebEvidenceSpan) -> WebEvidenceSpan:
    """Convert upstream byte offsets to Python character offsets.

    A byte range must begin and end on UTF-8 code-point boundaries.  The
    extracted text is checked after conversion so a bad upstream citation
    cannot become a project source anchor silently.
    """

    if span.unit == "character":
        start, end = span.start, span.end
    else:
        encoded = content.encode("utf-8")
        if span.end > len(encoded):
            raise ValueError("web evidence byte span exceeds content")
        try:
            start = len(encoded[: span.start].decode("utf-8"))
            end = len(encoded[: span.end].decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise ValueError("web evidence span is not on a UTF-8 character boundary") from exc

    if end > len(content) or content[start:end] != span.text:
        raise ValueError("web evidence span text does not match fetched content")
    return span.model_copy(update={"start": start, "end": end, "unit": "character"})


class HttpWigoloWebClient:
    """A no-dependency client for wigolo's documented REST routes."""

    def __init__(self, base_url: str, token: str | None, timeout_seconds: float):
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("wigolo base_url must be an absolute http(s) URL")
        if timeout_seconds <= 0:
            raise ValueError("wigolo timeout_seconds must be positive")
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_seconds = float(timeout_seconds)

    def fetch(self, request: WebFetchRequest) -> WebFetchResult:
        payload, error_reason = self._post("fetch", request.model_dump(mode="json", exclude_none=True))
        now = datetime.now(timezone.utc)
        if error_reason is not None or payload is None:
            return self._blocked_fetch(request.url, now, error_reason or "transport_error")

        canonical_url = self._string(payload.get("canonical_url"), request.url)
        markdown = self._string(payload.get("markdown"), "")
        error = self._optional_string(payload.get("error_reason"))
        warning = self._optional_string(payload.get("warning"))
        if error is not None or (
            not markdown and self._optional_string(payload.get("error")) is not None
        ):
            return self._blocked_fetch(request.url, now, error or "blocked_by_sidecar", canonical_url)
        if not markdown:
            return WebFetchResult(
                status="insufficient",
                url=request.url,
                canonical_url=canonical_url,
                title=self._optional_string(payload.get("title")),
                media_type=self._optional_string(payload.get("media_type")),
                retrieved_at=now,
                cache_status=self._optional_string(payload.get("cache_status")),
                warning=warning,
                error_reason="empty_content",
            )

        try:
            spans = self._parse_spans(payload, markdown)
        except ValueError:
            return self._blocked_fetch(request.url, now, "span_mismatch", canonical_url)
        return WebFetchResult(
            status="ok",
            url=request.url,
            canonical_url=canonical_url,
            title=self._optional_string(payload.get("title")),
            media_type=self._optional_string(payload.get("media_type")),
            markdown=markdown,
            spans=spans,
            retrieved_at=now,
            content_hash=hashlib.sha256(markdown.encode("utf-8")).hexdigest(),
            cache_status=self._optional_string(payload.get("cache_status")),
            warning=warning,
        )

    def search(self, request: WebSearchRequest) -> WebSearchResponse:
        payload, error_reason = self._post("search", request.model_dump(mode="json", exclude_none=True))
        if error_reason is not None or payload is None:
            return WebSearchResponse(status="blocked", error_reason=error_reason or "transport_error")
        if self._optional_string(payload.get("error_reason")) is not None:
            return WebSearchResponse(
                status="blocked",
                warnings=self._warnings(payload),
                error_reason=self._optional_string(payload.get("error_reason")),
            )
        candidates = tuple(
            self._candidate(item)
            for item in payload.get("results", [])
            if isinstance(item, Mapping) and self._optional_string(item.get("url"))
        )
        return WebSearchResponse(
            status="ok" if candidates else "insufficient",
            candidates=candidates,
            warnings=self._warnings(payload),
        )

    def extract(self, request: WebExtractRequest) -> WebExtractResponse:
        payload, error_reason = self._post(
            "extract",
            request.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        if error_reason is not None or payload is None:
            return WebExtractResponse(status="blocked", error_reason=error_reason or "transport_error")
        provider_error = self._optional_string(payload.get("error_reason"))
        if provider_error is not None:
            return WebExtractResponse(
                status="blocked",
                warnings=self._warnings(payload),
                error_reason=provider_error,
            )
        fields = payload.get("fields", {})
        if not isinstance(fields, Mapping):
            return WebExtractResponse(status="blocked", error_reason="invalid_fields")
        return WebExtractResponse(
            status="ok" if fields else "insufficient",
            fields=dict(fields),
            warnings=self._warnings(payload),
        )

    def diff(self, request: WebDiffRequest) -> WebDiffResponse:
        payload, error_reason = self._post("diff", request.model_dump(mode="json", exclude_none=True))
        if error_reason is not None or payload is None:
            return WebDiffResponse(status="blocked", error_reason=error_reason or "transport_error")
        provider_error = self._optional_string(payload.get("error_reason"))
        if provider_error is not None:
            return WebDiffResponse(
                status="blocked",
                warnings=self._warnings(payload),
                error_reason=provider_error,
            )
        changed = payload.get("changed")
        if not isinstance(changed, bool):
            return WebDiffResponse(status="insufficient", error_reason="missing_changed_flag")
        return WebDiffResponse(
            status="ok",
            changed=changed,
            current_content_hash=self._optional_hash(payload.get("current_content_hash")),
            previous_content_hash=self._optional_hash(payload.get("previous_content_hash")),
            warnings=self._warnings(payload),
        )

    def _post(self, tool: str, payload: Mapping[str, object]) -> tuple[dict[str, Any] | None, str | None]:
        if tool not in {"search", "fetch", "extract", "diff"}:
            raise ValueError(f"wigolo tool is not permitted by this client: {tool}")
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = Request(
            f"{self.base_url}/v1/{tool}",
            data=body,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self.token}"} if self.token else {}),
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read()
        except HTTPError as exc:
            return None, f"http_{exc.code}"
        except TimeoutError:
            return None, "timeout"
        except (URLError, OSError):
            return None, "transport_error"
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None, "invalid_json"
        if not isinstance(decoded, dict):
            return None, "invalid_response_envelope"
        return decoded, None

    @staticmethod
    def _blocked_fetch(
        url: str,
        now: datetime,
        reason: str,
        canonical_url: str | None = None,
    ) -> WebFetchResult:
        return WebFetchResult(
            status="blocked",
            url=url,
            canonical_url=canonical_url or url,
            retrieved_at=now,
            error_reason=reason,
        )

    @staticmethod
    def _parse_spans(payload: Mapping[str, Any], content: str) -> tuple[WebEvidenceSpan, ...]:
        raw_items = payload.get("citations", payload.get("evidence", []))
        if not isinstance(raw_items, list):
            return ()
        spans: list[WebEvidenceSpan] = []
        for index, item in enumerate(raw_items):
            if not isinstance(item, Mapping):
                continue
            raw_span = item.get("source_span", item)
            if not isinstance(raw_span, Mapping):
                continue
            start = raw_span.get("start", raw_span.get("char_start"))
            end = raw_span.get("end", raw_span.get("char_end"))
            text = raw_span.get("text", item.get("text", item.get("excerpt")))
            if not isinstance(start, int) or not isinstance(end, int) or not isinstance(text, str):
                continue
            span = WebEvidenceSpan(
                start=start,
                end=end,
                unit=raw_span.get("unit", "character"),
                text=text,
                citation_id=str(item.get("citation_id", f"citation-{index + 1}")),
            )
            spans.append(normalize_evidence_span(content, span))
        return tuple(spans)

    @staticmethod
    def _candidate(item: Mapping[str, Any]) -> WebSearchCandidate:
        return WebSearchCandidate(
            title=str(item.get("title") or item.get("url")),
            url=str(item["url"]),
            snippet=str(item.get("snippet") or ""),
            relevance_score=(
                float(item["relevance_score"])
                if isinstance(item.get("relevance_score"), (int, float))
                else None
            ),
        )

    @staticmethod
    def _warnings(payload: Mapping[str, Any]) -> tuple[str, ...]:
        warning = payload.get("warning")
        if isinstance(warning, str) and warning:
            return (warning,)
        warnings = payload.get("warnings")
        if isinstance(warnings, list):
            return tuple(str(item) for item in warnings if item)
        return ()

    @staticmethod
    def _string(value: object, default: str) -> str:
        return value if isinstance(value, str) and value else default

    @staticmethod
    def _optional_string(value: object) -> str | None:
        return value if isinstance(value, str) and value else None

    @staticmethod
    def _optional_hash(value: object) -> str | None:
        return value if isinstance(value, str) and len(value) == 64 else None
