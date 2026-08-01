from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.web_evidence_client import (
    HttpWigoloWebClient,
    normalize_evidence_span,
    validate_ingestion_tools,
)
from aviation_agentic_ai.agent_system.web_evidence_contracts import (
    WebDiffRequest,
    WebDiffResponse,
    WebEvidenceSpan,
    WebExtractRequest,
    WebExtractResponse,
    WebFetchRequest,
    WebFetchResult,
    WebSearchRequest,
    WebSearchResponse,
)


def _response(payload: object, *, status: int = 200) -> io.BytesIO:
    raw = json.dumps(payload).encode("utf-8")
    stream = io.BytesIO(raw)
    stream.status = status  # type: ignore[attr-defined]
    return stream


def test_web_document_is_a_distinct_source_family() -> None:
    assert SourceFamily.WEB_DOCUMENT.value == "web_document"


def test_transport_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        WebFetchResult(
            status="ok",
            url="https://www.faa.gov/page",
            canonical_url="https://www.faa.gov/page",
            media_type="text/html",
            markdown="FAA evidence",
            retrieved_at=datetime.now(timezone.utc),
            content_hash="a" * 64,
            unexpected="must not cross the adapter boundary",
        )


def test_byte_span_is_normalized_to_python_character_offsets() -> None:
    content = "Weather: 雷雨 near KJFK"
    text = "雷雨"
    start = len("Weather: ".encode("utf-8"))
    end = start + len(text.encode("utf-8"))
    span = WebEvidenceSpan(start=start, end=end, unit="byte", text=text, citation_id="c1")

    normalized = normalize_evidence_span(content, span)

    assert normalized.unit == "character"
    assert (normalized.start, normalized.end) == (9, 11)
    assert content[normalized.start : normalized.end] == text


def test_byte_span_that_cuts_a_utf8_codepoint_is_rejected() -> None:
    content = "雷雨"
    span = WebEvidenceSpan(start=1, end=4, unit="byte", text="雷", citation_id="c1")

    with pytest.raises(ValueError, match="UTF-8 character boundary"):
        normalize_evidence_span(content, span)


def test_ingestion_tools_exclude_research_and_agent_synthesis() -> None:
    assert validate_ingestion_tools(("fetch", "extract", "diff")) == (
        "fetch",
        "extract",
        "diff",
    )

    with pytest.raises(ValueError, match="not permitted for ingestion"):
        validate_ingestion_tools(("fetch", "research"))


def test_fetch_maps_successful_wigolo_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: object, timeout: float) -> io.BytesIO:
        assert timeout == 12.5
        return _response(
            {
                "url": "https://www.faa.gov/page",
                "canonical_url": "https://www.faa.gov/page",
                "title": "FAA page",
                "markdown": "# FAA evidence",
                "media_type": "text/html",
                "citations": [
                    {
                        "citation_id": "c1",
                        "source_span": {"start": 2, "end": 5, "unit": "character", "text": "FAA"},
                    }
                ],
                "cache_status": "miss",
            }
        )

    monkeypatch.setattr(
        "aviation_agentic_ai.agent_system.web_evidence_client.urlopen",
        fake_urlopen,
    )
    client = HttpWigoloWebClient("http://127.0.0.1:3333", None, 12.5)

    result = client.fetch(
        WebFetchRequest(url="https://www.faa.gov/page", max_content_chars=1000)
    )

    assert result.status == "ok"
    assert result.markdown == "# FAA evidence"
    assert result.content_hash == "93d95ce64ae2c0a4898ca8452bd0a2ebc7f793b0bac9c32426b211d41d99b8c2"
    assert result.spans[0].citation_id == "c1"
    assert result.spans[0].unit == "character"


def test_fetch_maps_challenge_response_to_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "aviation_agentic_ai.agent_system.web_evidence_client.urlopen",
        lambda request, timeout: _response(
            {
                "url": "https://www.faa.gov/page",
                "error": "challenge did not clear",
                "error_reason": "blocked_by_challenge",
            }
        ),
    )
    client = HttpWigoloWebClient("http://127.0.0.1:3333", None, 5.0)

    result = client.fetch(WebFetchRequest(url="https://www.faa.gov/page"))

    assert result.status == "blocked"
    assert result.error_reason == "blocked_by_challenge"
    assert result.markdown == ""


def test_fetch_maps_transport_timeout_to_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    def timeout(request: object, timeout: float) -> io.BytesIO:
        raise TimeoutError("sidecar timeout")

    monkeypatch.setattr(
        "aviation_agentic_ai.agent_system.web_evidence_client.urlopen",
        timeout,
    )
    client = HttpWigoloWebClient("http://127.0.0.1:3333", None, 5.0)

    result = client.fetch(WebFetchRequest(url="https://www.faa.gov/page"))

    assert result.status == "blocked"
    assert result.error_reason == "timeout"


def test_search_extract_and_diff_use_pinned_v1_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[tuple[str, dict[str, object]]] = []

    def fake_urlopen(request: object, timeout: float) -> io.BytesIO:
        url = request.full_url  # type: ignore[attr-defined]
        body = json.loads(request.data.decode("utf-8"))  # type: ignore[attr-defined]
        requests.append((url, body))
        if url.endswith("/v1/search"):
            return _response({"results": [{"title": "FAA", "url": "https://www.faa.gov"}]})
        if url.endswith("/v1/extract"):
            return _response({"fields": {"title": "FAA"}, "spans": []})
        return _response(
            {
                "changed": True,
                "current_content_hash": "b" * 64,
                "previous_content_hash": "a" * 64,
            }
        )

    monkeypatch.setattr(
        "aviation_agentic_ai.agent_system.web_evidence_client.urlopen",
        fake_urlopen,
    )
    client = HttpWigoloWebClient("http://127.0.0.1:3333/", "secret", 5.0)

    search = client.search(WebSearchRequest(query="FAA", max_results=2))
    extract = client.extract(WebExtractRequest(url="https://www.faa.gov", schema="reference"))
    diff = client.diff(WebDiffRequest(url="https://www.faa.gov", known_content_hash="a" * 64))

    assert isinstance(search, WebSearchResponse)
    assert search.candidates[0].url == "https://www.faa.gov"
    assert isinstance(extract, WebExtractResponse)
    assert extract.fields == {"title": "FAA"}
    assert isinstance(diff, WebDiffResponse)
    assert diff.changed is True
    assert [url for url, _ in requests] == [
        "http://127.0.0.1:3333/v1/search",
        "http://127.0.0.1:3333/v1/extract",
        "http://127.0.0.1:3333/v1/diff",
    ]


def test_http_errors_are_typed_as_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(request: object, timeout: float) -> io.BytesIO:
        raise HTTPError(
            request.full_url, 403, "forbidden", {}, io.BytesIO(b'{"error_reason":"unauthorized"}')
        )  # type: ignore[attr-defined]

    monkeypatch.setattr(
        "aviation_agentic_ai.agent_system.web_evidence_client.urlopen",
        forbidden,
    )
    client = HttpWigoloWebClient("http://127.0.0.1:3333", "secret", 5.0)

    result = client.fetch(WebFetchRequest(url="https://www.faa.gov/page"))

    assert result.status == "blocked"
    assert result.error_reason == "http_403"


def test_network_errors_are_typed_as_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "aviation_agentic_ai.agent_system.web_evidence_client.urlopen",
        lambda request, timeout: (_ for _ in ()).throw(URLError("connection refused")),
    )
    client = HttpWigoloWebClient("http://127.0.0.1:3333", None, 5.0)

    result = client.fetch(WebFetchRequest(url="https://www.faa.gov/page"))

    assert result.status == "blocked"
    assert result.error_reason == "transport_error"
