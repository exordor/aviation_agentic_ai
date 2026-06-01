# Data Source Extraction Method Matrix

## Material Passport

- Artifact: data-source classification and extraction-method matrix.
- Scope: current NASA ATMONTO pivot sources plus prior baseline and planned extension sources.
- Primary experiment role: choose the safest extraction path for each source before KG construction.
- Snapshot evidence used: NASA ATMONTO phase-1 collection, temporal alignment, FAA reference-document inventory, AIRM-O alignment inventory, local ontology files, and existing source backend policy.
- Consensus validation: `reports/stages/data_source_extraction_method_consensus_validation.md`.
- Claim boundary: retrospective research data integration only. No source in this matrix supports live operational flight decisions.

## Core Decision Rule

Use deterministic extraction whenever a source exposes official fields, tables,
archives, or ontology syntax. Use LLM extraction only for text-rich sources where
the target relation is semantic rather than syntactic, and always require exact
source evidence plus ontology validation.

## Method Classes

| Method class | Source signal | Primary extraction method | Output shape | LLM role |
| --- | --- | --- | --- | --- |
| M1 ontology/schema inventory | OWL, RDF, Turtle, alignment RDF | `rdflib` or XML parser; term inventory; namespace normalization; class/property/domain/range checks | TBox profile, mapping seeds, schema coverage report | None for facts; optional label/definition summarization only after parsing |
| M2 structured API translator | JSON/XML records with stable fields and timestamps | Typed API parser; field mapping rules; raw record preservation; checksum and manifest | Normalized JSONL plus deterministic KG candidate records | None for primary extraction; optional explanation generation only |
| M3 archive/reference-data parser | Fixed cycle ZIP or bulk table package | Archive inventory; member-specific parsers; cycle-valid metadata; entity-key normalization | Reference entity backbone and linkable identifiers | None |
| M4 semi-structured HTML event extraction | Public HTML pages with event/advisory text | Crawler, HTML text extraction, regex/header parser, then ATMONTO-constrained extraction | Event/advisory candidates with evidence spans and time intervals | Main semantic extractor, gated by exact evidence and ATMONTO validator |
| M5 reference document chunking | Official PDF or structured HTML manuals | Hybrid Docling + PyMuPDF for PDF; recursive main-content HTML parser for HTML; section-aware chunks | Reference chunks, terminology, controlled definitions, QA evidence | Limited to definition/relation candidates with quote evidence |
| M6 structured tabular translator | CSV, TSV, fixed-width, database-style downloads | Deterministic row parser; schema dictionary; type conversion; entity linking | Normalized entity/event tables and deterministic KG candidates | None except rare normalization proposals |
| M7 time-series/trajectory translator | State vectors, tracks, timestamps, coordinates | API snapshot; spatial/temporal filtering; deterministic geometry/time mapping | Track points, route fragments, sampled trajectory records | None for facts |
| M8 literature/source-selection extraction | Research papers, NTRS PDFs, reports | Metadata extraction plus hybrid PDF text extraction; citation/link inventory | Related-work evidence, source-justification notes | Optional summary only; not ABox extraction |

## Current Source Matrix

| Source family | Current local evidence | Data shape and temporal behavior | Recommended extraction method | KG role | Validation and limits |
| --- | --- | --- | --- | --- | --- |
| NASA ATMONTO modules | `data/ontology/external/icarus_ontology/NASA/` contains `ATM.owl`, `NAS.owl`, `atmontoCore.owl`, `data.owl`, `equipment.owl`, `general.owl` | OWL/XML TBox; not time-varying event data | M1. Parse with RDF/OWL tooling into a project runtime profile; keep allowed classes/properties/domain/range as validator inputs | Primary schema constraint for the ATMONTO experiment | Do not treat ontology classes as extracted facts or ground truth instances |
| AIRM-O and ATMONTO2AIRM alignments | `reports/stages/airm_o_ontology_alignment.json`; 915 classes, 1761 object properties, 494 datatype properties, 115 ATMONTO/AIRM mapping records | External OWL/Turtle ontology plus alignment RDF; schema-level only | M1. Parse ontology inventory and alignment cells; emit mapping JSONL for coverage and gap analysis | External ATM interoperability reference and schema audit source | Alignment records are not ABox facts; NASA ATMONTO stays the primary schema |
| ICARUS ontology repository | `data/ontology/external/icarus_ontology/` including NASA ATMONTO modules and `ICARUS_Ontology.owl` | OWL files; schema/reference material | M1. Parse for comparison, namespace reuse, and term provenance | External reference baseline; supports ontology-source justification | Keep separate from experiment ground truth and from current event data |
| AviationWeather METAR | 518 source and 518 aligned records in `data/processed/nasa_atmonto/.../aviationweather_metar.jsonl` | Structured JSON records with `reportTime` and raw METAR text; instant observations | M2. Deterministically map fields and raw report strings to weather-report and weather-condition records; preserve raw METAR | Weather observation evidence; silver-label source for weather extraction | Align by `reportTime`; no causal delay claims without other evidence |
| AviationWeather TAF | 87 source and 87 aligned records in `data/processed/nasa_atmonto/.../aviationweather_taf.jsonl` | Structured JSON records with validity intervals and raw TAF text | M2. Deterministically map forecast validity intervals and parsed fields; keep raw TAF for evidence | Forecast evidence and weather-condition context | Include by interval intersection with experiment window |
| AviationWeather station info | 3 source/aligned records for KJFK, KEWR, KLGA | Static airport/station metadata attached to the snapshot window | M2. Deterministic station/airport metadata mapping | Station and airport-weather linking context | Treat as metadata, not weather observations |
| FAA NASR 28-Day Subscription | 147 ZIP members in inventory; cycle `2026-05-14T00:00:00Z` to `2026-06-11T00:00:00Z` | Cycle-valid archive; many file types inside a fixed effective period | M3. Keep ZIP inventory, then add member-specific deterministic parsers for airports, runways, fixes, facilities, routes | NAS entity backbone and identifier authority | Attach all records to cycle validity; do not use for live status or weather |
| FAA NAS Status / ATCSCC advisories | 867 source advisories, 718 aligned advisories in `data/processed/nasa_atmonto/.../atcscc_advisories.jsonl` | Public HTML advisory/event text; partially structured with advisory times and affected entities | M4. Crawler plus HTML text parser; regex for advisory metadata and times; ATMONTO-constrained LLM for TMI semantics | Primary text-rich ABox extraction target for TMI/event concepts | Advisory timestamps are parser-derived and need review before gold use; require exact evidence quotes |
| FAA reference documents | 15 downloaded records, 181,320,851 bytes, groups: AIM, AIP, PCG, JO 7110.65, JO 7210.3, Aviation Weather Handbook, Chart Users Guide, catalog pages | Official PDFs and HTML entrypoints; mostly reference/terminology text with effective dates | M5. Use hybrid Docling + PyMuPDF for PDFs; recursive HTML capture for HTML content beyond entrypoints; section-aware chunking | Reference evidence, terminology, controlled vocabulary, QA corpus | Do not convert procedure/reference text into live event facts |
| PHAK Chapter 4 PDF | `data/raw/06_phak_ch4_0.pdf` plus existing chunks/KG/evaluation artifacts | Educational PDF; historical baseline corpus | M5. Hybrid PDF extraction for structure-aware chunks; keep as baseline comparability corpus | Prior prototype and benchmark baseline | Not the main ATMONTO-aligned experiment source |
| NASA Glenn aerodynamics pages | `data/sources/nasa_bga_aerodynamics_sources.yaml` and normalized metadata/sections | Educational HTML pages with clean main-content blocks | M5. Main-content HTML parser; section-aware page chunks | Cross-source educational evaluation for aerodynamics concepts | Useful for source diversity, not ATM/NAS event extraction |
| NTRS ontology papers and reports | `data/papers/ntrs_ontology_selection/` PDFs and analysis notes | Literature PDFs, reports, and metadata | M8. Hybrid PDF extraction plus citation/link inventory | Related work, ontology/source selection evidence | Do not use paper claims as operational ABox facts |
| FAA Aircraft Registry | Planned phase-2 source in experiment design | Structured public bulk tables refreshed frequently | M6. Deterministic table parser, schema dictionary, N-number/Mode S normalization | Equipment-module extension and aircraft identity linking | Avoid private inference beyond releasable fields |
| BTS TranStats On-Time Performance | Planned optional extension | Structured DOT/BTS table downloads by month/airport/carrier | M6. Deterministic table parser; link airports/carriers to NASR entities | Flight-performance and delay-context extension | Not real-time status; delay causality requires supporting evidence |
| OpenSky Network | Planned phase-3 optional source | Time-series ADS-B state vectors with access limits | M7. Snapshot API client, spatial/time filtering, deterministic state-vector mapping | Optional track-point and trajectory experiment | Not FAA/NASA official; separate from primary claims |

## Recommended Extraction Stack

| Pipeline layer | Sources | Method |
| --- | --- | --- |
| Schema layer | NASA ATMONTO, ICARUS, AIRM-O, ATMONTO2AIRM | M1 parse, profile, validate, map |
| Entity backbone | FAA NASR, station info, future registry | M2/M3/M6 deterministic translators |
| Dynamic observations | METAR, TAF, future ADS-B | M2/M7 deterministic translators with time-window filtering |
| Event/advisory layer | ATCSCC advisories | M4 constrained extraction with evidence and validator gates |
| Reference text layer | FAA manuals, glossary, AIM/AIP, PHAK, NASA Glenn | M5 section-aware chunking and controlled definition extraction |
| Literature layer | NTRS papers and reports | M8 metadata, source links, and related-work evidence |

## Gold/Silver/Bronze Policy

- Gold candidates: manually reviewed records or mappings with source evidence, ontology term validation, and temporal alignment.
- Silver candidates: deterministic translations from official structured fields, such as METAR/TAF parsed fields or NASR records.
- Bronze candidates: LLM-extracted triples from advisories or reference text before manual review.
- Not candidates: ontology classes by themselves, literature claims, reference-document procedure text without instance evidence, and raw browser/page text without provenance.

## Implementation Notes

- Add source-specific deterministic translators before adding a general LLM pass.
- Keep raw payload hashes, local raw paths, source URLs, retrieval commands, and parser versions in every manifest.
- For instant records, align by event/report time. For interval records, align by interval intersection. For cycle-valid reference data, attach the cycle coverage to every derived record.
- Use exact evidence containment checks for all LLM-produced triples.
- Run domain/range and allowed-term validation against the NASA ATMONTO runtime profile before accepting triples into the experimental KG.
