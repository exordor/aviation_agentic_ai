# TODO

Last updated: 2026-07-27

This file contains only the active execution queue and immediate deferred
decisions. Historical experiment backlogs are discoverable through
`ARTIFACT_INDEX.md` and Git history.

## Current Stage - Decision Case Graph v1

Objective: reconstruct three auditable historical decision cases by connecting
validated ATCSCC records to time-bounded Weather context and BTS-reported public
operational observations without causal, prescriptive, or model-generated
expansion.

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

Success: all three cases expose validated Weather context and BTS-reported
observations with source provenance, exact reason-state preservation, and zero
additional provider calls.

## Completed System Foundation

- [x] Implement the fixed multi-Agent construction workflow.
- [x] Add bounded facility and terminology authority resolution.
- [x] Add the tool-using Knowledge Graph Construction Agent.
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

## Next Decision After v1

Do not start another semantic expansion until the three-case v1 verification
and review are complete. The next approved task must choose only one bounded
increment, such as ASPM validation, regional Weather context, decision-episode
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
