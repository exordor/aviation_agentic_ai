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
| rag_experiments | 12 |
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
- Evidence-level evaluation: `reports/stages/evidence_level_evaluation.md`
- Web demo readiness: `reports/stages/web_demo_readiness.md`

## Current Experiment Snapshot

- Chunking comparison best strategy: `structure_aware` by Recall@5/MRR@5/Context Precision@5.
- Baseline Hybrid RAG strategy: `fixed_window`, because the first validated KG uses fixed-window chunk ids.
- Structure-aware Hybrid RAG strategy: `structure_aware`, with independently extracted KG and collection `phak_ch4_chunks_structure_aware`.
- Fixed-window result summary: vector Recall@5 = 1.0, graph Recall@5 = 0.8, hybrid Recall@5 = 0.9; graph and hybrid KG evidence coverage = 0.9.
- Structure-aware result summary: vector Recall@5 = 1.0, graph Recall@5 = 0.9, hybrid Recall@5 = 1.0; graph and hybrid KG evidence coverage = 0.9.
- Evidence-level result summary: structure-aware hybrid supported 9/10 answers versus fixed-window hybrid 7/10; both hybrid runs have KG triple relevance = 0.9.
- Web demo default strategy: `structure_aware`; live query is disabled by default for reproducible review.
- Web demo KG visualization: question-scoped graph renders retrieved KG triples for the selected CQ, strategy, and retrieval mode.

## Project Tracking

- Goals: `GOALS.md`
- Task board: `TASKS.md`
