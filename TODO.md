# TODO

Last updated: 2026-08-01

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
- [ ] Correct the observed insufficient-answer stop policy: when retrieved
  evidence establishes that actual control or causation is unsupported, the
  Query Agent should return `insufficient` before exhausting its 10-tool
  budget. Re-run the six-task cross-domain smoke once after that behavior is
  changed.
- [ ] Promote the six current TMI, Flight, Weather, Sector, cross-domain, and
  insufficient task categories from compatibility smoke to a frozen
  evaluation only after sampling, annotations, and acceptance rules are
  independently reviewed.
- [ ] Review and expand the explicitly allowlisted Web Evidence seed catalog
  only when a source role, parser profile, and evidence-support task are
  specified. Keep the Wigolo sidecar disabled by default.

Do not reintroduce fixed question registries or bypass the Query Agent for
apparently simple natural-language questions. Deterministic retrieval stays
inside bounded tools; natural-language interpretation and tool routing remain
model-mediated.

Do not promote an export, frozen evaluation dataset, or batch snapshot into the
runtime source of truth. New source families enter through the ingestion
pipeline and persistent evidence store; lexical, vector, RDF/Turtle, and Neo4j
representations remain rebuildable views.

Keep external Web Evidence acquisition at the sidecar boundary. It must persist
immutable source versions and anchors through the normal SQLite path, never
write during query time, and never be treated as an aviation authority or
causal source.

## Explicitly Deferred

- A formal representation of internal decision inputs, alternatives,
  constraints, rationale, trade-offs, and attributable outcomes.
- Weather-cause claims, operational effectiveness, and decision optimality.
- ASPM demand, AAR, capacity, EDCT, runway configuration, and flight-level
  impact.
- TCF, CWA, SIGMET, NOTAM, operational ADS-B, and national-scale
  single-flight trajectories beyond the bounded configured sources.
- Advisory lifecycle or TMI-episode grouping.
- National Playbook PDF grounding.
- Broad web crawling, unrestricted browser access, and automatic Web Evidence
  seed discovery.
- Operational-situation and outcome-aware similarity, learned reranking, and
  TMI recommendation.
- General-purpose planner, long-term Agent memory, and unrestricted aviation
  chat.
- Default-ingest activation of ontology candidate generation and a live
  candidate-fact benchmark; the current construction API remains opt-in.
- New Agent roles without an observed need.
- Multi-model or statistically powered evaluation beyond an approved protocol.
- Semantic Resolution performance claims until a reviewed set of naturally
  ambiguous authority-resolution tasks exists.
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
- Keep large historical reports and superseded plans in the dated external
  archive described by `docs/repository_artifact_policy.md`; do not restore
  them into the default checkout for convenience.
- Apply the research-prototype effort boundary in `AGENTS.md`.
- Require each mainline implementation batch to add or simplify a user-visible
  capability. A validator-only batch needs a reproduced supported-workflow
  failure or an explicit user request.
