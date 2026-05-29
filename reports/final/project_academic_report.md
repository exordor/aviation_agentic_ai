# Aviation Agentic AI: Ontology-Constrained GraphRAG for Aviation Learning

## Abstract

This project builds a reproducible aviation-domain GraphRAG prototype over FAA PHAK Chapter 4. The system converts a PDF into chunks, constrains KG extraction with an explainable curated ontology, builds vector and graph retrieval indexes, and reports grounded answers with citations. The current evidence shows that GraphRAG should be defended primarily as structured evidence support rather than as a single page-level Recall@5 improvement. Sources: `reports/stages/index.json`, `reports/stages/graphrag_review.json`.

Revised thesis claim: This thesis does not assume that GraphRAG universally improves retrieval Recall@k over vector-only RAG. Instead, it investigates a narrower and more safety-relevant claim: in aviation training question answering, an ontology-constrained GraphRAG pipeline can improve evidence traceability, structured KG evidence coverage, and insufficient-evidence abstention. The system is therefore evaluated with layered metrics: retrieval quality, KG evidence quality, answer citation quality, and safety-aware abstention are measured separately rather than collapsed into a single overall score.

## 1. Introduction

The course objective is to explain a full AI pipeline that can answer what the system does, why each design choice exists, and what evidence supports the claims. This implementation focuses on aviation learning and decision support, not operational flight authority. Sources: `GOALS.md`, `src/aviation_agentic_ai/advisory.py`.

## 2. Background and Research Gap

A vector-only RAG baseline can retrieve relevant pages, but it does not expose typed relations such as causes, affects, hasCondition, or supportedByEvidence. The project therefore uses an ontology-constrained KG to add interpretable evidence structure. Sources: `docs/ontology_design.md`, `configs/extraction_profile.yaml`.

## 3. Methodology

The implemented pipeline is PDF -> chunks -> curated ontology -> KG/ABox -> Chroma vector index -> graph/vector/hybrid retrieval -> grounded LLM answer -> layered evaluation report. The pipeline is CLI-first so that every major artifact can be regenerated and inspected. Sources: `README.md`, `configs/default.yaml`, `reports/final/project_report_sources.json`.

## 4. Explainable Ontology Design

The active ontology is `data/ontology/curated/06_phak_ch4_0.curated.ttl` and its design rationale is `docs/ontology_design.md`. The curated ontology replaces the baseline as the main explainable schema because it is small enough to present, validates KG extraction, and supports GraphRAG relations.

Ontology metrics: classes=35, object properties=9, TBox-only=True, class label coverage=1.0. Source: `reports/stages/curated_ontology_evaluation.json`.

## 5. KG Construction and Validation

KG extraction is constrained by the curated ontology and extraction profile; triples require evidence and provenance. Fixed-window and structure-aware KG artifacts are kept separate to avoid mixing chunk-id schemas.

Fixed-window KG: triples=172, validation errors=0. Structure-aware KG: triples=448, validation errors=0. Sources: `reports/stages/kg_validation.json`, `reports/stages/structure_aware_kg_validation.json`.

## 6. Chunking Comparison

The chunking comparison ranks `structure_aware` first with Recall@5=1.0, MRR@5=0.82, and Context Precision@5=0.52. It uses 267 chunks versus 35 fixed-window chunks. Source: `reports/stages/chunking_comparison.json`.

The result is consistent with the document type: aviation handbooks have page, section, and list structure, so preserving structure improves retrieval granularity even when it increases index size.

## 7. Hybrid RAG and GraphRAG Evaluation

This section reports retrieval quality, KG evidence quality, answer citation quality, and safety-aware abstention separately. It does not use a single mixed overall score.

Fixed-window vector Recall@5=1.0 and fixed-window hybrid Recall@5=0.9; fixed-window hybrid KG evidence coverage=0.9. Structure-aware vector Recall@5=1.0 and structure-aware hybrid Recall@5=1.0; structure-aware hybrid KG evidence coverage=0.9. Sources: `reports/stages/hybrid_rag_experiment.json`, `reports/stages/hybrid_rag_structure_aware.json`.

Evidence-level scoring is more useful for defending GraphRAG: structure-aware hybrid supports 9 answers versus 8 for fixed-window hybrid. Source: `reports/stages/evidence_level_evaluation.json`.

## 8. Discussion

The main interpretation is that vector-only retrieval can remain competitive on coarse page-level gold labels, while GraphRAG contributes relation-level evidence coverage and provenance. This distinction prevents the evaluation from collapsing retrieval, KG evidence, answer quality, and abstention into one misleading score. Source: `reports/stages/graphrag_review.json`.

## 9. Limitations and Threats to Validity

The gold labels are reviewed for source alignment, but they remain course-project labels rather than external aviation examiner certification. The dataset is limited to PHAK Chapter 4. KG extraction depends on LLM structured output and therefore requires deterministic validation. Visual assets are explanatory presentation artifacts and must not be treated as experiment evidence.

## 10. Web Demonstrator

The web demo readiness report marks ready=True, default strategy=structure_aware, and explanation ready=True. The final smoke report marks ready=True. The demo presents answer evidence, KG triples, relationship graph, mode comparison, pipeline explanation, and advisory boundary. Sources: `reports/stages/web_demo_readiness.json`, `reports/stages/web_demo_final_smoke.json`.

## 10.1 Final Evaluation Decision

The final evaluation selects `structure_aware` as the default demo and next-phase GraphRAG strategy while keeping `fixed_window` as the baseline. Gold label review status is `manual_reviewed` with review_required=False. Source: `reports/stages/final_evaluation_review.json`.

## 11. Advisory Boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.

## 12. Conclusion

The project is ready to be presented as a reproducible, evidence-layered GraphRAG prototype. The strongest defensible claim is not that graph retrieval universally beats vector retrieval, but that ontology-constrained KG evidence makes retrieved answers more explainable and auditable in the aviation handbook setting.

## Reproducibility Appendix

- `uv run aviation-ai report chunking-comparison`
- `uv run aviation-ai report hybrid-rag`
- `uv run aviation-ai report hybrid-rag --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --collection-name phak_ch4_chunks_structure_aware --chunking-strategy structure_aware --report-name hybrid_rag_structure_aware`
- `uv run aviation-ai report graphrag-review`
- `uv run aviation-ai report evidence-eval`
- `uv run aviation-ai report final-evaluation`
- `uv run aviation-ai report web-demo-readiness`
- `uv run aviation-ai report web-demo-smoke`
- `uv run aviation-ai report thesis-claims`
- `uv run aviation-ai report academic-paper --no-ai`
- `uv run aviation-ai report defense-notes`
- `uv run aviation-ai report defense-deck-outline`

## Source Paths

- `GOALS.md`
- `README.md`
- `TASKS.md`
- `configs/default.yaml`
- `configs/extraction_profile.yaml`
- `configs/ontology_generation.yaml`
- `data/cqs/06_phak_ch4_0.expanded.gold.json`
- `data/cqs/06_phak_ch4_0.gold.json`
- `data/kg/06_phak_ch4_0.kg.jsonl`
- `data/kg/06_phak_ch4_0.kg.ttl`
- `data/kg/06_phak_ch4_0.structure_aware.kg.jsonl`
- `data/kg/06_phak_ch4_0.structure_aware.kg.ttl`
- `data/ontology/curated/06_phak_ch4_0.curated.ttl`
- `docs/document_expansion_protocol.md`
- `docs/ontology_design.md`
- `docs/thesis_positioning.md`
- `reports/final/assets/kg_evidence_ai.png`
- `reports/final/assets/pipeline_hero_ai.png`
- `reports/final/assets/project_cover_ai.png`
- `reports/final/assets/visual_assets_manifest.json`
- `reports/final/assets/web_demo_ai.png`
- `reports/final/aviation_graphrag_defense_deck.pptx`
- `reports/final/aviation_graphrag_defense_deck_sources.json`
- `reports/final/defense_deck_outline.md`
- `reports/final/project_academic_report.md`
- `reports/final/project_academic_report_sources.json`
- `reports/final/project_defense_notes.json`
- `reports/final/project_defense_notes.md`
- `reports/stages/answer_evaluation.json`
- `reports/stages/answer_evaluation.md`
- `reports/stages/chunking_comparison.json`
- `reports/stages/chunking_comparison.md`
- `reports/stages/curated_ontology_evaluation.json`
- `reports/stages/curated_ontology_evaluation.md`
- `reports/stages/evidence_level_evaluation.json`
- `reports/stages/evidence_level_evaluation.md`
- `reports/stages/final_evaluation_review.json`
- `reports/stages/final_evaluation_review.md`
- `reports/stages/graphrag_review.json`
- `reports/stages/graphrag_review.md`
- `reports/stages/hybrid_rag_experiment.json`
- `reports/stages/hybrid_rag_experiment.md`
- `reports/stages/hybrid_rag_structure_aware.json`
- `reports/stages/hybrid_rag_structure_aware.md`
- `reports/stages/index.json`
- `reports/stages/kg_extraction_comparison.json`
- `reports/stages/kg_extraction_comparison.md`
- `reports/stages/kg_validation.json`
- `reports/stages/kg_validation.md`
- `reports/stages/retrieval_ablation.json`
- `reports/stages/retrieval_ablation.md`
- `reports/stages/robustness_evaluation.json`
- `reports/stages/robustness_evaluation.md`
- `reports/stages/structure_aware_kg_validation.json`
- `reports/stages/structure_aware_kg_validation.md`
- `reports/stages/thesis_claims_review.json`
- `reports/stages/web_demo_final_smoke.json`
- `reports/stages/web_demo_final_smoke.md`
- `reports/stages/web_demo_readiness.json`
- `reports/stages/web_demo_readiness.md`
