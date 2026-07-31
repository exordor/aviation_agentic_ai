# Project Goals

Last updated: 2026-07-31

This file defines durable system outcomes. Concrete work belongs in `TODO.md`;
historical evaluations are routed through `ARTIFACT_INDEX.md`.

## Primary Goal

Build a useful, extensible, ontology-grounded aviation knowledge-integration
and HybridRAG system that:

1. maps heterogeneous aviation sources to a shared ATMONTO-aligned semantic
   layer;
2. builds retrospective ATCSCC GDP, GS, and ReRoute event knowledge as the
   current end-to-end vertical slice;
3. escalates only genuine semantic ambiguity or evidence/schema choice to
   bounded Agents;
4. publishes only source-supported facts accepted by one explicit Formal
   Publication Kernel;
5. keeps `tmi-event-corpus-v3` as the canonical persisted layer and derives
   event graph, RDF/Turtle, Neo4j, and Chroma views from it;
6. routes every valid natural-language question through a bounded LLM Query
   Agent over read-only HybridRAG tools;
7. exposes evidence, limitations, and honest missing states for every supported
   answer.

ATMONTO supplies the admitted TBox and application-profile terms. ATMGRAPH
supplies ABox construction and cross-source-query principles. The project does
not import ATMGRAPH data or claim an exact replication.

The current TMI-event slice is a validation vehicle for the architecture, not
the permanent subject boundary. The goal is a runnable integration and query
system, not a claim that more Agents are always better.

## User Value

For a published ATCSCC TMI event, a user should be able to ask:

- what traffic-management measure was published;
- which facility it concerned;
- when it applied;
- which reason the source declared, if any;
- which source-qualified Weather records were retained as non-causal context;
- which BTS public observations describe baseline, active, and recovery
  windows;
- which historical TMI records match explicit metadata and vector criteria;
- which source and accepted fact support each answer statement.

The system must distinguish:

- formal TMI, Weather, and public-observation facts;
- source-bound profile gaps;
- non-causal context associations;
- provenance and evidence links;
- genuinely missing or insufficient information.

## Completed Foundation

The current system provides:

- one family registry rooted at `atm:TrafficManagementInitiative`, with active
  GDP, GS, and ReRoute application profiles over exact ATMONTO terms;
- deterministic advisory parsing, source normalization, time alignment, and
  FAA facility/terminology authority services;
- a shared Semantic Resolution Agent only for genuine multi-candidate
  authority ambiguity;
- a zero-call compiler for complete event evidence and a bounded Event Evidence
  Integration Agent only for unresolved sealed evidence/schema choice;
- one write-free Formal Publication Kernel over decision, Weather, and
  public-observation layers;
- content-addressed source storage, semantic fact deduplication, evidence
  links, profile gaps, non-causal context associations, and public
  observations;
- an event catalog and explicit event-to-fact membership in corpus v3;
- consistent JSONL, RDF/Turtle, and Neo4j fact projections;
- a rebuildable metadata-conditioned Chroma index over TMI events;
- six bounded read-only Query Agent tools;
- an always-on Query Agent action-observation loop with statement-level support
  validation;
- explicit `ok`, `insufficient`, `blocked`, and profile-gap semantics;
- payload-free Agent usage telemetry that is excluded from canonical corpus
  identity;
- compact alignment and TMI-family coverage summaries that are not additional
  publication authorities.

## Current Semantic Boundary

The admitted ATMONTO TMI event is the formal root. Corpus event membership is a
storage and retrieval relation; it is not a claim that the system reconstructed
an internal FAA decision process.

The current evidence rules are:

- ATCSCC records support published TMI fields and source-declared reasons;
- FAA authority records support facility and terminology resolution;
- TAF and METAR reports may become formal Weather report facts;
- event-to-Weather links remain `causal_claim=false`;
- BTS rows may become source-qualified public observations through their
  dedicated profile;
- BTS observations are not FAA demand, AAR, capacity, EDCT, decision rationale,
  effectiveness, or caused outcomes;
- Weather and BTS never supply a missing declared reason;
- optional-layer insufficiency does not invalidate an otherwise supported TMI
  event;
- any layer admitted to the final publication set must pass the same Formal
  Publication Kernel before a projection is written.

## Agent Boundary

Agents are organized by semantic responsibility, not by source:

- the Semantic Resolution Agent chooses only among sealed authority candidates;
- the Event Evidence Integration Agent chooses only among sealed evidence and
  schema candidates when deterministic integration is incomplete;
- the Query Agent selects read-only retrieval tools for every valid
  natural-language question.

Parsers, adapters, profile loaders, validators, writers, and vector search are
deterministic tools or services. No Agent can invent an ontology term, widen
its sealed scope, write directly to the graph, or treat model memory as
evidence.

## Success Criteria

The current mainline succeeds when:

- a selected GDP, GS, or ReRoute record builds end to end;
- each event is identified by an admitted ATMONTO TMI IRI;
- every published fact is admitted by the active profile and bound to source
  evidence;
- `events.jsonl` and `event_facts.jsonl` organize accepted knowledge without a
  synthetic decision-process node;
- JSONL, RDF/Turtle, and Neo4j expose the same formal fact identities;
- exact event, graph, Weather, BTS, and similarity tools remain inside the
  user-supplied scope;
- every valid natural-language query activates the Query Agent and retrieves
  before answering;
- each returned statement cites retrieved support;
- missing support yields `insufficient` rather than invention;
- a user can inspect why the system returned its answer.

These are system acceptance criteria, not expert semantic certification or
model-quality claims.

## Deferred Work

- A formal decision-process representation with attributable decision-state
  inputs, alternatives, constraints, rationale, trade-offs, and appropriately
  interpreted outcome evidence.
- Weather-based causal explanation.
- ASPM demand, AAR, capacity, EDCT, runway configuration, and flight-level
  impact.
- Initial, revision, extension, and cancellation episode grouping.
- National Playbook PDF grounding.
- F1/F3S/S4/S1S flight and sector data.
- Operational-situation or outcome-aware similarity, learned reranking, and
  TMI recommendation.
- General-purpose aviation QA.
- Automatic ontology expansion.
- New Agent roles without an observed system need.
- Production deployment, access control, and production-only hardening.

## Historical And Optional Tracks

The repository retains earlier PHAK GraphRAG work, schema-extraction
experiments, cross-source Weather evaluations, alignment experiments, browser
prototypes, and live-provider compatibility reports. They remain available for
an explicitly reactivated task but do not define the current architecture or
establish post-cutover performance.

See `ARTIFACT_INDEX.md` for routing and `DECISION_LOG.md` for the sequence of
scope decisions.
