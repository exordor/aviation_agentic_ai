# Bounded-Agent Aviation Decision-Case Knowledge System

Status: normative current architecture with explicit final publication,
selective Agent evidence, bounded Decision Case Analysis, metadata-conditioned
historical retrieval, and one registered case-scoped graph query

Date: 2026-07-29

## 1. Purpose and Scope

This document defines the runnable system for converting a selected corpus of
retrospective FAA ATCSCC advisories and bounded authority records into
evidence-bound decision cases, validated corpus artifacts, and bounded
graph-grounded answers. It is the normative description of the current
implementation.

The system is not live ATC decision support, a complete aviation ontology, a
causal explanation engine, or a TMI recommendation system. It does not claim
that a reported observation caused a measure or that a measure was optimal.

## 2. Current Architecture

![Selective Agent escalation for decision-case construction](figures/decision_case_construction_architecture.png)

Editable source:
[decision_case_construction_architecture.drawio](figures/decision_case_construction_architecture.drawio).

![Corpus-backed retrieval and evidence-grounded answering](figures/decision_case_retrieval_architecture.png)

Editable source:
[decision_case_retrieval_architecture.drawio](figures/decision_case_retrieval_architecture.drawio).

```text
718 advisory rows + bounded FAA authority records
  -> cohort/all selection or explicit source-ID subset
  -> deterministic preflight
  -> zero-call insufficient result for unsupported/incomplete records
  -> deterministic AdvisoryParser
  -> deterministic facility and terminology authority services
     -> shared Semantic Resolution Agent only for genuine ambiguity
  -> deterministic Weather and BTS adapters
  -> sealed Decision Case Assembly task
     -> canonical zero-call compiler for the three approved cases
     -> bounded Decision Case Assembly Agent only for genuine evidence/schema choice
  -> task-bound event-patch admissibility validation
  -> source-independent DecisionCase membership finalization
  -> write-free multi-profile Formal Publication Kernel
  -> canonical corpus v2 normalization
  -> exact corpus and case-scoped formal graph runtime views
  -> metadata-conditioned Chroma case index
  -> offline rebuildable RDF/Turtle and Neo4j exports
  -> deterministic corpus query routing with bounded read-only graph tools
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
| Capability | Build, inspect, and narrowly analyze a source-bounded corpus of ATCSCC decision cases with audited context and one closed graph evidence-path query. |
| Smallest end-to-end result | Build a selected source-ID subset into corpus v2, publish only accepted facts, and retrieve its event, Weather, and active BTS membership paths. |
| Minimum components | AdvisoryParser, authority services, optional semantic/assembly Agents, Weather/BTS adapters, DecisionCase core, Formal Publication Kernel, corpus store, closed graph view, materializers, and bounded query tools. |
| Evidence | Source IDs, exact evidence text, snapshot checksums, sealed contracts, preflight records, fact traces, and deterministic tests. |
| Success | Accepted facts materialize consistently; profile gaps and missing evidence remain distinct; registered queries return `ok`, `insufficient`, or `blocked`. |
| Failure | A component invents a candidate, source, fact, cause, ontology term, or graph write; a provider is built on a deterministic path; or a result bypasses the Kernel. |
| Deferred | Causal explanation, recommendation, lifecycle episode grouping, operational-situation or outcome-aware similarity, general aviation QA, and analysis outside the exact registered families. |

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
blocked. This event-patch check is an early admissibility gate; it does not
write a projection.

## 9. Formal Publication Kernel and Profiles

After optional-layer selection and DecisionCase membership finalization, the
write-free Formal Publication Kernel validates the entire admitted case once.
It checks active profile membership, identity, source evidence, datatype,
domain/range, graph constraints, and layer-specific evidence traces. It
accepts only the formal layers owned by their profiles:

1. ATCSCC decision facts under the NASA ATMONTO decision profile;
2. METAR/TAF report facts under the curated Weather profile;
3. BTS-reported observations under the public-observation profile;
4. `DecisionCase`, `DecisionCaseReconstruction`,
   `prov:specializationOf`, and `prov:hadMember` facts under the DecisionCase
   core profile.

The DecisionCase core records source-independent system structure. Its
membership relations say that an admitted record belongs to one
reconstruction; they do not state that Weather caused the TMI or that the TMI
caused a BTS observation.

Every accepted fact carries the owning profile identifier and checksum. No
model writes directly to RDF, Turtle, Neo4j, or a final graph artifact. Normal
optional-layer `insufficient` or `blocked` outcomes are omitted before final
publication. A malformed layer that was admitted to the final set blocks the
whole case and produces no formal projection; the system does not silently
drop that layer and retry a smaller publication.

## 10. Corpus v2 Artifacts and Batch Recovery

`agent-system build-corpus` is the only persistent writer. It selects the
frozen cohort (or an explicit source-ID subset), preflights each advisory, and
runs eligible records sequentially through the existing workflow. It writes
one `CorpusBuildResult` for every selected source. The frozen intake is 718
discovered, 68 selected, 42 Agent-eligible, 23 unsupported-TMI, and 3
incomplete-core-field records. The 26 preflight outcomes are `insufficient`
with zero model calls.

The corpus manifest has version `decision-case-corpus-v2` and registers every
table and projection by path, count, and SHA-256:

```text
corpus_manifest.json
build_results.jsonl
artifacts.jsonl
source_objects/<sha256>.txt
source_bindings.jsonl
cases.jsonl
facts.jsonl
case_facts.jsonl
evidence_links.jsonl
profile_gaps.jsonl
context_associations.jsonl
observations.jsonl
kg.jsonl
kg.ttl
neo4j_nodes.jsonl
neo4j_relationships.jsonl
```

Source payloads are globally deduplicated by content checksum. `facts.jsonl`
uses semantic identity independent of provenance; `evidence_links.jsonl`
retains one-to-many support for facts, profile gaps, context associations, and
observations. Profile gaps preserve exact original evidence text outside the
formal graph. Weather associations retain `causal_claim=false`. Observations
retain phase, metric, null or numeric value, unit, admitted fact IDs, profile,
and source artifact.

Corpus v2 is the canonical persisted knowledge layer. Every `cases.jsonl`
record requires a conceptual `case_iri` and a `reconstruction_iri` extracted
from accepted DecisionCase core facts. The exact corpus and case-scoped graph
are runtime read views. RDF/Turtle and Neo4j are offline rebuildable KG
exports; Chroma is a rebuildable metadata-conditioned retrieval index. Context
associations are excluded from formal RDF and Neo4j; already admitted BTS
public-observation facts remain formal.

The successful build also publishes a research-only usage sidecar:

```text
agent_usage/
  agent_usage.jsonl
  agent_usage_manifest.json
```

Each eligible workflow case contributes facility-resolution,
terminology-resolution, and decision-case-assembly rows. They distinguish
actual activation, deterministic bypass, and a role not reached, and aggregate
outcome, provider/tool calls, tokens, and recorded latency. Preflight
insufficiencies have no usage rows. The sidecar stores no prompt, raw model
response, tool payload, result payload, or reasoning text. Its manifest binds
the records to `corpus_id`, but the sidecar is excluded from the canonical
manifest and cannot change corpus identity.

A blocked provider or workflow result does not stop the batch. It prevents
final-manifest publication and is the only state retried by
`build-corpus --resume`. Successful finalization deletes temporary case
bundles; those staging packages are never a public read backend.

## 11. QueryEvidenceBundle and Decision Case Analysis

The query surface reads only checksum-verified corpus tables through bounded
read-only tools. Registered deterministic question families cover the
measure, facility, operational period, declared reason, provenance, decision
context, public observations, and reconstruction record. Missing or
unsupported registered evidence returns `insufficient` before model
construction. These existing routes, including the combined record question,
remain deterministic and make zero model calls.

One registered multi-hop question uses the case-scoped formal graph view:

```text
Which weather reports and active-window BTS public observations belong to this reconstructed decision case?
```

The closed traversal follows the selected reconstruction through
`prov:specializationOf` and `prov:hadMember`, then reads admitted Weather and
active-window BTS observation facts. It returns formal fact and source paths
from only the selected case, makes zero model calls, and returns
`insufficient` unless both required evidence families are complete. It does
not expose arbitrary predicates, hop counts, SPARQL, Cypher, or general graph
QA.

Exact registered analysis questions compile to closed typed plans. Episode,
operational-situation, and applicability analysis may activate the Decision
Case Analysis Agent with explicit model authorization. The Agent sees only a
plan-step ID, makes at most two model calls, executes at most three distinct
steps, and has no raw advisory reader, external web access, graph-write
capability, or model-memory fallback.

Deterministic routes form their answer directly from the validated
`QueryToolOutcome`. For an exact registered analysis route, selected runtime
reads are sealed into a typed `QueryEvidenceBundle`; evidence-support
validation checks the proposed analysis against that bundle before returning
citations, limitations, and terminal status. Query-time Analysis Agent
execution remains inside the existing query evidence result; it is not written
back into the corpus build usage sidecar.

Operational-situation analysis is the supported complete fixture. Episode
analysis reports only the current record and cannot group a lifecycle.
Applicability analysis can report formal facility/time applicability but
cannot infer observed individual-flight impact from aggregate BTS records.

Historical similarity is a separate deterministic retrieval route. One compact
document per accepted case encodes TMI type, canonical facility,
declared-reason state/value, UTC time of day, and duration bucket. Exact corpus
filters run before normalized cosine recall from a persistent local Chroma
sidecar, and the reference case is always excluded. This is a
metadata-conditioned decision-record index, not operational-situation,
Weather, outcome, or effectiveness similarity. The index is derived from and
bound to `corpus_id`; changing the corpus requires rebuilding it. Results are
retrieval records only and do not enter corpus facts, RDF, Neo4j, or the Formal
Publication Kernel. The route invokes no chat provider.

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
aviation-ai agent-system build-corpus --config <config> --output-dir <corpus-dir> [--selection cohort|all] [--source-id <id> ...] --allow-live-model [--resume]
aviation-ai agent-system index-cases --corpus-dir <corpus-dir> [--model-name <model>] [--allow-model-download]
aviation-ai agent-system ask --corpus-dir <corpus-dir> --question "<question>" [--event-id <event-id>] [--allow-live-model]
aviation-ai agent-system neo4j-export --corpus-dir <corpus-dir>
aviation-ai agent-system export-case --corpus-dir <corpus-dir> --event-id <event-id> --output-dir <export-dir>
```

This is a deliberate storage cutover. There is no public `ingest` command,
`ask-corpus` alias, `--runs-root` importer, `--run-dir` query/export path, or
v1 corpus migration layer. `build-corpus --source-id` is the bounded
single-case debug route. Corpus queries, projections, Neo4j loads, and case
exports all use the checksum-verified v2 tables.

`--allow-live-model` authorizes the existing bounded workflow for eligible
build records and a model-bound Decision Case Analysis route. Preflight,
existing deterministic questions, and historical similarity do not construct
a chat provider. Historical similarity accepts exact event-type, facility, and
declared-reason filters plus `archive` or `prior` candidate scope.

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

The tracked six-query retrieval smoke set over 38 accepted cases checks four
reviewed analogue pairs and two expected-insufficient filters. Its observed
Hit@1, Hit@3, and MRR are all `1.0`, with two of two expected-insufficient
queries passing. This is a bounded relevance smoke test, not expert Gold,
decision-quality evidence, or an operational recommendation benchmark.

## 15. Non-Capabilities

The current system does not provide general aviation chat, causal explanation,
operational optimization, TMI recommendation, lifecycle decision-episode
grouping, observed individual-flight impact, operational-situation or
outcome-aware similarity, learned reranking, automatic ontology expansion,
public deployment, or external expert certification.
