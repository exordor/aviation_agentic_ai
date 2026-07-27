# Project Audit And Context Router

Audit date: 2026-07-28
Canonical integration branch: `main`

This is the default entry point for a new project task. It replaces the former
thesis-first navigation model.

## Current Project Snapshot

Aviation Agentic AI is a runnable, source-bounded system for
converting one retrospective FAA ATCSCC advisory into a validated event
knowledge graph, RDF/Turtle, and a Neo4j projection, then answering a small
registered set of decision-record questions with explicit source evidence. The
completed Batch C.1 cutover prepares time-bounded weather context and BTS-reported
public operational observations, seals them into one task-bounded decision
case, and preserves their non-causal/source-qualified meaning.

The active path is:

```text
one advisory + FAA facility and terminology records
  -> deterministic AdvisoryParser and authority services
  -> shared Semantic Resolution Agent only for genuine ambiguity
  -> deterministic Weather/BTS context preparation and validation
  -> sealed Decision Case Assembly task
  -> deterministic compiler for the three canonical cases or bounded
     Decision Case Assembly Agent for genuine evidence/schema choice
  -> strict preflight
  -> deterministic Formal Graph Kernel
  -> publication and RDF/Neo4j materialization
  -> deterministic query routing with read-only graph tools
     -> Decision Case Analysis Agent for exact registered analysis questions
```

The Coordinator and Formal Graph Kernel are deterministic components, not
Agents. LLM output cannot bypass the publication gate.

## Verified Main-Branch Capabilities

- `agent-system ingest` builds one source-bounded run.
- `agent-system neo4j-export` loads a validated projection with parameterized
  `MERGE` when Neo4j is available.
- `agent-system ask` answers registered measure, facility, operational-period,
  declared-reason, provenance, and combined-record questions from local
  validated run artifacts.
- Missing or unsupported fields return an explicit insufficient state.
- Profile gaps remain audit records and never become formal KG facts.
- Canonical facility identity is reused across records.

The browser visualization exists only on
`codex/kg-visualization-research`. It is paused and not part of `main`.

## Active Feature Branch

`codex/decision-case-analysis-agent` builds on the current architecture for
the three approved records:

- the latest eligible TAF known at advisory issue time;
- the latest eligible pre-issue METAR and operational-period observations;
- BTS-reported baseline, active, and recovery-window public operational
  observations;
- separate source snapshots, context associations, formal observation facts,
  derivations, fact traces, and reconstruction membership.
- a sealed task containing task-owned formal facts, profile gaps, resolution
  results, context associations, public observations, and source bindings;
- exact task-signature preflight before the Formal Graph Kernel.

Weather associations are explicitly non-causal. BTS-reported observations are
not FAA demand, AAR, capacity, EDCT, or evidence that a particular TMI caused
an outcome. Ground Stop `123`, GDP `138`, and cancellation `020` use the
deterministic Assembly compiler and make zero Assembly provider calls. The
bounded Assembly Agent is reserved for genuine evidence/schema choice.

The branch also routes exact registered episode, operational-situation, and
applicability questions through a sealed plan and bounded Decision Case
Analysis Agent. Operational situation is the supported complete fixture.
Episode output is current-record-only; applicability cannot claim observed
individual-flight impact. Historical similarity remains deterministic
`insufficient` without a corpus, provider call, artifact, ranking, or
recommendation. Existing record questions remain deterministic and zero-call.

Batch C.1 deliberately breaks old-run compatibility: regenerate old runs.
`ingest`, `neo4j-export`, and `ask` are retained as current command names, not
as a guarantee that earlier artifacts remain readable.

## Context Routing

| Need | Read |
| --- | --- |
| Durable system goal and boundaries | `GOALS.md` |
| Installation and current commands | `README.md` |
| Active execution queue | `TODO.md` |
| Normative Agent-system design | `docs/multi_agent_kg_system_design.md` |
| Decision-record semantics and cases | `docs/atcscc_decision_record_explorer_design.md`, `docs/atcscc_decision_record_explorer_cases.md` |
| Artifact ownership and context hygiene | `ARTIFACT_INDEX.md` |
| Reproduction commands | `REPRODUCIBILITY.md` |
| Why a structural decision was made | `DECISION_LOG.md` |
| Optional historical experiments | `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`, `EXPERIMENTS.md`, `RESULTS.md` |

Do not preload optional experiments, stage reports, ignored run directories, or
archives. They do not define the current system.

## Current Boundaries

The project does not currently provide:

- general aviation question answering;
- live ATC or flight decision support;
- weather-based causal explanation;
- historical-case ranking or TMI recommendation;
- full-corpus autonomous model execution;
- a complete aviation ontology;
- external expert certification.

The approved current increment is bounded Decision Case Analysis on
`codex/decision-case-analysis-agent`. Broader source expansion, lifecycle
grouping, historical ranking, recommendation, and analysis outside the exact
registered families do not become active merely because a historical document
mentions them.

## File Audit Rubric

Before treating a file as current context, ask:

1. Which current system capability does it define?
2. Is it normative design, implementation, evidence, or history?
3. What are its inputs and outputs?
4. Does it describe `main` or another branch?
5. Does it make a claim stronger than the available evidence?
6. Should it remain default context?

Unknown artifacts are preserved and classified in `ARTIFACT_INDEX.md`; they
are not silently deleted.

## Verification Defaults

- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Code changes: `uv run ruff check .` and `uv run pytest -q`.
- Result claims require inspection of the implementation and the named
  artifacts, not a historical test count.
