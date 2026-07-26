# Task 1 Report — Multi-source contracts and evidence validation

## Scope delivered

- Extended `SourceFamily` with `metar`, `taf`, and `bts_on_time`.
- Added immutable `SourceSnapshot` instances and a typed `SourceSnapshotRegistry`.
- Added canonical `source_snapshots.jsonl` read/write support, with validation for duplicate source IDs, malformed rows, checksum/content conflicts, and supplied source-family expectations.
- Updated new ingest runs to emit the canonical snapshot artifact.
- Updated the Formal Graph Kernel evidence index to bind each `EvidenceClaim.source_id` only to the matching registered snapshot and to reject snapshots with invalid checksums.
- Updated profile-gap reading to prefer the canonical multi-source artifact and retain `source_snapshot.json` fallback compatibility.

## Explicitly deferred

- Weather and BTS source adapters.
- Visualization changes.
- Any new Agent role, schema expansion, query capability, or documentation change outside Task 1.

## TDD evidence

Each new behavior was introduced through a focused test and observed red state before its minimal green implementation. The red checks covered the missing registry API, duplicate IDs, malformed JSONL diagnostic, forged checksums, source-family mismatch, registry-aware evidence lookup, wrong-source evidence, forged legacy checksum, canonical query artifact loading, source-layer new-run writing, and legacy reader fallback. The immutable-snapshot assertion was likewise observed failing before freezing the model.

## Tests and verification

Passed:

```text
uv run pytest -q tests/test_agent_system_multisource_contracts.py tests/test_agent_system_graph_kernel.py tests/test_agent_system_query_tool_graph.py
79 passed, 5 warnings in 0.67s

git diff --check
uv run ruff check .
All checks passed!
```

The five pytest warnings are pre-existing third-party SWIG deprecation warnings; no test failures or project lint violations remain.

## Compatibility and failure behavior

- Legacy single-snapshot kernel input remains supported and is checksum-verified.
- Query profile-gap loading uses `source_snapshots.jsonl` when present and otherwise reads the legacy `source_snapshot.json` artifact.
- Unknown, wrong-source, malformed, ambiguous-by-duplicate-ID, or checksum-invalid evidence bindings are excluded before formal fact support can be established.
