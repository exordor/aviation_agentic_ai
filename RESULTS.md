# Results

> **Historical and optional evaluation ledger.** The rows below report earlier
> extraction, alignment, cross-source, and KG-RAG experiments. They do not
> define current `main` capabilities. Current system status is documented in
> `RESEARCH_AUDIT.md`, `README.md`, and `GOALS.md`.
>
> Migrated on 2026-07-05 and updated on 2026-07-13 for the then-current
> cross-source V2 study. Observations remain layer-specific; engineering
> conformance is not presented as independently reviewed semantic correctness.

## Deliverables And Evidence

| Deliverable | Observation | Evidence (artifact) | Interpretation | Confidence |
|---|---|---|---|---|
| Frozen ATCSCC data profile | Source family and format are documented and frozen. | `reports/stages/atcscc_data_format_and_processing_flow.md` | Defines the retrospective corpus and source-record shape. | high |
| Lightweight ATCSCC schema/profile | Application schema constrains accepted event fields and predicates; profile gaps documented. | `reports/stages/atcscc_ontology_profile_overview.md` | Engineering constraint, not full ontology. | high |
| Versioned authority/source snapshots | Cross-source configuration records versions, effective dates, source URLs, and checksums for terminology, facility, and weather inputs. | `configs/cross_source_v1.yaml`, `data/sources/faa_atcscc_terms_v1.yaml` | Reproducible source admission and refresh boundary. | high (process claim) |
| Autonomous two-layer alignment | The pinned 718-advisory run accepted 8,403 extracted mentions; 68 ambiguous `GS` mentions were context-aligned to `Ground Stop`. The 20-case hard challenge achieved 1.00 target and quarantine accuracy with zero out-of-registry acceptances. | `src/aviation_agentic_ai/cross_source/`, `data/evaluation/cross_source/v1/hard_ambiguity_v1.jsonl`, `reports/stages/cross_source_mainline_evaluation.md` | Supports the registered `GS` policy; not universal acronym disambiguation. | high (bounded challenge) |
| Controlled cross-source linking | The admitted 68-record cohort produced 1,475 typed cross-source links. | cross-source workflow artifacts, `data/evaluation/cross_source/v1/automated_regression_v1.jsonl` | Association and temporal co-occurrence links; not evidence of causation. | medium |
| Matched cross-source answer evaluation | Required evidence/citation-layer coverage is 0.25 source-only, 0.75 linked-text, and 1.00 KG-layered; abstention accuracy is 1.00, causal-overstatement count is zero, and the independent Evaluation Agent passes 24/24. | `data/evaluation/cross_source/v1/automated_regression_v1.jsonl`, `reports/stages/cross_source_mainline_evaluation.md` | Supports typed evidence-contract benefit; not external expert certification or causal attribution. | high (component/process claim) |
| Neo4j inspection projection | The generated projection contains 9,486 nodes and 18,281 relationships with no duplicate canonical IDs or duplicate relationship endpoints in the checked export. | `docs/neo4j_visualization.md`, Neo4j export artifacts | Visual inspection surface; Neo4j is not the canonical research artifact or a new thesis claim. | high (engineering claim) |
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
| Cross-source alignment and answers | `data/evaluation/cross_source/`, `reports/stages/cross_source_mainline_evaluation.md` (generated by the mainline closure run) |
