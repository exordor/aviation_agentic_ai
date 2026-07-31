"""Deterministic result wrapper for TMI event evidence integration."""

from __future__ import annotations

from dataclasses import dataclass

from aviation_agentic_ai.agent_system.construction_contracts import (
    EventEvidenceIntegrationFeedback,
    EventEvidenceIntegrationProposal,
)


@dataclass(frozen=True)
class EventEvidenceIntegrationResult:
    """Result of deterministic event-evidence compilation and validation."""

    proposal: EventEvidenceIntegrationProposal
    feedback: EventEvidenceIntegrationFeedback | None = None
    failure_reason: str | None = None
