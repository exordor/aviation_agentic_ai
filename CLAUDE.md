# CLAUDE.md

Compatibility instructions for tools that read this file.

`AGENTS.md` is the authoritative repository instruction file. For current
project context, read:

1. `RESEARCH_AUDIT.md`
2. `GOALS.md`
3. the task-specific design or interface document

Do not load the formal experiment, legacy GraphRAG, PHAK, web-demo, or archived
report families unless the task explicitly asks for them.

## Current Scope

Aviation Agentic AI is a system and framework project. It converts one
retrospective FAA ATCSCC advisory and bounded FAA authority records into a
validated event knowledge graph, RDF/Turtle, and a Neo4j projection, then
answers a registered set of decision-record questions with explicit source
evidence. The active Decision Case Graph v1 extension adds deterministic,
time-bounded METAR/TAF context and BTS-reported public operational observations
without adding an Agent role or model call.

LLMs perform bounded interpretation and graph construction. Deterministic
validation is the publication gate.

The project does not currently claim weather-based causal explanation,
historical-case recommendation, full-corpus autonomous processing, general
aviation question answering, or live operational decision support.

BTS-reported observations must never be described as FAA demand, AAR, capacity,
or EDCT. Weather associations remain non-causal, and public operational
observations do not establish that a TMI caused an outcome.

## Repository Rules

- Keep workflows CLI-first and reproducible.
- Keep source families separate until a current design admits integration.
- Treat schema validity, evidence support, canonical identity, and semantic
  correctness as different claims.
- Preserve unrelated user changes and generated artifacts.
- Keep credentials, model caches, local run directories, and scratch outputs
  out of Git.
- Use `git grep` for tracked-file context-hygiene scans.

## Verification

- Code changes: `uv run ruff check .` and `uv run pytest -q`.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
