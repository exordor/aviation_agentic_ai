# Aviation Agentic AI Project Report

## Project motivation and course objective alignment

This project investigates a reproducible aviation-domain RAG pipeline that turns FAA training text into ontology, KG, retrieval, and grounded-answer artifacts. The course objective is to build an AI-based advisory assistant for private pilots who may need help recalling procedures under stress, while preserving the system’s decision-support role rather than replacing pilot judgment; this is stated in `tmp/goal.md` and echoed in `README.md`. The project description identifies the implementation as a “CLI-first aviation ontology, KG, and GraphRAG research prototype” in `configs/default.yaml`, and the README describes the work as a research prototype for turning FAA Pilot’s Handbook of Aeronautical Knowledge material into machine-queryable knowledge in `README.md`.

## Architecture overview

The implementation is CLI-first and separates ontology generation, KG extraction, chunking, retrieval, evaluation, and reporting modules. This modular configuration is evidenced by `configs/default.yaml`, `configs/ontology_generation.yaml`, and `configs/extraction_profile.yaml`, which define project paths, retrieval settings, ontology generation inputs/outputs, and the focused ABox extraction profile. The default retrieval parameters are `vector_top_k=5`, `graph_hops=2`, and `hybrid_top_k=8` in `configs/default.yaml`. The README also presents the planned pipeline as a sequence from PHAK PDF to CQ generation, ontology generation, RDF validation, focused ABox/KG extraction, semantic chunking, graph/vector retrieval, and hybrid GraphRAG answer generation in `README.md`.

## Ontology/TBox generation and evaluation

The stage index indicates 10 ontology-related entries in its category listing, as reflected in `reports/stages/index.json` via the stage index evidence pack. The project README reports the current baseline ontology statistics as 2,773 RDF triples, 245 OWL classes, 173 object properties, 2 datatype properties, and 0 named individuals in the curated baseline TBox, with the baseline ontology stored at `data/ontology/baseline/06_phak_ch4_0.ttl` and the ontology report at `reports/stages/ontology_report.md` in `README.md`. The ontology-generation configuration targets `data/ontology/generated/06_phak_ch4_0.generated.ttl` from `data/raw/06_phak_ch4_0.pdf` with `temperature: 0.0` and `max_qa_cycles: 2` in `configs/ontology_generation.yaml`. Detailed completed metrics should be cited from the archived ontology evaluation artifacts listed in the stage index, but those metric values are not included in the evidence pack here; therefore, specific evaluation scores are TBD.

## KG/ABox extraction and validation

The KG stage is designed around focused triples with provenance and deterministic validation against the extraction profile. The extraction profile requires provenance and lists provenance fields including `source_document`, `page`, `section`, `chunk_id`, `evidence_text`, `model`, `confidence`, `extracted_at`, `subject`, `predicate`, and `object` in `configs/extraction_profile.yaml`. It also defines instantiable classes such as `Cl_Lift`, `Cl_Drag`, `Cl_AngleOfAttack`, `Cl_BoundaryLayer`, `Cl_WingtipVortex`, `Cl_Atmosphere`, `Cl_Pressure`, `Cl_Density`, `Cl_Temperature`, and `Cl_Altitude`, along with relation properties like `affects`, `causes`, `hasComponent`, `partOf`, `hasQuantity`, `appliesTo`, `hasCondition`, and `hasOutcome` in `configs/extraction_profile.yaml`. If no validated KG experiment report is listed in the evidence pack, end-to-end KG results are Not yet run; the provided evidence pack does not include a completed KG validation report.

## Chunking comparison design

RAG experiment artifacts listed: 0. The default chunking configuration in `configs/default.yaml` names four comparison strategies: `fixed_window`, `sentence_recursive`, `structure_aware`, and `semantic_meta_like`, with `fixed_window` as the default strategy. Chunking comparison should therefore be discussed as a retrieval tradeoff design rather than collapsed into a single score: fixed windows may prioritize simplicity and reproducibility, while structure-aware or semantic strategies may better preserve section boundaries and evidence locality, but no completed comparison results are present in the evidence pack. Any numerical comparison is TBD.

## Hybrid RAG protocol and layered metrics

Hybrid RAG uses separate retrieval, KG evidence, and LLM answer metrics, but the evidence pack does not include completed layered metric outputs. The configured retrieval defaults include `vector_top_k=5`, `graph_hops=2`, and `hybrid_top_k=8` in `configs/default.yaml`. The project’s intended protocol is consistent with the README’s planned flow from semantic chunking to graph retrieval plus vector retrieval and then to hybrid GraphRAG answer generation with citations in `README.md`. Completed metric values for retrieval quality, KG support, and answer groundedness are TBD / Not yet run.

## Current results and limitations

Current results must be reported only when present in the evidence pack. The evidence pack confirms the existence of the baseline ontology and the reporting infrastructure in `README.md`, `reports/stages/index.json`, and `configs/default.yaml`, but it does not provide completed full-loop KG or Hybrid RAG experiment results. The README states that the current implementation includes ontology generation code plus validation/reporting over the baseline aviation ontology generated from PHAK Chapter 4, and that future runs can regenerate candidate ontologies under `data/ontology/generated/` in `README.md`. Missing full-loop experiments should therefore be labeled TBD / Not yet run. No completed end-to-end retrieval, answer-generation, or KG extraction results are asserted here.

## Advisory assistant boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment. This boundary is explicitly stated in `tmp/goal.md` and repeated in the evidence pack under `advisory_boundary`.

## Next work plan

1. Run report hygiene to maintain a readable stage dashboard.
2. Run chunking comparison and Hybrid RAG experiments with recorded run manifests.
3. Refine gold labels from source-page to chunk/span evidence.
4. Use the AI report command to polish this deterministic draft.

These next steps are consistent with the repository’s CLI-first workflow and staged reporting structure described in `README.md` and the stage-indexed artifacts in `reports/stages/index.json`.

## Reproducibility appendix

- `uv run aviation-ai report hygiene --apply`
- `uv run aviation-ai report project --no-ai`
- `uv run aviation-ai report project --ai`

Evidence sources:
- Stage index: `reports/stages/index.json` (present)
- README: `README.md` (present)
- Goal: `tmp/goal.md` (present)
- Configs: `configs/default.yaml`, `configs/ontology_generation.yaml`, `configs/extraction_profile.yaml`
