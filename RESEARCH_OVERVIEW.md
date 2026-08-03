# Research Overview

This file is a reader-facing pointer, not an independent source of project
status. To avoid parallel descriptions:

- read `RESEARCH_AUDIT.md` for verified current implementation truth;
- read `GOALS.md` for durable research goals, boundaries, and deferred work;
- read `docs/multi_agent_kg_system_design.md` for the normative architecture;
- read `REPRODUCIBILITY.md` for executable source and experiment procedures.

The paper-facing research story is now maintained in the normative design and
the current project audit; a separate architecture-narrative copy is not
maintained.

The project studies an **ATMONTO-Grounded Agentic HybridRAG for Heterogeneous
Aviation Knowledge Integration**. Its research material is selected by source,
dataset, and temporal-scope configuration. ATCSCC TMI, NASA ATMONTO
Flight/Airspace, Weather, FAA reference, and operational records are
interoperable domains, not a fixed historical cohort.

The central method is:

```text
heterogeneous sources
  -> deterministic normalization and evidence anchors
  -> ATMONTO/profile-constrained semantic publication
  -> exact, graph, lexical, and vector retrieval
  -> LLM tool-family routing and bounded evidence loop
  -> statement-level support validation
```

The project demonstrates data query/search, information organization,
information integration, and terminology standardization. It does not claim
causal explanation, operational effectiveness, TMI recommendation, complete
aviation coverage, or reconstruction of internal FAA decision processes.
