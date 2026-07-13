# Cross-Source Mainline Evaluation

Snapshot set: `cross-source-2026-05-v1`.

## Hard Ambiguity Challenge

- Cases: 20
- Accepted-target accuracy: 1.0000
- Quarantine accuracy: 1.0000
- Out-of-registry acceptances: 0

This is an authored hard-case challenge, not external aviation-expert gold.

## Matched Answer Baselines

| System | Evidence layers | Citation layers | Abstention | Alignment | Critic failures | Causal overstatements |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Source only | 0.2500 | 0.2500 | 1.0000 | 0.0000 | 24 | 0 |
| Linked text | 0.7500 | 0.7500 | 1.0000 | 0.0000 | 0 | 0 |
| Cross-source KG | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 |

The linked-text baseline shares accepted record links with the KG system and therefore isolates typed graph evidence and answer-contract behavior.
Automated policy conformance is not independent semantic answer correctness.

## Independent Evaluation Agent Audit

- Audited answers: 24
- Passed: 24
- Failed: 0
- Pass rate: 1.0000

The evaluator checks exact advisory evidence, statement citations, registered weather records and graph links, layer separation, alignment expectations, abstention, and the Evidence Critic through a path separate from answer generation.
It removes human review as a runtime dependency but is not external aviation-expert certification.
