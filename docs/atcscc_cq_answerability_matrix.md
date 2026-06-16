# ATCSCC CQ Answerability Matrix

Status: design note for CQ refinement, evaluation protocol updates, and future
method figures. This document records a peer-slide-inspired matrix pattern. It
is not experiment evidence by itself.

Source note: the matrix pattern was inspired by PPT material shared by Emre Cem
Elevis, especially the correctness-question situation-by-phase matrix slide.
The ATCSCC matrix below is a project-specific adaptation and should be cited as
design inspiration, not as empirical evidence for this repository.

## Purpose

The ATCSCC source family is semi-structured and advisory-type dependent. A
Ground Stop, Ground Delay Program, Route advisory, AFP, CTOP, and Other
advisory do not expose the same fields. Therefore, missing information should
not always be scored as an extraction failure. Some fields are mandatory for a
given advisory type, some are only conditionally observable, and some should
produce no claim.

The answerability matrix defines this distinction before scoring:

> A field or competency question is evaluated only against the advisory types
> where the source is expected to support that claim.

## Legend

| Symbol | Meaning | Evaluation interpretation |
| --- | --- | --- |
| yes | Expected answerable | Missing or unsupported extraction can count as recall, correctness, or evidence-support failure. |
| partial | Conditionally or partially answerable | Missing data may be acceptable if the source lacks the field; generated claims require evidence. |
| no | No claim expected | Any generated value should be treated as an overclaim or unsupported-field hallucination unless explicitly justified by the source. |

## Draft Matrix

This matrix is intentionally compact. It should be refined against the reviewed
ATCSCC corpus and source parser outputs before becoming a hard evaluation
contract.

| CQ / field family | Ground Stop | Ground Delay Program | Route advisory | Airspace Flow Program | CTOP | Other |
| --- | --- | --- | --- | --- | --- | --- |
| Advisory identifier and advisory type | yes | yes | yes | yes | yes | yes |
| Affected airport, ARTCC, fix, or NAS element | yes | yes | partial | partial | partial | partial |
| Initiative or restriction type | yes | yes | yes | yes | yes | partial |
| Start time, end time, or active window | yes | yes | partial | partial | partial | partial |
| Cause or impacting condition | yes | yes | partial | partial | partial | partial |
| Scope or impact description | yes | yes | partial | partial | partial | partial |
| Route, reroute, or path details | no | no | yes | partial | yes | no |
| Program parameters such as delay, rate, or scope | partial | yes | no | partial | partial | no |
| Status, update, cancellation, or supersession signal | partial | partial | partial | partial | partial | partial |
| Evidence span for each generated fact | yes | yes | yes | yes | yes | yes |
| Schema/profile validity | yes | yes | yes | yes | yes | yes |
| Operational recommendation or live decision authority | no | no | no | no | no | no |

## Evaluation Consequences

The matrix changes how completeness and correctness should be interpreted.

1. **Task-relative completeness** should be measured over expected-answerable
   fields, not over a universal field list. A Route advisory should be evaluated
   for route details; a Ground Stop should not be penalized for lacking reroute
   information.
2. **Partial answerability** should be reported separately. These cells are
   useful for profile-gap analysis, source-format variation, and abstention
   behavior, but they should not be collapsed into mandatory-field recall.
3. **No-claim cells** should become an overclaim diagnostic. If an LLM generates
   route details for a Ground Stop without source evidence, that is a false
   positive even if the text looks plausible.
4. **Evidence spans are mandatory for generated facts** across all advisory
   types. A field can be optional, but an emitted claim still needs evidence.
5. **Operational recommendations remain out of scope** across the matrix. The
   project evaluates retrospective advisory-event extraction and QA, not live
   operational decision support.

## Candidate Metrics

| Metric | Definition | Why it helps |
| --- | --- | --- |
| Expected-field recall | Fraction of `yes` cells correctly populated with evidence-supported values. | Measures task-relative completeness without penalizing irrelevant fields. |
| Conditional-field support rate | Fraction of populated `partial` cells that include adequate evidence. | Measures whether optional extraction is grounded when attempted. |
| No-claim false positive rate | Fraction of `no` cells where the system generated a claim. | Detects hallucinated or out-of-scope fields. |
| Evidence-backed field precision | Fraction of emitted field values with source-contained evidence spans. | Separates surface extraction from provenance support. |
| Abstention correctness | Fraction of unanswerable or unsupported cells where the system abstains. | Rewards not inventing claims. |
| Matrix coverage | Fraction of advisory-type / CQ-family cells represented in the reviewed corpus. | Shows which parts of the matrix are actually tested. |

## Relation To The 12 Primary CQs

The primary CQ set should stay compact. The answerability matrix does not mean
the project needs dozens of new headline CQs. Instead, the 12 primary CQs define
the main information needs, and this matrix defines where each CQ should be
evaluated.

This gives a defensible explanation for keeping the CQ count small:

> The thesis uses a compact primary CQ set as the backbone of the information
> need. Advisory-type-specific applicability is handled by an answerability
> matrix, so completeness is measured against source-observable expectations
> rather than a universal all-fields checklist.

## Implementation Support Plan

| Step | Target artifact | Notes |
| --- | --- | --- |
| Encode matrix as data | `data/evaluation/nasa_atmonto/atcscc_cq_answerability_matrix.json` or equivalent | Keep it small and reviewed before using it as a scoring contract. |
| Link CQs to field families | CQ artifact or schema/profile metadata | Each CQ should declare mandatory, conditional, and no-claim advisory types. |
| Add scoring diagnostics | CQ evaluation and S7 answer reports | Report expected-field recall, no-claim false positives, and abstention correctness. |
| Add dashboard summary | Thesis dashboard | Show matrix coverage so reviewers know which cells are supported by data. |
| Update method figure | Architecture / evaluation figure | Use a small matrix inset to explain task-relative completeness. |

## Thesis-Ready Wording

Use this wording in the Method or Evaluation chapter:

> Because ATCSCC advisory types expose different source fields, we evaluate CQs
> through an advisory-type answerability matrix. The matrix marks each CQ family
> as expected, conditional, or out of scope for each advisory type. Completeness
> is therefore measured over source-observable expectations, while unsupported
> claims in out-of-scope cells are counted as overclaims.

Avoid wording such as:

- "Every advisory should contain every schema field."
- "Missing route details always indicate extraction failure."
- "The matrix proves the schema is complete."
- "No-claim fields are irrelevant." They are important for hallucination and
  abstention evaluation.
