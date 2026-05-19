# Web Demo Readiness

- Ready: True
- Default strategy: `structure_aware`
- Baseline strategy: `fixed_window`
- Live query: disabled by default

## Artifact Readiness

| Artifact | Present | Path |
| --- | ---: | --- |
| gold_labels | True | `data/cqs/06_phak_ch4_0.gold.json` |
| fixed_hybrid | True | `reports/stages/hybrid_rag_experiment.json` |
| structure_aware_hybrid | True | `reports/stages/hybrid_rag_structure_aware.json` |
| evidence_level_evaluation | True | `reports/stages/evidence_level_evaluation.json` |
| graphrag_review | True | `reports/stages/graphrag_review.json` |
| structure_aware_kg | True | `data/kg/06_phak_ch4_0.structure_aware.kg.jsonl` |
| structure_aware_chunks | True | `data/chunks/06_phak_ch4_0.structure_aware.jsonl` |

## Evidence Summary

| Strategy | Chunk Recall@5 | Span hit rate | KG triple relevance | Supported answers |
| --- | ---: | ---: | ---: | ---: |
| fixed_window | 0.8 | 0.8 | 0.9 | 7 |
| structure_aware | 0.9 | 0.8 | 0.9 | 9 |

## Demo Script

- Open the local FastAPI web demo.
- Confirm artifact readiness and advisory boundary in the sidebar.
- Select a boundary CQ and compare vector, graph, and hybrid evidence.
- Switch between structure-aware and fixed-window experiments.
- Explain GraphRAG as structured KG evidence support, not a single-score winner.

## Apple-Style UI Smoke Checklist

- macOS-style sidebar question list is visible.
- Top toolbar exposes strategy and retrieval mode segmented controls.
- Answer, gold label, chunk evidence, and KG triple evidence remain readable.
- Default selection is structure_aware + hybrid.
- Narrow viewport does not overlap controls or evidence text.

## Advisory Boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.
