# Task 2 Report — Deterministic Weather Context Adapter

## Delivered interface

- Added `DecisionContextEvent`, `WeatherContextAssociation`, `WeatherFactTrace`,
  and `WeatherContextBundle` contracts.
- Added `build_weather_context(event, canonical_facility, snapshot_registry)`.
- Added the frozen `nasa_atmonto_decision_context_weather_slice` sourced from
  the curated NASA ATMONTO catalog.

## Behavior and boundary

- The adapter deterministically selects the latest eligible TAF, the latest
  METAR at or before advisory issuance in the inclusive two-hour window, and
  all METARs in the half-open operational period.
- It validates source checksums and family/row agreement, blocks malformed or
  conflicting in-scope data, and returns `insufficient` when no report is
  eligible.
- It returns source-bound `ValidatedFact` weather-report provenance only. It
  emits no event-to-weather fact, no `data:hasMeteorologicalReport` inverse,
  no graph write, no Agent/model call, and no causal claim. Every association
  has `causal_claim=false` and remains a bundle-side audit record for Task 4
  to materialize.

## Verification

```text
uv run pytest -q tests/test_agent_system_weather_context.py \
  tests/test_agent_system_multisource_contracts.py \
  tests/test_agent_system_graph_kernel.py
62 passed, 5 external deprecation warnings

uv run ruff check .
All checks passed

git diff --check
Passed
```

## Deferred to Task 4

- Persisting `context_associations.jsonl`.
- Materializing the returned weather facts into RDF/Neo4j.
- Workflow integration, manifests, and bounded read-only query tools.
