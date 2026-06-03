# NASA ATMONTO S5/S6 Agentic Evidence Loop

## Boundary

S5/S6 are executable artifact-driven wrappers over the current S4 output. They are not an independent live multi-agent LLM extraction run.

## Summary

- Input system: `S4_hybrid_backbone_enrichment`
- Records: 100
- S5 routed facts: 686
- S6 evidence-gated facts: 686
- S5 unique scored facts: 685
- S6 unique scored facts: 685
- Quarantined facts: 0
- Strict main metrics changed: False
- Independent live LLM run: False

## Stage Definitions

| Stage | Input | Operation | Claim boundary |
| --- | --- | --- | --- |
| `S5_agentic_cq_module_routed_extraction` | S4_hybrid_backbone_enrichment accepted facts | Annotate facts with CQ/module route labels from the CQ manifest. | Reusable routing layer; not new semantic extraction quality by itself. |
| `S6_agentic_evidence_verifier_repair` | S5 routed facts and original ATCSCC source text | Verify evidence containment and quarantine unsupported facts. | Evidence gate; no unsupported value repair or profile extension is applied. |

## Semantic Metrics

| Layer | Predicted | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S4 reported | 685 | 491 | 194 | 152 | 0.7168 | 0.7636 | 0.7395 |
| S5 routed | 685 | 491 | 194 | 152 | 0.7168 | 0.7636 | 0.7395 |
| S6 evidence-gated | 685 | 491 | 194 | 152 | 0.7168 | 0.7636 | 0.7395 |

- Delta S6 minus S5: `{'predicted_fact_count': 0, 'true_positive_count': 0, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0}`

## CQ / Module Routing

| Module | Fact count |
| --- | ---: |
| `deterministic_core` | 394 |
| `graph_query` | 221 |
| `unmapped_profile_fact` | 2 |
| `validator_evidence` | 69 |

- Unmapped facts: 2

## Evidence Gate

- Supported facts: 686
- Quarantined facts: 0
- Support rate: 1.0

### Quarantine Examples

- None.

## SOTA Interpretation

- Satisfied: The artifact chain now drives a concrete S5/S6 routing and evidence-verifier pass over scored ATCSCC predictions.
- Remaining gap: A future S5/S6 run should call separate extractor, validator, critic, and refiner agents before S4-style scoring, rather than wrapping S4 outputs.
- Claim use: Use this artifact as executable loop evidence and a bridge to S5/S6 implementation; do not cite it as an autonomous multi-agent extraction result.
