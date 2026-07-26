# TODO

Last updated: 2026-07-26

This file contains only the active execution queue and immediate deferred
decisions. Historical experiment backlogs are discoverable through
`ARTIFACT_INDEX.md` and Git history.

## Current Stage - Main Metadata Cleanup

Objective: make every default project entry point describe the same active
multi-Agent system and remove obsolete thesis, Gold, cross-source experiment,
and web-demo wording from current context.

- [x] Confirm the primary worktree is on `main`.
- [x] Audit root metadata against the implemented CLI and Agent-system code.
- [x] Align `AGENTS.md`, `CLAUDE.md`, `RESEARCH_AUDIT.md`, `README.md`,
  `GOALS.md`, `TODO.md`, `ARTIFACT_INDEX.md`, `REPRODUCIBILITY.md`, and package
  metadata.
- [x] Mark formal experiment documents as optional historical evaluation
  tracks rather than current system definitions.
- [x] Update Decision Record Explorer documents to distinguish completed query
  support from the paused visualization branch.
- [x] Run documentation and repository verification.
- [ ] Review and commit the metadata batch when approved.

Success: a new session reaches the same project goal, current capabilities,
scope boundaries, and active queue without loading historical experiments.

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

## Next Mainline Decision

After the metadata batch, define one new user task before implementation.

Candidate directions:

- group related initial, revision, extension, and cancellation advisories into
  a source-bounded decision episode;
- add one approved situation-evidence source to a decision record;
- improve Query Agent interaction without adding new data semantics.

Selection criteria:

- directly advances the system's user value;
- can be demonstrated end to end with existing or explicitly admitted data;
- does not require unsupported causal or prescriptive claims;
- is smaller than a general cross-source or full-corpus expansion.

No candidate is active until the user approves its contract.

## Explicitly Deferred

- Weather-cause claims and decision optimality.
- ASPM outcomes and flight-level impact.
- Historical-case ranking and TMI recommendation.
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
