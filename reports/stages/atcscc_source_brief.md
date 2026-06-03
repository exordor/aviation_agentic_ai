# ATCSCC Source Brief

## Source Family

- Domain corpus: retrospective FAA ATCSCC advisory records only.
- Boundary: Retrospective FAA ATCSCC advisory extraction only; no live operational use.
- Reviewed gold artifact: `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- CQ manifest: `data/evaluation/nasa_atmonto/atcscc_cq_query_manifest.json`
- Reference schema/profile: `data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json`
- Support sources may explain terms, but they do not override the frozen advisory evidence.

## Included Source Artifacts

| Artifact | Path | Exists |
| --- | --- | --- |
| `gold` | `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl` | `True` |
| `scoring` | `reports/stages/nasa_atmonto_formal_experiment_scoring.json` | `True` |
| `semantic_groups` | `reports/stages/nasa_atmonto_gold_semantic_groups.json` | `True` |
| `rejection_adjudication` | `reports/stages/nasa_atmonto_rejection_adjudication.json` | `True` |
| `cq_manifest` | `data/evaluation/nasa_atmonto/atcscc_cq_query_manifest.json` | `True` |
| `prediction_validation` | `reports/stages/nasa_atmonto_prediction_output_validation.json` | `True` |
| `extraction_schema` | `data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json` | `True` |

## Non-Scope

- Live air-traffic management decisions.
- Complete NASA ATMONTO coverage beyond the ATCSCC application profile.
- Facts inferred from aviation common sense without advisory evidence.
