# Stage Report Index

This directory is the current report dashboard. Detailed stage artifacts are archived under `reports/archive/stages/2026-05-18`.

## Summary

- Archived stage artifacts: 23
- Review source artifacts: 2
- Archive policy: archive_without_delete

## Categories

| Category | Items |
| --- | ---: |
| generation_runs | 3 |
| kg_validation | 2 |
| ontology_evaluation | 10 |
| ontology_stats | 2 |
| rag_experiments | 24 |
| reviews | 4 |
| source_scope | 4 |
| stage_summaries | 2 |

## Final Report

- Draft: `reports/final/project_report.md`
- Sources: `reports/final/project_report_sources.json`

## Current Active Artifacts

- Active ontology: `data/ontology/curated/06_phak_ch4_0.curated.ttl`
- Ontology design: `docs/ontology_design.md`
- Curated ontology evaluation: `reports/stages/curated_ontology_evaluation.md`
- Validated KG: `data/kg/06_phak_ch4_0.kg.jsonl`
- KG TTL export: `data/kg/06_phak_ch4_0.kg.ttl`
- KG validation report: `reports/stages/kg_validation.md`
- Chunking comparison: `reports/stages/chunking_comparison.md`
- Hybrid RAG experiment: `reports/stages/hybrid_rag_experiment.md`
- Structure-aware KG: `data/kg/06_phak_ch4_0.structure_aware.kg.jsonl`
- Structure-aware KG TTL export: `data/kg/06_phak_ch4_0.structure_aware.kg.ttl`
- Structure-aware KG validation report: `reports/stages/structure_aware_kg_validation.md`
- Structure-aware Hybrid RAG experiment: `reports/stages/hybrid_rag_structure_aware.md`
- GraphRAG review: `reports/stages/graphrag_review.md`
- Gold labels: `data/cqs/06_phak_ch4_0.gold.json`
- Expanded gold labels: `data/cqs/06_phak_ch4_0.expanded.gold.json`
- Evidence-level evaluation: `reports/stages/evidence_level_evaluation.md`
- Retrieval ablation: `reports/stages/retrieval_ablation.md`
- KG extraction comparison: `reports/stages/kg_extraction_comparison.md`
- Answer evaluation: `reports/stages/answer_evaluation.md`
- Robustness evaluation: `reports/stages/robustness_evaluation.md`
- Final evaluation review: `reports/stages/final_evaluation_review.md`
- Web demo readiness: `reports/stages/web_demo_readiness.md`
- Web demo final smoke: `reports/stages/web_demo_final_smoke.md`
- Academic report: `reports/final/project_academic_report.md`
- Project defense notes: `reports/final/project_defense_notes.md`
- Defense deck outline: `reports/final/defense_deck_outline.md`
- Defense deck: `reports/final/aviation_graphrag_defense_deck.pptx`
- AI visual assets with local SVG fallbacks: `reports/final/assets/visual_assets_manifest.json`

## Current Experiment Snapshot

- Chunking comparison best strategy: `structure_aware` by Recall@5/MRR@5/Context Precision@5.
- Baseline Hybrid RAG strategy: `fixed_window`, because the first validated KG uses fixed-window chunk ids.
- Structure-aware Hybrid RAG strategy: `structure_aware`, with independently extracted KG and collection `phak_ch4_chunks_structure_aware`.
- Fixed-window result summary: vector Recall@5 = 1.0, graph Recall@5 = 0.8, hybrid Recall@5 = 0.9; graph and hybrid KG evidence coverage = 0.9.
- Structure-aware result summary: vector Recall@5 = 1.0, graph Recall@5 = 0.9, hybrid Recall@5 = 1.0; graph and hybrid KG evidence coverage = 0.9.
- Gold labels: reviewed chunk/span labels are marked `manual_reviewed`; they remain course-project gold, not external aviation examiner certification.
- Evidence-level result summary: structure-aware hybrid supported 9/10 answers versus fixed-window hybrid 8/10; both hybrid runs have KG triple relevance = 0.9 and citation validity = 1.0.
- Expanded evaluation labels: 35 total questions, including 5 insufficient-evidence/no-answer questions for abstention testing.
- Retrieval ablation: 12 deterministic scenarios over 35 expanded questions; vector-only and explicit graph-disabled hybrid Recall@5 = 0.6857, while structure-aware hybrid RRF Recall@5 = 0.6286 in the default top-k/hops setting, showing the expanded set is harder than the original 10 CQ benchmark.
- KG extraction comparison: structure-aware KG has 448 validated triples versus 172 fixed-window triples; key-entity coverage is 0.8571 versus 0.8286, with higher duplicate count that should be discussed as cost/noise.
- Answer evaluation: existing 10-CQ structure-aware hybrid answers have citation completeness = 1.0, citation correctness = 0.9, answer faithfulness = 0.9, and zero advisory-boundary violations.
- Robustness benchmark: 10 paraphrase/terminology/cross-page/unsupported cases; deterministic retrieval-only robustness has retrieval stability = 0.8, citation stability = 0.7, and abstention correctness = 0.6.
- Final evaluation decision: `structure_aware` is the default demo and next-phase GraphRAG strategy; `fixed_window` remains the baseline.
- Web demo default strategy: `structure_aware`; live query is disabled by default for reproducible review.
- Web demo KG visualization: question-scoped graph renders retrieved KG triples for the selected CQ, strategy, and retrieval mode.
- Web demo explanation layer: narrative, pipeline steps, mode comparison, and Why This Result explain the demo without reading raw reports.
- Web demo final smoke: FastAPI TestClient static/API checks passed for the root page, status, explanation, questions, detail, KG graph, live-query lockout, and favicon.
- Academic deliverables: deterministic paper-style report, defense Q&A notes, local SVG diagrams, and editable defense PPTX are available under `reports/final/`.
- Visual asset policy: current diagrams are local deterministic SVGs and do not call the configured LLM or image gateway.

## Project Tracking

- Goals: `GOALS.md`
- Task board: `TASKS.md`
