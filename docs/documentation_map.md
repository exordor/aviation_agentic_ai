# Documentation Map

This map is the current entry point for research and thesis documentation. It
separates canonical documents from historical reports so the project can keep
old evidence without letting old framing control the thesis story. It also
absorbs the former `documentation_maintenance.md`, `context_hygiene_audit.md`,
and `tracked_context_inventory.md` (merged here to remove redundancy).

## Start Here

| Purpose | Document |
| --- | --- |
| New-thread compact context | `docs/thread_handoff.md` |
| Master-project scope lock | `docs/master_project_scope_lock.md` |
| Research mainline, RQs, and validation gates | `docs/research_mainline.md` |
| Thesis writing spine | `docs/thesis_writing_spine.md` |
| Formal thesis framing and claim safety | `docs/thesis_positioning.md` |
| Pipeline authority and architecture principles | `docs/pipeline_authority_model.md` |
| Formal experiment protocol, metrics, and procedure | `docs/experiment_protocol.md` |
| Paper-analysis workflow | `docs/research_paper_analysis_protocol.md` |
| ATCSCC agent architecture | `docs/atcscc_agent_architecture.md` |
| LLM review protocol | `docs/llm_review_protocol.md` |
| Presentation style harness | `docs/presentation_style_harness.md` |
| Final deliverable directory status | `reports/final/README.md` |
| Current dashboard synthesis | `reports/stages/thesis_experiment_dashboard.md` |
| Reviewer-defense guardrails | `reports/stages/nasa_atmonto_reviewer_defense_audit.md` |

The minimal new-thread startup pack is intentionally small:
`thread_handoff.md` → `documentation_map.md` (this file). Load task-specific
files only after choosing the work type.

## Data And Source Boundary

| Topic | Document |
| --- | --- |
| ATCSCC source shape and processing | `reports/stages/atcscc_data_format_and_processing_flow.md` |
| ATCSCC source brief | `reports/stages/atcscc_source_brief.md` |
| Event-centric framing | `reports/stages/atcscc_event_centric_extraction_framing.md` |
| Gold annotation guide | `docs/nasa_atmonto_gold_annotation_guide.md` |

## Schema/Profile Documents

| Topic | Document |
| --- | --- |
| ATCSCC application schema overview | `reports/stages/atcscc_ontology_profile_overview.md` |
| CQ answerability matrix | `docs/atcscc_cq_answerability_matrix.md` |
| Semantic requirements | `reports/stages/atcscc_semantic_requirements.md` |
| Rejection/profile-gap analysis | `reports/stages/nasa_atmonto_rejection_adjudication.md` |
| Prediction output validation | `reports/stages/nasa_atmonto_prediction_output_validation.md` |

## Experiment Evidence

| Layer | Primary documents |
| --- | --- |
| Extraction scoring | `reports/stages/nasa_atmonto_formal_experiment_scoring.md` |
| CQ/query evaluation | `reports/stages/nasa_atmonto_cq_evaluation.md`, `reports/stages/nasa_atmonto_cq_query_evaluation.md` |
| Agentic loop | `reports/stages/nasa_atmonto_s5_s6_agentic_loop.md`, `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md`, `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md` |
| Retrieval and graph health | `reports/stages/nasa_atmonto_s7_retrieval.md`, `reports/stages/nasa_atmonto_s7_graph_health.md` |
| Answer generation | `reports/stages/nasa_atmonto_answer_generation.md`, `reports/stages/nasa_atmonto_s7_answer_generation.md`, `reports/stages/nasa_atmonto_s7_llm_answer_generation.md` |
| Failure review | `reports/stages/nasa_atmonto_s7_llm_failure_review.md`, `reports/stages/nasa_atmonto_s7_candidate_adjudication.md`, `reports/stages/nasa_atmonto_s7_profile_decision.md` |
| SOTA/readiness audit | `reports/stages/nasa_atmonto_sota_goal_audit.md`, `reports/stages/current_pipeline_sota_gap_audit.md` |

## Literature And Method Migration

| Topic | Document |
| --- | --- |
| Literature backbone | `reports/stages/agentic_ontology_graphrag_mainline_literature_search.md` |
| SOTA comparison matrix | `reports/stages/sota_comparison_matrix.md` |
| Domain-agnostic methodology roadmap | `reports/stages/domain_agnostic_ontology_kg_graphrag_methodology_roadmap.md` |
| Method-paper migration plan | `reports/stages/method_paper_migration_experiment_plan.md` |
| Multi-agent method adaptation | `reports/stages/multi_agent_pipeline_method_adaptation.md` |
| Claim KG / GraphRAG paper adaptation | `reports/stages/claim_kg_graphrag_paper_adaptation.md` |
| Gold-deposit ontology-to-KG paper analysis | `reports/stages/minerals_16_00050_paper_analysis.md` |
| CHATATC paper analysis | `reports/stages/chatatc_paper_analysis.md` |
| Paper figure gallery workflow | `docs/research_paper_analysis_protocol.md`, `scripts/build_paper_figure_gallery.py` |

## Scope And Historical-Document Risk

The current research line is:

> Agentic KG-RAG for evidence-grounded question answering over retrospective
> FAA ATCSCC advisories.

### Reports That Are Historical Or Secondary

The following document families are useful background but should not be treated
as the current thesis entry point:

- PHAK Chapter 4 ontology, chunking, KG, and web-demo reports.
- Early `hybrid_rag_*`, `retrieval_ablation*`, and `graphrag_review` reports
  from the aviation-training prototype.
- NASA BGA transfer-pilot reports, which provide transfer evidence only.
- `reports/stages/index.md`, which is an artifact inventory and still contains
  legacy stage-index content.
- Old `reports/final/*` drafts generated from the PHAK-era project evidence.

Historical reports may still be cited for method evolution or negative results,
but current thesis claims should be routed through `docs/research_mainline.md`,
`docs/thesis_positioning.md`, and `reports/stages/thesis_experiment_dashboard.md`.

### Secondary Reading Set (Per-File Risk)

These files may still be useful, but should not be treated as current narrative
without checking the framing documents first.

| File or family | Context risk | Safe use |
| --- | --- | --- |
| `reports/final/project_report.md` | Transitional report that still carries aviation-training / PHAK framing. | Reuse isolated sections only after manual rewrite into ATCSCC wording. |
| `reports/stages/index.md` | Artifact inventory with many legacy report links. | Navigation only, not thesis story. |
| `reports/stages/current_pipeline_sota_gap_audit.md` | Useful SOTA gap audit, but may refer to earlier pipeline state. | Use for gap framing after checking latest dashboard and reviewer audit. |
| `docs/archive/phak_era/nasa_atmonto_experiment_design.md` | Transitional document from the PHAK route toward NASA ATMONTO. | Use for historical motivation only after checking `docs/research_mainline.md`. |
| `reports/stages/data_source_extraction_method_matrix.md` | Mixes source-family comparison with historical PHAK baseline. | Use for source-family policy, not as current experiment evidence. |
| `reports/stages/sota_data_source_format_processing_review.md` | Useful data-format review, but not a replacement for current ATCSCC source docs. | Use as supporting literature-method context. |
| `reports/stages/*paper_analysis.md`, `*_figures_analysis.md`, `*_paper_adaptation.md` | Method inspiration may be domain-agnostic and not directly validated in ATCSCC. | Use for related work and design migration only. |

### Ignored Local Material

The following paths are intentionally ignored by Git and should not be loaded as
current research context unless the task is specifically about historical
forensics or cleanup:

| Path | Why it is risky |
| --- | --- |
| `reports/archive/` | Local archive of obsolete stage reports; keep out of thesis-writing context. |
| `outputs/` | Runtime outputs and scratch material that may combine multiple branches or stale experiments. |
| `reports/stages/paper_figure_gallery.html` and gallery manifests | Local visual-comparison pages generated during paper review; useful for inspection, not thesis evidence. |

### Reading Rules

1. Start every thesis-writing, review, or experiment-planning task from this
   map, not from `reports/stages/index.md`.
2. If a document says PHAK, handbook, aviation training, Chapter 4, web demo,
   or curated ontology as the main object, classify it as historical unless a
   current ATCSCC document explicitly links it.
3. Keep ATCSCC advisories, FAA/NASA reference PDFs, NASR/facility data, weather
   data, and transfer-pilot data as separate source families.
4. Do not merge source families into one extraction metric table unless a
   source-specific profile and gold/evaluation protocol exist for each family.
5. Treat completeness and correctness as task-relative (CQ coverage,
   source-observable completeness, evaluation completeness, reviewed-subset
   correctness are separate claims).
6. Paper-analysis files can motivate methods, but they cannot replace current
   ATCSCC evidence, gold review, or SOTA/reviewer-defense audits.

## Context Inventory

### Audit Commands

Use tracked-file scans for context hygiene:

```bash
git ls-files '*.md' 'reports/**/*.json'
git grep -n -E '<pattern>' -- AGENTS.md README.md docs reports src scripts tests data/papers
```

Do not use broad multi-root `rg` scans as proof that repository context is
clean; they can include ignored local archives when explicit paths are supplied.

### Tracked File-Family Snapshot

| Family | Default context status |
| --- | --- |
| Root project docs | mixed; `AGENTS.md` is authoritative, `CLAUDE.md` is a compatibility shim, `README.md` and `GOALS.md` are project references, `TASKS.md` is execution backlog only. |
| `docs/*.md` | canonical docs; PHAK-era protocols archived under `docs/archive/phak_era/`. |
| `reports/stages/*` | mixed; current ATCSCC evidence, method literature, and legacy experiment reports live together. |
| `reports/final/*` | mostly historical/transitional; current ATCSCC entry files are explicitly named `atcscc_*`. |
| `reports/reviews/*` | historical review evidence; useful for audit trail, not thesis entry context. |
| `data/evaluation/nasa_atmonto/*` | current evaluation evidence; load only for gold/review tasks. |
| `data/raw/nasa_bga_aerodynamics/*` | tracked transfer-pilot corpus; not current ATCSCC mainline. |

### Tracked But Non-Default Families

| Family | Why it can pollute context | Safe use |
| --- | --- | --- |
| `docs/archive/phak_era/*` | Describe the earlier aviation-training prototype; can make the thesis look ontology-first. | Historical method evolution only. |
| Early `reports/stages/benchmark_*`, `chunking_*`, `hybrid_rag_*`, `retrieval_ablation*`, `graphrag_review.*`, `kg_validation.*`, `web_demo_*` | Mix PHAK/web-demo evidence with current ATCSCC terminology. | Negative results, method evolution, or explicit comparison. |
| `reports/final/project_*`, `reports/final/defense_deck_outline.md`, old deck source JSON | Final-style but mostly pre-ATCSCC. | Presentation format reference or manually reviewed reusable fragments. |
| `reports/reviews/*` and root `reports/*review*.md` | Review trails from earlier branches may include stale issue lists or resolved risks. | Audit history only after checking current dashboard and reviewer-defense audit. |
| `data/cqs/06_phak_*.json` | Historical PHAK benchmark and gold data. | Load only for explicit PHAK benchmark or historical comparison tasks. |

### Current-Use Families

| Family | Use |
| --- | --- |
| `reports/stages/atcscc_*` | ATCSCC source, schema, validation, repair, and graph-use explainers. |
| `reports/stages/nasa_atmonto_*` | Current formal experiment scoring, agentic loop, retrieval, answer generation, and reviewer-defense evidence. |
| `data/evaluation/nasa_atmonto/*` | Gold review, CQ query templates, candidate review, and review packets. |
| `reports/stages/*sota*`, `*method*`, `*paper_analysis*`, `*paper_adaptation*` | Related work and method migration, not direct experiment evidence unless linked by the dashboard. |

## Maintenance Rules

### Codex Skill And Plugin Hygiene

Keep project threads on the smallest useful tool surface:

- Enable only the plugins needed for the current work.
- Treat skills as task routers, not background reading. Load a skill only when
  its trigger matches the current action, then return to the project startup
  pack and task-specific files.
- Do not use broad research, design, or document-generation skills as default
  project context. They can import assumptions unrelated to the ATCSCC
  schema-constrained KG-RAG line.
- Keep custom skill descriptions short and trigger-only. Long descriptions are
  injected into new threads and compete with project context.

| State | Plugins or skills | Use |
| --- | --- | --- |
| Keep enabled | Browser, GitHub, Superpowers | Local preview, repository publishing/review, planning and verification workflows. |
| Enable on demand | Documents, Data Analytics, Build Web Data Visualization, OpenAI Developers | Use only for document rendering, dashboard/report artifacts, visual analytics, or product/API-specific work. Disable again after the task. |
| Keep off by default | Product Design, Creative Production, Spreadsheets, Presentations, broad browser/desktop-control plugins | These add large generic instructions and usually do not help ATCSCC schema, KG extraction, retrieval, or thesis-text work. |

### Neutral Wording Audit

Project documents avoid model-brand and generic assistant wording in default
context. Use `model-assisted`, `model-based`, or `configured-model` for review
workflows unless a field name or metric explicitly uses `llm_*`.

Allowed technical residues: project title terms such as `Aviation Agentic AI`;
`LLM` as a technical method category in RQ/method/evaluation text; schema and
report fields such as `llm_review`, `requires_llm_review`, and
`llm_as_judge_enabled`. Do not use default-context wording such as model-brand
names, generic advisory assistant capability, generated-by-model labels, or
certified/operational assistant claims.

### Document Tiers

| Tier | Location | Examples | Maintenance rule |
| --- | --- | --- | --- |
| T0 canonical framing | `docs/` | `thesis_positioning.md`, `research_mainline.md`, `documentation_map.md` | Update when the thesis scope, RQs, claim boundaries, or entry points change. |
| T1 protocols and scope control | `docs/` | `experiment_protocol.md`, `research_paper_analysis_protocol.md` | Update when the reproducible workflow, scoring rules, or paper-intake process changes. |
| T2 current thesis evidence | `reports/stages/` | `nasa_atmonto_formal_experiment_scoring.md`, `nasa_atmonto_s7_retrieval.md`, `thesis_experiment_dashboard.md` | Keep as generated or reviewed evidence; cite through the dashboard and this map. |
| T3 source/schema explainers | `reports/stages/` | `atcscc_data_format_and_processing_flow.md`, `atcscc_ontology_profile_overview.md` | Keep thesis-facing and readable; update when data/profile boundaries change. |
| T4 method migration and paper analysis | `reports/stages/`, `data/papers/README.md` | `claim_kg_graphrag_paper_adaptation.md`, `multi_agent_pipeline_method_adaptation.md` | Use for design inspiration only after full-paper/figure inspection; do not import claims directly. |
| T5 historical artifacts | `docs/archive/phak_era/`, `reports/stages/`, `reports/final/` | PHAK reports, old web-demo reports, old final report drafts | Preserve for provenance, but do not let them override current ATCSCC framing. |
| T6 generated side artifacts | `reports/stages/*.json`, `.csv`, `.html`, `.log` | report JSON, review packets, worksheets, logs | Track only if they support a current dashboard/audit/chapter claim; otherwise keep under ignored output paths. |

### Where New Documents Should Go

| New material | Destination | Required follow-up |
| --- | --- | --- |
| Change to thesis scope, RQs, or contribution claims | `docs/thesis_positioning.md` and `docs/research_mainline.md` | Update this map. |
| Change to experiment order, metrics, or regeneration commands | `docs/experiment_protocol.md` | Verify report commands remain reproducible. |
| New source-family explanation | `reports/stages/<source>_source_brief.md` or `<source>_data_format_and_processing_flow.md` | Decide whether it is primary, reference-only, transfer-pilot, or out of scope. |
| New schema/profile explanation | `reports/stages/<source>_ontology_profile_overview.md` | State whether it is a full ontology, application profile, mapping layer, or runtime output schema. |
| New experiment result | `reports/stages/<experiment>.md` plus JSON when generated | Link it from the dashboard or leave it as secondary evidence. |
| New paper analysis | `reports/stages/<paper>_paper_analysis.md`, `<paper>_figures_analysis.md`, or `<paper>_paper_adaptation.md` | Register the paper in `data/papers/README.md` when it influences method design. |
| Final report or defense material | `reports/final/` | Ensure it cites current docs, not legacy stage index material. |

### Update Rules

1. If a document changes the thesis story, update the canonical docs first.
2. If a document only records an experiment output, keep it in `reports/stages/`
   and link it only when it supports a current claim.
3. If a report is superseded, do not delete it by default; mark it historical
   in this map or keep it unlinked from current entry points.
4. If a generated report starts creating dirty diffs on every run, fix the
   generator before treating the report as reproducible thesis evidence.
5. Keep source families separate. ATCSCC event extraction, FAA/NASA reference
   PDFs, NASR/facility data, weather data, and NASA BGA transfer pilots should
   not share one semantic F1 table.
6. Keep claim layers separate. Schema validity, semantic correctness, evidence
   support, retrieval quality, answer quality, automated diagnostics, and human
   review are different evidence types.

### Cleanup Policy

Do not delete old reports merely because they are no longer the main story.
Delete or ignore only when a file is: local scratch; large and reproducible; not
cited by any dashboard, audit, final report, or paper-analysis record; or
superseded by a cleaner tracked report and not needed for provenance. When in
doubt, preserve the old artifact and reduce its visibility by removing it from
canonical entry points.

## Artifact Management Policy

The repository intentionally tracks bounded thesis-evidence artifacts needed to
reproduce the current ATCSCC claims:

- reviewed gold and review-decision artifacts under `data/evaluation/nasa_atmonto/`;
- formal S0-S7 prediction and run-metadata artifacts under
  `data/experiments/nasa_atmonto/formal/`;
- stage-report JSON/Markdown files that feed the thesis dashboard, SOTA audit,
  reviewer-defense audit, and chapter draft.

The repository intentionally ignores raw/local/generated material that is either
large, environment-specific, or easy to rebuild: raw NASA ATMONTO snapshots under
`data/raw/nasa_atmonto/`; smoke outputs under
`data/experiments/nasa_atmonto/formal/smoke/`; vector indexes, chunks, local
paper PDFs, temporary PDF extraction assets, gallery HTML/manifest files,
historical local archives under `reports/archive/`, and `outputs/`.

Future large experiment outputs should enter Git only when they are referenced
by the thesis dashboard or a claim-safety audit. Otherwise place them under an
ignored runtime/output location and summarize them in a small tracked report.

## Document Precedence

When documents disagree, use this precedence:

1. `docs/thread_handoff.md` for compact new-thread orientation
2. `docs/thesis_positioning.md`
3. `docs/research_mainline.md`
4. `docs/experiment_protocol.md`
5. this map (`docs/documentation_map.md`)
6. `reports/stages/thesis_experiment_dashboard.md`
7. Latest SOTA/reviewer-defense audit reports
8. Older stage reports

This avoids old PHAK-oriented reports overriding the current ATCSCC
schema-constrained Agentic KG-RAG framing. A reviewer should be able to
reconstruct the thesis path using only:

```text
docs/thread_handoff.md
  -> docs/documentation_map.md
  -> docs/thesis_positioning.md
  -> docs/research_mainline.md
  -> docs/experiment_protocol.md
  -> reports/stages/thesis_experiment_dashboard.md
  -> reports/stages/nasa_atmonto_reviewer_defense_audit.md
```

All other reports are supporting evidence, historical context, or method
development notes.
