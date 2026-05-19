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

## KG Graph Readiness

- Ready: True
- Scope: `question_scoped_retrieved_evidence`
- Default: `structure_aware` + `hybrid`
- Sample: `06-phak-ch4-0-p00-fa9830b888` with 8 triples

## Demo Explanation Readiness

- Ready: True
- Default path: `structure_aware + hybrid`
- Recommended strategy: `structure_aware`
- Pipeline steps: 7
- Mode explanations: 3

## Demo Script

- Open the local FastAPI web demo.
- Start with the Demo Narrative and Pipeline Explanation panels.
- Confirm artifact readiness and advisory boundary in the sidebar.
- Select a boundary CQ and compare vector, graph, and hybrid evidence.
- Use Why This Result to explain the current evidence shape and metric signals.
- Use the KG relationship graph to explain retrieved structured evidence.
- Switch between structure-aware and fixed-window experiments.
- Explain GraphRAG as structured KG evidence support, not a single-score winner.

## Apple-Style UI Smoke Checklist

- macOS-style sidebar question list is visible.
- Top toolbar exposes strategy and retrieval mode segmented controls.
- Demo Narrative, Pipeline Explanation, and Mode Comparison are visible.
- Why This Result updates for the selected question and retrieval mode.
- Question-scoped KG graph renders nodes and edges for structure_aware + hybrid.
- Vector mode shows a clear empty state for KG graph evidence.
- Answer, gold label, chunk evidence, and KG triple evidence remain readable.
- Default selection is structure_aware + hybrid.
- Narrow viewport does not overlap controls or evidence text.

## Advisory Boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.
