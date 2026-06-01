# NASA ATMONTO Gold Annotation Validation

- Status: `pending_manual_annotation`
- Gold template: `data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl`
- Gold manifest: `data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json`
- Records: 100
- Reviewed records: 0
- Pending records: 100
- Errors: 0
- Warnings: 100

## Completion Gate

- Gold annotations are usable for formal precision/recall/F1 only when status is ready_for_scoring.

## Required Rejection Decisions

- For each reviewed record, every rejected validator fact must have a `rejected_fact_adjudications` entry.
- Allowed decisions: `extractor_bug`, `manual_review_only`, `profile_gap`, `source_ambiguity`

## Current Warnings

- `ATCSCC-GOLD-001` / `2026-05-19:032`: pending_manual_gold_annotation
- `ATCSCC-GOLD-002` / `2026-05-15:063`: pending_manual_gold_annotation
- `ATCSCC-GOLD-003` / `2026-05-18:069`: pending_manual_gold_annotation
- `ATCSCC-GOLD-004` / `2026-05-14:059`: pending_manual_gold_annotation
- `ATCSCC-GOLD-005` / `2026-05-19:059`: pending_manual_gold_annotation
- `ATCSCC-GOLD-006` / `2026-05-19:144`: pending_manual_gold_annotation
- `ATCSCC-GOLD-007` / `2026-05-16:051`: pending_manual_gold_annotation
- `ATCSCC-GOLD-008` / `2026-05-17:019`: pending_manual_gold_annotation
- `ATCSCC-GOLD-009` / `2026-05-20:040`: pending_manual_gold_annotation
- `ATCSCC-GOLD-010` / `2026-05-20:053`: pending_manual_gold_annotation
- `ATCSCC-GOLD-011` / `2026-05-19:108`: pending_manual_gold_annotation
- `ATCSCC-GOLD-012` / `2026-05-18:053`: pending_manual_gold_annotation
- `ATCSCC-GOLD-013` / `2026-05-18:124`: pending_manual_gold_annotation
- `ATCSCC-GOLD-014` / `2026-05-18:104`: pending_manual_gold_annotation
- `ATCSCC-GOLD-015` / `2026-05-20:137`: pending_manual_gold_annotation
- `ATCSCC-GOLD-016` / `2026-05-20:078`: pending_manual_gold_annotation
- `ATCSCC-GOLD-017` / `2026-05-19:079`: pending_manual_gold_annotation
- `ATCSCC-GOLD-018` / `2026-05-19:074`: pending_manual_gold_annotation
- `ATCSCC-GOLD-019` / `2026-05-15:067`: pending_manual_gold_annotation
- `ATCSCC-GOLD-020` / `2026-05-15:084`: pending_manual_gold_annotation
- ... 80 more warnings omitted

## Current Errors
