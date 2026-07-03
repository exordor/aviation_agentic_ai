# ATCSCC Thesis Report Outline

Status: outline for the current thesis route, not a completed manuscript.

Working title:

> Schema-Constrained Agentic KG-RAG for Evidence-Grounded Question Answering
> over FAA ATCSCC Advisories

## Source Spine

Use these documents as the primary source chain:

1. `docs/thesis_positioning.md`
2. `docs/research_mainline.md`
3. `docs/experiment_protocol.md`
4. `docs/experiment_protocol.md`
5. `reports/stages/atcscc_data_format_and_processing_flow.md`
6. `reports/stages/atcscc_ontology_profile_overview.md`
7. `reports/stages/thesis_experiment_dashboard.md`
8. `reports/stages/nasa_atmonto_reviewer_defense_audit.md`
9. `reports/stages/nasa_atmonto_sota_goal_audit.md`

## Core Claim

This thesis evaluates a retrospective, source-bounded Agentic KG-RAG pipeline
for FAA ATCSCC advisories. NASA ATMONTO-derived terms are used as a lightweight
application schema/profile to constrain event extraction, validation, and graph
construction. The contribution is not a complete aviation ontology. The
contribution is a reproducible workflow for schema-constrained extraction,
evidence-linked advisory event graphs, agentic validation/refinement, and
source-grounded KG-RAG evaluation.

## Chapter Structure

| Chapter | Purpose | Primary evidence |
| --- | --- | --- |
| 1. Introduction | Define the problem, motivation, scope, and contribution. | `docs/thesis_positioning.md`, `docs/research_mainline.md` |
| 2. Background and Related Work | Position against ontology-guided extraction, KG quality, GraphRAG, and multi-agent validation. | `reports/stages/agentic_ontology_graphrag_mainline_literature_search.md`, `reports/stages/sota_comparison_matrix.md`, paper-analysis reports |
| 3. Data and Task Definition | Explain FAA ATCSCC advisories, source format, frozen snapshot, and source-family boundary. | `reports/stages/atcscc_data_format_and_processing_flow.md`, `reports/stages/atcscc_source_brief.md` |
| 4. Application Schema/Profile | Explain why the full ATMONTO ontology is not used wholesale and how the ATCSCC profile constrains extraction. | `reports/stages/atcscc_ontology_profile_overview.md`, `reports/stages/nasa_atmonto_competency_questions.md` |
| 5. Method | Present the end-to-end pipeline: source parser, schema-constrained extractor, validator/refiner/critic loop, event graph, vector/graph/hybrid retrieval, answer verifier. | `docs/experiment_protocol.md`, `reports/stages/atcscc_agentic_artifact_contract.md` |
| 6. Evaluation Design | Define RQs, baselines, metrics, pass/fail gates, and no-overall-score policy. | `docs/research_mainline.md`, `docs/experiment_protocol.md` |
| 7. Results | Report extraction, agentic loop, retrieval, answer generation, and failure-review results separately. | `reports/stages/thesis_experiment_dashboard.md`, S0-S7 stage reports |
| 8. Discussion | Explain what the results support, what remains weak, and why negative/diagnostic results matter. | `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_sota_goal_audit.md` |
| 9. Threats to Validity | Separate source-boundary, schema-boundary, gold-review, automated-review, and operational-boundary limitations. | `docs/thesis_positioning.md`, reviewer-defense audit |
| 10. Conclusion | Summarize contribution and future work without overclaiming ontology completeness, domain generality, or live operational use. | `docs/research_mainline.md` |

## Research Questions And Evidence

| RQ | Short wording | Main report evidence |
| --- | --- | --- |
| RQ1 | Can schema-constrained extraction produce valid and evidence-linked event records? | `nasa_atmonto_formal_experiment_scoring.md`, `nasa_atmonto_prediction_output_validation.md`, `nasa_atmonto_cq_evaluation.md` |
| RQ2 | Does an agentic validation-refinement loop reduce schema violations and unsupported relations? | `nasa_atmonto_s5_s6_live_agentic_full_run.md`, `nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md` |
| RQ3 | Does KG-RAG improve evidence grounding and citation quality compared with vector-only RAG? | `nasa_atmonto_s7_retrieval.md`, `nasa_atmonto_s7_graph_health.md`, `nasa_atmonto_s7_llm_answer_generation.md` |
| RQ4 | What failure types remain, and where is human review still necessary? | `nasa_atmonto_s7_candidate_adjudication.md`, `nasa_atmonto_s7_profile_decision.md`, `nasa_atmonto_reviewer_defense_audit.md` |

## Required Figures

| Figure | Message | Source |
| --- | --- | --- |
| F1: System overview | ATCSCC advisories flow through schema-constrained extraction, agentic validation, event graph construction, and KG-RAG evaluation. | `docs/research_mainline.md` |
| F2: Data format example | ATCSCC is semi-structured: title/header, message block, effective time, signature. | `reports/stages/atcscc_data_format_and_processing_flow.md` |
| F3: Schema/profile boundary | Full NASA ATMONTO is sliced into an ATCSCC application profile and runtime extraction schema. | `reports/stages/atcscc_ontology_profile_overview.md` |
| F4: Agentic loop | Extractor, validator, refiner, and critic exchange structured artifacts under evidence gates. | `reports/stages/atcscc_agentic_artifact_contract.md` |
| F5: Evaluation stack | Extraction metrics, agentic-loop metrics, retrieval/answer metrics, and review-boundary metrics stay separate. | `docs/experiment_protocol.md` |

## Required Tables

| Table | Purpose | Source |
| --- | --- | --- |
| T1: RQ to validation matrix | Show experiment layer, baselines, metrics, artifacts, and pass/fail criteria. | `docs/research_mainline.md` |
| T2: ATCSCC source fields to profile terms | Defend source-observable completeness and profile scope. | `reports/stages/atcscc_data_format_and_processing_flow.md`, `reports/stages/atcscc_ontology_profile_overview.md` |
| T3: Baseline comparison | Compare S0-S7 extraction and KG-RAG systems without one mixed overall score. | `reports/stages/thesis_experiment_dashboard.md` |
| T4: Claim safety matrix | Safe wording versus unsafe wording. | `docs/thesis_positioning.md`, `reports/stages/nasa_atmonto_reviewer_defense_audit.md` |

## Claims To Preserve

- The system is retrospective and source-bounded.
- The ATCSCC profile is a lightweight application schema, not a full aviation
  ontology.
- Accepted facts require source IDs and evidence spans.
- Agentic validation/refinement is evaluated as an auditable repair loop, not
  autonomous ontology construction.
- KG-RAG is evaluated as structured grounding and citation support, not a
  universal retrieval winner.
- Human/expert review and live operational validation remain separate from
  automated diagnostics.

## Claims To Avoid

- The project builds or verifies a complete aviation ontology.
- NASA ATMONTO is complete ground truth for ATCSCC advisories.
- GraphRAG universally outperforms vector retrieval.
- Automated adversarial review replaces human or domain-expert review.
- The system is safe for live ATC, dispatch, or flight decision support.
- The method is proven domain-general from the current ATCSCC case study.
