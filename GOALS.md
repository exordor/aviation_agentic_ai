# Project Goals

Last updated: 2026-07-31

This file defines durable system outcomes. Concrete work belongs in `TODO.md`;
historical evaluations are routed through `ARTIFACT_INDEX.md`.

## Primary Goal

Build a useful, extensible **ATMONTO-Grounded Agentic HybridRAG for
Heterogeneous Aviation Knowledge Integration**. It combines
deterministic heterogeneous-data integration with model-directed HybridRAG
retrieval. The system:

1. maps heterogeneous aviation sources to a shared ATMONTO-aligned semantic
   layer;
2. incrementally ingests source versions and publishes retrospective ATCSCC
   GDP, GS, and ReRoute event knowledge as the current vertical slice;
3. escalates only genuine authority ambiguity to a bounded Semantic Resolution
   Agent and keeps normal evidence integration deterministic;
4. publishes only source-supported facts accepted by one explicit Formal
   Publication Kernel;
5. keeps the persistent SQLite evidence store authoritative while deriving
   FTS, Chroma, RDF/Turtle, and Neo4j views from it;
6. routes every valid natural-language question through a bounded LLM Query
   Agent over exact, graph, lexical, vector, and source-read tools;
7. exposes evidence, limitations, and honest missing states for every
   supported answer.

ATMONTO supplies the admitted TBox and application-profile terms. ATMGRAPH
supplies ABox-construction and cross-source-query principles. The project does
not import ATMGRAPH data or claim an exact replication.

The current TMI-event slice validates a reusable architecture. It is not the
permanent subject boundary, and the goal is not to maximize Agent count.

## User Value

For ingested aviation evidence, a user should be able to ask natural-language
questions that require one or more of:

- exact TMI event facts, facilities, times, and source-declared reasons;
- source-qualified Weather context known around an event;
- BTS public observations for baseline, active, and recovery windows;
- semantic graph edges and reviewed cross-source evidence paths;
- lexical or semantic discovery of source records followed by exact reading;
- metadata-conditioned retrieval of historical TMI event candidates;
- the source version and exact anchor supporting each answer statement.

The system must distinguish:

- formal TMI, Weather, and public-observation facts;
- source-bound profile gaps;
- non-causal context associations;
- provenance and evidence links;
- search candidates from verified source reads;
- genuinely missing or insufficient information.

## Completed Foundation

The current system provides:

- one family registry rooted at `atm:TrafficManagementInitiative`, with active
  GDP, GS, and ReRoute application profiles over exact ATMONTO terms;
- deterministic advisory parsing, source normalization, time alignment, and
  FAA facility/terminology authority services;
- a shared Semantic Resolution Agent only for genuine multi-candidate
  authority ambiguity;
- deterministic Event Evidence Integration that compiles source-supported
  sealed evidence and preserves honest insufficiency;
- one write-free Formal Publication Kernel over TMI, Weather, and
  public-observation layers;
- a versioned SQLite store for source assets, source versions, anchors,
  publications, facts, evidence, profile gaps, context, observations, and
  lightweight usage telemetry;
- incremental ingestion without a mandatory completed batch snapshot;
- SQLite FTS5 over source-record chunks;
- rebuildable Chroma collections for source records and compact TMI event
  summaries;
- optional JSONL, RDF/Turtle, and Neo4j exports;
- nine bounded read-only Query Agent tools;
- a Query Agent invoked for every valid natural-language question, with a
  bounded action-observation loop and statement-level support validation;
- a checksum-bound flight-competency supplement that executes the F1, F3S,
  S4, and S1S query shapes over pinned NASA and modern FAA/BTS/Weather sources
  without changing the authoritative TMI-event store or public Query Agent
  runtime;
- explicit `ok`, `insufficient`, and `blocked` semantics.

## Current Semantic Boundary

The admitted ATMONTO TMI event is the formal root. Store membership and event
publication records organize accepted facts; they do not claim that the system
reconstructed an internal FAA decision process.

The evidence rules are:

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
- every admitted formal layer passes the same Formal Publication Kernel before
  it enters the store.

## Agent Boundary

Agents are organized by semantic responsibility, not by source:

- the Semantic Resolution Agent chooses only among sealed authority candidates;
- the Query Agent interprets every valid natural-language question and selects
  read-only retrieval tools.

Parsers, adapters, profile loaders, validators, writers, SQLite queries, graph
views, FTS, and vector search are deterministic tools or services. No Agent can
invent an ontology term, widen its sealed scope, write directly to the
knowledge store, or treat model memory as evidence.

The flight-competency supplement is an offline deterministic evaluation
sidecar, not a public Agent query backend. NASA's published 2014 sample
supports sector-passage S4/S1S queries. May 2026 BTS departures, NASR ARTCC
assignments, FAA aircraft technical records, and KATL METAR/SPECI observations
support explicitly labelled modern F1/F3S proxies. These results do not
reconstruct the unavailable 2012 KATL prototype database and do not establish
weather causality or historical aircraft-registration state.

## Success Criteria

The current mainline succeeds when:

- configured source artifacts are versioned and can be ingested incrementally;
- each accepted event is identified by an admitted ATMONTO TMI IRI;
- every published fact is admitted by the active profile and bound to source
  evidence;
- an incomplete or unsupported record is preserved as `insufficient` rather
  than fabricated;
- exact and lexical reads remain available when a vector index is absent or
  stale;
- both Chroma collections can be rebuilt from the authoritative store;
- optional RDF/Turtle and Neo4j exports contain the same accepted formal fact
  identities;
- every valid natural-language query activates the Query Agent and retrieves
  before answering;
- search candidates are verified through exact source reads before supporting a
  source-record statement;
- each answer statement cites retrieved support;
- missing support yields `insufficient`, and a user can inspect why.

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
- Ingestion of flight/sector evidence and exposure of F1/F3S/S4/S1S through
  bounded Query Agent tools.
- Operational-situation or outcome-aware similarity, learned reranking, and
  TMI recommendation.
- General-purpose aviation QA.
- Automatic ontology expansion.
- New Agent roles without an observed system need.
- Production deployment, access control, and production-only hardening.

## Historical And Optional Tracks

The repository retains earlier PHAK GraphRAG work, schema-extraction
experiments, cross-source Weather evaluations, alignment experiments, browser
prototypes, batch snapshots, and live-provider compatibility reports. They
remain available for an explicitly reactivated task but do not define the
current architecture or establish ingestion-first performance.

See `ARTIFACT_INDEX.md` for routing and `DECISION_LOG.md` for the sequence of
scope decisions. The familiar records remain development/regression fixtures;
no frozen post-cutover evaluation set has been constructed.
