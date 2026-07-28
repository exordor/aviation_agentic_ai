# Aviation Agentic AI

Aviation Agentic AI is a system and framework for building source-bounded
aviation event knowledge from retrospective FAA ATCSCC advisories.

It coordinates bounded interpretation, semantic-resolution, and case-assembly
roles, applies a deterministic publication gate, materializes a validated event
graph, and answers a registered set of decision-record questions with explicit
source evidence. Deterministic adapters reconstruct time-bounded weather
context and BTS-reported public operational observations before assembly.

```text
ATCSCC advisory
  -> deterministic AdvisoryParser
  -> facility and terminology authority services
     -> shared Semantic Resolution Agent only for genuine ambiguity
  -> deterministic Weather + BTS context preparation
  -> sealed Decision Case Assembly task
  -> deterministic compiler or bounded Decision Case Assembly Agent
  -> task-bound validation
  -> Formal Graph Kernel
  -> publication/materialization
  -> deterministic query routing with bounded read-only tools
     -> Decision Case Analysis Agent only for exact registered analysis questions
```

## What The System Does

- Ingests one selected ATCSCC advisory per run.
- Uses FAA facility and terminology records as bounded authority sources.
- Resolves canonical facilities and operational terms.
- Produces a task-bounded Graph Patch through deterministic assembly for the
  three canonical records or a bounded tool-using Assembly Agent when a genuine
  evidence/schema choice exists.
- Publishes only facts accepted by the deterministic Formal Graph Kernel.
- Preserves source IDs, evidence spans, fact traces, and profile gaps.
- Selects eligible TAF/METAR records as time-bounded, non-causal decision
  context.
- Publishes source-qualified BTS-reported observations for baseline, active,
  and recovery windows through a dedicated formal profile.
- Generates RDF/Turtle and a Neo4j property-graph projection.
- Answers registered measure, facility, operational-period, declared-reason,
  provenance, decision-context, public-observation, and combined-record
  questions through read-only tools.
- Runs bounded Decision Case Analysis only for exact registered episode,
  operational-situation, and applicability questions, and persists each
  analysis under an immutable analysis-run directory.
- Returns explicit insufficient or blocked states instead of filling missing
  facts from model knowledge.

The system does not let a model write directly to RDF or Neo4j. Profile gaps
remain audit records and never become formal graph facts. Weather associations
are explicitly non-causal. BTS-reported observations are not FAA demand, AAR,
capacity, EDCT, or proof that a TMI caused an outcome.

Batch C.1 is a breaking architecture cutover. Regenerate old runs before using
them with the current system. The useful command names `ingest`,
`neo4j-export`, and `ask` remain current UX; they do not promise an old-run
reader, writer, alias, or artifact compatibility layer.

## Quick Start

Install the active system and development dependencies:

```bash
uv sync --extra dev --extra ontology-generation --extra neo4j
uv run aviation-ai agent-system --help
```

Python 3.11 or newer is required.

Before ingest, obtain the pinned FAA NASR snapshot declared by
`configs/cross_source_v1.yaml`. The 238 MB ZIP is intentionally ignored by Git,
so a clean checkout can run tests but cannot ingest until the source preflight
in `REPRODUCIBILITY.md` passes.

Ingest one advisory:

```bash
uv run aviation-ai agent-system ingest \
  --source-id 2026-05-19:123 \
  --config configs/cross_source_v1.yaml \
  --allow-live-model
```

The live flag permits a bounded model only when a conditional semantic or
assembly path genuinely activates. Set `DEEPSEEK_API_KEY` and optionally
`DEEPSEEK_BASE_URL`; the active system never substitutes the ambient general
provider. The flag does not authorize full-corpus processing, and the three
canonical cases do not need a provider.

Build a normalized corpus from any number of validated runs:

```bash
uv run aviation-ai agent-system build-corpus \
  --runs-root data/runs/agent_system \
  --output-dir data/corpus/agent_system/cross-source-2026-05-v1
```

The builder validates each existing run, stores identical source payloads once
by checksum, and writes a stable case catalog, canonical fact table, and
case-to-fact membership table. Per-run directories remain portable debugging
and evidence bundles; the corpus is the scalable cross-case storage layer.
Building it does not run an Agent or enable historical ranking.

Query the normalized case catalog without a model call:

```bash
uv run aviation-ai agent-system ask-corpus \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v1 \
  --question "Which decision cases are recorded in this corpus?" \
  --facility-id urn:aviation-agentic-ai:facility:airport:KJFK \
  --limit 20
```

Read the formal record for one selected event:

```bash
uv run aviation-ai agent-system ask-corpus \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v1 \
  --event-id <canonical-event-id> \
  --question "What traffic management measure was published?"
```

Corpus queries support exact case filters, bounded pagination, and the existing
formal measure, facility, period, reason, provenance, and combined-record
questions. They do not perform similarity ranking or reconstruct run-local
Weather associations and outcome summaries.

Ask a registered question from a validated run:

```bash
uv run aviation-ai agent-system ask \
  --run-dir <validated-run-directory> \
  --question "Which airport was controlled?"
```

All existing field, context, public-observation, provenance, and combined
record questions are deterministic and do not require a model. An exact
registered Decision Case Analysis question requires `--allow-live-model`;
the historical-similarity gate remains deterministic and insufficient until
an approved comparison corpus exists.

Load the validated Neo4j projection:

```bash
uv run aviation-ai agent-system neo4j-export \
  --run-dir <validated-run-directory>
```

Neo4j credentials can be supplied through command options or the documented
environment variables. Missing connectivity or credentials returns `BLOCKED`;
the loader never clears unrelated graph data.

## Agent And Deterministic Responsibilities

| Component | Responsibility |
| --- | --- |
| AdvisoryParser | Deterministically parses one advisory into source-supported mentions. |
| Facility and terminology authority services | Build bounded authority candidates and decide blocked, insufficient, or unique results deterministically. |
| Semantic Resolution Agent | Resolves only genuine multi-candidate ambiguity through source-bounded tools. |
| Decision Case Assembly Agent | Is activated only for a genuine evidence/schema choice; the three canonical cases use the zero-call compiler. |
| Formal Graph Kernel | Validates schema, identity, evidence, provenance, datatype, and graph constraints. |
| Query router and tools | Answer existing registered record questions deterministically from validated artifacts. |
| Decision Case Analysis Agent | Uses only plan-bound read tools for exact registered analysis questions and writes immutable analysis evidence artifacts. |

The LangGraph coordinator schedules the fixed workflow but is not counted as an
Agent. The ontology profile is a shared contract, not an Agent.

Each current run is profile-owned: `kg.jsonl`, `kg.ttl`,
`neo4j_nodes.jsonl`, and `neo4j_relationships.jsonl` are projections of
validated facts, while `run_manifest.json`, `source_snapshots.jsonl`,
`profile_gaps.jsonl`, context associations, and trace artifacts remain the
auditable record. Profile gaps carry the exact current decision-profile
ownership and field-specific advisory evidence binding, and their artifact is
registered with path, count, SHA-256, and status. A query reads these validated
run artifacts only.

Cross-run storage is normalized separately. A corpus contains
`cases.jsonl`, `facts.jsonl`, `case_facts.jsonl`,
`source_bindings.jsonl`, content-addressed `source_objects/`, and
`corpus_manifest.json`. RDF and Neo4j remain rebuildable projections rather
than independent sources of truth. The read-only corpus query path searches
the catalog and retrieves canonical formal facts. Run-local evidence bundles
remain the source for profile-gap wording, Weather associations, outcome
summaries, and Decision Case Analysis artifacts.

## Current Status

`main` contains the working ingest, formal validation, materialization,
Neo4j-load, bounded query path, Decision Case Assembly, and Decision Case
Analysis.

The decision-record critical fixes are also on `main`:

- Ground Stop `123` exposes its declared reason as a source-bound profile gap.
- Ground Delay Program `138` preserves its cross-midnight operational period
  and formal normalized reason.
- Cancellation `020` returns an honest missing-reason result without a model
  call.

The current `main` implementation builds on deterministic Weather/BTS context
and task-bounded Decision Case Assembly:

- TAF selection is limited to forecasts issued no later than the advisory and
  valid during the TMI operational period.
- METAR selection is limited to the approved pre-issue and operational windows.
- BTS-reported observations use fixed baseline, active, and recovery windows
  and enter the formal graph only through the source-qualified public
  observation profile.
- Optional context failures do not erase a validated core advisory event.
- A sealed task binds formal facts, profile gaps, context associations, public
  observations, source snapshots, and component states before assembly.
- The three canonical records use the deterministic compiler and make zero
  Decision Case Assembly provider calls.
- A bounded Assembly Agent is available only for genuine non-canonical
  evidence/schema choices; task-bound validation keeps its output within the
  approved task, schema, evidence, profile gaps, and source ownership.
- The Formal Graph Kernel remains the sole final publication authority.
- Exact registered analysis questions are routed through a sealed query plan
  and the bounded Decision Case Analysis Agent.
- Operational-situation analysis is the supported complete fixture. Episode
  analysis is limited to the current record, and applicability analysis cannot
  claim observed individual-flight impact.
- Historical similarity returns deterministic `insufficient`; no ranking,
  score, neighbor, or recommendation is produced.
- Each model-bound analysis writes
  `analysis/<analysis_run_id>/` without overwriting `query_run.json`.

The read-only browser visualization is implemented separately on
`codex/kg-visualization-research`. That branch is paused and has not been merged
into `main`.

## Scope Boundaries

Current non-capabilities:

- general aviation question answering;
- live traffic-management decision support;
- weather-based causal explanation or attribution of a TMI to a weather report;
- historical-case ranking or recommendation;
- FAA demand, AAR, capacity, or EDCT reconstruction from BTS;
- full-corpus autonomous model execution;
- automatic ontology expansion;
- external aviation-expert certification.

Optional formal experiments, cross-source weather work, the earlier alignment
MVE, PHAK GraphRAG prototypes, and old web demos remain in the repository as
historical or calibration material. They are not the default project entry
point.

This is a research prototype. Production deployment security and defenses
against hostile local artifact tampering are outside the current acceptance
scope unless activated by a separate security task.

## Project Map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Operational instructions for coding agents. |
| `RESEARCH_AUDIT.md` | Current context router and branch-level truth. |
| `GOALS.md` | Durable system goal and scope. |
| `TODO.md` | Current execution queue. |
| `docs/multi_agent_kg_system_design.md` | Normative system design. |
| `docs/atcscc_decision_record_explorer_design.md` | Decision-record interaction contract and completed query foundation. |
| `docs/atcscc_decision_record_explorer_cases.md` | Three source-audited acceptance cases. |
| `src/aviation_agentic_ai/agent_system/` | Active system implementation. |
| `tests/test_agent_system*.py` | Focused system verification. |
| `ARTIFACT_INDEX.md` | Active, optional, generated, and historical artifact routing. |
| `REPRODUCIBILITY.md` | Installation and regeneration commands. |

## Development Verification

```bash
uv run ruff check .
uv run pytest -q
git diff --check
```

This repository is a research prototype. It is intended for retrospective
analysis and system development, not live aviation operations.
