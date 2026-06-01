# ATMONTO / ATCSCC Experiment Direction Research Protocol

## Material Passport

- Material ID: `atmonto_atcscc_experiment_direction_v1`
- Material type: `experiment_plan`
- Status: `active_protocol`
- Generated: `2026-06-01`
- Scope: near-term aviation experiment using FAA ATCSCC advisories and a NASA ATMONTO-derived schema / validator profile.
- Non-scope: SAF, hydrogen, airport energy, PHAK, operational safety deployment, and general aviation KG completion.
- Primary local evidence:
  - `reports/stages/nasa_atmonto_formal_experiment_scoring.md`
  - `reports/stages/nasa_atmonto_formal_experiment_remediation_plan.md`
  - `reports/stages/sota_data_source_format_processing_review.md`
  - `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- External evidence base: Consensus-fetched records listed in the Literature Evidence Table.

## Executive Decision

Keep FAA ATCSCC advisories as the primary experimental data source. Do not replace them with PDFs.

The corrected thesis experiment should be framed as:

> FAA ATCSCC advisory event-KG extraction under an ATMONTO-derived schema and validator profile.

PDFs should be added as a secondary reference-grounding source family, not as a competing event-extraction dataset. NASA ATMONTO remains a schema / ontology profile and source of class-property definitions, not a ground-truth KG. NASR and FAA reference data remain canonicalization layers, not event-semantics gold.

The completed run now includes the corrected event-extraction stage:

- `S1b_llm_canonicalized`: fair canonicalized baseline from raw S1 facts.
- `S4_hybrid_backbone_enrichment`: S0 deterministic backbone plus S3/S4 semantic enrichment with validator and evidence gate.

The result changes the near-term status: the ATCSCC event-extraction experiment is now thesis-usable as a corrected KG-construction result. PDF reference grounding and GraphRAG retrieval / answer evaluation remain separate follow-up stages.

## Motivation / Thesis Story

The story is not "LLMs can build a complete aviation KG." That would overclaim.

The defensible motivation is:

1. Aviation operational text often exists as semi-structured advisories, procedure text, terminology documents, and reference datasets.
2. LLM-only extraction can produce plausible facts, but those facts are hard to use unless they are canonicalized into an ontology/profile and validated against evidence.
3. FAA ATCSCC advisories are a good narrow testbed because they contain real traffic-management events, stable identifiers and timestamps, and semantic fields such as reason, status, affected facility, route, and comments.
4. NASA ATMONTO supplies a relevant aviation schema vocabulary, but it does not provide gold ABox facts for the sampled advisories.
5. The scientific contribution is therefore a bounded pipeline study: deterministic parsing, ontology-guided semantic enrichment, canonicalization, validation, and layered KG / GraphRAG evaluation.

This gives the paper a clean narrative:

> In semi-structured aviation advisories, deterministic extraction is strong for explicit fields, while ontology-guided LLM components are useful for selected semantic predicates only after canonicalization and validation. The result motivates a hybrid KG construction pipeline rather than a pure LLM or pure ontology approach.

## Research Questions

**RQ1: Data-source suitability**

Are FAA ATCSCC advisories a defensible primary source family for an aviation ontology-guided KG extraction experiment?

Expected answer: yes, if claims are limited to ATCSCC advisory event extraction and the source snapshot is frozen.

**RQ2: Canonicalization bridge**

Does post-hoc canonicalization turn raw ontology-free LLM output into a fair, scoreable baseline?

Observed answer: yes, but with limited recall. `S1b_llm_canonicalized` produced 454 mapped candidate facts, 185 accepted facts, schema violation 0.593, and target-schema F1 0.227. This is a fairer baseline than raw S1, whose direct ATMONTO scoring is invalid.

**RQ3: Hybrid extraction**

Does an S0 backbone plus semantic enrichment outperform pure deterministic extraction on selected semantic predicates while preserving structured-field quality?

Observed answer: yes for this frozen ATCSCC set. `S4_hybrid_backbone_enrichment` reached overall F1 0.739 versus S0's 0.764, but improved selected semantic macro-F1 from 0.143 to 0.500 while preserving deterministic-field macro-F1 at 0.878.

**RQ4: PDF/reference grounding**

Can FAA / NASA PDFs improve schema, terminology, and explanation grounding without contaminating ATCSCC event-F1?

Expected answer: later PDF pilot, separate metric table.

**RQ5: GraphRAG evaluation**

Can the accepted event KG and reference passages improve retrieval and answer grounding?

Expected answer: not yet tested; requires a separate retrieval / answer evaluation layer after S4 exists.

## Hypotheses And Falsification Gates

| Hypothesis | Success criterion | Falsification / stop condition |
| --- | --- | --- |
| H1: ATCSCC is a suitable primary source family | 100 reviewed records remain source-grounded, reproducible, and profile-contained. | Source snapshot cannot be reproduced, or the majority of gold facts require external reference documents rather than advisory text. |
| H2: S1b fixes the unfair S1 all-zero comparison | `S1b` has non-zero accepted facts and lower schema violation than raw `S1`, while reporting canonicalization yield and reject taxonomy. | `S1b` remains near-zero after transparent mapping, or mapping depends on gold labels. |
| H3: S4 is the main candidate system | S4 preserves S0 deterministic-field F1 within 0.01 and improves selected semantic predicate macro-F1 over S0. | S4 overwrites/pollutes header fields, or semantic gains disappear after evidence gating. |
| H4: PDF grounding is useful but separate | PDF pilot reaches high evidence containment and page/section provenance quality on definition / term / procedure tasks. | PDF facts are mixed into ATCSCC event F1 or used to assert event truth. |
| H5: GraphRAG must be layered | Retrieval recall, citation support, faithfulness, and answer correctness are reported separately from KG construction F1. | GraphRAG answer quality is used as a substitute for extraction accuracy. |

## Variables And Controls

### Independent variables

- System architecture: `S0`, raw `S1`, `S1b`, `S2`, `S3`, `S4`.
- Schema exposure: none, ontology-free labels, ATMONTO schema slice, canonicalization layer, validator gate.
- Source family: ATCSCC event text, FAA / NASA PDF reference text.
- Evidence policy: no evidence gate, exact span gate, validator plus quarantine.

### Dependent variables

- JSON adherence.
- Candidate fact count.
- Accepted / rejected fact count.
- Structural acceptance and schema violation rate.
- Triple precision, recall, F1.
- Predicate macro-F1 and per-predicate support.
- Canonicalization yield and reject reason distribution.
- Evidence-span support rate.
- Repair precision and repair-induced false positive rate.
- For GraphRAG only: retrieval recall@k, citation support rate, answer faithfulness, unsupported claim rate, answer correctness.

### Controls

- Same frozen 100 reviewed ATCSCC records for event-extraction comparisons.
- Same ATMONTO-derived schema profile version.
- Same NASR / FAA entity reference cycle when entity canonicalization is evaluated.
- Same scoring normalizer and evidence-span policy across systems.
- No development examples drawn from the held-out 100 scoring records.
- ATMONTO and reference PDFs cannot be treated as event-truth gold.

## Experiment Matrix

| Stage | Status | Data | Systems / tasks | Main metrics | Claim unlocked |
| --- | --- | --- | --- | --- | --- |
| E0 diagnostic formal run | Completed | 100 reviewed ATCSCC advisories | `S0`, raw `S1`, `S2`, `S3` | schema violation, P/R/F1, repair success, rejection taxonomy | Feasibility and diagnosis only |
| E1 corrected event extraction | Completed | Same 100 ATCSCC advisories | `S1b`, `S4` | accepted ratio, schema violation, triple F1, predicate macro-F1 | S1b provides a fair canonicalized baseline; S4 improves selected semantics while preserving deterministic fields |
| E2 error taxonomy | Partially completed | Existing rejections and new S1b/S4 rejections | reject categories and profile gaps | distribution and actionability | Whether failures are engineering bugs or profile gaps |
| E3 PDF reference pilot | Pending | PCG, JO 7110.65BB, ATMONTO PDF | definition / alias / procedure / schema support extraction | evidence containment, section/page provenance, term mapping | Whether PDFs support grounding and explanation |
| E4 KG-RAG retrieval | Pending | accepted S4 KG plus reference passages | entity / triple / advisory retrieval | recall@k, MRR, path recall | Whether graph structure helps retrieval |
| E5 answer grounding | Pending | E4 retrieval output | QA / explanation answers | faithfulness, citation support, correctness | Whether GraphRAG improves answers |

## Current Completion Assessment

The project now has a completed corrected ATCSCC event-extraction experiment. It is still not a full GraphRAG paper until retrieval and answer evaluation are separately implemented.

| Layer | Completion | Evidence | Remaining work |
| --- | ---: | --- | --- |
| Frozen ATCSCC gold set | 100% | 100 reviewed records, scoring-ready gold. | Preserve source snapshot and hashes. |
| Diagnostic S0/S1/S2/S3 run | 100% | Generated scoring report and tests. | Reinterpret raw S1 as diagnostic, not fair baseline. |
| Methodology repair plan | 95% | SOTA data-source review, remediation plan, and corrected protocol report exist. | Polish claim wording and move selected text into thesis. |
| Corrected S1b/S4 event experiment | 100% | S1b/S4 predictions and scoring report generated; focused tests pass. | Treat as current ATCSCC main result, with limitations. |
| PDF reference pilot | 20% | Candidate PDFs identified and boundary defined. | Extract pilot items, define gold/eval, run separate metrics. |
| GraphRAG evaluation | 10% | Evaluation dimensions selected. | Build retrieval / answer tasks after accepted S4 KG exists. |

Practical thesis readiness estimate:

- For an ATCSCC event-KG extraction results chapter: roughly 85-90% ready.
- For a corrected main experiment claim under an ATMONTO validator profile: roughly 80-85% ready, pending prose polish and threat-to-validity wording.
- For full KG-RAG / GraphRAG claims: below 40%; those claims should remain future work unless E4/E5 are completed.

## Why ATCSCC, Not PDF, As Main Data Source?

ATCSCC should be primary because it provides event-instance facts. The task is event KG extraction, and the gold facts must come from the event text itself.

PDFs are valuable but they mostly provide definitions, procedures, terminology, and schema justification. They can say what a term means; they cannot prove that a specific advisory had reason `WEATHER` or status `RQD` unless the advisory text itself supports that fact.

| Criterion | ATCSCC advisories | PDFs |
| --- | --- | --- |
| Event-instance truth | Strong | Weak |
| Structured fields for deterministic baseline | Strong | Weak / variable |
| Fits ATMONTO TMI/advisory slice | Strong | Medium |
| Supports manual closed-profile gold | Strong | Medium |
| Supports terminology / schema grounding | Medium | Strong |
| Supports GraphRAG reference answers | Medium | Strong |
| Suitable as main F1 extraction source | Yes | No, unless a separate PDF extraction task is defined |

## Literature Evidence Table

| Evidence | What it supports here | Boundary |
| --- | --- | --- |
| [Extract, Define, Canonicalize](https://consensus.app/papers/extract-define-canonicalize-an-llmbased-framework-for-zhang-soh/711b33c15bfc562d9137b07050be7666/?utm_source=chatgpt), Zhang and Soh, 2024 | Split raw open extraction from target-schema canonicalization; justifies `S1 -> S1b`. | Do not copy its self-generated schema setting; use ATMONTO profile. |
| [Text2KGBench](https://consensus.app/papers/text2kgbench-a-benchmark-for-ontologydriven-knowledge-mihindukulasooriya-tiwari/b24be0d0ff9f52eebfa7a23833492952/?utm_source=chatgpt), Mihindukulasooriya et al., 2023 | Ontology-driven text-to-KG evaluation should measure fact extraction, ontology conformance, and hallucinations. | Benchmark domains are not aviation. |
| [Ontology-guided KGC from Maintenance Short Texts](https://consensus.app/papers/ontologyguided-knowledge-graph-construction-from-cauter-yakovets/28494e5fc0905fc598416a17f098c8c0/?utm_source=chatgpt), Cauter and Yakovets, 2024 | Strong analogy for short domain-specific records and few reviewed examples. | Maintenance text is not ATCSCC. |
| [JSONSchemaBench](https://consensus.app/papers/jsonschemabench-a-rigorous-benchmark-of-structured-geng-cooper/ca5abcbe21085a9dbcae79f8c52bcf9a/?utm_source=chatgpt), Geng et al., 2025 | Structured output compliance needs systematic evaluation, not just "valid JSON" reporting. | JSON schema compliance is not semantic truth. |
| [Structured information extraction from scientific text](https://consensus.app/papers/structured-information-extraction-from-scientific-text-dagdelen-dunn/075e3f5a3be0575d99f30dc34440d323/?utm_source=chatgpt), Dagdelen et al., 2024 | Supports PDF / paragraph extraction as a separate structured IE task. | Materials science domain, not aviation. |
| [Schema-Driven IE from Heterogeneous Tables](https://consensus.app/papers/schemadriven-information-extraction-from-heterogeneous-bai-kang/dd3a160b9e1f54a498177d3b0450bf57/?utm_source=chatgpt), Bai et al., 2023 | Human-authored schemas can define small structured extraction tasks over heterogeneous semi-structured sources. | Table extraction differs from advisory extraction. |
| [GraphRAG Survey](https://consensus.app/papers/graph-retrievalaugmented-generation-a-survey-peng-zhu/1b8c5362a3d3538ba1dd90f9b40178f1/?utm_source=chatgpt), Peng et al., 2024 | GraphRAG should be decomposed into indexing, retrieval, and generation layers. | Survey, not an extraction benchmark. |
| [Evaluation of RAG: A Survey](https://consensus.app/papers/evaluation-of-retrievalaugmented-generation-a-survey-yu-gan/861805cd172d534298b77a83a0d83d92/?utm_source=chatgpt), Yu et al., 2024 | Supports separate relevance, accuracy, and faithfulness metrics. | RAG evaluation cannot replace gold KG evaluation. |
| [GraphRAG-Bench](https://consensus.app/papers/graphragbench-challenging-domainspecific-reasoning-for-xiao-dong/622e8b388c575636b2d8f4b7463068c0/?utm_source=chatgpt), Xiao et al., 2025 | Supports holistic GraphRAG pipeline evaluation: construction, retrieval, answer generation, reasoning coherence. | New preprint; use cautiously. |

## arXiv HTML / Full-Text Verification Notes

Where possible, arXiv papers should be verified through the official arXiv HTML
view or an HTML rendering such as ar5iv before extracting experiment-design
details. This is especially useful for dataset tables, workflow diagrams, and
metric definitions that are often missing from abstracts.

EDC full-text check:

- Official arXiv HTML for `2404.03868` reported no available HTML conversion at
  the time of checking.
- The ar5iv HTML rendering was available at
  `https://ar5iv.labs.arxiv.org/html/2404.03868`.
- Full-text details verified from the HTML rendering:
  - EDC evaluates on WebNLG, REBEL, and Wiki-NRE.
  - WebNLG uses 1,165 text-triplet pairs and 159 relation types.
  - REBEL samples 1,000 text-triplet pairs from a much larger test partition and
    induces 200 relation types.
  - Wiki-NRE samples 1,000 text-triplet pairs and induces 45 relation types.
  - Evaluation uses token-based precision, recall, and F1, including Exact,
    Partial, and Strict matching variants.
  - The method separates open extraction, schema definition, post-hoc
    canonicalization, and optional schema-retriever refinement.

Implication for this project:

- The ATCSCC experiment should not score raw schema-free S1 directly against
  ATMONTO. It should report raw drift diagnostics, then score `S1b` after
  canonicalization.
- The 100-record ATCSCC gold set is smaller than EDC's benchmark samples, so
  the thesis should report confidence intervals, per-predicate support, and
  bounded claims rather than broad SOTA comparisons.
- The controlled ATMONTO profile makes this closer to EDC's target-alignment
  setting than to self-generated-schema KG construction.

## Execution Order

1. Use `reports/stages/nasa_atmonto_formal_experiment_scoring.md` as the current corrected ATCSCC result.
2. Move the ATCSCC source rationale, S1/S1b distinction, and S4 hybrid result into the thesis method/results narrative.
3. Define a small PDF reference pilot only as terminology/schema/procedure grounding.
4. Define KG-RAG retrieval and answer tasks only after accepted S4 facts and reference passages are indexed.
5. Keep GraphRAG answer-improvement claims out of the paper until retrieval and answer metrics exist.

## Claim Wording

Recommended thesis claim:

> On a frozen, manually reviewed set of FAA ATCSCC advisories, deterministic extraction provides a strong backbone for explicit structured fields. Ontology-guided LLM extraction is most useful as canonicalized semantic enrichment under an ATMONTO-derived validator profile. Reference PDFs improve terminology and schema grounding, but they should be evaluated as a separate source family rather than as event-truth gold.

Claims to avoid:

- "The system constructs a complete aviation KG."
- "NASA ATMONTO is the ground-truth KG."
- "PDF reference documents validate ATCSCC event facts."
- "LLM-only extraction fails at aviation KG extraction."
- "GraphRAG improves answers" before retrieval and answer metrics are run.
