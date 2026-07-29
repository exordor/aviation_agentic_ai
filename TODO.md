# TODO

Last updated: 2026-07-30

This file contains only the active execution queue and immediate deferred
decisions. Historical experiment backlogs are discoverable through
`ARTIFACT_INDEX.md` and Git history.

## Active Decisions

- [ ] Decide whether to merge the reviewed read-only visualization from
  `codex/kg-visualization-research` into `main`.
- [ ] If a model-compatibility task is approved, version prompt or output-token
  changes separately from the frozen `live_smoke` and `live_experiment`
  results.
- [ ] Otherwise, choose one bounded system increment with an explicit source
  and acceptance boundary, such as ASPM validation, regional Weather context,
  decision-episode grouping, or operational-situation similarity.

Do not expand Decision Case Analysis beyond the exact registered families
without a new approved task and evidence boundary.

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
- Prompt or token-cap tuning for the recorded `live_smoke` and
  `live_experiment` failures.
- Additional repeated-run, multi-model, or statistically powered live-Agent
  benchmarks.
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
