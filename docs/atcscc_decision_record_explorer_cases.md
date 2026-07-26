# ATCSCC Decision Record Explorer Case Set

Status: validated acceptance set; critical query fixes implemented on `main`
Selected: 2026-07-26
Scope: two positive records and one missing-reason control

## Stage Header

| Required item | Decision |
| --- | --- |
| Current objective | Lock the smallest source-audited case set before implementation. |
| Minimum experiment | One Ground Stop, one Ground Delay Program, and one record with no declared reason. |
| Minimum components | Existing tracked ATCSCC snapshot, active parser, schema guide, and configured facility registry. |
| Expected evidence | Exact source spans for type, facility, operational period, declared reason, and missing reason. |
| Success condition | Every expected value or missing state is source-observable without adding a source or ontology term. |
| Failure condition | A required value depends on model knowledge, an untracked raw file, or an expanded facility cohort. |
| Explicitly deferred | Episode grouping, weather evidence, outcomes, similarity, and recommendation. |

The case selection is **Critical Path**. It determines whether the existing
system can support the approved explorer without changing its data boundary.

## 1. Selection Rules

The selected records must:

- exist in the tracked aligned advisory snapshot;
- use facilities already present in the configured JFK/EWR/LGA cohort;
- contain exact source spans for every positive field;
- exercise Ground Stop and Ground Delay Program records;
- include one honest missing-reason outcome;
- require no new source, Agent, ontology class, or ontology property.

The tracked source of record is:

`data/processed/nasa_atmonto/aligned/2026-05-14/atcscc_advisories.jsonl`

The `raw_file` fields point to locally retained HTML snapshots, but those files
are ignored by Git. The explorer bundle must therefore be derived from the
tracked JSONL record and the validated run artifacts, not from an untracked HTML
path.

## 2. Positive Case A - Ground Stop

| Field | Approved value |
| --- | --- |
| Source ID | `2026-05-19:123` |
| Advisory | `123` |
| Decision record type | Ground Stop |
| Controlled facility | JFK |
| Canonical facility | `urn:aviation-agentic-ai:facility:airport:KJFK` |
| TMI operational period | `2026-05-19T21:00:00Z` to `2026-05-19T22:45:00Z` |
| Source-declared reason | `WEATHER / THUNDERSTORMS` |
| Tracked record | aligned advisory JSONL line 524 |

Required source spans:

```text
ATCSCC ADVZY 123 JFK/ZNY 05/19/2026 CDM GROUND STOP
CTL ELEMENT: JFK
GROUND STOP PERIOD: 19/2100Z - 19/2245Z
IMPACTING CONDITION: WEATHER / THUNDERSTORMS
```

This is the fixed real advisory already used by the Formal Graph Kernel, Query
Agent, and CLI test surface. It minimizes implementation risk.

The active NASA schema slice does not permit `atm:impactingCondition` on
`atm:GroundStopTMI`. The reason must therefore remain a source-bound
`ProfileGap`, not a formal KG fact. The explorer may state what the source says
and must visibly label the formal-profile limitation.

## 3. Positive Case B - Ground Delay Program

| Field | Approved value |
| --- | --- |
| Source ID | `2026-05-19:138` |
| Advisory | `138` |
| Decision record type | Ground Delay Program |
| Controlled facility | JFK |
| Canonical facility | `urn:aviation-agentic-ai:facility:airport:KJFK` |
| TMI operational period | `2026-05-19T22:05:00Z` to `2026-05-20T02:59:00Z` |
| Source-declared reason | `WEATHER / THUNDERSTORMS` |
| Tracked record | aligned advisory JSONL line 537 |

Required source spans:

```text
ATCSCC ADVZY 138 JFK/ZNY 05/19/2026 CDM GROUND DELAY PROGRAM
CTL ELEMENT: JFK
CUMULATIVE PROGRAM PERIOD: 19/2205Z - 20/0259Z
IMPACTING CONDITION: WEATHER / THUNDERSTORMS
```

This record stays within the configured facility cohort and provides a valid
GDP reason under the active schema. It also connects to the same canonical JFK
facility as Case A, allowing the explorer to demonstrate canonical entity reuse
without claiming that the two advisories belong to the same decision episode.

The earlier parser rejected the end of this cross-midnight period because its
day differed from the header day. The deterministic parser now accepts only an
anchored same-day or immediately following calendar day, including month and
year rollover.

## 4. Missing-Reason Control

| Field | Approved value |
| --- | --- |
| Source ID | `2026-05-20:020` |
| Advisory | `020` |
| Record form | Ground Delay Program cancellation |
| Controlled facility | EWR |
| Canonical facility | `urn:aviation-agentic-ai:facility:airport:KEWR` |
| Operational period | `2026-05-20T01:24:00Z` to `2026-05-20T05:46:00Z` |
| Source-declared reason | Absent |
| Tracked record | aligned advisory JSONL line 578 |

Required source spans:

```text
ATCSCC ADVZY 020 EWR/ZNY 05/20/2026 CDM GROUND DELAY PROGRAM CNX
CTL ELEMENT: EWR
GDP CNX PERIOD: 20/0124Z - 20/0546Z
```

There is no `IMPACTING CONDITION` field in this record. A declared-reason
question must return an explicit missing or insufficient state without a
provider call. The record is only a missing-field control; this stage does not
interpret cancellation or group it into a lifecycle.

## 5. Time Semantics

The active parser maps the TMI operational period to
`atm:effectiveStartTime` and `atm:effectiveEndTime`:

- `GROUND STOP PERIOD` for Ground Stop;
- `CUMULATIVE PROGRAM PERIOD` for Ground Delay Program;
- `GDP CNX PERIOD` for the missing-reason control.

The advisory also contains a separate field literally named `EFFECTIVE TIME`.
That field is an advisory envelope and may differ from the TMI operational
period. The explorer must not merge or relabel the two. The first implementation
shows the TMI operational period because that is the time represented in the
active formal graph.

## 6. Implementation Status

### Completed Critical Path

1. [x] Anchor a valid next-day period end for cross-midnight records such as
   `19/2205Z - 20/0259Z`.
2. [x] Normalize valid GDP reasons to the schema's lowercase value set and add
   `atm:advisoryNumber` and `atm:impactingCondition` to the bounded Query Agent
   read surface.
3. [x] Let the read-only query path retrieve source-bound `ProfileGap` entries so it
   can report the Ground Stop reason without promoting it to a KG fact.
4. [x] Stop the impacting-condition source span before the `COMMENTS:` field.
5. [x] Preserve the distinction between TMI operational period and advisory
   envelope in labels and evidence.

### Completed Evidence Checks

- [x] Show the normalized formal reason and exact source wording separately.
- [x] Show the fact ID or profile-gap record plus its source ID.
- [x] Confirm both positive records resolve to the same canonical JFK node.
- [x] Confirm the missing-reason control makes no provider call.

### Deferred Hardening

- materializing `atm:impactingConditionMessage`;
- a general multi-run search index;
- new airport cohorts;
- advisory episode inference.

## 7. Acceptance Expectations

The `main` implementation satisfies the acceptance contract when:

- Case A returns type, JFK, operational period, and source-bound reason;
- Case B returns type, JFK, complete cross-midnight operational period, and
  formally valid reason;
- the missing-reason control returns no invented reason;
- both positive cases reuse canonical KJFK;
- all displayed values trace to the selected source record;
- no output claims that WEATHER caused, justified, or optimized either TMI.
