# Agent System Real-Provider Experiment v2

## Result

- Runner status: `completed`
- Integrity valid: `true`
- Required successful real calls reached: `true`
- Provider / model: `deepseek` / `deepseek-v4-pro`
- Temperature / thinking / retries: `0.0` / `disabled` / `0`
- Provider prompt-context cache: `observed_automatic` (input-prefix KV reuse, not response replay)
- Prompt-cache hit / miss tokens: 342656 / 40545
- Prompt versions: decision-case-assembly-v1, hybrid-query-agent-v1
- Completed cycles: 12
- Attempted real calls: 120
- Successful real calls: 120
- Failed real calls: 0
- Input / output tokens: 383201 / 69986
- Valid / invalid tool calls: 120 / 0
- Provider latency: 902447.42 ms
- Raw-response artifact: `data/corpus/agent_system/live-agent-experiment-v2/raw_responses_v2.jsonl`
- Parsed-output artifact: `data/corpus/agent_system/live-agent-experiment-v2/parsed_outputs_v2.jsonl`

## Task-level acceptance

- Acceptance passed / failed / blocked / not run: 12 / 48 / 0 / 0
- Workflow ok / insufficient / blocked / not run: 12 / 48 / 0 / 0
- Assertions passed / failed: 384 / 48

Repeated real-provider behavior on five fixed tasks. Provider-call success is separate from parsed-contract and task acceptance; calls are repeated measures, not independent evaluation samples.
