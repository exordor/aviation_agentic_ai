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
  -> Advisory Agent
  -> Facility + terminology authority resolution
  -> deterministic Weather + BTS context preparation
  -> sealed Decision Case Assembly task
  -> deterministic compiler or bounded Decision Case Assembly Agent
  -> strict preflight
  -> Formal Graph Kernel
  -> publication/materialization
  -> Query Agent with bounded read-only tools
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
- Returns explicit insufficient or blocked states instead of filling missing
  facts from model knowledge.

The system does not let a model write directly to RDF or Neo4j. Profile gaps
remain audit records and never become formal graph facts. Weather associations
are explicitly non-causal. BTS-reported observations are not FAA demand, AAR,
capacity, EDCT, or proof that a TMI caused an outcome.

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

The live flag authorizes the bounded DeepSeek calls used by the construction
workflow. Set `DEEPSEEK_API_KEY` and optionally `DEEPSEEK_BASE_URL`; the active
system never substitutes the ambient general provider. The flag does not
authorize full-corpus processing.

Ask a registered question from a validated run:

```bash
uv run aviation-ai agent-system ask \
  --run-dir <validated-run-directory> \
  --question "Which airport was controlled?"
```

Deterministic field queries do not require a model. The combined record
question requires `--allow-live-model`.

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
| Advisory Agent | Parses one advisory and identifies source-supported mentions. |
| Facility and Terminology compatibility branches | Generate bounded authority candidates and resolve deterministic outcomes. |
| Semantic Resolution Agent | Resolves only genuine multi-candidate ambiguity through source-bounded tools. |
| Decision Case Assembly Agent | Selects among admitted evidence/schema choices and proposes an exact projection of a sealed task. |
| Formal Graph Kernel | Validates schema, identity, evidence, provenance, datatype, and graph constraints. |
| Query Agent | Selects bounded read-only tools and composes source-grounded answers. |

The LangGraph coordinator schedules the fixed workflow but is not counted as an
Agent. The ontology profile is a shared contract, not an Agent.

## Current Status

`main` contains the working ingest, formal validation, materialization,
Neo4j-load, and bounded query path.

The decision-record critical fixes are also on `main`:

- Ground Stop `123` exposes its declared reason as a source-bound profile gap.
- Ground Delay Program `138` preserves its cross-midnight operational period
  and formal normalized reason.
- Cancellation `020` returns an honest missing-reason result without a model
  call.

The active `codex/decision-case-assembly-agent` branch extends those records
with deterministic Weather/BTS context and Batch C Decision Case Assembly:

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
  evidence/schema choices; strict preflight prevents it from changing task
  identity, schema, evidence, profile gaps, or source ownership.
- The Formal Graph Kernel remains the sole final publication authority.
- Decision Case Analysis remains inactive.

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
