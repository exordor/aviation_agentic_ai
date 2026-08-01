# Project Audit And Context Router

Audit date: 2026-08-01

This is the default entry point for a new project task. It records current
implementation truth and routes historical material without making it default
context.

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
routing call first selects the `source`, `tmi`, and/or `flight_airspace`
capability families; the Agent then selects exact, graph, lexical, vector,
context, and source-read tools from that bounded subset. Deterministic support
validation checks the result before release.

The TMI slice is rooted at the admitted ATMONTO
`TrafficManagementInitiative` instance. The generic publication spine now also
admits Flight/Airspace, reference, Weather, and reviewed association roots.
Store membership organizes accepted facts without asserting that the system
reconstructed an internal decision process. ATMONTO supplies admitted schema
terms. ATMGRAPH supplies ABox-construction and cross-source-query principles,
not another imported dataset or an exact replication target.

The public commands are:

```text
ingest
reindex
ask
neo4j-export
export-event
```

The root CLI presents `agent-system` plus the still-supported `ontology`,
`source`, `cqs`, and `report` research utilities. Retired PHAK demos and the
historical `cross-source` workflow are not registered as current root commands.
Their implementations and artifacts remain classified through
`ARTIFACT_INDEX.md`.

There is no required batch snapshot, run-directory query path, legacy reader,
or compatibility alias.

## Verified Implementation Capabilities

- The only model-backed roles are the Query Agent invoked for every valid
  natural-language question and the selectively activated Semantic Resolution
  Agent.
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
- The dataset-bound SQLite store persists immutable source versions, exact
  anchors, active and historical event publications, semantic facts, evidence
  links, profile gaps, Weather associations, BTS public observations, source
  chunks, vector-index state, and compact usage telemetry.
- The former `Corpus v2` batch snapshot has no current runtime role.
  `data/evaluation_runs/agent_system/` contains ignored evaluation evidence,
  not canonical knowledge or a query backend.
- Ingestion commits each source version and accepted event publication
  independently. A failed later record does not invalidate earlier accepted
  evidence, and queryability does not depend on completing a batch manifest.
- SQLite FTS5 provides lexical source retrieval. Chroma provides independently
  rebuildable source-record and TMI-event vector collections. Vector state is
  current only when it matches the store knowledge revision.
- RDF/Turtle, JSONL, and Neo4j are optional, rebuildable exports over all
  active formal knowledge roots. They are not mandatory runtime databases and
  do not write back into SQLite.
- Every valid `ask` activates the Query Agent. There is no fixed question
  registry or deterministic answer fallback.
- The Query Agent selects among three capability families containing 18
  bounded, read-only evidence tools: `source` (3), `tmi` (6), and
  `flight_airspace` (9). The first model call selects families; subsequent
  turns see only that subset.
- The evidence loop permits at most 6 provider turns, 6 tool calls in one turn,
  and 10 evidence-tool calls in total.
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
`--domain all|tmi|flight-airspace`; `--advisory-id` is valid only with
`--domain tmi`.
The ingest summary reports a canonical checksum of the fully resolved
configuration. Store revisions remain content-driven rather than treating an
experimental configuration snapshot as runtime knowledge identity.

## Current Intake

The active configuration contains 718 advisory records. `ingest --domain tmi`
processes all configured advisories when no `--advisory-id` is supplied. With
one or more advisory IDs, it registers and constructs only those advisory
records while retaining the shared authority and context evidence required by
the pipeline.
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
- A retained checksum-bound deterministic supplement records the earlier
  F1/F3S/S4/S1S comparison: S4/S1S use NASA's 2014 sample trajectories;
  F1/F3S are explicitly labelled May 2026 FAA/BTS/Weather proxies. It is
  historical evidence, not the current runtime boundary.

## Evaluation Boundary

`offline_software_test` covers deterministic software, contracts, state
transitions, storage, retrieval plumbing, and validation. Fake or scripted
models are allowed only in that mode and do not establish LLM or Agent quality.

Tracked earlier reports remain frozen compatibility evidence for their named
architectures. They must not be relabeled as ingestion-first Query Agent
performance. Provider-call success and task acceptance remain separate claims.

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
| Active execution queue | `TODO.md` |
| Normative system design | `docs/multi_agent_kg_system_design.md` |
| Artifact ownership and history | `ARTIFACT_INDEX.md` |
| Reproduction commands | `REPRODUCIBILITY.md` |
| Structural decision history | `DECISION_LOG.md` |
| Optional historical experiments | `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`, `EXPERIMENTS.md`, `RESULTS.md` |

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
