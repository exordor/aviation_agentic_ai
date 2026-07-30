# Agent System Live Agent Smoke v2

## Boundary

Single-run provider compatibility and bounded-behavior smoke only; not a benchmark, statistical reliability result, or Semantic Resolution evaluation.

## Summary

- Runner status: `completed`
- Model acceptance: `failed`
- Live model: `true`
- Provider / model: `deepseek` / `deepseek-v4-pro`
- Temperature / thinking / retries: `0.0` / `disabled` / `0`
- Trials: 5
- Passed / failed / blocked / not run: 1 / 4 / 0 / 0
- Semantic Resolution: `not_evaluated_no_natural_ambiguity`
- Runner details: `none`

## Trials

| Trial | Role | Workflow | Activation | Acceptance | Calls | Tokens |
| --- | --- | --- | --- | --- | ---: | ---: |
| `assembly-025` | `decision_case_assembly` | `insufficient` | `activated` | `failed` | 2 | 5860/2018 |
| `assembly-030` | `decision_case_assembly` | `insufficient` | `activated` | `failed` | 2 | 5732/183 |
| `assembly-070` | `decision_case_assembly` | `insufficient` | `activated` | `failed` | 2 | 5068/179 |
| `assembly-072` | `decision_case_assembly` | `insufficient` | `activated` | `failed` | 2 | 5030/157 |
| `query-gdp-138` | `query` | `ok` | `activated` | `passed` | 2 | 10234/1255 |

Temperature 0 reduces sampling variance but does not guarantee identical provider outputs.
