"""Behavior coverage for the current authority-service architecture."""

from __future__ import annotations

from aviation_agentic_ai.agent_system.authority_resolution import (
    AuthorityResolutionResult,
)


def test_authority_services_expose_source_bound_result_not_agent_envelope() -> None:
    """Catches a return to the removed Facility/Terminology Agent envelope."""

    fields = AuthorityResolutionResult.__dataclass_fields__

    assert "evidence_card" in fields
    assert "agent_result" not in fields
