# Decision Log

> Seeded on 2026-07-05 from the project scope lock (`docs/master_project_scope_lock.md`) and the documentation map tiering rules. Each entry records a structural decision and its consequences. Future significant choices (tool changes, abandoned experiments, model selection, refactor scope) should be appended here.

## Current Precedence

Decisions are append-only historical records. Later decisions supersede earlier
ones when their scopes conflict.

| Decision | Current status |
| --- | --- |
| D001-D003 | Historical thesis and evaluation governance. |
| D004-D005 | Still applicable as archive and source-boundary guidance. |
| D006 | Documentation tiers remain applicable; its original thesis-routing table is superseded by D010. |
| D007-D008 | Historical cross-source evaluation route; optional, not the system mainline. |
| D009 | Decision-record interaction contract remains useful; query foundation is complete and visualization is paused. |
| D010 | Current project posture and default-context decision. |

## D001 — Single thesis-grade system study

### Date

(see git history of master_project_scope_lock.md)

### Context

The repository had accumulated multiple parallel experimental tracks (PHAK ontology, web demo, chunking experiments, multi-source pilots).

### Decision

Freeze the project outcome as one bounded thesis-grade system study: Evidence-Grounded Schema-Constrained Agentic KG-RAG for FAA ATCSCC Advisories.

### Reason

- Prevents research support work from expanding into parallel subprojects.
- Keeps thesis scope defensible.

### Alternatives Considered

- Multi-thesis split (ontology + RAG + agent loop as separate studies).
- Open-ended benchmark project.

### Consequences

Pro: clear stop rule and minimum deliverable set.
Con: any new idea must fit a locked deliverable or be deferred.

## D002 — Exactly four research questions

### Date

(same as above)

### Context

Multiple candidate RQs were circulating across stage reports.

### Decision

Keep exactly four RQs: schema-constrained extraction, agentic validation-refinement, KG-RAG grounding, failure boundary. Any additional question must fold into one of these four or move to future work.

### Reason

- Keeps the evaluation layered and bounded.
- Prevents open-ended benchmark creep.

### Alternatives Considered

- Adding a fifth research question for cross-source transfer.
- Treating ontology completeness as an research question.

### Consequences

Pro: each research question has an experiment layer, metrics, artifacts, pass/fail interpretation.
Con: cross-source and ontology-completeness work is future work only.

## D003 — Layered metrics, no overall score

### Date

(same as above)

### Context

A single mixed score would let one strong layer hide a weak one.

### Decision

Report layered metrics: extraction, evidence, agentic-loop, retrieval/answer, boundary. No mixed overall score.

### Reason

- Recall@5, provenance completeness, and unsupported-claim rate have different denominators and risk profiles.

### Alternatives Considered

- Weighted average score.
- Single "KG-RAG quality" number.

### Consequences

Pro: tradeoffs are visible; GraphRAG cannot be claimed to improve Recall@k without the retrieval-result support.
Con: results table is wider and harder to compress into one slide number.

## D004 — PHAK-era evidence is historical

### Date

2026-05/06 archive wave (see git log)

### Context

Early PHAK Chapter 4 ontology, chunking, and web-demo reports used different framing than the current ATCSCC line.

### Decision

Treat PHAK, web-demo, chunking-era, and old final-report docs as historical. They may be cited for method evolution or negative results, but cannot override current ATCSCC framing.

### Reason

- Prevents ontology-first framing from leaking into the schema-constrained KG-RAG thesis.

### Alternatives Considered

- Delete PHAK-era files.
- Keep PHAK-era as primary track.

### Consequences

Pro: thesis story stays coherent.
Con: some reuse requires manual rewrite into ATCSCC wording.

## D005 — Source families stay separate

### Date

(same as D001)

### Context

ATCSCC advisories, FAA/NASA reference PDFs, NASR/facility data, weather, and transfer-pilot corpora have different shapes and evaluation protocols.

### Decision

Keep source families separate. Do not merge them into one semantic-F1 table unless a source-specific profile and gold/evaluation protocol exists for each family.

### Reason

- A shared F1 table would mix different denominators and tasks.

### Alternatives Considered

- Unified cross-source extraction metric.

### Consequences

Pro: each source family gets a task-relative correctness claim.
Con: cross-source comparison is limited to structural conformance, evidence grounding, and canonicalization yield.

## D006 — Documentation tiers and tier maintenance rules

### Date

(same as ARTIFACT_INDEX.md's source)

### Context

The repo mixes canonical framing, protocols, current evidence, source explainers, paper analyses, historical artifacts, and generated side artifacts.

### Decision

Use the descriptively named documentation layers below and the "Where New
Documents Should Go" routing table to keep canonical framing, current evidence,
source explainers, paper analyses, historical artifacts, and generated side
artifacts from polluting each other.

### Document Tiers

| Tier | Location | Examples | Maintenance rule |
| --- | --- | --- | --- |
| Current system context | repo root | `AGENTS.md`, `RESEARCH_AUDIT.md`, `GOALS.md`, `README.md`, `TODO.md`, `ARTIFACT_INDEX.md` | Keep short, consistent, and implementation-accurate. |
| Normative system design | `docs/` | `docs/multi_agent_kg_system_design.md` | Update only when the approved system contract changes. |
| Optional evaluation protocols | repo root + `docs/` | `EXPERIMENTS.md`, `docs/research_paper_analysis_protocol.md` | Load only for an explicitly reactivated evaluation or paper-analysis task. |
| Historical evaluation evidence | `reports/stages/` | formal scoring, retrieval, and chapter-draft reports | Preserve as dated evidence; do not present as current system truth. |
| Source and schema explainers | `reports/stages/` | ATCSCC data-flow and ontology-profile reports | Keep thesis-facing and readable; update when data/profile boundaries change. |
| Method migration and paper analysis | `reports/stages/`, `data/papers/README.md` | adaptation and analysis reports | Use for design inspiration only after full-paper/figure inspection; do not import claims directly. |
| Historical artifacts | `docs/archive/phak_era/`, `reports/stages/`, `reports/final/` | old prototype and report drafts | Preserve for provenance, but do not let them override current ATCSCC framing. |
| Generated side artifacts | `reports/stages/*.json`, `.csv`, `.html`, `.log` | report JSON, review packets, worksheets, logs | Track only if they support a current dashboard/audit/chapter claim; otherwise keep under ignored output paths. |

### Historical Routing Table

The table below records the original thesis-era routing policy. D010 supersedes
it for active system work. New system goals, capability contracts, and
implementation priorities now route through `GOALS.md`, the relevant normative
design under `docs/`, and `TODO.md`; optional experiment changes continue to
use the experiment documents only when that track is explicitly reactivated.

| New material | Destination | Required follow-up |
| --- | --- | --- |
| Change to thesis scope, RQs, or contribution claims | `RESEARCH_OVERVIEW.md` and `RESEARCH_QUESTIONS.md` | Update this map. |
| Change to experiment order, metrics, or regeneration commands | `EXPERIMENTS.md` | Verify report commands remain reproducible. |
| New source-family explanation | `reports/stages/<source>_source_brief.md` or `<source>_data_format_and_processing_flow.md` | Decide whether it is primary, reference-only, transfer-pilot, or out of scope. |
| New schema/profile explanation | `reports/stages/<source>_ontology_profile_overview.md` | State whether it is a full ontology, application profile, mapping layer, or runtime output schema. |
| New experiment result | `reports/stages/<experiment>.md` plus JSON when generated | Link it from the dashboard or leave it as secondary evidence. |
| New paper analysis | `reports/stages/<paper>_paper_analysis.md`, `<paper>_figures_analysis.md`, or `<paper>_paper_adaptation.md` | Register the paper in `data/papers/README.md` when it influences method design. |
| Final report or defense material | `reports/final/` | Ensure it cites current docs, not legacy stage index material. |

### Reason

- Tier discipline keeps canonical framing, current evidence, source explainers, paper analyses, and historical artifacts from polluting each other.
- A documented precedence chain lets current ATCSCC framing override legacy PHAK-era framing without deleting the older evidence.

### Alternatives Considered

- Flat docs/ namespace.
- Per-date organization.

### Consequences

Pro: clear precedence chain (now anchored at RESEARCH_AUDIT.md after this refactor).
Con: tier discipline requires upkeep; stale tier assignments cause context pollution.

## D007 — Cross-source multi-agent work stays on an additive V2 track

### Date

2026-07-13

### Context

The project already contains an ATCSCC extraction loop and a minimal end-to-end
agent, while NASR and AviationWeather snapshots exist outside the scored
single-source thesis evaluation. Cross-source answers also require facility-code
and operational-abbreviation alignment before weather evidence can be linked
safely.

### Decision

Keep the scored ATCSCC thesis path frozen and build cross-source abbreviation
alignment and evidence-layered answers as an additive V2 subsystem. Use a
lightweight supervisor with explicit node/state contracts so the scheduler can
later migrate to a state-graph framework without rewriting the nodes.

### Reason

- Preserves current thesis claims and reviewed artifacts.
- Makes source, entity, terminology, temporal, and answer authority explicit.
- Allows the first cross-source cohort to be evaluated separately before any
  thesis-scope decision.

### Alternatives Considered

- Reopen the thesis and replace the current single-source evaluation.
- Use autonomous source agents with LLM-mediated identity and evidence fusion.
- Introduce a state-graph framework before the node contracts are stable.

### Consequences

Pro: the V2 path is reproducible, reviewable, and isolated from current thesis evidence.
Con: cross-source results cannot be presented as current thesis findings without a separate evaluation and scope decision.

## D008 - Promote Cross-Source V2 Into The Thesis Mainline

### Date

2026-07-13

### Context

The additive subsystem is implemented over pinned source snapshots, the
68-record cohort is reproducible, ambiguity gates are autonomous, and a
separate mainline evaluation now compares matched answer modes and stress-tests
`GS` ambiguity.

### Decision

Supersede the earlier additive-only scope boundary. Cross-source V2 is part of
the thesis mainline under the agentic validation, cross-source grounding, and
autonomous failure questions. Retain the existing single-source extraction
and routed KG-RAG experiments as the foundation rather than replacing them.

### Evidence Gate

- 20 ambiguity cases: accepted-target accuracy 1.00, quarantine accuracy 1.00,
  zero out-of-registry acceptances.
- 24 matched answers: required evidence/citation-layer coverage 0.25
  source-only, 0.75 linked-text, and 1.00 KG-layered.
- Independent Evaluation Agent: 24/24 pass; causal-overstatement count 0.

### Consequences

Pro: the thesis now evaluates an authority-grounded, genuinely cross-source
Agentic KG-RAG method with autonomous runtime gates.

Con: the result remains a component evaluation over one cohort and one
ambiguity family. The linked-text arm shares accepted links, and the automated
evaluator is not external aviation-expert certification.

## D009 - Make Published Decision-Record Understanding The Next User Goal

### Date

2026-07-26

### Context

The mainline system can ingest one retrospective ATCSCC advisory, construct and
validate an event graph, project it to RDF and Neo4j, and answer a bounded
graph-grounded question. The longer-term decision-case vision includes weather,
capacity, outcomes, lifecycle grouping, and historical similarity, but those
sources and semantic units are not yet established.

### Decision

The next user-facing stage is a bounded ATCSCC Decision Record Explorer. Its
purpose is to help a user understand and verify what measure was published,
which facility it controlled, when it was effective, which reason the advisory
declared, and which source supports each statement.

The stage reuses the existing Agents and ontology profile. It adds no new Agent
role, source family, causal explanation, historical ranking, or TMI
recommendation.

### Reason

- It exposes the value of the existing graph and provenance path to a user.
- It tests a complete user task before adding more data or semantic layers.
- It keeps source statements separate from system associations and unsupported
  causal inference.
- It creates the minimum interaction foundation needed before advisory
  lifecycle and cross-source decision-case work.

### Consequences

Pro: the system gains a concrete, verifiable user-facing purpose without
expanding its evidence claims.

Con: the explorer can explain a published record but cannot yet explain why the
decision was operationally optimal or recommend a future TMI.

## D010 - Make The Multi-Agent System The Mainline And Pause Visualization

### Date

2026-07-26

### Context

The repository had a working multi-Agent ingest, validation, RDF/Neo4j, and
bounded Query Agent path, but its root metadata still presented earlier thesis
experiments, cross-source weather evaluation, Gold workflows, and web-demo work
as current. The read-only query visualization had also reached a stable
feature-branch checkpoint.

### Decision

Treat system and framework construction as the only default mainline.

The active deliverable is the source-bounded multi-Agent event knowledge system
on `main`. Formal experiments remain optional evidence tracks. The
visualization implementation stays isolated on
`codex/kg-visualization-research` until the user explicitly requests a merge.

New sessions start from `RESEARCH_AUDIT.md` and `GOALS.md`; they do not preload
the experiment, result, stage-report, or archive families.

### Reason

- The project is intended to deliver a useful system, not to optimize a paired
  comparison paper.
- Stale root metadata repeatedly redirected new sessions into superseded work.
- Keeping visualization isolated allows the project to return to its semantic
  and user-value mainline without discarding reviewed UI work.

### Consequences

Pro: current implementation, project goal, and task queue now share one scope.
Historical experiments remain reproducible without polluting default context.

Con: the next semantic system increment is intentionally undecided and requires
an explicit user-task contract before implementation.

## D011 - Add Non-Causal Decision Context Before Case Recommendation

### Date

2026-07-26

### Context

The Decision Record Explorer established reliable source-grounded access to
three ATCSCC records, including a formal GDP reason, a Ground Stop profile gap,
and an honest missing-reason cancellation. It did not reconstruct what weather
information was available at issue time or what public operational results
surrounded the TMI period.

The user approved a bounded next increment over the same three records. The
available tracked data supports deterministic TAF/METAR selection and a pinned
BTS On-Time subset without adding a model-mediated source-fusion step.

### Decision

Implement Decision Context Case v0 as an additive deterministic layer:

- select only TAF reports issued no later than the advisory and valid during
  the TMI operational period;
- select METAR reports only within the approved pre-issue and operational
  windows;
- store event-to-weather links as non-causal context associations;
- summarize pinned public BTS rows into baseline, active, and recovery-window
  operational proxies;
- keep BTS summaries outside RDF and Neo4j;
- preserve the original reason status for all three records;
- expose the validated context and outcome summaries through bounded read-only
  Query Agent tools.

The system does not map BTS values to FAA demand, Airport Arrival Rate,
capacity, or EDCT. Carrier-reported weather and NAS delay fields remain source
attributions, not causal findings. The extension adds no Agent role, graph-write
tool, recommendation policy, or model call.

### Reason

- It advances the user task from reading a decision record to reconstructing an
  auditable historical case.
- Deterministic adapters are appropriate for stable structured source fields.
- Separate formal facts, context associations, and outcome summaries preserve
  the semantic boundary between source statements, temporal context, and public
  proxies.
- The three-record scope can reveal source-binding, temporal-leakage, and
  missing-evidence failures before broader data expansion.

### Consequences

Pro: the system can retrieve a bounded decision record together with
decision-time weather context and public operational proxies while retaining
source-level provenance and honest missing states.

Con: the reconstructed case does not establish why a TMI was selected, whether
it caused an outcome, or whether it was operationally optimal. ASPM demand,
AAR, capacity, EDCT, regional weather, lifecycle grouping, historical ranking,
and TMI recommendation remain separate future decisions.
