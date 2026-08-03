# AGENTS.md

Repository-level instructions for coding agents. Keep this file operational;
detailed designs and historical protocols live under `docs/`.

## Project Posture

This is a **system and framework construction project**. Its research-facing
positioning is **ATMONTO-Grounded Agentic HybridRAG for Heterogeneous Aviation
Knowledge Integration**. Retrospective FAA ATCSCC TMI records are one
end-to-end regression vertical slice; they are not the architecture's
permanent subject boundary or its research sample definition.

The active pipeline is:

```text
composed runtime + source + dataset/temporal-scope configuration
  -> configured ATCSCC, FAA authority, Weather, BTS, NASA ATMONTO,
     aircraft-registry, and airspace source artifacts
  -> immutable source assets, source versions, and anchors
  -> selected ingestion domain: all | tmi | document | flight-airspace
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
  -> rebuildable source-record, TMI-event, and knowledge-entity Chroma collections
  -> every valid natural-language ask activates the bounded Query Agent
     -> LLM selects source, tmi, knowledge, and/or flight_airspace tool families
     -> selected subset of 21 read-only evidence tools
     -> per-statement evidence and claim-boundary validation
     -> answer, insufficient, or blocked

The explicit ontology-construction research path is:

```text
complete ATMONTO TBox -> task ontology slice -> bounded candidate-fact
generator -> deterministic validation -> Formal Publication Kernel
  -> incremental semantic-store fusion
```

Framework names must remain source-neutral: use `document` for the ingestion
domain, `knowledge` for the query family, and `knowledge_entity` for derived
indexes. FAA-specific parsing, prompt examples, normalization, and extension
terms belong in `faa_order_*` adapter modules and its application profile.
`PolicyRule` is an allowed FAA adapter concept; `policy` must not reappear as a
public CLI domain, runtime family, generic module, index, or experiment name.

The dataset-bound SQLite evidence store is the canonical persisted knowledge
and evidence layer. The generic publication spine admits ATMONTO-aligned TMI,
Flight/Airspace, reference, Weather, and reviewed association roots; the TMI
root is one demonstrator, not the permanent subject boundary. None invents a
decision-process object. SQLite FTS5 and Chroma are rebuildable indexes.
RDF/Turtle, JSONL KG, and Neo4j are optional all-root offline exports.
The retired `Corpus v2` batch snapshot is historical only. Files under
`data/evaluation_runs/agent_system/` are evaluation evidence, not persisted
knowledge and not a runtime query backend.
The versioned application profile aligns the active TMI schema with exact
ATMONTO terms and constrains publication; it is not a separate Agent and is not
claimed to be a complete aviation ontology. The opt-in candidate generator is
write-free and cannot widen the profile. ATMGRAPH is the reference for
constructing and querying the populated ABox, not an imported dataset or an
exact system replica.

The normative implementation design is
`docs/multi_agent_kg_system_design.md`. Reader-facing documents use full Agent
names, not internal alphanumeric labels.

Document authority is intentionally narrow: `RESEARCH_AUDIT.md` owns current
status and evaluation observations; `GOALS.md` owns durable goals and
non-goals; `README.md` owns the public overview; and `REPRODUCIBILITY.md` owns
commands and source bindings. `docs/repository_artifact_policy.md` defines the
historical-material boundary.
Other documents must explain or illustrate these authorities, not restate
changing facts.

Historical plans, PHAK-era reports, and retired compatibility contracts are
not part of the default checkout. Their external-archive policy is documented
in `docs/repository_artifact_policy.md`; do not restore them or add new
runtime dependencies on them unless a legacy experiment is explicitly being
reactivated.

The old extraction/evaluation packages, root command wrappers, and their
dedicated tests/scripts have been moved to the dated external archive. They
are not importable runtime modules. Keep the six checksum-pinned NASA ATMONTO
OWL files and the curated application-profile JSON in the checkout: they are
active semantic authority inputs, not historical experiment leftovers. Other
external ontology copies and old evaluation inputs belong in the archive and
must not be added to the active runtime.

## Current Status

`RESEARCH_AUDIT.md` is the sole authority for current implementation status,
dataset counts, and evaluation observations. This section keeps only the
runtime rules that an executor needs; do not copy changing metrics or sample
inventories into this file.

- The active implementation contains incremental ingestion, a dataset-bound
  SQLite evidence store, the Formal Publication Kernel, deterministic Event
  Evidence Integration, store-backed exact and graph reads, SQLite FTS5,
  rebuildable Chroma indexes, optional exports, and the bounded HybridRAG Query
  Agent.
- `configs/aviation_knowledge_v1.yaml` composes separate runtime, source, and
  dataset/temporal-scope files. Do not collapse those concerns back into one
  experimental configuration.
- The default model-backed roles are the Query Agent invoked for every valid
  natural-language question and the selectively activated Semantic Resolution
  Agent. The Ontology Candidate Fact Generator is opt-in construction only;
  it proposes facts for the same deterministic publication kernel and is not
  part of default `ingest`.
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
  one or more of `source`, `tmi`, `knowledge`, and `flight_airspace`; the evidence
  loop then sees only that subset of 21 registered read-only tools. There is no fixed
  question registry or deterministic answer fallback.
- The Query Agent budget is 7 retrieval turns, at most 6 evidence-tool calls in
  one turn, and at most 16 evidence-tool calls in total. Knowledge retrieval uses
  compact graph observations so multi-paragraph questions retain room for
  exact source-anchor reads. A retrieval boundary with accumulated evidence
  triggers one tool-free Evidence Packet answer turn.
- Search tools return candidates. A source-record statement requires an exact
  `read_source` result with immutable source-version and anchor support.
- The ingestion-first storage cutover is complete. The public commands are
  `ingest`, `reindex`, `ask`, `build-kg`, `neo4j-export`, and `export-event`.
  There is no
  run-directory query path, mandatory batch snapshot, old reader, or command
  compatibility path.
- `ingest --domain all|tmi|document|flight-airspace|web` registers immutable source
  versions, skips terminal
  `ok/insufficient` versions, retries blocked versions, and commits each
  accepted knowledge-root publication independently. A targeted advisory
  backfill registers only the selected advisory records plus shared
  authority/context evidence.
  Queryability does not depend on finishing a batch manifest.
- Research scope is selected by the dataset and temporal-scope configuration,
  not by the size of a source inventory. The recommended high-coverage public
  prototype is the one-day NASA ATMONTO sample in
  `configs/atmonto_public_sample_v1.yaml`; the 2014 Flight, Weather, TMI, and
  infrastructure records remain in their own temporal domain.
- The 718-row 2026 ATCSCC inventory is retained as an optional historical TMI
  source and regression asset. `ingest --domain tmi` can process that inventory
  when explicitly selected, but it is not the current system scale, research
  cohort, or ontology-coverage target.
- The legacy cross-source experiment deterministically selected 68 records
  whose full text mentioned JFK, EWR, LGA, KJFK, KEWR, or KLGA. Its 46/3/18/1
  split is automated registry/preflight output, not manual review, a
  representative sample, or a current runtime cohort.
- SQLite FTS5 indexes exact source chunks. Chroma has separately rebuildable
  source-record, TMI-event, and knowledge-entity collections; a collection is usable only when
  its indexed knowledge revision matches the store.
- RDF/Turtle, JSONL KG, and Neo4j are optional all-root current-store exports
  and are never Query Agent prerequisites.
- The system output ceiling is 10,000 tokens for the Query Agent; the compact
  Semantic Resolution decision remains capped at 256 tokens. Event Evidence
  Integration is deterministic and makes no provider call.
- Historical provider runs, walkthroughs, and compatibility suites are routed
  through `docs/repository_artifact_policy.md`; they are not runtime status or model-quality
  claims.
- The five familiar records are development/regression fixtures only. No
  frozen post-cutover evaluation set is part of the default system.
- Broader ATMONTO coverage, weather expansion, causal explanation,
  recommendation, and production deployment remain deferred unless explicitly
  reactivated.

## Default Context

For a new task:

1. Read `RESEARCH_AUDIT.md`.
2. Read `GOALS.md`.
3. Load `README.md` or a design document only when the task needs that layer.

Do not preload the external archive's former research-question, hypothesis,
experiment, result, stage-report, ignored-store/export, or PHAK/web-demo
material. Those artifacts describe optional evaluation or historical work, not
the default system scope.

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
