# Benchmark Design

This project uses PHAK Chapter 4 benchmark labels to evaluate retrieval,
GraphRAG evidence, answer faithfulness, robustness, and insufficient-evidence
abstention as separate layers. The v2 benchmark is a thesis-oriented seed set,
not an externally aviation-expert-certified artifact.

## Benchmark V2

`data/cqs/06_phak_ch4_0.benchmark_v2.gold.json` expands the earlier 35-label
course-project set to 120 labels. It does not replace the existing gold files.

The fixed category distribution is:

| Question type | Count | Purpose |
| --- | ---: | --- |
| `supported_factual` | 40 | Direct factual questions grounded in one source span. |
| `concept_definition` | 15 | Definition or description questions for key Chapter 4 concepts. |
| `relation_causal` | 15 | Questions about causal, proportional, or relational statements. |
| `cross_page` | 10 | Questions requiring evidence from adjacent source pages. |
| `paraphrase` | 10 | Robustness questions with less literal wording. |
| `terminology_variation` | 10 | Robustness questions using alternate terminology. |
| `insufficient_evidence` | 20 | Safety-boundary questions that should abstain. |

## Label Schema

Each label includes:

- `cq_id`: stable unique benchmark identifier.
- `question`: user-facing question used by retrieval and answer evaluation.
- `question_type`: one of the v2 categories above.
- `tags`: secondary labels such as `supported`, `page_03`, or
  `safety_boundary`.
- `source_document`: `06_phak_ch4_0`.
- `source_page`: evidence page for supported labels, or `-1` for no-answer
  labels.
- `gold_level`: usually `span`; `no_answer` for insufficient-evidence labels.
- `expected_abstention`: `false` for supported labels and `true` for
  insufficient-evidence labels.
- `expected_chunk_ids`: source chunk IDs that contain the evidence.
- `evidence_spans`: exact source-backed spans with page numbers.
- `key_entities`: terms used for KG evidence coverage checks.
- `answer_key`: source-backed answer text or an insufficient-evidence policy
  answer.
- `review`: machine-seeded review status and review notes.

The gold loader intentionally ignores extra fields such as `tags` and `review`
when creating `GoldLabel` objects, so downstream evaluation can consume newer
benchmark files without breaking older interfaces.

## Annotation Rules

Supported labels must cite evidence from the repository source chunks:

- `data/chunks/06_phak_ch4_0.structure_aware.jsonl`
- `data/chunks/06_phak_ch4_0.jsonl`

Evidence span validation normalizes whitespace while preserving casing, then
checks that each span appears in at least one source chunk on the span page. Do
not use external aviation knowledge to fill answer keys for supported labels.

Cross-page labels may include multiple evidence spans. The label `source_page`
uses the first evidence page, while each span keeps its own page number.

## No-Answer Policy

`insufficient_evidence` labels cover operational and safety-boundary cases that
PHAK Chapter 4 alone cannot answer, including live weather, current NOTAMs, ATC
clearances, aircraft-specific V-speeds, POH checklist replacement, emergency
procedures, aircraft-specific weight and balance, and go/no-go decisions.

These labels must use:

- `gold_level`: `no_answer`
- `expected_abstention`: `true`
- `source_page`: `-1`
- empty `expected_chunk_ids`
- empty `evidence_spans`

The expected answer should explain that Chapter 4 provides insufficient evidence
and should defer to current official sources, the aircraft POH/AFM, approved
checklists, ATC instructions, regulations, instructor guidance, and pilot
judgment as applicable.

## Validation And Reporting

Validate the benchmark with:

```bash
uv run aviation-ai cqs validate-benchmark --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json
```

Write the summary report with:

```bash
uv run aviation-ai report benchmark-v2 --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json
```

The summary report writes:

- `reports/stages/benchmark_v2_summary.json`
- `reports/stages/benchmark_v2_summary.md`

## Limitations

The v2 benchmark is larger and more useful for thesis evaluation than the
course-project seed set, but it is still machine-seeded from local source chunks.
It is not human reviewed or aviation-expert certified. LLM-assisted review can
support internal cleanup and cautious thesis wording, while evaluation results
must keep retrieval, KG evidence, answer quality, and abstention metrics
separate.
