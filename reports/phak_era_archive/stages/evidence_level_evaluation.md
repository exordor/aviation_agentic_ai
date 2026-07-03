# Evidence-Level Evaluation

- Gold labels: `data/cqs/06_phak_ch4_0.gold.json`
- Labels: 10
- Scoring: layered metrics only; no mixed overall score.

## fixed_window

| Mode | Chunk Recall@5 | Span hit rate | Key entity coverage | KG triple relevance | Citation validity | Supported | Partial | Insufficient | Unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector | 1.0 | 1.0 | 0.0 | 0.0 | 1.0 | 0 | 8 | 2 | 0 |
| graph | 0.8 | 0.7 | 0.9 | 0.9 | 1.0 | 7 | 2 | 1 | 0 |
| hybrid | 0.8 | 0.9 | 0.9 | 0.9 | 1.0 | 8 | 2 | 0 | 0 |

## structure_aware

| Mode | Chunk Recall@5 | Span hit rate | Key entity coverage | KG triple relevance | Citation validity | Supported | Partial | Insufficient | Unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector | 0.8 | 0.7 | 0.0 | 0.0 | 1.0 | 0 | 8 | 2 | 0 |
| graph | 0.8 | 0.6 | 0.9 | 0.9 | 1.0 | 6 | 3 | 1 | 0 |
| hybrid | 1.0 | 0.7 | 0.9 | 0.9 | 1.0 | 9 | 1 | 0 | 0 |
