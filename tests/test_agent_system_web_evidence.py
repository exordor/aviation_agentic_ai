from __future__ import annotations

import io
import json
import hashlib
from datetime import UTC, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.web_evidence_ingestion import (
    collect_web_seed,
    normalize_web_fetch,
)
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
    WebSourceSeed,
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


def _seed(url: str = "https://www.faa.gov/reference") -> WebSourceSeed:
    return WebSourceSeed(
        seed_id="faa-reference",
        url=url,
        authority="FAA",
        document_role="faa_reference",
        parser_profile="faa_reference_document_v1",
        allowed_domains=("faa.gov",),
        max_pages=1,
    )


def _fetch_result(
    content: str,
    *,
    url: str = "https://www.faa.gov/reference",
    canonical_url: str | None = None,
    retrieved_at: datetime | None = None,
    status: str = "ok",
) -> WebFetchResult:
    return WebFetchResult(
        status=status,
        url=url,
        canonical_url=canonical_url or url,
        title="FAA reference",
        media_type="text/html",
        markdown=content if status == "ok" else "",
        spans=(
            WebEvidenceSpan(
                start=0,
                end=len(content),
                unit="character",
                text=content,
                citation_id="full",
            ),
        )
        if status == "ok"
        else (),
        retrieved_at=retrieved_at or datetime.now(UTC),
        content_hash=(hashlib.sha256(content.encode("utf-8")).hexdigest() if status == "ok" else None),
        error_reason=("sidecar_unavailable" if status == "blocked" else "empty_content" if status == "insufficient" else None),
    )


class _SequenceWebClient:
    def __init__(self, results: list[WebFetchResult]) -> None:
        self.results = results
        self.requests: list[WebFetchRequest] = []

    def fetch(self, request: WebFetchRequest) -> WebFetchResult:
        self.requests.append(request)
        return self.results.pop(0)


def _open_web_store(tmp_path: Path) -> AviationEvidenceStore:
    return AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:web-test",
        create=True,
    )


def test_normalize_web_fetch_uses_canonical_url_and_checksum_identity() -> None:
    content = "FAA 雷雨 reference"
    result = _fetch_result(
        content,
        url="https://FAA.gov:443/reference#heading",
        canonical_url="https://faa.gov/reference#heading",
    )

    version, anchors = normalize_web_fetch(result, _seed(result.url))

    assert version.family is SourceFamily.WEB_DOCUMENT
    assert version.source_url == "https://faa.gov/reference"
    assert version.source_id.startswith("web-document:")
    assert version.content_sha256 == hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert version.source_version_id.endswith(version.content_sha256[:12]) is False
    assert {anchor.anchor_kind for anchor in anchors} == {"full_record"}
    assert all("request" not in key.lower() for key in version.metadata)
    assert "raw_request" not in version.metadata


def test_normalize_web_fetch_rejects_span_text_mismatch() -> None:
    result = _fetch_result("FAA reference")
    result = result.model_copy(
        update={
            "spans": (
                WebEvidenceSpan(
                    start=0,
                    end=3,
                    unit="character",
                    text="NOT",
                    citation_id="bad",
                ),
            )
        }
    )

    with pytest.raises(ValueError, match="does not match fetched content"):
        normalize_web_fetch(result, _seed())


def test_collect_web_seed_deduplicates_content_and_indexes_web_text(tmp_path: Path) -> None:
    content = "FAA reference content"
    client = _SequenceWebClient(
        [
            _fetch_result(content, retrieved_at=datetime(2026, 8, 1, 8, 0, tzinfo=UTC)),
            _fetch_result(content, retrieved_at=datetime(2026, 8, 1, 9, 0, tzinfo=UTC)),
        ]
    )
    store = _open_web_store(tmp_path)
    try:
        first = collect_web_seed({}, _seed(), client, store, now=datetime.now(UTC))
        second = collect_web_seed({}, _seed(), client, store, now=datetime.now(UTC))

        assert first.status == second.status == "ok"
        assert first.source_version_ids == second.source_version_ids
        assert len(store.list_source_versions(families=(SourceFamily.WEB_DOCUMENT,))) == 1
        chunks = store.list_source_chunks(chunk_kind="source_record")
        assert len(chunks) == 1
        assert chunks[0].source_version_id == first.source_version_ids[0]
        assert store.search_source_text(
            "reference",
            families=(SourceFamily.WEB_DOCUMENT,),
        )[0].source_version_id == first.source_version_ids[0]
    finally:
        store.close()


def test_collect_web_seed_changed_content_creates_immutable_version(tmp_path: Path) -> None:
    client = _SequenceWebClient(
        [
            _fetch_result("FAA reference v1"),
            _fetch_result("FAA reference v2"),
        ]
    )
    store = _open_web_store(tmp_path)
    try:
        first = collect_web_seed({}, _seed(), client, store, now=datetime.now(UTC))
        second = collect_web_seed({}, _seed(), client, store, now=datetime.now(UTC))

        assert first.status == second.status == "ok"
        assert first.source_version_ids != second.source_version_ids
        versions = store.list_source_versions(families=(SourceFamily.WEB_DOCUMENT,))
        assert len(versions) == 2
        assert store.get_source_version(first.source_version_ids[0]) is not None
        assert store.get_latest_source_version(versions[0].source_id).source_version_id == second.source_version_ids[0]
    finally:
        store.close()


def test_blocked_or_insufficient_fetch_preserves_previous_version(tmp_path: Path) -> None:
    client = _SequenceWebClient(
        [
            _fetch_result("FAA reference v1"),
            _fetch_result("", status="blocked"),
            _fetch_result("", status="insufficient"),
        ]
    )
    store = _open_web_store(tmp_path)
    try:
        accepted = collect_web_seed({}, _seed(), client, store, now=datetime.now(UTC))
        blocked = collect_web_seed({}, _seed(), client, store, now=datetime.now(UTC))
        insufficient = collect_web_seed({}, _seed(), client, store, now=datetime.now(UTC))

        assert accepted.status == "ok"
        assert blocked.status == "blocked"
        assert insufficient.status == "insufficient"
        assert store.get_latest_source_version(
            normalize_web_fetch(_fetch_result("FAA reference v1"), _seed())[0].source_id
        ).source_version_id == accepted.source_version_ids[0]
        assert len(store.list_source_versions(families=(SourceFamily.WEB_DOCUMENT,))) == 1
    finally:
        store.close()


def test_collect_web_seed_rejects_url_outside_global_allowlist_before_fetch(
    tmp_path: Path,
) -> None:
    client = _SequenceWebClient([_fetch_result("must not fetch")])
    store = _open_web_store(tmp_path)
    try:
        result = collect_web_seed(
            {"allowed_domains": ["fly.faa.gov"]},
            _seed("https://www.faa.gov/reference"),
            client,
            store,
            now=datetime.now(UTC),
        )
        assert result.status == "blocked"
        assert result.error_reason is not None and result.error_reason.startswith("policy:")
        assert client.requests == []
    finally:
        store.close()
