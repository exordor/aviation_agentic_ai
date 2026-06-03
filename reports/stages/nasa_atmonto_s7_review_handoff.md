# NASA ATMONTO S7 Review Handoff

## Boundary

This handoff is a reviewer-facing work aid. It does not certify answer correctness, expert review, operational readiness, or SOTA completion. Human/expert claims remain blocked unless the reviewed CSV is validly imported. Automated adversarial completion must be labelled separately.

## Current State

- Packet status: `broad_answer_review_packet_created`
- Review cases: 60
- Failure-priority cases: 3
- Coverage-success cases: 57
- Import status: `review_import_rejected`
- Import can proceed: `False`
- Reviewed CSV exists: `False`
- Decision status: `s7_answer_review_decisions_pending`
- Completed cases: 0
- Pending cases: 60
- Invalid cases: 0
- Human review completed: `False`
- Automated review status: `automated_adversarial_review_completed`
- Automated review cases: 60
- Automated review completed: `True`
- Automated review accepted/rejected cases: 57/3
- SOTA completion gate passed: `True`
- Failed completion criteria: `[]`
- S7 review completion mode: `automated_adversarial`

## Artifact Checklist

| Artifact | Present | Path | Purpose |
| --- | --- | --- | --- |
| `worksheet_html` | `True` | `reports/stages/nasa_atmonto_s7_answer_review_worksheet.html` | Interactive review worksheet for inspecting all selected S7 answer cases. |
| `review_packet_markdown` | `True` | `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.md` | Broad answer-review packet summary. |
| `review_packet_json` | `True` | `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json` | Machine-readable 60-case review packet. |
| `review_packet_csv` | `True` | `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv` | Canonical review CSV with blank reviewer fields until human review is recorded. |
| `candidate_context` | `True` | `reports/stages/nasa_atmonto_s7_human_review_candidates.md` | Failure-priority and candidate context used to seed review attention. |
| `candidate_adjudication` | `True` | `reports/stages/nasa_atmonto_s7_candidate_adjudication.md` | Candidate-level adjudication context and boundary notes. |
| `review_protocol` | `True` | `reports/stages/nasa_atmonto_s7_answer_review_protocol.md` | Reviewer procedure, fields, allowed values, and completion gate. |
| `automated_adversarial_review` | `True` | `reports/stages/nasa_atmonto_s7_automated_adversarial_review.md` | Automated multi-role answer-layer evidence, citation, CQ, and profile audit. |
| `import_gate` | `True` | `reports/stages/nasa_atmonto_s7_answer_review_import.md` | Safe reviewed-CSV import status. |
| `decision_status` | `True` | `reports/stages/nasa_atmonto_s7_answer_review_decisions.md` | Current human-review decision completeness status. |
| `sota_completion_audit` | `True` | `reports/stages/nasa_atmonto_sota_goal_audit.md` | Overall SOTA goal completion audit and failed criteria. |

## Reviewer Handoff Steps

1. Open the worksheet HTML and keep the protocol report visible.
   Artifact: `reports/stages/nasa_atmonto_s7_answer_review_worksheet.html`
2. Review failure-priority cases first, then all coverage-success cases. Do not edit automatic metric columns.
   Artifact: `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv`
3. Export the reviewer-filled CSV as reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv.
   Artifact: `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv`
4. Either validate and import the human/expert reviewed CSV, or run the automated adversarial review report for all 60 cases.
   Artifact: `reports/stages/nasa_atmonto_s7_answer_review_import.md`
5. Regenerate the SOTA audit and require the completion gate to pass.
   Artifact: `reports/stages/nasa_atmonto_sota_goal_audit.md`

## Commands

- open_worksheet: `open reports/stages/nasa_atmonto_s7_answer_review_worksheet.html`
- validate_reviewed_csv: `uv run python scripts/build_nasa_atmonto_s7_answer_review_decisions.py --review-csv reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv`
- import_reviewed_csv: `uv run python scripts/import_nasa_atmonto_s7_reviewed_csv.py reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv --import-if-valid`
- refresh_sota_audit: `uv run python scripts/build_nasa_atmonto_sota_goal_audit.py`
- run_automated_adversarial_review: `uv run python scripts/build_nasa_atmonto_s7_automated_adversarial_review.py`
- require_sota_complete: `uv run python scripts/build_nasa_atmonto_sota_goal_audit.py --require-complete`

## Completion Rule

S7 answer-layer review can complete through either a 60-case human/expert CSV path or a 60-case automated adversarial path. The SOTA audit `--require-complete` command must exit 0, and the completion mode must remain visible in the report.
