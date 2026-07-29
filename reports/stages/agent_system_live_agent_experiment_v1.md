# Agent System Real-Provider Experiment v1

## Result

- Runner status: `completed`
- Integrity valid: `true`
- Required successful real calls reached: `true`
- Provider / model: `deepseek` / `deepseek-v4-pro`
- Temperature / thinking / retries: `0.0` / `disabled` / `0`
- Provider prompt-context cache: `observed_automatic` (input-prefix KV reuse, not response replay)
- Prompt-cache hit / miss tokens: 396928 / 34090
- Prompt versions: decision-case-analysis-v1, decision-case-assembly-v1
- Completed cycles: 12
- Attempted real calls: 108
- Successful real calls: 108
- Failed real calls: 0
- Input / output tokens: 431018 / 89148
- Valid / invalid tool calls: 96 / 0
- Provider latency: 882877.38 ms
- Raw-response artifact: `data/corpus/agent_system/live-agent-experiment-v1/raw_responses.jsonl`
- Parsed-output artifact: `data/corpus/agent_system/live-agent-experiment-v1/parsed_outputs.jsonl`

## Task-level acceptance

- Acceptance passed / failed / blocked / not run: 0 / 60 / 0 / 0
- Workflow ok / insufficient / blocked / not run: 0 / 48 / 12 / 0
- Assertions passed / failed: 336 / 60

Repeated real-provider behavior on five fixed tasks. Provider-call success is separate from parsed-contract and task acceptance; calls are repeated measures, not independent evaluation samples.
