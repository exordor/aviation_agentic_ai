# ATCSCC Agentic Artifact Contract

Date: 2026-06-02

Status: starter contract for applying the artifact-driven multi-agent method to
the current NASA ATMONTO / FAA ATCSCC case study. This is a planning artifact,
not a scored experiment result.

Method reference:
`reports/stages/multi_agent_pipeline_method_adaptation.md`

Template:
`templates/agentic_artifact_contract.md`

## Material Passport

- Domain: retrospective FAA ATCSCC advisories.
- Module: ontology-guided KG extraction, validation, retrieval routing, and
  report synthesis.
- Source scope: frozen ATCSCC advisory snapshot and project-approved FAA/NASA
  reference sources.
- Reference ontology/profile: NASA ATMONTO-derived ATCSCC schema/profile.
- Competency questions:
  `reports/stages/nasa_atmonto_competency_questions.md`.
- Query manifest:
  `data/evaluation/nasa_atmonto/atcscc_cq_query_manifest.json`.
- Gold policy: reviewed ATCSCC gold records plus Gold/Silver/Bronze extraction
  policy from existing source/method matrix reports.
- Non-scope: live air-traffic decisions, operational recommendations, complete
  aviation ontology coverage, or unsupported common-sense completion.

## Role Contract

| Role | Allowed inputs | Required output | Stop condition | Escalation condition |
| --- | --- | --- | --- | --- |
| Source Steward | FAA/NASA source inventory reports, frozen advisory snapshot | ATCSCC source brief | All sources are classified as in-scope, support-only, or excluded | Missing source provenance or unclear temporal boundary |
| CQ Designer | 12 primary CQs, advisory gold fields, ATMONTO profile | CQ contract / query manifest update | Every CQ has fields, route label, metric, and failure mode | CQ cannot be answered from frozen evidence or needs live operations |
| Domain Expert / SRD Agent | Source brief, CQs, advisory examples | ATCSCC Semantic Requirements Document | Every required advisory concept/relation maps to CQ IDs | Needed concept has no source support or ATMONTO/profile counterpart |
| Ontology Manager / TIP Agent | SRD, ATMONTO profile, existing system outputs | Technical Implementation Plan | Reuse/extension decisions are explicit for each concept/relation | Proposed extension would redefine ATMONTO ground truth |
| Extraction Planner | TIP, CQ contract, gold policy | Extraction Implementation Plan | Each field has extractor source, evidence rule, and abstention rule | Field requires unsupported inference or unsafe operational claim |
| Extractor / Coder | Extraction plan, source slice, current KG/profile | Candidate facts or patch | Candidate facts include source ID, span, profile predicate, CQ link | Missing span, out-of-profile predicate, or hallucinated value |
| Schema Validator | Candidate facts, ATMONTO/profile constraints | Validation findings | Parse, datatype, class, domain/range, and profile checks complete | Validator cannot classify violation or profile gap |
| Evidence Critic | Candidate facts, original advisory span, CQ expectations | Evidence support findings | Each fact is supported, unsupported, ambiguous, or no-source | Support decision requires human adjudication |
| Repair Planner | Validation/evidence findings, candidate facts | Bounded repair plan | Repair action is specific and cycle-limited | Repair would change unsupported facts into guessed facts |
| Graph-Use Planner | CQ manifest, KG health, retrieval baselines | Graph-use plan | Query route is vector, graph, hybrid, deterministic, or abstain | Graph route lacks connected KG support or exceeds cost budget |
| Evaluation Agent | Gold labels, outputs, retrieval results, cost logs | Layered evaluation report | Extraction, validation, graph health, retrieval, answer metrics separated | Metric would mix schema validity with semantic truth |
| Report Synthesizer | All accepted artifacts and failure logs | Claim-safe stage report | Claims cite artifacts and limitations | Claim implies live operations, certification, or universal GraphRAG benefit |

## Required Artifact Chain For S5/S6/S7

Before implementing new agentic systems, create or update these artifacts:

1. `reports/stages/atcscc_source_brief.md`
2. `reports/stages/atcscc_semantic_requirements.md`
3. `reports/stages/atcscc_technical_implementation_plan.md`
4. `reports/stages/atcscc_extraction_plan.md`
5. `reports/stages/atcscc_validation_findings.md`
6. `reports/stages/atcscc_evidence_support_findings.md`
7. `reports/stages/atcscc_repair_plan.md`
8. `reports/stages/atcscc_graph_use_plan.md`

The first implementation can be manual or script-assisted. Automation should
come after the artifact fields stabilize.

## Bounded Iteration Policy

- Maximum repair cycles per item: 2.
- Maximum graph-use route revisions per CQ: 1 after retrieval evidence exists.
- Repair cannot introduce a new fact without an explicit source span.
- Unsupported or ambiguous facts are quarantined rather than completed from
  common sense.
- Any profile extension proposal must be reported as a profile gap, not as
  existing ATMONTO truth.

## Evaluation Hooks

| Check | Mode | Artifact field |
| --- | --- | --- |
| Syntax/schema validity | deterministic | validation finding |
| Evidence containment | deterministic | source span and excerpt |
| Evidence support | human-supervised or LLM-assisted | support label and rationale |
| CQ alignment | deterministic plus review | CQ IDs |
| Profile gap detection | validator plus review | profile gap ID |
| Redundancy/reuse check | deterministic plus review | reused class/property IDs |
| Cost/latency accounting | deterministic | run metadata |

## Claim-Safety Boundary

This contract can support claims about a reusable, artifact-driven method for
retrospective ontology-guided KG extraction and GraphRAG evaluation. It cannot
support claims about live ATC use, certified operational decision support,
complete aviation ontology coverage, or general GraphRAG superiority.

## First Next Step

Draft `reports/stages/atcscc_semantic_requirements.md` from the 12 CQs and the
reviewed ATCSCC gold fields. That artifact should define the concepts,
relations, temporal fields, provenance requirements, abstention cases, and
profile gaps that S5 must respect.
