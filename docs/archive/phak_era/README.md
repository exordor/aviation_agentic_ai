# PHAK-Era Archived Documentation

This directory holds documentation from the project's earlier aviation-training
(PHAK Chapter 4) route. These files are preserved for provenance and historical
method evolution, but they are **not** current thesis entry points.

The active thesis line is:

> Agentic KG-RAG for evidence-grounded question answering over retrospective
> FAA ATCSCC advisories.

For current navigation, start at `docs/documentation_map.md` instead.

## Why these files were archived

`docs/context_hygiene_audit.md` (now merged into `docs/documentation_map.md`)
classified each of these as PHAK-era or transitional material that could
pollute current thesis context if loaded as default reading. They describe the
earlier aviation-training prototype (PHAK Chapter 4 ontology, chunking
experiments, web demo, NASA BGA transfer pilot) rather than the current ATCSCC
schema-constrained KG-RAG line.

## Archived files

| File | Historical role |
| --- | --- |
| `ontology_design.md` | PHAK Chapter 4 curated ontology presented as the active ontology. |
| `benchmark_design.md` | PHAK Chapter 4 retrieval/safety benchmark. |
| `document_expansion_protocol.md` | Expansion policy restricted to PHAK Chapter 4. |
| `chunking_experiment_protocol.md` | PHAK chunking experiments. |
| `benchmark_manual_review_protocol.md` | PHAK benchmark label review. |
| `heuristic_detection_failure_analysis.md` | Old PDF extraction heuristics and PHAK failure modes. |
| `nasa_aerodynamics_source_scope.md` | NASA BGA transfer/source-scope material. |
| `ontology_boundary_nasa.md` | Old PHAK/NASA ontology-boundary framing. |
| `pdf_extraction_backend_policy.md` | PDF/chunking support policy. |
| `nasa_atmonto_experiment_design.md` | Transitional document from the PHAK route toward NASA ATMONTO; predates the current ATCSCC schema-constrained framing. |

## Safe use

These files may be consulted for:

- historical method evolution (how the project moved from PHAK to ATCSCC);
- negative-result context (why certain approaches were abandoned);
- explicit comparison tasks that ask for PHAK-era baselines.

They must not be loaded as the current thesis story. Do not let them override
the current ATCSCC schema-constrained Agentic KG-RAG framing.

Archived: 2026-07-03.
