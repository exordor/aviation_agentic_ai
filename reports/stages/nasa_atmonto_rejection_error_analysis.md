# NASA ATMONTO Rejection Error Analysis

- Input: `data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_validated.jsonl`
- Rejected facts: 288
- Property/error groups: 4

## Decision Counts By Fact

- `extractor_normalization_bug_candidate`: 13
- `nasa_atmonto_profile_gap_candidate`: 275

## Property-Level Groups

### controlledNASelement / range_violation

- Count: 134
- Decision: `nasa_atmonto_profile_gap_candidate`
- Rationale: ATCSCC constrained facilities include ARTCC center identifiers, but the current runtime slice validates controlledNASelement against TFMcontrolElement. The NASA TBox path does not make nas:ARTCC a TFMcontrolElement in this profile.
- Recommended action: Review whether ATCSCC center facilities should be bridged into the runtime profile as controlled NAS elements, or whether they require a separate property.
- Subject classes: `{"GroundDelayProgramTMI": 16, "ReRouteTMI": 36, "TrafficManagementInitiative": 82}`
- Object classes: `{"ARTCC": 134}`
- Values: `{}`

### impactingConditionMessage / domain_violation

- Count: 132
- Decision: `nasa_atmonto_profile_gap_candidate`
- Rationale: Ground stop advisories contain explicit impacting-condition details, but impactingConditionMessage is currently constrained to GroundDelayProgramTMI.
- Recommended action: Review a profile extension for GroundStopTMI, or keep only impactingCondition and preserve the full source phrase as evidence until reviewed.
- Subject classes: `{"GroundStopTMI": 132}`
- Object classes: `{}`
- Values: `{"EQUIPMENT / OUTAGE": 1, "OTHER / EMERGENCY": 1, "OTHER / OTHER": 13, "OTHER / SECURITY": 1, "STAFFING / STAFFING": 4, "VOLUME / COMPACTED DEMAND": 1, "VOLUME / VOLUME": 1, "WEATHER / THUNDERSTORMS": 105, "WEATHER / WIND": 5}`

### extensionProbability / allowed_value_violation

- Count: 13
- Decision: `extractor_normalization_bug_candidate`
- Rationale: The source uses MODERATE while ATMONTO enumerates LOW, MEDIUM, HIGH, and NONE. This should be normalized to MEDIUM only if the mapping is approved.
- Recommended action: Add a reviewed enum-normalization rule MODERATE -> MEDIUM and keep the raw surface value in provenance.
- Subject classes: `{"ReRouteTMI": 13}`
- Object classes: `{}`
- Values: `{"MODERATE": 13}`

### impactingCondition / allowed_value_violation

- Count: 9
- Decision: `nasa_atmonto_profile_gap_candidate`
- Rationale: ATCSCC uses STAFFING as an impacting condition, but the ATMONTO enum contains equipment, other, runway, volume, and weather.
- Recommended action: Decide whether STAFFING should become a profile extension value or map to other with the raw value retained in impactingConditionMessage.
- Subject classes: `{"GroundDelayProgramTMI": 5, "GroundStopTMI": 4}`
- Object classes: `{}`
- Values: `{"staffing": 9}`

## Boundary

- These decisions are research triage labels.
- Profile-gap candidates require ontology/profile review before becoming accepted extensions.
- Extractor-bug candidates require a regression test before changing extraction behavior.
