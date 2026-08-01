# System And Research Overview

Last updated: 2026-08-01

This document explains the current research direction. Optional comparisons and
historical experiments remain routed through `ARTIFACT_INDEX.md`.

## Problem

ATM data comes from heterogeneous systems with different formats, identifiers,
time semantics, spatial granularity, and vocabularies. The active domains
combine:

- semi-structured FAA ATCSCC TMI advisories;
- FAA NASR and terminology authority records;
- time-bounded METAR and TAF records;
- source-qualified BTS public operational observations;
- the public NASA ATMONTO Flight/Airspace sample;
- bounded BTS flight records, FAA aircraft technical lookup, and NASR
  Airport/ARTCC reference data.

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
  -> deterministic TMI evidence integration and Flight/Airspace fact compilation
  -> semantic facts: Formal Publication Kernel
  -> cross-source links: deterministic association materializer
  -> authoritative ATMONTO-aligned SQLite evidence store
  -> exact, graph, lexical, vector, and source-read views
  -> LLM tool-family routing
  -> bounded Query Agent evidence loop
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

ATMONTO defines the admitted schema target. The TMI registry root is
`atm:TrafficManagementInitiative`, with active GDP, GS, and ReRoute subtypes.
Additional profiles admit the configured Flight/Airspace and reference
classes. Each profile constrains classes, predicates, domains, ranges,
datatypes, and enumerated values that may enter the formal graph.

ATMGRAPH is a construction and query reference. The implementation adopts its
principles of source-specific translation, stable cross-source identity,
explicit time, and graph-based cross-source querying. It does not import an
ATMGRAPH dataset and does not claim to reproduce the historical implementation.

This division is deliberate:

- ATMONTO alignment addresses schema and terminology interoperability;
- ATMGRAPH alignment addresses populated ABox construction and query use;
- the project-specific persistent store preserves source versions, evidence
  roles, accepted semantics, and rebuildable projections.

## Formal Knowledge Model

The generic publication spine admits ATMONTO-aligned TMI, Flight/Airspace,
reference, Weather, and reviewed association roots. The TMI regression slice
is rooted at an admitted ATMONTO TMI instance, but dataset and temporal-scope
configuration—not the legacy advisory inventory—selects research material.
The authoritative SQLite store contains immutable source
assets and versions, exact anchors, ingestion results, active and historical
publications, validated semantic facts, root membership, one-to-many evidence
support, profile gaps, non-causal Weather associations, source-qualified BTS
observations, deterministic derivations, and compact Agent usage telemetry.

The active top-level configuration composes separate runtime, source, and
dataset/temporal-scope files. This keeps deployment choices, artifact identity,
and research selection semantics distinct without turning an evaluation
snapshot into the runtime source of truth.

SQLite FTS5 and two Chroma collections provide lexical source discovery,
semantic source discovery, and metadata-conditioned TMI-event candidates.
JSONL, RDF/Turtle, and Neo4j remain optional rebuildable exports over all
active formal roots; none is a second source of truth.

This model does not claim to reconstruct internal decision inputs,
alternatives, constraints, rationale, or trade-offs. Such a construct is
deferred until appropriate sources and semantics exist.

## Agent Design

The workflow coordinator is deterministic. Only two roles can make bounded
model-mediated choices:

1. the Semantic Resolution Agent selects or abstains among sealed authority
   candidates;
2. the Query Agent first selects one or more capability families, then selects
   read-only retrieval tools for every valid natural-language question.

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
before answering. A first LLM call selects the `source`, `tmi`, and/or
`flight_airspace` capability families. The evidence loop then sees only the
relevant subset of 18 tools and may choose:

- exact TMI event discovery;
- formal event facts and profile gaps;
- non-causal Weather context;
- BTS public observations;
- event-scoped formal and cross-source evidence paths;
- metadata-conditioned TMI event ranking;
- lexical and semantic source discovery followed by exact `read_source`
  verification;
- Flight, airport, trajectory, and sector reads;
- temporal Flight–Weather associations and rule-derived TMI-applicability
  candidates;
- the general aviation graph view.

The loop permits 6 provider turns, at most 6 tool calls in one turn, and at
most 10 evidence-tool calls in total.

Deterministic tools return typed observations and evidence identities. A final
validator checks each answer statement against those returned IDs. Search hits
are candidates rather than citable evidence until the Agent retrieves the
exact immutable source version or anchor. Unsupported causal, recommendation,
or metric reinterpretation claims are rejected.

## Research Position

The present system demonstrates a modern, reproducible ATMONTO-aligned
integration path with selective Agent escalation. It does not yet demonstrate:

- complete ATM semantic coverage;
- causal explanation;
- optimal TMI selection;
- decision effectiveness;
- general-purpose aviation QA;
- broad post-cutover model performance.

The current cross-domain `live_smoke` recorded 33/33 successful
`deepseek-v4-pro` calls. Routing and retrieval passed 6/6 tasks; grounding and
answer acceptance passed 5/6. The remaining unsupported actual-control/causal
task exhausted the 10-tool budget instead of stopping with `insufficient` and
is retained as a stop-policy failure. This is compatibility evidence, not a
benchmark or general model-quality claim. Earlier GDP-biased reports remain
historical evidence for their named architectures.

See `GOALS.md` for durable outcomes, `TODO.md` for active decisions,
`RESEARCH_AUDIT.md` for current project truth, and `ARTIFACT_INDEX.md` for
historical routing.
