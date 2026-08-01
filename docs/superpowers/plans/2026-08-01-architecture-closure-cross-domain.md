# Architecture Closure and Cross-Domain Retrieval Plan

## Capability advanced

Close the gap between the active ATMONTO-grounded aviation runtime and the
older TMI-only documentation, export, retrieval, configuration, and evaluation
contracts. The user-facing result is one natural-language `ask` entry point
whose LLM selects an appropriate bounded tool family over TMI and
Flight/Airspace knowledge, with all formal knowledge available to offline KG
exports and a real-provider cross-domain acceptance run.

## Smallest end-to-end result

1. The documented flagship ingest command executes.
2. The Query Agent uses one shared tool registry and an LLM-selected tool
   family without fixed question strings.
3. Full-store JSONL/RDF/Neo4j export includes active TMI and Flight/Airspace
   formal publications.
4. Runtime settings, source catalog, and bounded dataset selection are separate
   configuration artifacts.
5. A frozen six-category natural-language suite exercises TMI, Flight,
   Weather, Sector, cross-domain, and insufficient behavior with the configured
   real provider.

## Batch G1: query runtime closure

- Add behavior tests for the documented targeted ingest command.
- Introduce a single typed Query tool registry consumed by runtime and live
  evaluation.
- Add an LLM domain-selection turn over bounded domain labels, then expose the
  selected tool family to the existing action-observation loop.
- Preserve the requirement that every valid question invokes a real Query
  Agent; do not add a fixed question registry or deterministic prose fallback.
- Report selected domain, available tool names, calls, tokens, and terminal
  status in the existing query evidence artifacts.

## Batch G2: complete formal KG projection

- Generalize full-store projection from TMI events to active formal knowledge
  publications.
- Preserve source-version and anchor provenance.
- Export Flight, Route, TrackPoint, Airport, ARTCC, Sector, and admitted
  cross-source formal facts where they have passed a publication profile.
- Do not promote contextual, heuristic, or candidate-only associations into
  formal graph facts.

## Batch G3: configuration and operational status

- Split the current combined YAML into:
  - runtime configuration;
  - immutable source catalog;
  - bounded dataset/experiment manifest.
- Add deterministic composition and checksum reporting.
- Label AIRM-O mappings as historical research alignment rather than current
  AIRM conformance.
- Preserve raw time, normalized time, time basis, and interpretation status for
  source-naive timestamps.
- Keep semantic ingestion authoritative when an index update fails, but surface
  the stale/blocked index state in the CLI summary.

## Batch G4: cross-domain live acceptance

- Freeze natural-language tasks across TMI, Flight, Weather, Sector,
  cross-domain, and unsupported/insufficient categories.
- Reuse the production ingestion, Query Agent, support checker, and shared tool
  registry.
- Run a `live_smoke` with the configured DeepSeek provider after offline tests
  pass. Report provider-return success separately from task acceptance.
- Do not describe the smoke as a benchmark. A `live_experiment` remains subject
  to the repository requirement for at least 100 successful real calls.

## Batch G5: documentation and architecture

- Synchronize README, GOALS, TODO, RESEARCH_AUDIT, REPRODUCIBILITY, AGENTS, and
  the normative design.
- Update the editable Draw.io construction and retrieval figures only after the
  runtime contracts stabilize.
- Archive the superseded flight competency sidecar and older cross-source
  designs as historical baselines without deleting reproducibility evidence.

## Evidence and acceptance

- Each production behavior is preceded by a focused failing test.
- The README targeted ingest command reaches the supported workflow.
- Runtime and live evaluation enumerate tools from the same registry.
- Domain selection is model-driven and not based on exact question matching.
- Full KG export contains both TMI and Flight/Airspace formal roots and excludes
  non-causal/candidate-only associations.
- Config composition is deterministic and old combined configuration is no
  longer the normative path.
- Index failures are visible without rolling back accepted semantic knowledge.
- Real-provider artifacts record model ID, calls, tokens, latency, tool traces,
  parsed results, and acceptance status under ignored runtime directories.

## Explicitly deferred

- Production concurrency and multi-user deployment.
- Database migration from SQLite to PostgreSQL, Neo4j, or a distributed store.
- Microsoft GraphRAG communities/reports or LightRAG algorithm reproduction.
- Causal inference, TMI recommendation, decision-process reconstruction, and
  nationwide multi-year trajectory scale claims.
- A statistical model benchmark beyond the approved real-provider smoke.
