"""Multi-Agent aviation event knowledge system (system mainline).

This package implements the runnable system mainline:

    ingest (one real ATCSCC advisory + NASR facility card + FAA term card)
    -> Advisory Agent, Facility Agent, Terminology Agent, KG Construction Agent
    -> source-bounded event KG (RDF/Turtle + JSONL)
    -> Neo4j projection
    -> Query Agent (KG-grounded answer listing actual source IDs)

LangGraph expresses the fixed multi-Agent topology; LangChain performs model
calls. The KG Construction Agent is ontology-guided via the existing NASA
ATMONTO ATCSCC schema slice. There is no Critic/Verification role, no
Self-Refine, no Gold workflow, no LLM judge, and no comparison-experiment
scoring in this package.
"""

from __future__ import annotations
