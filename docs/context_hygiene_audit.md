# Documentation Scope Audit

This audit identifies which documents should control the current thesis route
and which documents should remain historical background. Its purpose is to keep
legacy PHAK-era and broad ontology material from overriding the current ATCSCC
schema-constrained Agentic KG-RAG framing.

## Current Default Framing

The current research line is:

> Agentic KG-RAG for evidence-grounded question answering over retrospective
> FAA ATCSCC advisories.

The project should be described as schema-constrained, evidence-grounded
advisory-event extraction and KG-RAG evaluation. It should not be described as
a full aviation ontology-construction thesis or a live ATC decision-support
system.

## Primary Reading Set

Use these files first for thesis writing, review, and report generation.

| Role | Files |
| --- | --- |
| Navigation | `docs/documentation_map.md`, `docs/documentation_maintenance.md` |
| Thesis scope and claims | `docs/thesis_positioning.md`, `docs/research_mainline.md` |
| Experiment workflow and metrics | `docs/experiment_workflow.md`, `docs/evaluation_protocol.md`, `docs/experiment_protocol.md` |
| Data and schema boundary | `reports/stages/atcscc_data_format_and_processing_flow.md`, `reports/stages/atcscc_source_brief.md`, `reports/stages/atcscc_ontology_profile_overview.md`, `reports/stages/atcscc_semantic_requirements.md` |
| Current evidence synthesis | `reports/stages/thesis_experiment_dashboard.md`, `reports/stages/nasa_atmonto_sota_goal_audit.md`, `reports/stages/nasa_atmonto_reviewer_defense_audit.md` |
| Final-package entry points | `reports/final/README.md`, `reports/final/atcscc_thesis_report_outline.md`, `reports/final/atcscc_defense_deck_outline.md` |

## Secondary Reading Set

These files may still be useful, but they should not be treated as the current
research narrative without checking the current framing documents first.

| File or family | Context risk | Safe use |
| --- | --- | --- |
| `reports/final/project_report.md` | Transitional report that still carries aviation-training / PHAK framing. | Reuse isolated sections only after manual rewrite into ATCSCC wording. |
| `reports/stages/index.md` | Artifact inventory with many legacy report links. | Navigation only, not thesis story. |
| `reports/stages/current_pipeline_sota_gap_audit.md` | Useful SOTA gap audit, but may refer to earlier pipeline state. | Use for gap framing after checking latest dashboard and reviewer audit. |
| `docs/nasa_atmonto_experiment_design.md` | Transitional document from the PHAK route toward NASA ATMONTO. It predates the current low-pressure ATCSCC schema-constrained framing. | Use for historical motivation only after checking `docs/research_mainline.md`. |
| `reports/stages/data_source_extraction_method_matrix.md` | Mixes source-family comparison with historical PHAK baseline. | Use for source-family policy, not as current experiment evidence. |
| `reports/stages/sota_data_source_format_processing_review.md` | Useful data-format review, but not a replacement for current ATCSCC source docs. | Use as supporting literature-method context. |
| `reports/stages/*paper_analysis.md`, `*_figures_analysis.md`, `*_paper_adaptation.md` | Method inspiration may be domain-agnostic and not directly validated in ATCSCC. | Use for related work and design migration only. |

## Historical Background

The following documents are likely to pollute future context if loaded
uncritically. They are historical or secondary artifacts, not current thesis
entry points.

| Document or family | Why it is risky |
| --- | --- |
| `docs/ontology_design.md` | Presents a PHAK Chapter 4 curated ontology as the active ontology. |
| `docs/benchmark_design.md` | Presents the PHAK Chapter 4 benchmark as the main retrieval/safety benchmark. |
| `docs/document_expansion_protocol.md` | Restricts expansion around PHAK Chapter 4 and old source policy. |
| `docs/chunking_experiment_protocol.md` | Focuses on PHAK chunking experiments rather than ATCSCC advisory events. |
| `docs/benchmark_manual_review_protocol.md` | Defines PHAK benchmark review rather than ATCSCC event-fact review. |
| `docs/heuristic_detection_failure_analysis.md` | Documents old PDF extraction heuristics and PHAK failure modes. |
| `docs/nasa_aerodynamics_source_scope.md` | NASA BGA transfer/source-scope material, not the current ATCSCC mainline. |
| `docs/ontology_boundary_nasa.md` and `reports/stages/ontology_boundary_nasa.md` | Old PHAK/NASA ontology-boundary framing. |
| `docs/pdf_extraction_backend_policy.md` | PDF/chunking support policy; useful tooling context but not thesis framing. |
| `reports/final/project_academic_report.md` | Historical PHAK-era final draft. |
| `reports/final/project_defense_notes.md` | Historical PHAK-era defense notes. |
| `reports/final/defense_deck_outline.md` | Historical PHAK-era deck outline. |
| `reports/stages/benchmark_*`, `chunking_*`, `hybrid_rag_*`, `retrieval_ablation*`, `graph_traversal_ablation*`, `graphrag_review.*`, `kg_validation.*`, `evidence_level_evaluation.*`, `web_demo_*`, `pdf_*` | Old PHAK/web-demo/chunking/retrieval experiment families. Preserve for provenance, but do not use as current claim evidence. |
| `reports/stages/nasa_bga_*`, `reports/stages/nasa_source_*`, `reports/stages/nasa_ontology_extension_proposal.md` | NASA BGA or transfer-pilot material. Use only as transfer or source-expansion context. |

## Reading Rules

1. Start every thesis-writing, review, or experiment-planning task from
   `docs/documentation_map.md`, not from `reports/stages/index.md`.
2. If a document says PHAK, handbook, aviation training, Chapter 4, web demo,
   or curated ontology as the main object, classify it as historical unless a
   current ATCSCC document explicitly links it.
3. Keep ATCSCC advisories, FAA/NASA reference PDFs, NASR/facility data, weather
   data, and transfer-pilot data as separate source families.
4. Do not merge source families into one extraction metric table unless a
   source-specific profile and gold/evaluation protocol exist for each family.
5. Treat completeness and correctness as task-relative:
   - CQ coverage: whether each current CQ has a queryable schema path.
   - Source-observable completeness: whether explicit ATCSCC fields map to
     schema targets.
   - Evaluation completeness: whether reviewed gold event types are
     expressible or recorded as profile gaps.
   - Correctness: whether accepted facts are schema-valid and evidence-backed
     on the reviewed subset.
6. Paper-analysis files can motivate methods, but they cannot replace current
   ATCSCC evidence, gold review, or SOTA/reviewer-defense audits.

## Starting Point For New Work

For new documentation or experiment-planning work, begin with
`docs/documentation_map.md` and this scope audit. The current framing is
schema-constrained, evidence-grounded Agentic KG-RAG over retrospective FAA
ATCSCC advisories. Treat PHAK, web-demo, and chunking-era reports as historical
unless the task explicitly requests historical comparison. Keep source families
and evaluation layers separate.
