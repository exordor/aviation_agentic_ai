# ATCSCC Semantic Requirements Document

## Boundary

- Retrospective FAA ATCSCC advisory extraction only; no live operational use.
- NASA ATMONTO is the primary ontology/profile reference for this experiment.
- The gold set is reviewed retrospective ATCSCC advisory evidence, not live truth.

## Competency Question Contract

- CQ count: 12
- Route counts: `{"abstain": 1, "deterministic": 2, "graph": 2, "hybrid": 4, "validator": 3}`

## Required Predicates

| Predicate | CQ mentions |
| --- | ---: |
| `controlledNASelement` | 4 |
| `reRouteReason` | 4 |
| `effectiveEndTime` | 3 |
| `evidence_text` | 3 |
| `impactingCondition` | 3 |
| `initiativeComments` | 3 |
| `advisoryNumber` | 2 |
| `effectiveStartTime` | 2 |
| `extensionProbability` | 2 |
| `impactingConditionMessage` | 2 |
| `implementationStatus` | 2 |
| `issuedTime` | 2 |
| `reRouteType` | 2 |
| `source_id` | 2 |
| `rdf:type` | 1 |

## Subject Classes

| Class | Records |
| --- | ---: |
| `TrafficManagementInitiative` | 40 |
| `ReRouteTMI` | 23 |
| `GroundStopTMI` | 21 |
| `GroundDelayProgramTMI` | 16 |

## Evidence Contract

- Every extracted fact must carry source-bounded `evidence_text`.
- Facts without source support must be rejected or marked for abstention.
- Known gap: stable character offsets are not yet a first-class artifact.
