"""FAA Order document adapter.

The framework speaks in terms of document ingestion and ontology KG builds;
this module is the only adapter boundary that knows the FAA Order source key
and its FAA-specific extraction profile.
"""

from aviation_agentic_ai.agent_system.faa_order_document import (
    load_faa_order_source_package,
)
from aviation_agentic_ai.agent_system.faa_order_ingestion import (
    configured_faa_order_document_options,
    register_faa_order_source,
    run_faa_order_ingestion,
)
from aviation_agentic_ai.agent_system.faa_order_kg import run_faa_order_kg

SOURCE_KEY = "faa_order_7210_3ee"
ADAPTER_ID = "document:faa-order"

__all__ = [
    "ADAPTER_ID",
    "SOURCE_KEY",
    "configured_faa_order_document_options",
    "load_faa_order_source_package",
    "register_faa_order_source",
    "run_faa_order_ingestion",
    "run_faa_order_kg",
]
