# NASA ATMONTO Reviewer Defense Audit

## Scope

This report converts the parallel reviewer-style audit into explicit claim gates and defensive experiment/report improvements.

- SOTA audit status: `sota_goal_audit_created`
- Completion claim: `internal_diagnostic_package_complete`
- Completion scope: `internal_diagnostic`
- Internal diagnostic gate passed: `True`
- Human answer review completed: `False`
- Expert certification completed: `False`
- S7 retrieval labels: 317
- S7 LLM selected cases: 60
- S7 LLM cases per template/mode: 5
- Automated diagnostic cases: 60

## Main Guardrail

This thesis presents a retrospective, source-bounded study of schema-constrained Agentic KG-RAG for FAA ATCSCC advisories. A lightweight NASA ATMONTO-derived application schema constrains advisory event extraction; the research contribution is evidence-linked event extraction, agentic validation/refinement, and source-bounded KG-RAG evaluation. The strongest claims are structural schema conformance, evidence traceability, benchmark-specific retrieval and answer diagnostics, and failure-boundary analysis. Automated consistency diagnostics are an internal error-discovery layer, not human review, expert certification, domain-general proof, or operational aviation validation.

## Claim Scope Gates

| Scope | Passed | Status | Blocked by |
| --- | --- | --- | --- |
| `internal_diagnostic_package` | `True` | Complete for internal thesis diagnostics. | none |
| `retrospective_sota_comparable_case_study` | `True` | Defensible only as a source-bounded retrospective case study. | none |
| `human_answer_quality_review` | `False` | Human answer review remains incomplete. | reviewed S7 answer CSV is not complete |
| `external_expert_certification` | `False` | External aviation/domain expert certification remains incomplete. | no external expert certification artifact |
| `operational_decision_support` | `False` | Out of scope: retrospective educational/research evaluation only. | no live operational validation, not an FAA/ATC decision-support system |

## Formal KG Extraction Snapshot

| System | Accepted facts | Rejected facts | Precision | Recall | F1 | Structural acceptance |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `S2_llm_schema_slice` | 584 | 124 | 0.2062 | 0.1866 | 0.1959 | 0.8249 |
| `S3_llm_schema_slice_validator_repair` | 355 | 41 | 0.2423 | 0.1337 | 0.1723 | 0.8965 |
| `S4_hybrid_backbone_enrichment` | 686 | 0 | 0.7168 | 0.7636 | 0.7395 | 1.0000 |

## Retrieval And Answer Diagnostic Snapshot

| Mode | Source | Cases | Answer F1 | Answer correctness | Citation recall | Target hit | Context tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `token_matched_live_tfidf_vector` | retrieval | 317 | 0.8235 | n/a | n/a | 1.0000 | 38.9600 |
| `token_matched_dense_embedding_vector` | retrieval | 317 | 0.5166 | n/a | n/a | 0.5710 | 38.9600 |
| `routed_token_matched_live_tfidf_graphrag` | retrieval | 317 | 0.8534 | n/a | n/a | 1.0000 | 38.9600 |
| `routed_token_matched_dense_graphrag` | retrieval | 317 | 0.6105 | n/a | n/a | 0.9685 | 38.9600 |
| `routed_token_matched_dense_graphrag` | LLM selected sample | 30 | n/a | 0.9333 | 0.5945 | n/a | 33.0300 |
| `routed_token_matched_live_tfidf_graphrag` | LLM selected sample | 30 | n/a | 0.9667 | 0.6084 | n/a | 33.0300 |

## Reviewer Findings And Defensive Improvements

| ID | Severity | Reviewer angle | Risk | Defensive action | Claim boundary |
| --- | --- | --- | --- | --- | --- |
| `D1` | `high` | methodology / claim gate | Automated checks may be mistaken for human answer review. | Split completion into internal diagnostic, human review, expert certification, and operational scopes. | Current scope is `internal_diagnostic`. |
| `D2` | `high` | GraphRAG answer evaluation | The selected 60-case LLM sample can be overread as the full S7 benchmark. | Report 317 retrieval labels separately from the selected 60-case LLM diagnostic, with per-mode sample counts. | LLM metrics are selected-sample diagnostics, not full-label coverage. |
| `D3` | `high` | schema-guided event extraction / KG evidence | Schema conformance can be conflated with semantic correctness. | Keep structural acceptance, semantic precision/recall/F1, and evidence support as separate columns. | Schema validity is not equivalent to domain truth. |
| `D4` | `medium` | citation and evidence support | Citation precision alone hides incomplete evidence coverage. | Report citation recall and describe future span-level adequacy checks. | Citation validity does not prove full source-span support. |
| `D5` | `medium` | baseline fairness | GraphRAG gains may depend on route, top-k, or token budget choices. | Separate primary token-matched comparisons from diagnostic dense/vector sensitivity modes. | Results support source-bounded routed GraphRAG diagnostics. |
| `D6` | `medium` | reproducibility | LLM provider, prompt, and selected-case provenance can be underspecified. | Surface model, sample counts, prompt boundary, and required regeneration artifacts in the report. | Reproducibility is artifact-level unless raw provider traces are added. |

## No-Go Claims

- Do not treat the lightweight ATCSCC application schema as a complete aviation ontology.
- Do not claim that automated diagnostics replace human or expert answer review.
- Do not claim operational FAA/ATC decision-support readiness.
- Do not claim domain-general validation from the bounded ATCSCC plus NASA BGA pilot.
- Do not collapse schema conformance into semantic correctness.
- Do not present selected 60-case LLM diagnostics as the full 317-label answer benchmark.
