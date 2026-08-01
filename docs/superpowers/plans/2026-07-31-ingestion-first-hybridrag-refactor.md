# Ingestion-First Storage and HybridRAG Runtime Refactor Implementation Plan

> **Historical implemented cutover.** This plan records the migration that
> removed Corpus v2 from the runtime and established the authoritative SQLite
> evidence store. It is retained as implementation history, not as current
> instructions. Current truth is defined by `RESEARCH_AUDIT.md`, `GOALS.md`,
> and `docs/multi_agent_kg_system_design.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the batch-corpus runtime with a normal ingestion-first data system: configured aviation source artifacts are versioned, normalized, formally published, chunked, embedded, and persisted once; every natural-language query then uses the live structured store, semantic graph view, Chroma indexes, and exact source-reading tools without requiring an experiment corpus or manifest.

**Architecture:** The authoritative runtime is a small SQLite evidence store plus immutable registered source assets. The store contains source versions, normalized TMI events, Kernel-accepted semantic facts, event-scoped provenance, Weather context, BTS observations, chunks, and ingestion state. Chroma contains rebuildable source-chunk and TMI-event vectors. The graph reader is a store-backed semantic view; RDF/Turtle and Neo4j remain explicit derived exports. Online questions always activate the existing LLM Query Agent, which selects bounded exact, graph, vector, and source-reading tools, builds the existing evidence bundle, and returns only source-supported statements.

**Tech Stack:** Python 3.12, standard-library `sqlite3`, Pydantic v2, existing LangGraph/LangChain tool runtime, existing Formal Publication Kernel, existing Chroma and Sentence Transformers integration, RDF/Turtle and Neo4j export writers, pytest, Ruff, Draw.io.

## Global Constraints

- This is a breaking cutover. Do not add a corpus-v3 reader, migration command, compatibility aliases, or dual runtime.
- The normal runtime must not create or require `corpus_manifest.json`, `corpus_id`, a finalized cohort, or a persistent per-event run directory.
- Collection/downloading is not part of this refactor. Ingestion begins from the configured local source artifacts and logical records, registers their exact versions, and normalizes them.
- A source asset or logical source version is operational provenance, not an experiment snapshot. Frozen evaluation selections may reference stored version IDs but must not duplicate the runtime data.
- Preserve the ATMONTO-aligned TMI event as the semantic root. Do not reintroduce a formal `DecisionCase` wrapper.
- Preserve the Formal Publication Kernel as the only path by which semantic facts enter the authoritative store.
- Preserve the three declared-reason states: GS `123` remains `profile_gap`, GDP `138` remains formal Weather, and GDP Cancellation `020` remains `missing`.
- Weather remains a time-bounded non-causal association. BTS remains a public operational observation and must not become FAA demand, capacity, rationale, causal evidence, or decision effectiveness.
- Semantic fact identity is provenance-independent. Event membership and event-scoped evidence links are stored separately so a globally reused fact cannot leak another event's source.
- Every public `ask` invokes the configured real LLM Query Agent. There is no fixed-question registry or deterministic answer fallback.
- Vector hits discover candidates. A final factual statement must bind to exact stored facts or a bounded source version and source anchor.
- Do not add a new Agent, general planner framework, storage abstraction framework, message queue, migration framework, or production security layer.
- Stream configured JSONL records and use SQL filters/pagination; do not replace the corpus reader with another object that loads the full knowledge base into memory.
- Use fake/scripted models only for offline software tests. The final compatibility smoke must use the configured real DeepSeek provider.

---

## 1. Scope Decision

### Capability advanced

After one normal ingestion command, the user can ask a free natural-language question over all successfully ingested aviation evidence. The Query Agent may choose:

- exact TMI event and fact retrieval;
- graph edge or evidence-path retrieval;
- structured Weather and BTS retrieval;
- metadata-conditioned historical TMI event retrieval;
- semantic source-chunk retrieval;
- exact source-version reading with a stable text anchor.

No corpus build is required between ingestion and query.

### Smallest end-to-end result

For a bounded ingestion containing GS `123`, GDP `138`, and GDP Cancellation `020`:

1. Exact source text and immutable source versions are stored.
2. Each successful event is published in its own SQLite transaction.
3. The three reason states remain unchanged.
4. Textual source records and TMI event summaries are chunked and embedded into persistent Chroma collections.
5. `ask` opens the normal store, the Query Agent selects tools, and a statement can cite an exact `source_version_id + source_anchor_id`.
6. A fourth blocked record does not hide the three successful events.
7. No `corpus_manifest.json` exists or is consulted.

### Success conditions

- Re-ingesting an unchanged source version is a no-op for semantic tables and vectors.
- A revised source preserves the old immutable source version and adds a new version.
- An accepted revision atomically becomes the active semantic publication while older immutable publications remain addressable by publication ID.
- A blocked revision remains inspectable as raw evidence and an ingestion result; the last accepted semantic publication remains queryable and is clearly bound to its older accepted version.
- Missing or stale Chroma affects only vector tools; exact, graph, Weather, BTS, and source-read tools continue to work.
- Query statements cannot cite a vector hit alone and cannot cite evidence from another event.
- Active code, tests, CLI help, and current documentation contain no runtime `corpus_*`, `--corpus-dir`, `build-corpus`, or `corpus_id` contract.

### Failure conditions

- Any accepted fact bypasses the Formal Publication Kernel.
- A failed record prevents unrelated successful records from being queried.
- A source revision overwrites or deletes the old source content.
- Event-scoped provenance is inferred only by intersecting global source sets.
- Query execution requires an evaluation dataset, cohort selection, or export package.
- The final real-model smoke uses a fake, replay, response fixture, cache substitute, or deterministic answer path.

### Explicitly deferred

- Live FAA/web acquisition, polling, CDC, streaming, Kafka, Celery, or distributed workers.
- PostgreSQL, SQLAlchemy, Alembic, remote object storage, concurrent writers, and production deployment.
- General PDF chunking, National Playbook grounding, Document Grounding Agent, and OCR/visual retrieval.
- Flight trajectory, aircraft, sector, route occupancy, F1/F3S/S4/S1S completion, and new source families.
- Causal explanation, recommendation, TMI quality, effectiveness, or optimality.
- Weather/outcome-aware similarity, community detection, and full LightRAG.
- A new benchmark, a 100-call live experiment, or model-comparison claims.
- Migration of old corpus v1-v3 outputs. Re-ingest from configured source artifacts.

---

## 2. Target Runtime and Public Interfaces

### Offline ingestion pipeline

```text
Configured local source artifacts
  -> register artifact checksum and source metadata
  -> parse/normalize into immutable logical source versions
  -> deterministic preflight and authority/context preparation
  -> selective bounded Semantic Resolution Agent when genuinely ambiguous
  -> Formal Publication Kernel
  -> atomic SQLite event/fact/evidence publication
  -> source-specific chunking
  -> embedding
  -> Chroma upsert
```

SQLite publication and vector indexing are separate commit boundaries. A vector failure never rolls back accepted semantic facts; it records a stale/blocked index state that `reindex` can repair.

### Online HybridRAG pipeline

```text
Natural-language question
  -> LLM Query Agent
  -> model-selected exact / graph / vector / source tools
  -> QueryEvidenceBundle
  -> augmented answer context
  -> LLM answer generation
  -> deterministic evidence-support and claim-boundary validation
  -> answer | insufficient | blocked
```

### Public CLI after the cutover

```text
aviation-ai agent-system ingest
  --config <config>
  [--store-dir <store-dir>]
  [--source-id <logical-source-id> ...]
  [--allow-live-model]
  [--allow-model-download]

aviation-ai agent-system reindex
  --config <config>
  [--store-dir <store-dir>]
  [--model-name <embedding-model>]
  [--allow-model-download]

aviation-ai agent-system ask
  --config <config>
  [--store-dir <store-dir>]
  --question <question>
  [--source-id <logical-source-id> ...]
  [--source-family <family> ...]
  [existing event/filter/paging scope options]

aviation-ai agent-system neo4j-export
  --config <config>
  [--store-dir <store-dir>]
  [existing Neo4j connection options]

aviation-ai agent-system export-event
  --config <config>
  [--store-dir <store-dir>]
  --event-id <event-id>
  --output-dir <export-dir>
```

`ingest` processes every configured advisory by default. `--source-id` is only a bounded development/smoke selector. A later invocation skips unchanged terminal `ok/insufficient` source versions and retries unchanged `blocked` versions; there is no `--selection` or `--resume`.

### Remove from the public surface

```text
build-corpus
index-events
--corpus-dir
--output-dir as the knowledge-store identity
--selection cohort|all
--resume
```

`reindex` is a maintenance/recovery operation. Normal ingestion already chunks, embeds, and upserts changed records.

### Configuration cutover

Extend `configs/cross_source_v1.yaml` without changing the unrelated
cross-source collection/evaluation keys:

```yaml
agent_system:
  dataset_id: cross-source-2026-05-v1
  storage:
    root: data/stores/aviation/cross-source-2026-05-v1
    sqlite: aviation_evidence.sqlite3
    chroma: chroma
    exports: exports
    embedding_model: sentence-transformers/all-MiniLM-L6-v2
```

- Retain top-level `snapshot_set_id` and `cohort` because existing
  `cross_source/*` collection/alignment/evaluation code consumes them.
- The new `agent-system ingest` command ignores `cohort` and processes all 718
  advisories unless explicit source IDs bound the invocation.
- Active Agent-system documentation must describe `cohort` as an evaluation
  selector, never as a runtime publication boundary.
- Keep the existing `sources`, `source_metadata`, `source_urls`, alignment, and answering sections.
- `--store-dir` overrides `storage.root` for tests and bounded development runs.

---

## 3. Persistent Data Contracts

### New modules

- Create `src/aviation_agentic_ai/agent_system/storage_contracts.py`.
- Create `src/aviation_agentic_ai/agent_system/evidence_store.py`.

### Persistent DTOs

```python
class SourceAssetRecord(StrictModel):
    asset_id: str
    asset_key: str
    family: SourceFamily
    local_path: str
    source_url: str | None
    media_type: str
    content_sha256: str
    byte_count: int
    effective_start: str | None
    effective_end: str | None


class SourceVersionRecord(StrictModel):
    source_version_id: str
    source_id: str
    family: SourceFamily
    asset_id: str | None
    content: str
    content_sha256: str
    source_url: str | None
    logical_time: str | None
    metadata: dict[str, object]


class IngestionResult(StrictModel):
    source_version_id: str
    source_id: str
    status: Literal["ok", "insufficient", "blocked"]
    event_id: str | None
    publication_id: str | None
    reason: str
    provider_call_count: int
    tmi_family: str | None
    preflight_eligible: bool | None


class TMIEventRecord(StrictModel):
    event_id: str
    publication_id: str
    advisory_source_id: str
    publication_source_version_id: str
    event_type_iris: tuple[str, ...]
    facility_ids: tuple[str, ...]
    effective_start: datetime | None
    effective_end: datetime | None
    issued_at: datetime | None
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None


class SourceAnchorRecord(StrictModel):
    source_anchor_id: str
    source_version_id: str
    char_start: int
    char_end: int
    anchor_kind: Literal["full_record", "text_span"]


class SemanticFactRecord(StrictModel):
    fact_id: str
    subject_iri: str
    subject_class_iri: str
    predicate_iri: str
    object_kind: Literal["iri", "literal"]
    object_value: str
    object_class_iri: str | None
    datatype_iri: str | None
    validation_profile: ValidationProfileRef
    evidence_mode: Literal[
        "source_text",
        "deterministic_derivation",
        "profile_definition",
    ]


class EventEvidenceLink(StrictModel):
    evidence_link_id: str
    event_id: str
    publication_id: str
    owner_kind: Literal[
        "fact",
        "profile_gap",
        "weather_association",
        "public_observation",
    ]
    owner_id: str
    source_version_id: str
    source_anchor_id: str | None
    evidence_text: str | None
    evidence_ref: str


class SourceChunkRecord(StrictModel):
    chunk_id: str
    source_version_id: str
    event_id: str | None
    chunk_kind: Literal["source_record", "tmi_event_summary"]
    text: str
    char_start: int
    char_end: int
    source_anchor_id: str
    representation_version: str
    metadata: dict[str, object]
```

Rename the remaining corpus DTOs when ported:

```text
CorpusContextAssociation -> EventWeatherAssociation
CorpusObservation        -> PublicObservationRecord
CorpusEventFact          -> EventFactMembership
CorpusEventQuery         -> TMIEventQuery
CorpusEventPage          -> TMIEventPage
CorpusEventGraphView     -> TMIEventGraphView
```

Do not create empty compatibility subclasses.

### Stable identities

```text
asset_id
  = stable_id("source-asset", configured_asset_key, file_sha256)

source_version_id
  = stable_id("source-version", source_id, content_sha256)

source_anchor_id
  = stable_id(
      "source-anchor",
      source_version_id,
      char_start,
      char_end,
    )

event_id
  = existing stable ATMONTO TMI event identity derived from source_id + event class

publication_id
  = stable_id(
      "event-publication",
      event_id,
      publication_source_version_id,
      formal_publication_digest,
    )

fact_id
  = existing provenance-independent semantic fact identity

chunk_id
  = stable_id(
      "source-chunk",
      source_version_id,
      chunk_kind,
      char_start,
      char_end,
      representation_version,
    )
```

Retain `SourceSnapshotRegistry` only as the sealed, single-publication input to the Formal Publication Kernel. It is not the persistent store contract.

One exact `(source_version_id, char_start, char_end)` span produces one anchor.
`anchor_kind` is `full_record` only when the span covers the whole stored
content; otherwise it is `text_span`. When an evidence string occurs more than
once, select the lowest matching character offset. Missing source-text evidence
blocks package construction rather than inventing an anchor. Deterministic
derivations and profile-definition evidence retain `evidence_ref` on their
`EventEvidenceLink` but may have `source_anchor_id = None`.

### SQLite schema

Implement schema version `aviation-evidence-store-v1` with these tables:

| Table | Primary key / purpose |
|---|---|
| `store_metadata` | `key`; schema version, dataset ID, `knowledge_revision`, created/updated time |
| `ingestion_runs` | `ingestion_run_id`; operational start/end/status and compact counters |
| `source_assets` | `asset_id`; registered local file/URL/checksum metadata, no large binary BLOB |
| `sources` | `source_id`; logical identity, family, latest observed version, latest accepted version |
| `source_versions` | `source_version_id`; immutable exact logical content and metadata |
| `source_anchors` | `source_anchor_id`; exact immutable character span in one source version |
| `ingestion_results` | `source_version_id`; `ok/insufficient/blocked` and event outcome |
| `tmi_events` | `event_id`; stable TMI identity and `active_publication_id` |
| `event_publications` | `publication_id`; immutable event fields, source version, digest, publication time |
| `event_types` | `(publication_id, event_type_iri)` |
| `event_facilities` | `(publication_id, facility_id)` |
| `event_sources` | `(publication_id, source_version_id, source_role)` |
| `semantic_facts` | `fact_id`; provenance-independent formal fact |
| `event_facts` | `(publication_id, fact_id)` |
| `evidence_links` | `evidence_link_id`; includes event/publication and exact source version/optional anchor |
| `profile_gaps` | `(publication_id, gap_id)`; non-formal missing-profile evidence |
| `weather_associations` | `(publication_id, association_id)`; event/report/facility/time relation with `causal_claim = 0` |
| `public_observations` | `(publication_id, observation_id)`; event/phase/metric/value/unit/profile/source |
| `observation_facts` | `(publication_id, observation_id, fact_id)` |
| `source_chunks` | `chunk_id`; bounded text plus version/anchor/representation metadata |
| `source_chunks_fts` | SQLite FTS5 external-content index over `source_chunks.text` |
| `vector_index_state` | collection name; embedding model/dimension, indexed revision, status, counts |
| `agent_usage` | `(ingestion_run_id, source_id, role, task_scope)`; existing compact telemetry only |

Use foreign keys, explicit transactions, and deterministic `ORDER BY` clauses. Do not add a repository ORM or general migration framework.

Create ordinary indexes for source/version lookup, ingestion status, active
publication, event time, event type, facility, fact
subject/predicate/object, publication membership, evidence by
event/publication, and chunks by source version. All public list/search methods
must use bounded `LIMIT/OFFSET`; ingestion iterates source records and embeds
chunks in batches of at most 128.

### Store interface

```python
class AviationEvidenceStore:
    @classmethod
    def open(
        cls,
        root: str | Path,
        *,
        dataset_id: str,
        create: bool = False,
    ) -> "AviationEvidenceStore": ...

    def register_source_asset(
        self,
        asset: SourceAssetRecord,
    ) -> None: ...

    def register_source_version(
        self,
        version: SourceVersionRecord,
    ) -> Literal["inserted", "existing"]: ...

    def get_source_version(
        self,
        source_version_id: str,
    ) -> SourceVersionRecord | None: ...

    def get_latest_source_version(
        self,
        source_id: str,
    ) -> SourceVersionRecord | None: ...

    def get_source_anchor(
        self,
        source_anchor_id: str,
    ) -> SourceAnchorRecord | None: ...

    def apply_ingestion_attempt(
        self,
        attempt: IngestionAttempt,
    ) -> Literal["inserted", "activated", "unchanged"]: ...

    def find_tmi_events(
        self,
        query: TMIEventQuery,
    ) -> TMIEventPage: ...

    def get_event(
        self,
        event_id: str,
        *,
        publication_id: str | None = None,
    ) -> TMIEventRecord | None: ...

    def get_event_facts(
        self,
        event_id: str,
        *,
        publication_id: str | None = None,
    ) -> tuple[SemanticFactRecord, ...]: ...

    def get_event_evidence(
        self,
        event_id: str,
        *,
        publication_id: str | None = None,
    ) -> tuple[EventEvidenceLink, ...]: ...

    def get_event_weather(
        self,
        event_id: str,
    ) -> tuple[EventWeatherAssociation, ...]: ...

    def get_event_observations(
        self,
        event_id: str,
        phases: tuple[str, ...],
    ) -> tuple[PublicObservationRecord, ...]: ...

    def get_event_sources(
        self,
        event_id: str,
        *,
        publication_id: str | None = None,
    ) -> tuple[SourceVersionRecord, ...]: ...

    def search_source_text(
        self,
        query: str,
        *,
        families: tuple[SourceFamily, ...] = (),
        event_id: str | None = None,
        limit: int = 10,
    ) -> tuple[SourceChunkRecord, ...]: ...
```

`apply_ingestion_attempt` executes one transaction:

1. Confirm every referenced source version exists.
2. For `insufficient/blocked`, write only the result and latest observed source pointer.
3. For `ok`, insert an immutable `event_publication` and its types, facilities, source bindings, facts, evidence links, gaps, associations, and observations.
4. Upsert provenance-independent semantic facts without changing older publication memberships.
5. Point `tmi_events.active_publication_id` to the new publication and update `sources.latest_accepted_version_id`.
6. Write the `ok` result in the same transaction.
7. Increment `knowledge_revision` only when queryable knowledge or chunks changed.

An identical publication digest is a no-op. Older publications remain
immutable for reproducible evaluation/export; ordinary queries select only the
active publication. On any error, roll back the whole semantic publication.
The already registered immutable source version remains available, and the
pipeline records a separate blocked attempt after rollback.

---

## 4. Batch I1 — SQLite Evidence Store and Source Versions

### Files

**Create:**

- `src/aviation_agentic_ai/agent_system/storage_contracts.py`
- `src/aviation_agentic_ai/agent_system/evidence_store.py`
- `tests/test_agent_system_evidence_store.py`

**Modify:**

- `.gitignore`
- `src/aviation_agentic_ai/agent_system/contracts.py`
- `src/aviation_agentic_ai/agent_system/sources.py`
- `src/aviation_agentic_ai/config.py`
- `configs/cross_source_v1.yaml`

### TDD steps

- [ ] Add failing tests for store creation, schema version, and reopening the same dataset.
- [ ] Add a failing test that registers exact advisory content and verifies its SHA-256 and source version identity.
- [ ] Add a failing test that registers revised content under the same logical `source_id` and preserves both versions.
- [ ] Add a failing test that identical content registration is a no-op.
- [ ] Add failing tests for stable full-record/text-span anchors, duplicate-span collapse, bounded anchor reads, and rejection of an anchor from another source version.
- [ ] Add a failing transaction test for semantic publication rollback.
- [ ] Add a failing test that two events may share one semantic fact while retaining disjoint event-scoped evidence links.
- [ ] Add a failing test that two accepted revisions create immutable publications, ordinary reads select the second, and an explicit publication read reconstructs the first.
- [ ] Add a failing test that a blocked revision preserves the prior accepted publication and stores the new raw version/result.
- [ ] Implement DTOs, SQLite DDL, row conversion, deterministic ordering, and store methods.
- [ ] Add `/data/stores/` to `.gitignore`; runtime SQLite and Chroma data must never be committed.
- [ ] Add configured source-asset discovery for the ATCSCC JSONL, Weather JSONL, NASR ZIP/manifest, PCG PDF, term seed, and BTS files.
- [ ] Keep binary ZIP/PDF content in the configured files; store their project-relative path, URL, byte count, and checksum in `source_assets`.
- [ ] Store exact logical text for advisory, Weather, authority, and other text records in `source_versions`.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_evidence_store.py \
  tests/test_agent_system_multisource_contracts.py \
  tests/test_agent_system_runtime_binding.py
```

### Acceptance

- No manifest is required to open the store.
- Source revisions are immutable and queryable by version.
- Semantic facts and event evidence are separate.
- A forged or incomplete package cannot partially update the semantic store.

### Commit

```text
feat(agent-system): add persistent aviation evidence store
```

---

## 5. Batch I2 — Write-Free Publication Package and Incremental Ingestion

### Files

**Create:**

- `src/aviation_agentic_ai/agent_system/ingestion_package.py`
- `src/aviation_agentic_ai/agent_system/ingestion_pipeline.py`
- `tests/test_agent_system_ingestion_pipeline.py`

**Modify:**

- `src/aviation_agentic_ai/agent_system/workflow.py`
- `src/aviation_agentic_ai/agent_system/formal_graph.py`
- `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- `src/aviation_agentic_ai/agent_system/materialize.py`
- `src/aviation_agentic_ai/agent_system/agent_usage.py`
- `src/aviation_agentic_ai/agent_system/authority_evidence.py`
- `src/aviation_agentic_ai/agent_system/sources.py`
- `tests/test_agent_system_multisource_context.py`
- `tests/test_agent_system_public_observations.py`
- `tests/test_agent_system_reroute.py`
- `tests/test_agent_system_event_evidence_integration.py`
- `tests/test_agent_system_agent_usage.py`

### New package

```python
class EventIngestionPackage(StrictModel):
    event: TMIEventRecord
    source_version_ids: tuple[str, ...]
    source_anchors: tuple[SourceAnchorRecord, ...]
    facts: tuple[SemanticFactRecord, ...]
    event_fact_memberships: tuple[EventFactMembership, ...]
    evidence_links: tuple[EventEvidenceLink, ...]
    profile_gaps: tuple[PersistedProfileGap, ...]
    weather_associations: tuple[EventWeatherAssociation, ...]
    public_observations: tuple[PublicObservationRecord, ...]
    observation_fact_ids: dict[str, tuple[str, ...]]


class IngestionAttempt(StrictModel):
    result: IngestionResult
    package: EventIngestionPackage | None
```

`IngestionAttempt` enforces: `ok` requires a package;
`insufficient/blocked` forbid one. Only the success path can call:

```python
def build_event_ingestion_package(
    *,
    publication: FormalPublication,
    event_context: TMIEventContext,
    advisory_source_version_id: str,
    source_versions: tuple[SourceVersionRecord, ...],
    direct_fact_traces: tuple[FactTraceRow, ...],
    weather_fact_traces: tuple[WeatherFactTrace, ...],
    observation_fact_traces: tuple[ObservationFactTrace, ...],
    profile_gaps: tuple[PersistedProfileGap, ...],
    weather_associations: tuple[EventWeatherAssociation, ...],
    public_observations: tuple[PublicObservationRecord, ...],
) -> EventIngestionPackage: ...
```

The builder normalizes `FormalPublication.facts` into provenance-independent
`SemanticFactRecord` rows and uses the validated trace/sidecar inputs to create
event-publication-scoped evidence links and exact source anchors. Exporters
consume `SemanticFactRecord + EventEvidenceLink`; they must not expect
provenance fields to remain embedded in the semantic fact row. It computes the
formal publication digest and `publication_id`, then constructs the persisted
`TMIEventRecord`.

### Workflow refactor

- [ ] Add failing tests that `run_ingest` returns a typed publication package and creates no run files.
- [ ] Add failing tests that `ok` attempts require a package and `insufficient/blocked` attempts forbid one.
- [ ] Replace `IngestState.materialization` with `formal_publication` and `ingestion_package`.
- [ ] Remove `IngestContext.output_dir`; retain task/run identity only for in-memory model/tool telemetry.
- [ ] Replace `write_fact_trace` and `write_profile_gaps` calls with pure builders returning typed rows.
- [ ] Refactor `integrate_event_context` into a write-free `build_event_ingestion_package`.
- [ ] Add exact-anchor tests for direct source text, duplicate evidence text, Weather traces, profile gaps, and non-text deterministic observation derivations.
- [ ] Keep `run_formal_publication_kernel` unchanged as the final semantic authority.
- [ ] Restrict `materialize_formal_publication` to explicit export code; normal ingestion must not call it.

### Incremental pipeline

```python
def run_ingestion_pipeline(
    config: dict[str, object],
    store: AviationEvidenceStore,
    *,
    source_ids: tuple[str, ...] = (),
    allow_live_model: bool = False,
    allow_model_download: bool = False,
) -> IngestionSummary: ...
```

- [ ] Add a failing selection test: no source IDs streams all 718 configured advisories; supplied IDs bound only advisory event construction.
- [ ] Add a failing test that shared Schema Guide, authority catalog, Weather, and BTS resources load once.
- [ ] Add a failing test that every configured logical source record is registered before semantic publication.
- [ ] Add a failing test that preflight `insufficient` performs zero provider calls, stores its source version/result, and creates no event.
- [ ] Add a failing test that one blocked record does not prevent later records from being ingested.
- [ ] Add a failing test that re-running unchanged `ok/insufficient` versions skips semantic work.
- [ ] Add a failing test that unchanged `blocked` versions are retried.
- [ ] Add a failing test that an accepted revision atomically becomes active without mutating the prior publication.
- [ ] Add a failing test that a new `insufficient/blocked` revision advances the latest observed version but does not replace the latest accepted semantic publication.
- [ ] Implement sequential per-record ingestion; do not add concurrent Agent execution.
- [ ] Persist compact Agent usage to `agent_usage`; do not store prompt, raw response, tool arguments, tool results, or private reasoning.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_ingestion_pipeline.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_reroute.py \
  tests/test_agent_system_agent_usage.py
```

### Acceptance

- Each record is durable immediately after its own transaction.
- Batch completeness is not a publication condition.
- The canonical GS/GDP/Cancellation states and ReRoute mappings are unchanged.
- No persistent run bundle is produced.

### Commit

```text
refactor(agent-system): ingest publications incrementally
```

---

## 6. Batch I3 — Chunking, Embedding, and Persistent Chroma

### Files

**Create:**

- `src/aviation_agentic_ai/agent_system/source_retrieval.py`
- `tests/test_agent_system_source_retrieval.py`

**Modify:**

- `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_contracts.py`
- `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_documents.py`
- `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_index.py`
- `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_search.py`
- `src/aviation_agentic_ai/agent_system/ingestion_pipeline.py`
- `src/aviation_agentic_ai/retrieval/chroma_store.py`
- `tests/test_agent_system_tmi_event_retrieval_documents.py`
- `tests/test_agent_system_tmi_event_retrieval_index.py`
- `tests/test_agent_system_tmi_event_retrieval_search.py`
- `tests/test_chroma_store.py`

### Chunking policy v1

Use `aviation-source-chunk-v1`:

- ATCSCC advisory: one logical advisory record per chunk.
- METAR/TAF: one report/source record per chunk.
- NASR facility authority evidence: one normalized authority record per chunk.
- FAA terminology: one definition/term record per chunk.
- TMI event retrieval: one deterministic event summary per admitted event.
- BTS numeric rows remain structured observations and are not embedded in this batch.
- Large PDF/ZIP assets are registered but not chunked in this batch.

Every chunk carries exact character offsets into one `SourceVersionRecord`; generated TMI event summaries carry their formal event/fact/source bindings.

Source chunks are built independently from every newly registered textual
`SourceVersionRecord`; they are not members of `EventIngestionPackage`. TMI
event summary documents are built only after a successful formal publication.
Both collections retain immutable version/publication documents. Normal search
filters to current source versions and active TMI publications; evaluation may
bind exact historical document IDs.

### Collections and metadata

Use two persistent Chroma collections under `<store-dir>/chroma`:

```text
aviation_source_chunks_v1
tmi_events_v1
```

Replace `TMIEventIndexManifest(corpus_id=...)` with store metadata in `vector_index_state`:

```text
collection_name
representation_version
embedding_model_id
embedding_dimension
indexed_knowledge_revision
document_count
vector_count
status: current | stale | blocked
updated_at
failure_reason
```

### TDD steps

- [ ] Add failing tests for deterministic source chunks, anchors, and representation version.
- [ ] Add failing tests for incremental vector upsert, active-metadata cutover on a revised source/publication, and preservation of the old document ID.
- [ ] Add a failing test that unchanged ingestion performs zero embedding calls.
- [ ] Add a failing test that a vector error records `blocked/stale` state without rolling back SQLite publication.
- [ ] Add a failing test that a stale source index does not affect exact store reads.
- [ ] Port TMI event document building to `AviationEvidenceStore`.
- [ ] Port Chroma event similarity from `corpus_id` binding to store schema + knowledge revision.
- [ ] Implement `reindex_store` to recreate both collections from SQLite.
- [ ] Make normal ingestion upsert only changed source chunks and event summaries after SQLite commit.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_source_retrieval.py \
  tests/test_agent_system_tmi_event_retrieval_documents.py \
  tests/test_agent_system_tmi_event_retrieval_index.py \
  tests/test_agent_system_tmi_event_retrieval_search.py \
  tests/test_chroma_store.py
```

### Acceptance

- The project has an actual persistent vector database in the normal ingestion pipeline.
- Source chunk and event similarity indexes are derived and rebuildable.
- An index failure is visible but does not disable non-vector knowledge access.

### Commit

```text
feat(agent-system): index ingested aviation evidence
```

---

## 7. Batch I4 — Federated Query Runtime and Source Tools

### Files

**Create:**

- `src/aviation_agentic_ai/agent_system/query_runtime.py`
- `src/aviation_agentic_ai/agent_system/knowledge_query.py`
- `tests/test_agent_system_query_runtime.py`
- `tests/test_agent_system_source_query_tools.py`

**Rename:**

- `src/aviation_agentic_ai/agent_system/corpus_event_graph.py`
  -> `src/aviation_agentic_ai/agent_system/tmi_event_graph.py`

**Modify:**

- `src/aviation_agentic_ai/agent_system/contracts.py`
- `src/aviation_agentic_ai/agent_system/hybrid_query_tools.py`
- `src/aviation_agentic_ai/agent_system/hybrid_query_agent.py`
- `src/aviation_agentic_ai/agent_system/tmi_event_graph.py`
- `tests/test_agent_system_hybrid_query_tools.py`
- `tests/test_agent_system_hybrid_query_agent.py`
- `tests/test_agent_system_hybrid_query_public.py`
- `tests/test_agent_system_current_architecture.py`

### Runtime interface

```python
@dataclass(frozen=True)
class QueryRuntime:
    store: AviationEvidenceStore
    source_index: ChromaSourceRetrievalIndex | None
    event_index: ChromaTMIEventRetrievalIndex | None


def open_query_runtime(
    config: dict[str, object],
    *,
    store_dir: str | Path | None = None,
) -> QueryRuntime: ...


def answer_question(
    *,
    runtime: QueryRuntime,
    question: str,
    scope: HybridQueryScope,
    model_factory: ToolModelFactory,
) -> QueryToolOutcome: ...
```

`HybridQueryGateway` receives `QueryRuntime`, not a corpus reader.

Extend `HybridQueryScope` with optional `source_ids` and `source_families`.
The gateway computes the allowed source-version set:

- with `event_id`, event claims may read only versions bound to the selected
  active/specified publication through `event_sources`;
- without `event_id`, source search ranges over current source versions in the
  configured store, intersected with any CLI source/family filters;
- shared authority records may support general authority/terminology
  statements, but they may support an event statement only when that
  publication explicitly binds them;
- model tool arguments may narrow but never broaden this set.

### Existing tools to port

- `find_tmi_events`
- `read_tmi_event_facts`
- `read_tmi_operational_context`
- `read_public_observations`
- `read_tmi_event_graph`
- `find_similar_tmi_events`

This is a breaking tool-name cutover; do not retain
`read_decision_context` as an alias. The new tool documentation must say
“non-causal operational context,” not decision rationale.

### New source tools

```python
class SearchSourceTextInput(StrictModel):
    query: str
    families: tuple[SourceFamily, ...] = ()
    event_id: str | None = None
    limit: int = Field(default=10, ge=1, le=20)


class SemanticSearchSourcesInput(SearchSourceTextInput):
    pass


class ReadSourceInput(StrictModel):
    source_version_id: str
    source_anchor_id: str | None = None
    offset: int = Field(default=0, ge=0)
    max_chars: int = Field(default=6000, ge=1, le=8000)
```

Expose:

```text
search_source_text       -> SQLite FTS candidate chunks
semantic_search_sources  -> Chroma candidate chunks
read_source              -> exact bounded content and anchor
```

Both search tools return candidates, not statement support. `read_source` returns:

```text
source_id
source_version_id
source_anchor_id
family
content_sha256
bounded_text
offset/end
source_url
```

### Evidence contracts

Extend `HybridQueryEvidence`, `HybridQuerySupportRecord`, and final statement support with:

```text
source_version_ids
source_anchor_ids
chunk_ids
```

Add support kind `source_record`. A `source_record` statement must bind one exact `read_source` observation. A lexical/vector candidate alone cannot support a final statement.

### TDD steps

- [ ] Add a failing test that `ask` can run after ingestion with no corpus manifest.
- [ ] Add failing tool tests for lexical search, semantic search, and exact source read.
- [ ] Add a failing test that a vector candidate without `read_source` cannot support a final factual statement.
- [ ] Add a failing test that a source anchor from a different version or event is rejected.
- [ ] Add failing tests for event-scoped source-version access, broad current-source search, explicit source/family filters, and shared authority records used only for the permitted claim kind.
- [ ] Add a failing test that CLI scope cannot be broadened by model tool arguments.
- [ ] Add a failing test that stale/missing vector indexes yield tool-level `insufficient`, not global query failure.
- [ ] Add a failing test that the Query Agent must make at least one retrieval call before answering.
- [ ] Port exact, Weather, BTS, graph, and similarity tools to the store/runtime.
- [ ] Add the three source tools to the Query Agent prompt/tool registry without a fixed question registry.
- [ ] Replace `answer_corpus_question` with `answer_question`.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_query_runtime.py \
  tests/test_agent_system_source_query_tools.py \
  tests/test_agent_system_hybrid_query_tools.py \
  tests/test_agent_system_hybrid_query_agent.py \
  tests/test_agent_system_hybrid_query_public.py
```

### Acceptance

- Natural-language routing remains model-selected.
- Structured, graph, and vector retrieval are tools, not hard-coded question routes.
- The Query Agent can inspect exact original evidence through a bounded tool.
- Missing vector infrastructure does not disable the rest of HybridRAG.

### Commit

```text
refactor(agent-system): query the live hybrid knowledge runtime
```

---

## 8. Batch I5 — Exports, Evaluation Cutover, and Corpus Deletion

### Files

**Create:**

- `src/aviation_agentic_ai/agent_system/evidence_export.py`
- `src/aviation_agentic_ai/agent_system/evaluation_binding.py`
- `tests/test_agent_system_evidence_export.py`
- `tests/test_agent_system_evaluation_binding.py`

**Modify:**

- `src/aviation_agentic_ai/agent_system/materialize.py`
- `src/aviation_agentic_ai/agent_system/tmi_event_retrieval_evaluation.py`
- `src/aviation_agentic_ai/agent_system/live_agent_evaluation.py`
- `src/aviation_agentic_ai/agent_system/live_agent_experiment.py`
- `src/aviation_agentic_ai/cli_agent_system.py`
- `src/aviation_agentic_ai/cli.py`
- `tests/test_agent_system_corpus_projection.py` before port/delete
- `tests/test_agent_system_tmi_event_retrieval_evaluation.py`
- `tests/test_agent_system_live_evaluation.py`
- `tests/test_agent_system_live_experiment.py`
- `tests/test_cli_agent_system.py`

### Explicit exports

```python
def export_event(
    store: AviationEvidenceStore,
    event_id: str,
    output_dir: str | Path,
) -> Path: ...


def build_store_kg_projection(
    store: AviationEvidenceStore,
    output_dir: str | Path,
) -> KGProjection: ...
```

- RDF/Turtle and Neo4j files are generated from active store facts and exact event-scoped provenance.
- `neo4j-export` generates a temporary/current projection from the store and loads it with existing parameterized MERGE behavior.
- `export-event` contains only the selected event, its facts, evidence, context, observations, and referenced source versions.
- Exports may have a checksum manifest because they are bounded export artifacts. That manifest never becomes a query prerequisite.

### Evaluation binding

```python
class EvaluationVectorBinding(StrictModel):
    collection_name: str
    representation_version: str
    embedding_model_id: str
    embedding_dimension: int
    indexed_knowledge_revision: int
    document_ids: tuple[str, ...]


class EvaluationDataBinding(StrictModel):
    store_schema_version: str
    dataset_id: str
    knowledge_revision: int
    required_source_versions: dict[str, str]
    required_source_hashes: dict[str, str]
    required_event_publication_ids: tuple[str, ...]
    source_candidate_version_ids: tuple[str, ...]
    event_candidate_publication_ids: tuple[str, ...]
    source_vector_index: EvaluationVectorBinding
    event_vector_index: EvaluationVectorBinding
    validation_profile_checksums: tuple[str, ...]
```

- Query evaluation opens the normal store and selects required version/event IDs.
- It never builds a temporary query corpus.
- Before any provider call, verify the exact source-version, event-publication,
  candidate, Chroma document, index metadata, and knowledge-revision bindings.
- Verify the store `knowledge_revision` is unchanged after the evaluation; a
  concurrent/change mismatch invalidates the run rather than silently changing
  its retrieval universe.
- Assembly/ingestion trials may use a temporary work directory for raw provider artifacts, but that directory is not a Query Agent backend.
- Missing required versions yields `blocked_before_run`.
- Historical tracked reports remain unchanged and clearly historical.

### Delete after all callers are ported

- `src/aviation_agentic_ai/agent_system/corpus_query.py`
- `src/aviation_agentic_ai/agent_system/corpus_batch.py`
- `src/aviation_agentic_ai/agent_system/corpus_store.py`
- `src/aviation_agentic_ai/agent_system/runtime.py::create_run_binding`
- `src/aviation_agentic_ai/agent_system/runtime.py::write_run_manifest`
- `src/aviation_agentic_ai/agent_system/query_tools.py::QueryGraphStore`
- old corpus-only helpers in `context_artifacts.py` and `materialize.py`

Delete or port these test containers only after their semantic assertions exist in new tests:

- `tests/test_agent_system_corpus_store.py`
- `tests/test_agent_system_corpus_batch.py`
- `tests/test_agent_system_corpus_projection.py`
- `tests/test_agent_system_corpus_event_graph.py`

### TDD and deletion steps

- [ ] Add failing export tests for event isolation and exact source versions.
- [ ] Add a failing export test that source-text anchors and anchorless deterministic/profile evidence refs survive normalization.
- [ ] Add a failing test that full KG export facts equal active store facts.
- [ ] Add a failing test that Weather associations remain outside the formal KG unless represented by already admitted formal Weather facts.
- [ ] Add failing evaluation tests that query trials use an existing store and never build a corpus.
- [ ] Add a failing test that missing required source versions blocks before provider calls.
- [ ] Add a failing test that either Chroma collection/candidate mismatch or a store revision change invalidates the evaluation before metrics are accepted.
- [ ] Port Neo4j, RDF, event export, retrieval evaluation, live smoke, and live experiment.
- [ ] Atomically cut all five public commands to `ingest`, `reindex`, store-backed `ask`, store-backed `neo4j-export`, and store-backed `export-event`.
- [ ] In the same commit, remove `build-corpus`, `index-events`, and every `--corpus-dir` option; test every public command before deleting old modules.
- [ ] Search all production imports and delete corpus modules in dependency order.
- [ ] Run an active-tree scan:

```bash
git grep -nE \
  'CorpusQueryStore|CorpusBuildManifest|corpus_manifest|corpus_id|build-corpus|--corpus-dir' \
  -- \
  'src/**' 'tests/**' 'README.md' 'GOALS.md' 'RESEARCH_AUDIT.md' \
  'REPRODUCIBILITY.md' 'TODO.md' 'AGENTS.md' \
  'docs/multi_agent_kg_system_design.md'
```

Expected result: no active runtime contract matches. Historical plans, specs, archived documents, and frozen reports are excluded from this scan and are not rewritten.

- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_evidence_export.py \
  tests/test_agent_system_evaluation_binding.py \
  tests/test_agent_system_tmi_event_retrieval_evaluation.py \
  tests/test_agent_system_live_evaluation.py \
  tests/test_agent_system_live_experiment.py \
  tests/test_cli_agent_system.py
```

### Acceptance

- Exports are optional products of the runtime store.
- Evaluations bind to existing data without copying it into a runtime snapshot.
- No old corpus code remains reachable.

### Commit

```text
refactor(agent-system): remove the corpus runtime
```

---

## 9. Batch I6 — Documentation, Figures, Bounded Ingestion, Real Query Smoke, and Final Verification

### Files

**Modify:**

- `AGENTS.md`
- `README.md`
- `GOALS.md`
- `RESEARCH_AUDIT.md`
- `REPRODUCIBILITY.md`
- `TODO.md`
- `ARTIFACT_INDEX.md`
- `docs/multi_agent_kg_system_design.md`
- `docs/figures/tmi_event_construction_architecture.drawio`
- `docs/figures/tmi_event_construction_architecture.png`
- `docs/figures/tmi_event_retrieval_architecture.drawio`
- `docs/figures/tmi_event_retrieval_architecture.png`
- `tests/test_readme_commands.py`

**Create:**

- `data/evaluation/agent_system/live_ingestion_hybridrag_smoke_v1.yaml`
- sanitized live-smoke JSON/Markdown reports under `reports/stages/`

Do not rewrite historical plans, specifications, archived documents, or frozen old evaluation reports.

### Documentation model

Construction figure:

```text
Source artifacts
  -> parse / normalize
  -> source versions
  -> bounded semantic processing
  -> Formal Publication Kernel
  -> SQLite evidence + semantic store
  -> chunks / embeddings
  -> Chroma
```

Retrieval figure:

```text
Question
  -> LLM Query Agent
  -> exact store | semantic graph | Chroma | source read
  -> QueryEvidenceBundle
  -> LLM generation
  -> support validation
  -> answer
```

RDF/Turtle and Neo4j appear as offline exports from the authoritative store, not as mandatory runtime databases.

### Bounded ingestion smoke

```bash
uv run aviation-ai agent-system ingest \
  --config configs/cross_source_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --source-id 2026-05-19:123 \
  --source-id 2026-05-19:138 \
  --source-id 2026-05-20:020 \
  --allow-live-model \
  --allow-model-download
```

Verify:

- the store opens without a manifest;
- all three source versions exist;
- their reason states remain `profile_gap`, formal Weather, and `missing`;
- source chunks and TMI event vectors exist;
- no causal or recommendation fact appears.

The three canonical records normally use deterministic ingestion paths. The
presence of `--allow-live-model` is authorization only and does not turn this
into a model evaluation. If the configured dataset still contains no natural
Semantic Resolution ambiguity, report that role as
`not_evaluated_no_natural_ambiguity`.

Use a small real Query Agent suite with free natural-language questions; every
suite item must call the configured real provider. At least one question must
require `semantic_search_sources -> read_source`, one must use formal
graph/exact facts, and one must use Weather or BTS context. The product
contains no matching fixed-question route.

```bash
uv run python -m aviation_agentic_ai.agent_system.live_agent_evaluation \
  --config configs/cross_source_v1.yaml \
  --suite data/evaluation/agent_system/live_ingestion_hybridrag_smoke_v1.yaml \
  --store-dir data/stores/aviation/ingestion-refactor-smoke-v1 \
  --output-dir data/evaluation/agent_system/live-ingestion-hybridrag-smoke-v1 \
  --report-dir reports/stages \
  --allow-live-model
```

Record the observed provider/model, attempted/successful/failed calls, token use, tool calls, latency, raw artifact location, parsed artifact location, and task acceptance separately. This is `live_smoke`, not a statistical benchmark.

### Final steps

- [ ] Update all current commands, diagrams, and architecture wording.
- [ ] Visually inspect both exported PNGs for clipping, overlap, and crossed connectors.
- [ ] Run the bounded real ingestion and Query Agent smoke once.
- [ ] Run focused ingestion/runtime tests.
- [ ] Run final repository verification once:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

- [ ] Confirm the Git worktree contains only approved code, tests, docs, figures, and sanitized live-smoke reports.

### Commit

```text
docs(agent-system): document ingestion-first HybridRAG
```

---

## 10. Safe Execution and Review Order

Use Subagent-Driven execution with non-overlapping ownership:

1. One implementation subagent handles Batch I1 storage contracts/schema.
2. After review and commit, one subagent handles Batch I2 publication/ingestion.
3. After review and commit, one subagent handles Batch I3 chunk/vector indexing.
4. After review and commit, one subagent handles Batch I4 query runtime/CLI.
5. After review and commit, one subagent handles Batch I5 exports/evaluation/deletion.
6. The main agent owns Batch I6 documentation, Draw.io verification, real-provider smoke, and final verification.

For each batch:

- review the changed behavior once;
- fix only observed acceptance failures;
- run the listed focused tests;
- commit the batch;
- do not begin recursive reviewer/fixer cycles.

Do not delete an old module until `rg` shows every production caller has moved and the corresponding semantic assertions pass in the replacement tests.

## 11. Completion Checklist

- [ ] Normal ingestion persists all configured source families and per-source results.
- [ ] Successfully published events are queryable immediately and independently.
- [ ] Raw/logical source versions remain exact, immutable, and directly readable.
- [ ] Kernel-accepted semantic facts are stored independently from event membership and provenance.
- [ ] SQLite FTS, Chroma source chunks, TMI event similarity, and semantic graph views are operational.
- [ ] The LLM Query Agent routes every natural-language question.
- [ ] Final statements bind exact facts or source-version anchors.
- [ ] Evaluation selects stored versions; it does not build a runtime corpus.
- [ ] RDF/Turtle, Neo4j, and event packages are explicit exports.
- [ ] No active corpus runtime or compatibility path remains.
- [ ] Real DeepSeek smoke and final repository verification pass or are reported with their actual observed failure.
