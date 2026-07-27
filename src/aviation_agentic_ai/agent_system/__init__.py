"""Multi-Agent aviation event knowledge system (system mainline).

This package implements the runnable system mainline:

    ingest (one ATCSCC advisory + bounded FAA authority records)
    -> deterministic AdvisoryParser and authority services
    -> shared Semantic Resolution Agent only for genuine ambiguity
    -> deterministic Weather/BTS preparation
    -> canonical compiler or bounded Decision Case Assembly Agent
    -> Formal Graph Kernel and profile-owned JSONL/RDF/Neo4j artifacts
    -> bounded Query Agent (graph-grounded answer listing actual source IDs)

LangGraph expresses the fixed topology; LangChain is used only when a
conditional Agent path activates. The Formal Graph Kernel is the sole final
publication authority under the NASA ATMONTO decision profile and the separate
Weather and public-observation profiles. There is no Decision Case Analysis,
Critic, Verification role, Self-Refine, Gold workflow, LLM judge, or
comparison-experiment scoring in this package. Earlier runs require
regeneration after the Batch C.1 cutover.
"""

from __future__ import annotations
