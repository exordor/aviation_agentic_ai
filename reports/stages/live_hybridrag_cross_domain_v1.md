# Cross-Domain HybridRAG Live Smoke v1

- Mode: `live_smoke`
- Runner: `completed`
- Provider / model: `deepseek` / `deepseek-v4-pro`
- Prompt versions: `hybrid-query-agent-v9, hybrid-query-router-v1`
- Temperature / thinking / retries: `0.0` / `disabled` / `0`
- Dataset / knowledge revision: `aviation-knowledge-2026-05-v1` / `76`
- Trials accepted: 5/6
- Routing / retrieval / grounding / answer acceptance: 6/6 / 6/6 / 5/6 / 5/6
- Trial/provider binding: 6/6
- Real calls attempted / successful / failed: 33 / 33 / 0
- Tokens input / output: 265691 / 10352
- Raw provider artifact: `data/corpus/agent_system/live-hybridrag-cross-domain-v1/raw_provider_responses.jsonl`
- Raw SHA-256: `18e2028b57f392a058c63b2c87efd33e9ca4e0002e809148bcbbf537b7cf3ece`
- Parsed output artifact: `data/corpus/agent_system/live-hybridrag-cross-domain-v1/parsed_trial_outputs.jsonl`
- Parsed SHA-256: `856fafb8a8dd8842345d91b3d90fc9d19626e2a87ec081b1b80f06fae5f99af9`
- Artifact integrity: `verified`

| Category | Status | Route | Retrieval | Grounding | Answer | Accepted |
|---|---|---:|---:|---:|---:|---:|
| tmi | ok | 1 | 1 | 1 | 1 | 1 |
| flight | ok | 1 | 1 | 1 | 1 | 1 |
| weather | ok | 1 | 1 | 1 | 1 | 1 |
| sector | ok | 1 | 1 | 1 | 1 | 1 |
| cross_domain | ok | 1 | 1 | 1 | 1 | 1 |
| insufficient | blocked | 1 | 1 | 0 | 0 | 0 |

This is a real-provider compatibility smoke, not a statistical benchmark. Weather links remain temporal/non-causal, TMI applicability remains a candidate relation, and no result proves optimality or supports an operational recommendation.
