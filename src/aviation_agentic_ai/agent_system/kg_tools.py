"""Read-only context tools for the Knowledge Graph Construction Agent.

The model receives references and stable identifiers in its prompt, then
chooses which bounded context to inspect. Tool results contain only the active
Schema Guide slice and the three upstream EvidenceCards; they never expose a
filesystem path, credentials, Neo4j, or a graph-write operation.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from langchain_core.tools import BaseTool, tool
from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    EvidenceCard,
    EvidenceClaim,
    StrictModel,
)
from aviation_agentic_ai.agent_system.schema_guide import SchemaGuide


class KGToolError(RuntimeError):
    """Raised when a construction-context lookup violates its session scope."""


class EvidenceCardRole(str, Enum):
    """Upstream evidence-card roles visible to the KG Construction Agent."""

    ADVISORY = "advisory"
    FACILITY = "facility"
    TERMINOLOGY = "terminology"


class GetSchemaContextInput(StrictModel):
    """The already-resolved event class whose active profile is requested."""

    event_class: str = Field(min_length=1)


class GetSourceEvidenceInput(StrictModel):
    """One to three upstream EvidenceCards to inspect."""

    roles: list[EvidenceCardRole] = Field(min_length=1, max_length=3)


class ResolveCanonicalRefInput(StrictModel):
    """One canonical ID already supplied as an available reference."""

    canonical_ref: str = Field(min_length=1)


class KGConstructionToolResult(StrictModel):
    """One deterministic observation returned to the construction model."""

    tool: Literal[
        "get_schema_context",
        "get_source_evidence",
        "resolve_canonical_ref",
    ]
    status: Literal["ok"] = "ok"
    result_refs: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)


class KGVisibleEvidenceCard(StrictModel):
    """Minimal event-evidence projection exposed to the KG model."""

    agent_role: str
    status: AgentStatus
    claims: list[EvidenceClaim]
    canonical_refs: list[str]


def project_kg_visible_evidence(
    card: EvidenceCard,
    *,
    allowed_source_ids: set[str],
) -> KGVisibleEvidenceCard:
    """Keep only accepted event claims and canonical references they use."""

    claims = sorted(
        (
            claim.model_copy(update={"uncertainty": None})
            for claim in card.claims
            if claim.source_id in allowed_source_ids
        ),
        key=lambda claim: (
            claim.source_id,
            claim.field_name,
            claim.canonical_ref or "",
            claim.value,
            claim.evidence_text,
        ),
    )
    return KGVisibleEvidenceCard(
        agent_role=card.agent_role,
        status=card.status,
        claims=claims,
        canonical_refs=sorted(
            {
                claim.canonical_ref
                for claim in claims
                if claim.canonical_ref is not None
            }
        ),
    )


class KGConstructionToolGateway:
    """Session-scoped authority boundary behind the construction tools."""

    def __init__(
        self,
        *,
        guide: SchemaGuide,
        event_class: str,
        evidence_cards: dict[str, EvidenceCard],
        canonical_entities: dict[str, str],
        allowed_source_ids: set[str],
    ) -> None:
        self.guide = guide
        self.event_class = event_class
        self.evidence_cards = dict(evidence_cards)
        self.canonical_entities = dict(canonical_entities)
        self.allowed_source_ids = set(allowed_source_ids)

    def get_schema_context(self, *, event_class: str) -> KGConstructionToolResult:
        if event_class != self.event_class:
            raise KGToolError(f"event class is outside the current task: {event_class}")
        return KGConstructionToolResult(
            tool="get_schema_context",
            result_refs=[self.guide.schema_slice_id],
            payload={
                "schema_slice_id": self.guide.schema_slice_id,
                "schema_checksum": self.guide.checksum,
                "event_class": event_class,
                "context": self.guide.compact_context_for_event(event_class),
            },
        )

    def get_source_evidence(
        self,
        *,
        roles: list[EvidenceCardRole | str],
    ) -> KGConstructionToolResult:
        requested = [str(getattr(role, "value", role)) for role in roles]
        if len(requested) != len(set(requested)):
            raise KGToolError("duplicate EvidenceCard roles are not allowed")
        unknown = sorted(set(requested) - set(self.evidence_cards))
        if unknown:
            raise KGToolError(f"EvidenceCard roles are outside the current task: {unknown}")

        cards = [
            project_kg_visible_evidence(
                self.evidence_cards[role],
                allowed_source_ids=self.allowed_source_ids,
            )
            for role in requested
        ]
        source_ids = sorted(
            {
                claim.source_id
                for card in cards
                for claim in card.claims
            }
        )
        return KGConstructionToolResult(
            tool="get_source_evidence",
            result_refs=[f"evidence:{role}" for role in requested],
            source_ids=source_ids,
            payload={
                "evidence_cards": [
                    card.model_dump(mode="json")
                    for card in cards
                ]
            },
        )

    def resolve_canonical_ref(
        self,
        *,
        canonical_ref: str,
    ) -> KGConstructionToolResult:
        if canonical_ref not in self.canonical_entities:
            raise KGToolError(
                f"canonical reference is outside the current task: {canonical_ref}"
            )
        return KGConstructionToolResult(
            tool="resolve_canonical_ref",
            result_refs=[canonical_ref],
            payload={
                "canonical_ref": canonical_ref,
                "ontology_class": self.canonical_entities[canonical_ref],
            },
        )


def build_kg_construction_tools(
    gateway: KGConstructionToolGateway,
) -> list[BaseTool]:
    """Build the three model-visible read-only context tools."""

    @tool("get_schema_context", args_schema=GetSchemaContextInput)
    def get_schema_context(event_class: str) -> str:
        """Read the active ontology profile for the resolved event class."""

        return gateway.get_schema_context(event_class=event_class).model_dump_json()

    @tool("get_source_evidence", args_schema=GetSourceEvidenceInput)
    def get_source_evidence(roles: list[EvidenceCardRole]) -> str:
        """Read selected upstream EvidenceCards with exact source spans."""

        return gateway.get_source_evidence(roles=roles).model_dump_json()

    @tool("resolve_canonical_ref", args_schema=ResolveCanonicalRefInput)
    def resolve_canonical_ref(canonical_ref: str) -> str:
        """Read the ontology class for one already-resolved canonical ID."""

        return gateway.resolve_canonical_ref(
            canonical_ref=canonical_ref
        ).model_dump_json()

    return [get_schema_context, get_source_evidence, resolve_canonical_ref]


def kg_tool_registry(tools: list[BaseTool]) -> dict[str, BaseTool]:
    """Index construction tools by their framework-visible names."""

    registry = {tool_.name: tool_ for tool_ in tools}
    if len(registry) != len(tools):
        raise KGToolError("duplicate KG Construction Agent tool name")
    return registry


__all__ = [
    "EvidenceCardRole",
    "GetSchemaContextInput",
    "GetSourceEvidenceInput",
    "KGConstructionToolGateway",
    "KGConstructionToolResult",
    "KGVisibleEvidenceCard",
    "KGToolError",
    "ResolveCanonicalRefInput",
    "build_kg_construction_tools",
    "kg_tool_registry",
    "project_kg_visible_evidence",
]
