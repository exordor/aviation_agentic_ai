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
| ontology_evaluation | 10 |
| ontology_stats | 2 |
| rag_experiments | 4 |
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

## Current Experiment Snapshot

- Chunking comparison best strategy: `structure_aware` by Recall@5/MRR@5/Context Precision@5.
- Current Hybrid RAG strategy: `fixed_window`, because the validated KG uses fixed-window chunk ids.
- Fixed-window Chroma collection: `phak_ch4_chunks` under local ignored path `data/indexes/chroma`.
- Hybrid result summary: vector Recall@5 = 1.0, graph Recall@5 = 0.8, hybrid Recall@5 = 0.9; graph and hybrid KG evidence coverage = 0.9.

## Project Tracking

- Goals: `GOALS.md`
- Task board: `TASKS.md`
