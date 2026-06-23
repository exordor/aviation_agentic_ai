# NASA ATMONTO L1 Agent Batch Experiment

## Boundary

This is a small-batch, artifact-replay L1 Agent-loop experiment. It exercises the bounded extractor-validator-critic-repair-refiner loop without live LLM calls. Use it as reproducible evidence that the L1 loop can reduce emitted schema and support errors on the sampled ATCSCC corpus; do not cite it as external expert certification or live operational ATC support.

## Summary

- Status: `l1_agent_batch_experiment_scored`
- Records: 8
- Live LLM run: `False`
- Invoker: `artifact_replay`
- Max iterations: 2
- Baseline predictions: `data/experiments/nasa_atmonto/formal/s1b_llm_canonicalized_predictions.jsonl`
- Repair artifact: `data/experiments/nasa_atmonto/formal/s4_hybrid_backbone_enrichment_predictions.jsonl`
- Prediction output: `data/experiments/nasa_atmonto/formal/l1_agent_batch_predictions.jsonl`
- Run metadata: `data/experiments/nasa_atmonto/formal/l1_agent_batch_run_metadata.json`

## Before vs After

| Metric | Before baseline candidates | After L1 emitted facts | Delta |
| --- | ---: | ---: | ---: |
| Accepted facts | 16 | 31 | 15 |
| Schema violations | 13 | 0 | -13 |
| Unsupported facts | 0 | 0 | 0 |
| Evidence-in-source rate | 1.0 | 1.0 | 0.0 |

### Metric Definitions

- Schema violations: Facts rejected by the ATCSCC schema/profile validator.
- Unsupported facts: Facts rejected by deterministic critic support checks.
- Evidence-in-source rate: Fraction of candidate or emitted facts whose evidence text is contained in the source advisory.
- Repair success rate: Fraction of repair-attempted records whose accepted fact count increased after L1 repair.

### Interpretation

- In this small artifact-replay batch, the L1 loop emits no schema/profile violations after repair and validation.
- No deterministic unsupported-fact quarantine was observed in this sampled batch; this is a measured zero, not proof that unsupported facts cannot occur.
- All baseline candidates and L1 emitted facts in the sampled batch retain source-contained evidence spans.

## Repair

- Repair attempted records: 8
- Records with fact gain: 8
- Net accepted fact gain: 15
- Repair success rate: 1.0

## Example Records

| Source | Iterations | Before accepted | After accepted | Before schema violations | Before unsupported |
| --- | ---: | ---: | ---: | ---: | ---: |
| `2026-05-19:032` | 2 | 2 | 3 | 2 | 0 |
| `2026-05-15:063` | 2 | 1 | 3 | 0 | 0 |
| `2026-05-18:069` | 2 | 2 | 3 | 2 | 0 |
| `2026-05-14:059` | 2 | 5 | 6 | 1 | 0 |
| `2026-05-19:059` | 2 | 1 | 4 | 2 | 0 |

## Claim Use

- Use this report as evidence that the L1 loop is connected to a repeatable ATCSCC batch run.
- Treat the current run as artifact-replay diagnostics, not live autonomous LLM performance.
- The next stronger experiment is a live or fixed-model LLM run under the same metrics.
