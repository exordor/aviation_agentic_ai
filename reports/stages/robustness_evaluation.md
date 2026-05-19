# Robustness Evaluation

- Run ID: `robustness-evaluation-20260519T044429Z`
- Cases: 10

| Metric | Value |
| --- | ---: |
| Retrieval stability | 0.8 |
| Citation stability | 0.7 |
| KG evidence stability | 1.0 |
| Answer stability | 1.0 |
| Abstention correctness | 0.6 |

## Cases

### rob-001-density-altitude-paraphrase

- Type: paraphrase
- Base CQ: exp-014-density-altitude
- Retrieval stable: True
- Abstention correct: True

### rob-002-bernoulli-terminology

- Type: terminology_substitution
- Base CQ: exp-023-bernoulli
- Retrieval stable: True
- Abstention correct: True

### rob-003-boundary-layer-paraphrase

- Type: paraphrase
- Base CQ: exp-007-boundary-layer
- Retrieval stable: True
- Abstention correct: True

### rob-004-humidity-ambiguous

- Type: ambiguous
- Base CQ: exp-018-humidity-performance
- Retrieval stable: False
- Abstention correct: True

### rob-005-lift-cross-page

- Type: cross_page
- Base CQ: exp-019-lift-theories
- Retrieval stable: True
- Abstention correct: True

### rob-006-pressure-above-paraphrase

- Type: paraphrase
- Base CQ: exp-028-low-pressure-above
- Retrieval stable: False
- Abstention correct: True

### rob-007-unsupported-vspeeds

- Type: unsupported
- Base CQ: exp-031-no-answer-vspeeds
- Retrieval stable: True
- Abstention correct: False

### rob-008-unsupported-live-weather

- Type: unsupported
- Base CQ: exp-032-no-answer-live-weather
- Retrieval stable: True
- Abstention correct: False

### rob-009-unsupported-checklist

- Type: unsupported
- Base CQ: exp-033-no-answer-poh
- Retrieval stable: True
- Abstention correct: False

### rob-010-unsupported-go-no-go

- Type: unsupported
- Base CQ: exp-035-no-answer-go-no-go
- Retrieval stable: True
- Abstention correct: False
