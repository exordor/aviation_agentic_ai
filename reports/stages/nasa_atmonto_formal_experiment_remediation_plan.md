# NASA ATMONTO Formal Experiment Remediation Plan

- Status: `methodology_remediation_plan`
- Scope: near-term aviation-domain ATCSCC / NASA ATMONTO experiment repair.
- Non-scope: aviation-energy transition. The external research export at
  `data/papers/deep-research-report2.md` is retained as a long-term research memo,
  not as a reason to pivot the current experiment.

## Inputs Reviewed

### Local experiment artifacts

- Formal scoring report:
  `reports/stages/nasa_atmonto_formal_experiment_scoring.md`
- Formal scoring JSON:
  `reports/stages/nasa_atmonto_formal_experiment_scoring.json`
- Protocol:
  `EXPERIMENTS.md`
- Frozen reviewed gold:
  `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`
- External research export:
  `data/papers/deep-research-report2.md`

### External-methodology checks

Literature checks support the following remediation principles:

- Ontology-guided extraction should use relevant schema context and few-shot
  examples for domain-specific short texts, rather than relying on a purely
  zero-shot prompt.
- Open extraction and target-schema scoring should be separated by a
  canonicalization bridge. The EDC pattern is especially relevant:
  extract first, then define/canonicalize.
- LLMs should not be evaluated only as unconstrained few-shot extractors. For
  this experiment they are better positioned as canonicalizers, semantic
  enrichment modules, evidence checkers, and GraphRAG reasoning components.
- Automatically generated KG facts still need human-in-the-loop evaluation.
- Semi-structured sources should be treated differently from free prose:
  deterministic parsing can be a strong backbone, while LLMs are better used for
  semantic enrichment and normalization gaps.
- Heterogeneous-document KG construction needs document-layout/provenance
  handling in addition to semantic triples, which supports keeping the PDF pilot
  separate from ATCSCC event extraction.

Official-source checks with AnySearch confirmed that:

- FAA ATCSCC advisories are available as official advisory pages and recent
  advisory selection pages.
- FAA NASR 2026-05-14 is an official 28-Day NASR Subscription cycle with README
  and CSV/TXT transition caveats.
- NASA ATMONTO has official NASA data documentation and NASA NTRS technical
  documentation.

## Experiment Boundary

This experiment should be described as a narrow ATCSCC / ATM extraction study,
not as a general aviation KG study.

### NASA ATMONTO boundary

NASA ATMONTO is used here as an external ATM/NAS ontology reference. In the
official NASA documentation, the broader ontology covers ATM-relevant concepts
such as flights, aircraft, airports, airlines, air routes, NAS facilities, air
traffic advisories, and weather phenomena. The current experiment does not use
that whole ontology as a ground-truth KG.

The actual runtime profile is much narrower: an ATCSCC-focused schema slice with
18 classes, 11 object properties, and 11 datatype properties. It centers on
traffic-management initiatives and supporting aviation entities:

- `TrafficManagementInitiative`
- `GroundStopTMI`
- `GroundDelayProgramTMI`
- `ReRouteTMI`
- `AirportSpec`
- `ARTCC`
- `TFMcontrolElement`
- `ReRouteSegment`

The main scored properties are:

- identifiers and times: `advisoryNumber`, `issuedTime`,
  `effectiveStartTime`, `effectiveEndTime`
- NAS / airport control links: `controlledNASelement`,
  `includesAirport`, `includesARTCC`, `withinARTCC`
- TMI semantics: `impactingCondition`, `impactingConditionMessage`,
  `extensionProbability`, `implementationStatus`, `reRouteReason`,
  `reRouteType`, `initiativeComments`

### Question the current experiment can answer

The current experiment can answer:

> Can a NASA ATMONTO-derived ATCSCC schema slice improve structural validity and
> selected semantic extraction quality for retrospective FAA ATCSCC advisory KG
> extraction?

It can also answer narrower diagnostic questions:

- Which ATCSCC advisory fields are better handled by deterministic parsing?
- Which semantic predicates benefit from schema-constrained LLM enrichment?
- Which rejected facts are extractor bugs versus runtime-profile gaps?
- Does validator/repair improve schema conformance without silently creating
  unsupported semantic facts?

### Questions it cannot answer

The current experiment cannot support claims about:

- general aviation-domain KG extraction quality;
- operational flight planning, dispatch, ATC, or safety decisions;
- complete NAS reference-data correctness;
- fuel, SAF, hydrogen, airport-energy, accident-report, or aircraft-design
  ontology coverage;
- whether NASA ATMONTO itself is a complete or current operational standard.

### Data used in the previous run

The previous run used FAA ATCSCC advisory records, not a textbook, accident
corpus, or open-ended aviation document collection. The sampled source records
come from:

- `data/processed/nasa_atmonto/aligned/2026-05-14/atcscc_advisories.jsonl`
- 100 sampled advisories in
  `data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json`
- selected advisory dates from `2026-05-14` through `2026-05-20`

The sample was stratified by rejected-candidate exposure, candidate TMI class,
and source advisory date. Candidate subject classes were:

- `GroundDelayProgramTMI`: 16 records
- `GroundStopTMI`: 21 records
- `ReRouteTMI`: 23 records
- `TrafficManagementInitiative`: 40 records

## PDF Source-Family Extension

Adding PDF sources is recommended, but it should be framed as a second source
family for cross-source stress testing. Do not mix ATCSCC advisories and PDF
manual paragraphs into one undifferentiated score table.

### Why add PDFs

The current ATCSCC source family is semi-structured:

- short advisory records;
- visible advisory number/date headers;
- recurring TMI templates;
- many deterministic fields;
- good fit for S0 rule extraction.

The downloaded PDFs create a useful contrast:

- longer paragraphs;
- section hierarchy, tables, definitions, and procedure prose;
- less stable sentence boundaries after PDF extraction;
- stronger need for section-aware chunking and exact evidence spans;
- better fit for definition, terminology, procedure, and reference-evidence
  extraction rather than event-instance extraction.

This lets the thesis ask a stronger but still bounded question:

> Do ontology constraints and evidence-span validation behave differently on
> semi-structured ATCSCC advisories versus unstructured/long-form FAA and NASA
> PDF reference texts?

### Candidate local PDFs

Use the already-downloaded PDFs as follows:

| Candidate PDF | Local path | Recommended role | Boundary |
| --- | --- | --- | --- |
| FAA Pilot/Controller Glossary | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/PCG_Bsc_w_Chg_1_and_2_dtd_1-22-26.pdf` | Primary PDF terminology corpus. Extract definitions, aliases, and lexical anchors for terms found in ATCSCC advisories. | Not an ontology and not event data. |
| FAA JO 7110.65BB Air Traffic Control | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/7110.65BB_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf` | Procedure/phraseology evidence corpus for selected ATC/TMI concepts. | Do not turn procedure text into live operational advice. |
| FAA AIM | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/AIM_Basic_w_Chg_1_and_2_dtd_1-22-26.pdf` | Optional broader aviation reference corpus for selected sections only. | Too broad for the first rerun; sample narrowly. |
| NASA ATMONTO technical documentation | `data/papers/ntrs_ontology_selection/20170006095_nasa_air_traffic_management_ontology.pdf` | Ontology documentation and term-boundary evidence. | Use as schema documentation, not as extraction target for operational facts. |
| NASA semantic integration / querying paper | `data/papers/ntrs_ontology_selection/20190000452_nasa_atm_ontology_semantic_integration_querying.pdf` | Methodology and source-selection evidence. | Related-work evidence, not ABox gold. |
| NASA integrated ATM data semantic representation | `data/papers/ntrs_ontology_selection/20160007964_semantic_representation_integrated_atm_data.pdf` | Related-work evidence for heterogeneous ATM data integration. | Literature layer, not event extraction gold. |

Do not reuse `data/raw/06_phak_ch4_0.pdf` for this corrected ATMONTO rerun
unless it is explicitly labeled as a historical PDF baseline. The immediate
repair should stay on ATCSCC plus ATMONTO/FAA/NASA ATM reference PDFs.

### PDF task design

Create a separate PDF gold/dev slice:

- 20-40 passages from PCG and JO 7110.65BB;
- optional 5-10 passages from NASA ATMONTO technical documentation for schema
  term-boundary evidence;
- every gold item must record `document_id`, `page`, `section`, `span`,
  `source_text`, and `effective_date` where available.

Recommended PDF extraction targets:

- `term_has_definition(term, definition_text)`
- `term_has_alias(term, alias)`
- `procedure_mentions_concept(section, atmonto_concept)`
- `document_defines_or_constrains(term, concept_or_property)`
- `source_supports_mapping(source_span, atmonto_class_or_property)`

Keep these separate from ATCSCC event-instance predicates such as
`advisoryNumber`, `effectiveStartTime`, and `controlledNASelement`.

### PDF pipeline

Use the existing PDF backend policy:

- `hybrid_docling_pymupdf` as the candidate default for structure-aware PDF
  chunking;
- `pymupdf_text_legacy` as a legacy baseline only;
- record page/section/chunk provenance for every extracted fact;
- require exact evidence containment for LLM outputs.

The existing PDF reports already show why this matters:

- `reports/stages/pdf_extraction_comparison.md` shows PyMuPDF heading heuristics
  have low heading precision on prior PDF tests, while Docling/hybrid extraction
  gives better section structure.
- `reports/stages/pdf_backend_chunking_comparison.md` keeps structure quality
  and retrieval quality separate, which should remain the policy for this
  rerun.

### Cross-source comparison design

| Dimension | ATCSCC semi-structured advisories | PDF reference documents |
| --- | --- | --- |
| Primary extraction target | TMI/event ABox facts | definitions, terminology, procedure/evidence relations |
| Best baseline | S0 deterministic parser | section-aware PDF chunking + constrained extraction |
| Main ontology use | ATMONTO schema slice and validator | ATMONTO term mapping, PCG terminology, section provenance |
| Gold unit | advisory record | passage/section/span |
| Directly comparable metrics | JSON adherence, schema conformance, evidence-span validity, canonicalization yield | JSON adherence, schema conformance, evidence-span validity, canonicalization yield |
| Not directly comparable | event F1 vs definition F1 without separate task labels | definition F1 vs event F1 without separate task labels |

The thesis should compare trends, not claim one source type is universally
easier. A safe claim is:

> We evaluate ontology constraints across two aviation source families:
> semi-structured ATCSCC advisories for TMI event extraction and FAA/NASA PDF
> reference documents for terminology/procedure evidence extraction. Metrics are
> reported per source family and joined only at the level of structural
> conformance, evidence grounding, and canonicalization yield.

## Diagnosis

### D1. S1 is not a valid semantic baseline yet

The current `S1_llm_only` output is JSON-adherent and produced 1211 candidate
facts, but all 1211 were rejected by the target ATMONTO profile validator. The
formal score therefore reports:

| System | Candidate facts | Accepted | Schema violation rate | P | R | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `S1_llm_only` | 1211 | 0 | 1.000 | 0.000 | 0.000 | 0.000 |

This is a scoring-interface failure, not evidence that the LLM extracted no
useful information. A schema-free baseline cannot be directly scored as if it
already used the target ontology vocabulary. It needs an explicit
canonicalization bridge before semantic precision/recall/F1 are meaningful.

### D2. The aggregate score hides the useful division of labor

The ATCSCC advisories are semi-structured. The current rule-only system is
therefore strong on deterministic fields, while the schema-constrained LLM is
useful mostly on selected semantic fields.

| Predicate | S0 F1 | S3 F1 | Interpretation |
| --- | ---: | ---: | --- |
| `advisoryNumber` | 0.920 | 0.145 | Keep rule-only backbone. |
| `effectiveStartTime` | 0.929 | 0.047 | Keep rule-only backbone. |
| `effectiveEndTime` | 0.929 | 0.016 | Keep rule-only backbone. |
| `reRouteReason` | 0.000 | 0.514 | Use LLM semantic enrichment. |
| `reRouteType` | 0.000 | 0.588 | Use LLM semantic enrichment. |
| `implementationStatus` | 0.429 | 0.556 | LLM enrichment can help. |

The best next system is not "LLM replaces rules". It is a hybrid:

`S0 deterministic backbone + S3 semantic enrichment + validator gate`.

### D3. H3 is currently overstated

The protocol currently treats `S3 > S1` as evidence for ontology constraints.
That comparison is not meaningful while S1 is all-zero because of target-schema
rejection. The current H3 status should be downgraded to
`inconclusive_due_to_invalid_baseline_bridge`.

### D4. Profile gaps are a separate research outcome

The formal scoring report records 288 reviewed rejections, with 275 marked as
`profile_gap` and 13 as `extractor_bug`. This supports a useful profile-gap
analysis, but it does not mean every profile extension is automatically correct.
Profile extensions should remain proposed changes until they have source
evidence, ontology mapping rationale, and gold-review approval.

## Data Source Corrections

| Layer | Use now | Do not use as |
| --- | --- | --- |
| FAA ATCSCC advisories | Primary extraction corpus for the current aviation experiment. Treat as semi-structured advisory text. | A general aviation textbook corpus or complete NAS truth source. |
| NASA ATMONTO | External TBox, schema-slice, validator/profile vocabulary, and schema-constrained extraction reference. | Ground-truth extracted KG or FAA operational standard. |
| FAA NASR 2026-05-14 | Optional frozen reference-data layer for airport/NAVAID/fix/facility canonicalization and effective-cycle metadata. | Free-text extraction corpus or ontology. |
| FAA reference documents | Optional terminology/evidence layer for definitions and phraseology. | Official KG or direct ontology. |
| AIRM-O / ATMONTO2AIRM | Alignment and interoperability baseline. | Replacement gold truth for ATCSCC extraction. |
| Aviation-energy research memo | Long-term research memo for future SAF/PtL/hydrogen work. | Immediate experiment pivot or replacement for current aviation scoring. |

## SOTA Adaptation For The Rerun

The next rerun should use the literature as an experiment-design correction,
not as a generic prompt-quality argument. The main change is to evaluate the
right system roles: open extraction, schema canonicalization, ontology-guided
extraction, validation, and hybrid merging are different tasks and should not be
collapsed into one score.

| Literature signal | Direct adaptation in this experiment | Expected improvement | Guardrail |
| --- | --- | --- | --- |
| Extract-Define-Canonicalize separates open extraction from post-hoc schema canonicalization. | Split `S1_llm_only` into `S1_raw_open_llm` and `S1b_llm_canonicalized`. | Converts the all-zero S1 result into a diagnosable baseline: raw extraction coverage, mapping yield, and final ATMONTO-profile F1. | Do not report target-schema P/R/F1 for raw S1. |
| Ontology-guided KGC from domain short texts can work with a small set of semantically similar in-context examples. | Add 10-20 reviewed development examples for S2/S3, selected by advisory type and predicate family. | Improves semantic predicates where S0 is weak, especially `reRouteReason`, `reRouteType`, and `implementationStatus`. | Never select examples from the held-out 100-record scoring set. |
| LLMs are often stronger as support modules for reasoning, normalization, and inference than as unsupported few-shot extractors. | Use LLMs for canonicalization, semantic enrichment, evidence checking, and profile-gap explanation instead of making LLM-only the primary thesis system. | Reduces overclaiming and makes S4 the credible candidate system. | Keep a separate LLM-only diagnostic track for comparison. |
| Production ontology-guided extraction pipelines combine pattern rules, ontology snippets, grounding, and corroboration. | Implement `S4_hybrid_backbone_enrichment`: S0 backbone plus S3 semantic candidates plus evidence/validator/corroboration gates. | Preserves deterministic-field performance while adding semantic fields rules cannot recover. | Quarantine conflicts unless the evidence span and schema validator agree. |
| Semi-structured KG creation is a distinct setting from free prose extraction. | Keep ATCSCC advisory extraction and PDF reference extraction as separate source families. | Avoids unfairly scoring event-instance extraction and definition/procedure extraction in one table. | Compare only cross-family metrics such as JSON adherence, evidence validity, schema conformance, and canonicalization yield. |
| Technical-document extraction benefits from structured output and task-specific evaluation. | Add PCG / JO 7110.65BB PDF pilot with passage-level gold and section/page provenance. | Tests whether ontology constraints still help when input is long-form PDF text rather than advisory records. | Do not mix PDF definition F1 with ATCSCC event F1. |
| Human-in-the-loop evaluation remains necessary for automatically constructed KGs. | Freeze a held-out gold set, create a separate dev set, and review profile-extension candidates manually. | Prevents prompt tuning from leaking into gold labels and prevents profile gaps from being silently accepted. | Mark profile extensions as proposals until reviewed. |
| GraphRAG is normally evaluated as graph indexing, graph-guided retrieval, and graph-enhanced generation. | Report graph-construction metrics separately from retrieval and answer-generation metrics. | Lets the thesis claim which layer improved, instead of attributing all gains to "GraphRAG". | No end-to-end answer-quality claim unless graph retrieval and generation are both measured. |

### Concrete rerun changes

1. Create a `dev_examples` split outside the reviewed 100-record score set.
   Each example should include the source advisory, accepted facts, rejected
   facts, and evidence spans. Use these only for S2/S3 prompting and S1b
   canonicalizer calibration.
2. Add `S1_raw_open_llm` output files with generic `entity`, `event`,
   `attribute`, `relation`, `value`, `evidence_span`, and `confidence` fields.
   Record raw coverage, JSON adherence, and evidence containment only.
3. Add `S1b_llm_canonicalized` as a separate mapper from raw facts to the
   ATMONTO profile. Store `source_fact_id`, `mapped_class_or_property`,
   `mapping_confidence`, `mapping_reason`, and `unmapped_reason`.
4. Add `S4_hybrid_backbone_enrichment` with a deterministic precedence policy:
   S0 owns identifiers/times/template fields; S3 owns semantic enrichment only
   when evidence spans are valid and the validator accepts the mapped fact.
5. Add a `grounding_status` for every LLM-derived fact:
   `exact_span`, `paraphrase_supported`, `unsupported`, or `conflict`.
   Only `exact_span` and reviewed `paraphrase_supported` facts should count as
   accepted in the main score.
6. Report metric buckets:
   deterministic fields, semantic TMI fields, canonicalization yield, schema
   violations, evidence validity, profile gaps, and PDF definition/procedure
   facts.
7. Preserve the current all-zero S1 result as a negative control, but label it
   `invalid_direct_schema_scoring` rather than treating it as semantic failure.

## Methodology Review Assimilation

A separate methodology review, run after the initial literature pass, converged
on the same central diagnosis: the original
all-zero `S1_llm_only` score is best treated as an ontology-interface and
canonicalization failure, not as evidence that the LLM extracted no useful
advisory information. The review is useful as an implementation checklist, but
its newly suggested paper leads should be verified before being cited as formal
evidence.

### Accepted review recommendations

The following recommendations are adopted into the rerun design:

1. Treat `S1_raw_open_llm` as a drift diagnostic and `S1b_llm_canonicalized` as
   the comparable baseline.
2. Add a nine-stage pipeline:
   ATCSCC parsing, S0 backbone extraction, schema-slice retrieval, LLM semantic
   extraction, canonicalization, validator gate, repair with trace, graph
   materialization, and layered evaluation.
3. Add `S4_hybrid_backbone_enrichment` as the main candidate architecture:
   deterministic backbone plus semantic enrichment plus validator/evidence gate.
4. Make S4 merge rules explicit:
   - S0 wins for `advisoryNumber`, `issuedTime`, `effectiveStartTime`,
     `effectiveEndTime`, and other explicit header/template fields.
   - S3/S4 may add, but not overwrite, semantic facts such as `reRouteReason`,
     `reRouteType`, and `implementationStatus`.
   - conflicts, unsupported spans, fuzzy-only mappings, and validator-repaired
     facts must be logged with confidence or review status.
5. Keep ATMONTO as an external schema/profile/reference layer and not as a gold
   KG.
6. Keep GraphRAG evaluation layered: KG construction quality, graph retrieval
   quality, and answer faithfulness/completeness should be reported separately.

### Implementation additions from the review

Add or update the implementation plan with these concrete artifacts:

| Artifact | Required content | Purpose |
| --- | --- | --- |
| `schema/atcscc_tmi_profile.yaml` | `class`, `predicate_uri`, `label`, `aliases`, `domain`, `range`, `cardinality`, `allowed_enum`, `normalizer`, `validator_rule`, `example_spans`, `profile_version`, `source_doc`, `commit_hash` | Freezes the ATCSCC scoring profile independently from the full ATMONTO ontology. |
| Predicate canonicalizer | natural labels, aliases, and open-IE predicates to ATMONTO predicate URIs | Turns S1 raw facts into S1b comparable facts. |
| Enum canonicalizer | surface forms such as `required`, `recommended`, `planned`, `FYI` to `RQD`, `RMD`, `PLN`, `FYI`; reroute reason/type surfaces to profile enums | Prevents valid semantic mentions from being rejected as enum drift. |
| Entity canonicalizer | airport/fix/ARTCC/runway/route mentions to FAA/NASR/ATMONTO-compatible IDs where possible | Separates entity-linking failure from predicate extraction failure. |
| Time normalizer | ATCSCC time strings to normalized effective intervals with source timezone/cycle metadata | Keeps deterministic temporal fields from being reinterpreted by the LLM. |
| Repair trace | pre-error, repair action, post-validation status, semantic-change flag, evidence status | Distinguishes repair success from repair-induced false positives. |
| Error taxonomy | format error, predicate drift, class/domain error, range error, enum error, entity canonicalization error, unsupported span, temporal normalization error, duplicate/merge error | Makes failure modes explainable instead of reporting a flat rejection count. |
| GraphRAG retrieval eval | entity recall@k, triple recall@k, path recall, source citation support | Evaluates retrieval separately from extraction. |
| GraphRAG answer eval | faithfulness, answer relevance/completeness, citation support, gold-answer comparison where available | Avoids claiming end-to-end GraphRAG improvement from KG construction metrics alone. |

### Suggested quantitative rerun targets

These are design targets, not guaranteed claims:

- `S4` should preserve S0 F1 on deterministic fields within a small
  pre-registered tolerance.
- `S4` should improve macro-F1 on the semantic TMI predicate group
  (`reRouteReason`, `reRouteType`, `implementationStatus`) over S0.
- Accepted LLM-derived facts should have evidence-span support; unsupported
  accepted facts should remain below a pre-registered threshold or be moved to
  review/quarantine.
- Repair evaluation should include repair precision and repair-induced false
  positive rate, not only repair success rate.

### Literature leads from Pro review requiring verification

The Pro review suggested several additional papers and tools that may be useful
for the related-work section, but they should not be cited as formal evidence
until they are fetched and checked directly:

- OntoLogX / ontology-guided extraction from cybersecurity logs.
- JSON-Schema-guided information extraction.
- Graphusion / retrieval-augmented KGC with global fusion.
- RAKG / document-level retrieval-augmented KGC.
- RAGAS / automated RAG evaluation.
- STaRK / textual and relational retrieval benchmark.
- Microsoft GraphRAG / query-focused summarization.

Use these as search leads only. The currently verified methodology anchors in
this plan remain the checked KGC/GraphRAG papers and the official
NASA/FAA/W3C sources listed below.

## Pipeline Corrections

### Corrected system suite

| ID | Purpose | Scored how |
| --- | --- | --- |
| `S0_rule_only` | Deterministic parser for semi-structured ATCSCC fields. | Direct ATMONTO-profile scoring. |
| `S1_raw_open_llm` | Schema-free LLM extraction with generic entities, relations, attributes, values, and evidence spans. | Raw JSON/evidence/coverage diagnostics only. No direct target-schema P/R/F1. |
| `S1b_llm_canonicalized` | Post-hoc canonicalization of S1 raw facts into the ATMONTO scoring profile. | Direct ATMONTO-profile P/R/F1 after canonicalization. |
| `S2_llm_schema_slice` | LLM extraction with a compact relevant ATMONTO schema slice. | Direct ATMONTO-profile scoring. |
| `S3_llm_schema_slice_validator_repair` | S2 plus validator/repair loop. | Direct ATMONTO-profile scoring plus repair metrics. |
| `S4_hybrid_backbone_enrichment` | S0 deterministic backbone merged with S3 semantic enrichment. | Primary candidate system for the next thesis claim. |

### Corrected pipeline

1. Freeze source snapshot and manifest.
2. Keep ATCSCC advisories as the extraction corpus.
3. Run `S0_rule_only` for structured backbone fields.
4. Run `S1_raw_open_llm` with no ATMONTO terms in the extraction prompt.
5. Canonicalize S1 raw facts into `S1b_llm_canonicalized`.
6. Run `S2` and `S3` with compact relevant schema slices.
7. Build `S4_hybrid_backbone_enrichment`:
   - keep S0 for identifiers, times, TMI lifecycle anchors, and obvious airport
     control elements;
   - prefer S3 for semantic fields such as reroute reason, reroute type,
     implementation status, and evidence-rich comments;
   - reject or quarantine conflicts unless the validator and evidence span agree.
8. Score by predicate families, not only aggregate F1.
9. Report profile gaps separately from extractor bugs.

## Prompt Corrections

### S1 raw open extraction prompt

The S1 prompt should not mention NASA ATMONTO, ATMONTO classes, or ATMONTO
predicates. It should still require a stable JSON shape:

- `entities`
- `events`
- `attributes`
- `relations`
- `quantities_or_times`
- `evidence_span`
- `confidence`

This makes S1 a true schema-free extraction baseline while preserving enough
structure for a later canonicalization step.

### S2 and S3 schema-constrained prompts

S2/S3 should receive:

- only the relevant schema slice for the current advisory type;
- a small number of reviewed examples from a development split, not the held-out
  scoring set;
- explicit evidence-span requirements;
- one flat fact per predicate-value assertion.

If the current 100 reviewed records remain the held-out score set, create a
separate 10-20 record development set outside that 100 for prompt examples. If
that is not feasible, use cross-validation and report the split.

## Hypothesis Corrections

| Old hypothesis | Problem | Replacement |
| --- | --- | --- |
| `H1`: schema guidance reduces structural drift | Still usable for structural drift, but only if S1 raw and S1b canonicalized are separated. | `H1`: schema guidance reduces unsupported target-schema terms after canonicalization. |
| `H2`: validator/repair improves valid yield | Still usable, but it must separate structural acceptance from semantic correctness. | `H2`: validator/repair improves structural validity while preserving semantic F1 within the pre-registered tolerance. |
| `H3`: ontology constraints improve precision more than recall harm | Invalid while S1 is all-zero from schema rejection. | `H3`: S4 hybrid improves selected semantic-predicate F1 over S0 while preserving deterministic-field F1 within a pre-registered tolerance. |
| `H4`: rejection triage produces actionable decisions | Still usable. | Keep, but report profile gaps as extension candidates, not as accepted ontology changes. |

## Acceptance Criteria For The Next Rerun

The next stage should not be called successful merely because JSON parses or
because schema violation decreases. Use these criteria:

1. `S1_raw_open_llm` has non-empty raw extractions and evidence spans for most
   records.
2. `S1b_llm_canonicalized` has non-zero accepted facts, so LLM-only semantic
   scoring is no longer an artifact of direct schema rejection.
3. `S4_hybrid_backbone_enrichment` preserves S0 performance on deterministic
   fields within the pre-registered tolerance.
4. `S4_hybrid_backbone_enrichment` improves the target semantic predicates
   where S0 is weak, especially reroute reason, reroute type, and implementation
   status.
5. Reports distinguish:
   - structural conformance;
   - semantic correctness;
   - canonicalization yield;
   - evidence-span validity;
   - profile gaps;
   - extractor bugs.

## Immediate Implementation Checklist

1. Mark current `S1_llm_only` target-schema P/R/F1 as
   `invalid_direct_schema_scoring` in the report narrative.
2. Add `S1_raw_open_llm` output generation and diagnostics.
3. Add `S1b_llm_canonicalized` mapping into the ATMONTO fact schema.
4. Add `S4_hybrid_backbone_enrichment` merge rules.
5. Add a second PDF source-family pilot using PCG / JO 7110.65BB passages,
   keeping PDF definition/procedure extraction separate from ATCSCC event
   extraction.
6. Update `EXPERIMENTS.md` to revise H3, clarify S1 scoring, and
   describe source-family boundaries.
7. Regenerate `reports/stages/nasa_atmonto_formal_experiment_scoring.*`.
8. Add a short remediation appendix explaining why the original all-zero S1 was
   a baseline-interface problem.
9. Rerun the verification stack before promoting the new stage:
   `uv run ruff check .`, `uv run pytest`, and the formal experiment report
   generation command.

## External References Used For This Remediation

- Zeno Cauter and Nikolay Yakovets, "Ontology-guided Knowledge Graph
  Construction from Maintenance Short Texts", 2024. Supports ontology-guided
  triplet extraction with in-context examples for domain-specific short texts.
  https://consensus.app/papers/ontologyguided-knowledge-graph-construction-from-cauter-yakovets/28494e5fc0905fc598416a17f098c8c0/
- Bowen Zhang and Harold Soh, "Extract, Define, Canonicalize: An LLM-based
  Framework for Knowledge Graph Construction", 2024. Supports separating open
  extraction from schema definition and post-hoc canonicalization.
  https://consensus.app/papers/extract-define-canonicalize-an-llmbased-framework-for-zhang-soh/711b33c15bfc562d9137b07050be7666/
- Yuqi Zhu et al., "LLMs for knowledge graph construction and reasoning: recent
  capabilities and future opportunities", 2023. Supports treating LLMs as
  support modules for construction, normalization, reasoning, and external-source
  aided KG workflows rather than as the only extractor.
  https://consensus.app/papers/llms-for-knowledge-graph-construction-and-reasoning-zhu-wang/bc301ddc6b135419a9743367f3b5545c/
- Vamsi Krishna Kommineni, B. Konig-Ries, and Sheeba Samuel, "From human
  experts to machines: An LLM supported approach to ontology and knowledge graph
  construction", 2024. Supports human-in-the-loop evaluation for automatically
  generated KGs.
  https://consensus.app/papers/from-human-experts-to-machines-an-llm-supported-approach-to-kommineni-knig-ries/57f213fdb33c53609cd26604814de6b3/
- Vetle Ryen, A. Soylu, and D. Roman, "Building Semantic Knowledge Graphs from
  (Semi-)Structured Data: A Review", 2022. Supports treating structured and
  semi-structured data as a distinct KG construction setting.
  https://consensus.app/papers/building-semantic-knowledge-graphs-from-semistructured-ryen-soylu/1320b5afd1ab58d6a3e24c91a499425e/
- Samira Khorshidi et al., "ODKE+: Ontology-Guided Open-Domain Knowledge
  Extraction with LLMs", 2025. Supports a hybrid pipeline with pattern-based
  extraction, ontology-guided prompting, grounding, and corroboration.
  https://consensus.app/papers/odke-ontologyguided-opendomain-knowledge-extraction-khorshidi-nikfarjam/bf5f40fe4528547882c7ebbfbbd21113/
- John Dagdelen et al., "Structured information extraction from scientific text
  with large language models", 2024. Supports structured JSON-like extraction
  from specialized technical text when paired with task-specific evaluation.
  https://consensus.app/papers/structured-information-extraction-from-scientific-text-dagdelen-dunn/075e3f5a3be0575d99f30dc34440d323/
- Qiang Sun et al., "Docs2KG: A Human-LLM Collaborative Approach to Unified
  Knowledge Graph Construction from Heterogeneous Documents", 2025. Supports
  separating layout, metadata, and semantic KG layers for heterogeneous document
  sources and retaining human verification.
  https://consensus.app/papers/docs2kg-a-humanllm-collaborative-approach-to-unified-sun-luo/d2c7ec831d695f5fb3a02d3cd10ae6b0/
- Boci Peng et al., "Graph Retrieval-Augmented Generation: A Survey", 2024.
  Supports describing GraphRAG as a pipeline with graph-based indexing,
  graph-guided retrieval, and graph-enhanced generation rather than a single
  monolithic score.
  https://consensus.app/papers/graph-retrievalaugmented-generation-a-survey-peng-zhu/1b8c5362a3d3538ba1dd90f9b40178f1/
- Yunfan Gao et al., "Retrieval-Augmented Generation for Large Language Models:
  A Survey", 2023. Supports modular RAG evaluation across retrieval,
  generation, augmentation, grounding, and domain-specific external knowledge.
  https://consensus.app/papers/retrievalaugmented-generation-for-large-language-models-gao-xiong/4d433eb94a8a5f2cade94b64ac76b657/
- Nourhan Ibrahim et al., "A survey on augmenting knowledge graphs (KGs) with
  large language models (LLMs): models, evaluation metrics, benchmarks, and
  challenges", 2024. Supports separating KG-augmented LLM, LLM-augmented KG, and
  synergized-framework claims.
  https://consensus.app/papers/a-survey-on-augmenting-knowledge-graphs-kgs-with-large-ibrahim-aboulela/9e7ff761d4965088a60992a6db9ee584/
- Aoran Gan et al., "Retrieval Augmented Generation Evaluation in the Era of
  Large Language Models: A Comprehensive Survey", 2025. Supports evaluating RAG
  as a hybrid system with retrieval quality, factual accuracy, safety, and
  efficiency dimensions.
  https://consensus.app/papers/retrieval-augmented-generation-evaluation-in-the-era-of-gan-yu/f546e1890e8656f1bb0cb3a3ec7e882d/
- FAA ATCSCC advisory pages, NASR 2026-05-14 README, and NASA ATMONTO official
  documentation were checked with AnySearch during remediation planning.
