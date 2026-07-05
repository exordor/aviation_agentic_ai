# KG Extraction Comparison

- Run ID: `kg-extraction-comparison-20260519T044358Z`
- Scope: artifact-level comparison; no default live KG rebuild.

| Strategy | Triples | Valid triples | Unsupported | Provenance complete | Duplicates | Key entity coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fixed_window | 172 | 172 | 0 | 1.0 | 41 | 0.8286 |
| structure_aware | 448 | 448 | 0 | 1.0 | 107 | 0.8571 |

## Interpretation

Structure-aware extraction produced more validated triples; judge this gain against duplicate count, key-entity coverage, and cost before treating it as higher-quality evidence.
