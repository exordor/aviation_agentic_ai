# NASA ATMONTO Minimal Loop Validation

- Source catalog: `data/ontology/curated/nasa_atmonto_schema_catalog.json`
- Schema slice: `data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json`
- Extraction schema: `data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json`
- Candidate facts: `data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_candidates.jsonl`
- Validated facts: `data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_validated.jsonl`
- ATCSCC records processed: 718
- Candidate fact count: 4429
- Accepted fact count: 4141
- Rejected fact count: 288
- Repaired accepted fact count: 4141

## Status Counts

- `rejected_schema`: 288
- `repaired_accepted`: 4141

## Error Counts

- `allowed_value_violation`: 22
- `domain_violation`: 132
- `range_violation`: 134

## Boundary

- This validates schema adherence, identifier repair, datatype coercion, and evidence anchoring.
- Accepted facts remain `bronze_until_reviewed`; this is not an operational truth or safety claim.
- Rejections identify schema/surface-form mismatches that require either extraction changes or explicit profile extensions.
