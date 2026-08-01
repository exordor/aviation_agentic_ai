# Flagship Walkthrough: GDP Advisory 138

## Purpose And Status

This historical walkthrough demonstrates the ingestion-first,
ATMONTO-grounded HybridRAG TMI slice before LLM tool-family routing was added.
It used the normal persistent ingestion pipeline of that revision, its bounded
Query Agent, and the configured real DeepSeek provider.

The observed run completed and passed its evidence and answer-contract checks.
It is a `live_smoke / system walkthrough`: it shows that this versioned
end-to-end path executed successfully, but it is not current-runtime
acceptance, a benchmark, a holdout evaluation, or evidence of general model
quality.

The question was:

> What did ATCSCC publish for JFK in Advisory 138? Verify the
> source-declared reason from the original record, then summarize the
> time-aligned Weather reports and BTS public observations without inferring
> causality.

The broader system context is shown in the
[five-plane architecture](figures/aviation_hybridrag_system_architecture.png),
and the bounded action-observation contract is shown in the
[Query Agent workflow](figures/bounded_query_agent_workflow.png). The actual
run is summarized in the
[editable trace](figures/flagship_gdp138_live_trace.drawio) and
[rendered trace](figures/flagship_gdp138_live_trace.png).

## Evidence Slice

The normal `ingest` command admitted one ATMONTO-aligned TMI event and retained
its supporting source roles:

| Item | Stored identity or value |
| --- | --- |
| Source record | `2026-05-19:138` |
| Source version | `source-version:572124204ead2ee3` |
| Exact full-record anchor | `source-anchor:89a8d0df899b526b` |
| TMI event | `urn:aviation-agentic-ai:event:205dd8308f24ff4b` |
| Formal event type and facility | GDP for KJFK |
| Publication and active time | issued `2026-05-19 22:07Z`; active `19/2205Z` through `20/0259Z` |
| Source-declared reason | `WEATHER / THUNDERSTORMS` |
| Weather context | 6 non-causal associations: 1 TAF and 5 METAR reports |
| BTS active-phase observations | 77 scheduled, 68 completed, 4 cancelled, 5 diverted arrivals |

SQLite remains the authoritative evidence and semantic store. FTS5 and Chroma
are rebuildable retrieval views; search candidates do not become evidence
until an exact source read supplies a source version and anchor.

## Observed End-To-End Path

The run exercised all five architecture planes:

| Plane | Observed operation |
| --- | --- |
| Evidence | ATCSCC Advisory 138, FAA facility identity, Weather reports, and BTS public observations were retained as distinct source roles. |
| Deterministic ingestion | The parser, identity services, temporal alignment, Event Evidence Integration, and Formal Publication Kernel produced one accepted event. |
| Semantic and trust | The event was published under the ATMONTO TMI profile; Weather remained non-causal context and BTS remained source-qualified public observation. |
| Knowledge and retrieval | The Query Agent read the authoritative event facts, discovered the source record, verified its exact anchor, then read Weather and BTS views. |
| Agent interaction | The real LLM selected and sequenced bounded read-only tools, after which statement-level support and claim-boundary validation accepted the answer. |

The actual ordered tool trajectory was:

```text
read_tmi_event_facts
  -> search_source_text
  -> read_source
  -> read_tmi_operational_context
  -> read_public_observations
  -> statement support validation
  -> passed answer
```

This is an observed trajectory, not a fixed question route. The natural-language
question contains no internal tool names. In particular, lexical search only
found a candidate; `read_source` supplied the exact full-record support needed
for the ATCSCC source statement.

## Validated Answer

The accepted answer established the following supported content:

1. ATCSCC Advisory 138 published a CDM Ground Delay Program for JFK/KJFK. It
   was issued at `22:07Z`, with an active program period from `19/2205Z` to
   `20/0259Z`. The exact source record explicitly states
   `WEATHER / THUNDERSTORMS` as the impacting condition.
2. The store associated one TAF and five METAR reports with the event by the
   configured temporal rules. These reports are Weather context; they do not
   prove why ATCSCC selected or parameterized the GDP.
3. The BTS active-phase public observations recorded 77 scheduled arrivals,
   68 completed arrivals, 4 cancellations, and 5 diversions. These are
   retrospective BTS observations, not FAA demand, capacity, AAR, EDCT, or
   decision-input records.

### Statement-To-Evidence Map

| Statement role | Support used by the accepted run |
| --- | --- |
| ATCSCC source record | `2026-05-19:138` + `source-version:572124204ead2ee3` + `source-anchor:89a8d0df899b526b` |
| Formal TMI fact | Event `urn:aviation-agentic-ai:event:205dd8308f24ff4b`, admitted as GDP for KJFK with formal reason `weather` |
| Weather context | Six event-bound context associations, each retaining its Weather source version and Weather facts |
| BTS observations | Event-bound baseline, active, and recovery public-observation records; the summary above reports the active phase |

Every accepted statement in the sanitized query-run artifact has both
`citation_valid=true` and `claim_boundary_valid=true`.

## Claim Boundary

This walkthrough does **not** establish that Weather caused the GDP, that the
GDP caused the BTS observations, or that the observed GDP was effective. It
does not reconstruct ATCSCC's internal decision inputs, alternatives,
constraints, or rationale. It does not reinterpret BTS values as FAA demand,
capacity, AAR, or EDCT, and it does not recommend a TMI for a future event.

## Real-Model Execution Record

| Field | Observed result |
| --- | --- |
| Evaluation mode | `live_smoke / system walkthrough` |
| Runner / model acceptance | `completed` / `passed` |
| Provider / model | `deepseek` / `deepseek-v4-pro` |
| Temperature / thinking / retries | `0.0` / `disabled` / `0` |
| Attempted / successful / failed real calls | 3 / 3 / 0 |
| Bound read-only tool executions | 5 |
| Input / output tokens | 72,409 / 4,447 |
| Provider / tool latency | 74,354.468 ms / 82.551 ms |
| Raw / parsed binding | `valid` |

The native provider responses and parsed trial records remain gitignored. The
tracked, sanitized reports are
[Markdown](../reports/stages/agent_system_live_flagship_gdp138_walkthrough_v1.md)
and
[JSON](../reports/stages/agent_system_live_flagship_gdp138_walkthrough_v1.json).

The tracked report preserves the original at-run path. The retained local
files were moved without byte changes; the table below shows their current
local locations. See the
[relocation index](evaluation_artifact_relocations.md).

| Artifact | Current gitignored location | SHA-256 |
| --- | --- | --- |
| Native provider responses | `data/evaluation_runs/agent_system/flagship-gdp138-walkthrough-v1/raw_responses_v4.jsonl` | `469f3343fee058431814cd931a5e2ba196fdf9fbf45833bb0c1585787c9c0f51` |
| Parsed trial outputs | `data/evaluation_runs/agent_system/flagship-gdp138-walkthrough-v1/live_evaluation_results_v4.jsonl` | `c6ab95d8051b94c4164238885c77c9431985cf0f848b5fe046754d27a7c99dff` |
| Sanitized query run | `data/evaluation_runs/agent_system/flagship-gdp138-walkthrough-v1/hybrid_query_runs/flagship-cross-source-gdp138/hybrid_query_run.json` | `b6124bf1058c12f63a6b330c504ecde9dd18b762076ab32878c1b3fea921d923` |
| Evaluation data binding | `data/evaluation_runs/agent_system/flagship-gdp138-walkthrough-v1/evaluation_data_binding.json` | `677341ac4f59024459a96ee2279a08e3cc9a1e2dd91348a85cf2927acd1b5a8b` |

The evaluator separately reported the provider-call-to-parsed-trial binding as
`valid`.

## Reproduce The Walkthrough

After completing the source-snapshot preflight in
[REPRODUCIBILITY.md](../REPRODUCIBILITY.md), run:

```bash
uv run --extra agent-system aviation-ai agent-system ingest \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/flagship-gdp138-walkthrough-v1 \
  --domain tmi \
  --advisory-id 2026-05-19:138

uv run --extra agent-system aviation-ai agent-system reindex \
  --config configs/aviation_knowledge_v1.yaml \
  --store-dir data/stores/aviation/flagship-gdp138-walkthrough-v1 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
EVAL_RUN_DIR="data/evaluation_runs/agent_system/flagship-gdp138-walkthrough-v1-${RUN_ID}"

uv run python -m aviation_agentic_ai.agent_system.live_agent_evaluation \
  --config configs/aviation_knowledge_v1.yaml \
  --suite data/evaluation/agent_system/live_flagship_gdp138_walkthrough_v1.yaml \
  --store-dir data/stores/aviation/flagship-gdp138-walkthrough-v1 \
  --output-dir "$EVAL_RUN_DIR" \
  --report-dir "$EVAL_RUN_DIR/reports" \
  --allow-live-model \
  --repetitions 1
```

The live command requires the configured DeepSeek credential in an ignored
local environment file. It must not fall back to a fake, scripted, replayed,
or cached response. A future run may produce different wording even at
temperature `0`; report its observed task status and new artifact checksums
rather than presenting the tracked run as deterministic.
