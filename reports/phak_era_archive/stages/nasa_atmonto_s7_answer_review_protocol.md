# NASA ATMONTO S7 Answer Review Protocol

## Purpose

This protocol defines how the S7 answer-generation layer is reviewed after automatic source-bounded metrics. It is intended for human or external expert review of answer correctness, evidence support, citation sufficiency, and profile-boundary cases.

## Scope

- Cases: 60
- Failure-priority cases: 3
- Coverage-success cases: 57
- Unit of review: One S7 answer-generation case: question, answer values, source chunks, graph triples, automatic metrics, and reviewer fields.

## Artifacts

- worksheet: `reports/stages/nasa_atmonto_s7_answer_review_worksheet.html`
- packet_json: `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json`
- packet_csv: `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv`
- import_report: `reports/stages/nasa_atmonto_s7_answer_review_import.md`
- decision_report: `reports/stages/nasa_atmonto_s7_answer_review_decisions.md`

## Reviewer Procedure

1. Open the worksheet HTML in a browser.
2. Filter to `failure` priority cases first, then review coverage-success cases.
3. For each case, compare every answer value against the source chunks and graph triples.
4. Fill every required reviewer field; keep automatic metric columns unchanged.
5. Download the reviewed CSV from the worksheet.
6. Validate the reviewed CSV with the decision-status script.
7. Import the reviewed CSV only after validation succeeds.
8. Regenerate the SOTA audit and thesis dashboard after valid decisions are available.

## Decision Fields

| Field | Allowed values |
| --- | --- |
| `review_decision` | abstention_correct / correct / incorrect / partially_correct / profile_boundary / unsure |
| `evidence_support` | fully_supported / not_applicable / partially_supported / unsupported |
| `citation_sufficiency` | insufficient / not_applicable / partial / sufficient |
| `profile_boundary` | no / unsure / yes |
| `reviewer_role` | external_expert / human_reviewer / supervisor |

Required free-text or identity fields:

- `reviewer_notes`: optional explanatory note, recommended for non-correct decisions.
- `reviewer_id_or_initials`: pseudonym or initials.
- `reviewed_at`: date or ISO timestamp.

## Validation Commands

- build_packet: `uv run python scripts/build_nasa_atmonto_s7_broad_answer_review_packet.py`
- build_worksheet: `uv run python scripts/build_nasa_atmonto_s7_answer_review_worksheet.py`
- validate_default_csv: `uv run python scripts/build_nasa_atmonto_s7_answer_review_decisions.py`
- validate_reviewed_csv: `uv run python scripts/build_nasa_atmonto_s7_answer_review_decisions.py --review-csv reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv`
- import_reviewed_csv: `uv run python scripts/import_nasa_atmonto_s7_reviewed_csv.py reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv --import-if-valid`
- refresh_sota_audit: `uv run python scripts/build_nasa_atmonto_sota_goal_audit.py`
- refresh_dashboard: `uv run aviation-ai report thesis-experiment-dashboard`

## Completion Gate

The gate is complete only when `reports/stages/nasa_atmonto_s7_answer_review_decisions.json` reports `human_review_completed=true`, `completed_case_count=60`, `pending_case_count=0`, and `invalid_case_count=0`.

## Claim Boundary

The protocol is a review procedure, not review evidence. S7 answer-layer human review is complete only after all 60 cases have complete, valid reviewer fields and the decision report reports human_review_completed=True.
