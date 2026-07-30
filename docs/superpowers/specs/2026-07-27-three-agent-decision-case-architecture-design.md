# Three-Agent Decision Case Architecture Design

Status: historical design; query role superseded on 2026-07-30

> This document preserves the earlier fixed Analysis path for design history.
> The active runtime is defined by `docs/multi_agent_kg_system_design.md` and
> replaces that path with one always-on HybridRAG Query Agent.

Date: 2026-07-27

Branch: `codex/decision-case-assembly-agent`

Normative parent design:
`docs/multi_agent_kg_system_design.md`

## 1. Decision

The current system uses the word Agent only for a component that makes a
bounded choice from typed, sealed state and receives typed feedback. The three
defined Agent roles are:

1. Semantic Resolution Agent;
2. Decision Case Assembly Agent;
3. Decision Case Analysis Agent.

The first two are implemented conditionally. Decision Case Analysis is
inactive. Deterministic source adapters, parsing, authority lookup, unique
resolution, context preparation, validation, materialization, and routing are
services or tools, not Agents.

Batch C.1 completed the replacement of the older public role narrative with
this architecture. It is a breaking runtime and artifact cutover: old runs
must be regenerated. `ingest`, `neo4j-export`, and `ask` retain useful current
names as user experience, not as a backward-compatibility guarantee.

## 2. Current Topology

```text
ATCSCC advisory + bounded FAA authority records
  -> deterministic AdvisoryParser
  -> deterministic facility and terminology authority services
     -> shared Semantic Resolution Agent only for genuine ambiguity
  -> deterministic Weather and BTS adapters
  -> sealed Decision Case Assembly task
     -> canonical zero-call compiler for 123 / 138 / 020
     -> Decision Case Assembly Agent only for genuine evidence/schema choice
  -> exact preflight
  -> Formal Graph Kernel
  -> profile-owned JSONL, RDF, and Neo4j run artifacts
  -> bounded Query Agent
```

The coordinator is deterministic and is not a fourth Agent. The Formal Graph
Kernel is deterministic and is the sole final publication authority. The
ontology profiles are contracts, not Agent roles.

## 3. Stage Contract

| Item | Decision |
| --- | --- |
| Capability advanced | Evidence-bounded ambiguity resolution and decision-case assembly without inflating deterministic services into Agents. |
| Smallest end-to-end result | One advisory becomes a validated case whose registered question is answered from current run artifacts. |
| Required components | AdvisoryParser, authority services, the two conditional Agents, Weather/BTS adapters, Formal Graph Kernel, profiles, materializers, and Query Agent. |
| Evidence | Sealed tasks and proposals, source IDs and evidence, profile checksums, preflight result, fact trace, and focused acceptance tests. |
| Success | Conditional Agents activate only for their genuine decision; deterministic paths remain zero-call; only Kernel-accepted facts publish. |
| Failure | An Agent invents a source, candidate, ontology term, fact, cause, or graph write; a deterministic path builds a provider; or a result bypasses preflight or the Kernel. |
| Deferred | Decision Case Analysis, causal explanation, recommendation, lifecycle grouping, ranking, general planning, long-term memory, and specialist source Agents. |

## 4. Deterministic Components

The following remain deterministic services or tools:

- `AdvisoryParser` and structured-field parsing;
- source loaders and source-snapshot/checksum validation;
- facility and terminology candidate generation and unique acceptance;
- canonical identity construction;
- Weather/TAF/METAR temporal eligibility and BTS aggregation;
- profile loading, schema checks, exact contract preflight, and Formal Graph
  Kernel validation;
- JSONL, RDF/Turtle, and Neo4j projection materialization;
- audit manifest and trace writing;
- registered deterministic Query Agent routing.

Facility and terminology authority sources remain separate. A unique authority
result is accepted deterministically. A lack of eligible evidence remains
`insufficient`; a source or contract failure remains `blocked`; a
source-supported value outside an active profile remains a `profile_gap`.

## 5. Semantic Resolution Agent

### 5.1 Activation and State

The shared Semantic Resolution Agent activates only for multiple eligible
facility or terminology candidates. It receives a sealed `ResolutionTask`:

```text
mention
structural_slot
expected_entity_type
candidate IDs and eligibility audits
authority evidence and source IDs
ontology constraints
remaining tool and provider budget
```

It may select an eligible candidate or abstain. It cannot invent candidates,
canonical IDs, sources, authority definitions, ontology classes, or
properties.

### 5.2 Tool and Budget Boundary

The Agent may use one read-only, candidate-bounded batch selected from:

```text
get_resolution_candidates
get_authority_record
get_ontology_context
check_candidate_constraints
compare_candidate_evidence
```

The batch is capped at three tools and the Agent is capped at two provider
calls. Blocked, insufficient, zero-candidate, and unique-candidate cases do
not construct a model. Malformed, out-of-scope, or indistinguishable output
terminates with a sealed abstained or blocked proposal.

### 5.3 Output

The runtime records a sealed `ResolutionProposal` that binds the selected or
abstained candidate, rejected candidates, source support, tool traces,
limitation, run identity, and task checksum. The surrounding authority service
retains the source records and audit records; it does not publish event facts.

## 6. Decision Case Assembly Agent

### 6.1 Activation and State

Deterministic parsing, authority resolution, Weather/BTS preparation, and
profile validation seal a `CaseAssemblyTask`. It binds the core event facts,
profile gaps, resolution proposals, context associations, public observations,
component states, source snapshots, evidence, and compact schema context.

Ground Stop `2026-05-19:123`, GDP `2026-05-19:138`, and GDP cancellation
`2026-05-20:020` use the canonical compiler. They do not construct or call an
Assembly provider.

Only a non-canonical record with both a dedicated Assembly factory and a
genuine evidence/schema choice can activate the Assembly Agent. It receives no
graph-write capability and no unrestricted raw-source access.

### 6.2 Boundary and Publication

The activated Agent can request a bounded batch of task-owned read-only
evidence and schema tools, then emit a `CaseAssemblyProposal`. Exact preflight
requires the proposal to preserve the sealed fact, gap, evidence, resolution,
context, component, and source-binding sets.

The only permitted repair is the contract-defined value-only correction. A
causal, out-of-task, out-of-schema, profile, source, or evidence violation is
blocked. The Formal Graph Kernel alone accepts facts for publication.

## 7. Decision Case Analysis Agent

Decision Case Analysis remains inactive. It has no active prompt, model path,
tool surface, source expansion, planner, memory, recommendation, or causal
claim. It may be reconsidered only through a separately approved bounded
question family and implementation plan.

## 8. Shared Evidence and Publication Rules

All roles and deterministic services preserve source family, source ID,
evidence text, snapshot checksum, profile ownership, and the appropriate
sealed contract or trace. The formal graph has three independent validated
layers:

1. ATCSCC decision facts under the NASA ATMONTO decision profile;
2. METAR/TAF report facts under the Weather profile;
3. BTS-reported public observations under the public-observation profile.

Profile gaps remain audit records outside RDF and Neo4j. Weather associations
are audit-only and non-causal. BTS observations are not FAA demand, AAR,
capacity, EDCT, ASPM data, or evidence that a TMI caused an outcome.

## 9. Query Agent

The bounded Query Agent reads validated current-run artifacts through
read-only graph tools. Registered scalar and context questions take
deterministic paths. Missing or unsupported registered evidence returns
`insufficient` before model construction. A registered compound question may
use the bounded model-tool-model path, but it has no raw advisory reader,
external web access, graph-write tool, or model-memory fallback.

## 10. Canonical Cases

| Case | Preserved contract |
| --- | --- |
| Ground Stop 123 / KJFK | Period `21:00Z-22:45Z`; reason only as a source-bound profile gap; no formal `atm:impactingCondition`; active BTS-reported counts `(20, 18, 2, 0)`. |
| GDP 138 / KJFK | Period `2026-05-19T22:05:00Z-2026-05-20T02:59:00Z`; formal `weather`; evidence ends at `THUNDERSTORMS`; active counts `(77, 68, 4, 5)`. |
| GDP cancellation 020 / KEWR | Operational period retained; declared reason missing; reason answer `insufficient` before model construction; active counts `(50, 49, 1, 0)`. |

Weather context must not change a reason state. The canonical compiler and
registered deterministic queries make no unnecessary provider call for these
records.

## 11. Current Run and Cutover Rules

Current run artifacts are profile-owned and include `kg.jsonl`, `kg.ttl`,
`neo4j_nodes.jsonl`, `neo4j_relationships.jsonl`, `run_manifest.json`,
`source_snapshots.jsonl`, profile-gap records, context artifacts, and fact or
reconstruction traces. RDF and Neo4j are projections of Kernel-accepted facts,
not competing authorities.

Batch C.1 supersedes the former deferred public-naming and compatibility gate.
There is no old-run reader, writer, wrapper, alias, prompt, or artifact bridge
in the active Agent-system surface. The retained CLI names are deliberately
current UX only.

## 12. Verification

The architecture is accepted only with focused three-case regression checks,
the active-surface scan, full Ruff, full pytest, package build, and diff
whitespace check. Offline tests demonstrate contract behavior; they do not
claim live semantic accuracy or external expert certification.
