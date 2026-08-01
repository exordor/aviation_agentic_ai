"""Focused tests for the explicitly authorized read-only web query tools."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    HybridQueryStatement,
    HybridQuerySupportRecord,
    SourceFamily,
)
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.hybrid_query_agent import (
    validate_hybrid_query_statement,
)
from aviation_agentic_ai.agent_system.query_tool_registry import (
    OPTIONAL_QUERY_EVIDENCE_TOOL_NAMES,
    build_query_tool_registry,
)
from aviation_agentic_ai.agent_system.flight_airspace_query_tools import (
    FlightAirspaceQueryGateway,
    build_flight_airspace_query_tools,
)
from aviation_agentic_ai.agent_system.hybrid_query_tools import (
    HybridQueryGateway,
    build_hybrid_query_tools,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
from aviation_agentic_ai.agent_system.web_evidence_contracts import (
    WebDiffResponse,
    WebEvidenceConfig,
    WebEvidenceSpan,
    WebExtractResponse,
    WebFetchResult,
    WebSearchResponse,
)
from aviation_agentic_ai.agent_system.web_query_tools import (
    WebQueryGateway,
    build_web_query_tools,
)


URL = "https://example.test/reference"
CONTENT = "Ground delay programs are described here."
NOW = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)


class FakeWebClient:
    def __init__(self) -> None:
        self.fetch_calls = 0
        self.search_calls = 0
        self.extract_calls = 0

    def fetch(self, request):  # type: ignore[no-untyped-def]
        self.fetch_calls += 1
        return WebFetchResult(
            status="ok",
            url=request.url,
            canonical_url=request.url,
            title="Reference",
            markdown=CONTENT,
            retrieved_at=NOW,
            spans=(
                WebEvidenceSpan(
                    start=0,
                    end=12,
                    unit="character",
                    text="Ground delay",
                    citation_id="span-1",
                ),
            ),
            content_hash=hashlib.sha256(CONTENT.encode()).hexdigest(),
        )

    def search(self, request):  # type: ignore[no-untyped-def]
        self.search_calls += 1
        from aviation_agentic_ai.agent_system.web_evidence_contracts import (
            WebSearchCandidate,
        )

        return WebSearchResponse(
            status="ok",
            candidates=(
                WebSearchCandidate(
                    title="Reference",
                    url=URL,
                    snippet="candidate only",
                ),
            ),
        )

    def extract(self, request):  # type: ignore[no-untyped-def]
        self.extract_calls += 1
        return WebExtractResponse(
            status="ok",
            fields={"topic": "GDP"},
            spans=(
                WebEvidenceSpan(
                    start=0,
                    end=12,
                    unit="character",
                    text="Ground delay",
                    citation_id="extract-1",
                ),
            ),
        )

    def diff(self, request):  # type: ignore[no-untyped-def]
        return WebDiffResponse(status="ok", changed=False)


def _config() -> WebEvidenceConfig:
    return WebEvidenceConfig(
        enabled=True,
        allowed_domains=("example.test",),
        adapter_version="query-test-v1",
    )


def test_web_tools_are_not_part_of_the_default_registry() -> None:
    assert OPTIONAL_QUERY_EVIDENCE_TOOL_NAMES == {
        "web_search",
        "web_fetch",
        "web_extract",
    }


def test_disabled_configuration_cannot_build_web_tools() -> None:
    client = FakeWebClient()
    disabled = _config().model_copy(update={"enabled": False})
    with pytest.raises(ValueError, match="enabled web evidence"):
        build_web_query_tools(client, disabled)


def test_web_tools_are_added_as_one_explicit_family(tmp_path: Path) -> None:
    client = FakeWebClient()
    tools = build_web_query_tools(client, _config())
    store = AviationEvidenceStore.open(
        tmp_path,
        dataset_id="web-query-registry",
        create=True,
    )
    runtime = QueryRuntime(store=store, source_index=None, event_index=None)
    scope = HybridQueryScope()
    registry = build_query_tool_registry(
        [
            *build_hybrid_query_tools(
                HybridQueryGateway(runtime=runtime, scope=scope)
            ),
            *build_flight_airspace_query_tools(
                FlightAirspaceQueryGateway(runtime=runtime, scope=scope)
            ),
            *tools,
        ]
    )
    assert set(registry.family_specs) == {"source", "tmi", "flight_airspace", "web"}
    assert {tool.name for tool in registry.tools_for(("web",))} == {
        tool.name for tool in tools
    }
    store.close()


def test_search_is_candidate_only_and_fetch_has_exact_support() -> None:
    client = FakeWebClient()
    gateway = WebQueryGateway(client=client, config=_config())

    from aviation_agentic_ai.agent_system.web_evidence_contracts import (
        WebFetchRequest,
        WebSearchRequest,
    )

    search = gateway.search(WebSearchRequest(query="GDP"))
    assert search.status == "ok"
    assert search.support_records == ()

    fetched = gateway.fetch(WebFetchRequest(url=URL))
    assert fetched.status == "ok"
    assert fetched.details.source_version_ids
    assert fetched.details.source_anchor_ids
    assert fetched.support_records[0].kind == "source_record"
    assert client.fetch_calls == 1


def test_extract_requires_paired_fetch_and_never_writes_sqlite(tmp_path: Path) -> None:
    store = AviationEvidenceStore.open(
        tmp_path,
        dataset_id="web-query-test",
        create=True,
    )
    before = store.get_knowledge_revision()
    client = FakeWebClient()
    from aviation_agentic_ai.agent_system.web_evidence_contracts import (
        WebExtractRequest,
    )

    observation = WebQueryGateway(client=client, config=_config()).extract(
        WebExtractRequest(url=URL, schema={"topic": "string"})
    )
    assert observation.status == "ok"
    assert observation.details.source_version_ids
    assert client.extract_calls == 1
    assert client.fetch_calls == 1
    assert store.get_knowledge_revision() == before
    assert store.list_source_versions(families=(SourceFamily.WEB_DOCUMENT,)) == ()
    store.close()


def test_web_source_cannot_support_actual_control_claims() -> None:
    statement = HybridQueryStatement(
        kind="source_record",
        text="This page proves actual FAA control of the airport.",
        support_source_ids=("web-document:example",),
        support_source_version_ids=("source-version:example",),
        support_source_anchor_ids=("source-anchor:example",),
    )
    support = HybridQuerySupportRecord(
        kind="source_record",
        source_ids=statement.support_source_ids,
        source_version_ids=statement.support_source_version_ids,
        source_anchor_ids=statement.support_source_anchor_ids,
    )
    assert validate_hybrid_query_statement(statement, [support]) is not None
