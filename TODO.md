# TODO

Last updated: 2026-07-31

This file contains only the active execution queue and immediate deferred
decisions. Historical backlogs are routed through `ARTIFACT_INDEX.md`.

## Active Decisions

- [ ] Run a separately approved v3 real-provider evaluation after the
  event-centered cutover. It must use the current Event Evidence Integration
  and Query Agent contracts; prior v1/v2 and compact-selection results remain
  historical compatibility evidence.
- [ ] Replace the GDP-biased five-task evaluation with a cross-family suite over
  GDP, GS, and ReRoute, including paraphrased, multi-tool,
  insufficient-evidence, and claim-boundary questions.
- [ ] Admit any next TMI family only after an explicit ATMONTO mapping and
  reviewed source/evidence boundary. Do not promote informational notices only
  to increase coverage.

Do not reintroduce fixed question registries or bypass the Query Agent for
apparently simple natural-language questions. Deterministic retrieval stays
inside bounded tools; natural-language interpretation and tool routing remain
model-mediated.

## Explicitly Deferred

- A formal representation of internal decision inputs, alternatives,
  constraints, rationale, trade-offs, and attributable outcomes.
- Weather-cause claims, operational effectiveness, and decision optimality.
- ASPM demand, AAR, capacity, EDCT, runway configuration, and flight-level
  impact.
- TCF, CWA, SIGMET, NOTAM, ADS-B, and single-flight trajectories.
- Advisory lifecycle or TMI-episode grouping.
- National Playbook PDF grounding.
- F1/F3S/S4/S1S flight and sector query coverage.
- Operational-situation and outcome-aware similarity, learned reranking, and
  TMI recommendation.
- General-purpose planner, long-term Agent memory, and unrestricted aviation
  chat.
- New Agent roles without an observed need.
- Multi-model or statistically powered evaluation beyond an approved protocol.
- Frozen-cohort Semantic Resolution performance claims until a natural
  ambiguous task exists.
- Merging the paused visualization branch into the system mainline.
- Production hardening and public deployment.
- Adversarial path, symlink, concurrency, and cross-run tampering defenses
  unless a deployment or security task activates them.
- Reopening Gold, Critic, Self-Refine, or paired-comparison experiments as the
  default path.

## Maintenance Rules

- Keep this file short and current.
- Use descriptive capability names rather than internal batch labels.
- Do not store changing test counts as durable project claims.
- Keep generated corpora, provider artifacts, and credentials out of Git.
- Preserve historical material through the artifact index and Git history.
- Apply the research-prototype effort boundary in `AGENTS.md`.
