"""Optional, read-only Web Evidence tools for the bounded Query Agent.

The web tools are deliberately separate from ingestion.  They are exposed only
when the caller has explicitly authorized live web access and the configured
wigolo sidecar is enabled.  Search returns candidates only; fetch and extract
bind successful content to deterministic source/version/anchor identifiers in
memory, without writing to the authoritative SQLite store.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from langchain_core.tools import BaseTool, tool

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryEvidence,
    HybridQuerySupportRecord,
    HybridQueryToolObservation,
)
from aviation_agentic_ai.agent_system.web_evidence_client import (
    WebEvidenceClient,
)
from aviation_agentic_ai.agent_system.web_evidence_contracts import (
    WebEvidenceConfig,
    WebExtractRequest,
    WebFetchRequest,
    WebSearchRequest,
)
from aviation_agentic_ai.agent_system.web_evidence_ingestion import (
    normalize_web_fetch,
    validate_web_url_allowlist,
)


class WebQueryGatewayError(ValueError):
    """A caller or policy error that must not become a network request."""


@dataclass(frozen=True, slots=True)
class WebQueryGateway:
    """Read-only sidecar gateway with operator-configured URL bounds."""

    client: WebEvidenceClient
    config: WebEvidenceConfig

    @property
    def allowed_domains(self) -> tuple[str, ...]:
        configured = self.config.allowed_domains
        if configured:
            return configured
        return tuple(
            sorted(
                {
                    domain
                    for seed in self.config.seeds
                    for domain in seed.allowed_domains
                }
            )
        )

    def _require_domains(self) -> tuple[str, ...]:
        domains = self.allowed_domains
        if not domains:
            raise WebQueryGatewayError(
                "web query requires at least one configured allowed domain"
            )
        return domains

    def _canonical_url(self, url: str) -> str:
        domains = self._require_domains()
        try:
            return validate_web_url_allowlist(url, domains)
        except ValueError as exc:
            raise WebQueryGatewayError(str(exc)) from exc

    def _bounded_max_chars(self, requested: int) -> int:
        return min(requested, self.config.limits.max_content_chars)

    def _query_seed(self, url: str):
        """Build an in-memory source seed for exact query-time identities."""

        from aviation_agentic_ai.agent_system.web_evidence_contracts import (
            WebSourceSeed,
        )

        canonical = self._canonical_url(url)
        return WebSourceSeed(
            seed_id="query-web-document",
            url=canonical,
            authority="operator-authorized web evidence",
            document_role="query_evidence",
            parser_profile=self.config.adapter_version,
            allowed_domains=self.allowed_domains,
            max_pages=1,
        )

    def search(self, request: WebSearchRequest) -> HybridQueryToolObservation:
        try:
            domains = self._require_domains()
        except WebQueryGatewayError as exc:
            return _blocked(str(exc))
        bounded = request.model_copy(update={"allowed_domains": domains})
        try:
            response = self.client.search(bounded)
        except Exception as exc:
            return _blocked(f"web search client failed: {type(exc).__name__}")
        candidates = []
        for candidate in response.candidates:
            try:
                canonical = self._canonical_url(candidate.url)
            except WebQueryGatewayError:
                continue
            candidates.append(
                {
                    "title": candidate.title,
                    "url": canonical,
                    "snippet": candidate.snippet,
                    "relevance_score": candidate.relevance_score,
                }
            )
        status = "ok" if candidates and response.status == "ok" else response.status
        if response.status == "ok" and not candidates:
            status = "insufficient"
        content = _json(
            {
                "status": status,
                "candidates": candidates,
                "warnings": response.warnings,
                "evidence_note": (
                    "Search candidates are not evidence. Fetch an allowlisted "
                    "URL before citing a web source."
                ),
            }
        )
        return HybridQueryToolObservation(
            status=status,
            content=content,
            limitation=response.error_reason or "",
        )

    def fetch(self, request: WebFetchRequest) -> HybridQueryToolObservation:
        try:
            canonical = self._canonical_url(request.url)
        except WebQueryGatewayError as exc:
            return _blocked(str(exc))
        bounded = request.model_copy(
            update={
                "url": canonical,
                "max_content_chars": self._bounded_max_chars(
                    request.max_content_chars
                ),
            }
        )
        try:
            result = self.client.fetch(bounded)
        except Exception as exc:
            return _blocked(f"web fetch client failed: {type(exc).__name__}")
        return self._exact_fetch_observation(result, canonical)

    def extract(self, request: WebExtractRequest) -> HybridQueryToolObservation:
        try:
            canonical = self._canonical_url(request.url)
        except WebQueryGatewayError as exc:
            return _blocked(str(exc))
        bounded_extract = request.model_copy(
            update={
                "url": canonical,
                "max_content_chars": self._bounded_max_chars(
                    request.max_content_chars
                ),
            }
        )
        try:
            extracted = self.client.extract(bounded_extract)
        except Exception as exc:
            return _blocked(f"web extract client failed: {type(exc).__name__}")
        if extracted.status == "blocked":
            return _blocked(extracted.error_reason or "web extraction blocked")
        if extracted.status != "ok" or not extracted.fields:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json(
                    {
                        "status": "insufficient",
                        "fields": extracted.fields,
                        "warnings": extracted.warnings,
                        "evidence_note": (
                            "Structured extraction without exact source spans "
                            "is not citable."
                        ),
                    }
                ),
                limitation=extracted.error_reason or "missing extracted fields",
            )

        # The extract response contains fields but not necessarily the source
        # text.  A paired fetch is required to bind its spans to immutable
        # content before the model can cite the result.
        try:
            fetched = self.client.fetch(
                WebFetchRequest(
                    url=canonical,
                    mode=bounded_extract.mode,
                    max_content_chars=bounded_extract.max_content_chars,
                )
            )
        except Exception as exc:
            return _blocked(f"web extract grounding fetch failed: {type(exc).__name__}")
        if fetched.status != "ok":
            return HybridQueryToolObservation(
                status=fetched.status,
                content=_json(
                    {
                        "status": fetched.status,
                        "fields": extracted.fields,
                        "warning": fetched.warning,
                    }
                ),
                limitation=fetched.error_reason or "grounding fetch unavailable",
            )
        grounded = fetched.model_copy(
            update={"spans": tuple(extracted.spans)}
        )
        observation = self._exact_fetch_observation(grounded, canonical)
        if observation.status != "ok":
            return observation
        payload = json.loads(observation.content)
        payload["fields"] = extracted.fields
        return observation.model_copy(
            update={"content": _json(payload)}
        )

    def _exact_fetch_observation(
        self,
        result,
        requested_url: str,
    ) -> HybridQueryToolObservation:
        if result.status != "ok":
            return HybridQueryToolObservation(
                status=result.status,
                content=_json(
                    {
                        "status": result.status,
                        "url": requested_url,
                        "warning": result.warning,
                    }
                ),
                limitation=result.error_reason or "web fetch unavailable",
            )
        try:
            seed = self._query_seed(requested_url)
            version, anchors = normalize_web_fetch(
                result,
                seed,
                adapter_version=self.config.adapter_version,
            )
        except (TypeError, ValueError) as exc:
            return _blocked(f"web fetch evidence validation failed: {exc}")
        anchor_ids = tuple(anchor.source_anchor_id for anchor in anchors)
        support = HybridQuerySupportRecord(
            kind="source_record",
            source_ids=(version.source_id,),
            source_version_ids=(version.source_version_id,),
            source_anchor_ids=anchor_ids,
        )
        return HybridQueryToolObservation(
            status="ok",
            content=_json(
                {
                    "status": "ok",
                    "family": "web_document",
                    "url": requested_url,
                    "canonical_url": version.source_url,
                    "title": result.title,
                    "source_id": version.source_id,
                    "source_version_id": version.source_version_id,
                    "source_anchor_ids": anchor_ids,
                    "content_sha256": version.content_sha256,
                    "bounded_text": version.content,
                }
            ),
            details=HybridQueryEvidence(
                source_ids=(version.source_id,),
                source_version_ids=(version.source_version_id,),
                source_anchor_ids=anchor_ids,
            ),
            support_records=(support,),
        )


def _json(payload: object) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _blocked(reason: str) -> HybridQueryToolObservation:
    return HybridQueryToolObservation(
        status="blocked",
        content=_json({"status": "blocked", "reason": reason}),
        limitation=reason,
    )


def build_web_query_tools(
    client: WebEvidenceClient,
    config: WebEvidenceConfig,
) -> list[BaseTool]:
    """Build the three explicitly authorized, read-only web tools."""

    if not config.enabled:
        raise ValueError("web query tools require an enabled web evidence configuration")
    gateway = WebQueryGateway(client=client, config=config)

    @tool("web_search", args_schema=WebSearchRequest)
    def web_search_tool(**kwargs: object) -> dict[str, object]:
        """Return allowlisted web candidates; candidates are not evidence."""

        return gateway.search(
            WebSearchRequest.model_validate(kwargs)
        ).model_dump(mode="json")

    @tool("web_fetch", args_schema=WebFetchRequest)
    def web_fetch_tool(**kwargs: object) -> dict[str, object]:
        """Fetch exact allowlisted web content with source-anchor support."""

        return gateway.fetch(
            WebFetchRequest.model_validate(kwargs)
        ).model_dump(mode="json")

    @tool("web_extract", args_schema=WebExtractRequest)
    def web_extract_tool(**kwargs: object) -> dict[str, object]:
        """Extract fields only when a paired fetch can ground exact spans."""

        return gateway.extract(
            WebExtractRequest.model_validate(kwargs)
        ).model_dump(mode="json")

    return [web_search_tool, web_fetch_tool, web_extract_tool]


__all__ = ["WebQueryGateway", "build_web_query_tools"]
