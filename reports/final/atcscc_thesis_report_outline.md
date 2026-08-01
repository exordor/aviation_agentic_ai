# Current ATCSCC Thesis Report Outline

Status: current report spine for the ingestion-first mainline. This is an
outline and claim map, not a completed thesis manuscript or a benchmark report.

## Working title

**ATMONTO-Grounded Agentic HybridRAG for Evidence-Bounded Aviation Knowledge
Integration**

## Central claim

The project demonstrates a reusable method for integrating heterogeneous
aviation evidence under an ATMONTO-aligned semantic contract and answering
natural-language questions through a model-directed, evidence-bounded
HybridRAG Query Agent.

The claim is retrospective and source-bounded. The system does not claim live
ATC support, causal explanation, operational-effectiveness scoring, TMI
recommendation, or reconstruction of an internal FAA decision process.

## Research questions

### RQ1 — Semantic integration

Can heterogeneous ATCSCC, FAA authority, Weather, BTS, and Flight/Airspace
records be published into one authoritative store while preserving source
roles, temporal boundaries, ATMONTO terms, and exact evidence anchors?

### RQ2 — Model-directed retrieval

Can an LLM Query Agent route each natural-language question to a bounded family
of exact, graph, lexical, vector, context, and source-read tools, then produce
an answer whose statements pass deterministic support validation?

### RQ3 — Reusable knowledge spine

Can the same publication, provenance, retrieval, and support contracts admit
TMI, Flight/Airspace, reference, Weather, and reviewed association roots
without introducing a separate event-specific runtime?

## Chapter spine

### 1. Motivation and scope

- Heterogeneous aviation evidence cannot be answered reliably from one source.
- ATCSCC advisories provide the mature demonstrator, not the permanent domain
  boundary.
- Define the difference between published facts, context associations,
  public observations, and unsupported causal or recommendation claims.

### 2. Background and related foundations

- NASA ATMONTO as the admitted TBox and application-profile vocabulary.
- ATMGRAPH as a reference for ABox construction and cross-source querying.
- HybridRAG as the combination of exact, lexical, vector, and graph retrieval.
- Bounded tool-using Agents as the interaction mechanism, not as a reason to
  turn deterministic parsers and stores into artificial Agents.

### 3. Data and evidence model

- ATCSCC TMI records: published measures, facilities, time windows, and
  source-declared reasons.
- FAA/NASR authority: facility and terminology identity.
- METAR/TAF: time-aligned Weather reports and non-causal context.
- BTS: source-qualified public observations, never FAA demand or capacity.
- NASA 2014 and May 2026 Flight/Airspace domains: separate temporal scopes.
- Optional Web Evidence sidecar: public-document context with exact source
  versions and anchors.

The active configuration contains 718 advisory records. The five familiar
records are regression fixtures, not a manually reviewed Gold set or a
representative evaluation sample.

### 4. System architecture

Describe the five planes:

1. Evidence Plane;
2. Deterministic Ingestion Orchestration;
3. Semantic and Trust Plane;
4. Knowledge and Retrieval Plane;
5. Agent Interaction Plane.

The authoritative SQLite evidence store contains immutable source records,
semantic publications, facts, evidence links, profile gaps, associations,
observations, and chunks. FTS5, Chroma, RDF/Turtle, JSONL, and Neo4j are
rebuildable or optional views.

### 5. ATMONTO-grounded publication

- The active TMI registry is rooted at
  `atm:TrafficManagementInitiative`.
- GDP, Ground Stop, and ReRoute use the active application-profile families.
- Flight, Aircraft/Model, Airport/ARTCC, Route, TrackPoint, Sector, Weather,
  and reviewed association roots reuse the generic publication spine.
- One write-free Formal Publication Kernel is the final admission authority.
- Incomplete or unsupported evidence remains `insufficient` or a profile gap;
  it is not filled by Weather, BTS, or model memory.

### 6. Model-directed HybridRAG interaction

Every valid natural-language question activates the Query Agent. A first LLM
call selects one or more capability families. The bounded action-observation
loop then chooses read-only tools, verifies candidates with exact source reads,
and produces a `QueryEvidenceBundle` for statement-level support validation.

The Semantic Resolution Agent is different: it is selectively activated only
when deterministic authority resolution leaves multiple plausible candidates.
Normal ingestion remains deterministic.

### 7. Running example

Use GDP 138 only as an explanatory walkthrough:

> What was published, what reason did the source declare, and what Weather
> context and BTS public observations were retained?

The answer must keep the following layers separate:

- ATCSCC publication and declared reason;
- FAA facility identity;
- time-aligned Weather context;
- source-qualified BTS observations;
- limitations and missing states.

The walkthrough is historical compatibility evidence, not a current-runtime
benchmark.

### 8. Evaluation and evidence status

Report results by evaluation mode:

- `offline_software_test`: contracts, storage, retrieval plumbing, and
  validation; fake models do not establish Agent quality.
- `live_smoke`: small real-provider compatibility checks, not benchmarks.
- `live_experiment`: only when a frozen suite and the required real-call
  threshold are actually completed.

Current tracked smoke reports separate provider-call success from answer
acceptance and preserve negative outcomes. No frozen post-cutover benchmark
set currently exists.

### 9. Limitations and future work

- Formal decision-process representation with alternatives, constraints,
  rationale, and outcomes.
- Initial/revision/extension/cancellation episode grouping.
- National Playbook PDF grounding.
- Causal Weather analysis and operational-effectiveness studies.
- Outcome-aware similarity and TMI recommendation.
- Human or aviation-expert review.

These are future research directions, not current system capabilities.

## Current figures and evidence

Use the maintained figures and documents below as the primary presentation
objects:

- `docs/figures/cross_source_evidence_motivated_example.{drawio,png}`
- `docs/figures/aviation_hybridrag_system_architecture.{drawio,png}`
- `docs/figures/bounded_query_agent_workflow.{drawio,png}`
- `docs/figures/heterogeneous_source_formats.{drawio,png}`
- `docs/architecture_narrative.md`
- `docs/multi_agent_kg_system_design.md`
- `RESEARCH_AUDIT.md`
- `GOALS.md`
- `ARTIFACT_INDEX.md`

Historical extraction-loop figures, old Gold-sample claims, and the retired
competency runner must not be presented as the current architecture.
