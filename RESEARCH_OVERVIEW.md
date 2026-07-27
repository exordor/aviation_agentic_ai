# System And Research Overview

Last updated: 2026-07-27

This document explains the current system direction. Formal comparison
experiments remain optional and are routed through `EXPERIMENTS.md`.

## Problem

FAA ATCSCC advisories are semi-structured records of published traffic
management measures. They contain useful operational facts, but abbreviations,
facility identifiers, temporal fields, free text, and incomplete ontology
coverage make those facts difficult to integrate and inspect consistently.

A plain text extraction pipeline is not enough for this project. The system
must preserve:

- the source record and exact evidence;
- canonical facility and terminology identity;
- the ontology/profile rule that admits a fact;
- unresolved profile gaps and missing fields;
- a trace from a user-facing answer back to validated facts and sources.

## Project Outcome

The project builds an aviation event knowledge system that converts
one retrospective advisory and bounded FAA authority records into a validated
event knowledge graph, RDF/Turtle, and a Neo4j projection, then answers a
registered set of decision-record questions.

The core value is not the number of Agents. It is the separation of:

- deterministic source interpretation;
- deterministic authority lookup and normalization;
- conditional semantic resolution and case assembly;
- deterministic publication;
- read-only graph-grounded interaction.

## Architecture

```text
ATCSCC advisory
  -> deterministic AdvisoryParser
  -> facility and terminology authority services
     -> Semantic Resolution Agent only for genuine ambiguity
  -> deterministic Weather/BTS adapters
  -> canonical compiler or Decision Case Assembly Agent
  -> Formal Graph Kernel
  -> validated event KG
  -> RDF/Turtle and Neo4j projection
  -> Query Agent
  -> answer, evidence, provenance, or explicit insufficiency
```

The workflow coordinator is deterministic. The Formal Graph Kernel is also
deterministic and is the sole publication gate.

## Why Multi-Agent

The current components reflect real information boundaries:

- the AdvisoryParser sees the advisory;
- authority services see their own facility or terminology sources;
- the Semantic Resolution Agent sees a sealed candidate set only when unique
  deterministic resolution is impossible;
- the Decision Case Assembly Agent sees a sealed task and compact schema
  context only when the zero-call compiler is not applicable;
- the Query Agent receives only read-only graph tools.

No role receives unrestricted source access or graph-write authority. This
makes the collaboration protocol observable and limits unsupported knowledge
transfer between roles.

## Role Of The Ontology

The NASA ATMONTO-derived application profile is a publication contract. It
defines which classes, predicates, domains, ranges, datatypes, and enumerated
values may enter the formal graph.

The project does not claim:

- that the profile is a complete aviation ontology;
- that every source field already has a formal representation;
- that an LLM can extend the ontology implicitly.

A supported source field outside the profile becomes a typed profile gap. It
does not become an invented triple.

## Current User Task

The current bounded interaction task is to understand and verify one published
decision record:

- identify the traffic-management measure;
- identify the controlled facility;
- report the operational period;
- report the source-declared reason when present;
- show the fact, source, and provenance supporting the answer.

The three approved cases cover a Ground Stop reason represented as a profile
gap, a GDP formal reason with a cross-midnight period, and a missing-reason
cancellation.

## Evidence Model

The system keeps four states distinct:

| State | Meaning |
| --- | --- |
| Formal fact | Accepted by the active schema and evidence gate. |
| Derived provenance | A trace showing which source supports an accepted fact. |
| Profile gap | Source-supported information not representable in the active profile. |
| Missing or insufficient | The requested information is absent or unsupported. |

None of these states establishes that a declared reason caused a measure or
that the published measure was optimal.

## Current Implementation Boundary

Implemented by the current Batch C.1 architecture:

- bounded one-record ingest;
- deterministic facility and terminology authority services;
- conditional semantic resolution and decision-case assembly;
- deterministic validation and audit artifacts;
- JSONL, RDF/Turtle, and Neo4j projection;
- bounded decision-record queries;
- explicit profile-gap, insufficient, and blocked outcomes.

Implemented separately and paused:

- the read-only query evidence visualization on
  `codex/kg-visualization-research`.

Not implemented as current system capabilities:

- weather-based explanation;
- decision episodes spanning multiple advisories;
- ASPM outcomes or flight impact;
- similar-case ranking;
- TMI recommendation;
- general-purpose aviation QA;
- full-corpus live-model processing.

## Evaluation Position

The repository contains several historical and optional experiments covering
schema-guided extraction, alignment, Critic or refinement roles, cross-source
weather context, retrieval, and answer diagnostics. They can be reactivated to
evaluate a specific system claim.

They are not prerequisites for building the current system and must not be used
to infer that:

- multiple Agents are universally superior;
- the graph is semantically complete;
- automated checks equal external expert review;
- historical associations prove operational causation.

## Next Decision

The next mainline increment will be selected after the metadata cleanup.
Decision-episode identity and an additional source-bounded situation-evidence
layer are plausible directions, but neither is active without a new approved
contract.

See `GOALS.md` for durable outcomes, `TODO.md` for active work, and
`ARTIFACT_INDEX.md` for context routing.

The cutover is breaking: regenerate earlier runs. The familiar command names
remain current UX and do not promise backward compatibility.
