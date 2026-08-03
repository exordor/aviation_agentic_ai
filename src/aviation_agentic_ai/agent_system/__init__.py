"""ATMONTO-grounded Agentic HybridRAG runtime (system mainline).

This package implements the runnable system mainline:

    ingest configured aviation source records incrementally
    -> deterministic AdvisoryParser and authority services
    -> shared Semantic Resolution Agent only for genuine ambiguity
    -> deterministic Weather/BTS preparation
    -> deterministic Event Evidence Integration service
    -> event-patch Formal Graph Kernel admissibility check
    -> multi-profile Formal Publication Kernel
    -> persistent versioned evidence and semantic store
    -> rebuildable full-text, vector, RDF, and Neo4j views
    -> always-on bounded HybridRAG Query Agent

LangGraph expresses the fixed topology; LangChain is used only when a
conditional Agent path activates. The write-free Formal Publication Kernel is
the sole final authority across the NASA ATMONTO decision profile, Weather,
and public-observation profiles. Payload-free Agent usage records are attached
to ingestion runs in the evidence store. There is no Critic, separate Verifier
role, Self-Refine, Gold workflow, LLM judge, or comparison-experiment scoring
in this package.
"""

from __future__ import annotations
