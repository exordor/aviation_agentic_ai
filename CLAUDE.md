# CLAUDE.md

Compatibility instructions for tools that read this file.

`AGENTS.md` is authoritative. For current project context, read:

1. `RESEARCH_AUDIT.md`
2. `GOALS.md`
3. the task-specific design or interface document

Do not preload archived experiments, historical stage reports, ignored batch
snapshots/provider outputs, or the paused browser prototype.

## Current Scope

Aviation Agentic AI is an **ATMONTO-Grounded Agentic HybridRAG for
Heterogeneous Aviation Knowledge Integration**. Its active domains publish
ATMONTO-aligned TMI, Flight/Airspace, reference, Weather, and reviewed
cross-source association roots. The retrospective FAA ATCSCC material is a
regression vertical slice; dataset and temporal-scope configuration determine
the research material.

The TMI regression slice is rooted at an admitted ATMONTO
`TrafficManagementInitiative` instance. Event Evidence Integration is a
deterministic TMI service that compiles source-supported sealed evidence or
returns honest `insufficient`. The write-free Formal Publication Kernel and
generic knowledge-root spine are shared across TMI and Flight/Airspace
profiles; dataset and temporal-scope configuration determines research
material.

The versioned SQLite evidence store is the authoritative persisted layer.
SQLite FTS5, two Chroma collections, event graph views, RDF/Turtle, and Neo4j
are rebuildable indexes, views, or all-root exports. Every valid
natural-language `ask` activates the Query Agent. A first LLM routing call
selects `source`, `tmi`, and/or `flight_airspace`; the Agent then uses the
relevant subset of 18 read-only tools under a 6-turn, 6-per-turn, 10-total-tool
budget before producing evidence-bound statements.

The project does not currently claim a formal decision-process model, causal
explanation, operational effectiveness, historical recommendation, complete
aviation coverage, or live ATC decision support. Weather associations remain
non-causal. BTS observations are not FAA demand, AAR, capacity, EDCT, decision
rationale, or proof that a TMI caused an outcome.

## Repository Rules

- Keep workflows CLI-first and reproducible.
- Keep source families and evidence roles distinct.
- Treat schema validity, evidence support, canonical identity, and reviewed
  semantic correctness as different claims.
- Preserve unrelated user changes and generated artifacts.
- Keep credentials, model caches, local corpora, and provider output out of Git.
- Use tracked-file scans for current-context hygiene.

## Verification

- Code changes: `uv run ruff check .` and `uv run pytest -q`.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
