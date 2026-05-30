# Final Evaluation Review

## Summary

- Scoring policy: layered metrics only; no mixed overall score.
- Recommended default strategy: `structure_aware`
- Baseline strategy: `fixed_window`
- Chunking best by retrieval: `structure_aware`

## Gold Label Review

- Labels: 10
- Gold levels: `{'span': 10}`
- Review required: False
- Review status: `internal_project_gold_not_human_certified`
- Human review: False
- External aviation expert certified: False

## Strategy Decision

- Structure-aware chunks ranked first in chunking comparison by Recall@5/MRR@5/Context Precision@5.
- Structure-aware Hybrid RAG keeps vector-level page recall while exposing KG evidence.
- Fixed-window remains the baseline because the first KG and reports are reproducible artifacts.
- GraphRAG should be presented as structured evidence support, not as a single blended score.

Evidence-level delta, structure-aware hybrid minus fixed-window hybrid:

| Metric | Delta |
| --- | ---: |
| chunk_recall_at_5 | 0.2 |
| span_hit_rate | -0.2 |
| supported_answer_count | 1 |

## Chunking Failure Analysis

- Fixed-window is stable and reproducible but may split evidence at artificial boundaries.
- Structure-aware chunking preserves handbook sections, improving context precision and explanation quality.
- Semantic/meta-like chunking is closer to semantic boundary detection but is costlier and less reproducible in this v1 implementation.

## Hybrid Failure Analysis

| Group | Count |
| --- | ---: |
| fixed_window retrieval failures | 1 |
| structure_aware retrieval failures | 0 |
| fixed_window evidence failures | 2 |
| structure_aware evidence failures | 1 |

## Citation Completeness

| Experiment | Mode | Citation validity | Supported answers |
| --- | --- | ---: | ---: |
| fixed_window | vector | 1.0 | 0 |
| fixed_window | graph | 1.0 | 7 |
| fixed_window | hybrid | 1.0 | 8 |
| structure_aware | vector | 1.0 | 0 |
| structure_aware | graph | 1.0 | 6 |
| structure_aware | hybrid | 1.0 | 9 |

## Submission Claims

- The project implements a reproducible PDF-to-chunks-to-KG-to-vector-index-to-Hybrid-RAG pipeline for PHAK Chapter 4.
- Evaluation is intentionally layered into retrieval, KG evidence, and LLM answer/citation metrics.
- Structure-aware chunking is the recommended demo/default strategy; fixed-window remains the baseline.
- The advisory assistant boundary is explicit: this is flight learning and decision support, not a substitute for POH, checklist, ATC, instructor, or pilot judgment.

## Remaining Limitations

- Gold labels are reviewed for evidence alignment but are not certified by an aviation domain examiner.
- The KG is scoped to PHAK Chapter 4 and does not yet cover emergency/procedure manuals.
- Page-level Recall@5 is a coarse benchmark and under-represents structured evidence value.
- The local web demo is offline-first and does not prove production-scale deployment readiness.

## Advisory Boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.
