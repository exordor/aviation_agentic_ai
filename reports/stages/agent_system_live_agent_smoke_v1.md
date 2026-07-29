# Agent System Live Agent Smoke v1

## Boundary

Single-run provider compatibility and bounded-behavior smoke only; not a benchmark, statistical reliability result, or Semantic Resolution evaluation.

## Summary

- Runner status: `completed`
- Model acceptance: `failed`
- Live model: `true`
- Provider / model: `deepseek` / `deepseek-v4-pro`
- Temperature / thinking / retries: `0.0` / `disabled` / `0`
- Trials: 5
- Passed / failed / blocked / not run: 0 / 5 / 0 / 0
- Semantic Resolution: `not_evaluated_no_natural_ambiguity`
- Runner details: `none`

## Trials

| Trial | Role | Workflow | Activation | Acceptance | Calls | Tokens |
| --- | --- | --- | --- | --- | ---: | ---: |
| `assembly-025` | `decision_case_assembly` | `insufficient` | `activated` | `failed` | 2 | 5836/2006 |
| `assembly-030` | `decision_case_assembly` | `insufficient` | `activated` | `failed` | 2 | 5754/1981 |
| `assembly-070` | `decision_case_assembly` | `insufficient` | `activated` | `failed` | 2 | 5048/195 |
| `assembly-072` | `decision_case_assembly` | `insufficient` | `activated` | `failed` | 2 | 5040/1624 |
| `analysis-gdp-138` | `decision_case_analysis` | `blocked` | `activated` | `failed` | 1 | 14179/309 |

## Failure diagnosis

- Assembly 025, 030, and 072 exceeded the frozen 512-token output cap.
- Assembly 070 returned a malformed case-assembly contract.
- Analysis 138 completed its read-only evidence step and provider call, but
  the answer did not pass the typed answer/support contract.
- No provider call, tool-budget, frozen-configuration, causal-context, or BTS
  evidence-role check failed.

Temperature 0 reduces sampling variance but does not guarantee identical provider outputs.
