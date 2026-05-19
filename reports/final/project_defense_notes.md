# Project Defense Notes

## 30-Second Summary

This project turns one aviation handbook chapter into a reproducible GraphRAG pipeline: curated ontology, validated KG, chunking comparison, vector/graph/hybrid retrieval, grounded answers, and a web demo that makes the evidence inspectable.

## Demo Script

1. Open the web demo and state the advisory boundary first.
2. Select a boundary CQ and show vector, graph, and hybrid evidence panels.
3. Use the KG Relationship Graph to explain what GraphRAG adds beyond retrieved text.
4. Use Why This Result to explain recall, KG coverage, and citation completeness.
5. Close by showing reports/final/project_academic_report.md and the reproducibility commands.

## Metrics Talking Points

- Chunking: structure-aware is currently best by retrieval ranking (Recall@5=1.0, MRR@5=0.82).
- Fixed-window Hybrid RAG should be described as KG-aligned baseline, with hybrid KG evidence coverage=0.9.
- Structure-aware Hybrid RAG is the stronger current candidate: hybrid Recall@5=1.0 and supported answers=9.

## Likely Questions

### What is the ontology for?

It defines a compact, explainable schema for aviation-domain concepts and relations, so KG extraction can be validated and GraphRAG evidence can be explained.

Sources: `docs/ontology_design.md`, `reports/stages/curated_ontology_evaluation.json`

### Why not use the generated baseline ontology as the main one?

The baseline is useful historical evidence, but it is too complex to defend clearly. The curated ontology is smaller, modular, and aligned with KG extraction properties.

Sources: `docs/ontology_design.md`

### What does GraphRAG add if vector retrieval already has high Recall@5?

The value is structured KG evidence coverage and provenance. Current page-level Recall@5 is coarse, so vector retrieval can score well by retrieving any chunk from the right page.

Sources: `reports/stages/graphrag_review.json`, `reports/stages/evidence_level_evaluation.json`

### Why is structure-aware chunking recommended?

It preserves handbook structure and currently ranks first on retrieval quality; it also improves evidence-level answer support in the structure-aware Hybrid RAG run.

Sources: `reports/stages/chunking_comparison.json`, `reports/stages/evidence_level_evaluation.json`

### What is still weak?

Gold labels are reviewed for source alignment but are not external aviation examiner certification; the corpus is still only PHAK Chapter 4, and LLM extraction must remain validator-gated.

Sources: `data/cqs/06_phak_ch4_0.gold.json`, `reports/stages/final_evaluation_review.json`, `reports/stages/evidence_level_evaluation.json`

### Can this replace POH, checklist, ATC, instructor, or pilot judgment?

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.

Sources: `src/aviation_agentic_ai/advisory.py`

## Failure Cases

- **Coarse page-level gold can understate GraphRAG value.** Graph evidence may be relevant but off the gold source page, so page Recall@5 can penalize useful structured evidence. Sources: `reports/stages/graphrag_review.json`
- **KG evidence can fail even when retrieval succeeds.** Some CQs retrieve relevant text but lack extracted triples covering the key entity; this is a KG extraction and schema coverage issue. Sources: `reports/stages/evidence_level_evaluation.json`

## Source Paths

- `GOALS.md`
- `README.md`
- `TASKS.md`
- `configs/default.yaml`
- `configs/extraction_profile.yaml`
- `configs/ontology_generation.yaml`
- `data/cqs/06_phak_ch4_0.gold.json`
- `data/kg/06_phak_ch4_0.kg.jsonl`
- `data/kg/06_phak_ch4_0.kg.ttl`
- `data/kg/06_phak_ch4_0.structure_aware.kg.jsonl`
- `data/kg/06_phak_ch4_0.structure_aware.kg.ttl`
- `data/ontology/curated/06_phak_ch4_0.curated.ttl`
- `docs/ontology_design.md`
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
- `reports/stages/kg_validation.json`
- `reports/stages/kg_validation.md`
- `reports/stages/structure_aware_kg_validation.json`
- `reports/stages/structure_aware_kg_validation.md`
- `reports/stages/web_demo_final_smoke.json`
- `reports/stages/web_demo_final_smoke.md`
- `reports/stages/web_demo_readiness.json`
- `reports/stages/web_demo_readiness.md`
