# CLAUDE.md

Compatibility instructions for tools that read this file.

`AGENTS.md` is authoritative. For current project context, read:

1. `RESEARCH_AUDIT.md`
2. `GOALS.md`
3. the task-specific design or interface document

Do not preload archived experiments, historical stage reports, ignored batch
snapshots/provider outputs, or the paused browser prototype.

## Current Scope

Aviation Agentic AI is an ontology-grounded aviation knowledge-integration and
HybridRAG system. Its current vertical slice converts retrospective FAA ATCSCC
records into ATMONTO-aligned TMI-event facts, optional Weather facts, and
source-qualified BTS public observations.

The admitted ATMONTO `TrafficManagementInitiative` instance is the formal
knowledge root. Event Evidence Integration is a deterministic service that
compiles source-supported sealed evidence or returns honest `insufficient`.
The write-free Formal Publication Kernel is the only publication authority and
accepts the TMI, Weather, and public-observation profiles.

The versioned SQLite evidence store is the authoritative persisted layer.
SQLite FTS5, two Chroma collections, event graph views, RDF/Turtle, and Neo4j
are rebuildable indexes, views, or exports. Every valid natural-language `ask`
activates the Query Agent, which selects among nine read-only exact, Weather,
BTS, graph, lexical, vector, event-ranking, and source-read tools before
producing evidence-bound statements.

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
