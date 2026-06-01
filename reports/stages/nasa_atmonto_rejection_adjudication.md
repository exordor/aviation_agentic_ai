# NASA ATMONTO Rejection Adjudication

- Input: `reports/stages/nasa_atmonto_rejection_error_analysis.json`
- Rejected facts: 288
- Grouped facts: 288
- Property-level complete: `True`
- Pending manual-review-only facts: 0

## Final Decision Counts By Fact

- `extractor_bug`: 13
- `profile_gap`: 275

## Property-Level Decisions

| Predicate | Errors | Count | Initial decision | Final decision | Confidence |
| --- | --- | ---: | --- | --- | --- |
| `controlledNASelement` | `range_violation` | 134 | `nasa_atmonto_profile_gap_candidate` | `profile_gap` | `high` |
| `impactingConditionMessage` | `domain_violation` | 132 | `nasa_atmonto_profile_gap_candidate` | `profile_gap` | `high` |
| `extensionProbability` | `allowed_value_violation` | 13 | `extractor_normalization_bug_candidate` | `extractor_bug` | `medium` |
| `impactingCondition` | `allowed_value_violation` | 9 | `nasa_atmonto_profile_gap_candidate` | `profile_gap` | `medium` |

## Decision Rationale

### controlledNASelement / range_violation

- Final decision: `profile_gap`
- Basis: ATCSCC source evidence identifies constrained ARTCC centers, while the runtime NASA ATMONTO profile requires controlledNASelement objects to be atm:TFMcontrolElement. The mismatch is a profile coverage gap, not a surface extraction error.
- Follow-up: Add a reviewed profile bridge or alternate property for ARTCC-controlled NAS elements; keep current facts rejected until that profile change is approved.

### impactingConditionMessage / domain_violation

- Final decision: `profile_gap`
- Basis: Ground Stop advisories carry explicit impacting-condition message text, but the runtime profile only permits impactingConditionMessage on GroundDelayProgramTMI. The extracted text is source-supported; the domain constraint is too narrow for this ATCSCC subset.
- Follow-up: Review a GroundStopTMI domain extension for impactingConditionMessage, or store the message as provenance-only evidence until the profile is extended.

### extensionProbability / allowed_value_violation

- Final decision: `extractor_bug`
- Basis: The source surface value is MODERATE, while the runtime profile accepts LOW, MEDIUM, HIGH, or NONE. This is a normalization gap in the extractor or mapping layer, not a need to broaden the ontology before scoring.
- Follow-up: Add a regression-tested normalization rule MODERATE -> MEDIUM and retain the raw surface value in provenance.

### impactingCondition / allowed_value_violation

- Final decision: `profile_gap`
- Basis: The ATCSCC source explicitly uses STAFFING as an impacting condition, but the runtime NASA ATMONTO enum does not include a staffing category. Mapping it to other would lose a recurring operational distinction.
- Follow-up: Review STAFFING as a profile extension value, or map to other only with the raw staffing value preserved in impactingConditionMessage.

## Boundary

- This artifact finalizes property-level error categories for the 288 pilot rejections. It does not automatically approve profile extensions or convert validator-rejected facts into semantic gold facts.
