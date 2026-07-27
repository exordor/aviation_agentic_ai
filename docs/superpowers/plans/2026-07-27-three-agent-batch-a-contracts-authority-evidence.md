# Three-Agent Batch A Contracts and Authority Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status:** Implemented locally through Task 6. Three-Agent runtime migration
has not started; the current workflow remains the compatibility runtime.

**Goal:** Establish the strict three-Agent collaboration contracts and give the existing facility and terminology compatibility paths source-bound structural and authority evidence, without activating the three-Agent runtime.

**Architecture:** Batch A is an additive compatibility layer. New immutable, checksummed Resolution, Assembly, and Analysis contracts live beside the existing `AgentTask`, `AgentResult`, `GraphPatchBlock`, and `QueryToolOutcome` contracts. Deterministic parser and authority services construct candidate evidence from known advisory slots, typed authority registries, real FAA definitions, checksum-pinned source snapshots, and the active Schema Guide. Existing role functions remain temporary wrappers and the current workflow topology, CLI, Formal Graph Kernel, graph projections, and persisted artifact names remain unchanged.

**Tech Stack:** Python 3.10+, Pydantic 2, LangGraph compatibility workflow, PyYAML, JSONL, rdflib, pytest

## Global Constraints

- Work only on `codex/decision-case-semantic-expansion-design`.
- Use English for code, contracts, prompts, tests, artifacts, CLI messages, and active documentation.
- Follow strict RED-GREEN-REFACTOR for every new behavior. Observe the focused failure before changing production code.
- Commit each completed task separately. Do not merge or push.
- Do not activate, rename, or add workflow Agent nodes in Batch A.
- Keep the current runtime topology:

```text
advisory
  -> facility + terminology
  -> join
  -> knowledge_graph_construction
  -> materialize
  -> decision_context
```

- Keep the public call signatures of `run_advisory_agent`, `run_facility_agent`, `run_terminology_agent`, `run_kg_construction_agent`, and `run_query_agent`.
- Keep the current `AgentStatus`, `EvidenceCard`, `AgentTask`, `AgentResult`, `GraphPatchBlock`, `QueryToolOutcome`, CLI commands, command options, exit behavior, and current artifact filenames readable.
- Put new frozen contracts in a separate module. Do not make the existing `StrictModel` globally frozen.
- Do not add a new run artifact or manifest key. Authority records referenced by a compatibility resolution task may be added to the existing `source_snapshots.jsonl` registry for replay, but they remain resolution-audit sources rather than formal event-fact sources.
- Do not expose the future three Agent names through the active workflow, CLI, prompt-role registry, manifests, or reader-facing system claims.
- Do not add a resolution-provider call. Existing deterministic unique-candidate
  paths remain zero-model; missing, corrupt, and genuinely ambiguous candidate
  sets all terminate before resolution-provider construction in Batch A. The
  existing Knowledge Graph Construction tool-model budget remains unchanged.
- Preserve `configs/prompts/agent_system_v1.yaml`,
  `configs/cross_source_v1.yaml`, and
  `data/sources/faa_atcscc_terms_v1.yaml` byte-for-byte. Batch A does not
  activate a prompt v2 or repoint a v1 source identity. These v1 artifacts
  remain readable and byte-identical; the active facility/terminology runtime
  intentionally migrates to deterministic authority-bound wrappers, so Batch A
  does not claim behavioral replay of the former ambiguous-provider path.
- Do not use a preferred label, canonical ID, model memory, or a generic sentence as an authority definition or authority source.
- Do not use an abbreviation-only schema lookup to overwrite a candidate's `denotes_schema_term`.
- Do not create a formal KG fact from authority candidate evidence in this batch. Authority evidence supports resolution; the Formal Graph Kernel remains the only publication gate for event facts.
- Keep the graph-write allowlist narrower than the source snapshot registry: only source IDs carried by accepted event `EvidenceClaim` rows may support a Graph Patch line. NASR and PCG authority sources recorded for resolution must never enter that allowlist merely because they are registered.
- Preserve all three decision-record regressions:
  - Ground Stop `2026-05-19:123`: KJFK, reason remains a profile gap, and no formal `atm:impactingCondition`;
  - GDP `2026-05-19:138`: KJFK, cross-midnight period remains correct, reason remains formal `weather`, and evidence ends at `THUNDERSTORMS`;
  - GDP cancellation `2026-05-20:020`: KEWR, operational period remains present, and declared reason remains absent.
- Keep Weather context non-causal and BTS observations source-qualified. Batch A must not alter Weather, public-observation, lifecycle, applicability, similarity, recommendation, or visualization semantics.
- Make no real provider call. Live Semantic Resolution, Assembly, and Analysis smoke tests belong to Batches B, C, and D.

---

## Task 1: Freeze the Existing Compatibility Surface

**Files:**

- Create: `tests/test_agent_system_architecture_compatibility.py`
- Read only: `src/aviation_agentic_ai/agent_system/agents.py`
- Read only: `src/aviation_agentic_ai/agent_system/contracts.py`
- Read only: `src/aviation_agentic_ai/agent_system/workflow.py`
- Read only: `src/aviation_agentic_ai/agent_system/runtime.py`
- Read only: `src/aviation_agentic_ai/cli_agent_system.py`
- Read only: `configs/prompts/agent_system_v1.yaml`

### Compatibility assertions

The characterization suite freezes:

```python
LEGACY_AGENT_STATUS_VALUES = {
    "resolved",
    "abstain",
    "profile_gap",
    "blocked",
}

LEGACY_INGEST_NODES = {
    "advisory",
    "facility",
    "terminology",
    "join",
    "kg_construction",
    "materialize",
    "decision_context",
}

LEGACY_CLI_COMMANDS = {
    "ingest",
    "neo4j-export",
    "ask",
}
```

The suite also captures:

- exact parameter names and defaults for the five public `run_*_agent`
  functions named in Global Constraints;
- representative `EvidenceCard`, `AgentTask`, `AgentResult`, `GraphPatchBlock`, and `QueryToolOutcome` JSON keys;
- existing `run_manifest.json` top-level keys;
- current run artifact filenames;
- the current five-role catalog remaining loadable from `agent_system_v1.yaml`;
- the existing unique facility and unique term paths make zero provider calls;
- no three-Agent runtime role in workflow state, CLI output, or persisted legacy envelopes.

### Steps

- [ ] Write characterization tests using `inspect.signature`, representative Pydantic serialization, Click's test runner, and a compiled workflow.
- [ ] Run:

```bash
uv run pytest -q tests/test_agent_system_architecture_compatibility.py
```

Expected: PASS against the current branch. This task establishes the migration boundary rather than a new red behavior.

- [ ] Run:

```bash
uv run aviation-ai agent-system --help
uv run aviation-ai agent-system ingest --help
uv run aviation-ai agent-system neo4j-export --help
uv run aviation-ai agent-system ask --help
git diff --check
```

- [ ] Commit:

```bash
git add tests/test_agent_system_architecture_compatibility.py
git commit -m "test(agent-system): freeze Batch A compatibility surface"
```

---

## Task 2: Add Strict Three-Agent Migration Contract Families

**Files:**

- Create: `src/aviation_agentic_ai/agent_system/decision_case_contracts.py`
- Create: `tests/test_agent_system_decision_case_contracts.py`
- Modify: `src/aviation_agentic_ai/agent_system/graph_patch.py`

During Task 2, do not import these dormant contracts from `workflow.py`,
`cli_agent_system.py`, active prompt-role registration, or persisted artifact
readers. Task 5 may import only the Resolution compatibility contracts into the
existing facility/terminology wrappers and workflow state; Assembly and
Analysis contracts remain dormant throughout Batch A.

### Integrity primitives

```python
DECISION_CASE_CONTRACT_VERSION = "decision-case-agent-contracts-v1"
Sha256Hex = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class FrozenContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class ChecksummedContract(FrozenContractModel):
    contract_version: Literal[
        "decision-case-agent-contracts-v1"
    ] = DECISION_CASE_CONTRACT_VERSION
    payload_checksum: Sha256Hex
    created_at: AwareDatetime
    prompt_version: str | None = None
    tool_version: str | None = None


class ContractExecutionBinding(FrozenContractModel):
    run_id: str
    created_at: AwareDatetime
    prompt_version: str | None = None
    tool_version: str | None = None


def canonicalize_contract_value(value: Any) -> Any:
    """Convert one strict contract value into a canonical JSON primitive."""


def canonical_payload_bytes(
    model_type: type[BaseModel],
    fields: BaseModel,
    binding: ContractExecutionBinding,
) -> bytes:
    """Validate and encode checksum-covered fields except payload_checksum."""


def stable_contract_id(namespace: str, *canonical_inputs: str) -> str:
    """Build one length-prefixed, delimiter-safe stable ID."""


def canonical_id_tuple_token(
    values: Sequence[str],
    *,
    sort_values: bool,
) -> str:
    """Encode one duplicate-free ID sequence as a compact JSON array."""


def seal_resolution_task(
    *,
    fields: ResolutionTaskFields,
    binding: ContractExecutionBinding,
) -> ResolutionTask: ...


def seal_resolution_proposal(
    *,
    task: ResolutionTask,
    fields: ResolutionProposalFields,
    binding: ContractExecutionBinding,
) -> ResolutionProposal: ...


def seal_case_assembly_task(
    *,
    fields: CaseAssemblyTaskFields,
    binding: ContractExecutionBinding,
) -> CaseAssemblyTask: ...


def seal_case_assembly_proposal(
    *,
    task: CaseAssemblyTask,
    fields: CaseAssemblyProposalFields,
    binding: ContractExecutionBinding,
) -> CaseAssemblyProposal: ...


def seal_case_analysis_task(
    *,
    fields: CaseAnalysisTaskFields,
    binding: ContractExecutionBinding,
) -> CaseAnalysisTask: ...


def seal_query_evidence_bundle(
    *,
    task: CaseAnalysisTask,
    fields: QueryEvidenceBundleFields,
    binding: ContractExecutionBinding,
) -> QueryEvidenceBundle: ...


def seal_validation_feedback(
    *,
    task: CaseAssemblyTask,
    proposal: CaseAssemblyProposal,
    fields: ValidationFeedbackFields,
    binding: ContractExecutionBinding,
) -> ValidationFeedback: ...
```

Each `*Fields` model is a frozen, `extra="forbid"` model containing exactly
the corresponding contract fields shown below except
`contract_version`, `payload_checksum`, `created_at`, `prompt_version`, and
`tool_version`. A public builder accepts one of these typed field bundles; no
public builder accepts `**kwargs`, an untyped mapping, or omitted execution
metadata.

Canonicalization is exact:

- `BaseModel` values use `model_dump(mode="python",
  exclude={"payload_checksum"}, exclude_computed_fields=False)`;
- `Enum` values become `.value`;
- aware datetimes are converted to UTC and encoded with microseconds and a
  literal `Z`, for example `2026-05-19T20:15:00.000000Z`;
- naive datetimes, floats containing NaN/Infinity, bytes, sets, and unknown
  objects are rejected;
- tuples and lists retain their validated order;
- mapping keys must be strings and are sorted by the JSON encoder;
- UTF-8 canonical JSON uses:

```python
json.dumps(
    canonicalized_payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
).encode("utf-8")
```

The checksum is SHA-256 over those exact bytes after the final strict contract
payload has been assembled with `payload_checksum` omitted. The sealed model
is reconstructed with the checksum and must reproduce the same bytes.
`created_at` is copied from the run's frozen `run_started_at`; builders never
call `datetime.now()`. At least one of `prompt_version` and `tool_version` is
required. Batch A Resolution tasks and deterministic proposals bind only
`tool_version`; later model-mediated proposals must bind both.

`ContractExecutionBinding` accepts an aware timestamp and normalizes it to UTC;
the sealed contract validator itself rejects a naive or non-UTC `created_at`.
Every builder also requires `binding.run_id == fields.run_id`; proposal
builders additionally require the binding, task, and proposal field bundle to
share the same run ID.

The checksum function does not reorder arbitrary tuples. Trusted builders sort
and deduplicate only set-like ID collections such as candidate IDs, source IDs,
evidence IDs, and rejected IDs. Ordered semantic sequences such as
`executed_step_ids`, `tool_trace_ids`, `answer_statements`, validation feedback,
and component rows preserve runtime order and reject duplicates without
sorting.

Every list-like input shown in an ID recipe is first encoded by
`canonical_id_tuple_token`: set-like collections use `sort_values=True`,
ordered collections use `False`, and both become compact JSON arrays with
`ensure_ascii=False`. `stable_contract_id` accepts strings only and hashes the
namespace plus each UTF-8 input as an unsigned eight-byte big-endian length
followed by the bytes. It returns
`f"{namespace}:{sha256(framed_bytes).hexdigest()}"`. Thus collections are never
flattened or joined with an ambiguous delimiter, and expected IDs are portable.

Stable IDs have these exact inputs:

```text
authority source ID =
  stable_contract_id("authority-source", authority kind, candidate ID,
                     authority source ref, normalized source-record checksum)

authority evidence-claim ID =
  stable_contract_id("authority-evidence", candidate ID, authority source ID,
                     source snapshot checksum, authority artifact checksum)

constraint ID =
  stable_contract_id("resolution-constraint", candidate ID, check kind,
                     structural slot, expected type, schema snapshot checksum)

resolution task ID =
  stable_contract_id("resolution-task", run ID, event ID, mention,
                     structural slot, expected type,
                     sorted candidate-audit IDs,
                     schema slice ID, schema snapshot checksum)

resolution proposal ID =
  stable_contract_id("resolution-proposal", resolution task ID, decision,
                     selected candidate ID or NONE, sorted rejected IDs,
                     sorted supporting evidence-claim IDs)

case-assembly task ID =
  stable_contract_id("case-assembly-task", run ID, case ID,
                     sorted core event fact IDs,
                     sorted resolution proposal IDs,
                     sorted selected evidence-claim IDs,
                     schema profile ID, schema context ID,
                     schema snapshot checksum)

case-assembly proposal ID =
  stable_contract_id("case-assembly-proposal", case-assembly task ID,
                     task payload checksum, assembly status,
                     sorted proposed-fact item IDs,
                     sorted profile-gap item IDs,
                     sorted resolution proposal IDs)

validation feedback ID =
  stable_contract_id("validation-feedback", case-assembly task ID,
                     proposal payload checksum, affected proposal item ID,
                     violation code, constraint ID,
                     ordered allowed-correction IDs,
                     sorted evidence IDs)

case-analysis task ID =
  stable_contract_id("case-analysis-task", run ID, query-plan ID,
                     ordered event/case scope IDs,
                     sorted requested evidence layers,
                     answer-contract ID)

query evidence-bundle ID =
  stable_contract_id("query-evidence-bundle", case-analysis task ID,
                     task payload checksum, answer status,
                     ordered executed step IDs,
                     sorted retrieved fact/derivation/profile-gap/source IDs,
                     answer-contract ID)
```

Contract validation rejects an unsorted set-like tuple, duplicate ID, extra
field, non-UTC timestamp, missing execution binding, wrong version, malformed
checksum, or checksum that does not match the validated payload. The typed
`*Fields` models and task-specific builders are the only public sealing
surface. Proposal builders receive the already sealed task and enforce
cross-object invariants before sealing. `seal_validation_feedback` additionally
receives the sealed assembly proposal being reviewed and proves common
run/task/case ownership, exact `proposal_payload_checksum`, and ownership of
the affected proposal item before sealing feedback for a later bounded
revision.

`task_id` is the stable logical task identity. Because working-state snapshots
are frozen, task registries key an exact state as
`(task_id, payload_checksum)`. A proposal always carries both values, so a
later task state with different rejected candidates, retrieved evidence, or
validation feedback cannot be substituted under the same logical ID.

### Resolution contracts

```python
class ResolutionDecision(str, Enum):
    ACCEPTED = "accepted"
    ABSTAINED = "abstained"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


class ConstraintCheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


class CandidateBuildStatus(str, Enum):
    OK = "ok"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


class AuthorityEvidenceKind(str, Enum):
    FACILITY_RECORD = "facility_record"
    TERM_DEFINITION = "term_definition"


class AuthorityRecordEvidenceClaim(FrozenContractModel):
    evidence_id: str
    candidate_id: str
    evidence_kind: Literal["facility_record"]
    authority_record_text: str
    authority_record_locator: str
    authority_record_sha256: Sha256Hex
    authority_source_ref: str
    source_id: str
    source_snapshot_sha256: Sha256Hex
    authority_artifact_key: Literal["nasr_zip"]
    authority_artifact_sha256: Sha256Hex
    manifest_artifact_key: Literal["nasr_manifest"]
    manifest_artifact_sha256: Sha256Hex


class AuthorityDefinitionEvidenceClaim(FrozenContractModel):
    evidence_id: str
    candidate_id: str
    evidence_kind: Literal["term_definition"]
    definition_text: str
    definition_locator: str
    authority_source_ref: str
    source_id: str
    source_snapshot_sha256: Sha256Hex
    authority_artifact_key: Literal["pilot_controller_glossary"]
    authority_artifact_sha256: Sha256Hex
    definition_registry_artifact_key: Literal["authority_definition_seed"]
    definition_registry_artifact_sha256: Sha256Hex
    term_registry_artifact_key: Literal["term_seed"]
    term_registry_artifact_sha256: Sha256Hex


class SourceSnapshotBinding(FrozenContractModel):
    source_id: str
    source_family: SourceFamily
    source_snapshot_sha256: Sha256Hex


class ConstraintCheck(FrozenContractModel):
    constraint_id: str
    candidate_id: str
    check_kind: Literal[
        "structural_slot",
        "expected_entity_type",
        "schema_compatibility",
    ]
    status: ConstraintCheckStatus
    reason_code: str
    evidence_ids: tuple[str, ...] = ()
    schema_snapshot_sha256: Sha256Hex | None = None


class ResolutionCandidate(FrozenContractModel):
    candidate_id: str
    candidate_kind: Literal["facility", "term"]
    preferred_label: str
    surface_form: str
    candidate_type: str
    ontology_class_prefixed: str | None
    ontology_class_iri: str | None
    authority_evidence_ids: tuple[str, ...]
    constraint_checks: tuple[ConstraintCheck, ...]

    @computed_field
    @property
    def eligible(self) -> bool:
        ...


class RawResolutionCandidateRef(FrozenContractModel):
    candidate_id: str
    candidate_kind: Literal["facility", "term"]


class ResolutionCandidateAudit(FrozenContractModel):
    candidate_audit_id: str
    candidate_id: str
    candidate_kind: Literal["facility", "term"]
    build_status: CandidateBuildStatus
    candidate_payload_checksum: Sha256Hex | None = None
    evidence_id: str | None = None
    source_id: str | None = None
    reason_code: str | None = None
    error_id: str | None = None


class ResolutionTask(ChecksummedContract):
    task_id: str
    run_id: str
    event_id: str
    mention: str
    structural_slot: str
    expected_entity_type: str
    authority_domain_status: CandidateBuildStatus
    authority_domain_reason_code: str | None = None
    authority_domain_error_id: str | None = None
    raw_candidate_refs: tuple[RawResolutionCandidateRef, ...]
    candidates: tuple[ResolutionCandidate, ...]
    candidate_audits: tuple[ResolutionCandidateAudit, ...]
    authority_evidence: tuple[
        AuthorityRecordEvidenceClaim | AuthorityDefinitionEvidenceClaim,
        ...,
    ]
    authority_source_ids: tuple[str, ...]
    ontology_constraints: tuple[str, ...]
    schema_slice_id: str
    schema_snapshot_sha256: Sha256Hex
    rejected_candidate_ids: tuple[str, ...] = ()
    remaining_tool_budget: int = Field(ge=0, le=3)
    decision: ResolutionDecision | None = None


class ResolutionProposal(ChecksummedContract):
    resolution_proposal_id: str
    run_id: str
    task_id: str
    task_payload_checksum: Sha256Hex
    event_id: str
    mention: str
    structural_slot: str
    expected_entity_type: str
    selected_candidate_id: str | None
    rejected_candidate_ids: tuple[str, ...]
    decision: ResolutionDecision
    supporting_evidence_claim_ids: tuple[str, ...]
    authority_source_ids: tuple[str, ...]
    tool_trace_ids: tuple[str, ...]
    limitation: str | None


class ResolutionDomainOutcome(FrozenContractModel):
    domain: Literal["facility", "terminology"]
    required_for_case: bool
    decision: ResolutionDecision
    task_id: str
    task_payload_checksum: Sha256Hex
    resolution_proposal_id: str
    limitation_code: str | None = None
    error_id: str | None = None
```

Within Resolution contracts, `event_id` means the nonempty
`resolution_event_id` defined in Task 5. It is an execution/semantic-resolution
binding, not permission to publish a formal event URI.

`AuthorityRecordEvidenceClaim` and `AuthorityDefinitionEvidenceClaim` are the
typed rows in the dormant `EvidenceClaimRegistry`. Their `evidence_id` values
are therefore the IDs referenced by
`ResolutionProposal.supporting_evidence_claim_ids`; no conversion from a
different authority-evidence namespace is permitted.

`ResolutionCandidate` validates that:

- there is exactly one `structural_slot` check and exactly one
  `expected_entity_type` check;
- `ontology_class_prefixed` and `ontology_class_iri` are either both present or
  both absent;
- every candidate has exactly one `schema_compatibility` check; an unmapped
  candidate carries an explicit `fail` or `unknown` schema check rather than
  omitting the check;
- `eligible` is true only when both ontology mapping fields are present, every
  required check is `pass`, every required authority-claim ID is present, and
  schema binding is valid;
- `eligible` is computed, never trusted from provider or caller input.

`ResolutionCandidateAudit` is the checksum-sealed terminal row for every raw
mention-matched candidate:

```text
ok           -> candidate checksum + evidence ID + source ID; no reason/error
insufficient -> candidate checksum; no evidence/source; reason only
blocked      -> no candidate checksum/evidence/source; reason + stable error ID
```

Candidate payload checksums use canonical JSON over
`ResolutionCandidate.model_dump(mode="python",
exclude_computed_fields=True)`, passed through the same
`canonicalize_contract_value` and UTF-8 encoder defined above. Audit IDs are:

```text
stable_contract_id("resolution-candidate-audit", candidate ID, candidate kind,
                   build status, candidate payload checksum or NONE,
                   evidence ID or NONE, source ID or NONE,
                   reason code or NONE, error ID or NONE)
```

The `ResolutionTask` cross-validator proves that:

- domain `blocked` requires a stable reason/error and may contain no candidate
  rows when the source failed before enumeration;
- domain `insufficient` requires a reason, forbids an error, and distinguishes
  a legitimate empty catalog from a blocked unreadable catalog;
- audit rows exactly match the raw mention-matched candidate ID/kind set;
- `raw_candidate_refs` are sorted by `(candidate_kind, candidate_id)`, contain
  no duplicates, and provide the persisted expected set against which omission
  is checked;
- `candidates` correspond exactly to the `ok` and `insufficient` audit rows;
- each audit checksum equals the canonical `ResolutionCandidate` payload;
- every referenced evidence ID occurs exactly once, belongs to the same
  candidate, and agrees with the audit row's source ID;
- `authority_source_ids` equals the sorted unique source-ID projection of
  `authority_evidence`, with neither omission nor unrelated in-task source;
- blocked candidate IDs remain reconstructible from their audit rows without
  admitting unvalidated candidate content;
- every schema-check checksum equals
  `ResolutionTask.schema_snapshot_sha256`.

The exact-set assertion applies to the raw set the domain successfully
enumerated. A pre-enumeration domain `blocked` task seals an empty audit tuple
plus its domain reason/error; it must never be represented as an ordinary empty
candidate set.

`ResolutionProposal` enforces:

- `accepted` has exactly one selected candidate and nonempty authority support;
- all other decisions have no selected candidate;
- `abstained` has at least two eligible candidates in its bound task;
- `insufficient` represents no eligible candidate or missing required evidence;
- `blocked` carries a corruption limitation;
- the trusted builder verifies the selected and rejected IDs against the bound `ResolutionTask`.
- every non-selected audit row is represented in `rejected_candidate_ids`;
- every supporting evidence-claim ID and authority source ID is a subset of
  the bound task registries;
- proposal `authority_source_ids` equals the sorted unique source-ID projection
  of exactly its `supporting_evidence_claim_ids`, not an arbitrary task subset;
- a foreign claim, duplicate check, failed check with a selected candidate,
  or mismatched schema checksum fails contract validation.

### Assembly contracts

```python
class AssemblyStatus(str, Enum):
    OK = "ok"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


class ComponentLayerStatus(str, Enum):
    OK = "ok"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


class FactDisposition(str, Enum):
    FORMAL_FACT = "formal_fact"
    PROFILE_GAP = "profile_gap"
    REJECTED = "rejected"


class ComponentLayerResult(FrozenContractModel):
    layer_id: str
    status: ComponentLayerStatus
    required_for_task: bool
    artifact_ids: tuple[str, ...] = ()
    missing_reason_code: str | None = None
    blocking_error_id: str | None = None


class CaseFactProposal(FrozenContractModel):
    proposal_item_id: str
    subject_id: str
    predicate_iri: str
    object_kind: Literal["iri", "literal"]
    object_value: str
    evidence_claim_ids: tuple[str, ...] = ()
    derivation_ids: tuple[str, ...] = ()
    validation_profile_id: Annotated[str, Field(min_length=1)]

    @model_validator(mode="after")
    def require_support(self) -> Self:
        ...


class CaseProfileGapProposal(FrozenContractModel):
    proposal_item_id: str
    event_id: str
    field: str
    normalized_value: str
    evidence_claim_ids: Annotated[tuple[str, ...], Field(min_length=1)]
    schema_mapping_reason_code: str
    validation_profile_id: Annotated[str, Field(min_length=1)]


class FactAssessment(FrozenContractModel):
    assessment_id: str
    proposal_item_id: str
    disposition: FactDisposition
    published_fact_id: str | None = None
    profile_gap_id: str | None = None
    rejection_id: str | None = None
    support_ids: tuple[str, ...] = ()


class ValidationFeedback(ChecksummedContract):
    feedback_id: str
    run_id: str
    task_id: str
    case_id: str
    proposal_payload_checksum: Sha256Hex
    violation_code: str
    constraint_id: str
    affected_proposal_item_id: str
    repairable: bool
    allowed_corrections: tuple[str, ...]
    evidence_ids: tuple[str, ...]


class CaseAssemblyTask(ChecksummedContract):
    task_id: str
    run_id: str
    case_id: str
    core_event_fact_ids: tuple[str, ...]
    resolution_proposal_ids: tuple[str, ...]
    available_evidence_layer_ids: tuple[str, ...]
    required_case_slots: tuple[str, ...]
    optional_case_slots: tuple[str, ...]
    missing_slots: tuple[str, ...]
    schema_profile_id: str
    schema_context_id: str
    schema_snapshot_sha256: Sha256Hex
    selected_evidence_claim_ids: tuple[str, ...]
    proposed_facts: tuple[CaseFactProposal, ...]
    profile_gaps: tuple[CaseProfileGapProposal, ...]
    context_association_ids: tuple[str, ...]
    public_observation_ids: tuple[str, ...]
    omitted_slots: tuple[str, ...]
    validation_feedback: tuple[ValidationFeedback, ...]
    source_snapshot_bindings: tuple[SourceSnapshotBinding, ...]
    remaining_tool_budget: int = Field(ge=0, le=6)


class CaseAssemblyProposal(ChecksummedContract):
    case_assembly_proposal_id: str
    run_id: str
    task_id: str
    task_payload_checksum: Sha256Hex
    case_id: str
    assembly_status: AssemblyStatus
    component_layer_results: tuple[ComponentLayerResult, ...]
    proposed_facts: tuple[CaseFactProposal, ...]
    evidence_bindings: tuple[str, ...]
    resolution_proposal_ids: tuple[str, ...]
    context_association_ids: tuple[str, ...]
    profile_gaps: tuple[CaseProfileGapProposal, ...]
    omitted_slots: tuple[str, ...]
    limitations: tuple[str, ...]
    tool_trace_ids: tuple[str, ...]
    source_snapshot_bindings: tuple[SourceSnapshotBinding, ...]
    revision_count: int = Field(ge=0, le=1)
```

`FactAssessment` has a disposition-specific exactly-one validator:

```text
formal_fact -> published_fact_id only
profile_gap -> profile_gap_id only
rejected    -> rejection_id only
```

It rejects any payload that combines a published fact with a profile gap or
rejection. `ValidationFeedback.allowed_corrections` is an ordered, closed list;
a revised proposal may select one listed correction but may not add a new fact,
source, or vocabulary term.

At model level, every `CaseFactProposal` requires at least one evidence-claim
or derivation ID, and every `CaseProfileGapProposal` requires at least one
evidence-claim ID. Both reject an empty validation profile. The
`CaseAssemblyTask` and `CaseAssemblyProposal` cross-validators additionally
require every embedded proposal item's `validation_profile_id` to equal the
task's checksum-bound `schema_profile_id`; callers cannot bypass this by
constructing a row outside the text parser.

`ComponentLayerResult` enforces:

- `ok`: at least one artifact ID, no missing reason, no blocking error;
- `insufficient`: no artifact IDs, one missing-reason code, no blocking error;
- `blocked`: one blocking-error ID;
- a required `insufficient` layer cannot roll up to Assembly `ok` or `partial`;
- a blocked core layer rolls up to `blocked`;
- a blocked optional layer may roll up only to `partial`;
- a `profile_gap` remains a `FactDisposition`, never a layer or Assembly status.

### Analysis contracts

```python
class QueryStatus(str, Enum):
    OK = "ok"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"


class AnswerStatementKind(str, Enum):
    SOURCE_FACT = "source_fact"
    DETERMINISTIC_DERIVATION = "deterministic_derivation"
    AGENT_SYNTHESIS = "agent_synthesis"
    LIMITATION = "limitation"


class AnswerStatement(FrozenContractModel):
    statement_id: str
    statement_kind: AnswerStatementKind
    text: str
    support_fact_ids: tuple[str, ...] = ()
    support_derivation_ids: tuple[str, ...] = ()
    support_profile_gap_ids: tuple[str, ...] = ()
    support_source_ids: tuple[str, ...] = ()
    support_statement_ids: tuple[str, ...] = ()


class CaseAnalysisTask(ChecksummedContract):
    task_id: str
    run_id: str
    question: str
    intent_family: Literal[
        "episode",
        "operational_situation",
        "applicability_and_impact",
        "historical_similarity",
    ]
    event_or_case_scope: tuple[str, ...]
    query_plan_id: str
    available_bound_step_ids: tuple[str, ...]
    executed_bound_step_ids: tuple[str, ...]
    requested_evidence_layers: tuple[str, ...]
    retrieved_fact_ids: tuple[str, ...]
    retrieved_derivation_ids: tuple[str, ...]
    retrieved_profile_gap_ids: tuple[str, ...]
    retrieved_assessment_ids: tuple[str, ...]
    retrieved_source_ids: tuple[str, ...]
    component_layer_results: tuple[ComponentLayerResult, ...]
    missing_evidence: tuple[str, ...]
    source_snapshot_bindings: tuple[SourceSnapshotBinding, ...]
    remaining_step_budget: int = Field(ge=0, le=3)
    answer_status: QueryStatus | None
    answer_contract_id: str


class QueryEvidenceBundle(ChecksummedContract):
    query_id: str
    run_id: str
    task_id: str
    task_payload_checksum: Sha256Hex
    answer_status: QueryStatus
    answer_contract_id: str
    component_statuses: tuple[ComponentLayerStatus, ...]
    component_layer_results: tuple[ComponentLayerResult, ...]
    executed_step_ids: tuple[str, ...]
    unexecuted_required_step_ids: tuple[str, ...]
    retrieved_fact_ids: tuple[str, ...]
    retrieved_derivation_ids: tuple[str, ...]
    retrieved_profile_gap_ids: tuple[str, ...]
    retrieved_assessment_ids: tuple[str, ...]
    retrieved_source_ids: tuple[str, ...]
    source_snapshot_bindings: tuple[SourceSnapshotBinding, ...]
    tool_trace_ids: tuple[str, ...]
    answer_statements: tuple[AnswerStatement, ...]
    limitations: tuple[str, ...]
```

`SourceSnapshotBinding` is a frozen `(source_id, source_family,
source_snapshot_sha256)` row. Batch A validates only invariants that are
provable from the payload itself:

- every `CaseFactProposal.evidence_claim_id` and every
  `CaseProfileGapProposal.evidence_claim_id` is present in the task's
  `selected_evidence_claim_ids`;
- every proposal resolution ID is present in its bound task;
- every `AnswerStatement` support ID is present in the containing bundle;
- source bindings are unique by `source_id` and cannot disagree on family or
  checksum.

Cross-registry ownership of validated facts, derivations, profile gaps,
assessments, and source snapshots is deliberately deferred to the runtime
builders in Batches C and D, where those concrete registries are available.
The dormant Batch A contract module must not claim to validate an undefined
registry.

`AnswerStatement` enforces:

- `source_fact`: a fact or profile-gap ID plus a source ID;
- `deterministic_derivation`: a derivation ID plus supporting fact or source IDs;
- `agent_synthesis`: at least one prior supported statement ID in the same bundle;
- `limitation`: evidence may be empty only when a non-`ok` component layer represents the absence;
- all support IDs must occur in the containing bundle;
- an `unsupported` or `insufficient` bundle contains no unsupported source-fact statement.
- `component_statuses` equals the ordered projection of
  `component_layer_results[*].status`;
- a blocked required component rolls up to Query `blocked`, a missing required
  component rolls up to Query `insufficient`, and an unsupported intent has no
  retrieved evidence or answer statements;
- `executed_step_ids`, `tool_trace_ids`, and `answer_statements` retain
  execution/presentation order and are checksum-covered in that order.

### Additive provider-output parser

Add:

```python
class ParsedCaseAssemblySections(FrozenContractModel):
    proposed_facts: tuple[CaseFactProposal, ...]
    profile_gaps: tuple[CaseProfileGapProposal, ...]


def parse_case_assembly_output(
    raw: str,
    *,
    allowed_validation_profile_ids: frozenset[str],
) -> ParsedCaseAssemblySections:
    """Parse strict JSON-object rows under GRAPH_PATCH and PROFILE_GAPS."""
```

The new parser:

- accepts one JSON object per nonempty row;
- accepts `NONE` as the only empty-section marker;
- rejects pipe-delimited rows, prose, duplicate proposal IDs, unknown keys, missing support, invalid object kinds, and invalid profile IDs;
- requires a nonempty trusted `allowed_validation_profile_ids` set and rejects
  every row whose `validation_profile_id` is not a member;
- does not infer source IDs from a candidate ID;
- does not construct a full `CaseAssemblyProposal`, because trusted task, status, source, checksum, and trace metadata are not provider output;
- leaves the existing `parse_graph_patch` behavior unchanged for the compatibility runtime.

### Steps

- [ ] Write RED tests for every enum, strict/frozen behavior, stable-ID derivation, UTC timestamp rule, prompt/tool binding, set-like versus ordered tuple behavior, checksum rule, task/proposal checksum binding, status roll-up, answer-statement support rule, and parser failure mode above.
- [ ] Add adversarial contract tests:
  - caller supplies `eligible=true` while one required check fails;
  - candidate omits authority evidence, duplicates a required check, or cites evidence owned by another candidate;
  - one sealed task preserves mixed `ok`, `insufficient`, and `blocked`
    candidate-audit rows;
  - candidate audits fail when they omit a raw candidate, duplicate an ID,
    mismatch candidate kind/status, or carry a stale candidate checksum;
  - a blocked audit omits its stable error ID or includes unvalidated candidate
    payload/evidence;
  - a pre-enumeration blocked authority domain is distinguishable from a valid
    empty candidate set in the sealed task checksum;
  - proposal cites an evidence claim or source outside its bound task;
  - task/proposal authority source IDs differ from the exact evidence
    projection despite remaining subsets of an allowed registry;
  - schema check checksum differs from the bound task schema snapshot;
  - fact/profile-gap proposals have empty support or a validation profile that
    differs from the bound assembly task;
  - validation feedback is constructed without its typed fields builder or
    cites another assembly task/proposal state;
  - `FactAssessment` supplies more than one disposition output ID;
  - `component_statuses` differs from its ordered component projection;
  - a blocked required query layer is labelled `insufficient` or `ok`;
  - ordered step, trace, statement, and feedback sequences are changed by sealing.
- [ ] Run:

```bash
uv run pytest -q tests/test_agent_system_decision_case_contracts.py
```

Expected: import errors because the new contract module and parser do not exist.

- [ ] Implement the integrity primitives and contract families.
- [ ] Implement the additive parser without changing `parse_graph_patch`.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_decision_case_contracts.py \
  tests/test_agent_system_architecture_compatibility.py \
  tests/test_agent_system_graph_kernel.py
```

Expected: PASS, with the new contracts still unused by the active workflow.

- [ ] Run:

```bash
uv run ruff check \
  src/aviation_agentic_ai/agent_system/decision_case_contracts.py \
  src/aviation_agentic_ai/agent_system/graph_patch.py \
  tests/test_agent_system_decision_case_contracts.py
git diff --check
```

- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/decision_case_contracts.py \
  src/aviation_agentic_ai/agent_system/graph_patch.py \
  tests/test_agent_system_decision_case_contracts.py
git commit -m "feat(agent-system): add decision-case migration contracts"
```

---

## Task 3: Preserve Structural Slots and Expected Types

**Files:**

- Create: `tests/test_agent_system_structural_context.py`
- Modify: `src/aviation_agentic_ai/agent_system/agents.py`
- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Modify: `tests/test_agent_system.py`
- Modify: `tests/test_agent_system_graph_kernel.py`

### Parser output

Extend the compatibility parser result additively:

```python
@dataclass
class AdvisoryMentions:
    # Existing fields remain unchanged.
    element_type_code: str | None = None
    facility_structural_slot: str | None = None
    facility_expected_entity_type: str | None = None
    term_structural_slot: str | None = None
    term_expected_entity_type: str | None = None
```

Use these deterministic mappings:

```python
FACILITY_SLOT = "controlled_nas_element"
TERM_SLOT = "traffic_management_initiative_type"

ELEMENT_TYPE_TO_ENTITY_TYPE = {
    "APT": "airport",
    "ARTCC": "artcc",
}
```

For supported GDP and Ground Stop records:

```text
CTL ELEMENT: JFK ELEMENT TYPE: APT
```

must produce:

```text
facility_structural_slot = controlled_nas_element
facility_expected_entity_type = airport
term_structural_slot = traffic_management_initiative_type
term_expected_entity_type = traffic_management_initiative
```

An unknown element type is preserved in `element_type_code`, but its expected entity type remains absent. It must not be rewritten as a generic `nas:NASfacility`.

### Candidate inputs and filtering

Extend the compatibility dataclasses with defaulted additive fields:

```python
@dataclass
class FacilityCandidates:
    # Existing fields remain unchanged.
    structural_slot: str = ""
    expected_entity_type: str = ""


@dataclass
class TermCandidates:
    # Existing fields remain unchanged.
    structural_slot: str = ""
    expected_entity_type: str = ""
```

Change:

```python
def _facility_candidates_for_mention(
    all_candidates: list[Any],
    mention: str,
    expected_entity_type: str | None = None,
) -> list[Any]:
    ...
```

Filtering rules:

- code or alias matching runs first;
- every code/alias match is retained and deterministically sorted by canonical
  ID, even when its type is incompatible with the expected type;
- expected-type compatibility is recorded later as a candidate-level
  `ConstraintCheck`, never used as a pre-audit filter;
- an unknown candidate type is not mapped to `nas:NASfacility`;
- an ambiguous path with a missing known slot or expected type returns the compatibility `ABSTAIN` result before provider construction;
- no runtime path supplies `UNCLASSIFIED TEXT`.

The terminology lookup keeps all abbreviation matches until each candidate has an explicit candidate-level type and schema check. It must not preselect a TMI candidate merely by silently dropping other meanings before evidence construction.

### Steps

- [ ] Write RED tests:
  - `test_structured_parser_preserves_controlled_element_slot_and_apt_type`;
  - `test_structured_parser_preserves_unknown_element_type_without_generic_mapping`;
  - `test_workflow_propagates_known_facility_slot_and_expected_type`;
  - `test_workflow_propagates_known_term_slot_and_expected_type`;
  - `test_facility_candidates_are_preserved_for_candidate_level_type_audit`;
  - `test_unknown_facility_type_does_not_default_to_nas_facility`;
  - `test_missing_known_structural_context_makes_zero_provider_calls`;
  - `test_gs_lookup_preserves_both_meanings_before_candidate_compatibility`.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_structural_context.py \
  tests/test_agent_system.py \
  tests/test_agent_system_graph_kernel.py
```

Expected: new assertions fail because element type and structural context are currently discarded.

- [ ] Implement parser fields, exact mappings, candidate filtering, deterministic sorting, and workflow propagation.
- [ ] Remove the `_facility_ontology_type` generic fallback. Return no class for an unknown type and let the compatibility wrapper abstain.
- [ ] Keep direct function signatures and existing return types unchanged.
- [ ] Run the focused tests and confirm GREEN.
- [ ] Run:

```bash
rg -n "UNCLASSIFIED TEXT" src/aviation_agentic_ai
uv run ruff check \
  src/aviation_agentic_ai/agent_system/agents.py \
  src/aviation_agentic_ai/agent_system/workflow.py \
  tests/test_agent_system_structural_context.py
git diff --check
```

Expected: the runtime source tree contains no `UNCLASSIFIED TEXT`.

- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/agents.py \
  src/aviation_agentic_ai/agent_system/workflow.py \
  tests/test_agent_system.py \
  tests/test_agent_system_graph_kernel.py \
  tests/test_agent_system_structural_context.py
git commit -m "feat(agent-system): preserve resolution structural context"
```

---

## Task 4: Build Source-Bound Authority Evidence and Candidate Compatibility

**Files:**

- Create: `src/aviation_agentic_ai/agent_system/authority_evidence.py`
- Create: `tests/test_agent_system_authority_evidence.py`
- Create: `data/sources/faa_atcscc_authority_definitions_v1.yaml`
- Create: `tests/fixtures/agent_system_authority/nasr_records.txt`
- Create: `tests/fixtures/agent_system_authority/pcg_excerpt.txt`
- Create: `tests/fixtures/agent_system_authority/fixture_manifest.json`
- Modify: `src/aviation_agentic_ai/agent_system/sources.py`
- Modify: `tests/test_agent_system_multisource_contracts.py`

### Bounded authority-definition scope

Curate exact FAA Pilot/Controller Glossary excerpts for the only terms needed
by the current three-record path and the frozen `GS` ambiguity fixture:

```yaml
version: faa-atcscc-authority-definitions-v1
authority_source: faa_pilot_controller_glossary
authority_artifact_key: pilot_controller_glossary
authority_artifact_sha256: 6bf5b614446668f4a431b6fd9a5424811b52db6f80e946cb285d00c8a2d6727b
definitions:
  - abbreviation: GDP
    preferred_label: Ground Delay Program
    text: >-
      A traffic management process administered by the ATCSCC, when
      aircraft are held on the ground.
    source_ref: faa_pilot_controller_glossary:PCG_G-3:GROUND_DELAY_PROGRAM

  - abbreviation: GS
    preferred_label: Ground Stop
    text: >-
      The GS is a process that requires aircraft that meet a specific
      criteria to remain on the ground.
    source_ref: faa_pilot_controller_glossary:PCG_G-3:GROUND_STOP

  - abbreviation: GS
    preferred_label: Glide Slope
    text: >-
      Provides vertical guidance for aircraft during approach and landing.
    source_ref: faa_pilot_controller_glossary:PCG_G-1:GLIDESLOPE
```

These are curated source locators and excerpts, not ontology definitions and
not a replacement terminology registry. Other term candidates without a real
definition remain present in `faa_atcscc_terms_v1.yaml`, but their authority
build result is `insufficient`. A preferred label or model-generated sentence
never fills the gap.

Preserve `faa_atcscc_terms_v1.yaml` and `configs/cross_source_v1.yaml`
byte-for-byte. The new definition seed has its own logical version and checksum.
Its records bind to the configured PCG PDF checksum; the unchanged term-seed
checksum independently authenticates category and `denotes_schema_term`.

The ignored raw NASR ZIP and PCG PDF are runtime prerequisites, not portable
unit-test fixtures. Commit only bounded derived fixtures:

- record-addressable KJFK/KEWR NASR rows;
- the three normalized PCG excerpts;
- a fixture manifest naming the upstream artifact hashes, derivation method,
  and explicit `test_fixture_only=true`.

Unit tests build temporary ZIP/text-extractor inputs from those fixtures.
Production code still reads and checksum-validates the configured ZIP/PDF and
must never fall back to the fixture directory. A local source-acceptance test
verifies the committed excerpts against the real PDF when that ignored source
is present; absence of the ignored raw file must not break the portable unit
suite.

Use the repository's existing PDF reader dependency to extract the pinned PCG
locally as ordered `ExtractedPDFPage` rows. Normalize only whitespace for
containment checks, retain the matching page index and glossary entry in
`definition_locator`, and fail closed if an excerpt is absent, occurs on
multiple pages, or occurs under more than one unresolved entry. A flattened
whole-document string is not an accepted extractor result. Do not download or
silently replace the configured PDF.

### Exact authority artifact registry

Do not overload `build_local_snapshot_set` with a partial artifact selection:
that would give a full and a targeted snapshot different contents under the
same `snapshot_id`. Add an authority-specific immutable registry in
`authority_evidence.py`:

```python
AuthorityArtifactKey = Literal[
    "nasr_zip",
    "nasr_manifest",
    "pilot_controller_glossary",
    "term_seed",
    "authority_definition_seed",
    "schema_guide",
]


class AuthorityArtifactBinding(FrozenContractModel):
    artifact_key: AuthorityArtifactKey
    project_path: str
    sha256: Sha256Hex
    byte_count: int


class AuthorityArtifactLoadResult(FrozenContractModel):
    artifact_key: AuthorityArtifactKey
    status: Literal["ok", "insufficient", "blocked"]
    binding: AuthorityArtifactBinding | None = None
    reason_code: str | None = None
    error_id: str | None = None


class AuthoritySnapshotSet(FrozenContractModel):
    authority_snapshot_set_id: str
    base_snapshot_set_id: str
    created_at: AwareDatetime
    artifact_results: tuple[AuthorityArtifactLoadResult, ...]


def build_authority_snapshot_set(
    config: Mapping[str, Any],
    *,
    guide: SchemaGuide,
    schema_guide_path: str | Path,
    created_at: datetime,
    definition_seed_path: str | Path = DEFAULT_AUTHORITY_DEFINITION_SEED,
) -> AuthoritySnapshotSet:
    ...
```

The builder selects the named authority inputs from `config["sources"]`, adds
the explicit definition-seed and schema-guide paths, and emits exactly one
result for every key above. It ignores unrelated Weather/BTS source keys,
rejects a duplicate selected authority key, and rejects a caller-requested
unknown authority key. It reads `schema_guide_path`, proves that its bytes
produce `guide.checksum`, and stores that exact project path; it never assumes
the default guide path for a custom active guide. A valid file produces `ok`
plus one binding; a
missing/checksum-invalid file produces `blocked` plus reason/error and no
binding. It does not raise a global error merely because one source domain
failed. Results are sorted by key and the set ID derives from every
`key=status:sha256-or-error-id` token:

```text
authority_snapshot_set_id =
  stable_contract_id(
    "authority-snapshot-set",
    config.snapshot_set_id,
    "nasr_zip=ok:<sha256>",
    "nasr_manifest=ok:<sha256>",
    "pilot_controller_glossary=ok:<sha256>",
    "term_seed=ok:<sha256>",
    "authority_definition_seed=ok:<sha256>",
    "schema_guide=ok:<sha256>",
  )
```

The identity therefore changes if the exact selection, status, file, or stable
error changes. Facility loading consumes only
`nasr_zip + nasr_manifest + schema_guide`;
terminology loading consumes only
`pilot_controller_glossary + term_seed + authority_definition_seed +
schema_guide`. A NASR failure cannot block a valid terminology domain, and a
PCG failure cannot block a valid facility domain. Optional Weather/BTS files
are outside this registry. The binding table is fixed:

`error_id` is derived only from artifact key and a closed reason code; it never
contains an absolute path, exception text, or retrieval timestamp.

```text
facility authority record -> sources.nasr_zip
NASR ZIP checksum validation -> sources.nasr_manifest
term authority definition -> sources.pilot_controller_glossary
curated excerpt locator -> data/sources/faa_atcscc_authority_definitions_v1.yaml
term category/schema mapping -> sources.term_seed
schema compatibility -> active Schema Guide file
```

### Authority context

```python
class AuthorityBuildStatus(str, Enum):
    OK = "ok"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ExtractedPDFPage:
    page_index: int
    text: str


PDFPageExtractor = Callable[[Path], tuple[ExtractedPDFPage, ...]]


@dataclass(frozen=True)
class NASRAuthorityRecord:
    candidate_id: str
    member_name: str
    record_locator: str
    normalized_raw_record: str
    raw_record_sha256: Sha256Hex
    authority_source_ref: str


@dataclass(frozen=True)
class PCGAuthorityDefinition:
    candidate_id: str
    surface_form: str
    definition_text: str
    definition_locator: str
    authority_source_ref: str


@dataclass(frozen=True)
class FacilityAuthorityCatalog:
    status: AuthorityBuildStatus
    entities: tuple[CanonicalEntity, ...]
    records: tuple[NASRAuthorityRecord, ...]
    reason_code: str | None = None
    error_id: str | None = None


@dataclass(frozen=True)
class TermAuthorityCatalog:
    status: AuthorityBuildStatus
    definitions: tuple[PCGAuthorityDefinition, ...]
    registry_terms: tuple[TermConcept, ...]
    reason_code: str | None = None
    error_id: str | None = None


@dataclass(frozen=True)
class LoadedAuthorityCatalog:
    facility: FacilityAuthorityCatalog
    terminology: TermAuthorityCatalog
    snapshots: AuthoritySnapshotSet
    schema_slice_id: str
    schema_snapshot_sha256: Sha256Hex


@dataclass(frozen=True)
class AuthorityCandidateBuildResult:
    candidate_id: str
    candidate_kind: Literal["facility", "term"]
    status: AuthorityBuildStatus
    candidate: ResolutionCandidate | None = None
    evidence_claim: (
        AuthorityRecordEvidenceClaim | AuthorityDefinitionEvidenceClaim | None
    ) = None
    source_record: SourceRecord | None = None
    reason_code: str | None = None
    error_id: str | None = None


def load_authority_catalog(
    config: dict[str, Any],
    *,
    guide: SchemaGuide,
    schema_guide_path: str | Path,
    created_at: datetime,
    pcg_page_extractor: PDFPageExtractor = extract_pdf_pages,
) -> LoadedAuthorityCatalog:
    ...


def build_facility_resolution_candidate(
    entity: CanonicalEntity,
    *,
    structural_slot: str,
    expected_entity_type: str,
    catalog: FacilityAuthorityCatalog,
    authority_snapshots: AuthoritySnapshotSet,
    guide: SchemaGuide,
) -> AuthorityCandidateBuildResult:
    ...


def build_term_resolution_candidate(
    term: TermConcept,
    *,
    structural_slot: str,
    expected_entity_type: str,
    catalog: TermAuthorityCatalog,
    authority_snapshots: AuthoritySnapshotSet,
    guide: SchemaGuide,
) -> AuthorityCandidateBuildResult:
    ...
```

The CLI calls `load_authority_catalog` with the same active `SchemaGuide` and
the exact path from which it was loaded before provider construction. The
loader forwards both to `build_authority_snapshot_set`; it never substitutes a
default path for a custom guide. It loads
and checksum-validates independent facility and terminology authority domains,
but it does **not** construct a `ResolutionCandidate` or evaluate a mention.
For the active path, the CLI takes `facility_candidates` from
`catalog.facility.entities` and `term_candidates` from
`catalog.terminology.registry_terms`; it does not separately reopen the same
NASR/term files through a second global-failure path. The existing public
source-loader helpers remain available for compatible callers.
The advisory parser supplies `mention`, `structural_slot`, and
`expected_entity_type` later. `_facility_node` and `_terminology_node` then call
the corresponding candidate builder for each mention-matched canonical
candidate.

Facility and terminology failures stay independent. A malformed NASR artifact
blocks facility resolution but does not block a valid terminology path, and a
missing PCG definition makes only that term candidate `insufficient`.
`AuthorityCandidateBuildResult` invariants are:

```text
ok           -> candidate + evidence_claim + source_record; no reason/error
insufficient -> ineligible candidate; no evidence/source; reason_code only
blocked      -> no candidate/evidence/source; reason_code + error_id
```

`AuthorityBuildStatus` maps one-to-one by value to
`CandidateBuildStatus` when the result becomes a sealed audit row; unknown
values are contract errors.

`ok` means the candidate was constructed and audited; it may still be
ineligible because a deterministic slot, type, or schema check failed. For
example, Glide Slope is an `ok` constructed candidate for the `GS` surface form
but is ineligible for the TMI structural slot. An `insufficient` row preserves
the registry-derived candidate identity and explicit constraint checks, but its
empty `authority_evidence_ids` guarantees `eligible == false`. A `blocked` row
is represented by a checksum-sealed `ResolutionCandidateAudit`, in
`ResolutionTask.rejected_candidate_ids`, and in the proposal limitation;
unvalidated candidate content may not enter `ResolutionTask.candidates`.

Every `AuthorityCandidateBuildResult` converts to exactly one
`ResolutionCandidateAudit`. The candidate/result status, audit status, optional
candidate checksum, evidence/source references, reason, and error must agree
before the task can be sealed.

Before any terminal decision, the wrapper proves that the IDs and kinds in
`authority_candidate_results` exactly equal the mention-matched legacy
candidate set. A missing result, foreign result, duplicate ID, wrong
`candidate_kind`, or candidate/result type mismatch is `blocked`.

Mixed per-candidate results roll up conservatively:

- any mention-matched `blocked` result blocks that resolution domain even when
  another candidate is `ok`;
- every mention-matched `insufficient` result makes the resolution
  `insufficient`; Batch A does not waive missing authority merely from
  unbound registry type/schema metadata;
- an `ok` but incompatible candidate is retained in the audited task and
  rejected by explicit constraint checks;
- deterministic acceptance occurs only after every relevant raw candidate has
  an audited terminal result and exactly one complete candidate is eligible.

The normalized authority `SourceRecord` has a stable source ID distinct from
the candidate's canonical ID. Freeze its bytes with this dedicated contract:

```python
class AuthoritySourceContentFields(FrozenContractModel):
    candidate_id: str
    candidate_kind: Literal["facility", "term"]
    preferred_label: str
    candidate_type: str
    surface_form: str
    authority_text: str
    authority_source_ref: str
    authority_locator: str
    authority_record_sha256: Sha256Hex | None = None
    authority_artifact_key: Literal[
        "nasr_zip",
        "pilot_controller_glossary",
    ]
    authority_artifact_sha256: Sha256Hex
    manifest_artifact_key: Literal["nasr_manifest"] | None = None
    manifest_artifact_sha256: Sha256Hex | None = None
    definition_registry_artifact_sha256: Sha256Hex | None = None
    term_registry_artifact_sha256: Sha256Hex | None = None


def normalize_authority_text(value: str) -> str:
    """NFC, LF newlines, no trailing horizontal space or outer blank lines."""


def canonical_authority_source_content(
    fields: AuthoritySourceContentFields,
) -> str:
    normalized = fields.model_copy(
        update={"authority_text": normalize_authority_text(fields.authority_text)}
    )
    return json.dumps(
        normalized.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
```

`normalize_authority_text` applies Unicode NFC, converts CRLF/CR to LF, strips
trailing spaces and tabs from each line, removes leading/trailing blank lines,
preserves internal line structure, and rejects NUL. No other whitespace or
case normalization is allowed. Facility rows require
`authority_record_sha256` and `manifest_artifact_sha256`; term rows require the
two registry checksums. The content never includes `source_id` or the schema
checksum, avoiding cyclic and profile-dependent identity.

`source_snapshot_sha256` is
`sha256(content.encode("utf-8")).hexdigest()`. The source ID is:

```text
stable_contract_id("authority-source", candidate kind, candidate ID,
                   authority source ref, source snapshot checksum)
```

The evidence ID then binds the source ID, source snapshot checksum, and
authority artifact checksum. `authority_artifact_sha256` is the NASR ZIP
checksum for facility evidence or the PCG PDF checksum for definition evidence.
`manifest_artifact_sha256` separately binds the NASR manifest that authenticated
the ZIP.
`definition_registry_artifact_sha256` binds the curated locator/excerpt row.
`term_registry_artifact_sha256` separately binds term category and
`denotes_schema_term` to the unchanged v1 term-seed file. Candidate schema
checks bind the Schema Guide file checksum again through `guide.checksum`; no
second schema hash implementation is introduced. The schema checksum belongs
to the `ConstraintCheck` and `ResolutionTask`, not the authority
`SourceRecord`, so changing a profile does not rewrite the identity of a
source record.

### Facility authority rules

- retain a record-addressable NASR locator such as
  `faa_nasr:2026-05-14:APT.txt:KJFK`, the normalized raw record text, and a
  checksum of that exact raw record;
- choose the exact record-level `faa_nasr:` source reference rather than the
  edition-level `faa_nasr:2026-05-14` reference;
- render typed NASR fields such as preferred name, facility type, and codes;
- never use `airport facility record`;
- never use the entity URI as the authority source;
- require the expected entity type to match;
- map only known entity types to approved Schema Guide classes;
- missing NASR reference is `insufficient`;
- unknown, duplicate, or checksum-mismatched NASR snapshot is `blocked`.
- two facilities from one NASR edition must have different record locators and
  record checksums even though their upstream ZIP checksum is shared.

### Term authority and schema rules

- use one exact `TermDefinition.text` and its definition-level `source_ref`;
- require the normalized definition excerpt to occur in the checksum-pinned
  PCG extraction at the declared page/entry locator;
- reject a preferred label used in place of a definition;
- bind every `faa_pilot_controller_glossary:*` definition to the configured
  `pilot_controller_glossary` PDF checksum only;
- bind the excerpt locator to the new definition-seed checksum;
- bind `term_category` and `denotes_schema_term` separately to the configured
  unchanged `term_seed` v1 checksum; neither seed can self-authenticate the PCG
  definition;
- use `TermConcept.denotes_schema_term` as the candidate ontology class;
- preserve the candidate abbreviation or surface form in the candidate,
  normalized source record, and checksum-covered task payload;
- do not recompute an ambiguous candidate class from its abbreviation;
- resolve both the prefixed class (`atm:GroundStopTMI`) and its absolute IRI
  from the checksum-pinned Schema Guide; a schema checksum mismatch is
  `blocked`;
- mark Ground Stop compatible with:

```text
structural slot: traffic_management_initiative_type
expected type: traffic_management_initiative
ontology class: atm:GroundStopTMI
```

- mark Glide Slope incompatible for that same slot and expected type;
- mark a missing `denotes_schema_term`, absent Schema Guide class, wrong term category, or wrong expected type explicitly incompatible;
- missing definition is `insufficient`;
- unknown source reference, duplicate source binding, corrupt source content, or checksum mismatch is `blocked`.

### Steps

- [ ] Write RED tests:
  - `test_default_gdp_and_gs_candidates_have_real_definitions`;
  - `test_v1_term_seed_and_cross_source_config_remain_byte_identical`;
  - `test_authority_definition_seed_has_independent_version_and_checksum`;
  - `test_authority_snapshot_id_binds_exact_artifact_selection`;
  - `test_portable_authority_fixtures_are_explicitly_test_only`;
  - `test_local_real_pcg_acceptance_matches_pinned_excerpts_when_available`;
  - `test_pcg_definition_excerpt_occurs_in_pinned_pdf_extraction`;
  - `test_pcg_definition_uses_pcg_checksum_not_term_seed_checksum`;
  - `test_definition_term_registry_and_schema_have_separate_checksums`;
  - `test_term_candidate_uses_definition_level_source_reference`;
  - `test_term_candidate_preserves_abbreviation_surface_form`;
  - `test_preferred_label_is_not_accepted_as_a_definition`;
  - `test_facility_candidate_uses_nasr_source_not_canonical_id`;
  - `test_nasr_facilities_share_edition_checksum_but_not_record_locator`;
  - `test_facility_evidence_binds_nasr_zip_and_manifest_checksums`;
  - `test_authority_source_content_is_byte_stable_across_mapping_order`;
  - `test_authority_text_normalizes_crlf_unicode_and_trailing_whitespace`;
  - `test_authority_text_rejects_nul`;
  - `test_schema_change_does_not_rewrite_authority_source_id`;
  - `test_targeted_authority_snapshots_ignore_optional_context_files`;
  - `test_facility_record_rejects_nasr_manifest_checksum`;
  - `test_authority_checksum_mismatch_is_blocked`;
  - `test_unregistered_authority_source_is_blocked`;
  - `test_missing_definition_is_insufficient`;
  - `test_insufficient_candidate_is_preserved_but_never_eligible`;
  - `test_facility_and_term_catalog_failures_are_independent`;
  - `test_missing_or_corrupt_nasr_does_not_block_pcg_catalog`;
  - `test_missing_or_corrupt_pcg_does_not_block_nasr_catalog`;
  - `test_loaded_catalog_is_the_single_active_candidate_source`;
  - `test_candidate_build_result_carries_candidate_kind`;
  - `test_ok_and_blocked_relevant_candidates_roll_up_to_blocked`;
  - `test_ok_and_insufficient_relevant_candidates_roll_up_to_insufficient`;
  - `test_incompatible_but_unbound_insufficient_candidate_prevents_acceptance`;
  - `test_raw_and_built_candidate_sets_must_match_exactly`;
  - `test_schema_compatibility_is_candidate_specific_for_gs`;
  - `test_denotes_schema_term_must_match_the_active_guide`;
  - `test_schema_snapshot_checksum_mismatch_is_blocked`;
  - `test_candidate_ontology_class_must_exist_in_the_pinned_guide`;
  - `test_unique_candidate_is_zero_model_only_after_evidence_and_schema_checks`.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_authority_evidence.py \
  tests/test_agent_system_multisource_contracts.py
```

Expected: definition, source-binding, checksum, and compatibility assertions fail.

- [ ] Record fixture checksums for the unchanged v1 term seed and cross-source config, then add the independent v1 authority-definition seed.
- [ ] Implement the exact-key authority registry and deterministic per-domain catalog loaders without modifying the general cross-source snapshot builder.
- [ ] Build mention-specific candidates only after parser output supplies structural slot and expected type.
- [ ] Keep `load_term_source` as the terminology registry loader; make the authority builder reject a candidate without a separately verified PCG definition instead of falling back to its preferred label.
- [ ] Implement exact raw-candidate/build-result matching and the mixed-status roll-up before any deterministic acceptance.
- [ ] Ensure all IDs and row order are derived from canonical inputs and byte-stable.
- [ ] Run the focused tests and confirm GREEN.
- [ ] Run:

```bash
rg -n "an authority term definition|airport facility record" \
  src/aviation_agentic_ai data/sources
uv run ruff check \
  src/aviation_agentic_ai/agent_system/authority_evidence.py \
  src/aviation_agentic_ai/agent_system/sources.py \
  tests/test_agent_system_authority_evidence.py
git diff --check
```

Expected: no production placeholder authority text remains.

- [ ] Commit:

```bash
git add \
  data/sources/faa_atcscc_authority_definitions_v1.yaml \
  tests/fixtures/agent_system_authority/nasr_records.txt \
  tests/fixtures/agent_system_authority/pcg_excerpt.txt \
  tests/fixtures/agent_system_authority/fixture_manifest.json \
  src/aviation_agentic_ai/agent_system/authority_evidence.py \
  src/aviation_agentic_ai/agent_system/sources.py \
  tests/test_agent_system_authority_evidence.py \
  tests/test_agent_system_multisource_contracts.py
git commit -m "feat(agent-system): bind resolution candidates to authority evidence"
```

---

## Task 5: Add Deterministic Compatibility Wrappers and Frozen Run Bindings

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/runtime.py`
- Modify: `src/aviation_agentic_ai/cli_agent_system.py`
- Modify: `src/aviation_agentic_ai/agent_system/agents.py`
- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Create: `tests/test_agent_system_runtime_binding.py`
- Modify: `tests/test_agent_system.py`
- Modify: `tests/test_agent_system_tool_model.py`
- Modify: `tests/test_agent_system_multisource_context.py`
- Modify: `tests/test_cli_agent_system.py`

`configs/prompts/agent_system_v1.yaml`, the active prompt catalog constant, and
the five current role keys remain unchanged. Batch A does not render authority
candidates for a provider, parse a Semantic Resolution response, or persist a
model-mediated Resolution proposal. Those changes begin only in Batch B.

### One frozen run binding

Add:

```python
ModelInvokerFactory = Callable[[], ModelInvoker]


@dataclass(frozen=True)
class RunBinding:
    run_id: str
    run_dir: Path
    run_started_at: datetime


def create_run_binding(
    base_root: str | Path,
    source_id: str,
    *,
    started_at: datetime | None = None,
) -> RunBinding:
    ...
```

`create_run_binding` samples the clock exactly once, requires/normalizes UTC,
creates the same versioned run-directory shape, and returns one immutable
value. Keep `new_run_directory(base_root, source_id)` public and compatible by
delegating to `create_run_binding(...).run_dir`.

Add an optional `created_at: datetime | None = None` argument to
`write_run_manifest`. The CLI supplies `RunBinding.run_started_at`; a legacy
caller that omits it retains current behavior. Tests prove:

```text
ResolutionTask.created_at
= deterministic ResolutionProposal.created_at
= run_manifest.created_at
= RunBinding.run_started_at
```

The serialized manifest remains under its existing `created_at` key; no new
manifest key is introduced.

### Lazy resolution-provider boundary

Extend `IngestContext` additively:

```python
authority_catalog: LoadedAuthorityCatalog | None = None
run_started_at: datetime | None = None
model_invoker_factory: ModelInvokerFactory | None = None
```

Retain the existing injected `model_invoker` field for compatibility tests.
The CLI passes a factory:

```python
model_invoker_factory=lambda: make_live_model_invoker(
    catalog_path=DEFAULT_PROMPT_CATALOG
)
```

but does not call it. The Knowledge Graph Construction
`kg_tool_model_factory` remains a separate lazy factory with the unchanged
call budget. In Batch A no facility or terminology branch may call either the
injected Resolution invoker or its factory. Tests count both construction and
invocation, not just recorded model calls.

### Upstream event and schema binding

Add these defaulted fields to both `FacilityCandidates` and `TermCandidates`
without changing either public wrapper signature:

```python
resolution_event_id: str = ""
run_started_at: datetime | None = None
structural_slot: str = ""
expected_entity_type: str = ""
schema_slice_id: str = ""
schema_snapshot_sha256: str = ""
resolution_tool_version: str = ""
authority_domain_status: AuthorityBuildStatus | None = None
authority_domain_reason_code: str = ""
authority_domain_error_id: str = ""
authority_candidate_results: tuple[AuthorityCandidateBuildResult, ...] = ()
```

The `advisory` node derives a nonempty resolution event binding after
deterministic parsing and before fan-out:

1. read the normalized parsed event mention, or the literal
   `MISSING_EVENT_MENTION`;
2. compute:

```text
resolution_event_id =
  stable_contract_id("resolution-event", run_id, advisory.source_id,
                     normalized mention or "MISSING_EVENT_MENTION")
```

3. resolve only the parsed value through the active Schema Guide;
4. return the required `resolution_event_id`, optional `event_class_hint`, and
   optional `formal_event_uri_hint` in workflow state;
5. if the mention or class mapping is absent, retain the nonempty resolution
   binding and make the affected semantic resolution `insufficient` without
   provider construction.

The terminology result still owns the event-class claim. Before KG tool-model
construction, `_kg_construction_node` verifies that the resolved term class and
recomputed formal event URI equal the optional upstream hints. A mismatch is
`blocked`; neither hint becomes an event fact by itself.

The workflow supplies the same `run_started_at`, resolution event ID, guide slice ID,
guide checksum, and frozen `resolution-compatibility-v1` tool version to both
parallel branches. Direct callers expecting resolution must supply the same
metadata. Missing or inconsistent `resolution_event_id`, run timestamp, schema,
or tool binding is structurally `blocked`; a valid binding with a semantically
missing event mention/class is `insufficient`.
The node also copies only its own authority-domain status/reason/error into the
candidate envelope. A blocked facility catalog does not overwrite the
terminology catalog status, and vice versa.

### Compatibility wrapper behavior

Keep the public signatures:

```python
@dataclass(frozen=True)
class CompatibilityResolutionResult:
    agent_result: AgentResult
    domain_outcome: ResolutionDomainOutcome
    authority_source_records: tuple[SourceRecord, ...]


def _resolve_facility_compatibility(
    *,
    task: AgentTask,
    candidates: FacilityCandidates,
) -> CompatibilityResolutionResult:
    ...


def _resolve_terminology_compatibility(
    *,
    task: AgentTask,
    candidates: TermCandidates,
) -> CompatibilityResolutionResult:
    ...


def run_facility_agent(
    *,
    task: AgentTask,
    candidates: FacilityCandidates,
    model_invoker: ModelInvoker | None = None,
) -> AgentResult:
    ...


def run_terminology_agent(
    *,
    task: AgentTask,
    candidates: TermCandidates,
    model_invoker: ModelInvoker | None = None,
) -> AgentResult:
    ...
```

The public wrappers delegate to the corresponding internal compatibility
helper and return only `.agent_result`, preserving their signatures and return
contracts. Workflow nodes call the internal helpers and place
`.domain_outcome` and `.authority_source_records` into their typed state
channels. No mutable global, `AgentResult` extension, hidden tuple return, or
prose parsing is permitted.

The workflow supplies mention-specific build results; it never passes the
whole catalog to a wrapper. Direct tests must supply complete build results and
execution bindings when they expect resolution.

Both internal helpers construct and validate an in-memory `ResolutionTask` and
a deterministic `ResolutionProposal`, then map it to the existing
`AgentResult`/`EvidenceCard` shape:

| Audited result | Deterministic decision | Legacy status | Resolution provider |
| --- | --- | --- | --- |
| Exactly one eligible candidate | `accepted` | `resolved` | factory untouched |
| No eligible candidate because required evidence is absent | `insufficient` | `abstain` | factory untouched |
| More than one eligible candidate | `abstained` with `MODEL_MEDIATED_RESOLUTION_DEFERRED_BATCH_B` | `abstain` | factory untouched |
| Contract, source, checksum, or relevant-candidate corruption | `blocked` | `blocked` | factory untouched |

Each internal helper returns its typed `ResolutionDomainOutcome` to its
workflow node. Add separate `facility_resolution_outcome` and
`terminology_resolution_outcome` fields to `IngestState`; do not attempt to
recover these decisions from legacy `AgentResult` prose.
Task 5 also adds `resolution_event_id`, `event_class_hint`,
`formal_event_uri_hint`, and `resolution_preflight_status`; Task 6 only adds the
parallel authority-record registry channel shown later.

At `join`, run a deterministic required-domain preflight before constructing
the KG tool model:

```text
any required domain BLOCKED
  -> final ingest/context BLOCKED; KG factory construction count = 0

else any required domain INSUFFICIENT or ABSTAINED
  -> final ingest/context INSUFFICIENT; KG factory construction count = 0

else
  -> KG construction may proceed under the existing call budget
```

Independent branches still finish and retain their audited outcomes before the
preflight. Status precedence is `blocked > insufficient > resolved`; no legacy
mapping may weaken a required-domain `blocked` to `abstain` or later
`insufficient`. `integrate_decision_context` receives the typed preflight
status and preserves it in the existing manifest/status surface.

Before applying the table, each wrapper:

- maps its explicit authority-domain `blocked`/`insufficient` terminal before
  attempting candidate-set equality;
- requires exact candidate-ID and candidate-kind correspondence between the
  mention-matched legacy candidate set and
  `authority_candidate_results`;
- applies the mixed-result roll-up from Task 4;
- checks the task/run/event/schema/tool bindings;
- computes eligibility only from validated evidence and constraints;
- never filters a terminology candidate solely by abbreviation category;
- never weakens `blocked` to `abstain`;
- never uses the v1 permissive prompt or substring candidate picker.

Remove the dead placeholder renderers and active calls to
`_facility_candidate_row`, `_term_candidate_row`,
`_pick_candidate_from_response`, and `_pick_term_from_response`. Preserve the
v1 prompt file itself for archival inspection and fixture readability; Batch A
does not promise executable replay of its former ambiguous-provider behavior,
and the deterministic wrappers do not use it.

### Legacy envelope and authority isolation

Do not hide a new artifact inside `EvidenceCard.decision_basis` and do not
point `AgentResult.artifact_ref` at a proposal that was never persisted.

For Batch A:

- `decision_basis` remains one concise English sentence containing only the
  deterministic decision, reason code, `resolution_task_id`, and tool version;
- `ToolTraceEntry.result_refs` may contain the stable task ID and selected
  canonical candidate ID, but no authority evidence/source IDs or source text;
- `AgentResult.artifact_ref` retains its current behavior;
- accepted facility/term `EvidenceClaim.source_id` remains the advisory source
  whose exact advisory span supports the event claim;
- authority evidence claims, source IDs, locators, checksums, and raw text stay
  in the in-memory Resolution task and the separate workflow authority-record
  channel defined in Task 6;
- the task/proposal object is not added to `run_manifest.json`.

This is an intentionally reconstructible deterministic audit reference, not a
claim that Batch A persists the complete future Resolution Agent trace.

### Steps

- [ ] Write RED tests:
  - `test_run_binding_samples_one_utc_timestamp`;
  - `test_manifest_created_at_uses_frozen_run_started_at`;
  - `test_resolution_contracts_and_manifest_share_run_started_at`;
  - `test_cli_passes_lazy_resolution_invoker_factory`;
  - `test_public_wrappers_keep_agent_result_return_contract`;
  - `test_internal_helpers_return_typed_outcome_and_authority_records`;
  - `test_unique_candidate_constructs_and_calls_no_resolution_provider`;
  - `test_insufficient_candidate_constructs_and_calls_no_resolution_provider`;
  - `test_blocked_candidate_constructs_and_calls_no_resolution_provider`;
  - `test_multiple_eligible_candidates_defer_to_batch_b_without_provider`;
  - `test_wrapper_requires_exact_raw_and_built_candidate_sets`;
  - `test_foreign_missing_duplicate_or_wrong_kind_build_result_is_blocked`;
  - `test_blocked_catalog_with_no_candidates_differs_from_valid_empty_catalog`;
  - `test_relevant_ok_plus_blocked_candidate_is_blocked`;
  - `test_relevant_ok_plus_insufficient_candidate_is_insufficient`;
  - `test_legacy_wrapper_never_weakens_blocked_to_abstain`;
  - `test_workflow_builds_candidates_after_structural_parsing`;
  - `test_workflow_supplies_event_time_schema_and_tool_bindings`;
  - `test_missing_event_semantics_are_insufficient_with_valid_resolution_binding`;
  - `test_missing_or_corrupt_resolution_event_binding_is_blocked`;
  - `test_event_class_hint_mismatch_blocks_before_kg_model_construction`;
  - `test_required_blocked_domain_stops_kg_factory_and_remains_blocked`;
  - `test_required_insufficient_domain_stops_kg_factory`;
  - `test_workflow_ambiguous_resolution_constructs_no_kg_or_resolution_provider`;
  - `test_decision_basis_is_concise_and_has_no_authority_payload`;
  - `test_tool_trace_has_no_authority_source_or_evidence_ids`;
  - `test_authority_sources_never_enter_legacy_event_claim_source_ids`;
  - `test_v1_prompt_config_and_term_registry_are_byte_identical`;
  - `test_batch_a_keeps_exact_five_legacy_prompt_role_keys`;
  - `test_v1_artifacts_remain_readable_without_claiming_behavioral_replay`.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_runtime_binding.py \
  tests/test_agent_system.py \
  tests/test_agent_system_tool_model.py \
  tests/test_agent_system_authority_evidence.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_cli_agent_system.py
```

Expected: run-binding, lazy-construction, deterministic-wrapper, and
event/schema-binding assertions fail.

- [ ] Implement `RunBinding`, manifest timestamp injection, and the lazy
  Resolution factory without changing current CLI options.
- [ ] Load the authority catalog with the frozen run timestamp and pass it
  through `IngestContext`.
- [ ] Compute the event binding before fan-out; build per-mention candidate
  results only inside the facility and terminology nodes.
- [ ] Implement the exact candidate-set audit, mixed-status roll-up, sealed
  in-memory task/proposal, typed domain outcomes, required-domain preflight,
  and explicit new-to-legacy mapping.
- [ ] Remove placeholder candidate renderers and all active compatibility
  Resolution model calls. Do not edit the v1 prompt catalog.
- [ ] Run the focused tests and confirm GREEN.
- [ ] Run:

```bash
rg -n "an authority term definition|airport facility record|UNCLASSIFIED TEXT" \
  src/aviation_agentic_ai
git diff --exit-code -- \
  configs/prompts/agent_system_v1.yaml \
  configs/cross_source_v1.yaml \
  data/sources/faa_atcscc_terms_v1.yaml
uv run ruff check \
  src/aviation_agentic_ai/agent_system/runtime.py \
  src/aviation_agentic_ai/agent_system/agents.py \
  src/aviation_agentic_ai/agent_system/workflow.py \
  src/aviation_agentic_ai/cli_agent_system.py \
  tests/test_agent_system_runtime_binding.py \
  tests/test_agent_system.py \
  tests/test_cli_agent_system.py
git diff --check
```

Expected: no active runtime placeholder remains and the v1 prompt/source files
have no diff.

- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/runtime.py \
  src/aviation_agentic_ai/cli_agent_system.py \
  src/aviation_agentic_ai/agent_system/agents.py \
  src/aviation_agentic_ai/agent_system/workflow.py \
  tests/test_agent_system_runtime_binding.py \
  tests/test_agent_system.py \
  tests/test_agent_system_tool_model.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_cli_agent_system.py
git commit -m "feat(agent-system): ground deterministic resolution wrappers"
```

---

## Task 6: Integrate Authority Audit Snapshots Without Migrating the Runtime

**Files:**

- Modify: `src/aviation_agentic_ai/agent_system/workflow.py`
- Modify: `src/aviation_agentic_ai/agent_system/context_artifacts.py`
- Modify: `src/aviation_agentic_ai/agent_system/kg_tools.py`
- Modify: `tests/test_agent_system_multisource_contracts.py`
- Modify: `tests/test_agent_system_multisource_context.py`
- Modify: `tests/test_agent_system_graph_kernel.py`
- Modify: `tests/test_agent_system_kg_tool_graph.py`
- Modify: `tests/test_cli_agent_system.py`
- Modify: `docs/multi_agent_kg_system_design.md`
- Modify: `docs/superpowers/specs/2026-07-27-three-agent-decision-case-architecture-design.md`
- Modify: `docs/superpowers/plans/2026-07-27-three-agent-batch-a-contracts-authority-evidence.md`

### Runtime input carried forward from Task 5

Task 5 already adds:

```python
authority_catalog: LoadedAuthorityCatalog | None = None
run_started_at: datetime | None = None
model_invoker_factory: ModelInvokerFactory | None = None
```

The CLI has already loaded the checksum-validated catalog and captured one
UTC-aware `run_started_at` before any Resolution-provider construction.
`LoadedAuthorityCatalog.facility` and `.terminology` carry independent typed
`ok | insufficient | blocked` results, reason codes, and error IDs. There is no
global `authority_failure_reason`. The workflow nodes construct mention-specific
candidates only after the advisory parser has supplied slot and expected type.
Missing evidence yields `insufficient`; malformed snapshots, unknown source
refs, or checksum mismatches block only the affected resolution domain before
provider construction.

### Parallel authority-record state

Add one explicit state channel:

```python
class AuthoritySourceRegistryStatus(str, Enum):
    OK = "ok"
    BLOCKED = "blocked"


class AuthoritySourceRecordRegistry(FrozenContractModel):
    status: AuthoritySourceRegistryStatus
    records: tuple[SourceRecord, ...] = ()
    reason_code: str | None = None
    error_id: str | None = None


def merge_authority_source_records(
    left: AuthoritySourceRecordRegistry,
    right: AuthoritySourceRecordRegistry,
) -> AuthoritySourceRecordRegistry:
    ...


class IngestState(TypedDict):
    # Existing fields remain.
    resolution_event_id: str
    event_class_hint: str | None
    formal_event_uri_hint: str | None
    facility_resolution_outcome: ResolutionDomainOutcome | None
    terminology_resolution_outcome: ResolutionDomainOutcome | None
    resolution_preflight_status: ResolutionDecision | None
    authority_source_records: Annotated[
        AuthoritySourceRecordRegistry,
        merge_authority_source_records,
    ]
```

Each facility/terminology node returns an `ok` registry containing every
`SourceRecord` referenced by its
sealed task, including an explicitly incompatible but successfully audited
candidate. The reducer:

- sorts by `source_id`;
- deduplicates byte-identical rows;
- returns a `blocked` registry with no authority rows when the same source ID
  has a different family, canonical content, or content checksum;
- returns `blocked` for authority families outside `NASR_FACILITY` and
  `FAA_TERM`;
- does not merge a missing/blocked candidate that produced no valid source
  record.

Conflict error IDs derive from a closed reason code and conflicting source ID,
not exception prose. A blocked registry prevents authority snapshot merge,
preserves the already validated core source registry, and raises the final
typed status to `blocked`; it cannot crash out of the workflow or leave a
partially merged authority registry.

The decision-context node receives the merged immutable registry through
workflow state. No node recovers authority records from `EvidenceCard`,
`decision_basis`, or tool trace prose.

### Snapshot persistence

The existing `source_snapshots.jsonl` remains the only source registry artifact.

Persist:

```text
advisory source
+ every facility authority record referenced by a ResolutionTask
+ every term-definition authority record referenced by a ResolutionTask
+ already admitted Weather records
+ already admitted BTS source
```

Rules:

- persist every valid authority record included in the sealed task, including
  deterministically rejected or unselected candidates needed to reconstruct
  candidate compatibility;
- deterministic unique-candidate tasks persist the authority records referenced
  by that sealed task;
- preserve the normalized authority record's exact content checksum;
- require its upstream authority artifact checksum to match the candidate evidence;
- keep formal event facts bound to their existing advisory evidence;
- do not make authority records formal graph nodes merely because they are registered sources;
- compute KG `allowed_source_ids` only from accepted event
  `EvidenceClaim.source_id` values. Do not union authority
  `ToolTraceEntry.source_ids` or every registered snapshot into that allowlist;
- keep the pre-materialization registry used by the Formal Graph Kernel scoped
  to event evidence. Merge authority audit records only in the later
  `context_artifacts` persistence step after core graph validation;
- do not add a manifest key or a separate authority artifact file;
- repeated runs produce the same task-referenced authority source IDs and checksums.

When the authority registry is `ok`, `integrate_decision_context` extends its
current `persisted_records` list with
`state["authority_source_records"].records` before building the final
multisource registry. When it is `blocked`, it persists no authority rows and
preserves the typed blocked status. The existing
`context_artifacts.source_snapshots` metadata therefore registers the merged
file without a new artifact key.

### KG-visible evidence projection and allowlist

`KGConstructionToolGateway.get_source_evidence` must stop returning raw
`EvidenceCard.model_dump()` values. Add a deterministic projection containing
only:

```python
class KGVisibleEvidenceCard(StrictModel):
    agent_role: str
    status: AgentStatus
    claims: list[EvidenceClaim]
    canonical_refs: list[str]


def project_kg_visible_evidence(
    card: EvidenceCard,
    *,
    allowed_source_ids: set[str],
) -> KGVisibleEvidenceCard:
    ...
```

Exclude `decision_basis`, the entire free-form `uncertainties` list, authority
task/proposal IDs, authority source bindings, authority raw text, and all
upstream tool-trace internals. Do not replace `uncertainties` with free-form
prose; a later bounded limitation-code projection requires its own contract.
Build
`allowed_source_ids` from the accepted event `EvidenceClaim.source_id` values,
not from card-level source IDs, tool traces, or the complete snapshot registry.
The projected `canonical_refs` are the sorted unique canonical refs actually
used by the filtered claims; an unrelated card-level reference is omitted.

The Formal Graph Kernel and KG tool gateway both enforce “every cited source is
allowed.” A patch line citing `[advisory_source, authority_source]` is rejected
rather than partially filtered. A `prov:wasDerivedFrom` edge whose object is an
authority source is likewise rejected; registering an authority snapshot never
authorizes it as an event-fact source.

### Integration acceptance

For Ground Stop 123:

- both `GS` meanings are constructed as source-bound candidates;
- structural and schema checks leave Ground Stop as the sole eligible event meaning;
- zero terminology provider calls;
- KJFK remains canonical;
- the declared reason remains a profile gap;
- no formal `atm:impactingCondition` fact.

For GDP 138:

- GDP has a real definition and source binding;
- the candidate class is `atm:GroundDelayProgramTMI`;
- zero terminology provider calls;
- KJFK, cross-midnight interval, formal `weather`, and exact `THUNDERSTORMS` evidence remain unchanged.

For cancellation 020:

- GDP has the same source-bound term resolution;
- KEWR and the operational period remain unchanged;
- no Weather or authority definition completes the absent declared reason;
- a declared-reason query remains `insufficient` with zero provider calls.

All three runs:

- have the same KG construction call budget as before Batch A;
- add no Semantic Resolution, Assembly, or Analysis model call;
- preserve RDF and Neo4j facts;
- preserve Query behavior;
- persist task-referenced authority snapshots without duplicating KJFK, KEWR, facts, or relationships.

### Documentation boundary

Amend only:

- the compatibility/migration section of the normative system design;
- the Batch A status in the approved three-Agent architecture specification.

State:

```text
Batch A contracts and authority evidence implemented.
Three-Agent runtime migration not started.
Current workflow and reader-facing role names remain the compatibility runtime.
```

Do not change README, project metadata, `RESEARCH_AUDIT.md`, `GOALS.md`, `ARTIFACT_INDEX.md`, or `REPRODUCIBILITY.md` to claim a three-Agent runtime.

### Steps

- [ ] Write RED tests:
  - `test_facility_authority_corruption_does_not_block_valid_term_domain`;
  - `test_term_authority_corruption_does_not_block_valid_facility_domain`;
  - `test_cli_preserves_domain_isolation_when_one_authority_file_is_missing`;
  - `test_authority_corruption_stops_affected_domain_before_provider_construction`;
  - `test_blocked_resolution_status_survives_join_context_and_manifest`;
  - `test_parallel_authority_record_reducer_deduplicates_identical_rows`;
  - `test_parallel_authority_record_reducer_blocks_conflicting_source_ids`;
  - `test_task_referenced_authority_records_enter_existing_snapshot_registry`;
  - `test_incompatible_audited_candidate_is_persisted_for_reconstruction`;
  - `test_authority_sources_do_not_become_formal_graph_facts`;
  - `test_graph_patch_citing_only_nasr_or_pcg_authority_source_is_rejected`;
  - `test_graph_patch_mixing_advisory_and_authority_source_is_rejected`;
  - `test_provenance_edge_targeting_authority_source_is_rejected`;
  - `test_graph_allowlist_excludes_authority_tool_trace_sources`;
  - `test_kg_source_evidence_projection_excludes_authority_audit_internals`;
  - `test_kg_projection_rejects_authority_text_in_every_free_form_field`;
  - `test_authority_snapshots_join_only_after_formal_graph_validation`;
  - `test_repeated_ingest_keeps_authority_ids_and_checksums_stable`;
  - `test_three_cases_preserve_facility_time_and_reason_semantics`;
  - `test_batch_a_adds_no_model_calls`;
  - `test_cli_help_and_failure_messages_remain_compatible`.
- [ ] Run:

```bash
uv run pytest -q \
  tests/test_agent_system_multisource_contracts.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_graph_kernel.py \
  tests/test_agent_system_kg_tool_graph.py \
  tests/test_cli_agent_system.py
```

Expected: new authority-catalog, per-domain status, audit-snapshot, and
graph-allowlist assertions fail.

- [x] Merge every authority source record referenced by a sealed compatibility task into the existing persisted source registry.
- [x] Keep formal fact evidence bindings unchanged.
- [x] Refactor the KG source allowlist to use accepted event claims only,
  sanitize the KG-visible EvidenceCard projection, and prove that authority
  audit sources cannot authorize an event fact or provenance edge.
- [x] Update the two approved design documents with the exact Batch A status boundary.
- [x] Run the focused tests and confirm GREEN.
- [x] Run the complete Batch A focused suite:

```bash
uv run pytest -q \
  tests/test_agent_system_architecture_compatibility.py \
  tests/test_agent_system_decision_case_contracts.py \
  tests/test_agent_system_structural_context.py \
  tests/test_agent_system_authority_evidence.py \
  tests/test_agent_system_runtime_binding.py \
  tests/test_agent_system_multisource_contracts.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_graph_kernel.py \
  tests/test_agent_system_kg_tool_graph.py \
  tests/test_agent_system_tool_model.py \
  tests/test_agent_system.py \
  tests/test_cli_agent_system.py
```

- [ ] Run the final repository gates:

```bash
uv run ruff check .
uv run pytest -q
uv build
git diff --check
```

- [ ] Run final scope scans:

```bash
rg -n "an authority term definition|airport facility record|UNCLASSIFIED TEXT" \
  src data/sources

git grep -nE \
  "Semantic Resolution Agent|Decision Case Assembly Agent|Decision Case Analysis Agent" \
  -- \
  README.md \
  RESEARCH_AUDIT.md \
  GOALS.md \
  ARTIFACT_INDEX.md \
  src/aviation_agentic_ai/cli_agent_system.py
```

Expected:

- the placeholder scan returns no active match;
- the public-claim scan returns no new three-Agent runtime claim;
- tests make no real provider call.

- [ ] Commit:

```bash
git add \
  src/aviation_agentic_ai/agent_system/workflow.py \
  src/aviation_agentic_ai/agent_system/context_artifacts.py \
  src/aviation_agentic_ai/agent_system/kg_tools.py \
  tests/test_agent_system_multisource_contracts.py \
  tests/test_agent_system_multisource_context.py \
  tests/test_agent_system_graph_kernel.py \
  tests/test_agent_system_kg_tool_graph.py \
  tests/test_cli_agent_system.py \
  docs/multi_agent_kg_system_design.md \
  docs/superpowers/specs/2026-07-27-three-agent-decision-case-architecture-design.md \
  docs/superpowers/plans/2026-07-27-three-agent-batch-a-contracts-authority-evidence.md
git commit -m "feat(agent-system): integrate Batch A authority context"
```

---

## Batch A Completion Checkpoint

Batch A is complete only when one handoff reports all of the following:

```text
new migration contract module and contract version
canonical checksum algorithm and checksum tests
strict status and statement-support invariants
additive Case Assembly JSON parser
structural-slot and expected-type propagation
real GDP, Ground Stop, and Glide Slope definitions
authority source IDs, record locators, normalized snapshot checksums,
PCG/NASR artifact checksums, term-registry checksum, and schema checksum
candidate-specific schema compatibility
unchanged v1 prompt/config/source identities
one frozen run timestamp shared by contracts and manifest
explicit new-to-legacy status mapping
stable deterministic resolution references in the legacy envelope
no authority evidence or source data exposed to the KG Agent
all task-referenced authority records in source_snapshots.jsonl
proof that authority audit sources are excluded from the KG write allowlist
three-case semantic results
per-role model-call counts
focused and full test results
build result
remaining Batch B blockers
```

Expected model-call effect:

```text
Advisory deterministic path: unchanged
Facility unique path: 0
Terminology GDP/GS path after compatibility filtering: 0
KG construction path: unchanged
Decision-context adapters: 0
Query unsupported or missing-evidence paths: 0
New three-Agent roles: not activated
```

## Explicitly Deferred After Batch A

- Semantic Resolution Agent runtime loop and its accepted/abstained traces;
- Semantic Resolution prompt v2, canonical provider candidate payload, strict
  provider-output parser, and lazy-factory activation for genuine ambiguity;
- replacement of facility and terminology workflow nodes;
- Decision Case Assembly Agent and validation-guided revision;
- Decision Case Analysis Agent and bound-step gateway;
- new persisted Resolution, Assembly, or Analysis proposal artifacts;
- public three-Agent naming;
- corpus-scoped episode, applicability, and similarity stores;
- lifecycle grouping;
- flight-scope and observed-flight integration;
- ASPM, TCF, CWA, SIGMET, NOTAM, or ADS-B expansion;
- causal explanation;
- TMI recommendation or optimization;
- live-provider smoke tests;
- Agent-count comparisons or ablations.
