# Batch C.1 Final-Fix Report

Date: 2026-07-27

## Status

Complete. The final review's one Critical, three Important, and two Minor
findings are addressed in one coherent breaking-cutover batch. No provider call,
push, merge, or remote mutation was made.

## Findings Addressed

### Critical: profile-gap forgery

- `PersistedProfileGap` now requires the exact decision-profile reference and a
  deterministic evidence reference. Its stable ID covers the event, field,
  value, reason, evidence reference, and profile identity.
- The Formal Graph Kernel admits only the typed
  `impacting_condition -> atm:impactingCondition` gap when the property exists
  but is outside the current event-class profile and one exact field-specific
  `EvidenceClaim` binds it to the advisory snapshot.
- `profile_gaps.jsonl` is registered in `run_manifest.json` with path, count,
  SHA-256, and decision-layer status.
- Query loading fails closed on a missing, unsafe, unregistered, non-UTF-8,
  checksum-mismatched, count-mismatched, malformed, duplicate, cross-event,
  cross-source, wrong-profile, wrong-schema, or parser-inconsistent row.
- The cancellation-case forgery regression recomputes a self-consistent
  artifact checksum and count, yet is blocked because a generic source
  substring cannot reproduce the exact parsed field value and evidence span.

### Important: remove singleton snapshot compatibility

- Formal Graph Kernel, evidence-index, trace, and profile-gap publication APIs
  now accept only `SourceSnapshotRegistry`.
- The singleton auto-wrapping compatibility helper was removed, and all current
  Kernel fixtures now provide an explicit checksum-validated registry.

### Important: remove tolerant legacy KG-output surface

- The pipe-delimited tolerant Graph Patch reader, parse-rate logic, response
  classifier, and legacy outcome constants were removed.
- `GraphPatchBlock` remains the canonical deterministic Kernel contract.
- `graph_patch.py` remains because current Decision Case Assembly and its
  contract tests call its strict JSON-row `parse_case_assembly_output`; only the
  orphaned tolerant surface was deleted.
- The obsolete graph-construction evidence role and current-facing stale role
  wording were removed.

### Important: all-three authority-to-query acceptance

- One parameterized acceptance test now executes the current authority-backed
  ingest through deterministic parsing, authority resolution, sealed Decision
  Case Assembly, strict preflight, Formal Graph Kernel, materialization,
  manifest publication, and deterministic query for all three canonical cases.
- Ground Stop `2026-05-19:123` preserves its exact period and source-bound
  profile gap; GDP `2026-05-19:138` preserves its exact period and formal
  `weather` evidence; cancellation `2026-05-20:020` preserves its period and
  returns `insufficient` for a missing reason.
- All three preserve the expected BTS-reported active counts and construct no
  Semantic Resolution, Assembly, or Query model.

### Minor: fixture and wording residue

- The multi-source context fixture now obtains a complete
  `AuthorityResolutionResult` through the current authority-resolution
  contract instead of inserting casted nulls into required fields.
- Current comments, module descriptions, schema guidance, and structural test
  wording now name deterministic authority services and Decision Case Assembly
  rather than removed roles or compatibility paths.

## TDD Evidence

The first focused RED run produced four failures:

- the self-consistent cancellation forgery returned `ok`; and
- each of the three real authority-to-query cases lacked the required
  profile-gap manifest metadata.

After the contract and publication changes, the same four cases passed. A
separate non-UTF-8 artifact regression was then added RED, reproduced the raw
`UnicodeDecodeError`, and passed GREEN after conversion to a fail-closed
`QueryToolError`. The migrated focused suite finished with `232 passed`.

## Verification

- Critical malformed/forged artifact checks: `3 passed`.
- Focused Kernel/query/multi-source/runtime/structural suite: `232 passed`.
- `uv run ruff check .`: passed.
- `uv run pytest -q`: `879 passed, 11 warnings`.
- `uv build`: source distribution and wheel built successfully.
- `git diff --check`: passed.
- Active implementation scan found no singleton union API, singleton
  auto-wrapper, tolerant Graph Patch reader/classifier, removed evidence-role
  literal, null-cast fixture, or stale current-facing role wording.

The 11 test warnings are the existing SWIG deprecation and temporary-output-path
warnings; none failed verification. Historical execution-plan documents still
describe their historical architecture and were not rewritten as current
documentation.

## Scope Held

No new Agent, data source, ontology layer, comparison experiment, causal claim,
recommendation path, or live semantic evaluation was introduced. Old run
artifacts remain intentionally incompatible and must be regenerated.
