# AGENTS.md

Repository-level instructions for coding agents. Keep this file operational;
detailed designs and historical protocols live under `docs/`.

## Project Posture

This is a **system and framework construction project**. The primary deliverable
is a runnable, ontology-grounded aviation knowledge-integration and HybridRAG
system. Retrospective FAA ATCSCC TMI records are the current end-to-end
vertical slice; they are not the architecture's permanent subject boundary.

The active pipeline is:

```text
718 ATCSCC advisories + bounded FAA authority records
  -> cohort/all selection or explicit source-ID subset
  -> ATMONTO-aligned TMI classification (GDP, GS, and ReRoute active)
  -> deterministic preflight (boundary/deferred/incomplete -> zero-call insufficient)
  -> deterministic AdvisoryParser
  -> facility and terminology authority services
     -> shared Semantic Resolution Agent only for genuine ambiguity
  -> deterministic Weather and BTS context preparation and validation
  -> sealed Decision Case Assembly task
  -> zero-call deterministic compiler when all required slots are resolved
     or bounded Decision Case Assembly Agent for a genuine unresolved
     evidence/schema choice
  -> task-bound validation
  -> source-independent DecisionCase core and formal reconstruction membership
  -> write-free multi-profile Formal Publication Kernel
  -> canonical corpus v2 normalization
  -> rebuildable JSONL + RDF + Neo4j materialization
  -> rebuildable case-level Chroma index for filtered decision-record retrieval
  -> every valid natural-language ask activates the bounded Query Agent
     -> model-selected read-only Corpus, Weather, BTS, graph, and similarity tools
     -> per-statement evidence and claim-boundary validation
     -> answer, insufficient, or blocked
```

Corpus v2 is the canonical persisted knowledge and evidence layer. Formal graph
views, RDF/Turtle, and Neo4j are derived runtime views or rebuildable outputs.
The versioned application profile aligns the active TMI schema with exact
ATMONTO terms and constrains publication; it is not a separate Agent and is not
claimed to be a complete aviation ontology. ATMGRAPH is the reference for
constructing and querying the populated ABox, not an imported dataset or an
exact system replica.

The normative implementation design is
`docs/multi_agent_kg_system_design.md`. Reader-facing documents use full Agent
names, not internal alphanumeric labels.

## Current Status

- The active implementation contains the corpus-first builder, validation,
  corpus v2 materialization, full-corpus Neo4j projection, DecisionCase
  semantic core, Decision Case Assembly, and the bounded HybridRAG Query Agent.
- The common semantic root is `atm:TrafficManagementInitiative`; the active
  application-profile families are GDP, GS, and ReRoute. Family detection,
  preflight, formal property mapping, and retrieval labels share one registry.
- The formal case graph exposes general, case-scoped formal edges to a read-only
  query tool. It is no longer limited to one registered evidence-path shape.
- The three Decision Record Explorer cases are regression fixtures, not the
  system scope. They preserve their profile-gap, formal weather, and honest
  missing-reason states. Public answers are nevertheless model-routed and
  evidence-bound, not deterministic sentence matches.
- Complete active-profile records use the zero-call deterministic compiler
  when all required slots are resolved; source identifiers never choose that
  path. The Formal Publication Kernel remains the sole final publication
  authority.
- Every valid public `ask` invokes the Query Agent. The model may select exact
  corpus reads, Weather context, BTS observations, case-graph edges, or
  metadata-conditioned Chroma retrieval over multiple bounded turns. There is
  no fixed question registry or deterministic answer fallback.
- The corpus-first storage cutover is complete. The rebuildable `index-cases`
  sidecar supports the deterministic filtered-similarity route. The public
  commands are `build-corpus`, `index-cases`, `ask`, `neo4j-export`, and
  `export-case`.
  There is no persistent single-case `ingest`, `ask-corpus`, `--runs-root`,
  `--run-dir`, or corpus-v1 compatibility path. Use `build-corpus --source-id`
  for a bounded debug build.
- The frozen cohort is 718 discovered and 68 selected: 46 active-family
  eligible records, 3 incomplete records, 18 boundary notices, and 1 deferred
  ReRoute cancellation. The 22 preflight insufficiencies use zero model calls.
  A corpus manifest is published only when blocked is zero; `--resume` retries
  only blocked entries.
- Successful corpus builds include compact, rebuildable
  `alignment_audit.json` and `tmi_coverage.json` summaries. They describe the
  corpus/profile alignment and family coverage; they are not run ledgers or
  additional publication authorities.
- The system output ceiling is 10,000 tokens. The Query Agent and Decision Case
  Assembly Agent use that ceiling; the compact Semantic Resolution decision
  remains capped at 256 tokens.
- A current-ceiling DeepSeek smoke passed all five frozen tasks with 10/10 real
  provider calls and zero failures. The suite is GDP-biased historical
  compatibility evidence, not representative cross-family evaluation.
- `live_experiment`: the current compact-selection contract completed 12 full
  five-task cycles with DeepSeek `deepseek-v4-pro`: 120/120 real calls and all
  60 task measurements succeeded. Provider-call success is not by itself task
  acceptance; these are repeated measurements of five fixed, GDP-biased tasks,
  not 60 independent samples, cross-family evidence, or a model-quality
  benchmark.
- The pre-fix v2 experiment remains historical evidence: its Query task passed,
  while the former full-graph-patch Assembly contract failed. Do not relabel
  those failures as current compact-selection results.
- The v1 smoke and repeated experiment remain frozen historical evidence for
  the retired registered-analysis runtime. Do not relabel them as current Query
  Agent results.
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
`RESULTS.md`, stage-report directories, ignored corpus outputs, or archived
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
- Do not load ignored archives, `outputs/`, local corpus outputs, or figure
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
- Repeated cycles over the same frozen tasks are repeated measurements, not
  independent evaluation samples. Do not present them as a larger benchmark.

## Verification

- During implementation, run the focused tests for the changed capability.
- At batch completion, run `uv run ruff check .` and `uv run pytest -q` once.
- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Scripted and fake models verify software contracts and data flow only. They
  do not establish model, Agent, extraction, reasoning, or end-to-end semantic
  performance.
- `--allow-live-model` is execution authorization, not evidence of a real call
  or a successful result. The `agent_usage/` sidecar is operational telemetry,
  not model evaluation.
- A live smoke must report the configured provider result as observed.
  Temperature `0` reduces sampling variance but does not make provider output
  deterministic, and a single five-task run is not a statistical benchmark.
- Do not report synthetic ambiguity fixtures as frozen-cohort Semantic
  Resolution performance. The current cohort has no natural ambiguity that
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
