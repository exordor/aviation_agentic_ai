# Project Audit And Context Router

Audit date: 2026-07-31

This is the default entry point for a new project task. It records current
implementation truth and routes historical material without making it default
context.

## Current Project Snapshot

Aviation Agentic AI is a runnable, ontology-grounded aviation
knowledge-integration and HybridRAG system. Retrospective FAA ATCSCC TMI events
are the current vertical slice.

```text
718 advisory rows
  -> cohort/all selection or explicit source-ID subset
  -> ATMONTO-aligned GDP, GS, and ReRoute classification
  -> deterministic preflight and source preparation
  -> selective Semantic Resolution / Event Evidence Integration
  -> Formal Publication Kernel
  -> canonical tmi-event-corpus-v3
  -> exact event, event graph, and TMI-event vector views
  -> always-on bounded LLM Query Agent
  -> per-statement evidence validation
  -> answer / insufficient / blocked
```

The admitted ATMONTO `TrafficManagementInitiative` instance is the formal root.
Corpus event membership organizes accepted facts without asserting that the
system reconstructed an internal decision process. ATMONTO supplies the
admitted schema terms. ATMGRAPH supplies ABox construction and cross-source
query principles, not another imported dataset or an exact replication target.

The public commands are:

```text
build-corpus
index-events
ask
neo4j-export
export-event
```

There is no persistent one-record ingest interface, run-directory query path,
old-corpus reader, or compatibility alias.

## Verified Implementation Capabilities

- One registry rooted at `atm:TrafficManagementInitiative` drives GDP, GS, and
  ReRoute detection, required-field preflight, formal property mapping, and
  retrieval labels.
- Deterministic parsing and FAA facility/terminology authority services preserve
  source-family boundaries.
- The Semantic Resolution Agent activates only for genuine multi-candidate
  authority ambiguity.
- Complete event evidence uses a zero-call deterministic compiler. The Event
  Evidence Integration Agent activates only for unresolved sealed
  evidence/schema choice.
- The Formal Publication Kernel is write-free and is the sole publication
  authority over decision, Weather, and public-observation profiles.
- `tmi-event-corpus-v3` content-addresses source objects, deduplicates semantic
  facts independently from provenance, and stores:
  - a TMI event catalog;
  - explicit event-to-fact membership;
  - evidence links;
  - profile gaps;
  - non-causal Weather associations;
  - source-qualified BTS public observations.
- `alignment_audit.json` and `tmi_coverage.json` are compact rebuildable
  summaries, not additional gates or audit ledgers.
- RDF/Turtle and Neo4j are rebuildable offline KG projections. The event graph
  is a checksum-verified corpus-backed runtime view.
- `index-events` builds a corpus-bound Chroma sidecar with one compact vector
  document per admitted TMI event.
- Every valid `ask` activates the Query Agent. There is no fixed question
  registry or deterministic answer fallback.
- The Query Agent must retrieve before answering and may select six bounded
  read-only tools for exact events, formal facts, Weather, BTS observations,
  event graph paths, and metadata-conditioned similarity.
- Each final statement is checked against returned event, fact, gap, context,
  observation, graph-path, and source IDs.
- Missing support yields `insufficient`; failed providers, contracts, or
  dependencies yield `blocked`.
- A payload-free `agent_usage/` sidecar records activation, bypass, outcome,
  calls, tokens, and recorded latency. It is telemetry, not formal evidence or
  model-quality evaluation.

## Current Intake

The frozen source contains 718 discovered advisories and a selected 68-record
cohort:

| State | Count |
| --- | ---: |
| Active GDP/GS/ReRoute eligible | 46 |
| Incomplete core fields | 3 |
| Boundary notices | 18 |
| Deferred ReRoute cancellation | 1 |
| Deterministic preflight `insufficient` | 22 |

Every selected source receives one build result. The 22
boundary/deferred/incomplete results use zero provider calls. A final corpus
manifest is written only when the blocked count is zero; `--resume` retries
only blocked records.

## Evidence Boundaries

- ATCSCC records support published TMI fields and source-declared reasons.
- FAA authority sources support identity resolution, not event facts.
- TAF/METAR records may become formal Weather report facts.
- Event-to-Weather associations carry `causal_claim=false` and stay outside the
  formal graph.
- BTS rows may become source-qualified public observations through their own
  profile.
- BTS observations are not FAA demand, AAR, capacity, EDCT, decision rationale,
  operational effectiveness, or proof that a TMI caused an outcome.
- Weather or BTS evidence never fills a missing declared reason.
- Profile gaps remain source-supported non-formal records.

The tracked acceptance fixtures preserve:

- GS `2026-05-19:123`: declared reason as a profile gap;
- GDP `2026-05-19:138`: formal `weather`;
- GDP cancellation `2026-05-20:020`: honestly missing reason;
- ReRoute `2026-05-19:108` and `2026-05-20:137`: formal
  `atm:ReRouteTMI`, with unsupported ARTCC scope retained as a profile gap.

These are regression fixtures, not representative evaluation samples or
special execution routes.

## Evaluation Boundary

Evaluation mode `offline_software_test` covers deterministic software,
contracts, state transitions, storage, retrieval plumbing, and validation.
Fake or scripted models are allowed only in that mode and do not establish LLM
or Agent quality.

The tracked v1/v2 reports and later compact-selection compatibility runs all
predate the event-centered semantic cutover. They remain frozen, GDP-biased
historical compatibility evidence:

- the v1 repeated run recorded 108 successful provider calls but 0/60 task
  acceptance under the retired runtime;
- the v2 repeated run recorded 120 successful provider calls; its repeated GDP
  query passed 12/12 while the former construction tasks failed 48/48;
- a later compact-selection run recorded 120 successful calls and 60/60 task
  acceptance under its then-current contracts;
- a later 10,000-token one-shot smoke recorded 10 successful calls and accepted
  all five frozen tasks.

These measurements are not independent task samples, cross-family evidence, or
post-cutover performance. Provider-call success and task acceptance remain
separate claims.

Current `live_agent_smoke_v3.yaml` and `live_agent_experiment_v3.yaml` use the
event-centered role and tool names. No post-cutover live result should be
reported until a separately authorized real-provider run captures and verifies
raw responses, parsed outputs, call bindings, token usage, and manifest
checksums.

The frozen cohort contains no natural ambiguity that activates the Semantic
Resolution Agent. Synthetic ambiguity fixtures remain offline orchestration
tests and must not be reported as cohort performance.

## Context Routing

| Need | Read |
| --- | --- |
| Durable system goal and boundaries | `GOALS.md` |
| Installation and current commands | `README.md` |
| Active execution queue | `TODO.md` |
| Normative system design | `docs/multi_agent_kg_system_design.md` |
| Artifact ownership and history | `ARTIFACT_INDEX.md` |
| Reproduction commands | `REPRODUCIBILITY.md` |
| Structural decision history | `DECISION_LOG.md` |
| Optional historical experiments | `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`, `EXPERIMENTS.md`, `RESULTS.md` |

Do not preload optional experiments, historical stage reports, ignored corpus
outputs, or archives.

## Current Non-Capabilities

The project does not provide:

- general aviation QA;
- live ATC support;
- a complete aviation ontology;
- causal explanation;
- FAA decision inputs, alternatives, constraints, rationale, or trade-offs;
- operational effectiveness or optimality;
- lifecycle episode reconstruction;
- outcome-aware similarity or TMI recommendation;
- external expert certification;
- post-cutover live-model performance evidence.

Flight/sector queries such as F1, F3S, S4, and S1S remain data-source gaps, not
features to fabricate from the current corpus.

## Verification Defaults

- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Code changes: focused tests during development, then one final
  `uv run ruff check .`, `uv run pytest -q`, `uv build`, and
  `git diff --check`.
- Result claims require inspection of the active implementation and named
  artifacts, not historical test counts or executor summaries.
