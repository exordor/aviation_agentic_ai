# Project Goals

Last updated: 2026-07-30

This file defines durable system outcomes. Concrete work belongs in `TODO.md`;
historical comparison hypotheses belong in the optional experiment documents.

## Primary Goal

Build a useful, extensible bounded-Agent aviation decision-case knowledge
system that:

1. reads retrospective FAA ATCSCC advisories and bounded authority records
   into a repeatable corpus-first build;
2. coordinates deterministic parsing and authority services, conditionally
   activated semantic resolution and decision-case assembly Agents, and a
   graph-grounded read surface with bounded Decision Case Analysis for exact
   registered questions;
3. publishes only evidence-bound facts accepted by one explicit final
   multi-profile Formal Publication Kernel;
4. keeps corpus v2 as the canonical persisted knowledge layer and derives
   runtime corpus/graph views, offline RDF/Turtle and Neo4j exports, and a
   metadata-conditioned Chroma retrieval index;
5. answers bounded user questions through read-only graph tools while exposing
   evidence, uncertainty, and missing information.

The goal is a working system and framework, not proof that more Agent roles are
always better than fewer roles.

## User Value

The system should help a user understand and verify a published ATCSCC decision
record:

- what traffic-management measure was published;
- which facility it controlled;
- when it applied;
- which reason the source declared;
- which time-bounded forecast and observation records were available as
  non-causal context;
- which BTS-reported public operational observations describe the baseline,
  active, and recovery windows;
- which source and graph fact support each statement.

It must distinguish formal graph facts, source-bound profile gaps, derived
provenance, non-causal context associations, BTS-reported observations, and
genuinely missing information.

## Completed Foundation

The current system provides:

- deterministic one-record parsing and authority-resolution services;
- a shared Semantic Resolution Agent only for genuine multi-candidate
  authority ambiguity;
- a deterministic canonical-case compiler and a bounded Decision Case
  Assembly Agent only for genuine evidence/schema choice;
- a write-free final Formal Publication Kernel shared by decision, Weather,
  public-observation, and DecisionCase-core layers;
- a payload-free corpus-bound sidecar that measures selective Agent activation,
  bypass, outcome, calls, tokens, and recorded latency;
- explicit `live_smoke` and `live_experiment` harnesses that reuse the real
  corpus build, Formal Publication Kernel, and corpus query path without
  replacing failures with scripted responses;
- fact-level evidence binding and source provenance;
- canonical facility reuse and idempotent Neo4j merge behavior;
- JSONL, RDF/Turtle, and Neo4j projection artifacts;
- content-addressed corpus source storage, a case catalog, canonical facts, and
  explicit case-to-fact membership;
- a source-independent DecisionCase core with stable conceptual-case and
  reconstruction identities plus formal reconstruction membership;
- deterministic cross-case catalog filtering and selected-event formal fact
  retrieval with zero model calls;
- a closed case-scoped graph traversal for the exact registered Weather and
  active-window BTS evidence-path question, with zero model calls;
- deterministic corpus query routing through bounded read-only tools;
- deterministic support for measure, facility, operational period, declared
  reason, provenance, and combined decision-record questions;
- bounded Decision Case Analysis for exact registered episode,
  operational-situation, and applicability questions, with immutable analysis
  artifacts;
- deterministic historical decision-record retrieval through exact corpus
  filters followed by a rebuildable local Chroma vector index;
- explicit profile-gap, insufficient, and blocked outcomes.

Ground Stop `123`, Ground Delay Program `138`, and missing-reason cancellation
`020` are compact acceptance fixtures for those capabilities, not the system's
storage or processing boundary.

## Current Capability Boundary

The current decision-case construction path has these boundaries:

- eligible TAF and METAR reports become source-bound weather report facts;
- event-to-weather links remain audit-only associations with
  `causal_claim=false`;
- pinned BTS rows are deterministically aggregated into source-qualified public
  operational observations for fixed baseline, active, and recovery windows;
- validated BTS-reported observations enter RDF and Neo4j only through their
  dedicated profile and are never represented as FAA demand, AAR, capacity, or
  EDCT;
- observation fact traces, derivations, reconstruction membership, source
  bindings, and profile checksums remain independently auditable;
- missing or invalid optional layers remain `insufficient` or `blocked` without
  invalidating an otherwise verified ATCSCC event.
- Weather/BTS preparation occurs before one immutable Assembly task is sealed.
- Ground Stop `123`, GDP `138`, and cancellation `020` use a deterministic
  compiler and make zero Decision Case Assembly provider calls.
- A bounded Decision Case Assembly Agent may activate only for a genuine
  non-canonical evidence/schema choice.
- Task-bound event validation keeps Assembly output within the sealed evidence
  and schema scope. Case membership is then finalized before the
  multi-profile Formal Publication Kernel applies the sole final publication
  decision and any projection is written.

The Assembly role does not turn adapters into Agents and does not add model
calls to the three canonical cases. It reconstructs auditable historical
context; it does not evaluate operational optimality. The closed analysis
surface supports a complete operational-situation fixture. Episode analysis is
current-record-only, and applicability analysis has no observed
individual-flight evidence.

The DecisionCase semantic core owns reconstruction identity and membership
independently of the Weather and BTS profiles. Corpus queries use that formal
structure for one exact, closed evidence-path question; this is not a general
graph-query interface.

Published decision-record similarity embeds only TMI type, canonical facility,
declared-reason state/value, UTC time of day, and duration category. Exact
filters run before normalized cosine retrieval; the anchor case is excluded,
and the route makes zero chat-model calls. It does not compare Weather, BTS
outcomes, operational effectiveness, or recommended actions.

## Success Criteria

The system mainline succeeds when:

- a selected source record can run end to end;
- every published fact is admitted by the active schema profile;
- every published fact carries source and exact evidence support;
- canonical entities are reused rather than duplicated;
- RDF and Neo4j represent the same validated fact identities;
- corpus query routing exposes only query-relevant facts and evidence;
- unsupported or missing questions do not trigger model completion;
- a user can inspect why an answer was produced.

These are system acceptance criteria, not external semantic certification.

## Current Decision Boundary

The read-only visualization has reached a stable stopping point on
`codex/kg-visualization-research`. It is an optional presentation layer and is
not merged into `main`.

Later increments require an explicit user task and source boundary. Possible
directions include decision-episode identity, regional Weather,
ASPM-based demand/capacity evidence, operational-situation similarity, or a
separately versioned response to the recorded live-model compatibility
failures.

## Deferred Work

- Weather-based causal explanation.
- ASPM outcomes and flight-level impact.
- Initial/revision/extension/cancellation episode grouping.
- Operational-situation and outcome-aware similarity, learned reranking, and
  TMI recommendation.
- General-purpose aviation QA.
- Full-corpus live-model execution.
- Prompt and output-token-cap compatibility fixes for the recorded
  `live_smoke` and `live_experiment` failures.
- Multi-model or statistically powered live-Agent benchmarks.
- A natural frozen-cohort Semantic Resolution evaluation; synthetic ambiguity
  fixtures remain `offline_software_test` evidence and must not be reported as
  cohort results.
- Automatic ontology expansion.
- Production deployment and access control.
- New Agent roles without a demonstrated system need.
- Analysis beyond the exact registered question families.
- Paired comparison experiments as a prerequisite for feature delivery.

## Historical And Optional Tracks

The repository retains earlier PHAK GraphRAG work, schema-extraction
experiments, cross-source weather evaluation, alignment MVE artifacts, and
thesis-oriented reports. They remain useful for calibration, method history, or
an explicitly reactivated evaluation task. They do not define the current
system goal.

See `ARTIFACT_INDEX.md` for routing and `DECISION_LOG.md` for the sequence of
scope changes.
