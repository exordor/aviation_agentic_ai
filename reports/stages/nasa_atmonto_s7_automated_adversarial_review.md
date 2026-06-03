# NASA ATMONTO S7 Automated Consistency Diagnostic

## Boundary

This is an automated multi-angle consistency diagnostic over the S7 answer-review packet. It is useful as an internal error-discovery and claim-boundary check, but it cannot replace human answer review, external expert certification, or operational decision support.

## Summary

- Status: `automated_consistency_diagnostic_completed`
- Packet: `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json`
- Expected cases: 60
- Reviewed cases: 60
- Automated review completed: `True`
- Automated consistency diagnostic completed: `True`
- Diagnostic check modules: `['evidence_verifier', 'citation_auditor', 'cq_contract_validator', 'ontology_profile_validator', 'consistency_critic']`
- Human review completed: `False`
- External expert certified: `False`
- Unresolved conflicts: 0
- Accepted cases: 57
- Flagged cases: 0
- Rejected cases: 3
- Verdict counts: `{'accepted': 57, 'rejected': 3}`
- Role fail counts: `{'consistency_critic': 3, 'cq_contract_validator': 3, 'evidence_verifier': 3, 'ontology_profile_validator': 3}`

## Diagnostic Checks

| Check module | Rule |
| --- | --- |
| `evidence_verifier` | Evidence faithfulness is true and unsupported claim rate is zero. |
| `citation_auditor` | Citation precision is exact and at least one valid citation is detected. |
| `cq_contract_validator` | Answer values match the CQ expected answer set and abstention is correct. |
| `ontology_profile_validator` | Returned predicates stay inside the expected profile predicate set. |
| `consistency_critic` | Flags any case rejected by a preceding module. |

## Flagged Or Rejected Cases

| Review ID | Verdict | Failed roles | Notes |
| --- | --- | --- | --- |
| `S7-BR-013` | `rejected` | evidence_verifier, cq_contract_validator, ontology_profile_validator, consistency_critic | evidence_faithfulness is false or unsupported_claim_rate is non-zero (0.5); answer values do not satisfy the CQ expected answer set or abstention contract; answer predicates exceed the expected profile predicate set (actual=['impactingCondition', 'impactingConditionMessage'], expected=['impactingConditionMessage']); critic escalated failed roles: ['evidence_verifier', 'cq_contract_validator', 'ontology_profile_validator'] |
| `S7-BR-043` | `rejected` | evidence_verifier, cq_contract_validator, ontology_profile_validator, consistency_critic | evidence_faithfulness is false or unsupported_claim_rate is non-zero (0.5); answer values do not satisfy the CQ expected answer set or abstention contract; answer predicates exceed the expected profile predicate set (actual=['impactingCondition', 'impactingConditionMessage'], expected=['impactingConditionMessage']); critic escalated failed roles: ['evidence_verifier', 'cq_contract_validator', 'ontology_profile_validator'] |
| `S7-BR-045` | `rejected` | evidence_verifier, cq_contract_validator, ontology_profile_validator, consistency_critic | evidence_faithfulness is false or unsupported_claim_rate is non-zero (0.5); answer values do not satisfy the CQ expected answer set or abstention contract; answer predicates exceed the expected profile predicate set (actual=['impactingCondition', 'impactingConditionMessage'], expected=['impactingConditionMessage']); critic escalated failed roles: ['evidence_verifier', 'cq_contract_validator', 'ontology_profile_validator'] |
