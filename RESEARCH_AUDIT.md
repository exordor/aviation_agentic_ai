# Project Audit And Context Router

Audit date: 2026-07-30
Canonical integration branch: `main`

This is the default entry point for a new project task. It replaces the former
thesis-first navigation model.

## Current Project Snapshot

Aviation Agentic AI is a runnable, ontology-grounded aviation
knowledge-integration and HybridRAG system. Retrospective FAA ATCSCC TMI
records are its current end-to-end vertical slice. It deterministically
classifies active GDP, GS, and ReRoute families through one ATMONTO-aligned
application profile, processes eligible records through the bounded-Agent
workflow, and normalizes validated evidence into canonical corpus v2. Queries
and selected-case exports read that corpus. RDF/Turtle and Neo4j are offline,
rebuildable KG exports; Chroma is a rebuildable metadata-conditioned case
index.

```text
718 advisory rows
  -> cohort/all selection or explicit source-ID subset
  -> ATMONTO-aligned TMI classification
  -> deterministic preflight
  -> insufficient without model for 18 boundary + 1 deferred + 3 incomplete records
  -> sequential workflow for the remaining 46 active-family eligible records
  -> event-patch admissibility check
  -> DecisionCase assembly
  -> final decision/profile/membership Formal Publication Kernel
  -> canonical corpus v2
  -> read-only Corpus, case-graph, and metadata-conditioned vector tools
  -> bounded LLM action-observation query loop
  -> per-statement evidence support
  -> answer / insufficient / blocked
```

The Coordinator and Formal Publication Kernel are deterministic components,
not Agents. LLM output cannot bypass the publication gate. The persisted public
path is corpus-first: `build-corpus`, `index-cases`, `ask`, `neo4j-export`, and
`export-case`. There is no persistent single-case ingest interface,
run-directory query, or corpus v1 compatibility layer.

## Verified Main-Branch Capabilities

- One registry rooted at `atm:TrafficManagementInitiative` drives active GDP,
  GS, and ReRoute detection, preflight, formal property mapping, and retrieval
  labels. The application profile uses exact ATMONTO terms.
- ATMGRAPH is the ABox construction and cross-source-query reference. It is not
  imported as another dataset, and the project does not claim to reproduce its
  original store exactly.
- `agent-system build-corpus` builds a selected corpus directly from configured
  advisory sources. `--source-id` provides a bounded single-case debug path;
  `--resume` retries blocked records only.
- A payload-free `agent_usage/` sidecar reports selective Agent activation,
  deterministic bypass, outcomes, calls, tokens, and recorded latency. It is
  bound to, but excluded from, canonical corpus identity. This sidecar is
  operational telemetry, not an evaluation of model correctness.
- Corpus v2 content-addresses source objects and stores cases, semantic facts,
  membership, evidence links, profile gaps, Weather associations, BTS
  observations, and stable conceptual-case/reconstruction identities.
- Each accepted case has formal DecisionCase reconstruction membership.
  Bounded graph reads expose admitted case edges by entity, direction,
  predicate, and limit without arbitrary SPARQL, Cypher, or graph writes.
- `agent-system index-cases` builds an ignored, corpus-bound Chroma sidecar with
  one explicit vector per accepted decision record.
- Every valid `agent-system ask` request activates the bounded Query Agent.
  Natural-language interpretation and routing are model-mediated; deterministic
  read-only tools provide exact cases/facts, Weather context, BTS observations,
  case-graph edges, and historical vector recall.
- The Query Agent must retrieve before answering, stays inside the immutable CLI
  scope, and may use at most four provider turns and six tool calls.
- Every answer statement is checked against its cited case, fact, profile-gap,
  context, observation, graph-path, and source identities. Missing support is
  `insufficient`; invalid contracts or dependencies are `blocked`.
- The historical-similarity tool applies exact metadata filters before cosine
  recall, excludes the anchor, and supports archive and prior scopes. Tool
  execution is deterministic, but its selection occurs inside the LLM loop.
- `agent-system export-case` writes a selected bounded, non-replayable case.
- `agent-system neo4j-export` loads the full corpus projection with
  parameterized `MERGE` when Neo4j is available.
- RDF/Turtle and Neo4j are offline rebuildable KG exports; Chroma is a
  rebuildable metadata-conditioned retrieval index. None replaces corpus v2
  as the authority or runtime read contract.
- Missing or unsupported fields return explicit `insufficient`; provider or
  workflow failures return `blocked`; profile gaps never become formal KG facts.
- GS 123, GDP 138, and GDP 020 are regression fixtures rather than the system
  scope. They respectively preserve a profile gap, formal `weather`, and an
  honest missing declared-reason result.
- Weather associations remain non-causal. BTS observations are not FAA demand,
  AAR, capacity, EDCT, or proof that a TMI caused an outcome.
- `alignment_audit.json` and `tmi_coverage.json` are compact, rebuildable corpus
  summaries. They are not audit ledgers or additional publication gates.

## Historical Pre-Refactor Evaluations

These results were recorded before the always-on Hybrid Query Agent cutover.
They remain valid artifacts for the retired registered-analysis runtime, but
they are not evidence of current natural-language routing, tool selection, or
answer quality. The frozen task selection is GDP-biased and cannot support
cross-family performance claims.

Evaluation mode: `live_smoke`. The frozen one-shot DeepSeek run completed with
model acceptance `0/5`: three Assembly output-token-cap failures, one malformed
Assembly contract, and one retired-analysis answer/evidence-support contract
failure.

Evaluation mode: `live_experiment`. The corrected repeated real-provider
experiment ran the same pre-refactor five tasks for 12 full cycles. DeepSeek
`deepseek-v4-pro` returned successfully for all 108 provider calls with zero
recorded provider failures, 431,018 input tokens, and 89,148 output tokens.
Task acceptance was still `0/60`: all 48 Assembly trials exceeded the frozen
output-token cap and all 12 retired-analysis trials failed the typed
answer/support contract. DeepSeek reported 396,928 prompt-cache-hit tokens and
34,090 prompt-cache-miss tokens from its automatic input-prefix context cache.
This was not cached-response replay; every call returned a unique provider
response ID. The earlier local
`live-agent-experiment-v1-invalid-observer-phase` and
`live-agent-experiment-v1-normalized-response-only` diagnostics are excluded:
the former changed Assembly outcomes and missed provider turns, while the
latter did not retain the full native response payload required by the final
contract.

## Evaluation Boundary

Evaluation mode: `offline_software_test`. Scripted and fake models verify
software contracts, control flow, and data handling. They are not evidence of
real-model extraction, tool selection, reasoning, or end-to-end Agent quality.
Likewise, `--allow-live-model` is only authorization to construct a configured
provider, and `agent_usage/` records only execution telemetry.

The frozen pre-refactor `live_smoke` used DeepSeek `deepseek-v4-pro`,
temperature `0.0`, thinking disabled, no automatic retry, one repetition, four
Assembly tasks, and one registered-analysis task. Temperature `0` reduces
sampling variance but does not guarantee identical provider outputs. A single
five-task smoke is a provider compatibility diagnostic for the retired
runtime, not a statistical benchmark.

The Semantic Resolution Agent is
`not_evaluated_no_natural_ambiguity`: the current frozen cohort supplies no
natural multi-candidate activation. Synthetic ambiguity fixtures remain valid
offline software tests, but must not be reported as cohort performance.
The failed frozen result remains unchanged as historical evidence; the later
compact-selection compatibility fix is reported separately below.

The pre-refactor `live_experiment` is likewise a compatibility and reliability
diagnostic. Its 60 trial rows are 12 repetitions of five tasks, not 60
independent evaluation samples. The 108 successful calls establish provider
return and trace capture under that frozen configuration; they do not establish
current Query Agent task success.

## Current Hybrid Query Agent Live Evaluation

The v2 experiment evaluated the current Hybrid Query Agent without changing
the four frozen Assembly tasks. It ran 12 repetitions of five tasks with
DeepSeek `deepseek-v4-pro`, temperature `0.0`, thinking disabled, no automatic
retry, and no local response cache.

The runner recorded 120 attempted and 120 successful real-provider calls,
zero failed calls, 383,201 input tokens, and 69,986 output tokens. Raw-response
and parsed-output file hashes independently matched the experiment manifest;
there were no call-binding, duplicate-trial, missing-trial, configuration, or
local-cache integrity failures.

Task acceptance was `12/60`, not `120/120`. The GDP `138` natural-language
HybridRAG query passed in all 12 cycles. The four Assembly tasks failed all 48
measurements: 28 exceeded the frozen output-token cap and 20 returned malformed
typed contracts. These results establish query-loop provider compatibility for
one repeated GDP task and expose a separate Assembly compatibility gap. They
are GDP-biased historical compatibility evidence, not a broad query benchmark,
representative cross-family evaluation, or 60 independent samples.

## Compact Assembly Output-Contract Acceptance

The compatibility gap was first addressed by changing the output contract
rather than relying on a larger response. Instead of regenerating a complete
GraphPatch, the Agent reads one sealed candidate bundle and emits a compact
accept-or-abstain selection. The full proposal is restored deterministically
and still passes through the existing preflight and Formal Publication Kernel.
The active system ceiling was subsequently raised to 10,000 output tokens for
the Query Agent and Decision Case Assembly Agent; Semantic Resolution retains
its compact 256-token decision cap.

Before the ceiling change, the same five frozen tasks ran for 12 cycles with real DeepSeek
`deepseek-v4-pro`, temperature `0.0`, thinking disabled, no automatic retries,
and no local response cache. The runner recorded 120 attempted and 120
successful calls, zero failed calls, 261,238 input tokens, and 30,561 output
tokens. All 60 task measurements and 432 assertions passed. There were zero
invalid tool calls, call-binding mismatches, missing or duplicate trial
executions, configuration mismatches, or integrity failures.

The ignored raw and parsed artifacts are:

```text
data/corpus/agent_system/live-agent-output-contract-v3-experiment/raw_responses_v2.jsonl
data/corpus/agent_system/live-agent-output-contract-v3-experiment/parsed_outputs_v2.jsonl
data/corpus/agent_system/live-agent-output-contract-v3-experiment/experiment_manifest_v2.json
```

Their independently verified SHA-256 values are
`491ad8dc2966e863b0e65571ba143f57302a840de98e13eb091a15fb5bc6994c`
and
`ac827ab06e2a19aeca9206e9f32241aa1174b9b4c32310b7402ede00bf6f9edf`
for raw and parsed JSONL respectively. This is a repeated, GDP-biased
compatibility result on five fixed tasks, not 60 independent samples,
representative cross-family evaluation, or a broad Agent benchmark.

A fresh one-repetition run using the subsequent 10,000-token configuration
completed 10/10 real DeepSeek calls and passed all five frozen tasks, with zero
failed calls, 21,780 input tokens, and 2,705 output tokens. This verifies
provider compatibility with the active ceiling; it is not a statistical
benchmark.

## Current Intake And Publication Rules

The frozen cohort starts with 718 discovered advisories. It selects 68 records:
46 are eligible under the active GDP/GS/ReRoute profiles, 3 have incomplete
core fields, 18 are boundary notices, and 1 is a deferred ReRoute
cancellation. Each selected advisory receives one `CorpusBuildResult`.
Preflight returns the 22 boundary/deferred/incomplete records as `insufficient`
with zero model calls. A final `decision-case-corpus-v2` manifest is published
only when no entry is `blocked`; `--resume` retries only blocked entries.

Corpus facts use semantic identity independent of provenance. Source content is
deduplicated globally by SHA-256, while `evidence_links.jsonl` preserves all
supporting source bindings. The manifest registers every table and projection
with count and checksum. Temporary staging packages are not the public backend
and are removed after successful normalization.

## Context Routing

| Need | Read |
| --- | --- |
| Durable system goal and boundaries | `GOALS.md` |
| Installation and current commands | `README.md` |
| Active execution queue | `TODO.md` |
| Normative Agent-system design | `docs/multi_agent_kg_system_design.md` |
| Decision-record semantics and cases | `docs/atcscc_decision_record_explorer_design.md`, `docs/atcscc_decision_record_explorer_cases.md` |
| Artifact ownership and context hygiene | `ARTIFACT_INDEX.md` |
| Reproduction commands | `REPRODUCIBILITY.md` |
| Why a structural decision was made | `DECISION_LOG.md` |
| Optional historical experiments | `RESEARCH_QUESTIONS.md`, `HYPOTHESES.md`, `EXPERIMENTS.md`, `RESULTS.md` |

Do not preload optional experiments, stage reports, ignored corpus outputs, or
archives. They do not define the current system.

## Current Boundaries

The project does not provide general aviation QA, live ATC support,
weather-based causal explanation, operational-situation or outcome-aware
similarity, TMI recommendation, a complete aviation ontology, or external
expert certification. The tracked six-query relevance smoke set is not expert
Gold or decision-quality evidence and predates LLM-routed similarity. The v1
five-task live-Agent runs predate the current Query Agent. The current v2
five-task runs are repeated compatibility measurements, not a broad query
benchmark or evidence of reliable performance across an operational task
distribution.

Comparison experiments, Gold adjudication, broader ATMONTO family coverage,
Weather expansion, causal explanation, and recommendation require an explicit
approved task. Production security against hostile local artifact tampering is
also deferred unless explicitly activated.

## Verification Defaults

- Documentation-only changes: `git diff --check` and `uv run ruff check .`.
- Code changes: focused tests during development, then one final
  `uv run ruff check .` and `uv run pytest -q`.
- Storage-batch verification: run the commands in `REPRODUCIBILITY.md`, inspect
  corpus output and manifest, and keep real output ignored and uncommitted.
- Result claims require inspection of the implementation and named artifacts,
  not a historical test count.
