# Decision Case Graph v1 Design

> **Historical and superseded.** This design predates both the TMI semantic
> cutover and the ingestion-first persistence cutover. DecisionCase and Corpus
> persistence are not current domain or runtime contracts. Current truth is
> defined by `RESEARCH_AUDIT.md`, `GOALS.md`, and
> `docs/multi_agent_kg_system_design.md`.

Status: historical design; superseded by the TMI semantic and ingestion-first cutovers

Date: 2026-07-27

Branch: `codex/decision-case-graph-v1`

Normative parent design:
`docs/multi_agent_kg_system_design.md`

## 1. Stage Header

| Item | Decision |
| --- | --- |
| User-facing capability | Inspect one reconstructed ATCSCC decision case containing the TMI record, canonical airport, decision-time Weather reports, and BTS-reported public operational observations. |
| Smallest end-to-end result | Materialize and query GDP 138 with KJFK, eligible TAF/METAR reports, and baseline/active/recovery BTS observations. |
| Minimum components | Existing Decision Context branch, deterministic BTS summaries, a public-observation ontology profile, Formal Graph Kernel-compatible validation, RDF/Neo4j materialization, and bounded read-only query tools. |
| Expected evidence | Stable observation identities, source/checksum binding, RDF/Neo4j parity, exact time windows, preserved reason states, and zero additional provider calls. |
| Success condition | BTS-reported observations are queryable in the same formal KG without being represented as FAA demand, AAR, capacity, EDCT, or causal evidence. |
| Failure condition | Any observation is mislabeled as an AviationEvent or Facility, a missing value becomes zero, BTS is mapped to an FAA operational variable, Weather becomes a causal edge, or cancellation 020 gains a reason. |
| Explicitly deferred | Advisory lifecycle grouping, ASPM, regional Weather, NOTAM, flight trajectories, case similarity, recommendation, UI work, and full-corpus execution. |
| Classification | Critical Path for the Decision Case Graph; provenance and vocabulary conformance are Evidence Quality. |

This stage builds a system capability. It does not compare Agent
architectures and does not test a Multi-Agent advantage.

## 2. Approved Architecture

The approved option is one formal knowledge graph with distinguishable
semantic layers:

```text
Decision case collection
  + ATCSCC TMI event facts
  + canonical airport facts
  + selected formal TAF/METAR report facts
  + BTS-reported public operational observations
  + fact-level provenance
```

The implementation does not use RDF named graphs in v1. Semantic separation
comes from explicit classes, source families, predicates, validation profiles,
and Neo4j labels. Query tools may combine the layers, but no layer may weaken
the validation rules of another.

The following standards are reused:

- NASA ATMONTO for TMI, airport, and Weather-report concepts;
- SOSA/SSN for observations, observable properties, features of interest,
  phenomenon time, and results;
- OWL-Time for deterministic baseline, active, and recovery intervals;
- PROV-O for decision-case membership and source provenance;
- QUDT for numerical values and units;
- SKOS for observable-property labels, definitions, and scope notes.

References:

- <https://www.w3.org/TR/vocab-ssn/>
- <https://www.w3.org/TR/owl-time/>
- <https://www.w3.org/TR/prov-o/>
- <https://qudt.org/schema/qudt/>

## 3. Terminology

Active contracts, code identifiers, prompts, query answers, CLI messages,
documentation, and UI labels use source-qualified BTS terminology.

The source-qualified terminology is:

- `BTS-reported scheduled arrivals`;
- `BTS-reported completed arrivals`;
- `BTS-reported cancellations`;
- `BTS-reported diversions`;
- `BTS-reported arrivals delayed at least 15 minutes`;
- `BTS-reported mean arrival delay`;
- `BTS-reported median arrival delay`;
- `BTS-reported carrier-attributed Weather delay minutes`;
- `BTS-reported carrier-attributed NAS delay minutes`.

The summary contract uses `scheduled_arrival_count` as its only supported
scheduled-arrival field.

The graph and reader-facing output preserve this scope statement:

```text
BTS On-Time reporting carriers and scheduled domestic passenger operations.
```

Source qualification, coverage metadata, observation definitions, and
provenance maintain the semantic boundary. The feature does not rely on a
warning word in a property name.

The following equivalences are forbidden:

```text
BTS-reported scheduled arrivals != FAA Arrival Demand
BTS-reported completed arrivals != airport capacity or AAR
BTS-reported Weather delay != ATCSCC impacting condition
BTS-reported NAS delay != ATCSCC impacting condition
```

## 4. Graph Model

### 4.1 Namespaces

```text
sosa:    http://www.w3.org/ns/sosa/
time:    http://www.w3.org/2006/time#
prov:    http://www.w3.org/ns/prov#
qudt:    http://qudt.org/schema/qudt/
unit:    http://qudt.org/vocab/unit/
skos:    http://www.w3.org/2004/02/skos/core#
dcterms: http://purl.org/dc/terms/
case:    urn:aviation-agentic-ai:decision-case-schema:
btsobs:  urn:aviation-agentic-ai:observable-property:bts:
phase:   urn:aviation-agentic-ai:observation-phase:
proc:    urn:aviation-agentic-ai:observation-procedure:
```

### 4.2 Decision case

The graph distinguishes the conceptual case from one immutable reconstruction.
The conceptual case is both `case:DecisionCase` and `prov:Entity`, with a
stable ID derived from the validated event ID:

```text
urn:aviation-agentic-ai:decision-case:<event-hash>
```

The immutable reconstruction is both `case:DecisionCaseReconstruction` and
`prov:Collection`, whose ID is a hash of:

```text
event_id
selected Weather report IDs, source IDs, and checksums
BTS source ID and checksum
outcome summary artifact checksum
decision, Weather, and observation profile IDs and checksums
aggregation procedure ID and checksum
```

It links to the conceptual case with `prov:specializationOf`. Identical inputs
reuse the same reconstruction ID. Changed evidence, profiles, or procedure
produce a new reconstruction instead of retaining stale members on an existing
Neo4j node.

The reconstruction uses `prov:hadMember` for:

- the validated TMI event;
- each Weather report selected for the event;
- each BTS-reported operational observation selected for the event.

The reconstruction and every member are explicitly typed as `prov:Entity` in
addition to their domain-specific type. This avoids depending on an external
RDFS reasoner to infer the range of `prov:hadMember`.

Collection membership means only "included in this reconstructed evidence
case." It does not mean caused, motivated, justified, affected, or optimized.

No `causedBy`, `motivatedBy`, `hasOutcome`, `affectedBy`, or equivalent edge is
introduced in v1.

### 4.3 Observation granularity

One `sosa:Observation` represents exactly one:

```text
event x phase x metric
```

For three events, three phases, and nine metrics, the maximum is 81
observations. A null metric produces no observation. A reported zero remains a
zero-valued observation.

Observation IDs are stable hashes of:

```text
reconstruction_id
| phase
| metric_iri
| source_id
| source_snapshot_sha256
| aggregation_procedure_checksum
```

The observation contains:

```text
rdf:type                 sosa:Observation
                         prov:Entity
sosa:hasFeatureOfInterest canonical airport
sosa:observedProperty     source-qualified observable property
sosa:phenomenonTime       phase interval
sosa:hasResult            QUDT quantity-value result
sosa:usedProcedure        versioned deterministic aggregation procedure
prov:wasGeneratedBy       phase aggregation activity
prov:wasDerivedFrom       BTS source record
```

The event is not the feature of interest. The canonical airport is the feature
of interest because the summary describes airport-level reported operations.
For this application profile, the airport instance is also typed
`sosa:FeatureOfInterest`; the NASA airport class itself is not globally changed.

There is one deterministic `prov:Activity` per reconstruction and phase. The
activity:

```text
rdf:type       prov:Activity
prov:used      BTS source record
prov:generated every non-null observation in that phase
```

The procedure resource is both `sosa:Procedure` and `prov:Plan`:

```text
proc:bts-on-time-aggregation-v1
```

Its tracked definition and checksum include the formulas and null rules in
Section 5.1. No model creates or revises the procedure.

### 4.4 Time intervals

Each event has exactly three OWL-Time intervals:

```text
baseline = [operational_start - 2h, operational_start)
active   = [operational_start, operational_end)
recovery = [operational_end, operational_end + 6h)
```

Each interval is a `time:Interval` with stable `time:Instant` beginning and end
nodes. Each instant uses `time:inXSDDateTimeStamp`. Each phase resource is a
`case:ObservationPhase` and `skos:Concept`. The interval is tagged with one of:

```text
phase:baseline
phase:active
phase:recovery
```

using `dcterms:type`.

Half-open membership remains a deterministic adapter rule. The graph stores
the resulting interval boundaries; it does not recalculate flight membership.

### 4.5 Results and units

Every observation has a deterministic result node:

```text
rdf:type          sosa:Result
                  qudt:QuantityValue
qudt:numericValue typed literal
qudt:unit         unit:NUM or unit:MIN
```

Counts use `xsd:integer` and `unit:NUM`.

Mean, median, and attributed delay minutes use a canonical decimal literal and
`unit:MIN`.

The tracked profile explicitly types both admitted unit resources as
`qudt:Unit`; the run graph does not invent or infer any other unit.

### 4.6 Observable properties

The observation profile defines nine reusable
`sosa:ObservableProperty` individuals:

| Local name | Preferred label | Unit |
| --- | --- | --- |
| `scheduled-arrival-count` | BTS-reported scheduled arrivals | `unit:NUM` |
| `completed-arrival-count` | BTS-reported completed arrivals | `unit:NUM` |
| `cancelled-count` | BTS-reported cancellations | `unit:NUM` |
| `diverted-count` | BTS-reported diversions | `unit:NUM` |
| `arrival-delay-15-count` | BTS-reported arrivals delayed at least 15 minutes | `unit:NUM` |
| `mean-arrival-delay` | BTS-reported mean arrival delay | `unit:MIN` |
| `median-arrival-delay` | BTS-reported median arrival delay | `unit:MIN` |
| `carrier-attributed-weather-delay` | BTS-reported carrier-attributed Weather delay | `unit:MIN` |
| `carrier-attributed-nas-delay` | BTS-reported carrier-attributed NAS delay | `unit:MIN` |

Each property has:

- `rdf:type sosa:ObservableProperty`;
- `skos:prefLabel`;
- `skos:definition`;
- `skos:scopeNote` naming the BTS reporting population and calculation basis.

The definitions are tracked in the observation profile and are not generated
by a model.

### 4.7 Minimal application classes

The observation profile defines only the application classes needed to
classify case and phase nodes without heuristic Neo4j fallbacks:

```text
case:DecisionCase
  rdfs:subClassOf prov:Entity

case:DecisionCaseReconstruction
  rdfs:subClassOf prov:Collection

case:ObservationPhase
  rdfs:subClassOf skos:Concept
```

No project-specific causal, demand, capacity, result, membership, or
provenance predicate is introduced. Relationships reuse the standard
predicates listed in Section 7.

## 5. Contracts And Artifacts

### 5.1 Existing summary migration

`BTSOutcomeSummary` remains the deterministic aggregation result, with these
changes:

```python
scheduled_arrival_count: int
reporting_scope: Literal[
    "BTS On-Time reporting carriers and scheduled domestic passenger operations."
]
causal_claim: Literal[False]
```

Earlier experimental field names are retired from active v1 contracts. Earlier
unmerged v0 run artifacts are not treated as v1 artifacts; the three approved
cases are regenerated.

Other metric field names remain:

```python
completed_arrival_count
cancelled_count
diverted_count
arrival_delay_15_count
mean_arrival_delay_minutes
median_arrival_delay_minutes
carrier_reported_weather_delay_minutes
carrier_reported_nas_delay_minutes
```

Null values remain null in the summary artifact.

The following formulas are normative:

```text
selected rows =
  matching canonical destination airport
  AND scheduled_arrival_utc in the half-open phase interval

scheduled_arrival_count =
  count(selected rows)

completed rows =
  selected rows where Cancelled == 0 AND Diverted == 0

completed_arrival_count =
  count(completed rows)

cancelled_count =
  count(selected rows where Cancelled == 1)

diverted_count =
  count(selected rows where Diverted == 1)

arrival_delay_15_count =
  count(completed rows where ArrDel15 == 1)

mean_arrival_delay_minutes =
  arithmetic mean of non-null ArrDelay over completed rows

median_arrival_delay_minutes =
  median of non-null ArrDelay over completed rows

carrier_reported_weather_delay_minutes =
  sum of non-null WeatherDelay over selected rows

carrier_reported_nas_delay_minutes =
  sum of non-null NASDelay over selected rows
```

If a delay field has no non-null values in the selected population, its
aggregate is null, not zero. Counts are always defined for a valid selected
population and may legitimately be zero.

The same adapter pass emits one immutable derivation seed per phase:

```python
class ObservationDerivationSeed:
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

class BTSOutcomeBundle:
    status: Literal["ok", "insufficient", "blocked"]
    summaries: list[BTSOutcomeSummary]
    derivation_seeds: list[ObservationDerivationSeed]
    failure_reason: str
```

The adapter reads the normalized-snapshot and archive checksums from the pinned
BTS manifest. It sorts selected row IDs before hashing them. The graph builder
never reopens raw rows or independently recalculates a summary.

The source loader returns those manifest values as a typed immutable binding;
the CLI and `IngestContext` carry that binding to the adapter rather than
discarding it and restamping module defaults. The aggregation procedure ID and
checksum come from the checksum-verified public-observation profile. The
profile loader rejects a procedure descriptor that differs from the one
admitted by the application profile, and the adapter emits exactly that
descriptor in every seed.

### 5.2 Observation profile

Add a tracked, checksum-pinned application profile:

```text
data/ontology/curated/decision_case_public_observation_slice.json
```

It admits only the classes and predicates specified in Section 4. It records
the nine metric definitions, expected units, literal datatypes, source-family
requirements, deterministic procedure definition, and forbidden FAA/causal
predicates.

The profile is independent of the ATCSCC TMI profile and the Weather profile.
A fact must pass the profile that owns its semantic layer.

Every formal fact carries an immutable profile reference:

```python
class ValidationProfileRef:
    profile_id: str
    profile_checksum: str
    layer: Literal["decision", "weather", "public_operational_observation"]

class ValidatedFact:
    ...
    validation_profile: ValidationProfileRef
    evidence_mode: Literal[
        "source_text",
        "deterministic_derivation",
        "profile_definition",
        "system_membership",
    ]
    evidence_ref: str
```

The materializer receives a checksum-verified profile registry and validates
each fact with its owning profile. It does not stamp one schema ID across facts
from unrelated profiles. The legacy loader may synthesize the prior single
ATCSCC profile reference only for old read-only artifacts; all new runs must
persist explicit ownership.

`ValidationProfileRegistry` is immutable and checksum-verified. It resolves a
`ValidationProfileRef` to exactly one loaded profile. A separate explicit
read-only legacy adapter may synthesize the historical ATCSCC profile reference
for old artifacts. New validation or write paths reject synthesized ownership.

`evidence_ref` is validated by mode:

```text
source_text              -> FactTraceRow.fact_id
deterministic_derivation -> ObservationFactTrace.fact_id
profile_definition       -> ValidationProfileRef.profile_id + checksum
system_membership        -> ReconstructionTrace.reconstruction_trace_id
```

Materialization and query code never infer an evidence target from an empty
source field or from fact-ID naming conventions.

The tracked observation profile contributes definition facts for observable
properties, units, phases, and the procedure. Those facts use
`evidence_mode="profile_definition"` and bind to the tracked profile checksum.
Run-specific case, activity, observation, result, and interval facts are
separate instance facts and cannot alter the profile definitions.

The profile rejects:

- `https://data.nasa.gov/ontologies/atmonto/data#arrivalDemand`;
- `https://data.nasa.gov/ontologies/atmonto/data#airportArrivalRate`;
- any other FAA capacity, AAR, ADR, EDCT, or demand predicate not explicitly
  admitted by a later source-specific profile;
- causal predicates;
- `owl:equivalentProperty`, `rdfs:subPropertyOf`, `skos:exactMatch`, or
  `skos:closeMatch` from a BTS observable property to an FAA operational
  property.

### 5.3 Runtime artifacts

The context artifact set is:

```text
source_snapshots.jsonl
context_associations.jsonl
outcome_summaries.jsonl
observation_derivations.jsonl
observation_fact_trace.jsonl
reconstruction_trace.json
```

After validation, observation facts join the canonical formal artifacts:

```text
kg.jsonl
kg.ttl
neo4j_nodes.jsonl
neo4j_relationships.jsonl
fact_trace.jsonl
```

The run manifest records:

- observation profile ID and checksum;
- observation, result, interval, instant, activity, procedure, conceptual-case,
  and reconstruction counts;
- BTS source ID and checksum;
- aggregation procedure ID and checksum;
- `observation_derivations.jsonl` path, count, and checksum;
- `observation_fact_trace.jsonl` path, count, and checksum;
- `reconstruction_trace.json` path and checksum;
- observation-layer status: `ok`, `insufficient`, or `blocked`;
- formal layer counts for `decision`, `weather`, and
  `public_operational_observation`.

`outcome_summaries.jsonl` remains the source-audited aggregation artifact. It
does not become a second query authority after formalization.

`observation_derivations.jsonl` is the audit bridge from aggregate facts to
their deterministic calculation. One row per event and phase contains:

```python
derivation_id: str
activity_iri: str
summary_id: str
summary_sha256: str
source_id: str
source_snapshot_sha256: str
archive_sha256: str
aggregation_procedure_id: str
aggregation_procedure_checksum: str
selected_row_ids: tuple[str, ...]       # sorted
selected_row_ids_sha256: str
```

The selected row IDs are validated against the checksum-pinned normalized
snapshot. A derivation row is audit metadata and does not introduce flight rows
as graph nodes.

`reconstruction_trace.json` contains:

```python
reconstruction_trace_id: str
conceptual_case_iri: str
reconstruction_iri: str
reconstruction_input_sha256: str
member_iris: tuple[str, ...]
profile_refs: tuple[ValidationProfileRef, ...]
source_bindings: tuple[SourceBinding, ...]
aggregation_procedure_id: str
aggregation_procedure_checksum: str
```

It is the evidence target for conceptual-case, reconstruction, specialization,
and membership facts.

`observation_fact_trace.jsonl` contains the typed `ObservationFactTrace` rows
defined in Section 6. It is separate from the exact-text `fact_trace.jsonl` so
readers and validators cannot confuse derived aggregates with extracted source
spans.

## 6. Validation And Publication

The deterministic BTS adapter remains the only component that calculates
summary values. Formal observations are projected from the already validated
summary; they are not recalculated from raw rows.

The observation builder may invoke the existing deterministic Weather selector
against the same event, canonical facility, and checksum-pinned snapshot
registry solely to recover the selected Weather report member IDs. It does not
reimplement Weather selection or reinterpret Weather content. The integration
layer cross-checks those IDs against the already validated Weather bundle
before publication.

Add:

```python
build_bts_observation_facts(
    event: DecisionContextEvent,
    canonical_facility: CanonicalEntity,
    outcome_bundle: BTSOutcomeBundle,
    snapshot_registry: SourceSnapshotRegistry,
    profile_registry: ValidationProfileRegistry,
) -> BTSObservationBundle
```

The bundle contains:

```python
status: Literal["ok", "insufficient", "blocked"]
case_facts: list[ValidatedFact]
activity_facts: list[ValidatedFact]
observation_facts: list[ValidatedFact]
fact_traces: list[ObservationFactTrace]
derivations: list[ObservationDerivation]
failure_reason: str | None
```

`ObservationFactTrace` is not a fabricated text span. It records:

```python
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
```

Directly extracted ATCSCC and Weather facts continue to require exact source
text. Computed observations require a valid derivation row, matching summary
hash, selected-row digest, source checksums, procedure checksum, and
`evidence_mode="deterministic_derivation"`. They never receive invented
`evidence_texts`.

Case reconstruction and `prov:hadMember` facts use
`evidence_mode="system_membership"` and bind to the reconstruction input hash,
not to a claim that the membership relation appeared in a BTS row.

Publication fails closed when:

- event or facility identity differs from the validated TMI graph;
- a phase is missing, duplicated, or has the wrong interval;
- the BTS source ID/family/checksum is not registered;
- a summary value conflicts with the summary artifact;
- a metric has the wrong datatype or unit;
- an unknown metric or predicate appears;
- a null is converted to zero;
- a selected row ID, row digest, summary hash, archive hash, procedure ID, or
  procedure checksum does not match;
- a fact has a missing, unknown, or wrong-layer validation profile;
- a forbidden FAA or causal predicate appears.

An observation-layer failure does not delete a previously validated ATCSCC
event graph. The manifest records the observation layer as `blocked`, and
observation queries return `blocked`.

No LLM or Agent can create, revise, or approve observation facts.

## 7. RDF And Neo4j Materialization

The RDF writer continues to materialize `ValidatedFact` objects. It reifies
directly extracted statements with exact source evidence. Deterministically
computed statements carry the structured derivation trace from Section 5.3,
`prov:wasGeneratedBy`, `prov:wasDerivedFrom`, and the versioned procedure; they
do not claim an aggregate value appeared verbatim in a source row.

The Neo4j projection must classify nodes from explicit class IRIs. It must not
use the current fallback that treats unknown subjects as `AviationEvent` and
unknown IRI objects as `Facility`.

RDF and Neo4j writers receive the checksum-verified
`ValidationProfileRegistry`. For every fact they resolve the class, predicate,
label, datatype, and relationship mapping from that fact's
`validation_profile`; no single global `SchemaGuide` or schema ID is applied to
the merged graph. The legacy single-profile adapter is read-only and cannot be
used by these writers for new runs.

New Neo4j labels:

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

Existing labels remain:

```text
AviationEvent
Facility
MeteorologicalReport
SourceRecord
```

Required relationship mappings:

```text
prov:hadMember             -> HAS_MEMBER
prov:specializationOf      -> SPECIALIZATION_OF
sosa:hasFeatureOfInterest  -> HAS_FEATURE_OF_INTEREST
sosa:observedProperty      -> OBSERVED_PROPERTY
sosa:phenomenonTime        -> PHENOMENON_TIME
sosa:hasResult             -> HAS_RESULT
sosa:usedProcedure         -> USED_PROCEDURE
time:hasBeginning          -> HAS_BEGINNING
time:hasEnd                -> HAS_END
dcterms:type               -> HAS_PHASE
qudt:unit                  -> HAS_UNIT
prov:wasGeneratedBy        -> WAS_GENERATED_BY
prov:used                  -> USED
prov:generated             -> GENERATED
prov:wasDerivedFrom        -> DERIVED_FROM
```

Every relationship retains the original ontology predicate IRI. Repeated
materialization and Neo4j loading use stable IDs and parameterized `MERGE`.

RDF and Neo4j must contain the same conceptual-case, reconstruction,
observation, result, interval, instant, phase, property, unit, procedure,
activity, airport, event, Weather report, and source identities.

## 8. Query Behavior

The public high-level tool remains:

```python
get_outcome_summary(
    event_id: str,
    phases: tuple[str, ...] = ("baseline", "active", "recovery"),
) -> OutcomeSummaryRead
```

After v1 materialization, it reads and validates formal observation facts. It
does not answer from `outcome_summaries.jsonl` alone.

The read contract is:

```python
class OutcomeObservationRead:
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

class OutcomeSummaryRead:
    status: Literal["ok", "insufficient", "blocked"]
    event_id: str
    observations: tuple[OutcomeObservationRead, ...]
    source_ids: tuple[str, ...]
    failure_reason: str | None
```

The shared `QueryToolResult.status` is extended to
`Literal["ok", "insufficient", "blocked"]`. Its meaning is fixed:

- `ok`: validated observations exist, including legitimate reported zeros;
- `insufficient`: the requested context is absent or not applicable;
- `blocked`: a checksum, profile, derivation, schema, or source-binding
  validation failed.

The tool returns source-qualified labels, values, units, phases, observation
IDs, fact IDs, derivation IDs, source IDs, profile IDs, and checksums.

At store construction, the bounded query layer loads and validates the formal
facts, profile registry, observation fact traces, derivation rows,
reconstruction trace, source registry, and manifest layer status. Provenance is
resolved through each fact's `evidence_mode` and `evidence_ref`. A blocked
observation layer remains queryable as `blocked` without preventing validated
core event facts from loading.

The combined reconstructed-case query may retrieve:

1. event facts;
2. selected formal Weather facts and non-causal selection records;
3. formal BTS-reported observations.

The deterministic router resolves support before constructing a model. Missing
or unsupported observation questions make zero provider calls.

Declared-reason routing is isolated from the observation layer. It may read
only the validated ATCSCC reason fact or the source-bound profile-gap record.
It never consults Weather reports, Weather context associations, BTS Weather
attribution, BTS NAS attribution, or any other observation to fill or expand a
reason. Thus cancellation 020 remains `insufficient` with zero provider calls.

Answers use wording such as:

```text
During the active interval, BTS reported 77 scheduled arrivals, 68 completed
arrivals, 4 cancellations, and 5 diversions for JFK within the tracked BTS
reporting scope.
```

Answers must not use:

```text
FAA demand
airport capacity
AAR
caused
justified
optimal
```

unless a later admitted source and profile directly support that statement.

## 9. Three-Case Acceptance

### Ground Stop 123 / KJFK

- ATCSCC reason remains a source-bound profile gap.
- No formal `atm:impactingCondition` fact is created.
- The active BTS observations report scheduled `20`, completed `18`,
  cancelled `2`, and diverted `0`.
- Weather and BTS membership in the reconstructed case makes no causal claim.

### GDP 138 / KJFK

- Formal ATCSCC reason remains `weather`.
- The active BTS observations report scheduled `77`, completed `68`,
  cancelled `4`, and diverted `5`.
- BTS Weather/NAS attribution cannot expand or replace the ATCSCC reason.

### GDP cancellation 020 / KEWR

- Declared reason remains absent.
- The active BTS observations report scheduled `50`, completed `49`,
  cancelled `1`, and diverted `0`.
- Weather or BTS observations cannot fill the missing reason.
- A declared-reason query makes zero provider calls.

## 10. Automated Acceptance

Tests must prove:

- active contracts and reader-facing messages use only source-qualified
  BTS-reported terminology;
- each non-null event/phase/metric yields exactly one observation;
- null metrics yield no observation and zero metrics remain observations;
- observation IDs and ordering are reproducible;
- changed source/profile/procedure inputs create a new reconstruction ID, while
  identical inputs remain idempotent;
- every BTS-derived observation and activity fact binds to the BTS source ID
  and checksum, while profile-definition and system-membership facts use their
  own declared evidence modes;
- every fact carries the correct profile ID, checksum, and semantic layer;
- direct facts use exact source evidence while aggregate facts use only the
  checksum-verified derivation trace;
- selected row IDs, row digest, summary checksum, archive checksum, and
  procedure checksum all validate;
- all three intervals are exact and half-open at aggregation time;
- counts use `unit:NUM`, minute values use `unit:MIN`;
- neither
  `https://data.nasa.gov/ontologies/atmonto/data#arrivalDemand` nor
  `https://data.nasa.gov/ontologies/atmonto/data#airportArrivalRate` is emitted;
- no AAR, capacity, EDCT, causal predicate, or exact/equivalent/subproperty
  mapping from a BTS observable property to an FAA operational property is
  emitted;
- no TMI event is used as `sosa:hasFeatureOfInterest`;
- the canonical airport is also a `sosa:FeatureOfInterest`;
- results are both `sosa:Result` and `qudt:QuantityValue`;
- every observation names the checksum-pinned deterministic procedure and its
  phase aggregation activity;
- RDF parses and uses the approved standard IRIs;
- Neo4j uses the explicit new labels, including phase, unit, procedure, and
  activity nodes, and never fallback labels;
- RDF/Neo4j IDs and predicate IRIs agree;
- repeated materialization is idempotent;
- query results carry observation/fact/source IDs;
- observation queries distinguish `ok`, `insufficient`, and `blocked`;
- unsupported, missing-context, and missing-reason requests make zero provider
  calls;
- declared-reason routing never reads Weather or BTS observations;
- all three ATCSCC reason states remain unchanged.

Required verification:

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

No real provider call is permitted.

## 11. Branch And Integration Safety

Implementation proceeds on `codex/decision-case-graph-v1`, derived from the
clean `codex/decision-context-cases` worktree.

The main checkout contains an untracked
`tests/test_agent_system_multisource_contracts.py` that differs from the
tracked Decision Context version. It is user-owned and must not be deleted,
moved, overwritten, staged, or assumed disposable.

Do not switch or merge the main checkout while that collision exists. Final
integration requires an explicit user decision for that file.

The v1 branch is not pushed or merged until implementation review and full
verification complete.

## 12. Later Sequential Stages

### Lifecycle Link Audit v0

The next independent design may extract explicit lifecycle markers and persist
an audit artifact distinguishing:

- `explicit`: the source names the predecessor advisory;
- `candidate`: facility, TMI family, chronology, and comments support a link;
- `ambiguous`: more than one predecessor remains possible.

Only explicit source-named links may enter the formal graph without review.
Facility/time similarity alone cannot establish an episode.

### ASPM

ASPM is a separate source-admission stage. It requires verified access,
official field definitions, a fixed snapshot, and a source-specific profile
before adding Arrival Demand, AAR, EDCT, or runway configuration.

ASPM observations supplement BTS-reported observations. They do not rename or
retroactively reinterpret BTS data.
