# NASA ATMONTO Competency Questions for ATCSCC Advisory Extraction

Last updated: 2026-06-02

## Material Passport

- Artifact: thesis-grade competency-question matrix for the NASA ATMONTO /
  FAA ATCSCC advisory KG extraction study.
- Deep Research input reviewed: downloaded ChatGPT Pro/Deep Research report;
  raw report is treated as local research scratch and distilled here.
- Primary ontology role: NASA ATMONTO runtime profile and ATCSCC schema slice.
- Source family: retrospective FAA ATCSCC / NAS Status advisory records.
- Current gold set: 100 reviewed ATCSCC records in
  `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`.
- Boundary: retrospective research only. These CQs do not support live aviation
  operations, flight planning, dispatch, ATC decisions, or safety certification.

## Review Of The Deep Research Report

Assessment: useful as a design scaffold, but not bibliography-ready without
local verification.

Strengths:

- It correctly reframes CQs as ontology-engineering tests rather than generic
  user questions.
- It separates domain typing, extraction, ontology conformance, provenance,
  queryability, and abstention.
- It forces each CQ to name a metric, likely failure modes, and the system layer
  being tested.
- It preserves the core boundary that ATMONTO is a schema/profile, not semantic
  ground truth.

Limitations to correct before thesis use:

- The downloaded report keeps ChatGPT-internal citation markers such as
  `turn6view...`; those are not reusable thesis citations.
- Some proposed fields, such as `affectedNASelement`, `sourceSpanStart`,
  `sourceSpanEnd`, and PROV-O predicates, are design extensions rather than
  fields in the current common fact contract.
- AFP/CTOP coverage should remain conditional unless the current ATCSCC profile
  and sampled records provide enough evidence for scored evaluation.
- Queryability must stay source-bounded. The current remediation supports KG
  construction metrics and limited graph queries, not an end-to-end GraphRAG
  answer-improvement claim.

Portable source anchors to use instead of internal ChatGPT citations:

- NASA NTRS: The NASA Air Traffic Management Ontology technical documentation,
  NASA/TM-2017-219526.
- FAA ATCSCC advisory database categories: Airspace Flow Programs, CTOP
  Programs, Ground Stops, Ground Delay Programs, Route advisories, and other
  advisories.
- W3C SHACL Recommendation: RDF data-graph validation against shapes graphs.
- W3C PROV-O Recommendation: OWL2 ontology for representing provenance in RDF.
- Local protocol and scoring artifacts:
  `docs/experiment_protocol.md`,
  `docs/nasa_atmonto_gold_annotation_guide.md`, and
  `reports/stages/nasa_atmonto_formal_experiment_scoring.md`.

## Design Principles

1. A CQ is accepted only if it can drive an annotation field, validator rule,
   query pattern, or evaluation metric.
2. Source text is the semantic evidence for ABox facts. ATMONTO constrains
   terms, classes, predicates, datatypes, and domain/range checks.
3. S0 owns deterministic fields: `advisoryNumber`, `issuedTime`,
   `effectiveStartTime`, `effectiveEndTime`, and header/template facts.
4. S3/S4 may add semantic fields but must not overwrite reviewed deterministic
   facts: `controlledNASelement`, `departureScope`, `extensionProbability`,
   `impactingCondition`, `impactingConditionMessage`, `implementationStatus`,
   `initiativeComments`, `reRouteReason`, and `reRouteType`.
5. Validator acceptance is not semantic truth. Schema-valid but unsupported facts
   remain false positives; source-supported but profile-rejected facts remain
   profile gaps until a reviewed bridge is added.
6. Missing information should produce `Unknown`, no triple, or an abstention
   decision. It should not be filled from aviation common sense.

## Primary CQ Matrix

| ID | Role | Wording | In-scope advisory types | ATMONTO/profile terms | Gold fields | Validation/query pattern | Metric | Failure modes | System layer |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CQ-D01 | Domain typing | Can each advisory be represented as exactly one reviewed primary TMI/advisory type for the current profile? | `GroundStopTMI`, `GroundDelayProgramTMI`, `ReRouteTMI`, generic `TrafficManagementInitiative`; AFP/CTOP only when profile/sample support exists. | `TrafficManagementInitiative`, `GroundStopTMI`, `GroundDelayProgramTMI`, `ReRouteTMI`, `rdf:type`, `advisoryNumber`. | `subject_class`, `advisoryNumber`, `source_id`, title/evidence cue. | Count primary type assertions per advisory; flag `count != 1` or unsupported class. | Primary-type accuracy; type-cardinality violation rate. | Title-string misclassification, cancellation treated as new TMI, generic TMI overuse, AFP/CTOP overclaim. | S0, S1b, S2, S3, S4, validator. |
| CQ-D02 | Entity role | Can the system identify the controlled NAS element and avoid merging it with broader affected/scope text? | GS, GDP, ReRoute, generic advisories. | `controlledNASelement`, `Airport`, `TFMcontrolElement`, `Facility`, `Route`, local NAS element IDs. | `predicate`, `object`, `object_class`, `evidence_text`, `source_id`. | Require at least one evidence-supported controlled element when the source states one; unresolved objects are quarantined. | Role-aware entity F1; unresolved-element rate. | ARTCC center rejected as range gap, route/fix collapsed into text, FCA treated as airport, controlled versus affected element confusion. | S0 parser, entity canonicalizer, S2/S4 enrichment, validator. |
| CQ-D03 | Temporal semantics | Can the system keep issued, effective-start, and effective-end times distinct and normalized without inventing missing times? | All reviewed advisory classes. | `issuedTime`, `effectiveStartTime`, `effectiveEndTime`, `xsd:dateTime`. | Normalized value, raw time string, evidence span, `source_id`. | Parse raw `SIGNATURE`, `EFFECTIVE TIME`, or equivalent fields; check datatype and feasible ordering while allowing reviewed zero-duration intervals. | Exact normalized-time accuracy; fabricated-time false-positive rate. | Signature/effective-time confusion, cross-day rollover error, volcanic advisory DTG mistaken for ATCSCC signature, invented end time. | S0 time normalizer, S1b canonicalizer, S2/S3/S4. |
| CQ-E01 | Status/action | Can the system extract lifecycle or action status without turning possible, planned, revised, or cancelled text into an active initiative? | GS, GDP, ReRoute, generic advisories. | `implementationStatus`, `initiativeComments`, `effectiveStartTime`, `effectiveEndTime`. | Status value, action cue, comments text, evidence span. | Enum check plus source cue check for active/revised/cancelled/planned/possible or local reviewed equivalent. | Status-label accuracy; active-overclaim rate. | Cancellation ignored, planned/proposed text treated as active, revised text becomes duplicate advisory, empty comments captured as status. | S0, S2, S3, S4. |
| CQ-E02 | Cause/condition | When the source explicitly states a reason or impacting condition, can the system extract it and preserve the supporting message text? | GS, GDP, AFP/CTOP if supported, generic advisories. | `impactingCondition`, `impactingConditionMessage`, `initiativeComments`, `reRouteReason`. | Condition label, raw cause text, evidence span, comments. | Accept a cause only when the evidence span states it; map approved enums only. | Cause-label macro-F1; unsupported-cause rate. | Weather defaulting, staffing lost as `other`, unsupported enum mapping, source comments dropped. | S2/S3/S4 enrichment, enum canonicalizer, gold review. |
| CQ-E03 | Route/airspace semantics | For route-like advisories, can the system extract route or constrained-airspace semantics without collapsing them into airport-only GS/GDP facts? | ReRoute first; AFP/CTOP deferred unless profile/sample support exists. | `ReRouteTMI`, `reRouteType`, `reRouteReason`, `controlledNASelement`, `initiativeComments`. | Primary type, route/constrained element, reroute type, explicit reason, evidence. | Require ReRoute-specific predicates only on ReRoute-compatible records; otherwise quarantine. | ReRoute predicate-family F1; constrained-element F1. | Reroute cancellation treated as active reroute, route string collapsed into comments only, reason hallucinated, AFP/CTOP confused with ReRoute. | S2/S3/S4, validator/repair. |
| CQ-O01 | Core conformance | Does every accepted TMI/advisory instance satisfy the current profile's required identity, source, time, and evidence constraints? | All reviewed advisory classes. | `TrafficManagementInitiative`, `advisoryNumber`, `source_id`, `issuedTime`, `evidence_text`. | Fact IDs, predicates, datatypes, evidence text, validator status. | SHACL/custom shape: one advisory number, one source ID, one issued time when present in source, nonempty evidence for accepted non-type facts. | Schema violation rate; repair success rate. | Duplicate IDs, missing source, empty evidence, invalid datatype, repair-only semantic drift. | Validator/repair, S3, S4. |
| CQ-O02 | Type-specific conformance | Are type-specific fields consistent with the primary class and current profile rather than leaking across advisory types? | GS, GDP, ReRoute; AFP/CTOP conditional. | `GroundStopTMI`, `GroundDelayProgramTMI`, `ReRouteTMI`, `extensionProbability`, `reRouteType`, `reRouteReason`, `impactingConditionMessage`. | Primary type, typed predicates, raw/normalized values, validator errors. | Class-specific shape groups; reject or quarantine fields outside approved domain/range. | Type-specific violation rate; profile-gap count. | GS carrying GDP-only message fields, ReRoute with only airport stop fields, `MODERATE` not normalized to `MEDIUM`, validator over-repair. | Schema-slice LLM, validator/repair, S4. |
| CQ-P01 | Evidence coverage | Does every accepted non-type fact have source ID plus a minimal evidence text that appears in the advisory record? | All reviewed advisory classes. | `source_id`, `evidence_text`, optional future span offsets, provenance metadata. | `source_id`, `evidence_text`, `source_system_id`, `fact_id`, extraction stage. | Exact or whitespace-normalized evidence containment check. | Percent facts with contained evidence; evidence near-miss count. | Orphan triples, document-level citation only, reused vague span, evidence text not in source. | S0/S2/S3/S4, evidence checker. |
| CQ-P02 | Evidence support | Does the evidence span actually support the extracted value, not merely co-occur in the same advisory? | All reviewed advisory classes. | `evidence_text`, `initiativeComments`, `impactingConditionMessage`, local support judgement. | Target value, evidence text, support judgement, invalid candidate IDs. | Manual or LLM-assisted support judgement: supported, unsupported, ambiguous, profile-gap. | Unsupported-triple rate; semantic precision. | Correct paragraph but wrong object, post-hoc citation, paraphrase beyond source, schema-valid false positive. | Gold review, adversarial validator review, S4 diagnostics. |
| CQ-Q01 | Source-bounded queryability | Can the materialized KG answer a template query over the frozen snapshot without consulting live sources or adding unstated facts? | Current reviewed ATCSCC snapshot only. | `TrafficManagementInitiative`, `controlledNASelement`, `impactingCondition`, `effectiveStartTime`, `effectiveEndTime`, `implementationStatus`. | Query target fields, returned advisory IDs, citations/evidence. | Template query: affected element + TMI type + time window + explicit condition/status. | Answer-set precision/recall; citation support. | Time filter error, cancelled records included, source-family leakage, normalized entity mismatch. | Graph materialization, graph query, later GraphRAG layer. |
| CQ-A01 | Abstention | When a field is absent, weakly implied, out of profile, or cross-source-dependent, does the system abstain or mark it unknown instead of inventing a triple? | All reviewed advisory classes. | `effectiveEndTime`, `extensionProbability`, `impactingCondition`, `reRouteReason`, `controlledNASelement`, evidence metadata. | Field-present/absent flags, explicitness label, evidence text, missing-fact notes. | If gold has no explicit evidence, output no triple, `Unknown`, or an abstention reason. | Absent-field false-positive rate; abstention correctness. | Common-sense completion, controlled vocabulary forcing, inferred weather/volume/runway cause, unsupported profile extension. | S1b/S2/S3/S4, sufficiency/abstention layer. |

## Deferred Cross-Source CQs

| Deferred CQ | Why deferred |
| --- | --- |
| Can route, fix, FCA, airport, and ARTCC mentions be linked to NASR/AIXM identifiers with reviewed alias and spatial rules? | Requires external reference layers and entity-disambiguation policy; not a clean single-source extraction metric. |
| Can weather-related impacting conditions be corroborated against METAR, TAF, SIGMET, CWSU, or volcanic ash advisories? | Changes the task from source-bounded extraction to cross-source corroboration. |
| Can FAA/NASA PDF reference documents provide definitions, procedure constraints, and mapping evidence for ATCSCC terms? | Belongs to the separate PDF reference-document source family and should not be mixed with ATCSCC event F1. |
| Can AIRM-O or ATMONTO2AIRM alignments improve interoperability without replacing NASA ATMONTO as the primary profile? | Alignment is schema-level evidence, not ABox ground truth. |
| Can GraphRAG answer free-form aviation questions with faithful citations after KG construction succeeds? | Requires a separate answer-generation protocol; current claims are KG construction and limited source-bounded queryability. |

## Literature Search Strings

| Priority | Search string |
| --- | --- |
| P1 | `"competency questions" ontology engineering Gruninger Fox SPARQL formalization` |
| P2 | `site:ntrs.nasa.gov ATMONTO "Air Traffic Management Ontology" "TrafficManagementInitiative"` |
| P3 | `site:fly.faa.gov ATCSCC advisory "Ground Stops" "Ground Delay Programs" "Route advisories"` |
| P4 | `"ontology-based information extraction" schema constrained knowledge graph population` |
| P5 | `site:w3.org SHACL Recommendation RDF validation shapes constraints` |
| P6 | `"SHACL repair" RDF graph validation constraint violation explanation` |
| P7 | `site:w3.org PROV-O provenance ontology evidence grounding RDF` |
| P8 | `"citation faithfulness" retrieval augmented generation attribution GraphRAG provenance` |

## Acceptance Gate

This CQ matrix is good enough for the thesis only if the implementation and
evaluation can answer the following checks:

1. Exactly 12 primary CQs are used for the first reviewed ATCSCC snapshot.
2. Each primary CQ maps to at least one gold field, validator rule, query
   pattern, or metric.
3. Profile gaps remain explicit and are not counted as accepted gold facts until
   a reviewed bridge exists.
4. Citation correctness, evidence containment, semantic correctness, and schema
   conformance are reported separately.
5. No claim is made about live operational use or general aviation KG
   completeness.

## Recommended Thesis Wording

This thesis evaluates whether a NASA ATMONTO-derived ATCSCC schema slice can
help an LLM-assisted extraction pipeline produce semantically reviewed,
schema-valid, evidence-grounded, and source-bounded queryable knowledge graph
facts from retrospective FAA ATCSCC advisories. The competency questions test
domain typing, controlled NAS elements, temporal semantics, stated causes,
type-specific fields, validator conformance, evidence support, profile-gap
handling, and disciplined abstention. They do not claim operational readiness,
real-time decision support, or that ATMONTO alone is aviation ground truth.
