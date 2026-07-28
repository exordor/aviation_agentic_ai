# Multi-Agent Aviation Event Knowledge System

Status: normative current architecture with bounded Decision Case Analysis

Date: 2026-07-28

## 1. Purpose and Scope

This document defines the runnable system for converting one retrospective FAA
ATCSCC advisory and bounded authority records into an evidence-bound decision
case, validated graph artifacts, and bounded graph-grounded answers. It is the
normative description of the current implementation.

The system is not live ATC decision support, a complete aviation ontology, a
causal explanation engine, or a TMI recommendation system. It does not claim
that a reported observation caused a measure or that a measure was optimal.

## 2. Current Architecture

```text
ATCSCC advisory + bounded FAA authority records
  -> deterministic AdvisoryParser
  -> deterministic facility and terminology authority services
     -> shared Semantic Resolution Agent only for genuine ambiguity
  -> deterministic Weather and BTS adapters
  -> sealed Decision Case Assembly task
     -> canonical zero-call compiler for the three approved cases
     -> bounded Decision Case Assembly Agent only for genuine evidence/schema choice
  -> exact preflight
  -> deterministic Formal Graph Kernel
  -> profile-owned current-run artifacts
  -> deterministic query routing with bounded read-only graph tools
     -> Decision Case Analysis Agent only for exact registered analysis questions
```

The coordinator, parsers, authority services, adapters, validators, profiles,
writers, and materializers are deterministic components. They are not Agents.
The ontology profile constrains publication; it is not an Agent.

Only three components can make bounded model-mediated decisions:

1. the shared Semantic Resolution Agent;
2. the Decision Case Assembly Agent;
3. the Decision Case Analysis Agent for exact registered bounded analysis
   questions.

No Critic, Verifier, Planner, Memory, Weather, BTS, ASPM, or recommendation
Agent is active.

## 3. System Increment and Boundaries

| Item | Current decision |
| --- | --- |
| Capability | Build, inspect, and narrowly analyze one source-bounded ATCSCC decision case with audited context. |
| Smallest end-to-end result | Ingest one approved advisory, publish only accepted facts, and answer registered questions from the run artifacts. |
| Minimum components | AdvisoryParser, authority services, optional semantic/assembly Agents, Weather/BTS adapters, Formal Graph Kernel, profiles, materializers, deterministic query tools, and bounded Decision Case Analysis. |
| Evidence | Source IDs, exact evidence text, snapshot checksums, sealed contracts, preflight records, fact traces, and deterministic tests. |
| Success | Accepted facts materialize consistently; profile gaps and missing evidence remain distinct; registered queries return `ok`, `insufficient`, or `blocked`. |
| Failure | A component invents a candidate, source, fact, cause, ontology term, or graph write; a provider is built on a deterministic path; or a result bypasses the Kernel. |
| Deferred | Causal explanation, recommendation, lifecycle episode grouping, historical ranking, full-corpus live execution, general aviation QA, and analysis outside the exact registered families. |

## 4. Source and Evidence Boundaries

The source families remain distinct:

- ATCSCC advisory records support source-declared event fields and declared
  reasons.
- FAA NASR and ARTCC records support facility authority resolution.
- FAA terminology records support operational-term authority resolution.
- METAR and TAF records supply time-bounded Weather context.
- BTS records supply source-qualified public operational observations.

Every accepted fact has source IDs, exact evidence text, a profile binding, and
an auditable fact trace. Authority records support resolution only; they do not
authorize event facts. Profile gaps are source-supported audit records and
never become formal RDF or Neo4j facts.

The runtime uses these terminal states:

| State | Meaning |
| --- | --- |
| `ok` | Validated evidence supports the requested result. |
| `insufficient` | The field, optional layer, or registered evidence is absent or unsupported. |
| `blocked` | A required contract, source, checksum, schema, or provider dependency failed. |
| `profile_gap` | The source supports a value that the active formal profile cannot publish. |

## 5. Deterministic Intake and Authority Services

`AdvisoryParser` deterministically extracts source-supported mentions and
structured fields from one advisory. It does not canonicalize a facility,
choose an ontology term, write a graph, or make a provider call.

The facility and terminology authority services each preserve their own source
family and candidate construction. They deterministically return a blocked,
insufficient, or unique accepted result when the authority evidence permits
one. They do not become Agents merely because their result is recorded in an
EvidenceCard.

For every authority result, the runtime preserves the source record bindings,
candidate audits, task and proposal identity, source-qualified evidence, and
the decision basis. A unique result must not construct a model factory.

## 6. Shared Semantic Resolution Agent

The Semantic Resolution Agent activates only when a facility or terminology
authority service has more than one eligible, source-bound candidate. It
receives a sealed `ResolutionTask` with a closed candidate set, authority
evidence, schema constraints, and remaining budget. It can accept an eligible
candidate or abstain; it cannot create a candidate, canonical ID, source,
definition, class, or property.

Its tools are read-only and candidate-bounded:

```text
get_resolution_candidates
get_authority_record
get_ontology_context
check_candidate_constraints
compare_candidate_evidence
```

The Agent may request one batch of at most three tools and has at most two
provider calls. A pre-activation blocked, insufficient, zero-candidate, or
unique-candidate path uses no provider. Malformed, out-of-scope, or
indistinguishable output returns a sealed abstained or blocked result, as the
contract requires.

## 7. Weather and BTS Context

Weather and BTS preparation is deterministic and precedes Decision Case
Assembly. The adapters select and validate source-bound records, then seal
their state into the Assembly task.

Weather rules:

- a TAF is issued no later than the advisory signature time and overlaps the
  operational period;
- the METAR context is the latest report in the allowed pre-issue window plus
  reports in the half-open operational period;
- Weather reports can enter the formal graph only through the curated Weather
  profile;
- event-to-Weather associations are audit-only and carry
  `causal_claim=false`.

BTS rules:

- baseline, active, and recovery windows are respectively `[-2h, start)`,
  `[start, end)`, and `[end, +6h)`;
- the formal public-observation profile owns BTS-reported observations,
  derivations, quantities, units, and traces;
- BTS observations are not FAA demand, AAR, capacity, EDCT, ASPM data, or
  proof that a TMI caused an outcome.

Weather and BTS context never supplies or changes a declared-reason state.

## 8. Decision Case Assembly

The runtime seals a `CaseAssemblyTask` after deterministic parsing, authority
resolution, Weather/BTS preparation, and profile checks. The task binds core
facts, source and evidence references, profile gaps, resolution proposals,
context associations, observations, component states, and source snapshots.

The three approved cases use `compile_case_assembly_proposal` and require no
Assembly provider construction or call. A non-canonical record may activate the
Decision Case Assembly Agent only when a dedicated factory is available and a
genuine evidence/schema choice remains. The Agent sees a compact task-bound
schema context and read-only task tools; it never receives graph-write
authority.

Every proposal is checked against the exact sealed task before publication. A
repair is allowed only for the explicitly permitted value-only correction. Any
out-of-task, causal, source-binding, schema, profile, or evidence violation is
blocked. The Formal Graph Kernel remains the sole final publication authority.

## 9. Formal Graph Kernel and Profiles

The Formal Graph Kernel validates graph-patch facts for active profile
membership, identity, source evidence, datatype, domain/range, and graph
constraints. It accepts only the formal layers owned by their profiles:

1. ATCSCC decision facts under the NASA ATMONTO decision profile;
2. METAR/TAF report facts under the curated Weather profile;
3. BTS-reported observations under the public-observation profile.

Every accepted fact carries the owning profile identifier and checksum. No
model writes directly to RDF, Turtle, Neo4j, or a final graph artifact.

## 10. Current Run Artifacts

A current validated run contains the profile-owned projections:

```text
kg.jsonl
kg.ttl
neo4j_nodes.jsonl
neo4j_relationships.jsonl
```

It also contains the audit record appropriate to the run, including
`run_manifest.json`, `source_snapshots.jsonl`, `profile_gaps.jsonl`,
`context_associations.jsonl`, `outcome_summaries.jsonl`,
`weather_fact_trace.jsonl`, `observation_derivations.jsonl`,
`observation_fact_trace.jsonl`, and `reconstruction_trace.json`. The manifest
records paths, counts, checksums, and `ok | insufficient | blocked` layer
states.

RDF and Neo4j are projections of accepted formal facts. The audit artifacts do
not become an independent semantic authority. Each persisted profile gap is
owned by the exact current decision profile and checksum, carries a stable
event/source/snapshot identity plus a deterministic evidence reference, and
must reproduce the advisory parser's exact field value and evidence span.
`profile_gaps.jsonl` is registered independently in the manifest with its
path, row count, SHA-256, and status; a generic substring from the source
cannot authorize a profile-gap answer.

Model-bound analysis writes a separate immutable directory:

```text
analysis/<analysis_run_id>/
  case_analysis_task.json
  query_evidence_bundle.json
  case_analysis_run.json
```

These artifacts do not modify the run manifest or overwrite `query_run.json`.

## 10.1 Cross-Run Corpus Storage

Validated run directories are portable evidence and debugging bundles. For
multi-event processing, `agent-system build-corpus` compacts them into a
normalized corpus:

```text
source_objects/<sha256>.txt
source_bindings.jsonl
cases.jsonl
facts.jsonl
case_facts.jsonl
corpus_manifest.json
```

Source payloads are stored once by content checksum. `facts.jsonl` retains the
canonical `ValidatedFact` representation with full IRIs, while
`case_facts.jsonl` records membership without duplicating fact content. This
layer adds no Agent role, model call, causal claim, vector index, or historical
ranking. RDF and Neo4j remain rebuildable projections.

`agent-system ask-corpus` opens a checksum-verified read view over the case,
fact, membership, and source-binding tables. It supports exact filters with
bounded pagination and can answer the existing formal record questions for an
explicit event ID. It does not emulate a complete run directory: profile-gap
evidence text, non-causal context associations, outcome summaries, and
analysis artifacts remain owned by the original run bundle.

## 11. Query Tools and Decision Case Analysis

The query surface reads only validated run artifacts through bounded read-only
tools. Registered deterministic question families cover the
measure, facility, operational period, declared reason, provenance, decision
context, public observations, and reconstruction record. Missing or
unsupported registered evidence returns `insufficient` before model
construction. These existing routes, including the combined record question,
remain deterministic and make zero model calls.

Exact registered analysis questions compile to closed typed plans. Episode,
operational-situation, and applicability analysis may activate the Decision
Case Analysis Agent with explicit model authorization. The Agent sees only a
plan-step ID, makes at most two model calls, executes at most three distinct
steps, and has no raw advisory reader, external web access, graph-write
capability, or model-memory fallback.

Operational-situation analysis is the supported complete fixture. Episode
analysis reports only the current record and cannot group a lifecycle.
Applicability analysis can report formal facility/time applicability but
cannot infer observed individual-flight impact from aggregate BTS records.
Historical similarity returns deterministic `insufficient` until an approved
comparison corpus and profile exist; it invokes no provider and writes no
analysis artifact.

## 12. Canonical Acceptance Cases

The three cases are regression contracts, not a causal or semantic benchmark.

| Source ID | Facility and period | Declared-reason state | Active BTS-reported counts |
| --- | --- | --- | --- |
| `2026-05-19:123` | KJFK, `2026-05-19T21:00:00Z` to `2026-05-19T22:45:00Z` | Source-bound profile gap only; no formal `atm:impactingCondition`. | 20 scheduled, 18 completed, 2 cancellations, 0 diversions. |
| `2026-05-19:138` | KJFK, `2026-05-19T22:05:00Z` to `2026-05-20T02:59:00Z` | Formal `weather`; exact advisory evidence ends at `THUNDERSTORMS`. | 77 scheduled, 68 completed, 4 cancellations, 5 diversions. |
| `2026-05-20:020` | KEWR, preserved operational period | Declared reason missing; declared-reason query is `insufficient` before model construction. | 50 scheduled, 49 completed, 1 cancellation, 0 diversions. |

All three take the canonical zero-call Assembly path. Weather context remains
non-causal and cannot widen, infer, replace, or otherwise change these reason
states.

## 13. Command Interface and Breaking Cutover

The current commands are:

```text
aviation-ai agent-system ingest --source-id <source-id> --config configs/cross_source_v1.yaml [--allow-live-model]
aviation-ai agent-system neo4j-export --run-dir <run-directory>
aviation-ai agent-system ask --run-dir <run-directory> --question "<question>" [--allow-live-model]
```

Batch C.1 completed a deliberate breaking cutover. Earlier run directories
must be regenerated; the runtime has no old-run reader, writer, alias, or
artifact bridge. The familiar command names are retained as current user
experience, not as a backward-compatibility guarantee.

`--allow-live-model` authorizes only a model-bound Decision Case Analysis
route. Existing deterministic questions and the historical-similarity gate do
not construct a provider.

## 14. Verification Requirements

The active verification gate is:

```text
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

Focused three-case checks verify the exact source IDs, facilities, operational
periods, reason states, evidence wording, source provenance, non-causal
Weather boundary, active BTS-reported counts, and absence of unnecessary
provider use. A passing offline contract check does not claim external expert
certification or live semantic accuracy.

## 15. Non-Capabilities

The current system does not provide general aviation chat, causal explanation,
operational optimization, TMI recommendation, lifecycle decision-episode
grouping, observed individual-flight impact, historical similarity ranking,
full-corpus provider execution, automatic ontology expansion, public
deployment, or external expert certification.
