# ATCSCC as Event-Centric Semantic Knowledge Extraction

Date: 2026-06-03

Status: thesis framing report. This document explains the task structure behind
the current ATCSCC / NASA ATMONTO experiment.

## Core Claim

The ATCSCC advisory task is best described as:

> Event-centric semantic knowledge extraction from semi-structured aviation
> advisories, constrained by an ATMONTO-derived application profile and
> evaluated through competency questions.

It is not a generic document summarization task, and it is not full ontology
population for the entire NASA ATMONTO ontology.

## Why ATCSCC Advisories Are Event-Centric

Each ATCSCC advisory describes a traffic-management event or event update:

- an advisory identifier and issue time;
- an event type such as Ground Stop, Ground Delay Program, Reroute, or generic
  Traffic Management Initiative;
- affected NAS elements such as airports, ARTCCs, fixes, routes, or facilities;
- temporal arguments such as start time and end time;
- status/action fields such as issued, canceled, amended, planned, or updated;
- causal or contextual conditions such as weather, volume, equipment, runway,
  staffing, or operational constraints;
- provenance fields linking the extracted fact back to the source advisory and
  evidence text.

The extraction target is therefore an event record with typed arguments and
relations, not a bag of unrelated triples.

## Event Schema

| Event component | ATCSCC example | Ontology/profile target | Evaluation role |
| --- | --- | --- | --- |
| Event mention | one advisory HTML record | TMI individual or subclass instance | creates the source-bounded event unit |
| Event type | GS, GDP, Reroute, advisory/update | `GroundStopTMI`, `GroundDelayProgramTMI`, `ReRouteTMI`, `TrafficManagementInitiative` | checks class assignment and event typing |
| Identifier | advisory number | `advisoryNumber` | deterministic backbone and source alignment |
| Time arguments | issued, effective start, effective end | `issuedTime`, `effectiveStartTime`, `effectiveEndTime` | temporal completeness and consistency |
| Affected element | airport, ARTCC, route, fix, NAS element | `controlledNASelement` or profiled target field | answerability for affected-scope CQs |
| Cause/condition | weather, volume, runway, equipment, other | `impactingCondition`, `impactingConditionMessage`, `reRouteReason` | semantic extraction and abstention |
| Status/action | implemented, canceled, amended, planned | `implementationStatus`, `initiativeComments` | event lifecycle semantics |
| Route semantics | route type, reroute reason, constrained element | `reRouteType`, `reRouteReason`, `controlledNASelement` | relation-heavy queryability |
| Provenance | source ID, evidence text/span | `source_id`, `evidence_text`, source-span metadata | evidence containment/support |

## Extraction Subtasks

| Subtask | What the system must do | Current implementation layer |
| --- | --- | --- |
| Event detection | identify one advisory event record from raw HTML | ATCSCC parser and aligned records |
| Event typing | map advisory format/title/content to a TMI type | S0 parser plus ATMONTO profile |
| Argument extraction | fill event fields for time, target, cause, status, route | S0/S2/S3/S4 candidate facts |
| Ontology canonicalization | map extracted labels to profile predicates/classes/enums | schema slice, canonicalizers, validators |
| Evidence grounding | attach each extracted value to source advisory evidence | reviewed gold and candidate evidence text |
| Constraint validation | reject facts outside domain/range/cardinality/profile rules | validator gate and rejection analysis |
| Repair/quarantine | repair structural issues or quarantine unsupported facts | S3/S4 repair and rejection logs |
| Queryability evaluation | answer CQs over accepted facts | CQ query evaluation |
| GraphRAG evaluation | compare source/vector/graph/hybrid answer layers | answer-generation pilot and planned S7 gate |

## Why A Profile Slice Is Correct

Full ATMONTO covers a wider aviation and NAS conceptual model than the ATCSCC
advisory source exposes. ATCSCC advisories mostly reveal TMI event ABox facts:
type, target, time, reason, status, and evidence provenance.

Using the whole ontology would create three problems:

1. **Unsupported completeness claims:** many ATMONTO concepts are not observable
   from an ATCSCC advisory.
2. **Extraction noise:** the model would be encouraged to invent concepts that
   are absent from the source.
3. **Unfair evaluation:** missing facts from unrelated ATMONTO areas would look
   like extraction failures even though the source never contained them.

The defensible object is therefore an **ATCSCC application profile**:

- complete relative to the 12 primary ATCSCC CQs;
- correct relative to source-supported event fields and ATMONTO-compatible
  domain/range constraints;
- explicitly incomplete for non-ATCSCC aviation knowledge.

## Relation To S0-S4 Systems

| System | Event-centric role |
| --- | --- |
| `S0_rule_only` | deterministic event backbone for identifiers, obvious fields, and stable template structure |
| `S1_llm_only` | drift diagnostic for open extraction without a reliable ontology interface |
| `S1b_llm_canonicalized` | open LLM facts canonicalized into the event profile for fair comparison |
| `S2_llm_schema_slice` | flat ontology-profile prompting for event facts |
| `S3_llm_schema_slice_validator_repair` | profile validation and repair for event facts |
| `S4_hybrid_backbone_enrichment` | current best event-centric extractor: deterministic backbone plus semantic enrichment |

## Evaluation Implications

The event-centric framing requires layered metrics:

- **event coverage:** how many advisory events have a valid event instance;
- **argument precision/recall/F1:** per field or predicate family;
- **event type accuracy:** correct TMI subclass or generic TMI fallback;
- **temporal correctness:** valid issued/start/end times and missing-time
  abstention;
- **cause/status correctness:** supported cause and lifecycle fields;
- **evidence support:** each value is traceable to source evidence;
- **ontology conformance:** class, predicate, domain/range, cardinality, and
  profile constraints;
- **queryability:** CQs can recover the source-bounded answer sets;
- **GraphRAG behavior:** graph retrieval is useful only when event relations,
  joins, or paths are needed.

## Thesis Wording

Use:

> The case study addresses event-centric semantic knowledge extraction from FAA
> ATCSCC advisories. A NASA ATMONTO-derived application profile constrains the
> extraction of traffic-management event types, arguments, temporal fields,
> conditions, and provenance. The resulting KG is evaluated by competency
> questions, evidence support, schema conformance, and downstream
> source-bounded retrieval/answering.

Do not use:

> The system extracts the full NASA ATMONTO ontology from ATCSCC advisories.

The latter is not correct because ATCSCC advisories do not expose the full
conceptual scope of ATMONTO.
