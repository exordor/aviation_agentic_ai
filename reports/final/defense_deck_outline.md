# Aviation GraphRAG Defense Deck Outline

- Presentation type: `structured_argument`
- Deck profile: `engineering-platform`
- Design: white academic technical deck, dark navy primary, sparse blue accents.

## Slide Spine

### 1. Ontology-constrained GraphRAG makes aviation handbook answers auditable

- Role: `title`
- Claim: The project turns PHAK Chapter 4 into an evidence-grounded GraphRAG demo.
- Visual: reports/final/assets/project_cover_ai.png
- Sources: `reports/stages/index.json`, `reports/final/project_academic_report.md`
- Speaker note: Open with the problem, the source document, and the advisory boundary.

### 2. The course goal is answered by a full evidence pipeline, not a single model call

- Role: `motivation`
- Claim: The project can explain what it does, why each component exists, and how results are evaluated.
- Visual: course objective and deliverable map
- Sources: `GOALS.md`, `TASKS.md`
- Speaker note: Frame the work as a reproducible research prototype.

### 3. The pipeline preserves traceability from PDF text to grounded answers

- Role: `method`
- Claim: Each answer can be traced through chunks, KG triples, retrieval mode, and citations.
- Visual: reports/final/assets/pipeline_hero_ai.png
- Sources: `README.md`, `configs/default.yaml`
- Speaker note: Walk left-to-right through the pipeline.

### 4. A curated ontology keeps the KG explainable enough to defend

- Role: `method`
- Claim: The active ontology has 35 classes and 9 object properties.
- Visual: ontology module diagram
- Sources: `docs/ontology_design.md`, `reports/stages/curated_ontology_evaluation.json`
- Speaker note: Explain why the baseline ontology is not the main narrative object.

### 5. KG extraction is useful only because every triple is validator-gated

- Role: `method`
- Claim: Fixed-window KG has 172 triples; structure-aware KG has 448 triples.
- Visual: reports/final/assets/kg_evidence_ai.png
- Sources: `reports/stages/kg_validation.json`, `reports/stages/structure_aware_kg_validation.json`
- Speaker note: Stress evidence/provenance validation rather than raw triple count.

### 6. Structure-aware chunking is the best current retrieval candidate

- Role: `result`
- Claim: Best strategy: structure_aware with Recall@5=1.0 and MRR@5=0.82.
- Visual: chunking comparison bar chart
- Sources: `reports/stages/chunking_comparison.json`
- Speaker note: Explain handbook structure, not just the metric ranking.

### 7. GraphRAG should be judged as structured evidence, not just page Recall

- Role: `result`
- Claim: Structure-aware hybrid Recall@5=1.0 and KG coverage=0.9.
- Visual: layered retrieval metric comparison
- Sources: `reports/stages/hybrid_rag_structure_aware.json`, `reports/stages/graphrag_review.json`
- Speaker note: Defend why a graph layer matters even when vector Recall is high.

### 8. Evidence-level scoring favors the structure-aware hybrid run

- Role: `result`
- Claim: Structure-aware hybrid supports 9 answers versus 8 for fixed-window hybrid.
- Visual: supported answer distribution
- Sources: `reports/stages/evidence_level_evaluation.json`
- Speaker note: Use this as the strongest experiment-level defense claim.

### 9. The web demo turns raw evidence into an inspectable explanation surface

- Role: `demo`
- Claim: Readiness=True; default strategy=structure_aware; smoke=True.
- Visual: reports/final/assets/web_demo_ai.png
- Sources: `reports/stages/web_demo_readiness.json`, `reports/stages/web_demo_final_smoke.json`
- Speaker note: Show answer, chunks, KG triples, KG graph, and Why This Result.

### 10. Current limitations define the next evaluation work

- Role: `discussion`
- Claim: Gold labels are reviewed for source alignment; the next hardening step is external review, CI, and broader document coverage.
- Visual: limitation to next-work ladder
- Sources: `data/cqs/06_phak_ch4_0.gold.json`, `reports/stages/final_evaluation_review.json`, `TASKS.md`
- Speaker note: Be explicit about what the project does not prove yet.

### 11. The assistant is for aviation learning support, not operational authority

- Role: `boundary`
- Claim: Learning and decision-support only; not a POH, checklist, ATC, instructor, or pilot-judgment substitute.
- Visual: boundary statement
- Sources: `src/aviation_agentic_ai/advisory.py`
- Speaker note: Say the full advisory boundary before and after the demo if asked about real flight use.

### 12. The final contribution is an auditable prototype and a reproducible experiment protocol

- Role: `conclusion`
- Claim: The work is defensible because its claims are linked to artifacts, metrics, and reproducibility commands.
- Visual: takeaway checklist
- Sources: `reports/stages/index.json`, `reports/final/project_academic_report.md`, `reports/final/project_defense_notes.md`
- Speaker note: End on this slide for Q&A.

### 13. The artifact index makes the experiment reproducible after the talk

- Role: `appendix`
- Claim: All deck claims map back to local source files, reports, and generated evidence artifacts.
- Visual: artifact index grid
- Sources: `reports/stages/index.json`, `reports/final/aviation_graphrag_defense_deck_sources.json`, `reports/final/project_report_sources.json`
- Speaker note: Use this appendix slide only when asked where a metric or artifact came from.

## Academic QA Checklist

- Every content slide has an action title.
- Reading action titles alone tells the argument.
- Every metric-bearing claim cites a local evidence source.
- Generated images are decorative/explanatory only and contain no fake metrics.
- A references/artifact-index appendix exists after the conclusion slide.
- The final non-appendix slide is a conclusion, not a thank-you slide.

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
