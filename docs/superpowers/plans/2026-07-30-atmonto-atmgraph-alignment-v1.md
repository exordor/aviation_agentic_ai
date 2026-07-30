# ATMONTO / ATMGRAPH Alignment and TMI Target Correction v1

> **Execution mode:** Subagent-driven inventory and one focused review,
> followed by local test-driven implementation. Run focused tests while
> implementing, then one final repository verification.

## Capability Being Advanced

Restore the system's ATCSCC scope from a hard-coded GS/GDP subset to an
ATMONTO-aligned, event-family-driven TMI pipeline, beginning with an
end-to-end ReRoute path.

The alignment contract has two layers:

1. **Schema/TBox:** published aviation-domain terms are exact, checksum-pinned
   ATMONTO IRIs admitted by a versioned application profile.
2. **KG/ABox:** constructed event instances follow ATMGRAPH's relevant
   principles: source-specific parsing, stable identities, explicit time,
   cross-source links, and a clear separation between ATMONTO domain facts and
   project/standards extensions.

ATMGRAPH is not treated as another ontology or imported dataset. ATMONTO is its
representational foundation; ATMGRAPH is the construction and query reference.

## Verified Target Drift

The correction is based on repository evidence, not only the external review:

- The frozen 68-record cohort contains 24 GS, 21 GDP, and 23 records outside
  the current parser. Three GS records are incomplete, so the current 42
  eligible records are exactly 21 GS + 21 GDP.
- The 23 excluded records contain four active `ROUTE RQD` records, one
  Reroute cancellation, seven NATOTS notices, seven arrival-delay notices, one
  SWAP notice, and three hotline notices.
- The 100-record reviewed Gold set was deliberately stratified as 16 GDP,
  21 GS, 23 ReRoute, and 40 generic TMI records. It is not a natural frequency
  estimate, but it proves that the earlier evaluation scope was broader.
- All five tasks in both current v2 live suites are GDP tasks. Those frozen
  historical results remain valid compatibility evidence, but are not
  cross-TMI performance evidence.

The correction therefore targets the GS/GDP-only implementation boundary and
GDP-only acceptance selection. It does not remove the natural-language Query
Agent or the canonical corpus.

## Smallest End-to-End Result

One application-profile registry drives:

```text
source pattern
  -> TMI family
  -> ATMONTO event class
  -> family-specific required fields
  -> family-specific ATMONTO property mappings
  -> corpus coverage and retrieval labels
```

The active v1 event families are:

- `GDP` -> `atm:GroundDelayProgramTMI`
- `GS` -> `atm:GroundStopTMI`
- `REROUTE` -> `atm:ReRouteTMI`

The root `atm:TrafficManagementInitiative` remains the common abstraction.
Generic informational notices are detected and counted but are not forced into
formal TMI publication without an approved mapping. Reroute cancellation is
deferred to a later DecisionEpisode/lifecycle model.

Two reviewed active Reroutes (`2026-05-19:108` and `2026-05-20:137`) must
produce ATMONTO event facts for:

- `rdf:type atm:ReRouteTMI`
- `atm:advisoryNumber`
- `atm:issuedTime`
- `atm:effectiveStartTime` / `atm:effectiveEndTime`
- `atm:implementationStatus = RQD`
- `atm:reRouteType = ROUTE`
- `atm:reRouteReason = WEATHER`
- `atm:extensionProbability`, when the source value maps to the ATMONTO enum

`CONSTRAINED AREA: ZBW/ZNY` is retained as a source-supported profile gap
because the pinned ATMONTO range does not admit `nas:ARTCC` as the formal
`controlledNASelement` object. It must not be silently discarded or forced
through the range.

## Minimum Components

1. Exact-IRI ATMONTO application profile and event-family registry.
2. Registry-driven advisory parser, preflight, assembly mapping, and retrieval
   type labels.
3. The two unambiguous ATMONTO completeness fixes already identified:
   `atm:issuedTime` and Weather report
   `data:meteorologicalConditionStatus`.
4. A lightweight corpus-level `alignment_audit.json` and
   `tmi_coverage.json`; no new run ledger or query-time audit subsystem.
5. Cross-type regression acceptance over two GDP, two GS, two ReRoute, and two
   non-publishable boundary records.

## Evidence of Success

- The application profile is reproduced from pinned OWL/XML modules and has no
  accidental `urn:absolute:icarus#` active term.
- Event detection, preflight, formal property mapping, vector labels, and
  coverage reporting read the same registry rather than separate GS/GDP sets.
- The two reviewed ReRoute records publish without a live provider call in the
  deterministic unambiguous path.
- GDP 138, GDP 020, GS 123, and GS 120 preserve their existing semantics.
- Arrival-delay 059 and hotline 092 remain explicit boundary outcomes; neither
  is fabricated as a supported subtype.
- The coverage report distinguishes detected, eligible, insufficient, and
  published counts by family.
- The alignment audit reports zero unknown formal terms and separates:
  `atmonto_core`, external-standard extensions, and project extensions.
  ATMGRAPH remains a declared ABox-construction reference, not a namespace
  classification.
- Corpus, RDF, Neo4j, and case retrieval retain the same formal fact identity.

## Failure Conditions

- A non-GS event is still implicitly treated as GDP.
- ReRoute reason is written as GDP `impactingCondition`.
- An ARTCC constrained area is forced into an invalid ATMONTO
  `controlledNASelement` edge.
- A generic informational advisory is promoted to a supported TMI subtype.
- Event-family support remains duplicated in parser, preflight, workflow, or
  retrieval code.
- Any of the established GDP/GS reason states changes.
- The alignment/coverage artifacts become another per-run audit ledger rather
  than compact corpus-level research outputs.

## Explicitly Deferred

- ReRoute cancellation and full DecisionEpisode lifecycle linking
- AFP, CTOP, SWAP, NATOTS, MIT/MINIT, arrival-delay, and hotline publication
- Route-segment/table population and National Playbook PDF grounding
- Flight, trajectory, sector, F1/F3S/S4/S1S execution
- Full ATMONTO import/reasoner or ATMGRAPH ABox import
- Named graphs/TriG, GraphDB performance reproduction, AIRM-O alignment
- New Agents, a new framework, causal claims, or TMI recommendations
- A new real-provider benchmark; the current GDP-only suites are documented as
  historical and a balanced live suite is a later explicitly approved batch

---

## Batch R1 — Exact ATMONTO Profile and Event-Family Registry

### Tests first

Create `tests/test_agent_system_ontology_alignment.py` and
`tests/test_agent_system_tmi_profiles.py`.

Cover:

- exact-IRI selection excludes the ICARUS `FlightSpec` bridge;
- admitted class hierarchy is closed;
- the historical `staffing` value is an explicit overlay, not an upstream
  ATMONTO enum;
- upstream OWL/XML checksums are pinned;
- the common TMI root and GDP/GS/ReRoute active subtypes exist;
- each active profile declares required fields and only valid ATMONTO
  properties;
- inactive/boundary families cannot be obtained as publishable profiles;
- the registry classifies the verified 68-record cohort as 24 GS, 21 GDP,
  4 active Reroute, 1 deferred Reroute cancellation, and 18 boundary notices.

### Implementation

Modify `src/aviation_agentic_ai/ontology/atmonto_minimal_loop.py`:

- select exact ATMONTO IRIs rather than local names;
- close selected ATMONTO ancestors;
- retain hierarchy edges only when both endpoints are admitted;
- remove the hidden `staffing` mutation from generated upstream constraints.

Create:

- `data/ontology/curated/atmonto_application_profile_v1.json`
- `src/aviation_agentic_ai/agent_system/tmi_profiles.py`
- `src/aviation_agentic_ai/agent_system/ontology_alignment.py`

The application profile pins source modules/checksums, term origins, active
event profiles, boundary detectors, and ATMGRAPH's reference-only role.

Commit:

```text
feat(ontology): align active TMI profiles with ATMONTO
```

---

## Batch R2 — Registry-Driven Parsing and ReRoute Publication

### Tests first

Add focused tests to:

- `tests/test_agent_system_agents.py`
- `tests/test_agent_system_corpus_batch.py`
- `tests/test_agent_system_graph_kernel.py`
- `tests/test_agent_system_query_tool_graph.py`
- `tests/test_agent_system_case_retrieval.py`

Cover:

- GDP/GS behavior is unchanged;
- `ROUTE RQD` maps to `REROUTE`, not generic TMI or GDP;
- ReRoute parses `REASON`, `RQD`, `ROUTE`, issued/effective times, and
  ATMONTO-compatible extension probability;
- preflight reads family-specific requirements;
- Reroute cancellation and boundary notices remain insufficient without model
  calls;
- Assembly maps ReRoute fields to `reRouteReason`, `reRouteType`, and
  `implementationStatus`;
- constrained ARTCC is a profile gap and not a formal controlled-element edge;
- ReRoute is available to graph and case retrieval using the registry label.

### Implementation

Modify:

- `agent_system/agents.py`
- `agent_system/schema_guide.py`
- `agent_system/corpus_batch.py`
- `agent_system/workflow.py`
- `agent_system/formal_graph.py`
- `agent_system/case_retrieval_documents.py`
- `agent_system/case_retrieval_search.py`
- `data/sources/faa_atcscc_terms_v1.yaml`

Use the event profile for parsing, required-field checks, ontology class
selection, property dispatch, profile gaps, and retrieval labels. Remove:

- `_EVENT_RE` as a GDP/GS-only policy;
- `if event_type not in {"GS", "GDP"}`;
- the implicit `non-GS -> GDP impactingCondition` branch;
- retrieval's independent GDP/GS type mapping.

Do not add a new Agent or provider call. Exact source patterns and the pinned
application profile make these Reroutes deterministic; ambiguity still follows
the existing bounded escalation path.

Commit:

```text
feat(agent-system): publish ATMONTO ReRoute events
```

---

## Batch R3 — ATMONTO Completeness and ATMGRAPH-Style Corpus Audit

### Tests first

Extend:

- `tests/test_agent_system_weather_context.py`
- `tests/test_agent_system_ontology_alignment.py`
- `tests/test_agent_system_corpus_store.py`

Cover:

- every formal TMI has source-bound `atm:issuedTime`;
- METAR reports have `meteorologicalConditionStatus=observed`;
- TAF reports have `meteorologicalConditionStatus=forecast`;
- ATMONTO domain facts classify as `atmonto_core`;
- DecisionCase/PROV/SOSA/QUDT remain explicit extensions;
- the corpus manifest registers one compact alignment audit and one coverage
  report;
- repeated builds are byte-stable.

### Implementation

Modify:

- `agent_system/context_artifacts.py`
- `agent_system/weather_context.py`
- `agent_system/weather_context_validation.py`
- `data/ontology/curated/nasa_atmonto_decision_context_weather_slice.json`
- `agent_system/corpus_store.py`

Generate:

```text
alignment_audit.json
tmi_coverage.json
```

only at corpus finalization. Do not add transient-run profile recording,
query-time profile revalidation, raw prompt/model traces, or additional
publication-ledger consistency checks.

Commit:

```text
feat(agent-system): audit ATMONTO-aligned corpus coverage
```

---

## Batch R4 — Cross-Type Acceptance and Documentation

### Acceptance set

Publishable:

- GDP: `2026-05-19:138`, `2026-05-20:020`
- GS: `2026-05-19:123`, `2026-05-19:120`
- ReRoute: `2026-05-19:108`, `2026-05-20:137`

Boundaries:

- generic arrival-delay: `2026-05-14:059`
- hotline/status: `2026-05-19:092`

Deferred lifecycle:

- Reroute cancellation: `2026-05-20:098`

### Documentation

Update `RESEARCH_AUDIT.md`, `GOALS.md`, `README.md`, `TODO.md`, and
`docs/multi_agent_kg_system_design.md` to state:

- the primary ABox event is an ATMONTO TMI, not a DecisionCase;
- DecisionCase is a project reconstruction/membership view;
- the active publication scope is GDP/GS/ReRoute;
- generic and lifecycle records retain explicit boundary statuses;
- previous v2 live results are GDP-only compatibility evidence;
- DecisionEpisode is the next semantic expansion after cross-type alignment.

Commit:

```text
docs(research): restore cross-TMI ATMONTO scope
```

---

## Verification

During each batch, run only the affected tests. At the end run once:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

Inspect the generated six-case formal facts and two boundary results. Do not
merge or push until the user requests it.
