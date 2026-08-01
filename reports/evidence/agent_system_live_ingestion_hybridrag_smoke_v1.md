# Agent System Live Query Smoke: ingestion-first-hybridrag-query-agent-smoke-v1

## Boundary

Provider compatibility and bounded-behavior measurements over a versioned development/regression task suite; repetitions are repeated measurements, not independent samples, a frozen holdout, or a Semantic Resolution evaluation.

## Summary

- Runner status: `completed`
- Model acceptance: `failed`
- Live model: `true`
- Provider / model: `deepseek` / `deepseek-v4-pro`
- Temperature / thinking / retries: `0.0` / `disabled` / `0`
- Trials: 3
- Passed / failed / blocked / not run: 1 / 2 / 0 / 0
- Provider calls: 6
- Native / bound tool calls: 9 / 8
- Input / output tokens: 113806 / 5774
- Provider / tool latency (ms): 64624.949 / 660.439
- Semantic Resolution: `not_evaluated_no_natural_ambiguity`
- Runner details: `none`

## Trials

| Repetition | Trial | Role | Workflow | Activation | Acceptance | Calls | Tokens |
| ---: | --- | --- | --- | --- | --- | ---: | ---: |
| 1 | `semantic-source-grounding-138` | `query` | `blocked` | `activated` | `failed` | 1 | 2466/263 |
| 1 | `exact-graph-evidence-123` | `query` | `blocked` | `activated` | `failed` | 3 | 44048/1610 |
| 1 | `context-observations-138` | `query` | `ok` | `activated` | `passed` | 2 | 67292/3901 |

Temperature 0 reduces sampling variance but does not guarantee identical provider outputs.

## Runtime artifacts

- Parsed outputs: `data/corpus/agent_system/live-ingestion-hybridrag-smoke-v1/live_evaluation_results_v4.jsonl`
- Parsed outputs SHA-256: `7ddbd5bad9d4c24a9841ac916de1d6c3d78f5dc42df2d11cfd505e0ff51bcf8c`
- Raw provider responses: `data/corpus/agent_system/live-ingestion-hybridrag-smoke-v1/raw_responses_v4.jsonl`
- Attempted / successful / failed real calls: 6 / 6 / 0
- Raw / parsed binding: `valid`
- Raw responses SHA-256: `bffb912e5b149262ce2845b75b42a7d5f2f3e70244a413fbbe742552c49eda75`

Raw provider responses and parsed outputs are gitignored; only this sanitized summary is tracked.
