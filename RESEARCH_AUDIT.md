# Project Audit And Context Router

Audit date: 2026-08-02

This is the default entry point for a new project task. It records current
implementation truth and routes historical material without making it default
context.

This is the single authority for changing project status, dataset scope,
implementation capabilities, and evaluation observations. Other current
documents may explain the system for readers, but must not introduce a
competing status narrative.

Historical plans and large report bundles are kept in the dated external
archive described by `docs/repository_artifact_policy.md`; do not treat their
absence from the checkout as a missing runtime dependency.

## Current Project Snapshot

Aviation Agentic AI is a runnable **ATMONTO-Grounded Agentic HybridRAG for
Heterogeneous Aviation Knowledge Integration**. Retrospective FAA ATCSCC TMI
events are the current architecture demonstrator and reusable vertical slice,
not the permanent subject boundary.

```text
Evidence Plane
  -> Deterministic Ingestion Orchestration
  -> Semantic and Trust Plane
  -> Knowledge and Retrieval Plane
  -> Agent Interaction Plane
```

The Query Agent is invoked for every valid natural-language question. One LLM
routing call first selects the `source`, `tmi`, `knowledge`, and/or
`flight_airspace`
capability families; the Agent then selects exact, graph, lexical, vector,
context, and source-read tools from that bounded subset. When explicitly
authorized, an additional `web` family exposes allowlisted sidecar reads.
Deterministic support validation checks the result before release.

The document-to-KG capability is framework-level. Its public boundaries are
the `document` ingestion domain, `knowledge` query family, generic ontology KG
contracts, and `knowledge_entities_v1` index. FAA JO 7210.3EE Chapter 18 is the
current `faa_order_*` adapter; its `PolicyRule` vocabulary does not define the
framework or its public API.

The generic publication spine admits ATMONTO-aligned TMI, Flight/Airspace,
reference, Weather, and reviewed association roots. TMI instances are the
current regression vertical slice, rooted at an admitted ATMONTO
`TrafficManagementInitiative`, rather than the permanent subject boundary.
Store membership organizes accepted facts without asserting that the system
reconstructed an internal decision process. ATMONTO supplies admitted schema
terms. ATMGRAPH supplies ABox-construction and cross-source-query principles,
not another imported dataset or an exact replication target.

The current research demonstrator realizes four ATMONTO use cases: data
query/search, information organization, information integration, and
terminology standardization. Information exchange is retained as the broader
interoperability motivation only; no external ATMONTO exchange protocol is
claimed as implemented.

The semantic parity baseline is the six-module ATMONTO catalog recorded in
`data/ontology/curated/atmonto_semantic_coverage_v1.json`. It inventories 105
classes, 106 object properties, 176 datatype properties, 83 hierarchy axioms,
282 property signatures, and 13 cardinality constraints. The runtime uses a
closed active subset; the report separately marks explicit next-scope terms as
`planned` and the remaining upstream terms as `unsupported`. This prevents a
small runtime slice from being presented as the whole aviation ontology while
also making the KG's semantic expansion measurable.

The public commands are:

```text
ingest
reindex
ask
neo4j-export
export-event
```

The root CLI presents only `agent-system`. The former `ontology`, `source`,
`cqs`, `report`, PHAK, and historical `cross-source` implementations and
artifacts are outside the active checkout in the dated external archive.
`docs/repository_artifact_policy.md` records the retention boundary.

There is no required batch snapshot, run-directory query path, legacy reader,
or compatibility alias.

## Verified Implementation Capabilities

- The default model-backed roles are the Query Agent invoked for every valid
  natural-language question and the selectively activated Semantic Resolution
  Agent. An opt-in Ontology Candidate Fact Generator now provides a sealed
  candidate-ABox construction path; it is not wired into default `ingest` and
  has no live performance claim.
- One registry rooted at `atm:TrafficManagementInitiative` drives GDP, GS, and
  ReRoute detection, required-field preflight, formal property mapping, and
  retrieval labels.
- Deterministic parsing and FAA facility/terminology authority services
  preserve source-family boundaries.
- The Semantic Resolution Agent activates only for genuine multi-candidate
  authority ambiguity.
- Event Evidence Integration compiles source-supported sealed evidence and
  returns honest `insufficient` when required evidence is absent; it does not
  call a provider.
- The write-free Formal Publication Kernel is the sole publication authority
  for semantic facts under the active TMI, Weather, public-observation,
  Flight/Airspace, and reference profiles. Source-supported association roots
  are emitted by a separate deterministic derivation materializer.
- Candidate facts from the opt-in ontology construction path use the same
  publication kernel. Deterministic diagnostics report ontology compliance,
  evidence-anchor coverage, profile gaps, duplicate semantic facts, and
  blocked publications; these are software-contract metrics, not model
  quality results. The FAA JO 7210.3EE document adapter now uses full-Chapter-18
  recursive chunks, a compact ATMONTO+FAA schema, separate LLM NER and relation
  extraction, deterministic entity resolution, and incremental publication of
  evidence-bound ontology entities. The completed versioned live experiment used
  `deepseek-v4-flash` with temperature 0, thinking disabled, no retries, and no
  response cache. It made 210/210 successful real calls (168 NER and 42 RE),
  used 876,508 input and 269,963 output tokens, resolved 1,452 entities,
  validated 218 relations, and retained 840 publications with 3,293 facts and
  4,124 evidence links. Six chunks abstained and two local chunks/publication
  groups remained blocked, so the runner completed but construction status is
  honestly `blocked`; this is not reported as a perfect extraction result. The
  online Query Agent uses knowledge-entity
  discovery, exact graph reads, and separate source-anchor reads.
- The dataset-bound SQLite store persists immutable source versions, exact
  anchors, active and historical event publications, semantic facts, evidence
  links, profile gaps, Weather associations, BTS public observations, source
  chunks, vector-index state, compact usage telemetry, and optional
  `web_document` versions collected through the sidecar.
- The former `Corpus v2` batch snapshot has no current runtime role.
  `data/evaluation_runs/agent_system/` contains ignored evaluation evidence,
  not canonical knowledge or a query backend.
- Ingestion commits each source version and accepted event publication
  independently. A failed later record does not invalidate earlier accepted
  evidence, and queryability does not depend on completing a batch manifest.
- SQLite FTS5 provides lexical source retrieval. Chroma provides independently
  rebuildable source-record, TMI-event, and knowledge-entity vector collections. Web source
  chunks enter the source-record collection only; TMI-event vectors remain
  limited to admitted TMI publications. Vector state is current only when it
  matches the store knowledge revision.
- RDF/Turtle, JSONL, and Neo4j are optional, rebuildable exports over all
  active formal knowledge roots. They are not mandatory runtime databases and
  do not write back into SQLite.
- Every valid `ask` activates the Query Agent. There is no fixed question
  registry or deterministic answer fallback.
- The Query Agent selects among four core capability families containing 21
  bounded, read-only evidence tools: `source` (3), `tmi` (6), `knowledge` (3 plus
  the shared exact `read_source` tool),
  and `flight_airspace` (9). The knowledge family discovers and reads published
  ontology roots by candidate discovery and exact graph reads; it is distinct
  from exact PDF source reads. An explicitly
  authorized sidecar adds an optional `web` family with three read-only tools.
  The first model call selects families; subsequent turns see only that subset.
- The evidence loop permits at most 7 retrieval turns, 6 tool calls in one
  turn, and 16 evidence-tool calls in total. When a retrieval boundary is
  reached after evidence exists, one tool-free Answer Formation turn receives
  a fresh Evidence Packet instead of inheriting the tool transcript.
- Search candidates do not support final source-record claims by themselves;
  `read_source` supplies the exact source version and anchor.
- Source discovery also returns active event identities bound by the
  authoritative store, allowing an unscoped natural-language question to move
  from source discovery to event, context, observation, and graph tools.
- Each final statement is checked against returned event, fact, gap, context,
  observation, graph-path, source-version, anchor, chunk, and similarity
  identifiers as appropriate.
- Missing support yields `insufficient`; provider, contract, or dependency
  failures yield `blocked`.

The active top-level configuration composes separate runtime, source, and
dataset/temporal-scope files. The CLI exposes
`--domain all|tmi|document|flight-airspace|web`; `--advisory-id` is valid only with
`--domain tmi`. The Web domain remains disabled unless a local configuration
overlay and `--allow-live-web` authorize it.
The ingest summary reports a canonical checksum of the fully resolved
configuration. Store revisions remain content-driven rather than treating an
experimental configuration snapshot as runtime knowledge identity.

## Current Intake

Research scope is selected by the dataset and temporal-scope configuration.
The recommended high-coverage public prototype is the one-day NASA ATMONTO
sample (`configs/atmonto_public_sample_v1.yaml`), which keeps Flight,
Weather, TMI, and infrastructure records in one explicit 2014 temporal
domain. The 2026 ATCSCC inventory is an optional historical TMI source, not a
definition of the current system scale or research cohort.

`ingest --domain tmi` processes all advisories in the explicitly selected
source configuration when no `--advisory-id` is supplied. With one or more
advisory IDs, it registers and constructs only those advisory records while
retaining the shared authority and context evidence required by the pipeline.
Terminal `ok` and `insufficient` versions are skipped on a later run; blocked
versions can be retried.

The legacy cross-source experiment deterministically selected 68 records whose
full text mentioned JFK, EWR, LGA, KJFK, KEWR, or KLGA. Its 46 active-family
eligible / 3 incomplete / 18 boundary / 1 deferred split is automated
registry/preflight output, not manual review, a representative sample, or the
active runtime scope.

The tracked acceptance fixtures preserve:

- GS `2026-05-19:123`: declared reason as a profile gap;
- GDP `2026-05-19:138`: formal `weather`;
- GDP cancellation `2026-05-20:020`: honestly missing reason;
- ReRoute `2026-05-19:108` and `2026-05-20:137`: formal
  `atm:ReRouteTMI`, with unsupported ARTCC scope retained as a profile gap.

These are development/regression fixtures, not evaluation samples,
representative coverage, or special execution routes.

The Flight/Airspace domain publishes the configured NASA July 2014 public
sample and the bounded May 2026 operational-source slice into the same store,
while preserving distinct temporal-domain identifiers and prohibiting a
cross-temporal join. It exposes Flight, Airport/ARTCC, trajectory, sector,
Flight–Weather association, and TMI-applicability candidate queries through
the public Query Agent.

The July 2014 public-sample build now has a complete source-grounded ABox
construction path for every configured NASA sample layer. In the verified
fresh build, 24,820 source roots were selected; 24,817 were accepted, three
airport–ARTCC references were insufficient, and none were blocked. The formal
projection contains 164,182 unique ATMONTO-aligned facts across Flight,
Airport, ARTCC, NavigationFix, Sector, METAR, TAF, AirportStatisticsData, and
TMI roots. The projection is bounded by the local six-module ATMONTO catalog;
it is a complete KG for this configured public sample, not a claim of complete
NASA or national ATM coverage. Derived association roots remain separate and
non-causal.

## Evidence Boundaries

- ATCSCC records support published TMI fields and source-declared reasons.
- FAA authority sources support identity resolution, not event facts.
- TAF/METAR records may become formal Weather report facts.
- Event-to-Weather associations carry `causal_claim=false` and stay outside
  the formal graph.
- BTS rows may become source-qualified public observations through their own
  profile.
- BTS observations are not FAA demand, AAR, capacity, EDCT, decision rationale,
  operational effectiveness, or proof that a TMI caused an outcome.
- Weather or BTS evidence never fills a missing declared reason.
- Profile gaps remain source-supported non-formal records.
- Lexical and vector hits are candidate discovery, not source verification.
- Optional Web Evidence pages are public-document context only. Search
  candidates require an exact sidecar fetch/span before supporting a claim;
  the sidecar cannot create a TMI reason or causal relation.
- A retained checksum-bound deterministic supplement records the earlier
  F1/F3S/S4/S1S comparison: S4/S1S use NASA's 2014 sample trajectories;
  F1/F3S are explicitly labelled May 2026 FAA/BTS/Weather proxies. It is
  historical evidence, not the current runtime boundary.

## Evaluation Boundary

`offline_software_test` covers deterministic software, contracts, state
transitions, storage, retrieval plumbing, and validation. Fake or scripted
models are allowed only in that mode and do not establish LLM or Agent quality.

The Chapter 18 ontology-construction `live_experiment` completed its provider
run with `deepseek-v4-flash`, temperature 0, thinking disabled, a 10,000-token
output ceiling, no automatic retries, and local response caching disabled.
All 210 attempted calls returned successfully: 168 NER calls and 42
relation-extraction calls. The run used 876,508 input tokens and 269,963 output
tokens; the provider reported 772,096 cache-read input tokens and zero
cache-creation tokens. It resolved 1,452 entities, validated 218 relations,
and retained 840 incremental publications containing 3,293 facts and 4,124
evidence links. Six chunks abstained and two local chunk/publication groups
remained blocked. Consequently, `runner_status=completed` while
`construction_status=blocked`; provider success is not being relabeled as
perfect extraction acceptance.

The ignored raw provider responses are stored at
`data/evaluation_runs/agent_system/chapter18-atmonto-kg-v1/raw_provider_responses.jsonl`
(SHA-256 `3854232e37b5ec19b012dd947351b9dde11284a323d0745057fa6a89a574a29b`).
Parsed outputs are stored separately at
`data/evaluation_runs/agent_system/chapter18-atmonto-kg-v1/parsed_extraction_outputs.jsonl`
(SHA-256 `9d0211ac6106526d0c95b17f297c5ad7697d76b179e8cc2b0da688819746e3b6`).
The experiment manifest verified both artifacts and bound them to knowledge
revision 841. These files are evaluation evidence, not the runtime knowledge
backend.

A separate post-build `live_smoke` exercised the ordinary natural-language
Query Agent over the current knowledge entity index, formal graph, and exact PDF
reader. GDP, Ground Stop, System Operations responsibility, and coordination
questions each achieved an accepted real-model run. Their accepted trajectories
used respectively 9/14, 8/15, 7/9, and 4/2 model/tool calls. Independent repeats
of the responsibility question also exposed one pre-fix multi-anchor binding
rejection and one malformed final JSON response. The former produced a
regression test and now permits the union of multiple independently exact
source reads; the latter remains an observed provider-output failure. These
are compatibility observations, not a statistical stability or quality
benchmark.

Earlier reports remain frozen compatibility evidence for their named
architectures in the dated external archive. They must not be relabeled as
ingestion-first Query Agent performance. Provider-call success and task
acceptance remain separate claims.

The earlier v4 query compatibility smoke recorded 11 real
`deepseek-v4-pro` calls and accepted 5/5 development/regression tasks,
including a source-bound Weather graph path. It predates the persistent-store
query cutover and is not a frozen holdout or model benchmark.

The ingestion-first store-bound smoke completed with `deepseek-v4-pro`,
temperature 0, thinking disabled, and no automatic retries. All 6 provider
calls returned without provider error; the run used 113,806 input and 5,774
output tokens. One of three Query Agent tasks passed. Two failed the typed
answer-contract/evidence acceptance checks despite successful provider calls.
The ignored raw-response artifact and parsed-result artifact contain 6 and 3
rows respectively and are checksum-bound from the tracked sanitized report.
All 6 call IDs are unique, every parsed trial names its captured calls, and the
raw/parsed binding check passed.
This is compatibility evidence over development/regression tasks, not a frozen
holdout or model-quality benchmark.

The tracked ingestion-first GDP 138 flagship walkthrough is historical
pre-family-router TMI-slice evidence. Its single natural-language Query Agent task
passed (1/1), all 3 real `deepseek-v4-pro` calls returned, and all 5 bounded
tool executions were bound to the accepted trial. The answer retained exact
ATCSCC source support, non-causal Weather context, and source-qualified BTS
observations. This is not current-runtime acceptance, a statistical benchmark,
or evidence of general model quality.

The current cross-domain `live_smoke` used `deepseek-v4-pro`, temperature 0,
thinking disabled, and no automatic retries. All 33/33 real provider calls
returned. Routing and retrieval passed 6/6 tasks; grounding and answer
acceptance passed 5/6. TMI, Flight, Weather, Sector, and cross-domain
applicability tasks passed. The unsupported actual-control/causal task should
have terminated as `insufficient`, but the Agent continued retrieving until
the 10-tool ceiling and returned `blocked`. This is a preserved stop-policy
failure and a compatibility result, not a statistical benchmark.

No natural ambiguity has been identified in the legacy deterministic NYC
selection that activates the Semantic Resolution Agent; synthetic ambiguity
fixtures remain offline orchestration tests and are not current-source
performance evidence.

## Context Routing

| Need | Read |
| --- | --- |
| Durable system goal and boundaries | `GOALS.md` |
| Installation and current commands | `README.md` |
| Current decisions and deferred work | `GOALS.md` |
| Normative system design | `docs/multi_agent_kg_system_design.md` |
| Artifact ownership and history | `docs/repository_artifact_policy.md` |
| Reproduction commands | `REPRODUCIBILITY.md` |
| Optional Web Evidence operations | `docs/wigolo_web_evidence_operations.md` |
| Structural decision history | `DECISION_LOG.md` |
| Optional historical experiments | Dated external archive `docs/legacy_runtime/` |

Do not preload optional experiments, historical stage reports, ignored local
stores or exports, or archives.

## Current Non-Capabilities

The project does not provide:

- general aviation QA;
- live ATC support;
- a complete aviation ontology;
- causal explanation;
- FAA decision inputs, alternatives, constraints, rationale, or trade-offs;
- operational effectiveness or optimality;
- lifecycle episode reconstruction;
- outcome-aware similarity or TMI recommendation;
- external expert certification;
- verified actual TMI control of a specific flight or caused flight impact.
- unrestricted web browsing, background crawling, or a Web Evidence sidecar
  that bypasses the configured allowlist.

Flight-level and sector-level records are now public `agent-system ask`
routes, but their evidence boundary remains narrow. The original 2012 KATL
F1/F3S database was not recovered: the retained modern F1/F3S report is a proxy
reconstruction, and NASA trajectory knowledge covers only the published 2014
sample rather than national operations. Weather matching is temporal and
non-causal; current FAA aircraft registry data is a later technical lookup,
not historical aircraft-state proof.

## Verification Defaults

- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Code changes: focused tests during development, then one final
  `uv run ruff check .`, `uv run pytest -q`, `uv build`, and
  `git diff --check`.
- Result claims require inspection of the active implementation and named
  artifacts, not historical test counts or executor summaries.
