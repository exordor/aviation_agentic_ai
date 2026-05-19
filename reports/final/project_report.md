# Aviation Agentic AI Project Report

## Project motivation and course objective alignment

This project investigates a reproducible aviation-domain RAG pipeline that turns FAA training text into ontology, KG, retrieval, and grounded-answer artifacts. Course goal evidence: `tmp/goal.md` (present).

## Architecture overview

The implementation is CLI-first and separates ontology, KG extraction, chunking, retrieval, evaluation, and reporting modules. Primary configuration evidence is `configs/default.yaml`, `configs/ontology_generation.yaml`, and `configs/extraction_profile.yaml`.

## Ontology/TBox generation and evaluation

The active ontology is `data/ontology/curated/06_phak_ch4_0.curated.ttl`, with design rationale in `docs/ontology_design.md`. It replaces the historical baseline as the explainable schema used for KG extraction.
Curated ontology metrics: triples=188, classes=35, object_properties=9, TBox-only=True, label coverage=1.0.
Ontology judgment: valid TBox prototype=True, publication-ready=False.
Historical ontology evaluation artifacts indexed: 10.

## KG/ABox extraction and validation

The KG stage is designed around focused triples with provenance and deterministic validation against the extraction profile.
Validated KG artifact: `data/kg/06_phak_ch4_0.kg.jsonl`. Triples=172; validation errors=0; ontology constraint=`data/ontology/curated/06_phak_ch4_0.curated.ttl`.

## Chunking comparison design

Chunking comparison evidence: `reports/stages/chunking_comparison.md`. It evaluated 10 boundary CQs across 4 strategies.
Best chunking strategy: structure_aware with Recall@5=1.0, MRR@5=0.82, and Context Precision@5=0.52.
Fixed-window remains the KG-aligned strategy for the current Hybrid RAG run: Recall@5=1.0, MRR@5=0.7583, Context Precision@5=0.42, chunks=35.
Interpretation: structure_aware improves ranking quality and context precision by preserving handbook structure, but its finer granularity increases chunk count to 267. It is a candidate for future KG re-extraction rather than being mixed with the current fixed-window KG.

## Hybrid RAG protocol and layered metrics

Hybrid RAG evidence: `reports/stages/hybrid_rag_experiment.md`. It evaluated 10 boundary CQs using `fixed_window` chunks, collection `phak_ch4_chunks`, and LLM openai/gpt-5.4-mini.
Retrieval metrics: vector Recall@5=1.0, graph Recall@5=0.8, hybrid Recall@5=0.9; vector MRR@5=0.7583, graph MRR@5=0.65, hybrid MRR@5=0.7533.
KG evidence metrics: graph coverage=0.9, hybrid coverage=0.9, hybrid provenance complete=1.0, hybrid invalid triples=0.0.
LLM answer metrics: vector citation completeness=1.0, graph=1.0, hybrid=1.0; hybrid insufficient-evidence abstention=0.0.
Hybrid lift is reported as layered evidence, not a mixed total score: vs vector Recall@5=-0.1, vs graph Recall@5=0.1.

## Current results and limitations

Current evidence now covers the explainable curated ontology, validated KG, chunking comparison, and fixed-window Hybrid RAG loop when their reports are present in the stage index.
Limitations: gold labels are still source-page level, the current KG is aligned to fixed-window chunks, and the Hybrid RAG run improved graph recall but did not beat vector-only Recall@5 on this coarse benchmark.

## Advisory assistant boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.

## Next work plan

1. Review the chunking and Hybrid RAG reports for project-defense claims.
2. Decide whether to re-extract the KG with `structure_aware` chunks.
3. Refine gold labels from source-page to chunk/span evidence.
4. Generate the AI-polished final report after review.
5. Implement the minimal web interface demonstrator.

## Reproducibility appendix

- `uv run aviation-ai report chunking-comparison`
- `uv run aviation-ai index build`
- `uv run aviation-ai report hybrid-rag`
- `uv run aviation-ai report hygiene --apply`
- `uv run aviation-ai report project --no-ai`
- `uv run aviation-ai report project --ai`

## Evidence Sources

- Stage index: `reports/stages/index.json` (present)
- README: `README.md` (present)
- Goal: `tmp/goal.md` (present)
- Configs: `configs/default.yaml`, `configs/ontology_generation.yaml`, `configs/extraction_profile.yaml`
