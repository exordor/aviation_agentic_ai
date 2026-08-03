"""Framework-level checks for document adapter boundaries."""

from aviation_agentic_ai.agent_system.adapters.faa_order import (
    ADAPTER_ID,
    SOURCE_KEY,
    run_faa_order_ingestion,
    run_faa_order_kg,
)


def test_faa_order_adapter_is_explicitly_scoped() -> None:
    assert ADAPTER_ID == "document:faa-order"
    assert SOURCE_KEY == "faa_order_7210_3ee"
    assert callable(run_faa_order_ingestion)
    assert callable(run_faa_order_kg)
