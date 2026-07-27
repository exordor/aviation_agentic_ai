# Decision Case Graph v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the approved BTS-reported operational observations as checksum-verifiable formal knowledge-graph facts, preserve the three ATCSCC reason states, and make the resulting observations available through bounded read-only query tools.

**Architecture:** The existing deterministic BTS adapter remains the only calculator. It emits source summaries and immutable derivation seeds in one pass. A separate deterministic builder validates those inputs against a multi-profile registry, creates SOSA/SSN, OWL-Time, PROV-O, QUDT, SKOS, and `case:` facts, and returns typed traces. The formal materializer validates every fact against its owning profile and evidence mode before producing JSONL, RDF, and explicit Neo4j projections. Query tools read only the validated formal graph and its audit artifacts.

**Tech Stack:** Python 3.11+, Pydantic, rdflib, JSONL, pytest, Neo4j projection

## Global Constraints

- Work only in the isolated `codex/decision-case-graph-v1` worktree.
- Preserve the user-owned untracked test file in the main checkout.
- Use English for code, contracts, tests, artifacts, messages, and active documentation.
- Use source-qualified `BTS-reported` terminology. Do not map BTS fields to FAA Arrival Demand, AAR, capacity, EDCT, or ATCSCC reasons.
- Keep the existing ATCSCC, Weather, and public operational observation semantic layers separately owned and separately validated.
- Do not add an Agent, LLM parsing step, model call, graph-write tool, causal predicate, recommendation, lifecycle link, ASPM field, or visualization change.
- Follow strict RED-GREEN-REFACTOR for every behavior. A failing test must be observed before production code is changed.
- Commit each completed task separately. Do not push or merge.
- Every new run must persist explicit profile ownership and evidence references. Legacy ownership synthesis is read-only and cannot enter publication paths.
- A blocked observation layer must leave validated ATCSCC and Weather facts queryable.
- A declared-reason query must never open Weather or BTS observation artifacts.

---

## Task 1: Add Explicit Validation-Profile Ownership

**Files:**

- Create: `src/aviation_agentic_ai/agent_system/validation_profiles.py`
- Create: `data/ontology/curated/decision_case_public_observation_slice.json`
- Create: `tests/test_agent_system_public_observations.py`
- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/formal_graph.py`
- Modify: `src/aviation_agentic_ai/agent_system/weather_context.py`
- Modify: `src/aviation_agentic_ai/agent_system/weather_context_validation.py`
- Modify: focused test fixtures that construct `ValidatedFact`

### Interfaces

```python
class ValidationProfileRef(StrictModel):
    profile_id: str
    profile_checksum: str
    layer: Literal[
        "decision",
        "weather",
        "public_operational_observation",
    ]


class LoadedValidationProfile(StrictModel):
    ref: ValidationProfileRef
    source_path: str
    namespace_prefixes: dict[str, str]
    class_mappings: dict[str, dict[str, str]]
    property_mappings: dict[str, dict[str, str]]
    forbidden_predicates: tuple[str, ...] = ()


class ValidationProfileRegistry:
    def resolve(self, ref: ValidationProfileRef) -> LoadedValidationProfile: ...
    def require_layer(
        self,
        ref: ValidationProfileRef,
        layer: Literal[
            "decision",
            "weather",
            "public_operational_observation",
        ],
    ) -> LoadedValidationProfile: ...


def load_validation_profile_registry(
    *,
    decision_guide: SchemaGuide,
    weather_profile_path: str | Path = DEFAULT_WEATHER_PROFILE_PATH,
    public_observation_profile_path: str | Path = (
        DEFAULT_PUBLIC_OBSERVATION_PROFILE_PATH
    ),
) -> ValidationProfileRegistry: ...
```

Extend the writable `ValidatedFact` contract:

```python
validation_profile: ValidationProfileRef
evidence_mode: Literal[
    "source_text",
    "deterministic_derivation",
    "profile_definition",
    "system_membership",
]
evidence_ref: str
```

Legacy decoding uses a separate read-only legacy contract and adapter. The
writable `ValidatedFact` model never permits missing ownership or an empty
evidence reference.

### Steps

- [ ] Write tests proving that the registry:
  - verifies the file checksum before loading a profile;
  - resolves one exact profile ID, checksum, and layer;
  - rejects unknown IDs, duplicate IDs, wrong checksums, wrong layers, malformed mappings, and forbidden predicates;
  - loads independent decision, Weather, and public-observation profiles.
- [ ] Write tests proving that new ATCSCC and Weather facts carry their own `ValidationProfileRef`, `evidence_mode="source_text"`, and a trace-addressable `evidence_ref`.
- [ ] Write a test proving that a legacy fact can be decoded through an explicitly named read-only adapter but is rejected by the new publication validator.
- [ ] Run the focused tests and confirm RED:

```bash
uv run pytest -q \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_graph_kernel.py \
  tests/test_agent_system_multisource_context.py
```

Expected: imports or assertions fail because profile contracts and ownership do not yet exist.

- [ ] Implement the profile contracts and immutable registry.
- [ ] Add the observation profile with:
  - approved namespace prefixes;
  - the classes and predicates in the approved design;
  - the nine metric definitions;
  - `unit:NUM` for counts and `unit:MIN` for minute values;
  - the pinned deterministic aggregation procedure ID and checksum;
  - the forbidden NASA operational and causal predicates;
  - no property-equivalence or subproperty mappings to FAA operational properties.
- [ ] Stamp new ATCSCC and Weather facts with their owning profile references and exact source-trace references.
- [ ] Add the isolated read-only legacy adapter. Do not call it from validation, writing, or materialization paths.
- [ ] Run the focused tests and confirm GREEN.
- [ ] Run:

```bash
uv run ruff check .
git diff --check
```

- [ ] Commit:

```bash
git add \
  data/ontology/curated/decision_case_public_observation_slice.json \
  src/aviation_agentic_ai/agent_system/contracts.py \
  src/aviation_agentic_ai/agent_system/validation_profiles.py \
  src/aviation_agentic_ai/agent_system/formal_graph.py \
  src/aviation_agentic_ai/agent_system/weather_context.py \
  src/aviation_agentic_ai/agent_system/weather_context_validation.py \
  tests
git commit -m "feat(agent-system): add formal fact profile ownership"
```

---

## Task 2: Emit BTS Derivation Seeds in the Existing Aggregation Pass

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/bts_outcomes.py`
- Modify: `src/aviation_agentic_ai/agent_system/sources.py`
- Modify: `src/aviation_agentic_ai/agent_system/validation_profiles.py`
- Modify: `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: direct query readers and tests only to migrate the retired summary field
- Modify: current Decision Record Explorer design wording for the same migration
- Modify: `tests/test_agent_system_bts_outcomes.py`
- Modify: `tests/test_agent_system_multisource_contracts.py`

### Interfaces

```python
class BTSOutcomeSummary(StrictModel):
    summary_id: str
    run_id: str
    event_id: str
    facility_id: str
    phase: Literal["baseline", "active", "recovery"]
    window_start: datetime
    window_end: datetime
    source_id: str
    source_snapshot_sha256: str
    scheduled_arrival_count: int
    completed_arrival_count: int
    cancelled_count: int
    diverted_count: int
    arrival_delay_15_count: int
    mean_arrival_delay_minutes: float | None
    median_arrival_delay_minutes: float | None
    carrier_reported_weather_delay_minutes: float | None
    carrier_reported_nas_delay_minutes: float | None
    reporting_scope: Literal[
        "BTS On-Time reporting carriers and scheduled domestic passenger operations."
    ]
    causal_claim: Literal[False]


class ObservationDerivationSeed(StrictModel):
    derivation_id: str
    summary_id: str
    summary_sha256: str
    source_id: str
    source_snapshot_sha256: str
    archive_sha256: str
    aggregation_procedure_id: str
    aggregation_procedure_checksum: str
    selected_row_ids: tuple[str, ...]
    selected_row_ids_sha256: str


class BTSOutcomeBundle(StrictModel):
    status: Literal["ok", "insufficient", "blocked"]
    summaries: list[BTSOutcomeSummary]
    derivation_seeds: list[ObservationDerivationSeed]
    failure_reason: str
```

`build_bts_outcome_summaries` remains the sole calculator and accepts the pinned archive and procedure identifiers needed for seed creation. It emits one summary and one seed per phase in the same row-selection pass.

`load_bts_context_source` returns a typed manifest binding alongside the source
record and rows. The CLI carries that binding into `IngestContext`, and the
context integration passes its archive and normalized checksums explicitly to
the adapter. The procedure ID and checksum come from the checksum-verified
public-observation profile; the adapter has no independent conflicting
procedure constant.

### Steps

- [ ] Replace active tests and fixtures with `scheduled_arrival_count` and the exact `reporting_scope`.
- [ ] Add RED tests proving:
  - the KJFK Ground Stop 123 active phase reports scheduled `20`, completed `18`, cancelled `2`, and diverted `0`;
  - the KJFK GDP 138 active phase reports scheduled `77`, completed `68`, cancelled `4`, and diverted `5`;
  - the KEWR cancellation 020 active phase reports scheduled `50`, completed `49`, cancelled `1`, and diverted `0`;
  - one seed is emitted per phase;
  - selected row IDs are sorted before hashing;
  - summary and selected-row hashes are byte-stable;
  - a changed archive, source snapshot, procedure ID, procedure checksum, or selected row changes the appropriate digest or blocks the bundle;
  - null delay aggregates remain null and reported zero counts remain zero.
- [ ] Add tests for duplicate natural keys, wrong ZIP/member/normalized checksums, an empty terminal CSV column, DST, cross-midnight arrival-day derivation, and half-open phase boundaries.
- [ ] Run and confirm RED:

```bash
uv run pytest -q \
  tests/test_agent_system_bts_outcomes.py \
  tests/test_agent_system_multisource_contracts.py
```

- [ ] Implement the contract migration and seed emission without a second raw-row pass.
- [ ] Read the archive and normalized-snapshot checksums from the pinned BTS manifest.
- [ ] Cross-check the aggregation procedure ID and checksum against the
  checksum-verified public-observation profile before emitting any seed.
- [ ] Derive stable IDs only from canonical serialized inputs.
- [ ] Ensure the bundle returns:
  - `insufficient` for a valid source with no selected rows;
  - `blocked` for checksum, schema, time, identity, or duplicate-key failures.
- [ ] Run the focused tests and confirm GREEN.
- [ ] Scan active code, messages, and contracts for retired field or demand-language remnants:

```bash
git grep -n -i 'scheduled_arrival_count_\\|public scheduled-demand' -- \
  src/aviation_agentic_ai/agent_system \
  tests/test_agent_system*.py \
  data/ontology/curated \
  data/sources/bts_on_time_2026_05_manifest.json
```

Expected: no matches.

- [ ] Construct the retired general term without spelling it in active project
  text and confirm it has no active code, test, message, or data match:

```bash
retired_term="$(printf '\\160\\162\\157\\170\\171')" &&
git grep -n -i "${retired_term}" -- \
  src/aviation_agentic_ai/agent_system \
  tests/test_agent_system*.py \
  data/ontology/curated \
  data/sources/bts_on_time_2026_05_manifest.json
```

Expected: no matches.

- [ ] Run `uv run ruff check .` and `git diff --check`.
- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/contracts.py \
  src/aviation_agentic_ai/agent_system/bts_outcomes.py \
  src/aviation_agentic_ai/agent_system/sources.py \
  tests/test_agent_system_bts_outcomes.py \
  tests/test_agent_system_multisource_contracts.py
git commit -m "feat(agent-system): record BTS observation derivations"
```

---

## Task 3: Build Immutable Decision-Case Observation Facts

**Files:**

- Create: `src/aviation_agentic_ai/agent_system/public_observations.py`
- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- Modify: `tests/test_agent_system_public_observations.py`

### Interfaces

```python
class SourceBinding(StrictModel):
    source_id: str
    source_family: SourceFamily
    snapshot_sha256: str


class ObservationDerivation(StrictModel):
    derivation_id: str
    activity_iri: str
    summary_id: str
    summary_sha256: str
    source_id: str
    source_snapshot_sha256: str
    archive_sha256: str
    aggregation_procedure_id: str
    aggregation_procedure_checksum: str
    selected_row_ids: tuple[str, ...]
    selected_row_ids_sha256: str


class ObservationFactTrace(StrictModel):
    fact_id: str
    observation_id: str
    derivation_id: str
    summary_id: str
    metric_key: str
    canonical_value: int | Decimal | None
    source_id: str
    source_snapshot_sha256: str
    summary_sha256: str
    aggregation_procedure_id: str
    aggregation_procedure_checksum: str


class ReconstructionTrace(StrictModel):
    reconstruction_trace_id: str
    conceptual_case_iri: str
    reconstruction_iri: str
    reconstruction_input_sha256: str
    member_iris: tuple[str, ...]
    profile_refs: tuple[ValidationProfileRef, ...]
    source_bindings: tuple[SourceBinding, ...]
    aggregation_procedure_id: str
    aggregation_procedure_checksum: str


class BTSObservationBundle(StrictModel):
    status: Literal["ok", "insufficient", "blocked"]
    case_facts: list[ValidatedFact]
    activity_facts: list[ValidatedFact]
    observation_facts: list[ValidatedFact]
    fact_traces: list[ObservationFactTrace]
    derivations: list[ObservationDerivation]
    reconstruction_trace: ReconstructionTrace | None
    failure_reason: str | None
```

Entry point:

```python
def build_bts_observation_facts(
    event: DecisionContextEvent,
    canonical_facility: CanonicalEntity,
    outcome_bundle: BTSOutcomeBundle,
    snapshot_registry: SourceSnapshotRegistry,
    profile_registry: ValidationProfileRegistry,
) -> BTSObservationBundle: ...
```

The builder validates existing summary and seed hashes. It never opens the BTS archive or normalized CSV and never recalculates an aggregate.
It may invoke the existing deterministic Weather selector against the same
event, facility, and checksum-pinned registry solely to derive the selected
Weather member IDs. Task 5 cross-checks those IDs against the already validated
Weather bundle before publication.

### Steps

- [ ] Add RED tests for:
  - one conceptual `case:DecisionCase` per event identity;
  - one immutable `case:DecisionCaseReconstruction` per exact reconstruction input;
  - baseline, active, and recovery OWL-Time intervals with beginning/end instants;
  - one PROV activity per phase and one SOSA observation per non-null phase/metric;
  - separate result, property, unit, phase, procedure, event, airport, and source identities;
  - `sosa:hasFeatureOfInterest` targets the canonical airport, never the TMI event;
  - null metrics emit no observation while zero emits an observation;
  - count results use `unit:NUM` and minute results use `unit:MIN`;
  - the airport is typed as `sosa:FeatureOfInterest`;
  - result nodes are both `sosa:Result` and `qudt:QuantityValue`;
  - all computed facts use the public-observation profile and a typed derivation evidence reference;
  - profile-definition and system-membership facts use their own declared evidence modes;
  - identical inputs produce identical bytes and IDs;
  - changed event, facility, source, profile, or procedure input creates a new reconstruction;
  - every selected row ID resolves to an exact row in the checksum-pinned normalized BTS snapshot;
  - tampered but self-consistently rehashed row IDs fail closed;
  - unknown metrics, wrong units/datatypes, stale summary hashes, wrong row digests, source mismatches, event/facility mismatches, forbidden predicates, and causal predicates return `blocked`.
- [ ] Run and confirm RED:

```bash
uv run pytest -q tests/test_agent_system_public_observations.py
```

- [ ] Implement canonical serialization and stable-ID helpers.
- [ ] Implement profile-definition facts separately from run-instance facts.
- [ ] Implement observation derivations, observation fact traces, and reconstruction trace.
- [ ] Add deterministic JSON/JSONL writers and strict readers for:

```text
observation_derivations.jsonl
observation_fact_trace.jsonl
reconstruction_trace.json
```

- [ ] Confirm that derivations contain sorted selected-row IDs but do not create flight-row graph nodes.
- [ ] Run the focused tests and confirm GREEN.
- [ ] Run `uv run ruff check .` and `git diff --check`.
- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/contracts.py \
  src/aviation_agentic_ai/agent_system/public_observations.py \
  src/aviation_agentic_ai/agent_system/context_artifacts.py \
  tests/test_agent_system_public_observations.py
git commit -m "feat(agent-system): build public observation facts"
```

---

## Task 4: Make Formal Materialization Multi-Profile

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/materialize.py`
- Modify: `src/aviation_agentic_ai/agent_system/runtime.py`
- Modify: `tests/test_agent_system_public_observations.py`
- Modify: `tests/test_agent_system_batch_two.py`
- Modify: `tests/test_agent_system.py`

### Interfaces

```python
def validate_fact_publication(
    *,
    facts: Sequence[ValidatedFact],
    profile_registry: ValidationProfileRegistry,
    snapshot_registry: SourceSnapshotRegistry,
    fact_traces: Sequence[FactTraceRow],
    weather_fact_traces: Sequence[WeatherFactTrace],
    observation_fact_traces: Sequence[ObservationFactTrace],
    reconstruction_trace: ReconstructionTrace | None,
) -> None: ...


def materialize_validated_facts(
    *,
    facts: list[ValidatedFact],
    profile_registry: ValidationProfileRegistry,
    source_snapshot: SourceSnapshot | SourceSnapshotRegistry,
    fact_traces: Sequence[FactTraceRow] = (),
    weather_fact_traces: Sequence[WeatherFactTrace] = (),
    observation_fact_traces: Sequence[ObservationFactTrace] = (),
    reconstruction_trace: ReconstructionTrace | None = None,
    output_dir: str | Path,
    guide: SchemaGuide | None = None,
) -> FactMaterialization: ...
```

`guide` exists only for the explicit old-artifact read path. New publication requires `profile_registry`.

### Steps

- [ ] Add RED tests proving publication rejects:
  - missing, unknown, wrong-checksum, or wrong-layer profile ownership;
  - a source-text evidence reference absent from exact ATCSCC or Weather traces;
  - a deterministic evidence reference absent from observation traces;
  - a profile-definition evidence reference not equal to the profile ID and checksum;
  - a membership evidence reference absent from the reconstruction trace;
  - a source ID or checksum absent from the registry;
  - any class or predicate absent from the owning profile;
  - unknown IRI subjects or objects that would previously receive heuristic labels.
- [ ] Add RED projection tests for all explicit labels and relationship mappings in the design.
- [ ] Add RED parity tests asserting the same identity and predicate sets in RDF and Neo4j projection.
- [ ] Run and confirm RED:

```bash
uv run pytest -q \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_batch_two.py \
  tests/test_agent_system.py
```

- [ ] Implement `validate_fact_publication` with mode-aware evidence validation.
- [ ] Resolve classes, predicates, labels, datatypes, and relationship mappings per fact from `ValidationProfileRegistry`.
- [ ] Remove the unknown-subject-to-`AviationEvent` and unknown-IRI-object-to-`Facility` fallbacks from the new path.
- [ ] Add explicit Neo4j labels:

```text
DecisionCase
DecisionCaseReconstruction
Observation
ObservationResult
TimeInterval
TimeInstant
ObservationPhase
ObservableProperty
Unit
AggregationActivity
ObservationProcedure
```

- [ ] Add the explicit standard relationship mappings in the approved design.
- [ ] Preserve original predicate IRI, profile ID/checksum, evidence mode/reference, and source bindings in formal JSONL and Neo4j records.
- [ ] Encode source-text evidence and deterministic PROV derivation differently in RDF. Never invent source comments for computed facts.
- [ ] Confirm repeated materialization is byte-stable and Neo4j IDs remain idempotent.
- [ ] Run focused tests and confirm GREEN.
- [ ] Run `uv run ruff check .` and `git diff --check`.
- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/materialize.py \
  src/aviation_agentic_ai/agent_system/runtime.py \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_batch_two.py \
  tests/test_agent_system.py
git commit -m "feat(agent-system): materialize multi-profile facts"
```

---

## Task 5: Integrate Observation Publication into the Workflow

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Modify: `src/aviation_agentic_ai/agent_system/runtime.py`
- Modify: `tests/test_agent_system_multisource_context.py`
- Modify: `tests/test_agent_system.py`
- Modify: `tests/test_cli_agent_system.py`

### Runtime Sequence

```text
validate core event
  -> select and validate Weather
  -> calculate BTS summaries and derivation seeds
  -> build public observation facts
  -> write audit artifacts
  -> validate each semantic layer
  -> merge only validated formal facts
  -> materialize JSONL, RDF, and Neo4j projections
```

### Steps

- [ ] Add RED end-to-end tests proving:
  - the workflow writes the three new audit artifacts;
  - the manifest records path, count, checksum, profile references, layer status, formal counts, procedure checksum, and source bindings;
  - validated public observations join `kg.jsonl`, `kg.ttl`, and Neo4j projections;
  - a blocked public-observation layer writes no observation facts and preserves queryable ATCSCC and Weather facts;
  - an insufficient BTS layer is recorded honestly;
  - rerunning the same case does not duplicate KJFK, KEWR, Weather reports, observations, activities, results, associations, or summaries;
  - KG Construction model-call counts are unchanged.
- [ ] Run and confirm RED:

```bash
uv run pytest -q \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system.py \
  tests/test_cli_agent_system.py
```

- [ ] Add `observation_context` to runtime state.
- [ ] Integrate the adapter and builder after event/facility/Weather validation.
- [ ] Write `outcome_summaries.jsonl` and derivation artifacts before formal publication.
- [ ] On public-observation validation failure:
  - mark only that layer `blocked`;
  - omit its formal facts;
  - retain validated core and Weather facts;
  - store a bounded failure reason;
  - make no provider call.
- [ ] Register all artifacts and layer counts in the manifest.
- [ ] Run focused tests and confirm GREEN.
- [ ] Run `uv run ruff check .` and `git diff --check`.
- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/context_artifacts.py \
  src/aviation_agentic_ai/agent_system/workflow.py \
  src/aviation_agentic_ai/agent_system/runtime.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system.py \
  tests/test_cli_agent_system.py
git commit -m "feat(agent-system): publish decision case observations"
```

---

## Task 6: Make Formal Observations the Bounded Query Authority

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/query_context_store.py`
- Modify: `src/aviation_agentic_ai/agent_system/query_tools.py`
- Modify: `src/aviation_agentic_ai/agent_system/query_tool_graph.py`
- Modify: `src/aviation_agentic_ai/agent_system/contracts.py`
- Modify: `tests/test_agent_system_query_tools.py`
- Modify: `tests/test_agent_system_query_tool_graph.py`
- Modify: `tests/test_cli_agent_system.py`
- Modify: active project metadata and design documents listed below

### Interfaces

```python
class OutcomeObservationRead(StrictModel):
    observation_id: str
    fact_ids: tuple[str, ...]
    phase: Literal["baseline", "active", "recovery"]
    metric_key: str
    label: str
    value: int | Decimal
    datatype_iri: str
    unit_iri: str
    derivation_id: str
    evidence_ref: str
    source_id: str
    source_snapshot_sha256: str
    profile_id: str
    profile_checksum: str


class OutcomeSummaryRead(StrictModel):
    status: Literal["ok", "insufficient", "blocked"]
    event_id: str
    observations: tuple[OutcomeObservationRead, ...]
    source_ids: tuple[str, ...]
    failure_reason: str | None
```

Extend `QueryToolResult.status` to `Literal["ok", "insufficient", "blocked"]`.

The deterministic user question is:

```python
PUBLIC_OUTCOME_QUESTION = (
    "What BTS-reported public operational observations are recorded?"
)
```

### Steps

- [ ] Add RED tests proving that `QueryContextStore`:
  - reads public outcomes from formal observation facts;
  - cross-checks the profile registry, observation fact traces, derivations, reconstruction trace, source registry, and manifest;
  - resolves every derivation row ID against the checksum-pinned normalized BTS snapshot and rejects tampered but self-consistently rehashed ID sets;
  - never treats `outcome_summaries.jsonl` alone as answer authority;
  - returns `blocked` on checksum, profile, derivation, schema, or source-binding failure;
  - returns `insufficient` when the validated context is absent;
  - returns legitimate zero observations as `ok`;
  - carries observation, fact, derivation, source, profile, checksum, unit, and phase data.
- [ ] Add RED routing tests proving:
  - public-outcome and reconstructed-case questions are deterministic and make zero provider calls;
  - unsupported and absent-context questions make zero provider calls;
  - declared-reason routing never opens Weather or BTS artifacts;
  - Ground Stop 123 remains a profile gap;
  - GDP 138 remains formal `weather`;
  - cancellation 020 remains `insufficient` with zero provider calls.
- [ ] Run and confirm RED:

```bash
uv run pytest -q \
  tests/test_agent_system_query_tools.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_cli_agent_system.py
```

- [ ] Implement strict formal observation reconstruction in the query store.
- [ ] Return the exact source-qualified wording:

```text
During the active interval, BTS reported 77 scheduled arrivals, 68 completed
arrivals, 4 cancellations, and 5 diversions for JFK within the tracked BTS
reporting scope.
```

- [ ] Preserve separate declared-reason and public-observation routes.
- [ ] Record retrieved observation, fact, and derivation IDs in `query_run.json`.
- [ ] Extend `QueryToolTrace` and `QueryToolOutcome` with explicit retrieved
  observation and derivation ID collections; do not overload summary IDs.
- [ ] Clean active terminology and update current scope in:
  - `AGENTS.md`
  - `ARTIFACT_INDEX.md`
  - `CLAUDE.md`
  - `GOALS.md`
  - `README.md`
  - `REPRODUCIBILITY.md`
  - `RESEARCH_AUDIT.md`
  - `TODO.md`
  - `docs/atcscc_decision_record_explorer_design.md`
  - `docs/multi_agent_kg_system_design.md`
- [ ] Append a superseding decision to `DECISION_LOG.md`; do not rewrite historical decisions.
- [ ] Scan active project surfaces:

```bash
git grep -n -i 'scheduled_arrival_count_\\|public scheduled-demand' -- \
  AGENTS.md ARTIFACT_INDEX.md CLAUDE.md GOALS.md README.md \
  REPRODUCIBILITY.md RESEARCH_AUDIT.md TODO.md \
  docs/atcscc_decision_record_explorer_design.md \
  docs/multi_agent_kg_system_design.md \
  src/aviation_agentic_ai/agent_system \
  tests/test_agent_system*.py \
  data/ontology/curated \
  data/sources/bts_on_time_2026_05_manifest.json
```

Expected: no matches.

- [ ] Run the constructed retired-term scan across every active project surface:

```bash
retired_term="$(printf '\\160\\162\\157\\170\\171')" &&
git grep -n -i "${retired_term}" -- \
  AGENTS.md ARTIFACT_INDEX.md CLAUDE.md GOALS.md README.md \
  REPRODUCIBILITY.md RESEARCH_AUDIT.md TODO.md \
  docs/atcscc_decision_record_explorer_design.md \
  docs/multi_agent_kg_system_design.md \
  src tests data
```

Expected: no matches.

- [ ] Run focused tests and confirm GREEN.
- [ ] Run the full acceptance suite:

```bash
uv run pytest -q \
  tests/test_agent_system_public_observations.py \
  tests/test_agent_system_bts_outcomes.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_query_tools.py \
  tests/test_agent_system_query_tool_graph.py \
  tests/test_agent_system.py \
  tests/test_cli_agent_system.py

uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

- [ ] Inspect generated RDF and Neo4j fixtures for the three cases and confirm:
  - no forbidden FAA operational or causal predicate;
  - no fallback node labels;
  - formal and derived evidence remain distinguishable;
  - the three ATCSCC reason states are unchanged;
  - no real provider call occurred.
- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/contracts.py \
  src/aviation_agentic_ai/agent_system/query_context_store.py \
  src/aviation_agentic_ai/agent_system/query_tools.py \
  src/aviation_agentic_ai/agent_system/query_tool_graph.py \
  tests AGENTS.md ARTIFACT_INDEX.md CLAUDE.md GOALS.md README.md \
  REPRODUCIBILITY.md RESEARCH_AUDIT.md TODO.md DECISION_LOG.md \
  docs/atcscc_decision_record_explorer_design.md \
  docs/multi_agent_kg_system_design.md
git commit -m "feat(agent-system): query formal decision case observations"
```

---

## Final Review Gate

- [ ] Compare the final diff to the approved design and this plan.
- [ ] Verify only the intended worktree changed.
- [ ] Verify all commits are local and the branch is not pushed or merged.
- [ ] Verify the main checkout's user-owned untracked test remains unchanged.
- [ ] Record the exact test counts, build artifact result, three-case values, layer statuses, model-call counts, and remaining blockers in the handoff.
