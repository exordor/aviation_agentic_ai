# TODO

Last updated: 2026-07-28

This file contains only the active execution queue and immediate deferred
decisions. Historical experiment backlogs are discoverable through
`ARTIFACT_INDEX.md` and Git history.

## Current Stage - Scalable Corpus Storage

Batch C.1 and Batch D are complete on `main`. The system now reconstructs the
three canonical decision cases with Weather and BTS context, assembles them
through bounded roles, and answers exact registered analysis questions.

The approved storage increment normalizes any number of validated runs into a
content-addressed source store, cross-case catalog, canonical fact table, and
case-to-fact membership table. It does not add an Agent, model call, vector
database, historical ranking, or recommendation.

## Recently Completed Mainline

- [x] Preserve the Ground Stop `123`, GDP `138`, and cancellation `020` reason
  states across multi-source reconstruction.
- [x] Publish source-qualified Weather and BTS observations without causal,
  FAA demand, AAR, capacity, EDCT, or individual-flight claims.
- [x] Keep the three canonical cases on deterministic zero-call Assembly.
- [x] Add bounded Decision Case Analysis for exact episode,
  operational-situation, and applicability questions.
- [x] Keep historical similarity deterministic `insufficient` until an
  approved comparison corpus exists.
- [x] Merge Batch C.1 and Batch D into `main`.

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

## Next Decision

Do not expand analysis beyond the exact registered families without a new
approved task and evidence boundary. The next approved task must choose only
one bounded increment, such as ASPM validation, regional Weather context,
decision-episode grouping, or a reviewed historical comparison corpus.

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
- Adversarial local-object, path, symlink, concurrency, and cross-run tampering
  defenses unless a deployment or security task activates them.
- Reopening optional alignment, Gold, Critic, Self-Refine, or paired-comparison
  experiments as the default project path.

## Maintenance Rules

- Keep this file short and current.
- Use descriptive task names rather than internal letter or number codes.
- Do not store changing test counts as durable project claims.
- Keep generated run artifacts and credentials out of Git.
- Preserve historical material through the artifact index and Git history
  instead of leaving it in the active queue.
- Apply the research-prototype effort boundary in `AGENTS.md`; do not duplicate
  production-hardening policy here.
