# TODO

Last updated: 2026-07-31

This file contains only the active execution queue and immediate deferred
decisions. Historical backlogs are routed through `ARTIFACT_INDEX.md`.

## Active Decisions

- [ ] Design a future frozen evaluation set independently from the five
  development/regression fixtures. Until the sampling frame, annotations,
  tasks, and acceptance rules are reviewed, record its status as
  `NOT CONSTRUCTED`.
- [ ] Admit any next TMI family only after an explicit ATMONTO mapping and
  reviewed source/evidence boundary. Do not promote informational notices only
  to increase coverage.

Do not reintroduce fixed question registries or bypass the Query Agent for
apparently simple natural-language questions. Deterministic retrieval stays
inside bounded tools; natural-language interpretation and tool routing remain
model-mediated.

Do not promote an export, frozen evaluation dataset, or batch snapshot into the
runtime source of truth. New source families enter through the ingestion
pipeline and persistent evidence store; lexical, vector, RDF/Turtle, and Neo4j
representations remain rebuildable views.

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
- Development-cohort Semantic Resolution performance claims until a natural
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
- Keep generated stores, vector indexes, exports, provider artifacts, and
  credentials out of Git.
- Preserve historical material through the artifact index and Git history.
- Apply the research-prototype effort boundary in `AGENTS.md`.
- Require each mainline implementation batch to add or simplify a user-visible
  capability. A validator-only batch needs a reproduced supported-workflow
  failure or an explicit user request.
