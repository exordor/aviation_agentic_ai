# Storage Batch S3 Historical Case Retrieval Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add case-level embeddings and combine exact corpus filters with vector recall to retrieve similar published ATCSCC decision records from the S2 corpus.

**Architecture:** Keep `decision-case-corpus-v2` as the immutable evidence source and build a separate, rebuildable Chroma case-index sidecar bound to its `corpus_id`. A deterministic representation builder converts each `CorpusCase` into one compact decision-record document; a lazily loaded Sentence Transformers backend generates explicit normalized vectors; an embedded persistent Chroma collection stores the documents, vectors, and filter metadata; and a corpus-only search service executes metadata filtering before vector recall. The historical-similarity question remains deterministic and makes zero chat-model calls.

**Tech Stack:** Python 3.10+, Pydantic v2, JSONL, Click, ChromaDB 1.x, `sentence-transformers/all-MiniLM-L6-v2` through a new optional `case-retrieval` extra, pytest, Ruff.

## Stage Definition

| Item | Decision |
|---|---|
| Capability advanced | Retrieve structurally similar historical ATCSCC decision records from the corpus. |
| Smallest end-to-end result | Build one vector per accepted corpus case, filter candidates by exact corpus fields, and return ranked matches for one reference event. |
| Minimum components | Deterministic case-document builder, local embedding encoder, persistent Chroma collection, filtered vector search, and one corpus-backed query route. |
| Evidence | Typed unit tests plus a six-query smoke relevance set over the existing 38 accepted cases. |
| Success | 38 documents/vectors, stable filtering and ranking, zero chat-model calls, four reviewed analogues at rank one, and two unique-filter queries returning `insufficient`. |
| Failure | Corpus/index mismatch, semantic reason-state collapse, reference-case leakage, filters applied after ranking, or retrieval presented as recommendation/effectiveness evidence. |
| Deferred | Operational-situation similarity, outcome-aware ranking, managed/remote vector service, reranker, recommendation, and production hardening. |

## Subagent-Driven Execution Batches

| Batch | Tasks | Review boundary |
|---|---|---|
| S3A — Representation and vector store | Tasks 1–2 | Review document semantics, lazy dependencies, Chroma persistence, and corpus binding once after both tasks. |
| S3B — Filtered retrieval | Task 3 | Review filter-before-vector order, deterministic ranking, and zero-chat-model query behavior once. |
| S3C — Smoke evaluation and docs | Task 4 | Review the real 38-case output and active claims once before considering merge. |

Use one implementation subagent at a time because the tasks touch shared
contracts and CLI files. The primary agent reviews each batch once; do not add
extra audit passes unless a focused test exposes a semantic failure.

## Global Constraints

- Execute from a new `codex/historical-case-retrieval` branch based on S2 commit `27ab05efb244772e2fdade1d5329329ea47c6e44`; do not implement S3 from the older `main` tree.
- Use English for code, contracts, tests, CLI output, generated artifacts, and active documentation.
- This batch implements **published decision-record similarity**, not complete operational-situation similarity.
- The embedded representation contains TMI type, canonical facility, declared-reason state/value, UTC start/end time-of-day, and a deterministic operational-duration bucket.
- Do not embed advisory numbers, source/event/case IDs, absolute dates, raw source text, Weather reports, BTS observations, provenance boilerplate, or later outcomes.
- Preserve `formal`, `profile_gap`, and `missing` reason states as different representation values. A profile-gap reason remains source-supported but non-formal.
- Apply exact structured filters before vector recall. Exclude the reference case from every result.
- Vector ranking is normalized cosine similarity with a stable `case_id` tie-break. Do not add a learned reranker or a hand-tuned composite score.
- The default candidate scope is the full retrospective archive. `prior` scope admits only candidates whose operational end is earlier than the reference operational start.
- Similarity results are derived retrieval records. They do not enter `facts.jsonl`, RDF, Neo4j, or the Formal Graph Kernel.
- Use one embedded persistent Chroma collection as the S3 vector database. Do not add a separate vector-server deployment, Agent, prompt, chat-model call, community detection, LightRAG pipeline, TMI recommendation, causal claim, or production-hardening layer.
- Existing commands must continue to import and run without the `case-retrieval` extra. Import `chromadb` and `sentence_transformers` only inside S3 index/search construction.
- Unit tests inject a fake encoder and fake vector-store adapter; one focused integration test and the real smoke run use a temporary/local Chroma database. Tests never download a model or call a provider.
- Real case indexes and evaluation output remain ignored and uncommitted.
- Each task receives one focused review and one commit. Run the full suite only after all implementation tasks.

---

## Public Interfaces

Add one deterministic index command:

```text
aviation-ai agent-system index-cases
  --corpus-dir <corpus-dir>
  [--model-name sentence-transformers/all-MiniLM-L6-v2]
  [--allow-model-download]
```

Extend the existing corpus query:

```text
aviation-ai agent-system ask
  --corpus-dir <corpus-dir>
  --event-id <reference-event-id>
  --question "Which historical case is most similar?"
  [--event-type-iri <exact-iri>]
  [--facility-id <canonical-id>]
  [--reason-status formal|profile_gap|missing]
  [--reason-value <exact-value>]
  [--candidate-scope archive|prior]
  [--offset 0]
  [--limit 20]
```

Behavior:

- `archive` searches every indexed case except the reference case.
- `prior` additionally requires `candidate.operational_end < reference.operational_start`.
- `offset` and `limit` are applied after ranking.
- Missing index or an empty candidate set returns `insufficient` with zero model calls.
- An index bound to another `corpus_id`, malformed vector dimensions, or checksum-invalid index artifacts returns `blocked` before ranking.
- `--allow-live-model` does not alter this route; historical retrieval remains zero-chat-model.

Add this derived sidecar under the corpus directory:

```text
case_index/
  case_index_manifest.json
  case_documents.jsonl
  chroma/
```

`case_index_manifest.json` uses `decision-case-index-v1` and records:

```text
corpus_id
representation_version = decision-record-v1
vector_backend = chromadb
collection_name = decision_cases
distance_metric = cosine
embedding_model_id
embedding_dimension
document_count
vector_count
case_documents path / count / SHA-256
```

The sidecar manifest is written last. Rebuilding the corpus changes
`corpus_id`; the old index then becomes stale and must be rebuilt. S3 does not
change corpus v2 identity or require rerunning the 38 accepted Agent cases.
The Chroma collection metadata repeats `corpus_id`, representation version,
embedding model, and dimension; the collection configuration fixes HNSW space
to cosine. The reader compares those values with the sidecar manifest before
every similarity query.

---

### Task 1: Freeze the decision-record representation

**Files:**
- Create: `src/aviation_agentic_ai/agent_system/case_retrieval_contracts.py`
- Create: `src/aviation_agentic_ai/agent_system/case_retrieval_documents.py`
- Create: `tests/test_agent_system_case_retrieval_documents.py`

**Interfaces:**
- Consumes: `CorpusCase` and `CorpusQueryStore.cases` from `agent_system/corpus_store.py`.
- Produces:

```python
REPRESENTATION_VERSION = "decision-record-v1"

class CaseRetrievalDocument(StrictModel):
    document_id: str
    case_id: str
    event_id: str
    advisory_source_id: str
    representation_version: Literal["decision-record-v1"]
    text: str
    tmi_type_iri: str
    facility_ids: tuple[str, ...]
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None
    duration_bucket: Literal[
        "under_1_hour",
        "1_to_2_hours",
        "2_to_4_hours",
        "4_to_8_hours",
        "8_hours_or_more",
    ]
    operational_start: str
    operational_end: str

def build_case_retrieval_documents(
    store: CorpusQueryStore,
) -> tuple[CaseRetrievalDocument, ...]: ...
```

- The generated English text follows this exact field order:

```text
Traffic management measure: Ground Delay Program.
Controlled facility: KJFK.
Declared reason status: formal.
Declared reason category: weather.
Operational start time (UTC): 22:05.
Operational end time (UTC): 02:59.
Operational duration category: 4 to 8 hours.
```

- A profile gap uses `Declared reason status: profile gap.` followed by
  `Source-supported reason category: <value>.`
- A missing reason uses `Declared reason status: missing.` and emits no reason
  category line.
- `prov:Entity` is excluded when selecting the ATM TMI class.

- [ ] **Step 1: Write failing representation tests**

Add literal assertions for all three reason states and for excluded content:

```python
def test_three_reason_states_have_distinct_canonical_documents(corpus_store):
    documents = {
        row.advisory_source_id: row
        for row in build_case_retrieval_documents(corpus_store)
    }

    assert "Declared reason status: profile gap." in documents[
        "2026-05-19:123"
    ].text
    assert "Source-supported reason category: weather." in documents[
        "2026-05-19:123"
    ].text
    assert "Declared reason status: formal." in documents[
        "2026-05-19:138"
    ].text
    assert "Declared reason category: weather." in documents[
        "2026-05-19:138"
    ].text
    assert "Declared reason status: missing." in documents[
        "2026-05-20:020"
    ].text
    assert "Declared reason category:" not in documents["2026-05-20:020"].text


def test_decision_record_document_excludes_non_record_context(corpus_store):
    document = next(iter(build_case_retrieval_documents(corpus_store)))
    forbidden = (
        document.case_id,
        document.event_id,
        document.advisory_source_id,
        "METAR",
        "TAF",
        "scheduled_arrival_count",
        "cancelled_count",
        "2026-05",
    )
    assert all(value not in document.text for value in forbidden)
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
uv run pytest -q tests/test_agent_system_case_retrieval_documents.py
```

Expected: collection or import failure because the two new modules and
`build_case_retrieval_documents` do not exist.

- [ ] **Step 3: Add the contracts and minimal deterministic builder**

Implement:

```python
def _duration_bucket(start: str, end: str) -> str:
    start_time = datetime.fromisoformat(start.replace("Z", "+00:00"))
    end_time = datetime.fromisoformat(end.replace("Z", "+00:00"))
    minutes = (end_time - start_time).total_seconds() / 60
    if minutes < 60:
        return "under_1_hour"
    if minutes < 120:
        return "1_to_2_hours"
    if minutes < 240:
        return "2_to_4_hours"
    if minutes < 480:
        return "4_to_8_hours"
    return "8_hours_or_more"
```

Format the UTC clock fields from the parsed datetimes with `%H:%M`; retain no
calendar date in `text`. The full ISO boundaries remain typed document metadata
for `prior` filtering.

Map only `GroundStopTMI` and `GroundDelayProgramTMI` to their reviewed labels.
Sort cases by `case_id`, facilities lexically, and construct `document_id` with:

```python
stable_id(
    "case-retrieval-document",
    REPRESENTATION_VERSION,
    case.case_id,
    text,
)
```

Raise `ValueError` when an accepted `CorpusCase` lacks a reviewed TMI type,
facility, or operational boundary; do not create a partial document.

- [ ] **Step 4: Run focused tests and Ruff**

```bash
uv run pytest -q tests/test_agent_system_case_retrieval_documents.py
uv run ruff check \
  src/aviation_agentic_ai/agent_system/case_retrieval_contracts.py \
  src/aviation_agentic_ai/agent_system/case_retrieval_documents.py \
  tests/test_agent_system_case_retrieval_documents.py
```

Expected: all focused tests pass.

- [ ] **Step 5: Review and commit Task 1**

Review the exact document text, reason-state distinction, duration buckets,
and exclusion list. Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/case_retrieval_contracts.py \
  src/aviation_agentic_ai/agent_system/case_retrieval_documents.py \
  tests/test_agent_system_case_retrieval_documents.py
git commit -m "feat(agent-system): add case retrieval documents"
```

---

### Task 2: Build the persistent Chroma case index

**Files:**
- Modify: `src/aviation_agentic_ai/agent_system/case_retrieval_contracts.py`
- Create: `src/aviation_agentic_ai/retrieval/chroma_store.py`
- Create: `src/aviation_agentic_ai/agent_system/case_retrieval_index.py`
- Create: `tests/test_chroma_store.py`
- Create: `tests/test_agent_system_case_retrieval_index.py`
- Modify: `src/aviation_agentic_ai/retrieval/indexing.py`
- Modify: `tests/test_hybrid_retrieval.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: `src/aviation_agentic_ai/cli.py`
- Modify: `tests/test_cli_agent_system.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Consumes: `build_case_retrieval_documents()` and `CorpusQueryStore`.
- Produces:

```python
DEFAULT_CASE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

class CaseEncoder(Protocol):
    model_id: str

    def encode(
        self,
        texts: Sequence[str],
    ) -> Sequence[Sequence[float]]: ...

class CaseDocumentArtifact(StrictModel):
    path: str
    count: int
    sha256: str

class CaseIndexManifest(StrictModel):
    manifest_version: Literal["decision-case-index-v1"]
    corpus_id: str
    representation_version: Literal["decision-record-v1"]
    vector_backend: Literal["chromadb"]
    collection_name: str
    distance_metric: Literal["cosine"]
    embedding_model_id: str
    embedding_dimension: int
    document_count: int
    vector_count: int
    case_documents: CaseDocumentArtifact

class CaseVectorHit(StrictModel):
    case_id: str
    event_id: str
    advisory_source_id: str
    distance: float
    similarity: float

class SentenceTransformerCaseEncoder:
    def __init__(
        self,
        model_name: str = DEFAULT_CASE_EMBEDDING_MODEL,
        *,
        allow_download: bool = False,
    ) -> None: ...

def build_case_retrieval_index(
    corpus_dir: str | Path,
    *,
    encoder: CaseEncoder,
    index_dir: str | Path | None = None,
) -> CaseIndexManifest: ...

class ChromaCaseRetrievalIndex:
    def __init__(
        self,
        store: CorpusQueryStore,
        index_dir: str | Path,
    ) -> None: ...

    def get_case_vector(self, case_id: str) -> tuple[float, ...]: ...

    def query_candidates(
        self,
        *,
        query_vector: Sequence[float],
        candidate_case_ids: Sequence[str],
        n_results: int,
    ) -> tuple[CaseVectorHit, ...]: ...
```

- Add one thin shared backend in `retrieval/chroma_store.py` for:

```text
open/recreate PersistentClient collection
upsert explicit embeddings, documents, and scalar metadata
get one stored embedding by ID
query precomputed embeddings with a metadata where clause
convert cosine distance to similarity
```

`retrieval/indexing.py` retains its current public chunk-index functions but
delegates Chroma client lifecycle to this backend. The Agent system owns its
case-document schema and never reuses the chunk-specific `SourceChunk`
contract.

- Update both optional dependency paths to a current shared Chroma version:

```toml
[project.optional-dependencies]
graphrag = [
  "chromadb>=1.5,<2",
  "networkx>=3.2",
  "sentence-transformers>=3.0",
]
case-retrieval = [
  "chromadb>=1.5,<2",
  "sentence-transformers>=3.0",
]
```

- The encoder uses the current Sentence Transformers API:

```python
model = SentenceTransformer(
    model_name,
    local_files_only=not allow_download,
)
vectors = model.encode(
    list(texts),
    normalize_embeddings=True,
    show_progress_bar=False,
)
```

- Imports remain inside `SentenceTransformerCaseEncoder.__init__`.
- The index writer normalizes each returned vector again with standard-library
  math and validates one common non-zero dimension.
- Recreate collection `decision_cases` with `embedding_function=None` and
  cosine HNSW configuration. Collection metadata binds the index to the corpus,
  representation, model, and dimension.

```python
client = chromadb.PersistentClient(path=str(index_dir / "chroma"))
collection = client.get_or_create_collection(
    name="decision_cases",
    embedding_function=None,
    configuration={"hnsw": {"space": "cosine"}},
    metadata={
        "corpus_id": corpus_id,
        "representation_version": REPRESENTATION_VERSION,
        "embedding_model_id": encoder.model_id,
        "embedding_dimension": embedding_dimension,
    },
)
```

- Upsert the normalized vectors explicitly. Chroma IDs are stable
  `document_id` values; metadata contains scalar `case_id`, `event_id`, and
  `advisory_source_id`.
- Write sorted `case_documents.jsonl`, confirm collection count, then write
  `case_index_manifest.json` last. Do not duplicate vectors in JSONL.

- [ ] **Step 1: Write failing shared-store and case-index tests**

Reuse the current `FakeClient`/`FakeCollection` pattern from
`tests/test_hybrid_retrieval.py` to prove the shared backend receives explicit
embeddings and the candidate-ID filter. Use literal vectors in the case-index
test:

```python
class FakeEncoder:
    model_id = "test/four-dimensional"

    def encode(self, texts):
        return [
            [float(index + 1), 1.0, 0.0, 0.0]
            for index, _ in enumerate(texts)
        ]


def test_index_persists_one_normalized_vector_per_case(corpus_dir):
    store = CorpusQueryStore(corpus_dir)
    manifest = build_case_retrieval_index(
        corpus_dir,
        encoder=FakeEncoder(),
    )
    index = ChromaCaseRetrievalIndex(
        store,
        Path(corpus_dir) / "case_index",
    )

    assert manifest.corpus_id == store.manifest.corpus_id
    assert manifest.document_count == len(store.cases)
    assert manifest.vector_count == len(store.cases)
    assert manifest.embedding_dimension == 4
    assert index.collection.count() == len(store.cases)
    vector = index.get_case_vector(store.cases[0].case_id)
    assert sum(value * value for value in vector) == pytest.approx(1.0)
```

Also cover:

- repeated builds keep stable Chroma IDs and collection count;
- a temporary real Chroma collection survives reopening and returns a
  metadata-filtered cosine query;
- existing chunk indexing still delegates successfully to the shared backend;
- a sidecar bound to another `corpus_id` is rejected;
- inconsistent vector dimensions fail before manifest publication;
- importing/running existing non-index CLI commands does not import
  `chromadb` or `sentence_transformers`.

- [ ] **Step 2: Run the tests and verify RED**

```bash
uv run --extra case-retrieval pytest -q \
  tests/test_chroma_store.py \
  tests/test_agent_system_case_retrieval_index.py \
  tests/test_hybrid_retrieval.py \
  tests/test_cli_agent_system.py::test_public_agent_system_surface_is_exactly_corpus_first
```

Expected: imports fail and the public command set lacks `index-cases`.

- [ ] **Step 3: Implement the sidecar writer and reader**

Write:

```text
case_index/case_documents.jsonl
case_index/chroma/
case_index/case_index_manifest.json
```

The reader checks:

```python
if manifest.corpus_id != store.manifest.corpus_id:
    raise ValueError("case index belongs to another corpus")
```

Verify the registered document checksum, collection metadata, collection count,
and stored vector dimension. Do not checksum Chroma's internal binary files,
read source objects, or reconstruct facts during search.

- [ ] **Step 4: Add the `index-cases` CLI**

The command constructs `SentenceTransformerCaseEncoder` lazily and prints:

```text
indexed_cases: 38
vector_backend: chromadb
collection_name: decision_cases
embedding_model: sentence-transformers/all-MiniLM-L6-v2
embedding_dimension: 384
case_index_manifest: <corpus-dir>/case_index/case_index_manifest.json
```

If the optional dependency is absent, return:

```text
Install case retrieval dependencies with uv sync --extra case-retrieval.
```

If the dependency exists but the model is not cached, fail with a short
instruction to rerun with `--allow-model-download`; do not silently access the
network.

Update the top-level command metadata and its exact-surface test to include
`index-cases`.

- [ ] **Step 5: Run focused tests and Ruff**

```bash
uv run --extra case-retrieval pytest -q \
  tests/test_chroma_store.py \
  tests/test_agent_system_case_retrieval_documents.py \
  tests/test_agent_system_case_retrieval_index.py \
  tests/test_hybrid_retrieval.py \
  tests/test_cli_agent_system.py
uv run ruff check \
  src/aviation_agentic_ai/agent_system/case_retrieval_contracts.py \
  src/aviation_agentic_ai/agent_system/case_retrieval_documents.py \
  src/aviation_agentic_ai/agent_system/case_retrieval_index.py \
  src/aviation_agentic_ai/retrieval/chroma_store.py \
  src/aviation_agentic_ai/retrieval/indexing.py \
  src/aviation_agentic_ai/cli_agent_system.py \
  tests/test_chroma_store.py \
  tests/test_agent_system_case_retrieval_index.py \
  tests/test_hybrid_retrieval.py \
  tests/test_cli_agent_system.py
```

- [ ] **Step 6: Review and commit Task 2**

Review lazy imports, shared Chroma lifecycle, sidecar/corpus binding,
idempotent rebuild, cosine configuration, and absence of vectors from corpus v2
artifacts. Commit:

```bash
git add \
  pyproject.toml \
  src/aviation_agentic_ai/agent_system/case_retrieval_contracts.py \
  src/aviation_agentic_ai/agent_system/case_retrieval_index.py \
  src/aviation_agentic_ai/retrieval/chroma_store.py \
  src/aviation_agentic_ai/retrieval/indexing.py \
  src/aviation_agentic_ai/cli.py \
  src/aviation_agentic_ai/cli_agent_system.py \
  tests/test_chroma_store.py \
  tests/test_agent_system_case_retrieval_index.py \
  tests/test_hybrid_retrieval.py \
  tests/test_cli_agent_system.py
git commit -m "feat(agent-system): add persistent case vector index"
```

---

### Task 3: Combine exact filtering with vector recall

**Files:**
- Modify: `src/aviation_agentic_ai/agent_system/case_retrieval_contracts.py`
- Create: `src/aviation_agentic_ai/agent_system/case_retrieval_search.py`
- Create: `tests/test_agent_system_case_retrieval_search.py`
- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/corpus_query.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: `tests/test_agent_system_query_tool_graph.py`
- Modify: `tests/test_cli_agent_system.py`

**Interfaces:**
- Consumes: verified `CorpusQueryStore` and `ChromaCaseRetrievalIndex`.
- Add `CaseSimilarityMatch` to the existing
  `agent_system/contracts.py` file beside `QueryToolOutcome`, so the latter does
  not import the case-retrieval module.
- Add `CaseSimilarityQuery` and `CaseSimilarityResult` to
  `case_retrieval_contracts.py`. The result imports and reuses the match type
  from `contracts.py`.
- Produces:

```python
class CaseSimilarityQuery(StrictModel):
    reference_event_id: str
    candidate_scope: Literal["archive", "prior"] = "archive"
    event_type_iri: str | None = None
    facility_id: str | None = None
    reason_status: Literal["formal", "profile_gap", "missing"] | None = None
    reason_value: str | None = None
    offset: int = 0
    limit: int = 20

class CaseSimilarityMatch(StrictModel):
    rank: int
    case_id: str
    event_id: str
    advisory_source_id: str
    score: float
    tmi_type_iri: str
    facility_ids: tuple[str, ...]
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None

class CaseSimilarityResult(StrictModel):
    status: Literal["ok", "insufficient", "blocked"]
    query: CaseSimilarityQuery
    candidate_count: int
    representation_version: str
    embedding_model_id: str
    matches: tuple[CaseSimilarityMatch, ...] = ()
    limitation: str = ""

def find_similar_cases(
    store: CorpusQueryStore,
    index: ChromaCaseRetrievalIndex,
    query: CaseSimilarityQuery,
) -> CaseSimilarityResult: ...
```

- Add a defaulted field to `QueryToolOutcome`:

```python
similarity_matches: list[CaseSimilarityMatch] = Field(default_factory=list)
```

- Search order is fixed:

```text
1. Resolve the reference event.
2. Page through CorpusQueryStore exact event/facility/reason filters.
3. Exclude the reference case and apply candidate_scope.
4. Fetch the reference vector from Chroma.
5. Query Chroma with where={"case_id": {"$in": candidate_case_ids}}.
6. Convert cosine distance to similarity and apply the stable case_id tie-break.
7. Apply offset and limit to the ranked database results.
```

- [ ] **Step 1: Write failing search tests**

Use four literal cases and vectors to prove filtering occurs before ranking:

```python
def test_exact_filters_are_applied_before_cosine_ranking(store, index):
    result = find_similar_cases(
        store,
        index,
        CaseSimilarityQuery(
            reference_event_id="event:query",
            facility_id="urn:aviation-agentic-ai:facility:airport:KJFK",
            limit=3,
        ),
    )

    assert result.status == "ok"
    assert result.candidate_count == 2
    assert [row.event_id for row in result.matches] == [
        "event:kjfk-nearest",
        "event:kjfk-second",
    ]
    assert all("KJFK" in row.facility_ids[0] for row in result.matches)
    assert index.last_candidate_case_ids == (
        "case:kjfk-nearest",
        "case:kjfk-second",
    )
```

Add literal tests for:

- reference case exclusion;
- `prior` scope excluding same-time and later cases;
- score tie broken by `case_id`;
- `offset` and `limit` after ranking;
- no eligible candidates after exact filters returning `insufficient`;
- absent index returning `insufficient` at the query layer;
- stale/corrupt index returning `blocked`;
- indexed similarity making zero chat-model calls.

- [ ] **Step 2: Run the tests and verify RED**

```bash
uv run --extra case-retrieval pytest -q \
  tests/test_agent_system_case_retrieval_search.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_cli_agent_system.py
```

Expected: the search module is absent and the corpus route still returns the
S3 limitation.

- [ ] **Step 3: Implement filtered Chroma vector recall**

Use `CorpusQueryStore.find_cases()` in bounded pages to obtain every exact
candidate without changing its public pagination contract. Apply `prior` and
anchor exclusion before constructing the Chroma filter:

```python
hits = index.query_candidates(
    query_vector=reference_vector,
    candidate_case_ids=sorted(candidate_case_ids),
    n_results=min(len(candidate_case_ids), query.offset + query.limit),
)
similarity = 1.0 - cosine_distance
```

The index adapter translates `candidate_case_ids` to Chroma
`where={"case_id": {"$in": ...}}`. Chroma performs the vector ranking; Python only converts distance, applies the
stable `case_id` tie-break to the returned pool, and slices pagination. Round
only the serialized/displayed score to six decimal places. Do not apply a
minimum-score threshold or a second scoring formula.

- [ ] **Step 4: Replace only the corpus-backed S3 gate**

In `answer_corpus_question()`:

- require `event_id` for `HISTORICAL_SIMILARITY`;
- load `<corpus-dir>/case_index`;
- bind the existing exact filters, `candidate_scope`, `offset`, and `limit`;
- call `find_similar_cases`;
- return ranked `similarity_matches`, `retrieved_case_ids`, and one
  `QueryToolTrace(tool="find_similar_cases", ...)`;
- keep `model_calls=[]` and `analysis_artifact_dir=None`.

Do not modify the old run-oriented `query_plan.py` or
`case_analysis_tools.py` similarity gate. S3 is a corpus-only deterministic
capability.

The answer template is:

```text
The closest published decision record in the <scope> candidate set is
<source-id> with cosine similarity <score>. Similarity describes record
structure only; it is not a recommendation, causal explanation, or assessment
that the historical decision was effective.
```

- [ ] **Step 5: Extend CLI output**

Add `--candidate-scope archive|prior`, defaulting to `archive`. Print one line
per match:

```text
similar_case: rank=1 source_id=2026-05-19:128 score=0.941207
```

The exact registered question continues to pass the existing unsafe-wording
gate. Near-match questions and recommendation wording remain `insufficient`
with zero model calls.

- [ ] **Step 6: Run focused tests and Ruff**

```bash
uv run --extra case-retrieval pytest -q \
  tests/test_chroma_store.py \
  tests/test_agent_system_case_retrieval_documents.py \
  tests/test_agent_system_case_retrieval_index.py \
  tests/test_agent_system_case_retrieval_search.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_cli_agent_system.py
uv run ruff check .
```

- [ ] **Step 7: Review and commit Task 3**

Review anchor binding, filter order, temporal scope, deterministic ranking,
zero-chat-model behavior, and non-recommendation wording. Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/case_retrieval_contracts.py \
  src/aviation_agentic_ai/agent_system/case_retrieval_search.py \
  src/aviation_agentic_ai/agent_system/contracts.py \
  src/aviation_agentic_ai/agent_system/corpus_query.py \
  src/aviation_agentic_ai/cli_agent_system.py \
  tests/test_agent_system_case_retrieval_search.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_cli_agent_system.py
git commit -m "feat(agent-system): add filtered historical case retrieval"
```

---

### Task 4: Add a compact retrieval-quality smoke set and document S3

**Files:**
- Create: `data/evaluation/agent_system/case_retrieval_smoke_v1.yaml`
- Create: `src/aviation_agentic_ai/agent_system/case_retrieval_evaluation.py`
- Create: `tests/test_agent_system_case_retrieval_evaluation.py`
- Modify: `README.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `TODO.md`
- Modify: `RESEARCH_AUDIT.md`
- Modify: `GOALS.md`
- Modify: `docs/multi_agent_kg_system_design.md`
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: the real 38-case S2 corpus and the S3 sidecar index.
- Produces:

```python
class RetrievalSmokeMetrics(StrictModel):
    query_count: int
    ranked_query_count: int
    hit_count_at_1: int
    hit_count_at_3: int
    hit_rate_at_1: float
    hit_rate_at_3: float
    mean_reciprocal_rank: float
    expected_insufficient_count: int
    expected_insufficient_pass_count: int

def evaluate_case_retrieval_smoke(
    corpus_dir: str | Path,
    gold_path: str | Path,
) -> RetrievalSmokeMetrics: ...
```

- The tracked smoke set contains four reviewed analogues and two queries whose
  exact filters intentionally leave no candidate:

```yaml
version: case-retrieval-smoke-v1
queries:
  - query_source_id: "2026-05-20:147"
    expected_status: ok
    filters:
      event_type_iri: "https://data.nasa.gov/ontologies/atmonto/ATM#GroundDelayProgramTMI"
      facility_id: "urn:aviation-agentic-ai:facility:airport:KEWR"
      reason_status: formal
      reason_value: weather
    relevant_source_ids: ["2026-05-20:089"]
  - query_source_id: "2026-05-20:155"
    expected_status: ok
    filters:
      event_type_iri: "https://data.nasa.gov/ontologies/atmonto/ATM#GroundDelayProgramTMI"
      facility_id: "urn:aviation-agentic-ai:facility:airport:KLGA"
      reason_status: formal
      reason_value: weather
    relevant_source_ids: ["2026-05-20:158"]
  - query_source_id: "2026-05-20:129"
    expected_status: ok
    filters:
      event_type_iri: "https://data.nasa.gov/ontologies/atmonto/ATM#GroundStopTMI"
      facility_id: "urn:aviation-agentic-ai:facility:airport:KEWR"
      reason_status: profile_gap
      reason_value: weather
    relevant_source_ids: ["2026-05-20:135"]
  - query_source_id: "2026-05-19:156"
    expected_status: ok
    filters:
      event_type_iri: "https://data.nasa.gov/ontologies/atmonto/ATM#GroundStopTMI"
      facility_id: "urn:aviation-agentic-ai:facility:airport:KJFK"
      reason_status: profile_gap
      reason_value: other
    relevant_source_ids: ["2026-05-19:161"]
  - query_source_id: "2026-05-20:069"
    expected_status: insufficient
    filters:
      event_type_iri: "https://data.nasa.gov/ontologies/atmonto/ATM#GroundStopTMI"
      facility_id: "urn:aviation-agentic-ai:facility:airport:KLGA"
      reason_status: profile_gap
      reason_value: volume
  - query_source_id: "2026-05-20:020"
    expected_status: insufficient
    filters:
      event_type_iri: "https://data.nasa.gov/ontologies/atmonto/ATM#GroundDelayProgramTMI"
      facility_id: "urn:aviation-agentic-ai:facility:airport:KEWR"
      reason_status: missing
```

This is a smoke relevance set, not an expert-certified benchmark. It checks
whether obvious same-facility, same-TMI, same-reason-state record analogues are
recalled and unique exact filters abstain. It does not prove decision quality.

- [ ] **Step 1: Write failing evaluation tests**

Use a scripted index to verify:

```python
def test_smoke_metrics_compute_ranked_and_insufficient_cases(tmp_path):
    metrics = evaluate_case_retrieval_smoke(
        corpus_dir=tmp_path / "corpus",
        gold_path=tmp_path / "gold.yaml",
    )
    assert metrics.query_count == 3
    assert metrics.ranked_query_count == 2
    assert metrics.hit_count_at_1 == 1
    assert metrics.hit_count_at_3 == 2
    assert metrics.hit_rate_at_1 == pytest.approx(0.5)
    assert metrics.hit_rate_at_3 == pytest.approx(1.0)
    assert metrics.mean_reciprocal_rank == pytest.approx(0.75)
    assert metrics.expected_insufficient_count == 1
    assert metrics.expected_insufficient_pass_count == 1
```

The scripted ranked queries place their relevant cases at ranks one and two;
the third query is the expected `insufficient`. Also assert that an unknown
source ID in the smoke set blocks evaluation rather than silently reducing the
denominator.

- [ ] **Step 2: Run the tests and verify RED**

```bash
uv run pytest -q tests/test_agent_system_case_retrieval_evaluation.py
```

Expected: import failure because the evaluation module does not exist.

- [ ] **Step 3: Implement the evaluator and module entry point**

Support:

```bash
uv run --extra case-retrieval python -m \
  aviation_agentic_ai.agent_system.case_retrieval_evaluation \
  --corpus-dir <corpus-dir> \
  --gold data/evaluation/agent_system/case_retrieval_smoke_v1.yaml
```

Print canonical JSON containing all `RetrievalSmokeMetrics` fields. The
evaluator blocks if a ranked result contains the anchor or violates any
declared exact filter.

- [ ] **Step 4: Update active documentation**

Document:

- corpus v2 remains the evidence source;
- `index-cases` builds a rebuildable persistent Chroma sidecar;
- Chroma stores explicit case vectors and exact-filter candidate IDs are passed
  through its metadata `where` clause before ANN recall;
- historical similarity is published decision-record similarity;
- exact filters run before vector recall;
- similarity makes zero chat-model calls;
- results are neither recommendation nor evidence of effectiveness;
- Weather-context and operational-situation similarity remain deferred.

- [ ] **Step 5: Run focused and full verification once**

```bash
uv run --extra case-retrieval pytest -q \
  tests/test_agent_system_case_retrieval_documents.py \
  tests/test_agent_system_case_retrieval_index.py \
  tests/test_agent_system_case_retrieval_search.py \
  tests/test_agent_system_case_retrieval_evaluation.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_cli_agent_system.py

uv run ruff check .
uv run --extra case-retrieval pytest -q
uv build
git diff --check
```

- [ ] **Step 6: Build and inspect the real 38-case index**

```bash
uv run --extra case-retrieval aviation-ai agent-system index-cases \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --model-name sentence-transformers/all-MiniLM-L6-v2 \
  --allow-model-download
```

Required index result:

```text
document_count = 38
vector_count = 38
embedding_dimension = 384
vector_backend = chromadb
collection_name = decision_cases
corpus_id = 2f6ae6b1cc1ba24a4a9aca742d51d6ba4645d8e2068007102371a6d5387faf5d
```

Run one archive query and one prior-only query. Verify the reference case is
absent, every explicit filter is satisfied, scores are descending, and no chat
provider is constructed.

- [ ] **Step 7: Run the real smoke relevance set**

```bash
uv run --extra case-retrieval python -m \
  aviation_agentic_ai.agent_system.case_retrieval_evaluation \
  --corpus-dir data/corpus/agent_system/cross-source-2026-05-v2 \
  --gold data/evaluation/agent_system/case_retrieval_smoke_v1.yaml
```

Go condition:

```text
query_count = 6
ranked_query_count = 4
hit_count_at_1 = 4
hit_count_at_3 = 4
hit_rate_at_1 = 1.0
hit_rate_at_3 = 1.0
mean_reciprocal_rank = 1.0
expected_insufficient_pass_count = 2
```

If any gate fails, do not merge or document S3 as available; preserve the
feature branch and ignored index for diagnosis, and do not tune the smoke labels
or representation against the failed results in the same batch.

- [ ] **Step 8: Review and commit Task 4**

Review measured output before changing current documentation claims. Commit:

```bash
git add \
  data/evaluation/agent_system/case_retrieval_smoke_v1.yaml \
  src/aviation_agentic_ai/agent_system/case_retrieval_evaluation.py \
  tests/test_agent_system_case_retrieval_evaluation.py \
  README.md REPRODUCIBILITY.md TODO.md RESEARCH_AUDIT.md GOALS.md \
  docs/multi_agent_kg_system_design.md AGENTS.md
git commit -m "feat(agent-system): evaluate historical case retrieval"
```

---

## Acceptance Summary

S3 is complete only when:

- the 38 accepted corpus cases produce 38 deterministic record documents and
  38 normalized 384-dimensional vectors;
- a persistent Chroma collection stores all 38 vectors, uses cosine distance,
  is bound to the S2 `corpus_id`, and can be rebuilt without Agent execution;
- structured filters are applied before cosine recall;
- the reference case is never returned;
- archive/prior candidate scope is explicit in the result;
- the exact similarity question returns ranked typed matches with zero chat
  model calls;
- missing/stale indexes and empty candidate sets return honest terminal states;
- all four ranked smoke queries return the reviewed analogue at rank one and
  both unique-filter queries return `insufficient`;
- GS 123, GDP 138, and GDP 020 retain their profile-gap/formal/missing reason
  semantics;
- no vector, score, or similarity result enters formal facts, RDF, or Neo4j;
- no answer uses recommendation, causality, effectiveness, or optimality
  language.

## Explicitly Deferred

- Weather-context embedding and complete operational-situation similarity;
- ASPM demand, AAR, capacity, EDCT, and runway configuration;
- BTS outcomes as similarity features;
- advisory lifecycle or decision-episode grouping;
- natural-language query embeddings;
- learned reranking, cross-encoder reranking, and LLM similarity judgment;
- remote/managed Chroma service, Qdrant/pgvector migration, sharding,
  community detection, and LightRAG;
- case-to-case similarity edges in RDF or Neo4j;
- TMI recommendation, effectiveness comparison, and causal explanation;
- full 718-record live-model execution;
- parallel indexing and production deployment hardening.
