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

## Review round 1 corrective verification

Two P1 provenance findings were corrected in a separate follow-up commit without rewriting the original Task 1 commit.

- The Formal Graph Kernel now requires every Graph Patch citation to be a checksum-valid member of the supplied snapshot registry, in addition to any caller-provided known-source list. A mixed valid/unsnapshotted citation rejects the complete line; an unsnapshotted `prov:wasDerivedFrom` object rejects its provenance line.
- Accepted facts retain only the source ID of their matched claim, or the validated provenance endpoint. Materialization independently rejects facts that cite an absent snapshot.
- The snapshot registry now flows through validation, profile-gap collection/persistence, fact-trace persistence, RDF materialization, and the workflow. Profile gaps require exactly one evidence-containing snapshot; trace and profile-gap rows use that snapshot's own checksum. Legacy single-snapshot input remains normalized and checksum-validated.

The correction followed focused red/green cycles for full-kernel mixed/provenance rejection, multi-source profile-gap artifact binding, fact-trace checksum selection, and materialization rejection. Final verification passed:

```text
uv run pytest -q tests/test_agent_system_multisource_contracts.py tests/test_agent_system_graph_kernel.py tests/test_agent_system_batch_two.py tests/test_agent_system_query_tool_graph.py
118 passed, 5 warnings in 0.98s

git diff --check
uv run ruff check .
All checks passed!

uv run pytest -q
576 passed, 11 warnings in 7.47s
```

The 11 full-suite warnings are existing SWIG deprecations and test fixtures that intentionally exercise output-path warnings; no failures or lint violations remain.
