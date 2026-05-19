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

RAG experiment artifacts listed: 0. Chunking comparison should discuss retrieval tradeoffs rather than collapse them into a single score.

## Hybrid RAG protocol and layered metrics

Hybrid RAG uses separate retrieval, KG evidence, and LLM answer metrics. Configured retrieval defaults include vector_top_k=5, graph_hops=2, and hybrid_top_k=8.

## Current results and limitations

Current results must be reported only when present in the evidence pack. Missing full-loop experiments should be labeled TBD / Not yet run.

## Advisory assistant boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.

## Next work plan

1. Run report hygiene to maintain a readable stage dashboard.
2. Run chunking comparison and Hybrid RAG experiments with recorded run manifests.
3. Refine gold labels from source-page to chunk/span evidence.
4. Use the AI report command to polish this deterministic draft.

## Reproducibility appendix

- `uv run aviation-ai report hygiene --apply`
- `uv run aviation-ai report project --no-ai`
- `uv run aviation-ai report project --ai`

## Evidence Sources

- Stage index: `reports/stages/index.json` (present)
- README: `README.md` (present)
- Goal: `tmp/goal.md` (present)
- Configs: `configs/default.yaml`, `configs/ontology_generation.yaml`, `configs/extraction_profile.yaml`
