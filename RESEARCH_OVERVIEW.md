# System And Research Overview

Last updated: 2026-07-31

This document explains the current research direction. Optional comparisons and
historical experiments remain routed through `ARTIFACT_INDEX.md`.

## Problem

ATM data comes from heterogeneous systems with different formats, identifiers,
time semantics, spatial granularity, and vocabularies. The current vertical
slice combines:

- semi-structured FAA ATCSCC TMI advisories;
- FAA NASR and terminology authority records;
- time-bounded METAR and TAF records;
- source-qualified BTS public operational observations.

No source alone supplies the complete cross-source knowledge needed for a
natural-language answer. At the same time, temporal association cannot be
silently promoted to causation, and public BTS fields cannot be reinterpreted
as FAA demand or capacity.

## Project Outcome

The project builds an ontology-grounded integration and HybridRAG system:

```text
heterogeneous aviation sources
  -> deterministic adapters and authority services
  -> selective bounded Semantic Resolution for genuine ambiguity
  -> deterministic Event Evidence Integration
  -> Formal Publication Kernel
  -> canonical ATMONTO-aligned TMI Event Corpus v3
  -> exact, graph, and vector read views
  -> bounded LLM Query Agent
  -> evidence-supported answer / insufficient / blocked
```

The core contribution is not the number of Agents. It is the controlled
combination of:

- deterministic source handling;
- ontology-guided semantic alignment;
- selective Agent escalation;
- source- and profile-bound publication;
- graph and vector retrieval;
- statement-level answer support.

## ATMONTO And ATMGRAPH Alignment

ATMONTO defines the admitted schema target. The formal root is
`atm:TrafficManagementInitiative`, with active GDP, GS, and ReRoute subtypes.
The application profile constrains classes, predicates, domains, ranges,
datatypes, and enumerated values that may enter the formal graph.

ATMGRAPH is a construction and query reference. The implementation adopts its
principles of source-specific translation, stable cross-source identity,
explicit time, and graph-based cross-source querying. It does not import an
ATMGRAPH dataset and does not claim to reproduce the historical implementation.

This division is deliberate:

- ATMONTO alignment addresses schema and terminology interoperability;
- ATMGRAPH alignment addresses populated ABox construction and query use;
- the project-specific corpus preserves evidence roles and rebuildable
  projections.

## Formal Knowledge Model

The admitted ATMONTO TMI event is the formal root. The corpus contains:

- `events.jsonl`: TMI event catalog;
- `facts.jsonl`: validated semantic facts;
- `event_facts.jsonl`: event-to-fact membership;
- `evidence_links.jsonl`: one-to-many source support;
- `profile_gaps.jsonl`: supported but currently unpublishable source fields;
- `context_associations.jsonl`: non-causal event-to-Weather associations;
- `observations.jsonl`: query-ready BTS public observations.

This model does not claim to reconstruct internal decision inputs,
alternatives, constraints, rationale, or trade-offs. Such a construct is
deferred until appropriate sources and semantics exist.

## Agent Design

The workflow coordinator is deterministic. Only two roles can make bounded
model-mediated choices:

1. the Semantic Resolution Agent selects or abstains among sealed authority
   candidates;
2. the Query Agent selects read-only retrieval tools for every valid
   natural-language question.

Event Evidence Integration, data fetching, parsing, normalization, time
alignment, aggregation, profile validation, RDF/Neo4j writing, and vector
search remain deterministic tools or services. No Agent can create a candidate
outside its sealed task or write directly to the formal graph.

## Evidence Model

The system keeps these states distinct:

| State | Meaning |
| --- | --- |
| Formal fact | Accepted by its profile and the Formal Publication Kernel. |
| Evidence/provenance | Source support and derivation for an accepted record. |
| Profile gap | Source-supported information outside the active profile. |
| Non-causal context | Time-bounded association with `causal_claim=false`. |
| Public observation | Source-qualified BTS observation under its own profile. |
| Missing/insufficient | Requested information is absent or unsupported. |
| Blocked | A required source, contract, provider, or validation step failed. |

Weather and BTS context never fills a missing source-declared reason. BTS is
not FAA demand, AAR, capacity, EDCT, decision rationale, effectiveness, or
proof of a caused outcome.

## HybridRAG Query Surface

Every valid public question enters the LLM Query Agent. The Agent must retrieve
before answering and may choose:

- exact TMI event discovery;
- formal event facts and profile gaps;
- non-causal Weather context;
- BTS public observations;
- event-scoped formal and cross-source evidence paths;
- metadata-conditioned TMI event ranking.

Deterministic tools return typed observations and evidence identities. A final
validator checks each answer statement against those returned IDs and rejects
unsupported causal, recommendation, or metric reinterpretation claims.

## Research Position

The present system demonstrates a modern, reproducible ATMONTO-aligned
integration path with selective Agent escalation. It does not yet demonstrate:

- complete ATM semantic coverage;
- causal explanation;
- optimal TMI selection;
- decision effectiveness;
- general-purpose aviation QA;
- current post-cutover model performance.

Historical real-provider results are useful compatibility evidence for their
named earlier contracts, but they are GDP-biased and predate the current
event-centered role and corpus identities. The current v3 live suites require a
new authorized run before any post-cutover model claim.

See `GOALS.md` for durable outcomes, `TODO.md` for active decisions,
`RESEARCH_AUDIT.md` for current project truth, and `ARTIFACT_INDEX.md` for
historical routing.
