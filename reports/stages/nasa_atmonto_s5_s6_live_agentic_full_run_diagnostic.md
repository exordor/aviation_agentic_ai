# NASA ATMONTO S5/S6 Live Agentic Full Run Diagnostic

## Summary

- Status: `live_full_run_diagnostic_created`
- Records: 100
- Failed records: 0
- Zero-S6 records: 4
- Refiner fallback count: 96
- Final schema-valid records: 96

## Metric Comparison

| System | Predicted | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Live S5 validator accepted | 535 | 270 | 265 | 373 | 0.5047 | 0.4199 | 0.4584 |
| Live S6 critic/refined | 485 | 257 | 228 | 386 | 0.5299 | 0.3997 | 0.4557 |
| Deterministic independent S6 | 545 | 462 | 83 | 181 | 0.8477 | 0.7185 | 0.7778 |

- Live S6 minus live S5: `{'predicted_fact_count': -50, 'true_positive_count': -13, 'precision': 0.0252, 'recall': -0.0202, 'f1': -0.0027}`
- Live S6 minus deterministic S6: `{'predicted_fact_count': -60, 'true_positive_count': -205, 'false_positive_count': 145, 'false_negative_count': 205, 'precision': -0.3178, 'recall': -0.3188, 'f1': -0.3221}`

## Top Error Predicates

- Top false-negative predicates: `[('initiativeComments', 67), ('effectiveEndTime', 62), ('effectiveStartTime', 57), ('controlledNASelement', 46), ('advisoryNumber', 31), ('impactingCondition', 22), ('implementationStatus', 21), ('issuedTime', 20), ('reRouteReason', 20), ('reRouteType', 19)]`
- Top false-positive predicates: `[('initiativeComments', 50), ('effectiveEndTime', 48), ('effectiveStartTime', 43), ('advisoryNumber', 20), ('controlledNASelement', 16), ('departureScope', 12), ('impactingConditionMessage', 12), ('reRouteReason', 10), ('issuedTime', 5), ('allowedRoute', 3)]`

## Predicate Breakdown

| Predicate | Predicted | Gold | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `initiativeComments` | 64 | 81 | 14 | 50 | 67 | 0.2188 | 0.1728 | 0.1931 |
| `effectiveEndTime` | 84 | 98 | 36 | 48 | 62 | 0.4286 | 0.3673 | 0.3956 |
| `effectiveStartTime` | 84 | 98 | 41 | 43 | 57 | 0.4881 | 0.4184 | 0.4506 |
| `controlledNASelement` | 16 | 46 | 0 | 16 | 46 | 0.0 | 0.0 | 0.0 |
| `advisoryNumber` | 89 | 100 | 69 | 20 | 31 | 0.7753 | 0.69 | 0.7302 |
| `reRouteReason` | 10 | 20 | 0 | 10 | 20 | 0.0 | 0.0 | 0.0 |
| `issuedTime` | 83 | 98 | 78 | 5 | 20 | 0.9398 | 0.7959 | 0.8619 |
| `impactingCondition` | 2 | 22 | 0 | 2 | 22 | 0.0 | 0.0 | 0.0 |
| `impactingConditionMessage` | 12 | 10 | 0 | 12 | 10 | 0.0 | 0.0 | 0.0 |
| `implementationStatus` | 0 | 21 | 0 | 0 | 21 | 0.0 | 0.0 | 0.0 |
| `reRouteType` | 0 | 19 | 0 | 0 | 19 | 0.0 | 0.0 | 0.0 |
| `extensionProbability` | 21 | 30 | 19 | 2 | 11 | 0.9048 | 0.6333 | 0.7451 |
| `departureScope` | 12 | 0 | 0 | 12 | 0 | 0.0 | 0.0 | 0.0 |
| `allowedRoute` | 3 | 0 | 0 | 3 | 0 | 0.0 | 0.0 | 0.0 |
| `flightInclusionSpec` | 3 | 0 | 0 | 3 | 0 | 0.0 | 0.0 | 0.0 |
| `includesAirport` | 2 | 0 | 0 | 2 | 0 | 0.0 | 0.0 | 0.0 |

## Interpretation

- **Primary Finding:** The full live LLM agentic run is operationally robust but substantially weaker than the deterministic source-derived S5/S6 control. The gap is caused mainly by live extractor recall and precision, not by runtime failures.
- **Critic Effect:** The S6 critic/refiner layer removes 50 facts, raising precision from 0.5047 to 0.5299 but lowering recall from 0.4199 to 0.3997, leaving F1 essentially unchanged.
- **Refiner Effect:** The refiner triggered safety fallback on 96 of 100 records, so current S6 quality should be attributed mostly to deterministic validation plus critic filtering, not to successful LLM rewriting.
- **Thesis Claim:** Use the full run as negative/diagnostic SOTA-comparison evidence: multi-agent orchestration and hard gates are executable and auditable, but unconstrained live LLM extraction does not beat a domain-specific deterministic extractor for semi-structured ATCSCC advisories.
