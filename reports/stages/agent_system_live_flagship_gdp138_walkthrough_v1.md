# Agent System Live Query Smoke: flagship-gdp138-walkthrough-v1

## Boundary

Provider compatibility and bounded-behavior measurements over a versioned development/regression task suite; repetitions are repeated measurements, not independent samples, a frozen holdout, or a Semantic Resolution evaluation.

## Summary

- Runner status: `completed`
- Model acceptance: `passed`
- Live model: `true`
- Provider / model: `deepseek` / `deepseek-v4-pro`
- Temperature / thinking / retries: `0.0` / `disabled` / `0`
- Trials: 1
- Passed / failed / blocked / not run: 1 / 0 / 0 / 0
- Provider calls: 3
- Native / bound tool calls: 5 / 5
- Input / output tokens: 72409 / 4447
- Provider / tool latency (ms): 74354.468 / 82.551
- Semantic Resolution: `not_evaluated_no_natural_ambiguity`
- Runner details: `none`

## Trials

| Repetition | Trial | Role | Workflow | Activation | Acceptance | Calls | Tokens |
| ---: | --- | --- | --- | --- | --- | ---: | ---: |
| 1 | `flagship-cross-source-gdp138` | `query` | `ok` | `activated` | `passed` | 3 | 72409/4447 |

Temperature 0 reduces sampling variance but does not guarantee identical provider outputs.

## Runtime artifacts

- Parsed outputs: `data/corpus/agent_system/flagship-gdp138-walkthrough-v1/live_evaluation_results_v4.jsonl`
- Parsed outputs SHA-256: `c6ab95d8051b94c4164238885c77c9431985cf0f848b5fe046754d27a7c99dff`
- Raw provider responses: `data/corpus/agent_system/flagship-gdp138-walkthrough-v1/raw_responses_v4.jsonl`
- Attempted / successful / failed real calls: 3 / 3 / 0
- Raw / parsed binding: `valid`
- Raw responses SHA-256: `469f3343fee058431814cd931a5e2ba196fdf9fbf45833bb0c1585787c9c0f51`

Raw provider responses and parsed outputs are gitignored; only this sanitized summary is tracked.
