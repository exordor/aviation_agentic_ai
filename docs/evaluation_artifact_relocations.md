# Evaluation Artifact Relocations

This index separates retained evaluation evidence from the authoritative
knowledge store. Historical tracked reports remain byte-immutable and continue
to show the artifact locations recorded at execution time.

On 2026-08-01, the two locally retained evaluation runs were moved out of the
retired Corpus v2 namespace. File contents and SHA-256 checksums did not
change.

| Historical recorded root | Current local root | Status |
| --- | --- | --- |
| `data/corpus/agent_system/flagship-gdp138-walkthrough-v1/` | `data/evaluation_runs/agent_system/flagship-gdp138-walkthrough-v1/` | Retained live-smoke evidence |
| `data/corpus/agent_system/live-hybridrag-cross-domain-v1/` | `data/evaluation_runs/agent_system/live-hybridrag-cross-domain-v1/` | Retained live-smoke evidence |

Selected checksum-bound retained files:

| File under current local root | Rows | SHA-256 |
| --- | ---: | --- |
| `flagship-gdp138-walkthrough-v1/raw_responses_v4.jsonl` | 3 | `469f3343fee058431814cd931a5e2ba196fdf9fbf45833bb0c1585787c9c0f51` |
| `flagship-gdp138-walkthrough-v1/live_evaluation_results_v4.jsonl` | 1 | `c6ab95d8051b94c4164238885c77c9431985cf0f848b5fe046754d27a7c99dff` |
| `flagship-gdp138-walkthrough-v1/hybrid_query_runs/flagship-cross-source-gdp138/hybrid_query_run.json` | n/a | `b6124bf1058c12f63a6b330c504ecde9dd18b762076ab32878c1b3fea921d923` |
| `flagship-gdp138-walkthrough-v1/evaluation_data_binding.json` | n/a | `677341ac4f59024459a96ee2279a08e3cc9a1e2dd91348a85cf2927acd1b5a8b` |
| `live-hybridrag-cross-domain-v1/raw_provider_responses.jsonl` | 33 | `18e2028b57f392a058c63b2c87efd33e9ca4e0002e809148bcbbf537b7cf3ece` |
| `live-hybridrag-cross-domain-v1/parsed_trial_outputs.jsonl` | 6 | `856fafb8a8dd8842345d91b3d90fc9d19626e2a87ec081b1b80f06fae5f99af9` |

The obsolete local `cross-source-2026-05-v2`, `smoke-v2`, `smoke-v2-final`,
and `smoke-v2-valid` directories were deleted. They were retired Corpus v2
snapshots, not current knowledge and not retained evaluation evidence.

Evaluation runs remain gitignored. Current knowledge is persisted only in the
dataset-bound SQLite evidence store; FTS5 and Chroma are rebuildable indexes,
and RDF/Turtle, JSONL KG, and Neo4j are optional offline exports.
