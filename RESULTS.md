# Results

> Migrated on 2026-07-05 from `docs/master_project_scope_lock.md` §Minimum Deliverable Set and `docs/documentation_map.md` §Experiment Evidence. Those source files (now archived under `docs/archive/governance_era/`) were migrated on 2026-07-05. No new claims — every row points at an existing evidence artifact.

## Deliverables And Evidence

| Deliverable | Observation | Evidence (artifact) | Interpretation | Confidence |
|---|---|---|---|---|
| Frozen ATCSCC data profile | Source family and format are documented and frozen. | `reports/stages/atcscc_data_format_and_processing_flow.md` | Defines the retrospective corpus and source-record shape. | high |
| Lightweight ATCSCC schema/profile | Application schema constrains accepted event fields and predicates; profile gaps documented. | `reports/stages/atcscc_ontology_profile_overview.md` | Engineering constraint, not full ontology. | high |
| Schema-constrained extraction experiment | Rule / LLM / schema / repair / hybrid extraction scored on the reviewed 100-record sample. | `reports/stages/nasa_atmonto_formal_experiment_scoring.md` | Layered metrics; structural acceptance is not semantic correctness. | medium (semantic layer requires reviewed gold) |
| Agentic validation/refinement loop | Validator/refiner/critic reduces specific schema and support failures. | `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md` | Auditable repair/rejection; not autonomous ontology construction. | medium |
| KG-RAG answer-generation comparison | Vector / graph / hybrid / routed retrieval compared for source-grounded answers. | `reports/stages/nasa_atmonto_s7_retrieval.md`, `reports/stages/nasa_atmonto_s7_llm_answer_generation.md` | KG-RAG improves some source-bounded grounding diagnostics; vector-only remains a fair baseline for source-local questions. | medium |
| Failure and claim-safety audit | Remaining failures categorized; human-review boundary explicit. | `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_sota_goal_audit.md` | Automated diagnostics separated from human/expert review. | high (process claim) |
| Thesis synthesis | Evidence turned into the research story. | `reports/stages/nasa_atmonto_experiment_chapter_draft.md` | Draft; final acceptance pending submission gates. | low (draft) |

## Confidence Levels

| Level | Meaning |
|---|---|
| `low` | single observation or draft state |
| `medium` | repeated observation or partial evidence layer |
| `high` | baseline- or repetition-supported, or process/protocol claim |

## Evidence Layer Map

| Layer | Primary documents |
| --- | --- |
| Extraction scoring | `reports/stages/nasa_atmonto_formal_experiment_scoring.md` |
| CQ/query evaluation | `reports/stages/nasa_atmonto_cq_evaluation.md`, `reports/stages/nasa_atmonto_cq_query_evaluation.md` |
| Agentic loop | `reports/stages/nasa_atmonto_s5_s6_agentic_loop.md`, `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md`, `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md` |
| Retrieval and graph health | `reports/stages/nasa_atmonto_s7_retrieval.md`, `reports/stages/nasa_atmonto_s7_graph_health.md` |
| Answer generation | `reports/stages/nasa_atmonto_answer_generation.md`, `reports/stages/nasa_atmonto_s7_answer_generation.md`, `reports/stages/nasa_atmonto_s7_llm_answer_generation.md` |
| Failure review | `reports/stages/nasa_atmonto_s7_llm_failure_review.md`, `reports/stages/nasa_atmonto_s7_candidate_adjudication.md`, `reports/stages/nasa_atmonto_s7_profile_decision.md` |
| SOTA/readiness audit | `reports/stages/nasa_atmonto_sota_goal_audit.md`, `reports/stages/current_pipeline_sota_gap_audit.md` |
