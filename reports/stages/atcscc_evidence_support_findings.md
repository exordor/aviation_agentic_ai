# ATCSCC Evidence Support Findings

## Evidence Contract

- Evidence required: `True`
- Current support unit: `evidence_text`
- Known gap: stable character offsets are not yet a first-class artifact.

## Profile Gap Signals

| Predicate | Rejected/adjudicated count | Treatment |
| --- | ---: | --- |
| `impactingConditionMessage` | 17 | Report as profile/application-scope boundary. |
| `controlledNASelement` | 15 | Report as profile/application-scope boundary. |
| `extensionProbability` | 8 | Report as profile/application-scope boundary. |
| `impactingCondition` | 8 | Report as profile/application-scope boundary. |

## Support Labels

- `supported`: value is directly grounded in the cited advisory text.
- `ambiguous`: source text is present but does not determine a unique value.
- `unsupported`: no matching advisory evidence; fact must be rejected or quarantined.
- `profile_gap`: source-supported candidate is outside the current ATCSCC profile slice.
