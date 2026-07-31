# Cross-Source Multi-Agent V2 Design

> **Historical design — superseded.** This document records the former
> cross-source V2 plan and retired CLI. It is not the current architecture or
> execution guide. Use `RESEARCH_AUDIT.md`, `REPRODUCIBILITY.md`, and
> `docs/multi_agent_kg_system_design.md` for the ingestion-first persistent-store
> runtime.

## 1. Goal

Build a reproducible multi-agent extension that:

1. aligns facility codes and operational abbreviations in retrospective FAA
   ATCSCC advisories to canonical knowledge-graph entities and terms;
2. links accepted advisory entities to temporally compatible NASR,
   AviationWeather METAR, TAF, and station records;
3. answers cross-source questions with separate source-assertion,
   observation/forecast, and system-association evidence layers; and
4. preserves an auditable trace for every automatic alignment, rejected
   candidate, quarantine decision, cross-source link, and answer citation.

The first cross-source cohort contains the 68 records in the existing 718-record
aligned ATCSCC snapshot that mention JFK, EWR, LGA, KJFK, KEWR, or KLGA. Term
mention extraction runs over all 718 aligned advisories. The first automated
policy-regression suite contains 24 questions selected from the 68-record cohort.

## 2. Scope Boundary

### In scope

- Facility-code alignment for airports, weather stations, ARTCCs, TRACONs,
  ATCTs, navaids, fixes, and airspace identifiers.
- Operational-term alignment for terms such as GDP, GS, AFP, CTOP, SWAP, FCA,
  MIT, EDCT, and other source-observed ATCSCC contractions.
- Versioned snapshots of FAA JO 7340.2, the FAA Pilot/Controller Glossary, the
  FAA traffic-management glossary, FAA NASR, and AviationWeather metadata.
- Deterministic exact resolution before contextual LLM disambiguation.
- An autonomous quarantine for low-confidence, conflicting, or out-of-scope mappings.
- Facility-identity and temporal-overlap links between advisories and weather.
- Layered answers with citations, limitations, abstention, and trace metadata.
- Interfaces that can later be scheduled by a state-graph framework without
  rewriting the nodes or data contracts.

### Out of scope

- Re-scoring or rewriting the existing ATCSCC extraction-to-answer experiments.
- Treating V2 results as current thesis evidence without a separate evaluation
  and an explicit thesis-scope decision.
- Live operational ATC decision support.
- Autonomous creation of canonical facilities or terminology by an LLM.
- Inferring that weather caused a traffic-management initiative solely because
  weather records overlap in time and location.
- Attaching airport weather to an ARTCC without an explicit, authoritative
  facility relationship.
- Expanding the first cohort beyond the existing historical weather snapshot.

## 3. Authority Model

LLM agents may propose a candidate alignment or phrase an evidence-bounded
answer. They cannot publish a source snapshot, create a registry target, write
an accepted alignment, create a formal cross-source edge, or approve an answer.

Authority is assigned in this order:

1. source snapshots and their effective dates;
2. canonical facility and terminology registries;
3. deterministic type, identity, temporal, evidence, and provenance checks;
4. alignment and answer critics;
5. autonomous quarantine and answer abstention for unresolved cases.

Every formal KG edge must identify its source snapshot set, evidence, creation
method, and gate decision.

## 4. Architecture

The V2 path extends the frozen single-source foundation. It consumes controlled facts and source records from
the existing ATCSCC path but does not mutate those inputs.

```text
frozen ATCSCC facts + aligned advisory records
    -> mention extraction
    -> deterministic facility / term resolution
    -> contextual alignment only for ambiguous candidates
    -> alignment critic
       -> accepted alignment -> canonical and audit graphs
       -> quarantine         -> no formal KG edge and answer abstention
    -> facility and temporal cross-source linking
    -> evidence retrieval
    -> layered answer generation
    -> evidence critic
    -> final answer or abstention
```

### Agent and component responsibilities

| Unit | Responsibility | May write formal KG? |
| --- | --- | --- |
| Source Refresh Agent | Fetch a requested official resource and produce a candidate snapshot. | No |
| Snapshot Validator | Check checksum, effective date, required fields, parser version, and conflicts before activation. | No |
| Mention Agent | Extract facility codes and operational-term mentions with exact evidence spans. | No |
| Registry Resolver | Resolve unique authoritative code or alias matches. | No |
| Context Alignment Agent | Rank only the supplied candidates for an ambiguous mention. | No |
| Alignment Critic | Apply source, type, date, context, threshold, and candidate-set gates. | Approves a writer action |
| Graph Writer | Materialize only critic-accepted canonical and audit records. | Yes |
| Cross-Source Link Agent | Create deterministic facility and temporal links. | Yes, after link validation |
| Query Router | Select required evidence layers and predicates for one question. | No |
| Evidence Retriever | Return cited graph and source records. | No |
| Layered Answer Agent | Produce a source-bounded draft answer. | No |
| Evidence Critic | Check citations, evidence layers, temporal validity, causal wording, and abstention. | No |

## 5. State and Execution Interface

Each node consumes immutable workflow state and returns a state patch plus a
trace event. The lightweight supervisor owns transitions. A future graph
scheduler can replace the supervisor without changing node behavior.

```python
class WorkflowNode(Protocol):
    node_id: str

    def run(self, state: CrossSourceState) -> NodeResult:
        ...
```

The shared state contains:

- `run_id` and `snapshot_set_id`;
- selected advisory IDs and optional question;
- extracted mentions and alignment candidates;
- accepted, quarantined, and rejected alignment decisions;
- validated cross-source links;
- retrieved evidence layers;
- draft or final answer;
- trace events and structured errors.

Network access is permitted only in the explicit snapshot-refresh path. Align,
build, answer, and evaluate commands must run offline from pinned artifacts.

## 6. Versioned Snapshot Model

Each snapshot manifest records:

- snapshot ID and source family;
- source URL;
- effective start and optional effective end;
- retrieval timestamp;
- SHA-256 of every raw input;
- parser name and parser version;
- normalized artifact paths and record counts;
- previous snapshot ID when applicable;
- candidate, active, rejected, or superseded status;
- validation errors and warnings.

The first authority order is:

| Layer | Priority |
| --- | --- |
| Facility identity | FAA NASR, AviationWeather station/airport metadata, ATMONTO schema type |
| Operational terminology | FAA JO 7340.2, FAA Pilot/Controller Glossary, FAA traffic-management glossary |

For a historical advisory, the resolver selects resources effective at the
advisory time. It must not silently use a newly refreshed resource when a
pinned historical snapshot set was requested.

## 7. Core Data Contracts

### Canonical entity

- `entity_id`: stable internal URI.
- `entity_type`: airport, weather station, ARTCC, TRACON, ATCT, navaid, fix,
  airspace, or unknown facility.
- `preferred_label`.
- typed codes containing scheme and value.
- aliases.
- validity interval.
- source references.

Stable identifiers use the most specific authoritative code, for example:

```text
urn:aviation-agentic-ai:facility:airport:KJFK
urn:aviation-agentic-ai:facility:artcc:ZNY
urn:aviation-agentic-ai:term:tmi:GDP
```

### Term concept

- `term_id`, abbreviation, preferred label, aliases, and category;
- one or more versioned definitions;
- optional link to an ATMONTO class or property;
- validity interval and source references.

### Mention

- source record and source family;
- surface and normalized forms;
- facility-code or operational-term type;
- source evidence text and character offsets;
- record time and detector version.

### Alignment candidate and decision

- mention and candidate target IDs;
- exact-code, exact-alias, contextual, or none method;
- authority sources;
- gate score and candidate margin;
- critic checks;
- accepted, quarantined, or rejected status;
- snapshot set, trace ID, and decision reason.

The score is a gate score, not a calibrated probability claim.

### Cross-source link

- subject, predicate, and object IDs;
- canonical facility ID;
- advisory and evidence intervals;
- link method;
- authority sources and evidence references;
- explicit `causal_claim: false` for time/location associations.

### Layered answer

- source assertions;
- observation evidence;
- forecast evidence;
- system associations;
- citations;
- limitations;
- abstention flag and rationale;
- snapshot set and trace ID.

## 8. Canonical and Audit Graphs

The canonical query graph stores only critic-accepted entities, terms,
advisory facts, facility links, and temporal links. The audit graph stores raw
mentions, all candidates, scores, critic results, and autonomous disposition.

Legacy identifiers such as
`urn:aviation-agentic-ai:nas-element:EWR` remain unchanged in frozen artifacts.
A separate bridge maps them to V2 canonical identifiers such as
`urn:aviation-agentic-ai:facility:airport:KEWR`.

Abbreviations become graph-aligned in two ways:

1. canonical resources carry preferred labels, alternative labels, typed codes,
   definitions, and source provenance;
2. audit assertions record which source mention resolved to which canonical
   resource and why.

## 9. Alignment Gate

Initial configurable thresholds are:

| Case | Action |
| --- | --- |
| Unique authoritative code with compatible type and date | Accept |
| Unique authoritative alias requiring a code-system bridge | Accept after critic pass |
| Context candidate score at least 0.90 and lead margin at least 0.20 | Accept after critic pass |
| Score below 0.90, insufficient margin, or source conflict | Quarantine and abstain |
| Incompatible type/date or out-of-registry target | Reject |
| Context agent proposes a target outside the supplied registry candidates | Reject |

The thresholds are explicit engineering policy. The regression suite checks
their behavior but does not present them as empirically calibrated confidence.

## 10. Cross-Source Link Rules

- FAA, IATA, and ICAO codes may identify one canonical airport only when an
  authoritative source provides the bridge.
- An ARTCC remains a distinct entity and is never treated as an airport alias.
- METAR links require the same canonical station/facility and a timestamp in
  the configured advisory-neighbor window.
- TAF links require the same canonical station/facility and an intersecting
  forecast validity interval.
- NASR records are selected from the cycle effective at advisory time.
- Every timestamp is normalized to UTC while preserving the raw value.
- Temporal or spatial co-occurrence creates an association, not a causal edge.

## 11. Evidence-Layered Answer Contract

The final answer keeps these fields separate:

```json
{
  "source_assertions": [],
  "observation_evidence": [],
  "forecast_evidence": [],
  "system_associations": [],
  "alignment_explanations": [],
  "citations": [],
  "limitations": [],
  "abstain": false,
  "rationale": "",
  "snapshot_set_id": "",
  "trace_id": ""
}
```

The evidence critic rejects or abstains when an answer:

- lacks a citation for a factual statement;
- presents a TAF as an observation;
- uses a non-overlapping weather record;
- relies on an unaccepted abbreviation alignment;
- abstains on an ambiguous abbreviation without returning its candidate set,
  authority basis, source context, confidence, and candidate margin;
- converts temporal/location association into causal wording; or
- requests live operational decision support.

## 12. Repository Layout

```text
src/aviation_agentic_ai/cross_source/
  contracts.py
  supervisor.py
  artifacts.py
  snapshots/
  alignment/
  graph/
  linking/
  qa/
  evaluation/
src/aviation_agentic_ai/cli_cross_source.py
configs/cross_source_v1.yaml
tests/fixtures/cross_source/
tests/test_cross_source_*.py
```

Artifact layout:

```text
data/raw/cross_source/<snapshot-set>/                 ignored raw snapshots
data/processed/cross_source/<snapshot-set>/           normalized registries and decisions
data/kg/cross_source/<snapshot-set>/                  canonical and audit graphs
data/evaluation/cross_source/v1/                      automated regression and metrics
```

Only bounded normalized or evaluation artifacts required by a reproducible V2
command or evaluation report should enter Git.

## 13. Retired CLI Contract

The former root group exposed `refresh`, `align`, `build`, `neo4j-export`,
`neo4j-load`, `answer`, and `evaluate`. That public command surface has been
removed. The historical Python implementation, focused tests, configuration,
and recorded outputs remain for code-level inspection; they are not a supported
or executable runtime path.

## 14. Automated Policy Regression

The first benchmark contains 24 questions from the 68-record cohort, stratified
across JFK, EWR, and LGA; Ground Stop, GDP, reroute, and general TMI records;
unique and ambiguous abbreviations; METAR-only, TAF-only, combined, and correct
abstention cases.

It evaluates these layers separately:

- mention detection;
- facility alignment;
- operational-term alignment;
- ambiguous-only alignment;
- facility identity links;
- temporal links;
- evidence-layer classification;
- citation precision and recall;
- answer support and abstention;
- unsupported or causal-overstatement counts.

## 15. Release Gates

- Every facility mapping in the regression set resolves to its expected canonical target.
- Every contextual decision records candidates, evidence, score, margin, and
  critic checks.
- Every formal KG edge records snapshot and provenance.
- Citation precision target is 100 percent.
- Unsupported claims and causal overstatements must be zero.
- METAR/TAF evidence-layer confusion must be zero.
- Trace completeness must be 100 percent.
- Evidence gaps or alignment conflicts must result in quarantine and abstention.

These are engineering release gates for the first V2 cohort, not broad research
claims.

## 16. Implementation Sequence

1. Contracts, stable identifiers, artifact I/O, configuration, and CLI shell.
2. Snapshot registry and normalized facility and terminology registries.
3. Mention extraction, deterministic resolution, quarantine, and legacy URI
   bridge.
4. Context alignment node and alignment critic.
5. Canonical and audit graph materialization.
6. Deterministic selection and linking of the 68-record cohort.
7. Layered answers and evidence critic.
8. The 24-question automated regression, evaluation report, and reproducibility
   documentation.

Each stage must be independently testable. Existing ATCSCC agent and thesis
tests remain regression gates throughout the implementation.

## 17. Initial V1 Implementation Status

The first deterministic implementation is now available under
`src/aviation_agentic_ai/cross_source/` and exposed through the `cross-source`
CLI group. It implements versioned local snapshot manifests, NASR and
AviationWeather facility normalization, an FAA-sourced operational-term
registry, two-layer mention extraction, deterministic and contextual alignment
interfaces, critic gates, an autonomous quarantine, canonical/audit RDF graphs, the
frozen 68-record cohort, METAR/TAF temporal linking, layered answers, and an
evidence critic. `CrossSourceState`, `WorkflowNode`, `NodeResult`, and the
validated functional-node adapter form the scheduler-neutral compatibility
surface for a later state-graph implementation.

The graph writer also emits a canonical Neo4j property-graph projection and a
Bolt loader. Neo4j Browser can display accepted mention-to-term/facility edges
and advisory-to-weather associations without changing the RDF canonical or
audit graphs; see `docs/neo4j_visualization.md`.

The verified local build over the pinned inputs currently reports:

- 718 advisories scanned and exactly 68 cohort records selected;
- 28 canonical facility entities and 24 term concepts;
- 8,403 extracted mentions and 8,403 accepted decisions; the pinned run has no
  quarantined decisions because all 68 ambiguous `GS` mentions contain strong
  traffic-management cues;
- 1,475 facility-and-time-gated cross-source associations covering all 68
  cohort advisories;
- 74,006 canonical-graph triples and 166,344 audit-graph triples.
- 9,486 Neo4j nodes and 18,281 Neo4j relationships with no missing endpoints
  or duplicate IDs.

These are implementation diagnostics, not human-validated thesis results. Generated
processed and graph artifacts are ignored and rebuilt from the pinned source
paths. The tracked 24-case `automated_regression_v1.jsonl` currently passes all
24 abstention expectations, all four contextual `GS` expectations, and the
evidence critic. This is policy conformance, not human-validated correctness.
V1 snapshot refresh validates and checksums
configured local artifacts without network access. A network-fetching Source
Agent can be added behind the same snapshot contract without changing the
offline align, build, answer, or evaluate commands.
