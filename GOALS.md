# Project Goals

Last updated: 2026-08-01

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
   TMI plus Flight/Airspace knowledge through a shared generic publication
   spine;
3. escalates only genuine authority ambiguity to a bounded Semantic Resolution
   Agent and keeps normal evidence integration deterministic;
4. publishes only source-supported facts accepted by one explicit Formal
   Publication Kernel;
5. keeps the persistent SQLite evidence store authoritative while deriving
   FTS, Chroma, all-root RDF/Turtle, and all-root Neo4j views from it;
6. routes every valid natural-language question through a bounded LLM Query
   Agent that first selects source, TMI, and/or Flight/Airspace capability
   families and then invokes their exact, graph, lexical, vector, and
   source-read tools;
7. exposes evidence, limitations, and honest missing states for every
   supported answer.

ATMONTO supplies the admitted TBox and application-profile terms. ATMGRAPH
supplies ABox-construction and cross-source-query principles. The project does
not import ATMGRAPH data or claim an exact replication.

The current TMI and Flight/Airspace domains validate a reusable architecture.
They are not the permanent subject boundary, and the goal is not to maximize
Agent count.

## User Value

For ingested aviation evidence, a user should be able to ask natural-language
questions that require one or more of:

- exact TMI event facts, facilities, times, and source-declared reasons;
- source-qualified Weather context known around an event;
- BTS public observations for baseline, active, and recovery windows;
- semantic graph edges and reviewed cross-source evidence paths;
- lexical or semantic discovery of source records followed by exact reading;
- metadata-conditioned retrieval of historical TMI event candidates;
- Flight facts, airport/ARTCC reference relations, trajectories and sector
  passages;
- temporal Flight–Weather associations and rule-derived TMI-applicability
  candidates;
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

- one TMI family registry rooted at `atm:TrafficManagementInitiative`, with
  active GDP, GS, and ReRoute application profiles over exact ATMONTO terms;
- deterministic advisory parsing, source normalization, time alignment, and
  FAA facility/terminology authority services;
- a shared Semantic Resolution Agent only for genuine multi-candidate
  authority ambiguity;
- deterministic Event Evidence Integration that compiles source-supported
  sealed evidence and preserves honest insufficiency;
- one write-free Formal Publication Kernel used by TMI, Weather,
  public-observation, Flight/Airspace, and reference semantic facts, plus a
  separate deterministic materializer for source-supported association roots;
- a versioned SQLite store for source assets, source versions, anchors,
  publications, facts, evidence, profile gaps, context, observations, and
  lightweight usage telemetry;
- incremental ingestion without a mandatory completed batch snapshot;
- SQLite FTS5 over source-record chunks;
- rebuildable Chroma collections for source records and compact TMI event
  summaries;
- optional all-root JSONL, RDF/Turtle, and Neo4j exports;
- three model-routed Query Agent capability families containing 18 bounded
  read-only evidence tools;
- a Query Agent invoked for every valid natural-language question, with a
  6-turn, 6-per-turn, 10-total-tool action-observation loop and
  statement-level support validation;
- Flight/Airspace ingestion and read-only tools covering stored flights,
  airports, trajectories, sectors, temporal Weather associations, TMI
  applicability candidates, and graph reads;
- a retained historical checksum-bound supplement for the F1, F3S, S4, and
  S1S query shapes;
- explicit `ok`, `insufficient`, and `blocked` semantics.

## Current Semantic Boundary

The store supports typed formal knowledge roots. ATMONTO TMI instances remain
the root of the mature advisory slice; Flight, Aircraft, Airport/ARTCC, Route,
TrackPoint, Sector, Weather, and reviewed association roots use the same
publication spine. None claims that the system reconstructed an internal FAA
decision process.

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

The public Query Agent uses a first LLM call to select one or more tool
families, then binds only those evidence tools. The active families are
`source` (3 tools), `tmi` (6 tools), and `flight_airspace` (9 tools). This
model-directed gate avoids exposing all 18 evidence tools on every turn while
retaining a shared runtime and support contract.

The older flight-competency supplement remains an offline deterministic
comparison artifact. Its modern F1/F3S proxies do not reconstruct the
unavailable 2012 KATL database and do not establish Weather causality or
historical aircraft-registration state.

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
- optional RDF/Turtle and Neo4j exports contain accepted facts from every
  active formal knowledge root, with publication and provenance bindings;
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
