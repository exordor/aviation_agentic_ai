# Flight–Airspace Operational Knowledge Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the current ATMONTO-grounded TMI vertical slice into a comprehensive heterogeneous aviation knowledge system that persistently ingests Flight, Aircraft, Airport/ARTCC, Weather, Route, TrackPoint, Fix, Sector, and TMI evidence; exposes generic deterministic retrieval and analysis tools; and lets the existing LLM Query Agent dynamically compose those tools for natural-language cross-source questions.

**Architecture:** Upgrade the SQLite evidence store from an event-only publication model to a general ATMONTO knowledge-publication spine. Immutable source assets, logical source versions, exact anchors, semantic fact identity, publication membership, and provenance are shared by every semantic root. TMI and Flight/Airspace records retain domain-specific structured tables for scalable filtering and aggregation. High-frequency trajectory points remain in structured storage; only useful ATMONTO relations are materialized into semantic graph views. FTS and Chroma remain rebuildable retrieval indexes, while RDF/Turtle and Neo4j remain optional exports. The existing bounded Query Agent remains the sole natural-language router and answer generator; deterministic tools perform joins, counts, temporal comparisons, and graph traversal.

**Tech Stack:** Python 3.11+, standard-library `sqlite3`, Pydantic v2, rdflib, existing FAA/NASA/BTS adapters and authority services, existing Formal Publication Kernel, LangChain/LangGraph bounded tool runtime, SQLite FTS5, Chroma/Sentence Transformers, pytest, Ruff, Draw.io, DeepSeek `deepseek-v4-pro` for live acceptance.

## Global Constraints

- This is a comprehensive architecture expansion, not a four-query demo. Do not add `run_F1`, `run_F3S`, `run_S4`, `run_S1S`, fixed question strings, deterministic natural-language routing, or special-case answers.
- The four published NASA query shapes are acceptance questions over generic storage and tools. Each generic tool must also pass parameter-variation tests whose results differ from the frozen acceptance values.
- Preserve one normal RAG/HybridRAG lifecycle: offline ingestion and indexing; online retrieval, augmentation, and LLM generation. Do not create or require an experiment corpus, cohort manifest, or per-query data snapshot.
- SQLite is authoritative. FTS, Chroma, graph views, RDF/Turtle, and Neo4j are rebuildable from accepted store records and never write semantic facts back into SQLite.
- Use one general knowledge-publication spine for TMI, Flight, Aircraft, Airport, Route, and other roots. Do not create a permanently parallel Flight fact/evidence subsystem and do not force Flight facts into `EventIngestionPackage`.
- The general spine is the only publication authority. Retire `event_publications`, `event_sources`, `event_facts`, and event-scoped formal `evidence_links`; TMI-specific tables may reference a general publication but may not own a second active-publication pointer, fact membership, or provenance truth.
- Every formal fact must pass the existing write-free Formal Publication Kernel under a checksum-pinned application profile before publication.
- Treat every logical CSV row or ZIP member record as a canonical `SourceVersionRecord` bound to its raw source asset. Preserve member name, row number, raw-row checksum, and parser version in metadata, and use a full-record character anchor over the canonical row. Do not add an unmodelled row-locator side channel.
- Source-specific parsing is deterministic. Do not add a BTS Agent, PDF Agent, Weather Agent, Flight Agent, or one Agent per source.
- Every valid natural-language `ask` still invokes the LLM Query Agent. The model selects tools and writes the answer; deterministic services execute structured filters, joins, time arithmetic, counts, ranking, and graph traversal.
- Search/vector hits remain candidate discovery. Exact source records, accepted facts, structured associations, graph paths, or deterministic derivations support final statements.
- Use NASA's public `2014-07-15` atmontoPlus NYC slice as the canonical
  end-to-end prototype. Keep May/July 2026 raw-source supplements in separate
  temporal domains and reject unsupported cross-era composite claims.
- Bind every publication and cross-record association to a `temporal_domain_id`; association construction must verify domain compatibility and must reference concrete publication versions rather than only stable roots.
- Treat a BTS source row and a semantic Flight root as different identities. A Flight root is source-qualified and version-stable only under a frozen identity rule; do not merge across source families or source versions without reviewed identity evidence.
- Treat BTS `reporting_carrier` as that exact source role; do not silently map it to ATMONTO `operatedBy` unless an admitted source field supports the stronger semantics.
- Treat the July 2026 FAA aircraft registry as a later technical snapshot. A BTS May 2026 tail-to-model join is a `flight_aircraft_snapshot_match`, not proof of the aircraft model at flight time.
- Every flight–weather association has `causal_claim=false`. Weather proximity does not explain or cause a departure, delay, or TMI.
- Every flight–TMI relation is an `applicability_candidate` based on explicit rule inputs. It is not proof that the flight was actually controlled, delayed, or assigned an EDCT.
- Generate TMI applicability candidates only after UTC-qualified temporal overlap, facility/departure-scope filtering, and a versioned family-specific predicate. Missing timezone, scope, or required fields yields `unknown`/insufficient, never a broad name match.
- S4-style aggregation requires an explicit `[start, end)` interval in the runtime. The frozen bare-hour oracle is not the scalable public contract.
- S1S-style passage differences preserve seconds. Do not floor or round the stored comparison to integer minutes.
- F3S-style weather matching exposes cardinality (`nearest` or `all`) and a strict `< max_minutes` boundary.
- Persist source observations and source-qualified time deltas; select `nearest|all` at query time rather than materializing two competing association sets.
- Every deterministic aggregate or comparison returns a typed derivation containing a stable ID, procedure/method version, normalized parameters, ordered input publication/source identities, result checksum, result summary, and supporting entity IDs. Aggregate answers are not unsupported prose and are not promoted to permanent semantic facts.
- Do not claim national live sector coverage. The canonical trajectory source
  is NASA's published 100-flight sample for flights departing on
  `2014-07-15`; arrivals spill into `2014-07-16`.
- Upgrade the store to `aviation-evidence-store-v2`. Do not add v1 migration or compatibility code; old stores are rebuilt from configured source artifacts.
- Kernel validation may be batched for throughput, but digest, membership, status, failure isolation, and active-publication activation are partitioned per semantic root. One malformed row must not block unrelated roots in the same chunk.
- Preserve existing TMI reason states, Weather context, public-observation semantics, source-reading guarantees, and natural-language GDP 138 flagship behavior.
- Fake/scripted providers may test software contracts only. Live acceptance must use the configured real provider. Any `live_experiment` requires at least 100 successful real calls; a smaller compatibility run must be labelled `live_smoke`.
- Optimize for complete architecture, end-to-end pipeline, and research semantics rather than production security, concurrent writers, or distributed deployment.

---

## 1. Capability, Scope, and Acceptance Contract

### Capability advanced

After a normal `ingest`, a user can ask free natural-language questions spanning:

- TMI publications and source-declared reasons;
- Flight identity, date, airport, reporting-carrier, and operational timestamps;
- Aircraft and model technical reference snapshots;
- Airport-to-ARTCC assignments with assignment role;
- actual Flight–Route–TrackPoint–Fix–Sector paths;
- METAR/SPECI observations and non-causal flight–weather time associations;
- deterministic sector traffic rankings and close-passage pairs;
- evidence-bounded TMI applicability candidates;
- exact source records, semantic graph neighbors, and provenance.

### Canonical public-sample scope

The default research prototype is the checksum-pinned NASA `atmontoPlus`
bundle, not a modern monthly BTS archive. `2014-07-15` is the only date in the
public documentary subset that combines the following layers in one NASA
artifact:

| Layer | Public sample inventory | Geographic/temporal scope |
| --- | ---: | --- |
| Flight and trajectory | 100 Flights with planned and actual routes | JFK/EWR/LGA arrivals or departures; departures on `2014-07-15`, arrival spillover through `2014-07-16T04:54:00Z` |
| METAR | 130 reports | KJFK, KEWR, and KLGA on `2014-07-15` |
| TAF | 42 reports issued on the date | KJFK, KEWR, and KLGA; 66 validity intervals overlap the date |
| ASPM AirportData | 72 airport-hour records | 24 hours for each of KJFK, KEWR, and KLGA on `2014-07-15` |
| Traffic management initiatives | 80 TMI records | all-NAS scope: 10 GDP, 16 GS, and 54 ReRoute records issued on `2014-07-15`; 114 effective intervals overlap the date |
| Aeronautical infrastructure | airport, runway, route, fix, ARTCC, and sector instances | static reference coverage bundled with atmontoPlus |

This is the public 100-flight documentary subset of ATMGRAPH, not the private
approximately 100,000-flight July 2014 graph. ASPM values are airport-hour
operational observations, not flight-level outcomes.

### Optional modern raw-source supplements

These sources exercise additional adapters and scaling paths independently.
They are not required to make the canonical public sample complete and must
not be joined to the 2014 sample merely because labels match.

| Source | Configured artifact | Optional role | Temporal domain |
| --- | --- | --- | --- |
| FAA ATCSCC | 718 processed advisory records | modern TMI ingestion supplement | 2026-05-14 to 2026-05-21 |
| BTS On-Time | May 2026 monthly ZIP | optional public Flight-operation adapter/scalability source; full archive is not the default slice | 2026-05 |
| FAA NASR | 2026-05-14 28-day ZIP | modern Airport/ARTCC reference supplement | effective 2026-05-14 to 2026-06-10 |
| FAA Aircraft Registry | 2026-07-28 release ZIP | later non-personal aircraft/model snapshot | snapshot dated 2026-07-28 |
| IEM ASOS/METAR | KATL CSV, 202 observations | modern historical-weather adapter supplement | 2026-05-14 to 2026-05-22 |

### Frozen acceptance values

These values are parity checks, not hard-coded outputs:

- Canonical public sample: 100 Flight, 130 METAR, 42 TAF, 72 ASPM
  AirportData, and 80 TMI records on `2014-07-15`.
- Canonical TMI breakdown: 10 GDP, 16 GS, and 54 ReRoute records.
- The canonical ingestion selection is issue-date based for TAF and TMI. The
  separate overlap inventories are 66 TAF validity intervals and 114 TMI
  effective intervals; these counts are not mixed with the issued-on-date
  inventory.
- Canonical flight window: departures from `2014-07-15T00:01:00Z` through
  `2014-07-15T23:59:00Z`, with arrival spillover through
  `2014-07-16T04:54:00Z`.
- ZTL airport union: 131 airports, retaining `boundary_artcc` and `responsible_artcc` as distinct assignment roles.
- Optional F1 modern proxy: 624 BTS DL-reporting A319 matches, 616 with actual wheels-off, 8 cancelled/no-wheels-off records, and 2 diverted among departed matches; origins ATL 584, CLT 31, GSO 1; 4,117 of 4,119 tail candidates match the later registry snapshot. This does not join to the 2014 sample.
- Optional F3S modern proxy: 81 KATL departures with nearest explicit-RA observation strictly under 30 minutes; the IEM source has 202 observations and 7 explicit-rain observations; `causal_claim=false`. This does not join to the 2014 sample.
- S4 published sample: `KLGAairportSector`, 12 distinct flights and 146 passage/track-point bindings during `[2014-07-15T02:00:00Z, 2014-07-15T03:00:00Z)`. The historical supplement's bare `hour == 2` result is recorded separately and is not the runtime contract.
- S1S published sample: exactly three unordered pairs in `ZTLsector040`, with time differences `0`, `1525`, and `1525` seconds.
- NASA trajectory-query acceptance slice: 100 flights, 23,300 TrackPoints,
  20,826 queryable SectorPassages, 935 explicitly typed Sector definitions,
  and 400 sector identifiers referenced by the trajectory. The runtime adds 45
  source-referenced sector roots absent from `SectorLocationInst.ttl`, yielding
  980 queryable Sector roots without claiming that all were explicitly typed
  in that member. Report these categories separately.
- Optional BTS source inventory: 611,735 monthly rows. That full count is an
  adapter/scalability check, not the default prototype ingestion target; any
  bounded BTS slice remains entirely within the 2026 temporal domain.

### Success conditions

- Every canonical atmontoPlus layer enters the normal immutable source
  registry and authoritative store; no compiled supplement report is ingested
  as knowledge.
- Optional modern source families can be ingested independently without being
  required for, or cross-linked into, the canonical 2014 public sample.
- TMI and Flight/Airspace publications share one publication/membership/provenance spine.
- Re-ingesting identical logical records is idempotent; a new source version preserves the previous immutable publication.
- A malformed record is recorded or skipped without invalidating unrelated accepted records or previously queryable knowledge.
- ATMONTO application profiles admit every formal Flight/Airspace fact; unsupported source fields stay structured, source-qualified, or non-formal.
- SQLite, RDF/Turtle, and Neo4j exports contain the same admitted formal fact identities for the selected scope.
- FTS and Chroma can be rebuilt from store records; stale/unavailable vectors do not block exact, structured, graph, or source reads.
- The Query Agent dynamically selects generic Flight/Airspace tools and produces statement-level source support in Chinese or English.
- Real-provider smoke accepts natural-language variants of all four query shapes without a fixed question registry.
- Every accepted aggregate statement cites a typed derivation, and every source-qualified association cites both participating publication versions and exact source anchors.

### Failure conditions

- Flight facts bypass the Formal Publication Kernel or lack exact publication provenance.
- The runtime reads `atmonto_competency_query_supplement_v1.json` as its data backend.
- A tool contains one of the four frozen answers or routes on one of the four question labels.
- 2014 trajectory records are joined to 2026 BTS/Weather merely because airport or carrier labels match.
- BTS reporting carrier becomes an unqualified operating-carrier fact.
- Weather proximity is worded as causation, or TMI applicability is worded as actual control/impact.
- A full batch manifest or completed export is required before previously accepted records can be queried.
- A BTS local-time value without a configured, source-supported UTC conversion participates in local-time filtering only and is excluded from UTC joins or applicability generation.
- Offline scripted results are reported as LLM/Agent acceptance.

### Explicitly deferred

- Live FAA acquisition, polling, ADS-B streaming, national current trajectories, Kafka/Celery, distributed workers, or concurrent writers.
- Decision rationale, effectiveness, optimality, and recommendation. The
  public sample's source-qualified ASPM demand, rate, delay, and operational
  observations are in scope, but they do not establish these stronger claims.
- National Playbook PDF grounding, NOTAM, TCF, CWA, SIGMET, PIREP, or new Agent roles.
- Automatic ontology expansion, unrestricted SPARQL/Cypher, causal inference, and current operational decision support.
- PostgreSQL/Neo4j as authoritative storage, production authentication, access control, hostile-input hardening, and public deployment.

---

## 2. Target Architecture and Public Interfaces

### Offline ingestion/indexing

```text
Configured source artifacts
  -> checksum and source-version registry
  -> source-specific deterministic adapters
  -> normalized source-qualified domain records
  -> ATMONTO fact compiler
  -> write-free Formal Publication Kernel
  -> atomic knowledge publication in SQLite v2
  -> source/entity chunks and FTS
  -> rebuildable Chroma source/entity index
  -> optional RDF/Turtle and Neo4j exports
```

### Online HybridRAG

```text
Natural-language question
  -> bounded LLM Query Agent
  -> model-selected exact / structured / graph / lexical / vector tools
  -> typed QueryEvidenceBundle
  -> augmented answer turn
  -> deterministic support and claim-boundary validation
  -> answer | insufficient | blocked
```

### Public CLI

Keep the current command family and expand normal ingestion:

```text
aviation-ai agent-system ingest
  --config <config>
  [--store-dir <store-dir>]
  [--domain all|tmi|flight-airspace]
  [--source-root <external-source-root>]
  [--advisory-id <id> ...]        # advanced TMI backfill only
  [--allow-live-model]
  [--allow-model-download]

aviation-ai agent-system reindex
  --config <config>
  [--store-dir <store-dir>]
  [--allow-model-download]

aviation-ai agent-system ask
  --config <config>
  [--store-dir <store-dir>]
  --question <natural-language question>
  [advanced semantic scope filters]

aviation-ai agent-system neo4j-export
  --config <config>
  [--store-dir <store-dir>]
  [--domain <domain>]
  [--start <UTC> --end <UTC>]

aviation-ai agent-system export-knowledge
  --config <config>
  [--store-dir <store-dir>]
  --root-id <semantic-root-id>
  --output-dir <output-dir>
```

`ask` never requires a source ID, Flight ID, event ID, or NASA query label from an ordinary user. IDs returned by discovery tools are internal continuation handles.

---

## 3. Batch P1A — Store v2 and General Publication Spine

**Capability:** TMI and Flight/Airspace knowledge can be published through one versioned fact/evidence backbone.

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/storage_contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/evidence_store.py`
- Modify: `src/aviation_agentic_ai/agent_system/ingestion_package.py`
- Modify: `src/aviation_agentic_ai/agent_system/evaluation_binding.py`
- Modify: `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_index.py`
- Create: `src/aviation_agentic_ai/agent_system/knowledge_publication.py`
- Create: `src/aviation_agentic_ai/agent_system/flight_airspace_contracts.py`
- Modify: `tests/test_agent_system_evidence_store.py`
- Create: `tests/test_agent_system_knowledge_publication.py`
- Create: `tests/test_agent_system_flight_airspace_contracts.py`

**Schema v2:**

```text
knowledge_roots
knowledge_publications
publication_sources
publication_facts
publication_evidence_links
knowledge_ingestion_results

tmi_events / tmi_publication_details
flights / flight_publications
air_carriers
aircraft / aircraft_models / flight_aircraft_snapshot_matches
airports / artccs / airport_artcc_assignments
navigation_fixes / sectors
routes / track_points / sector_passages
weather_observations / flight_weather_associations
flight_tmi_applicability
```

`knowledge_roots.active_publication_id` is the only active-publication pointer.
`knowledge_publications` is the only formal membership/provenance root. TMI
detail tables reference the general publication ID and retain only event-type,
facility, time, and reason-state fields. Associations are non-formal,
publication-version-bound records with separate exact evidence links and a
versioned deterministic procedure checksum.

- [ ] **Step 1:** Write failing schema tests for `aviation-evidence-store-v2`, early rejection of a v1 store before schema mutation, and all required general/domain tables.
- [ ] **Step 2:** Write failing contract tests for stable knowledge-root, publication, membership, evidence-link, derivation, Flight, Aircraft, Airport/ARTCC assignment, Route, TrackPoint, SectorPassage, Weather-association, snapshot-match, and TMI-applicability identities.
- [ ] **Step 3:** Extend `SourceFamily` and validation-layer contracts for BTS Flight operations, FAA aircraft registry, NASA ATMONTO instances, aeronautical reference, and historical METAR/SPECI while preserving current families.
- [ ] **Step 4:** Implement the general knowledge-publication DTOs; replace the old event publication/membership/evidence authority with TMI detail rows referencing the same spine, without a dual-write compatibility path.
- [ ] **Step 5:** Implement v2 initialization so an existing version mismatch is detected before any `CREATE TABLE` mutation.
- [ ] **Step 6:** Implement atomic `apply_knowledge_publication()` and `apply_knowledge_publication_batch()` with per-root partitioning, idempotent semantic facts, publication-scoped membership, multi-source evidence, generic ingestion results, exact association provenance, and one knowledge-revision increment per successful commit.
- [ ] **Step 7:** Adapt existing TMI `apply_ingestion_attempt()` to publish through the general spine while preserving event tables and current outputs.
- [ ] **Step 8:** Add structured bulk APIs and indexes for domain records without adding production migration or ORM layers. Cover Flight date/origin/destination/reporting-carrier/tail, TrackPoint route/sequence/time, SectorPassage sector/time/Flight, Weather station/time, applicability TMI/Flight publication, and ARTCC role/effective interval.
- [ ] **Step 9:** Run focused store/package tests and verify the three existing TMI reason states remain unchanged.
- [ ] **Step 10:** Commit as `refactor(agent-system): generalize the knowledge publication store`.

---

## 4. Batch P1B — ATMONTO Flight/Airspace Application Profiles

**Capability:** Flight/Airspace facts use reviewed ATMONTO classes and properties instead of an ad hoc graph vocabulary.

**Files:**

- Create: `data/ontology/curated/atmonto_flight_operation_slice.json`
- Create: `data/ontology/curated/atmonto_aeronautical_reference_slice.json`
- Create: `data/ontology/curated/atmonto_trajectory_slice.json`
- Modify: `src/aviation_agentic_ai/agent_system/validation_profiles.py`
- Modify: `src/aviation_agentic_ai/agent_system/materialize.py`
- Create: `src/aviation_agentic_ai/agent_system/flight_airspace_publication.py`
- Modify: `tests/test_agent_system_graph_kernel.py`
- Create: `tests/test_agent_system_flight_airspace_profiles.py`
- Create: `tests/test_agent_system_flight_airspace_publication.py`

**Admitted semantic core:**

```text
atm:Flight
atm:ActualFlightRoute
atm:AircraftTrackPoint
atm:NavigationFix
nas:Airport
nas:ARTCC
nas:Sector
nas:AirCarrier
eqp:Aircraft
eqp:AircraftModel
data:MeteorologicalReport
data:METARreport
data:TAFreport
data:AirportData

atm:departureAirport
atm:arrivalAirport
atm:aircraftFlown
atm:operatedBy (only with matching source semantics)
atm:hasActualRoute
gen:hasSequencedItem
atm:aircraftFix
atm:locatedInSector
atm:reportingTime
atm:actualDepartureTime
atm:callSign
nas:withinARTCC
eqp:hasAircraftModel
```

The profile uses only IRIs present in the checked ATMONTO catalog. NASA sample
records retain the exact `data:METARreport`, `data:TAFreport`, and
`data:AirportData` classes from the bundle; no project-defined Weather or
operational-metric subclass is introduced.

- [ ] **Step 1:** Write failing profile tests that derive expected IRIs, domains, and ranges independently from the implementation.
- [ ] **Step 2:** Build three small checksum-pinned profiles from the existing ATMONTO schema catalog; do not import the entire ontology as the application profile.
- [ ] **Step 3:** Extend profile loading to preserve admitted class ancestry needed for `ActualFlightRoute -> Sequence` and `AircraftTrackPoint -> SequencedItem` validation.
- [ ] **Step 4:** Compile source-qualified normalized records into `ValidatedFact` proposals with exact source traces.
- [ ] **Step 5:** Route Flight operation, aeronautical reference, and trajectory layers through `run_formal_publication_kernel()`.
- [ ] **Step 6:** Keep reporting-carrier, snapshot-match, temporal-association, and applicability semantics outside stronger ATMONTO relations when their sources do not support those relations.
- [ ] **Step 7:** Run profile/Kernel/publication tests, including rejected wrong-domain, wrong-source-family, and causal predicates.
- [ ] **Step 8:** Commit as `feat(agent-system): add ATMONTO flight and airspace profiles`.

---

## 5. Batch P1C — Deterministic Source Adapters and Full Ingestion

**Capability:** The canonical atmontoPlus layers and any explicitly selected
modern supplements are streamed into the normal store through source-specific
deterministic adapters.

**Files:**

- Create: `src/aviation_agentic_ai/agent_system/source_path_resolver.py`
- Create: `src/aviation_agentic_ai/agent_system/flight_sources.py`
- Create: `src/aviation_agentic_ai/agent_system/airspace_sources.py`
- Create: `src/aviation_agentic_ai/agent_system/flight_airspace_ingestion.py`
- Modify: `src/aviation_agentic_ai/agent_system/sources.py`
- Modify: `src/aviation_agentic_ai/agent_system/ingestion_pipeline.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: `configs/aviation_knowledge_v1.yaml`
- Modify: `configs/flight_competency_v1.yaml`
- Create: `tests/test_agent_system_flight_sources.py`
- Create: `tests/test_agent_system_airspace_sources.py`
- Create: `tests/test_agent_system_flight_airspace_ingestion.py`
- Modify: `tests/test_agent_system_ingestion_pipeline.py`
- Modify: `tests/test_cli_agent_system.py`

**Adapter responsibilities:**

- BTS: treat the monthly archive as an optional raw-source supplement. Apply an
  explicit date/geographic ingestion scope before semantic materialization,
  then preserve source row identity, Flight date, reporting carrier, flight
  number, tail, origin/destination, scheduled/actual times, cancellation,
  diversion, and explicit time basis. Full-month ingestion is an explicit
  scalability mode, not the prototype default.
- FAA registry: keep only non-personal technical fields; normalize tail number; preserve registry snapshot time and manufacturer/model reference.
- NASR: ingest all records from the explicitly configured APT/FIX/AWY source members, preserve Airport identity plus boundary and responsible ARTCC roles separately, and bind the source-scope selector to the source version. Only materialize `nas:withinARTCC` under the reviewed role mapping.
- IEM METAR/SPECI: preserve exact raw report and structured station/time/phenomenon tokens; do not infer causality.
- NASA atmontoPlus: use an explicit member allowlist for Flight, route, track
  point, fix, sector, airport, ARTCC, airline, aircraft, aircraft-model, METAR,
  TAF, ASPM AirportData, and TMI instances. Preserve member-level identity,
  source IRI, Flight, call sign, route, sequence number, TrackPoint, reporting
  time, ground speed/position when available, Fix, every sector membership,
  report validity/observation time, airport-hour interval, and TMI identity.
  Register the full ZIP asset plus canonical member-record source versions.

**Frozen identity/time rules:**

- `bts-row:<asset-checksum>:<member>:<row-number>:<row-checksum>` identifies an immutable source row. A semantic Flight root is derived only from source family, service date, reporting carrier, flight number, origin, destination, and the source-supported scheduled-departure key; collisions or missing key fields remain separate source-qualified roots.
- No cross-source or cross-version Flight merge occurs without an explicit reviewed identity mapping.
- NASA naive timestamps use the bundle's documented UTC interpretation and retain that interpretation in source metadata.
- BTS timestamps retain `origin_local` unless a configured airport timezone and date produce an unambiguous UTC conversion. Unknown/ambiguous local times are excluded from UTC joins.
- Snapshot matches, temporal associations, sector passages, and applicability candidates bind participating publication IDs, exact source versions/anchors, procedure ID/checksum, and temporal domain.
- `tmi-applicability-v1` first requires compatible temporal domains and UTC-qualified overlap. GDP/GS candidates additionally require an exact controlled-destination match and an explicit departure-scope match when the advisory declares a scope. Reroute candidates require explicit origin/destination or route-scope matches. Missing required scope/time inputs yield `unknown`; unsupported TMI families yield `not_applicable`. The result is always a candidate, never an actual-control or delay claim.

- [ ] **Step 1:** Port the existing synthetic loader tests into failing adapter tests and add missing cancellation/diversion, DST/2400, unknown-timezone, multi-sector, sequence, and source-anchor cases.
- [ ] **Step 2:** Add and test `--source-root` path resolution so ignored raw artifacts may live outside an isolated worktree without tracked machine-specific paths. External-root resolution precedes project-relative resolution, conflicts fail loudly, and the acceptance command records the chosen root without committing it.
- [ ] **Step 3:** Implement streaming BTS CSV, NASR fixed-width, FAA registry ZIP, IEM CSV, and NASA Turtle adapters. Default to the canonical 2014 NASA slice; require an explicit bounded scope or explicit scalability mode for BTS and never load its month into one Python list.
- [ ] **Step 4:** Register each raw asset checksum and one immutable canonical source version per logical row/member record; put member name, row number, raw-row checksum, parser version, time basis, and source-scope metadata on the version and create a full-record character anchor.
- [ ] **Step 5:** Implement chunked parsing plus per-root Kernel/publication partitions so a malformed record does not roll back unrelated records; do not create one cross-root `FormalPublication` digest.
- [ ] **Step 6:** Materialize domain tables and Kernel-accepted semantic facts after each accepted chunk/source publication.
- [ ] **Step 7:** Build explicit `flight_aircraft_snapshot_matches`, source observation/time-delta `flight_weather_associations`, derived `sector_passages`, and evidence-bounded `flight_tmi_applicability` candidates. Every association has exact evidence and procedure bindings; nearest/all remains a query-time selection.
- [ ] **Step 8:** Add `ingest --domain all|tmi|flight-airspace`; default `all` loads every configured domain, while an advisory selector remains an advanced TMI backfill control.
- [ ] **Step 9:** Verify idempotent re-ingest, independent source failure, source-row versus Flight-root identity, 2014/2026 temporal-domain enforcement, publication-version-bound associations, and UTC/local-time gating using fixtures.
- [ ] **Step 10:** Commit as `feat(agent-system): ingest flight and airspace knowledge`.

---

## 6. Batch P1D — Generic Structured and Graph Query Services

**Capability:** Deterministic services answer broad Flight/Airspace filters and analyses without embedding the four acceptance questions.

**Files:**

- Create: `src/aviation_agentic_ai/agent_system/flight_airspace_query.py`
- Create: `src/aviation_agentic_ai/agent_system/aviation_knowledge_graph.py`
- Modify: `src/aviation_agentic_ai/agent_system/tmi_event_graph.py`
- Create: `tests/test_agent_system_flight_airspace_query.py`
- Create: `tests/test_agent_system_aviation_knowledge_graph.py`

**Required deterministic operations:**

```text
find_flights(filters, offset, limit)
get_flight(flight_id)
find_airports(filters, offset, limit)
get_flight_route(flight_id, offset, limit)
find_sector_passages(filters, offset, limit)
rank_sector_traffic(start, end, limit)
find_close_sector_passage_pairs(sector_id, start, end, max_seconds)
find_flight_weather_associations(filters, match_mode)
find_tmi_applicability_candidates(filters)
get_semantic_neighbors(root_id, direction, predicates, limit)
```

Every aggregate/comparison operation returns a typed `QueryDerivation` with
`derivation_id`, operation, method version, normalized filters and interval,
ordered input publication/source IDs, input entity IDs, result checksum,
result summary, and bounded sample/support IDs. Its stable ID includes the
store revision, procedure version, normalized parameters, ordered inputs, and
result checksum.

- [ ] **Step 1:** Write failing query tests with hand-derived fixture counts and altered filters/intervals.
- [ ] **Step 2:** Implement SQL filters and paging for Flight, Airport/ARTCC, route, and sector-passage records.
- [ ] **Step 3:** Implement interval-based distinct-flight and passage-binding counts; do not use a bare hour-of-day contract. Freeze S4 acceptance to `[2014-07-15T02:00:00Z, 2014-07-15T03:00:00Z)`.
- [ ] **Step 4:** Implement unordered close-passage pairs with closest exact timestamps and seconds.
- [ ] **Step 5:** Implement nearest/all Weather association queries with strict boundary semantics and `causal_claim=false`.
- [ ] **Step 6:** Implement applicability-candidate reads with explicit candidate/unknown/not-applicable status, family rule/version, normalized inputs, and limitation fields; generate candidates through temporal overlap, facility/scope filtering, then the family-specific predicate.
- [ ] **Step 7:** Build a general store-backed graph view over publication facts; retain the TMI event evidence-path view as a specialized wrapper.
- [ ] **Step 8:** Verify that structured results and graph paths bind to the same accepted fact/source identities, that derivations are reproducible, and that invented graph handles are rejected unless returned by a prior discovery/structured tool.
- [ ] **Step 9:** Commit as `feat(agent-system): add flight and airspace query services`.

---

## 7. Batch P1E — Query Evidence Contracts and Generic Agent Tools

**Capability:** The existing Query Agent can dynamically discover and use Flight/Airspace knowledge with typed statement support.

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Create: `src/aviation_agentic_ai/agent_system/flight_airspace_query_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/hybrid_query_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/hybrid_query_agent.py`
- Modify: `src/aviation_agentic_ai/agent_system/knowledge_query.py`
- Modify: `src/aviation_agentic_ai/agent_system/query_runtime.py`
- Rename: `configs/prompts/tmi_event_agents_v1.yaml` to `configs/prompts/aviation_hybridrag_agents_v1.yaml`
- Modify: `src/aviation_agentic_ai/agent_system/prompts.py`
- Modify: `tests/test_agent_system_hybrid_query_agent.py`
- Create: `tests/test_agent_system_flight_airspace_query_tools.py`
- Create: `tests/test_agent_system_flight_airspace_query_agent.py`
- Modify: `tests/test_agent_system_prompt_catalog.py`

**New tool registry:**

```text
find_flights
read_flight
find_airports
read_flight_trajectory
find_sector_passages
analyze_sector_traffic
find_flight_weather_associations
find_tmi_applicability_candidates
read_aviation_graph
```

These are added to the existing TMI, source search, source read, context, observation, graph, and similarity tools.

**New statement/support kinds:**

```text
flight_fact
aircraft_fact
reference_association
snapshot_association
trajectory_fact
sector_passage
aggregate_result
temporal_association
tmi_applicability
```

**New evidence identifiers:**

```text
flight_ids
aircraft_ids
airport_artcc_assignment_ids
snapshot_match_ids
route_ids
track_point_ids
sector_passage_ids
derivation_ids
temporal_association_ids
tmi_applicability_ids
```

`QueryDerivation` objects travel with tool observations, statement support,
final outcomes, and live-evaluation artifacts. `reference_association` supports
source-qualified Airport–ARTCC role assignments; `snapshot_association`
supports later Registry snapshot matches without asserting historical aircraft
state. Scope selectors are domain-specific continuation constraints: an event
selector limits TMI reads, a Flight selector limits Flight reads, and
source-family/time scopes bound cross-domain association tools. An event scope
must not silently exclude the Flight evidence required for an explicitly
requested applicability-candidate query.

- [ ] **Step 1:** Write failing contract/Agent tests for every new statement kind and its minimum support binding.
- [ ] **Step 2:** Extend `HybridQueryEvidence`, support records, final statements, traces, and outcomes consistently; carry typed derivations end to end and generalize outcome/CLI counts beyond `events_retrieved` to bounded Flight, passage, association, and derivation totals.
- [ ] **Step 3:** Replace duplicated hand-written support-field checks with one shared table-driven support specification.
- [ ] **Step 4:** Implement the nine read-only Flight/Airspace tools as thin adapters over deterministic query services. `read_aviation_graph` accepts only a continuation handle returned by a discovery/structured tool in the current bounded run.
- [ ] **Step 5:** Keep `hybrid_query_tools.py` as registry composition rather than adding another thousand lines of domain logic.
- [ ] **Step 6:** Update the Query Agent prompt to the general aviation HybridRAG runtime, prompt version `hybrid-query-agent-v7`, new tool descriptions, new JSON contract, and exact semantic boundaries.
- [ ] **Step 7:** Verify natural-language paraphrases cause model-selected generic tools in offline orchestration tests; include one multi-domain question requiring discovery plus at least two retrieval tools within the deliberate turn/tool budget; do not claim scripted tests as Agent quality.
- [ ] **Step 8:** Verify candidate search still requires exact `read_source` before a source-record claim; verify snapshot, ARTCC-role, applicability, weather, and cross-era claim boundaries independently.
- [ ] **Step 9:** Commit as `feat(agent-system): expose flight and airspace Agent tools`.

---

## 8. Batch P1F — Rebuildable Retrieval Indexes and KG Exports

**Capability:** Flight/Airspace records participate in lexical/vector candidate discovery and in consistent RDF/Neo4j graph exports.

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/storage_contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/source_retrieval.py`
- Modify: `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_documents.py`
- Modify: `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_index.py`
- Modify: `src/aviation_agentic_ai/agent_system/evidence_export.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: `tests/test_agent_system_source_retrieval.py`
- Create: `tests/test_agent_system_flight_airspace_retrieval.py`
- Create: `tests/test_agent_system_flight_airspace_projection.py`
- Modify: `tests/test_cross_source_neo4j.py`

- [ ] **Step 1:** Generalize source chunks from `event_id` to optional `semantic_root_id`. Keep raw source-record chunks in the source collection; add separately named, versioned `flight_summary`, `trajectory_summary`, and `reference_summary` entity representations.
- [ ] **Step 2:** Add a separate `aviation_knowledge_entities` Chroma collection and `semantic_search_knowledge` discovery tool. Entity hits must be verified by `read_flight`, structured, or graph tools; they must never be passed to `read_source` as if they were source records. Bind source and entity collection states independently to the same authoritative store revision.
- [ ] **Step 3:** Ensure missing/stale Flight vectors degrade only semantic candidate discovery; structured and graph tools remain available.
- [ ] **Step 4:** Make RDF/Neo4j export enumerate general active publications, not only TMI events.
- [ ] **Step 5:** Export ATMONTO Flight–Route–TrackPoint–Fix–Sector object properties as real graph edges; preserve `predicate_iri` for general semantic relations.
- [ ] **Step 6:** Provide domain/time/root export scopes so the user does not have to export every high-frequency track point.
- [ ] **Step 7:** Verify exact formal fact-ID parity across SQLite, RDF/Turtle, and Neo4j rows for selected scopes; parity counts formal facts only.
- [ ] **Step 8:** Keep Weather temporal associations, registry snapshot matches, and TMI applicability candidates outside the formal ATMONTO projection. If exported for analysis, place them in an explicitly named auxiliary association view with separate counts and bounded predicates, never causal/actual-impact edges.
- [ ] **Step 9:** Commit as `feat(agent-system): project flight and airspace knowledge`.

---

## 9. Batch P1G — Canonical Public-Sample Parity and Supplement Cutover

**Capability:** The authoritative runtime reconstructs the complete public
`2014-07-15` NYC sample from the NASA artifact, while optional 2026 supplements
remain independently testable and outside the canonical case.

**Files:**

- Create: `scripts/run_flight_airspace_acceptance.py`
- Create: `data/evaluation/agent_system/flight_airspace_acceptance_v1.yaml`
- Create: `tests/test_agent_system_flight_airspace_acceptance.py`
- Modify: `src/aviation_agentic_ai/competency_query_supplement.py`
- Modify: `tests/test_competency_query_supplement.py`
- Modify: `ARTIFACT_INDEX.md`
- Modify: `REPRODUCIBILITY.md`

- [ ] **Step 1:** Add a local-only acceptance runner that first verifies the canonical NASA artifact checksum and records its member and selected-record counts. Verify optional-source checksums only when those supplements are explicitly selected.
- [ ] **Step 2:** Ingest the canonical public sample into a fresh ignored v2 store using `uv run aviation-ai agent-system ingest --config configs/flight_competency_v1.yaml --domain flight-airspace --source-root <main-checkout-or-raw-root>` rather than copying data into Git; record the resolved root only in ignored execution metadata.
- [ ] **Step 3:** Assert 100 Flight, 130 METAR, 42 TAF, 72 ASPM AirportData, and 80 TMI records for `2014-07-15`, plus the NASA module/member inventory and exact `0/1525/1525` second pair deltas. Run the historical ZTL/BTS and KATL/IEM parity checks separately only when their optional 2026 sources are selected; do not require 611,735 BTS rows in the default prototype store.
- [ ] **Step 4:** Assert the corrected runtime semantics: interval-based S4, exact-second S1S, explicit F3 match mode, distinct ARTCC roles, and 2014/2026 separation.
- [ ] **Step 5:** Add altered-parameter runs whose results differ from the frozen values, proving the implementation is general; include `nearest|all`, a different interval/sector, a different ARTCC, and a local-time record that is correctly excluded from a UTC join.
- [ ] **Step 6:** Retire the supplement as an active runner after parity; keep its tracked JSON/MD result as a historical migration oracle through `ARTIFACT_INDEX.md`.
- [ ] **Step 7:** Record ignored store, raw-source, parsed-output, and checksum locations in reproducibility documentation.
- [ ] **Step 8:** Commit as `test(agent-system): verify flight and airspace source parity`.

---

## 10. Batch P1H — Natural-Language and Real-Provider Acceptance

**Capability:** A real LLM dynamically routes natural-language Flight/Airspace questions to generic tools and returns evidence-bound answers.

**Files:**

- Create: `data/evaluation/agent_system/live_flight_airspace_smoke_v1.yaml`
- Create: `tests/test_agent_system_live_flight_airspace_evaluation.py`
- Modify: `src/aviation_agentic_ai/agent_system/live_agent_evaluation.py`
- Create after real run: `reports/stages/agent_system_live_flight_airspace_smoke_v1.json`
- Create after real run: `reports/stages/agent_system_live_flight_airspace_smoke_v1.md`

**Frozen real-provider tasks:**

1. Summarize the canonical `2014-07-15` sample inventory and cite the NASA bundle records supporting Flight, METAR, TAF, ASPM, and TMI counts.
2. Identify the busiest sector in the NASA sample during `[2014-07-15T02:00:00Z, 2014-07-15T03:00:00Z)` and distinguish flights from passage bindings.
3. Find unordered Flight pairs passing ZTLsector040 within 30 minutes and preserve exact time differences.
4. Read one selected Flight's Flight–Route–TrackPoint–Fix–Sector evidence path.
5. For one selected NYC airport-hour, retrieve the contemporaneous METAR, TAF, ASPM observation, and TMI records while keeping temporal association separate from causation or actual Flight impact.
6. Ask an out-of-scope causal/recommendation question that must return `insufficient` without inventing support.

The May 2026 BTS and KATL/IEM questions remain optional supplement smoke tasks;
they are never combined with the 2014 canonical tasks in one evidence claim.

- [ ] **Step 1:** Write offline evaluator tests for authorization, raw/parsed binding, tool/evidence capture, and report redaction; scripted providers are allowed only for these evaluator software tests.
- [ ] **Step 2:** Generalize the existing live evaluator and artifacts so Flight/sector/derivation evidence is valid without a required TMI event ID; do not create a parallel evaluator contract.
- [ ] **Step 3:** Freeze DeepSeek `deepseek-v4-pro`, temperature 0, thinking disabled, retry 0, prompt version, dataset/store revision, and suite checksum before the first call.
- [ ] **Step 4:** Execute one six-task `live_smoke` with the configured real provider and no fake/replay/cache fallback. Each task must activate its intended generic tool(s), return the required typed support kind, and pass evidence validation; matching prose alone is not acceptance.
- [ ] **Step 5:** Verify model ID, attempted/successful/failed calls, tokens, latency, tool calls, raw-response location/checksum, parsed-output location/checksum, and task acceptance separately.
- [ ] **Step 6:** If research metrics are requested, execute a separate `live_experiment` with at least 100 successful real calls; label repeated tasks as repeated measurements, not independent samples.
- [ ] **Step 7:** Commit only sanitized summaries; retain raw provider and parsed trial artifacts in ignored paths.
- [ ] **Step 8:** Commit as `test(agent-system): record live flight and airspace acceptance`.

---

## 11. Batch P1I — Professional Architecture, User Story, and Documentation

**Capability:** The repository tells one coherent, accurate story from heterogeneous ingestion through ATMONTO publication and Agentic HybridRAG retrieval.

**Files:**

- Modify: `docs/figures/aviation_hybridrag_system_architecture.drawio`
- Modify: `docs/figures/aviation_hybridrag_system_architecture.png`
- Create: `docs/figures/flight_airspace_knowledge_pipeline.drawio`
- Create: `docs/figures/flight_airspace_knowledge_pipeline.png`
- Create: `docs/figures/cross_source_flight_query_workflow.drawio`
- Create: `docs/figures/cross_source_flight_query_workflow.png`
- Modify: `README.md`
- Modify: `GOALS.md`
- Modify: `RESEARCH_AUDIT.md`
- Modify: `TODO.md`
- Modify: `docs/architecture_narrative.md`
- Modify: `docs/multi_agent_kg_system_design.md`
- Modify: `docs/pipeline_authority_model.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `ARTIFACT_INDEX.md`

- [ ] **Step 1:** Update the system overview to show six heterogeneous source families, deterministic adapters, the common publication spine, structured operational tables, ATMONTO KG view, FTS/Chroma, generic tools, and the bounded Query Agent.
- [ ] **Step 2:** Draw a source-to-knowledge pipeline with a single main direction, orthogonal connectors, no crossings, and explicit time-domain boundaries for 2014 and 2026.
- [ ] **Step 3:** Draw a natural-language cross-source query workflow in which the LLM selects generic tools and deterministic services perform joins/aggregates before evidence-bound generation.
- [ ] **Step 4:** Show Flight table, trajectory/sector timeline, local semantic graph, and evidence/provenance as user-facing result views without claiming a production UI.
- [ ] **Step 5:** Update active documentation from "TMI runtime with an offline supplement" to "ATMONTO-grounded heterogeneous aviation runtime with TMI and Flight/Airspace domains."
- [ ] **Step 6:** Document data volumes, source formats, temporal scopes, exact semantic boundaries, store-v2 rebuild requirement, and public CLI.
- [ ] **Step 7:** Move the supplement decision out of TODO and classify the old report as historical migration evidence.
- [ ] **Step 8:** Inspect every PNG for clipping, overlap, crooked/non-orthogonal lines, and readability; keep editable Draw.io sources paired with exports.
- [ ] **Step 9:** Commit as `docs(agent-system): document flight and airspace expansion`.

---

## 12. Execution, Review, and Final Verification

### Subagent-Driven execution rules

- Execute P1A through P1I in order because later batches depend on the store and evidence contracts.
- For each batch, use one implementer subagent on a bounded file set, then one focused read-only review. Do not start recursive reviewer loops.
- Root agent owns integration, resolves overlapping contracts, and runs focused tests after each batch.
- Mark plan checkboxes as work completes and commit each batch separately.
- Preserve unrelated user files and ignored raw/provider artifacts.

### Focused verification during implementation

```bash
uv run pytest -q tests/test_agent_system_evidence_store.py \
  tests/test_agent_system_knowledge_publication.py \
  tests/test_agent_system_flight_airspace_contracts.py

uv run pytest -q tests/test_agent_system_flight_sources.py \
  tests/test_agent_system_airspace_sources.py \
  tests/test_agent_system_flight_airspace_ingestion.py

uv run pytest -q tests/test_agent_system_flight_airspace_query.py \
  tests/test_agent_system_flight_airspace_query_tools.py \
  tests/test_agent_system_flight_airspace_query_agent.py

uv run pytest -q tests/test_agent_system_flight_airspace_projection.py \
  tests/test_agent_system_flight_airspace_acceptance.py
```

### Final repository verification

Run once after all implementation and focused review fixes:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

### Final evidence report

Report separately:

- offline software-test results;
- pinned-source parity and data counts;
- SQLite/RDF/Neo4j fact-identity consistency;
- Chroma/FTS index state;
- live-provider call success;
- live task acceptance;
- known unsupported questions and remaining data limits.

Do not merge or push until the user explicitly requests publication after reviewing the completed branch.
