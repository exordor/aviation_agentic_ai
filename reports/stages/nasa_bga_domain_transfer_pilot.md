# NASA BGA Domain Transfer Pilot

## Boundary

This pilot shows that the artifact contract can be applied to a second NASA source family with source, CQ, chunking, KG, and validation artifacts. It is not a second event-centric operational domain, not human-reviewed, and not a full GraphRAG answer-generation ablation.

## Summary

- Status: `second_domain_transfer_pilot_created`
- Transfer domain: NASA Beginner's Guide to Aerodynamics
- Source type: `nasa_web_educational_page`
- Non-ATM source family: `True`
- Event-centric: `False`
- Human review: `False`

## Source Snapshot

- Pages total: 90
- Valid pages: 89
- Experiment subset pages: 8

## CQ and KG Contract

- CQ labels: 50
- Supported labels: 45
- No-answer labels: 5
- Label distribution: `{'concept_factual': 25, 'equation_formula': 5, 'insufficient_evidence': 5, 'paraphrase_terminology': 5, 'relation_causal': 10}`
- Chunks: 32
- Triples: 134
- Valid triples: 134
- KG errors: 0
- Evidence-in-source rate: 1.0
- Provenance completeness: 1.0

## Artifact Contract Coverage

| Step | Status | Evidence | Limitation |
| --- | --- | --- | --- |
| source_snapshot | `satisfied` | `reports/stages/nasa_source_ingestion.json` | educational NASA pages, not operational event advisories |
| ontology_profile_boundary | `satisfied` | `reports/stages/ontology_boundary_nasa.json` | uses an existing curated aviation profile, not a new reviewed domain ontology |
| competency_question_contract | `satisfied` | `data/cqs/nasa_bga_aerodynamics.seed.gold.json`<br>`reports/stages/nasa_benchmark_summary.json` | seed labels are project/LLM generated and not human reviewed |
| chunking_and_indexable_units | `satisfied` | `data/chunks/nasa_bga_aerodynamics.structure_aware_large.jsonl`<br>`reports/stages/nasa_chunking_summary.json` | chunking is diagnostic and not optimized for this second domain |
| kg_construction_and_validation | `satisfied` | `data/kg/nasa_bga_aerodynamics.structure_aware_large.kg.jsonl`<br>`reports/stages/nasa_kg_validation.json` | schema-valid triples do not prove semantic correctness |
| retrieval_or_graphrag_smoke | `partial` | `reports/stages/multisource_retrieval_smoke.json` | retrieval smoke exists, but S7-style answer-generation ablations are not run |

## Transfer Interpretation

- Artifact contract coverage: 5 satisfied, 1 partial, 0 missing.
- The transfer evidence is sufficient to replace the previous 'no second-domain run' gap with a bounded source-family transfer pilot.
- The evidence is not sufficient for a broad domain-general GraphRAG claim because the pilot is concept-centric, seed-labelled, and lacks full answer-generation ablations.

## Next Actions

- Add reviewed answer labels if this reference-domain pilot becomes a thesis chapter.
- Run retrieval and answer-generation ablations only after the seed labels are reviewed.
- Use a truly non-aviation event source for stronger domain-general claims.
