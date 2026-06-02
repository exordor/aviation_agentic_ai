# Agentic Artifact Contract

Use this template before adding a multi-agent or agent-assisted step to the
pipeline. The goal is to make each role accountable for one artifact, one
boundary, and one measurable handoff.

## Material Passport

- Domain:
- Module:
- Run ID:
- Date:
- Owner:
- Source scope:
- Reference ontology/profile:
- Competency questions:
- Prior artifacts consumed:
- Output artifacts emitted:

## Role Contract

| Role | Allowed inputs | Required output | Stop condition | Escalation condition |
| --- | --- | --- | --- | --- |
| Source Steward | | `source_inventory.{json,md}` | | |
| CQ Designer | | `competency_questions.md` / `cq_query_manifest.json` | | |
| Domain Expert / SRD Agent | | `semantic_requirements.md` | | |
| Ontology Manager / TIP Agent | | `technical_implementation_plan.md` | | |
| Extraction Planner | | `extraction_plan.md` | | |
| Extractor / Coder | | candidate facts, TTL, JSONL, or patch | | |
| Schema Validator | | `validation_findings.{json,md}` | | |
| Evidence Critic | | `evidence_support_findings.{json,md}` | | |
| Repair Planner | | `repair_plan.md` | | |
| Graph-Use Planner | | `graph_use_plan.md` | | |
| Evaluation Agent | | `evaluation_report.{json,md}` | | |
| Report Synthesizer | | claim-safe stage report | | |

## Artifact Requirements

Each emitted artifact must include:

- source or prior-artifact IDs consumed;
- CQ IDs or module IDs affected;
- source evidence spans or explicit `no_source_support`;
- ontology/profile elements used or profile gaps found;
- validation status;
- unresolved failure modes;
- whether the artifact is `accepted`, `partial`, `quarantined`, `rejected`, or
  `deferred`.

## Bounded Iteration Policy

- Maximum repair cycles:
- Maximum tokens or cost:
- Maximum wall time:
- Conditions that stop repair:
- Conditions that require human review:
- Conditions that quarantine the item:

## Evaluation Hooks

| Check | Deterministic, LLM-assisted, or human | Artifact field |
| --- | --- | --- |
| Syntax/schema validity | | |
| Evidence containment | | |
| Evidence support | | |
| CQ alignment | | |
| Profile gap detection | | |
| Redundancy/reuse check | | |
| Cost/latency accounting | | |

## Claim-Safety Boundary

- What this run can support:
- What this run cannot support:
- Domain-transfer warning:
- Operational-use warning:

## Failure Log

| Attempt | Role | Failure mode | Evidence | Decision |
| --- | --- | --- | --- | --- |
| | | | | |
