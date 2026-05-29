# Aviation Agentic AI Project Report

## Project motivation and course objective alignment

This project investigates a reproducible aviation-domain RAG pipeline that turns FAA training text into ontology, KG, retrieval, and grounded-answer artifacts. Course goal evidence: `GOALS.md` (present).

## Thesis claim positioning

This thesis does not assume that GraphRAG universally improves retrieval Recall@k over vector-only RAG. Instead, it investigates a narrower and more safety-relevant claim: in aviation training question answering, an ontology-constrained GraphRAG pipeline can improve evidence traceability, structured KG evidence coverage, and insufficient-evidence abstention. The system is therefore evaluated with layered metrics: retrieval quality, KG evidence quality, answer citation quality, and safety-aware abstention are measured separately rather than collapsed into a single overall score.

Thesis positioning evidence: `docs/thesis_positioning.md` (present); claim review evidence: `reports/stages/thesis_claims_review.md` (present).

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
Structure-aware KG artifact: `data/kg/06_phak_ch4_0.structure_aware.kg.jsonl`. Triples=448; validation errors=0. It is kept separate from the fixed-window KG to avoid mixing chunk-id schemas.

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
Structure-aware Hybrid RAG evidence: `reports/stages/hybrid_rag_structure_aware.md`. It evaluated 10 boundary CQs with hybrid Recall@5=1.0, KG evidence coverage=0.9, and lift vs vector Recall@5=0.0.
GraphRAG interpretation evidence: `reports/stages/graphrag_review.md` explains retrieval, KG evidence, and LLM answer behavior separately.
Evidence-level evaluation: `reports/stages/evidence_level_evaluation.md` shows structure-aware hybrid span hit rate=0.7 and supported answers=9; fixed-window hybrid span hit rate=0.9 and supported answers=8.

## Current results and limitations

Current evidence now covers the explainable curated ontology, fixed-window KG, structure-aware KG, chunking comparison, fixed-window Hybrid RAG, structure-aware Hybrid RAG, and GraphRAG review when their reports are present in the stage index.
Web demo readiness: ready=True, default strategy=structure_aware.
The web demo is an offline-first FastAPI interface with a macOS-style sidebar, toolbar controls, answer workspace, chunk evidence, KG triple evidence, KG relationship graph, pipeline explanation, mode comparison, Why This Result panel, and advisory boundary display.
Web explanation readiness: ready=True, default path=structure_aware + hybrid, recommended strategy=structure_aware.
Final evaluation review: default strategy=structure_aware, baseline=fixed_window, gold review status=manual_reviewed, review required=False.
Web demo smoke: ready=True for static/API checks.
Expanded evaluation labels: 35 questions, including 5 insufficient-evidence/no-answer cases.
Retrieval ablation: 12 scenarios over 35 questions; vector Recall@5=0.6857, graph-disabled hybrid Recall@5=0.6857, and default hybrid Recall@5=0.6286.
KG extraction comparison: fixed-window valid triples=172 with key-entity coverage=0.8286; structure-aware valid triples=448 with key-entity coverage=0.8571.
Answer evaluation: hybrid citation completeness=1.0, citation correctness=0.9, answer faithfulness=0.9, advisory-boundary violations=0.
Robustness evaluation: retrieval stability=0.8, citation stability=0.7, abstention correctness=0.6.
Limitations: chunk/span gold labels are reviewed for source alignment but are not external aviation examiner certification, structure-aware KG extraction is more expensive because it uses many smaller chunks, and GraphRAG should be defended as structured evidence support rather than a single-score Recall improvement.

## Advisory assistant boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.

## Next work plan

1. Run final quality gates and keep the repository ready for submission.
2. Add GitLab CI for `ruff` and `pytest` if automated checks are required.
3. Optionally mirror the remaining P3 tasks into GitLab issues.
4. Expand beyond PHAK Chapter 4 only after document metadata and section schema are enforced.

## Reproducibility appendix

- `uv run aviation-ai report chunking-comparison`
- `uv run aviation-ai index build`
- `uv run aviation-ai report hybrid-rag`
- `uv run aviation-ai kg extract --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --output data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --ttl-output data/kg/06_phak_ch4_0.structure_aware.kg.ttl`
- `uv run aviation-ai kg validate --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --output-dir reports/stages --report-name structure_aware_kg_validation`
- `uv run aviation-ai index build --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --collection-name phak_ch4_chunks_structure_aware`
- `uv run aviation-ai report hybrid-rag --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --collection-name phak_ch4_chunks_structure_aware --chunking-strategy structure_aware --report-name hybrid_rag_structure_aware`
- `uv run aviation-ai report graphrag-review`
- `uv run aviation-ai cqs gold-draft`
- `uv run aviation-ai report evidence-eval`
- `uv run aviation-ai report web-demo-readiness`
- `uv run aviation-ai web serve`
- `uv run aviation-ai report web-demo-smoke`
- `uv run aviation-ai report final-evaluation`
- `uv run aviation-ai report thesis-claims`
- `uv run aviation-ai report hygiene --apply`
- `uv run aviation-ai report project --no-ai`
- `uv run aviation-ai report project --ai`

## Evidence Sources

- Stage index: `reports/stages/index.json` (present)
- README: `README.md` (present)
- Goal: `GOALS.md` (present)
- Thesis positioning: `docs/thesis_positioning.md` (present)
- Configs: `configs/default.yaml`, `configs/ontology_generation.yaml`, `configs/extraction_profile.yaml`
