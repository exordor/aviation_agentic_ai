# Documentation Map

This map is the current entry point for research and thesis documentation. It
separates canonical documents from historical reports so the project can keep
old evidence without letting old framing control the thesis story.

## Start Here

| Purpose | Document |
| --- | --- |
| Research mainline, RQs, and validation gates | `docs/research_mainline.md` |
| Formal thesis framing and claim safety | `docs/thesis_positioning.md` |
| Documentation tiers and maintenance rules | `docs/documentation_maintenance.md` |
| Experiment sequence and regeneration commands | `docs/experiment_workflow.md` |
| Metric definitions and no-overall-score policy | `docs/evaluation_protocol.md` |
| Paper-analysis workflow | `docs/research_paper_analysis_protocol.md` |
| Current dashboard synthesis | `reports/stages/thesis_experiment_dashboard.md` |
| Reviewer-defense guardrails | `reports/stages/nasa_atmonto_reviewer_defense_audit.md` |

## Data And Source Boundary

| Topic | Document |
| --- | --- |
| ATCSCC source shape and processing | `reports/stages/atcscc_data_format_and_processing_flow.md` |
| ATCSCC source brief | `reports/stages/atcscc_source_brief.md` |
| Event-centric framing | `reports/stages/atcscc_event_centric_extraction_framing.md` |
| Formal experiment protocol | `docs/experiment_protocol.md` |
| Gold annotation guide | `docs/nasa_atmonto_gold_annotation_guide.md` |

## Schema/Profile Documents

| Topic | Document |
| --- | --- |
| ATCSCC application schema overview | `reports/stages/atcscc_ontology_profile_overview.md` |
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
| CHATATC paper analysis | `reports/stages/chatatc_paper_analysis.md` |
| Paper figure gallery workflow | `docs/research_paper_analysis_protocol.md`, `scripts/build_paper_figure_gallery.py` |

## Reports That Are Historical Or Secondary

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

## Artifact Management Policy

The repository intentionally tracks bounded thesis-evidence artifacts that are
needed to reproduce the current ATCSCC claims:

- reviewed gold and review-decision artifacts under `data/evaluation/nasa_atmonto/`;
- formal S0-S7 prediction and run-metadata artifacts under
  `data/experiments/nasa_atmonto/formal/`;
- stage-report JSON/Markdown files that feed the thesis dashboard, SOTA audit,
  reviewer-defense audit, and chapter draft.

The repository intentionally ignores raw/local/generated material that is either
large, environment-specific, or easy to rebuild:

- raw NASA ATMONTO snapshots under `data/raw/nasa_atmonto/`;
- smoke outputs under `data/experiments/nasa_atmonto/formal/smoke/`;
- vector indexes, chunks, local paper PDFs, temporary PDF extraction assets,
  gallery HTML/manifest files, and `outputs/`.

Future large experiment outputs should enter Git only when they are referenced
by the thesis dashboard or a claim-safety audit. Otherwise place them under an
ignored runtime/output location and summarize them in a small tracked report.

## Document Precedence

When documents disagree, use this precedence:

1. `docs/thesis_positioning.md`
2. `docs/research_mainline.md`
3. `docs/documentation_maintenance.md`
4. `docs/experiment_workflow.md`
5. `reports/stages/thesis_experiment_dashboard.md`
6. Latest SOTA/reviewer-defense audit reports
7. Older stage reports

This avoids old PHAK-oriented reports overriding the current ATCSCC
schema-constrained Agentic KG-RAG framing.
