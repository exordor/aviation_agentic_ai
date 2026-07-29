# TODO

Last updated: 2026-07-29

This file contains only the active execution queue and immediate deferred
decisions. Historical experiment backlogs are discoverable through
`ARTIFACT_INDEX.md` and Git history.

## Current Stage - Corpus-First Retrieval

Batch C.1 and Batch D are complete on `main`. The system now reconstructs the
three canonical decision cases with Weather and BTS context, assembles them
through bounded roles, and answers exact registered analysis questions.

Storage Batch S2 is complete. The public persisted path is `build-corpus`,
`ask`, `neo4j-export`, and `export-case`; no persistent single-case ingest,
run-directory query, `ask-corpus`, `--runs-root`, or corpus v1 migration path
remains. Corpus v2 stores content-addressed sources, cases, semantic facts,
fact membership, evidence links, profile gaps, non-causal Weather associations,
BTS observations, and rebuildable full-corpus exports.

The frozen cohort design is 718 discovered, 68 selected, 42 Agent-eligible, 23
unsupported-TMI, and 3 incomplete-core-field records. The 26 preflight
failures are deterministic `insufficient` with zero model calls. `--resume`
retries only `blocked` results and final publication waits for blocked count
zero.

Storage Batch S3 is complete. `index-cases` builds a persistent local Chroma
sidecar with one compact decision-record vector per accepted case. Exact
event-type, facility, and declared-reason filters are applied before vector
recall; archive and prior scopes exclude the reference case. Historical
retrieval remains deterministic and uses zero chat-model calls.

The DecisionCase semantic core is complete. Every accepted corpus case carries
stable conceptual-case and reconstruction identities, and the reconstruction
formally owns its admitted event, Weather, and BTS members. One exact
case-scoped evidence-path question traverses this graph with zero model calls.

Architecture Consistency and Selective Agent Evidence is complete. Every
admitted formal layer now passes one explicit final Formal Publication Kernel
before projection writes. A non-authoritative `agent_usage/` sidecar measures
selective Agent activation without changing corpus identity.

Batch F is complete as a live-evaluation harness with frozen diagnostic runs.
The one-shot DeepSeek smoke completed with `0/5` accepted tasks: three
Assembly trials reached the output-token cap, one Assembly trial returned a
malformed contract, and the Analysis trial failed its typed answer/support
contract. Prompt and token-cap changes are intentionally deferred to a
separate task.

The repeated real-provider experiment is complete: 12 full cycles produced
108/108 successful DeepSeek calls and `0/60` accepted tasks. The failures were
48 Assembly output-token-cap results and 12 Analysis answer/support-contract
results. Treat this as repeated compatibility evidence, not 60 independent
tasks.

## Recently Completed Work

- [x] Add an explicit live-model evaluation entry point that reuses the real
  corpus build, Formal Publication Kernel, and corpus query path.
- [x] Record a redacted one-shot five-task DeepSeek smoke report without fake
  fallback, provider substitution, prompt changes, or token-cap changes.
- [x] Separate software-contract tests, Agent usage telemetry, and live-model
  acceptance claims.
- [x] Mark Semantic Resolution as
  `not_evaluated_no_natural_ambiguity` rather than treating synthetic
  ambiguity fixtures as frozen-cohort performance.
- [x] Record at least 100 successful real-provider calls with separate raw and
  parsed artifacts, no fake/replay/cache fallback, and honest task-level
  acceptance.
- [x] Make the final multi-profile Formal Publication Kernel explicit and
  remove the malformed-BTS drop-and-retry publication fallback.
- [x] Record three payload-free Agent usage rows for each eligible workflow
  case and no rows for deterministic preflight insufficiencies.
- [x] Publish usage totals in a corpus-bound sidecar outside canonical corpus
  identity.
- [x] Replace the crowded system diagram with separate construction and
  retrieval architecture figures.
- [x] Add conceptual-case and reconstruction identities with formal
  `prov:specializationOf` and `prov:hadMember` relations under the
  DecisionCase core profile.
- [x] Answer the exact reconstructed-case Weather and active-window BTS
  evidence-path question through closed graph traversal with zero model calls.
- [x] Preserve the Ground Stop `123`, GDP `138`, and cancellation `020` reason
  states across multi-source reconstruction.
- [x] Publish source-qualified Weather and BTS observations without causal,
  FAA demand, AAR, capacity, EDCT, or individual-flight claims.
- [x] Keep the three canonical cases on deterministic zero-call Assembly.
- [x] Add bounded Decision Case Analysis for exact episode,
  operational-situation, and applicability questions.
- [x] Build a corpus-bound, rebuildable Chroma case index without changing
  corpus v2 identity or formal facts.
- [x] Retrieve published decision-record analogues through exact filtering
  followed by normalized cosine ranking.
- [x] Verify four reviewed analogue queries and two expected-insufficient
  queries on a small tracked smoke set.
- [x] Query the normalized corpus by exact case metadata and canonical event
  ID without constructing a provider.
- [x] Build selected advisories directly into corpus v2 with one result per
  selected source and blocked-only resume.
- [x] Move query, RDF, Neo4j, and selected-case export to the corpus tables.
- [x] Merge Batch C.1 and Batch D into `main`.

## Completed System Foundation

- [x] Implement deterministic advisory parsing and bounded facility and
  terminology authority services.
- [x] Add the shared Semantic Resolution Agent for genuine ambiguity.
- [x] Replace the predecessor construction path with the canonical compiler or bounded
  Decision Case Assembly Agent.
- [x] Enforce early event-patch validation and one final deterministic
  multi-profile Formal Publication Kernel.
- [x] Preserve fact-level evidence, provenance, profile gaps, and explicit
  failure states.
- [x] Materialize validated JSONL, RDF/Turtle, and Neo4j projections.
- [x] Load Neo4j through parameterized idempotent `MERGE`.
- [x] Add the bounded read-only Query Agent.
- [x] Support measure, facility, operational-period, declared-reason,
  provenance, and combined-record questions.
- [x] Correct cross-midnight parsing and declared-reason boundaries.
- [x] Verify the Ground Stop `123`, GDP `138`, and missing-reason `020` cases.

## Paused Visualization Track

The read-only query evidence explorer is implemented and reviewed on
`codex/kg-visualization-research`. It is intentionally paused.

- [x] Build a frozen query-local visualization bundle.
- [x] Build the four-panel read-only browser view.
- [x] Verify formal facts, provenance, profile gaps, missing states, keyboard
  interaction, and narrow layouts.
- [ ] Merge the visualization branch only when the user wants it in `main`.

## Next Decision

Do not expand analysis beyond the exact registered families without a new
approved task and evidence boundary. A follow-up may address the observed
prompt/output-token compatibility failures, but it must be separate from the
frozen Batch F result. Otherwise, the next approved task must choose one
bounded increment, such as ASPM validation, regional Weather context,
decision-episode grouping, or operational-situation similarity.

## Explicitly Deferred

- Weather-cause claims and decision optimality.
- ASPM demand, AAR, capacity, EDCT, runway configuration, and flight-level
  impact.
- TCF, CWA, SIGMET, NOTAM, ADS-B, and single-flight trajectories.
- Advisory lifecycle or decision-episode grouping.
- Operational-situation and outcome-aware similarity, learned reranking, and
  TMI recommendation.
- General-purpose planner and long-term Agent memory.
- General RAG and general aviation chat.
- New Agent roles without an observed need.
- Prompt or token-cap tuning for the recorded Batch F failures.
- Repeated-run, multi-model, or statistically powered live-Agent benchmarks.
- Frozen-cohort Semantic Resolution performance claims until a natural
  ambiguous case exists.
- Production hardening and public deployment.
- Adversarial local-object, path, symlink, concurrency, and cross-run tampering
  defenses unless a deployment or security task activates them.
- Reopening optional alignment, Gold, Critic, Self-Refine, or paired-comparison
  experiments as the default project path.

## Maintenance Rules

- Keep this file short and current.
- Use descriptive task names rather than internal letter or number codes.
- Do not store changing test counts as durable project claims.
- Keep generated corpus artifacts and credentials out of Git.
- Preserve historical material through the artifact index and Git history
  instead of leaving it in the active queue.
- Apply the research-prototype effort boundary in `AGENTS.md`; do not duplicate
  production-hardening policy here.
