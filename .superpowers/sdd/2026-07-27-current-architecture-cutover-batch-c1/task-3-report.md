# Task 3 Report: Require the Current Profile-Owned Run Artifact Format

## Implementation summary

- Added `RUN_MANIFEST_VERSION = "decision-case-run-v1"` and made every new
  manifest record that exact version.
- Reduced canonical provider accounting to `provider_attempts` and
  `provider_successes`; removed `provider_calls`.
- Restricted manifest materialization summaries to `FactMaterialization | None`
  and simplified the ingest CLI output to the current validated-fact result.
- Removed the single-source snapshot writer. The Formal Graph Kernel now keeps
  its provisional advisory registry in memory; `integrate_decision_context`
  remains the sole writer of the final `source_snapshots.jsonl` registry.
- Removed `LegacyValidatedFact`, its decoder, `GraphPatchMaterialization`,
  `materialize_graph_patch`, and the guide-only materialization/projection
  branch.
- Restricted formal publication to exact profile-owned `ValidatedFact` values
  and `SourceSnapshotRegistry`.
- Made `QueryGraphStore` reject missing or wrong-version manifests before
  reading `kg.jsonl`. It validates current materialization metadata, all three
  formal-layer profile bindings and states, the registered snapshot artifact,
  fact ownership/evidence fields, exact source IDs/checksums, and aggregate
  counts before accepting graph rows.
- Made `QueryContextStore` require the current manifest version and current
  materialization before reading optional context artifacts. Explicit current
  `insufficient` and `blocked` layer states remain supported.
- Removed the `source_snapshot.json` fallback and no-manifest/summary-only
  query branches.
- Preserved source binding in the current profile-owned Neo4j projection by
  deriving canonical `SourceRecord` nodes and `DERIVED_FROM` relationships
  from each validated fact's registered source IDs.

No provider calls, new Agents, data sources, ontology terms, recommendations,
or causal claims were added.

## RED

Command:

```bash
uv run pytest -q \
  tests/test_agent_system_current_architecture.py \
  tests/test_agent_system_query_tools.py \
  tests/test_agent_system_multisource_contracts.py \
  tests/test_agent_system_runtime_binding.py
```

Result before implementation:

```text
3 failed, 69 passed
```

The expected failures were:

1. a graph without a current manifest was accepted;
2. a legacy `source_snapshot.json` authorized a profile gap;
3. the manifest had no version and still wrote `provider_calls`.

During repository-wide migration, the removed guide-only projection surfaced
27 old-fixture failures (`842 passed`). Those failures drove migration through
shared current-format fixture funnels and the source-binding preservation in
the current Neo4j projection.

## GREEN

Complete Task 3 focused suite:

```bash
uv run pytest -q \
  tests/test_agent_system_current_architecture.py \
  tests/test_agent_system_graph_kernel.py \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_query_tools.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_agent_system_multisource_contracts.py \
  tests/test_agent_system_runtime_binding.py \
  tests/test_cli_agent_system.py
```

Result:

```text
223 passed
```

Repository-wide regression:

```bash
uv run pytest -q
```

Result:

```text
870 passed, 11 warnings
```

The warnings are existing SWIG deprecations and test output-path warnings.

Static verification:

```bash
uv run ruff check .
git diff --check
```

Result:

```text
All checks passed.
```

## Files changed

Production:

- `src/aviation_agentic_ai/agent_system/materialize.py`
- `src/aviation_agentic_ai/agent_system/query_context_store.py`
- `src/aviation_agentic_ai/agent_system/query_tools.py`
- `src/aviation_agentic_ai/agent_system/runtime.py`
- `src/aviation_agentic_ai/agent_system/sources.py`
- `src/aviation_agentic_ai/agent_system/validation_profiles.py`
- `src/aviation_agentic_ai/agent_system/workflow.py`
- `src/aviation_agentic_ai/cli_agent_system.py`

Tests:

- `tests/test_agent_system_batch_two.py`
- `tests/test_agent_system_graph_kernel.py`
- `tests/test_agent_system_multisource_context.py`
- `tests/test_agent_system_multisource_contracts.py`
- `tests/test_agent_system_public_observations.py`
- `tests/test_agent_system_query_tool_graph.py`
- `tests/test_agent_system_query_tools.py`
- `tests/test_agent_system_runtime_binding.py`
- `tests/test_cli_agent_system.py`

No files were deleted. Compatibility-only tests for the removed legacy fact
decoder were deleted from the current public-observation suite.

## Fixture migration

- Shared query fixtures now write the exact current manifest version, current
  materialization summary, all three formal-layer records, a registered
  `source_snapshots.jsonl`, and profile-owned graph rows with evidence mode,
  evidence reference, source IDs, and exact snapshot checksums.
- Optional context fixtures now register explicit empty `insufficient`
  artifacts instead of relying on absence or a no-manifest fallback.
- Batch-two and multi-source integration fixtures now construct
  `SourceSnapshotRegistry`, exact validation-profile ownership, and fact traces
  through shared helpers. They no longer call the removed guide-only branch.
- Required snapshot-registry corruption now expects the whole run to fail
  closed. Optional context-artifact corruption still does not disable unrelated
  core questions.
- The deferred `cast(Any, None)` multi-source fixture was not naturally
  required for this contract cutover and remains unchanged.

## Self-review

Source scans confirmed:

- no production `source_snapshot.json` fallback or single-snapshot writer;
- no production no-manifest or summary-only query branch;
- no legacy fact model or decoder;
- no `GraphPatchMaterialization` or `materialize_graph_patch`;
- no guide-only formal materialization/projection branch;
- no production `provider_calls`;
- the only final registry writer in the workflow path is
  `integrate_decision_context`;
- current `insufficient` and `blocked` optional-layer branches remain explicit.

## Concerns

- The cutover intentionally makes old run directories unsupported; they must be
  regenerated with the current ingest command.
- The required snapshot registry is now a run-wide trust root. Any missing,
  unregistered, malformed, or checksum-mismatched registry blocks all graph and
  context queries, including core questions.
- No migration tool or dual reader was added.

## Fix Round 1

### Review findings addressed

- `QueryGraphStore` now reconstructs every current graph row as a
  `ValidatedFact` under the checksum-pinned local `ValidationProfileRegistry`.
  It then applies the same publication validator used by materialization.
- The shared validator now enforces profile-admitted evidence modes, source
  families, property object kinds, decision-profile domains and ranges, and
  exact source-text evidence references.
- Direct-source reads require `evidence_ref == fact_id`, exact graph/trace
  evidence-text agreement, a trace checksum matching the registered source
  snapshot, and trace evidence contained in that snapshot.
- Weather source-text traces, public-observation deterministic traces, and
  reconstruction/system-membership evidence retain their separate contracts.
- The final context artifact registry now includes `fact_trace.jsonl` with
  exact path, row count, SHA-256, and decision-layer status. There is no
  circular checksum: the trace checksum is computed before the manifest is
  written, and the manifest is not an input to the trace.
- The ingest CLI provider ceiling now counts every recorded attempt with
  `len(model_calls)`, including failed attempts.
- Added regressions for a self-consistent Weather-as-declared-reason forgery,
  cross-fact `evidence_ref`, mismatched `evidence_text`, and failed provider
  attempts.

No compatibility reader, manifest-trusted profile reconstruction, new Agent,
source, ontology term, recommendation, or causal claim was added.

### RED

Commands:

```bash
uv run pytest -q \
  tests/test_agent_system_query_tools.py::test_store_rejects_self_consistent_weather_reason_owned_by_decision_profile \
  tests/test_cli_agent_system.py::test_ingest_provider_limit_counts_failed_attempts

uv run pytest -q \
  tests/test_agent_system_query_tools.py::test_store_rejects_graph_row_bound_to_another_direct_fact_trace \
  tests/test_agent_system_query_tools.py::test_store_rejects_graph_evidence_text_that_disagrees_with_trace
```

Results before the fixes:

```text
2 failed
1 failed, 1 passed
```

The first pair proved the forged decision-owned Weather reason and two failed
provider attempts were accepted. The second pair proved a row could point at a
different direct fact's otherwise matching trace; evidence-text mismatch was
already rejected by the newly shared validator.

### GREEN

Focused query/materialization/runtime/CLI verification:

```bash
uv run pytest -q \
  tests/test_agent_system_current_architecture.py \
  tests/test_agent_system_graph_kernel.py \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_query_tools.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_agent_system_multisource_contracts.py \
  tests/test_agent_system_runtime_binding.py \
  tests/test_cli_agent_system.py
```

Result:

```text
258 passed in 5.87s
```

Repository-wide regression:

```bash
uv run pytest -q
```

Result:

```text
874 passed, 11 warnings in 25.12s
```

The warnings remain the existing SWIG deprecations and test output-path
warnings.

Static verification:

```bash
uv run ruff check .
git diff --check
```

Result:

```text
All checks passed.
```
