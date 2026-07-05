# Answer Evaluation

- Run ID: `answer-evaluation-20260529T235322Z`
- Answers: 30
- Scoring: answer layer only; no retrieval/KG mixed total score.
- Score method: deterministic heuristic unless an optional LLM/manual field is explicitly populated.

| Mode | Answers | Citation complete | Citation precision | Citation recall | Citation correct | Faithfulness | Answer correctness | Relevance | Abstention correct | Boundary violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector | 10 | 1.0 | 1.0 | 0.5968 | 1.0 | 0.8 | 0.7 | 0.9 | 0.8 | 0 |
| graph | 10 | 1.0 | 1.0 | 0.5074 | 0.8 | 0.7 | 0.6 | 0.9 | 0.9 | 0 |
| hybrid | 10 | 1.0 | 0.9838 | 0.4239 | 0.9 | 0.9 | 0.8 | 0.9 | 1.0 | 0 |

## Advisory Boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.
