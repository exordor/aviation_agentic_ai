# Project Goals

Last updated: 2026-08-02

This file defines durable system outcomes, boundaries, and deferred work.
Historical evaluations and retired report surfaces are outside the default
checkout; changing implementation status belongs in `RESEARCH_AUDIT.md`.

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
5. keeps a canonical semantic and evidence layer, currently implemented with
   SQLite, while deriving FTS, Chroma, all-root RDF/Turtle, and all-root Neo4j
   views from it;
6. routes every valid natural-language question through a bounded LLM Query
   Agent that first selects source, TMI, knowledge, and/or Flight/Airspace
   capability families and then invokes their exact, graph, lexical, vector,
   and source-read tools;
7. exposes evidence, limitations, and honest missing states for every
   supported answer; and
8. can optionally acquire allowlisted public documents through a separately
   running Web Evidence sidecar without making that sidecar a source of
   aviation facts or a required runtime dependency.

The project also provides an explicit ontology-grounded document-to-KG
framework for researching LLM-assisted ABox generation. It uses the complete ATMONTO TBox
to build a task-specific slice, gives a bounded model only sealed evidence
and candidate identities, validates candidate facts deterministically, and
incrementally fuses accepted semantic facts with one-to-many provenance.
This path is opt-in; the default ingestion compiler remains deterministic.
FAA JO 7210.3EE Chapter 18 is the first configured adapter and demonstrator,
not the subject boundary of that framework.

ATMONTO supplies the admitted TBox and application-profile terms. ATMGRAPH
supplies ABox-construction and cross-source-query principles. The project does
not import ATMGRAPH data or claim an exact replication.

The ATMONTO use-case boundary is explicit: the current system demonstrates
data query/search, information organization, information integration, and
terminology standardization. External information exchange is a future
interoperability capability, not a current runtime claim.

The semantic control plane also maintains a deterministic inventory of the six
local ATMONTO OWL modules. Its eight-domain coverage report records class
hierarchy, object/datatype property signatures, and cardinality constraints,
with explicit active, planned, and unsupported statuses. This is the baseline
for measuring KG semantic complexity; it is not a claim that every upstream
term is populated by the current source adapters.

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
- optionally, an allowlisted public web document fetched through the Web
  Evidence adapter, with exact source-version and span support.

The system must distinguish:

- formal TMI, Weather, and public-observation facts;
- source-bound profile gaps;
- non-causal context associations;
- provenance and evidence links;
- search candidates from verified source reads;
- genuinely missing or insufficient information.

## Implementation Status

Current implementation truth belongs to `RESEARCH_AUDIT.md`. This goals
document deliberately does not repeat changing command inventories, provider
results, dataset counts, or implementation checklists. The durable contract
is that accepted facts are ATMONTO/profile constrained, source-supported,
published through one Formal Publication Kernel, and queried through an
evidence-bound Agentic HybridRAG path.

## Current Semantic Boundary

The store supports typed formal knowledge roots. ATMONTO TMI instances provide
one regression publication path; Flight, Aircraft, Airport/ARTCC, Route,
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
- the opt-in Ontology Candidate Fact Generator proposes typed ABox facts only
  from a sealed task; it never writes the store and may abstain or emit a
  profile gap.

Parsers, adapters, profile loaders, validators, writers, SQLite queries, graph
views, FTS, and vector search are deterministic tools or services. No Agent can
invent an ontology term, widen its sealed scope, write directly to the
knowledge store, or treat model memory as evidence.

The public Query Agent uses a first LLM call to select one or more tool
families, then binds only those evidence tools. The core families are
`source` (3 tools), `tmi` (6 tools), and `flight_airspace` (9 tools). An
explicitly authorized Web Evidence sidecar adds an optional `web` family with
three read-only tools. This model-directed gate avoids exposing all core or
optional tools on every turn while retaining a shared runtime and support
contract.

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
- all Chroma collections can be rebuilt from the authoritative store;
- optional RDF/Turtle and Neo4j exports contain accepted facts from every
  active formal knowledge root, with publication and provenance bindings;
- every valid natural-language query activates the Query Agent and retrieves
  before answering;
- search candidates are verified through exact source reads before supporting a
  source-record statement;
- each answer statement cites retrieved support;
- missing support yields `insufficient`, and a user can inspect why.

When Web Evidence is enabled, ordinary ingestion remains disabled unless the
operator supplies both the configured seed/allowlist and `--allow-live-web`.
The sidecar is external and its source versions enter the same SQLite-backed
source and retrieval contracts; it is not vendored or required for the core
aviation pipeline.

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
- A reviewed frozen evaluation set and statistically powered benchmark.
- New TMI families without an explicit ATMONTO mapping and source/evidence
  boundary.
- Correction and re-evaluation of the observed unsupported-query stop policy.
- Broader Web Evidence seeds without a defined source role, parser profile,
  and support task.
- New Agent roles without an observed system need.
- Production deployment, access control, and production-only hardening.

## Historical And Optional Tracks

Earlier PHAK GraphRAG work, schema-extraction outputs, ATCSCC stage reports,
and retired live-provider compatibility tracks are preserved in the dated
external archive. They remain available for an explicitly reactivated task
but are not in the runtime checkout, do not define the current architecture,
and do not establish ingestion-first performance. The archive is not an import
path, and the active checkout intentionally contains no historical report tree
or decision-log index. The familiar records remain development/regression
fixtures; no frozen post-cutover evaluation set has been constructed.
