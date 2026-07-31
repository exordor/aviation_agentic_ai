# Agent System Query Agent Smoke v4

## Boundary

Provider compatibility and bounded-behavior measurements over a versioned development/regression task suite; repetitions are repeated measurements, not independent samples, a frozen holdout, or a Semantic Resolution evaluation.

## Summary

- Runner status: `completed`
- Model acceptance: `passed`
- Live model: `true`
- Provider / model: `deepseek` / `deepseek-v4-pro`
- Temperature / thinking / retries: `0.0` / `disabled` / `0`
- Trials: 5
- Passed / failed / blocked / not run: 5 / 0 / 0 / 0
- Provider calls: 11
- Native / bound tool calls: 10 / 10
- Input / output tokens: 190604 / 13547
- Provider / tool latency (ms): 178062.956 / 53.899
- Semantic Resolution: `not_evaluated_no_natural_ambiguity`
- Runner details: `none`

## Trials

| Repetition | Trial | Role | Workflow | Activation | Acceptance | Calls | Tokens |
| ---: | --- | --- | --- | --- | --- | ---: | ---: |
| 1 | `development-exact-facts-084` | `query` | `ok` | `activated` | `passed` | 2 | 5358/703 |
| 1 | `development-weather-context-115` | `query` | `ok` | `activated` | `passed` | 2 | 28549/3885 |
| 1 | `regression-public-observations-159` | `query` | `ok` | `activated` | `passed` | 2 | 8486/1199 |
| 1 | `regression-weather-graph-path-084` | `query` | `ok` | `activated` | `passed` | 2 | 65094/4309 |
| 1 | `regression-event-graph-115` | `query` | `ok` | `activated` | `passed` | 3 | 83117/3451 |

Temperature 0 reduces sampling variance but does not guarantee identical provider outputs.
