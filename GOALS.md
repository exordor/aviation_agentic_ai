# Project Goals

Last updated: 2026-07-26

This file defines durable system outcomes. Concrete work belongs in `TODO.md`;
historical comparison hypotheses belong in the optional experiment documents.

## Primary Goal

Build a useful, extensible multi-Agent aviation event knowledge system that:

1. reads a retrospective FAA ATCSCC advisory and bounded authority records;
2. coordinates specialized Agents for source interpretation, facility
   resolution, terminology normalization, and graph construction;
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
- which source and graph fact support each statement.

It must distinguish formal graph facts, source-bound profile gaps, derived
provenance, and genuinely missing information.

## Completed Foundation

The current `main` branch provides:

- one-record ingest through a fixed LangGraph construction workflow;
- bounded Facility and Terminology authority resolution;
- a tool-using Knowledge Graph Construction Agent;
- deterministic formal validation as the sole publication gate;
- fact-level evidence binding and source provenance;
- canonical facility reuse and idempotent Neo4j merge behavior;
- JSONL, RDF/Turtle, and Neo4j projection artifacts;
- a bounded read-only Query Agent;
- deterministic support for measure, facility, operational period, declared
  reason, provenance, and combined decision-record questions;
- explicit profile-gap, insufficient, and blocked outcomes.

The three approved records - Ground Stop `123`, Ground Delay Program `138`, and
missing-reason cancellation `020` - exercise those capabilities.

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

After this metadata cleanup, the next mainline capability must be chosen
explicitly. Plausible later increments include decision-episode identity or
additional source-bounded situation evidence, but neither is active until its
data boundary and user task are approved.

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
- Paired comparison experiments as a prerequisite for feature delivery.

## Historical And Optional Tracks

The repository retains earlier PHAK GraphRAG work, schema-extraction
experiments, cross-source weather evaluation, alignment MVE artifacts, and
thesis-oriented reports. They remain useful for calibration, method history, or
an explicitly reactivated evaluation task. They do not define the current
system goal.

See `ARTIFACT_INDEX.md` for routing and `DECISION_LOG.md` for the sequence of
scope changes.
