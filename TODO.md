# TODO

Last updated: 2026-07-27

This file contains only the active execution queue and immediate deferred
decisions. Historical experiment backlogs are discoverable through
`ARTIFACT_INDEX.md` and Git history.

## Current Stage - Batch C.1 Architecture Cutover

Objective: reconstruct three auditable historical decision cases by preparing
validated Weather/BTS context, sealing one task-bounded Assembly input, and
publishing only proposals accepted by strict preflight and the Formal Graph
Kernel.

- [x] Add a canonical multi-source snapshot registry and per-source checksum
  validation.
- [x] Add deterministic TAF/METAR selection and formal Weather report facts.
- [x] Keep event-to-Weather associations audit-only and non-causal.
- [x] Add deterministic BTS normalization and baseline/active/recovery
  aggregation.
- [x] Add a source-qualified public-observation profile with explicit
  properties, units, datatypes, reporting scope, and forbidden FAA mappings.
- [x] Materialize validated BTS-reported observations in JSONL, RDF, and Neo4j.
- [x] Bind every observation to its selected rows, aggregation procedure,
  source snapshot, profile checksum, fact trace, and reconstruction trace.
- [x] Integrate both adapters after core event/facility validation without
  adding an Agent role or model call.
- [x] Add bounded deterministic context and outcome query tools.
- [x] Preserve all three reason states: Ground Stop 123 profile gap, GDP 138
  formal `weather`, and cancellation 020 missing.
- [x] Add fail-closed source, checksum, time, identity, and layer-disjointness
  checks.
- [x] Complete documentation review and the full repository verification gate.
- [x] Keep the reviewed branch unpushed and unmerged for user review.
- [x] Move deterministic Weather/BTS preparation before Decision Case
  Assembly.
- [x] Seal task-owned formal facts, profile gaps, evidence, resolution results,
  context associations, public observations, and source bindings.
- [x] Keep Ground Stop `123`, GDP `138`, and cancellation `020` on the
  deterministic zero-call Assembly path.
- [x] Add a bounded Decision Case Assembly Agent only for genuine
  non-canonical evidence/schema choice.
- [x] Enforce exact task-signature preflight, advisory-only declared reasons,
  explicit causal denial, and one value-only repair turn.
- [x] Keep the Formal Graph Kernel as the sole final publication authority.
- [x] Keep Decision Case Analysis inactive.
- [x] Complete the breaking cutover to deterministic parsing and authority
  services, conditional Semantic Resolution and Decision Case Assembly Agents,
  the Formal Graph Kernel, and current profile-owned run artifacts.
- [x] Require regeneration for old runs while retaining `ingest`,
  `neo4j-export`, and `ask` as current UX only.

Success: all three cases expose validated Weather context and BTS-reported
observations with source provenance, exact reason-state preservation, and zero
Decision Case Assembly provider calls.

## Completed System Foundation

- [x] Implement deterministic advisory parsing and bounded facility and
  terminology authority services.
- [x] Add the shared Semantic Resolution Agent for genuine ambiguity.
- [x] Replace the predecessor construction path with the canonical compiler or bounded
  Decision Case Assembly Agent.
- [x] Enforce the deterministic Formal Graph Kernel publication gate.
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

## Next Decision After Batch C.1

Do not activate Decision Case Analysis or another semantic expansion without a
new approved task. The next approved task
must choose only one bounded increment, such as a first read-only analysis
question family, ASPM validation, regional Weather context, decision-episode
grouping, or historical-case retrieval.

## Explicitly Deferred

- Weather-cause claims and decision optimality.
- ASPM demand, AAR, capacity, EDCT, runway configuration, and flight-level
  impact.
- TCF, CWA, SIGMET, NOTAM, ADS-B, and single-flight trajectories.
- Advisory lifecycle or decision-episode grouping.
- Historical-case ranking and TMI recommendation.
- General-purpose planner and long-term Agent memory.
- Full-corpus live-model runs.
- General RAG and general aviation chat.
- New Agent roles without an observed need.
- Production hardening and public deployment.
- Reopening optional alignment, Gold, Critic, Self-Refine, or paired-comparison
  experiments as the default project path.

## Maintenance Rules

- Keep this file short and current.
- Use descriptive task names rather than internal letter or number codes.
- Do not store changing test counts as durable project claims.
- Keep generated run artifacts and credentials out of Git.
- Preserve historical material through the artifact index and Git history
  instead of leaving it in the active queue.
