# NASA ATMONTO S7 Answer Review Import

## Boundary

This import report validates whether a reviewer-filled CSV is safe to promote to the canonical S7 answer-review CSV. It does not create or modify reviewer decisions.

## Summary

- Status: `review_import_rejected`
- Reviewed CSV: `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv`
- Canonical CSV: `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv`
- Require complete: `True`
- Can import: `False`
- Imported: `False`
- Decision status: `s7_answer_review_decisions_pending`
- Expected cases: 60
- Completed cases: 0
- Pending cases: 0
- Invalid cases: 0
- Human review completed: `False`

## Failure Reasons

- reviewed CSV does not exist
- reviewed CSV is missing expected review IDs
- reviewed CSV is not a complete 60-case human review

## Decision Aggregate

- Row status counts: `{}`
- Review decision counts: `{}`
- Missing review IDs: `['S7-BR-001', 'S7-BR-002', 'S7-BR-003', 'S7-BR-004', 'S7-BR-005', 'S7-BR-006', 'S7-BR-007', 'S7-BR-008', 'S7-BR-009', 'S7-BR-010', 'S7-BR-011', 'S7-BR-012', 'S7-BR-013', 'S7-BR-014', 'S7-BR-015', 'S7-BR-016', 'S7-BR-017', 'S7-BR-018', 'S7-BR-019', 'S7-BR-020', 'S7-BR-021', 'S7-BR-022', 'S7-BR-023', 'S7-BR-024', 'S7-BR-025', 'S7-BR-026', 'S7-BR-027', 'S7-BR-028', 'S7-BR-029', 'S7-BR-030', 'S7-BR-031', 'S7-BR-032', 'S7-BR-033', 'S7-BR-034', 'S7-BR-035', 'S7-BR-036', 'S7-BR-037', 'S7-BR-038', 'S7-BR-039', 'S7-BR-040', 'S7-BR-041', 'S7-BR-042', 'S7-BR-043', 'S7-BR-044', 'S7-BR-045', 'S7-BR-046', 'S7-BR-047', 'S7-BR-048', 'S7-BR-049', 'S7-BR-050', 'S7-BR-051', 'S7-BR-052', 'S7-BR-053', 'S7-BR-054', 'S7-BR-055', 'S7-BR-056', 'S7-BR-057', 'S7-BR-058', 'S7-BR-059', 'S7-BR-060']`
- Extra review IDs: `[]`
- Duplicate review IDs: `[]`
