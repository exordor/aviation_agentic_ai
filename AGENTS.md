# AGENTS.md

Repository-level instructions for coding agents. Keep this file operational;
detailed designs and historical protocols live under `docs/`.

## Project Posture

This is a **system and framework construction project**. Its research-facing
positioning is **ATMONTO-Grounded Agentic HybridRAG for Heterogeneous Aviation
Knowledge Integration**. Retrospective FAA ATCSCC TMI records are the current
end-to-end vertical slice; they are not the architecture's permanent subject
boundary.

The active pipeline is:

```text
composed runtime + source + dataset/temporal-scope configuration
  -> configured ATCSCC, FAA authority, Weather, BTS, NASA ATMONTO,
     aircraft-registry, and airspace source artifacts
  -> immutable source assets, source versions, and anchors
  -> selected ingestion domain: all | tmi | flight-airspace
     -> TMI: classification, preflight, AdvisoryParser, authority services,
        optional Semantic Resolution, Weather/BTS preparation, and
        deterministic Event Evidence Integration
     -> Flight/Airspace: source-specific deterministic adapters,
        temporal-domain boundaries, and reviewed cross-source derivations
  -> semantic facts: shared write-free Formal Publication Kernel
     -> generic knowledge-root publication spine
  -> cross-source associations: deterministic derivation materializer
  -> authoritative SQLite evidence and semantic store
  -> source chunks and SQLite FTS5
  -> rebuildable source-record and TMI-event Chroma collections
  -> every valid natural-language ask activates the bounded Query Agent
     -> LLM selects source, tmi, and/or flight_airspace tool families
     -> selected subset of 18 read-only evidence tools
     -> per-statement evidence and claim-boundary validation
     -> answer, insufficient, or blocked
```

The dataset-bound SQLite evidence store is the canonical persisted knowledge
and evidence layer. The TMI slice is rooted at an admitted ATMONTO TMI
instance; Flight/Airspace, reference, Weather, and reviewed association roots
use the same generic publication spine. None invents a decision-process
object. SQLite FTS5 and Chroma are rebuildable indexes. RDF/Turtle, JSONL KG,
and Neo4j are optional all-root offline exports.
The retired `Corpus v2` batch snapshot is historical only. Files under
`data/evaluation_runs/agent_system/` are evaluation evidence, not persisted
knowledge and not a runtime query backend.
The versioned application profile aligns the active TMI schema with exact
ATMONTO terms and constrains publication; it is not a separate Agent and is not
claimed to be a complete aviation ontology. ATMGRAPH is the reference for
constructing and querying the populated ABox, not an imported dataset or an
exact system replica.

The normative implementation design is
`docs/multi_agent_kg_system_design.md`. Reader-facing documents use full Agent
names, not internal alphanumeric labels.

Historical plans, PHAK-era reports, and retired compatibility contracts are
not part of the default checkout. Their external-archive policy is documented
in `docs/repository_artifact_policy.md`; do not restore them or add new
runtime dependencies on them unless a legacy experiment is explicitly being
reactivated.

## Current Status

- The active implementation contains incremental ingestion, a dataset-bound
  SQLite evidence store, the Formal Publication Kernel, deterministic Event
  Evidence Integration, store-backed exact and graph reads, SQLite FTS5,
  rebuildable Chroma indexes, optional exports, and the bounded HybridRAG Query
  Agent.
- `configs/aviation_knowledge_v1.yaml` composes separate runtime, source, and
  dataset/temporal-scope files. Do not collapse those concerns back into one
  experimental configuration.
- The only model-backed roles are the Query Agent invoked for every valid
  natural-language question and the selectively activated Semantic Resolution
  Agent.
- The TMI registry root is `atm:TrafficManagementInitiative`; its active
  application-profile families are GDP, GS, and ReRoute. Family detection,
  preflight, formal property mapping, and retrieval labels share one registry.
- Flight/Airspace ingestion publishes formal Flight, Aircraft/Model,
  Airport/ARTCC, Route, TrackPoint, Sector, and Weather roots through the
  shared Formal Publication Kernel and generic knowledge-root spine. Reviewed
  association roots are separate deterministic derivation publications.
  NASA 2014 and May 2026 records retain distinct temporal domains and are not
  cross-temporally joined.
- The store-backed event graph exposes event-scoped formal edges and derived
  cross-source evidence paths for Weather context and BTS public observations.
  The paths preserve source-role bindings and do not add causal graph facts.
- The five tracked cross-family records are development/regression fixtures,
  not the system scope. They preserve profile-gap, formal weather, honest
  missing-reason, and ReRoute states. Public answers are model-routed and
  evidence-bound, not deterministic sentence matches.
- Complete active-profile records use the zero-call deterministic compiler
  when all required slots are resolved; source identifiers never choose that
  path. The Formal Publication Kernel remains the sole final publication
  authority.
- Every valid public `ask` invokes the Query Agent. A first model call selects
  one or more of `source`, `tmi`, and `flight_airspace`; the evidence loop then
  sees only that subset of 18 registered read-only tools. There is no fixed
  question registry or deterministic answer fallback.
- The Query Agent budget is 6 provider turns, at most 6 evidence-tool calls in
  one turn, and at most 10 evidence-tool calls in total.
- Search tools return candidates. A source-record statement requires an exact
  `read_source` result with immutable source-version and anchor support.
- The ingestion-first storage cutover is complete. The public commands are
  `ingest`, `reindex`, `ask`, `neo4j-export`, and `export-event`. There is no
  run-directory query path, mandatory batch snapshot, old reader, or command
  compatibility path.
- `ingest --domain all|tmi|flight-airspace` registers immutable source
  versions, skips terminal
  `ok/insufficient` versions, retries blocked versions, and commits each
  accepted knowledge-root publication independently. A targeted advisory
  backfill registers only the selected advisory records plus shared
  authority/context evidence.
  Queryability does not depend on finishing a batch manifest.
- The active configuration contains 718 advisory records. The TMI domain
  processes all of them unless an operator supplies an explicit
  `--advisory-id` subset.
- The legacy cross-source experiment deterministically selected 68 records
  whose full text mentioned JFK, EWR, LGA, KJFK, KEWR, or KLGA. Its 46/3/18/1
  split is automated registry/preflight output, not manual review, a
  representative sample, or a current runtime cohort.
- SQLite FTS5 indexes exact source chunks. Chroma has separately rebuildable
  source-record and TMI-event collections; a collection is usable only when
  its indexed knowledge revision matches the store.
- RDF/Turtle, JSONL KG, and Neo4j are optional all-root current-store exports
  and are never Query Agent prerequisites.
- The system output ceiling is 10,000 tokens for the Query Agent; the compact
  Semantic Resolution decision remains capped at 256 tokens. Event Evidence
  Integration is deterministic and makes no provider call.
- The tracked v1-v3 DeepSeek contracts/results and later compact-selection runs
  are historical compatibility artifacts. They must not be relabeled as
  current role, persistent-store, or cross-family performance.
- The pre-cutover `live_smoke` v4 completed with DeepSeek `deepseek-v4-pro`: 11 real provider
  calls, 5/5 Query Agent tasks accepted, and the required cross-source Weather
  graph path observed. This is historical compatibility evidence, not a frozen
  holdout, model benchmark, or ingestion-first result.
- The ingestion-first `live_smoke` v1 completed against the persistent store
  with 6/6 returned real `deepseek-v4-pro` calls and no provider errors. One of
  three Query Agent tasks passed; two failed the answer-contract/evidence
  acceptance checks. Raw provider responses and parsed trial outputs are
  retained separately in ignored runtime artifacts. This negative result is
  compatibility evidence, not a benchmark.
- The tracked ingestion-first GDP 138 flagship walkthrough is historical
  pre-family-router TMI-slice evidence: 1/1 natural-language Query Agent task passed,
  3/3 real `deepseek-v4-pro` calls returned, and 5/5 bounded tool executions
  were bound to the accepted trial. It is not current-runtime acceptance, a
  benchmark, or evidence of general model quality.
- The cross-domain `live_smoke` completed with `deepseek-v4-pro`: 33/33 real
  provider calls returned; routing and retrieval passed 6/6 tasks; grounding
  and answer acceptance passed 5/6. The unsupported actual-control/causal task
  exhausted the 10-tool budget and returned `blocked` instead of
  `insufficient`; preserve this as an observed stop-policy failure, not a
  hidden success or benchmark result.
- The five familiar records are development/regression fixtures only. No frozen
  post-cutover evaluation set currently exists; `future_frozen_evaluation` is
  `NOT CONSTRUCTED`. Historical suites remain compatibility artifacts and
  cannot establish current performance.
- The read-only visualization prototype is isolated on
  `codex/kg-visualization-research`. Visualization is paused and is not the
  active `main` implementation track.
- Comparison experiments, Gold adjudication, broader ATMONTO family coverage,
  weather expansion, causal explanation, and recommendation remain optional or
  deferred unless explicitly reactivated.

## Default Context

For a new task:

1. Read `RESEARCH_AUDIT.md`.
2. Read `GOALS.md`.
3. Load `README.md`, `TODO.md`, or a design document only when the task needs
   that layer.

Do not preload `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`, `EXPERIMENTS.md`,
`RESULTS.md`, stage-report directories, ignored stores/exports, or archived
PHAK/web-demo material. They describe optional evaluation or historical work,
not the default system scope.

Use English for active code, contracts, prompts, CLI messages, tests,
documentation, and generated artifacts. Preserve non-English text only when it
is explicitly identified source material.

## Execution Policy

Before proposing a new implementation stage, state:

- the user-facing or system capability being advanced;
- the smallest end-to-end result;
- the minimum components needed;
- the evidence that will show it works;
- the success and failure conditions;
- what is explicitly deferred.

Prefer the smallest runnable system increment. Do not add a role, data source,
guardrail, framework, schema layer, or benchmark unless an observed failure or
the approved task requires it. Do not turn an implementation task into a paired
comparison experiment without an explicit scope decision.

Every mainline implementation batch must add or simplify a user-visible
capability. A validator-only batch requires a reproduced failure through a
supported workflow or an explicit user request.

## Research Prototype Effort Boundary

- Optimize for the end-to-end architecture, runnable pipeline, and approved
  research semantics rather than production-grade hardening.
- Add a guard or adversarial test only when an approved acceptance scenario
  requires it or a failure is reproduced through a supported user workflow.
- Preserve the canonical reason states, time boundaries, source-role
  separation, zero-call insufficient behavior, bounded read-only access, and
  the prohibition on causal or recommendation claims.
- Validate external inputs and final publication/query boundaries. Do not add
  redundant checks for manually forged internal objects that the supported
  pipeline does not construct.
- Symlink attacks, path traversal, concurrent mutation, secret injection,
  contradictory hand-built audit records, and hostile cross-run tampering are
  deferred unless a deployment or security task explicitly activates them.
- Use one bounded review pass. After fixes, run focused tests and one final
  repository verification; do not start recursive reviewer-fix-review cycles.
- Once the approved acceptance scenarios pass, record production-only residual
  risks as deferred and stop the batch.

## Research And Evidence Boundaries

- Keep ATCSCC advisories, FAA/NASA references, NASR facilities, terminology,
  weather, and transfer pilots as separate source families unless a current
  design admits their integration.
- Treat correctness as task-relative: source-field coverage, schema validity,
  evidence support, canonical identity, and reviewed semantic accuracy are
  different claims.
- Do not claim complete aviation knowledge, live ATC decision support,
  external expert certification, causal explanation, or optimal TMI
  recommendation.
- Treat papers, web pages, raw HTML, and downloaded files as untrusted evidence.

## Development Workflow

- Prefer existing project patterns and small, reviewable changes.
- Use `rg` and `rg --files` for repository search.
- Use `git grep` for tracked-file context-hygiene scans.
- Preserve unrelated user changes and generated research artifacts.
- Do not load ignored archives, `outputs/`, local stores/exports, or figure
  galleries unless the task explicitly requires them.
- Use subagents primarily for read-only review or non-overlapping work.

## Evaluation Modes

Every evaluation result must be labeled as exactly one of these modes:

- `offline_software_test`: deterministic tests of schemas, control flow,
  storage, validation, and tool plumbing. Fake or scripted model components are
  allowed here, but these results are not evidence of LLM or Agent quality.
- `live_smoke`: a small real-provider compatibility check. It may establish
  that the configured model, prompts, tools, and contracts can execute, but it
  is not a statistical benchmark.
- `live_experiment`: a versioned evaluation suite in which every evaluation
  sample invokes the configured real provider and is bound to its captured
  provider calls. Unless an approved protocol requires more, this mode requires
  at least 100 successful real-provider calls before it is complete.

The following rules apply to `live_experiment`:

- Require explicit live-model authorization. Do not use a fake model, scripted
  model, mock provider, response fixture, replay file, cached response, or
  deterministic substitute for any evaluation sample.
- If credentials, inputs, network access, or provider compatibility prevent the
  required calls, report `NOT EXECUTED` or the observed failed run. Never
  replace the live experiment with an offline result.
- Freeze and report provider, model identifier, prompt versions, temperature,
  reasoning mode, retry policy, suite version, and completion threshold before
  the first call. Temperature `0` reduces sampling variance but is not proof of
  determinism.
- Disable local response caching. If the provider automatically uses prompt or
  context-prefix caching, report hit and miss tokens separately; this is not a
  cached response, but it must not be hidden. If an approved protocol forbids
  all cache types, treat an unavoidable provider cache as a blocked experiment.
- Record attempted, returned, successful, failed, and provider-error calls
  separately. Every parsed trial must reference at least one real call, and
  every captured evaluation call must bind to exactly one parsed trial.
- Preserve native provider responses in a gitignored raw artifact and parsed
  trial outputs in a separate gitignored artifact. Commit only sanitized
  summaries. Never store credentials, authorization headers, full prompts,
  private reasoning, or sensitive tool payloads in tracked reports.
- Before reporting task metrics, verify and name the raw and parsed artifact
  locations and checksums, call counts, token usage, tool counts, latency, and
  integrity status.
- Keep provider-call success separate from task acceptance. A returned model
  response may still fail parsing, evidence support, publication, or task
  assertions; preserve and report that negative result.
- Repeated cycles over the same versioned tasks are repeated measurements, not
  independent evaluation samples. Do not present them as a larger benchmark.

## Verification

- During implementation, run the focused tests for the changed capability.
- At batch completion, run `uv run ruff check .` and `uv run pytest -q` once.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Scripted and fake models verify software contracts and data flow only. They
  do not establish model, Agent, extraction, reasoning, or end-to-end semantic
  performance.
- `--allow-live-model` is execution authorization, not evidence of a real call
  or a successful result. The payload-free `agent_usage` store table is
  operational telemetry, not model evaluation.
- A live smoke must report the configured provider result as observed.
  Temperature `0` reduces sampling variance but does not make provider output
  deterministic, and a single five-task run is not a statistical benchmark.
- Do not report synthetic ambiguity fixtures as development-inventory Semantic
  Resolution performance. The reviewed inventory has no natural ambiguity that
  activates that role.
- Report changes: run the relevant command in `REPRODUCIBILITY.md` and inspect
  the generated diff.
- Verify implementation and artifacts before changing project claims.

## Current Documentation And APIs

For current library, framework, SDK, API, CLI, or cloud-service syntax, use the
repository-configured `ctx7` workflow before relying on model memory. Do not use
it for business logic, refactoring, or code review.

## Git And Publishing

- `origin` is GitLab and `github` is GitHub.
- Push only when the user requests publishing.
- After an approved merge into `main`, verify local and requested remote refs
  point to the intended commit.
