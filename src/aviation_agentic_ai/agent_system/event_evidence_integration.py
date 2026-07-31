"""Deterministic result wrapper for TMI event evidence integration."""

from __future__ import annotations

from dataclasses import dataclass

from aviation_agentic_ai.agent_system.construction_contracts import (
    EventEvidenceIntegrationFeedback,
    EventEvidenceIntegrationProposal,
)

# Retained temporarily for the frozen historical evaluator, which is removed
# from the active path in a later batch.
MAX_INTEGRATION_TOOL_CALLS = 1
MAX_INTEGRATION_PROVIDER_TURNS = 2


@dataclass(frozen=True)
class EventEvidenceIntegrationResult:
    """Result of deterministic event-evidence compilation and validation."""

    proposal: EventEvidenceIntegrationProposal
    feedback: EventEvidenceIntegrationFeedback | None = None
    failure_reason: str | None = None
