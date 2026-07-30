"""Multi-Agent aviation event knowledge system (system mainline).

This package implements the runnable system mainline:

    ingest (one ATCSCC advisory + bounded FAA authority records)
    -> deterministic AdvisoryParser and authority services
    -> shared Semantic Resolution Agent only for genuine ambiguity
    -> deterministic Weather/BTS preparation
    -> canonical compiler or bounded Decision Case Assembly Agent
    -> event-patch Formal Graph Kernel admissibility check
    -> DecisionCase membership finalization
    -> multi-profile Formal Publication Kernel
    -> canonical corpus v2 and rebuildable retrieval/export views
    -> always-on bounded HybridRAG Query Agent

LangGraph expresses the fixed topology; LangChain is used only when a
conditional Agent path activates. The write-free Formal Publication Kernel is
the sole final authority across the NASA ATMONTO decision profile, Weather,
public-observation, and DecisionCase-core profiles. The payload-free Agent
usage sidecar is non-authoritative and cannot change corpus identity. There is
no Critic, separate Verifier role, Self-Refine, Gold workflow, LLM judge, or
comparison-experiment scoring in this package.
"""

from __future__ import annotations
