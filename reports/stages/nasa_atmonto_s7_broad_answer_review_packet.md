# NASA ATMONTO S7 Broad Answer Review Packet

## Boundary

This is a broad reviewer packet over every selected S7 LLM answer case. It contains automatic metrics and blank reviewer fields, but it is not human-reviewed evidence until an external reviewer records decisions.

## Summary

- Source LLM cases: 60
- Review packet cases: 60
- Failure / needs-review cases: 3
- Auto-success coverage cases: 57
- Human review completed: `False`

## Review Schema

| Field | Allowed values |
| --- | --- |
| `review_decision` | correct / partially_correct / incorrect / abstention_correct / profile_boundary / unsure |
| `evidence_support` | fully_supported / partially_supported / unsupported / not_applicable |
| `citation_sufficiency` | sufficient / partial / insufficient / not_applicable |
| `profile_boundary` | yes / no / unsure |
| `reviewer_notes` | free text |
| `reviewer_id_or_initials` | pseudonym or initials |
| `reviewer_role` | external_expert / human_reviewer / supervisor |
| `reviewed_at` | YYYY-MM-DD or ISO timestamp |

## Aggregate

- Review status counts: `{'auto_success': 57, 'needs_review': 3}`
- Template counts: `{'QT-A01-ABSTENTION-FIELDS': 10, 'QT-Q01-AFFECTED-NAS-ELEMENTS': 10, 'QT-Q01-CAUSE-CONDITION': 10, 'QT-Q01-ROUTE-SEMANTICS': 10, 'QT-Q01-STATUS-ACTION': 10, 'QT-Q01-TIME-WINDOW': 10}`
- Mode counts: `{'routed_token_matched_dense_graphrag': 30, 'routed_token_matched_live_tfidf_graphrag': 30}`

## Case Index

| Review ID | Priority | Template | Source | Mode | Auto correct | Unsupported |
| --- | --- | --- | --- | --- | ---: | ---: |
| `S7-BR-001` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `2026-05-19:079` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-002` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `2026-05-19:074` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-003` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `2026-05-15:067` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-004` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `2026-05-15:084` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-005` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `2026-05-14:089` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-006` | coverage_success | `QT-Q01-TIME-WINDOW` | `2026-05-19:032` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-007` | coverage_success | `QT-Q01-TIME-WINDOW` | `2026-05-15:063` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-008` | coverage_success | `QT-Q01-TIME-WINDOW` | `2026-05-18:069` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-009` | coverage_success | `QT-Q01-TIME-WINDOW` | `2026-05-14:059` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-010` | coverage_success | `QT-Q01-TIME-WINDOW` | `2026-05-19:059` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-011` | coverage_success | `QT-Q01-CAUSE-CONDITION` | `2026-05-19:079` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-012` | coverage_success | `QT-Q01-CAUSE-CONDITION` | `2026-05-19:074` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-013` | failure | `QT-Q01-CAUSE-CONDITION` | `2026-05-15:067` | `routed_token_matched_live_tfidf_graphrag` | False | 0.5 |
| `S7-BR-014` | coverage_success | `QT-Q01-CAUSE-CONDITION` | `2026-05-15:084` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-015` | coverage_success | `QT-Q01-CAUSE-CONDITION` | `2026-05-15:064` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-016` | coverage_success | `QT-Q01-STATUS-ACTION` | `2026-05-19:032` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-017` | coverage_success | `QT-Q01-STATUS-ACTION` | `2026-05-19:079` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-018` | coverage_success | `QT-Q01-STATUS-ACTION` | `2026-05-19:074` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-019` | coverage_success | `QT-Q01-STATUS-ACTION` | `2026-05-15:067` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-020` | coverage_success | `QT-Q01-STATUS-ACTION` | `2026-05-15:084` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-021` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `2026-05-19:079` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-022` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `2026-05-19:074` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-023` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `2026-05-15:067` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-024` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `2026-05-15:084` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-025` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `2026-05-14:089` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-026` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `2026-05-19:032` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-027` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `2026-05-15:063` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-028` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `2026-05-18:069` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-029` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `2026-05-14:059` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-030` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `2026-05-19:059` | `routed_token_matched_live_tfidf_graphrag` | True | 0.0 |
| `S7-BR-031` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `2026-05-19:079` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-032` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `2026-05-19:074` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-033` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `2026-05-15:067` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-034` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `2026-05-15:084` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-035` | coverage_success | `QT-Q01-AFFECTED-NAS-ELEMENTS` | `2026-05-14:089` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-036` | coverage_success | `QT-Q01-TIME-WINDOW` | `2026-05-19:032` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-037` | coverage_success | `QT-Q01-TIME-WINDOW` | `2026-05-15:063` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-038` | coverage_success | `QT-Q01-TIME-WINDOW` | `2026-05-18:069` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-039` | coverage_success | `QT-Q01-TIME-WINDOW` | `2026-05-14:059` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-040` | coverage_success | `QT-Q01-TIME-WINDOW` | `2026-05-19:059` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-041` | coverage_success | `QT-Q01-CAUSE-CONDITION` | `2026-05-19:079` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-042` | coverage_success | `QT-Q01-CAUSE-CONDITION` | `2026-05-19:074` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-043` | failure | `QT-Q01-CAUSE-CONDITION` | `2026-05-15:067` | `routed_token_matched_dense_graphrag` | False | 0.5 |
| `S7-BR-044` | coverage_success | `QT-Q01-CAUSE-CONDITION` | `2026-05-15:084` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-045` | failure | `QT-Q01-CAUSE-CONDITION` | `2026-05-15:064` | `routed_token_matched_dense_graphrag` | False | 0.5 |
| `S7-BR-046` | coverage_success | `QT-Q01-STATUS-ACTION` | `2026-05-19:032` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-047` | coverage_success | `QT-Q01-STATUS-ACTION` | `2026-05-19:079` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-048` | coverage_success | `QT-Q01-STATUS-ACTION` | `2026-05-19:074` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-049` | coverage_success | `QT-Q01-STATUS-ACTION` | `2026-05-15:067` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-050` | coverage_success | `QT-Q01-STATUS-ACTION` | `2026-05-15:084` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-051` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `2026-05-19:079` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-052` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `2026-05-19:074` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-053` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `2026-05-15:067` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-054` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `2026-05-15:084` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-055` | coverage_success | `QT-Q01-ROUTE-SEMANTICS` | `2026-05-14:089` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-056` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `2026-05-19:032` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-057` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `2026-05-15:063` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-058` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `2026-05-18:069` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-059` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `2026-05-14:059` | `routed_token_matched_dense_graphrag` | True | 0.0 |
| `S7-BR-060` | coverage_success | `QT-A01-ABSTENTION-FIELDS` | `2026-05-19:059` | `routed_token_matched_dense_graphrag` | True | 0.0 |

## Reviewer Instructions

1. Start with cases where `Priority` is `failure`.
2. Verify that each returned value is supported by the source chunk or graph triple.
3. Mark profile-boundary cases separately from retrieval or generation errors.
4. Fill the CSV review columns; do not edit automatic metric columns.
5. For browser-based review, use `reports/stages/nasa_atmonto_s7_answer_review_worksheet.html`.

## Claim Boundary

Use this packet to perform or document human/supervisor review of answer correctness, evidence support, citation sufficiency, and profile-boundary cases. Do not cite it as expert validation before reviewer decisions are filled in.
