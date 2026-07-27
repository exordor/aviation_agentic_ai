# Project Goals

Last updated: 2026-07-28

This file defines durable system outcomes. Concrete work belongs in `TODO.md`;
historical comparison hypotheses belong in the optional experiment documents.

## Primary Goal

Build a useful, extensible multi-Agent aviation event knowledge system that:

1. reads a retrospective FAA ATCSCC advisory and bounded authority records;
2. coordinates deterministic parsing and authority services, conditionally
   activated semantic resolution and decision-case assembly Agents, and a
   graph-grounded read surface with bounded Decision Case Analysis for exact
   registered questions;
3. publishes only evidence-bound facts accepted by a deterministic schema and
   provenance gate;
4. materializes one canonical event graph as JSONL, RDF/Turtle, and a Neo4j
   projection;
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
- deterministic formal validation as the sole publication gate;
- fact-level evidence binding and source provenance;
- canonical facility reuse and idempotent Neo4j merge behavior;
- JSONL, RDF/Turtle, and Neo4j projection artifacts;
- a bounded read-only Query Agent;
- deterministic support for measure, facility, operational period, declared
  reason, provenance, and combined decision-record questions;
- bounded Decision Case Analysis for exact registered episode,
  operational-situation, and applicability questions, with immutable analysis
  artifacts;
- explicit profile-gap, insufficient, and blocked outcomes.

The three approved records - Ground Stop `123`, Ground Delay Program `138`, and
missing-reason cancellation `020` - exercise those capabilities.

## Current Approved Extension

Batch C combines Decision Case Graph v1 context with task-bounded Decision Case
Assembly for the same three records:

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
- Strict preflight requires an exact projection of the sealed task before the
  Formal Graph Kernel applies the final publication decision.

The new Assembly role does not turn adapters into Agents and does not add model
calls to the three canonical cases. It reconstructs auditable historical
context; it does not evaluate operational optimality.

The active Batch D extension exposes that validated case through a closed
analysis surface. Operational-situation analysis is the supported complete
fixture. Episode analysis is current-record-only, applicability analysis has
no observed individual-flight evidence, and historical similarity remains a
deterministic insufficient gate without a comparison corpus.

## Success Criteria

The system mainline succeeds when:

- a selected source record can run end to end;
- every published fact is admitted by the active schema profile;
- every published fact carries source and exact evidence support;
- canonical entities are reused rather than duplicated;
- RDF and Neo4j represent the same validated fact identities;
- the Query Agent retrieves only query-relevant facts;
- unsupported or missing questions do not trigger model completion;
- a user can inspect why an answer was produced.

These are system acceptance criteria, not external semantic certification.

## Current Transition

The read-only visualization batch has reached a stable stopping point on
`codex/kg-visualization-research`. It is an optional presentation layer and is
not merged into `main`.

Batch C.1 completed the breaking architecture cutover. The active
`codex/decision-case-analysis-agent` branch adds only bounded read-side
analysis and immutable analysis artifacts. Old runs require regeneration. The
current command names are retained for user continuity, not as an artifact or
runtime compatibility guarantee.

Later increments still require an explicit user task and source boundary.
Possible directions include decision-episode identity, regional weather,
ASPM-based demand/capacity evidence, and historical case retrieval.

## Deferred Work

- Weather-based causal explanation.
- ASPM outcomes and flight-level impact.
- Initial/revision/extension/cancellation episode grouping.
- Historical similarity ranking and TMI recommendation.
- General-purpose aviation QA.
- Full-corpus live-model execution.
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
