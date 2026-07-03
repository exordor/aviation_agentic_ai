# NASA ATMONTO Experiment Design

> Transitional context warning: this file documents the shift from the old PHAK
> prototype toward NASA ATMONTO. It is useful history, but the current thesis is
> narrower: schema-constrained, evidence-grounded Agentic KG-RAG over
> retrospective FAA ATCSCC advisories. Start from
> `docs/context_hygiene_audit.md` and `docs/research_mainline.md` first.

Last updated: 2026-06-01

## Material Passport

- Artifact: NASA ATMONTO experiment design.
- Status: proposed pivot design.
- Scope: replace the PHAK Chapter 4 primary experiment with a NASA ATMONTO-aligned heterogeneous aviation data integration experiment.
- Primary ontology: local NASA/ATMONTO modules under `data/ontology/external/icarus_ontology/NASA/`.
- Historical baseline: the former PHAK Chapter 4 curated ontology remains a prior prototype, not the main experimental ontology.
- Claim boundary: retrospective data integration and evidence-traceable QA only. This experiment does not support live operational flight decisions.

## Pivot Decision

The project should stop treating the hand-built PHAK Chapter 4 ontology as the
main research object. That ontology was useful when no practical aviation
ontology file had been located. Now that local NASA/ATMONTO files are available,
the defensible thesis route is:

> Adopt NASA ATMONTO as the authoritative aviation TBox baseline, build an
> ontology-constrained extraction and validation pipeline around it, and test
> whether it improves KG validity, provenance, cross-source integration, and
> evidence-traceable aviation QA.

This requires changing the source corpus. PHAK Chapter 4 is mostly
aerodynamics/training text, while NASA ATMONTO is strongest for air traffic
management, NAS infrastructure, weather reports, airport data, equipment, routes,
traffic management initiatives, flight plans, and data-source integration.

## Research Aim

Evaluate whether NASA ATMONTO-constrained LLM extraction and deterministic
source translators can produce a more schema-valid, provenance-preserving, and
queryable aviation KG than unconstrained or weakly constrained extraction.

The experiment is not designed to prove that an LLM understands aviation
semantics in general. It tests a narrower, falsifiable claim:

> NASA ATMONTO constraints reduce invalid or unverifiable KG triples while
> preserving enough coverage to answer retrospective, source-grounded ATM/NAS
> competency questions.

## Research Questions

- **RQ1**: Can NASA ATMONTO be transformed into a usable project ontology profile for KG extraction and validation?
- **RQ2**: Does ATMONTO-constrained extraction reduce unsupported classes, unsupported properties, and domain/range violations compared with unconstrained LLM extraction?
- **RQ3**: Does an explicit mapping-rule layer improve cross-source entity linking and provenance completeness?
- **RQ4**: Does the resulting KG improve evidence-traceable competency-question answering over source-only retrieval?
- **RQ5**: Which NASA ATMONTO areas are well covered by open reproducible data, and which require restricted sources or ontology extension?

## Hypotheses

- **H1**: ATMONTO-constrained extraction has a lower schema violation rate than unconstrained extraction.
- **H2**: Domain/range validation improves triple precision but may reduce recall.
- **H3**: Mapping rules and a repair loop recover some recall lost by strict validation without materially increasing hallucinated ontology terms.
- **H4**: Cross-source KG queries improve citation traceability for multi-source questions compared with source-only RAG.
- **H5**: Open reproducible sources cover NAS, weather, airport, aircraft, and some TMI concepts better than flight-plan and operational-track concepts.

## Data Sources

Use a reproducible snapshot-based design. All live or frequently updated sources
must be copied into `data/raw/nasa_atmonto/<snapshot_date>/` with metadata,
license/access notes, retrieval command, timestamp, and checksum.

| Source | Role | ATMONTO alignment | Access status | Experimental priority |
| --- | --- | --- | --- | --- |
| NOAA Aviation Weather Center Data API/cache | METAR, TAF, PIREP/AIREP, SIGMET/G-AIRMET, station and airport weather data. | `data:MeteorologicalReport`, `data:WeatherCondition`, `data:SurfaceWindCondition`, `data:VisibilityCondition`, `data:SkyCondition`, `data:CloudLayer`, `data:hasWeatherCondition`. | Public API/cache; API access is limited by rate limits and recent-history window. | Primary. |
| FAA Aeronautical Data / NASR 28-Day Subscription | Airports, runways, fixes, routes, facilities, NAS components. | `nas:Airport`, `nas:OperationalRunway`, `nas:PhysicalRunway`, `nas:ARTCC`, `nas:TRACON`, `atm:NavigationFix`, `gen:Location`. | Public FAA downloads with current and archived cycles. | Primary. |
| FAA Aircraft Registry releasable download | Aircraft registration, model, engine, Mode S, N-number metadata. | `eqp:Aircraft`, `eqp:AircraftModel`, `eqp:AircraftEngine`, `eqp:registrationNumber`, `eqp:modeSCode`. | Public FAA download refreshed daily. | Secondary, strong for equipment module. |
| FAA NAS Status / ATCSCC advisories | Traffic management initiatives, ground stops, ground delay programs, reroutes, airport events. | `atm:TrafficManagementInitiative`, `atm:GroundStopTMI`, `atm:GroundDelayProgramTMI`, `atm:ReRouteTMI`, `atm:AirspaceFlowProgramTMI`, `atm:impactingCondition`. | Public web source; historical depth and scraper stability must be verified per run. | Primary if retrieval is stable; otherwise secondary. |
| BTS TranStats On-Time Performance | Scheduled and actual flight operations, delays, carrier, origin/destination, time fields. | `atm:Flight`, `atm:plannedDepartureTime`, `atm:actualDepartureTime`, `atm:arrivalAirport`, `atm:departureAirport`, `nas:AirCarrier`. | Public DOT/BTS table downloads. | Optional extension for flight-level data. |
| OpenSky Network | ADS-B state vectors and trajectories. | `atm:AircraftTrackPoint`, `atm:ActualFlightRoute`, `eqp:modeSCode`. | Public/academic access with limits; not FAA/NASA official. | Optional extension only. |

Do not use ASDI, ERAM, TRACON tracks, CIWS, CTAS, TBFM, Exelis commercial feeds,
or NASA Ames ATM Data Warehouse as required experiment inputs unless authenticated
or licensed access is obtained. They are valid related-work evidence, not
reproducible thesis data sources.

## Main Data Source Usage Plan

The first implementation should use three primary source families:
AviationWeather, FAA NASR/Aeronautical Data, and FAA NAS Status/ATCSCC
advisories. These cover the `data`, `nas`, and `atm` ATMONTO modules and are
enough for a defensible first KG extraction and cross-source integration
experiment.

FAA Aircraft Registry and BTS TranStats should be second-phase extensions.
OpenSky should remain a third-phase optional trajectory source because it is not
an FAA/NASA source and it adds access and interpretation complexity.

### Shared Acquisition Rules

Every source download must be snapshot-based. Do not query sources live during
evaluation.

For each source family, create:

- `data/raw/nasa_atmonto/<snapshot_date>/<source_family>/`
- `data/raw/nasa_atmonto/<snapshot_date>/<source_family>/manifest.json`
- `data/processed/nasa_atmonto/<source_family>.jsonl`
- `reports/stages/nasa_atmonto_<source_family>_source_inventory.json`

Each `manifest.json` entry should include:

- `source_family`
- `source_url`
- `retrieval_command`
- `retrieved_at`
- `source_effective_date`
- `raw_file`
- `raw_payload_hash`
- `format`
- `license_or_access_note`
- `parser_version`
- `record_count`
- `known_limitations`

### Phase 1 Core Sources

| Source family | How to use | Use scope | ATMONTO targets | Do not use for |
| --- | --- | --- | --- | --- |
| AviationWeather Data API/cache | Pull METAR, TAF, PIREP/AIREP, SIGMET/G-AIRMET, station info, and airport info for the sampled airports and time window. Prefer cache files for large current snapshots; use API calls only for scoped airport/time queries. Store both raw text and parsed JSON/XML where available. | Weather observations, forecasts, pilot reports, weather advisories, station metadata, airport weather context. | `data:MeteorologicalReport`, `data:WeatherCondition`, `data:SurfaceWindCondition`, `data:VisibilityCondition`, `data:SkyCondition`, `data:CloudLayer`, `data:forecastingAirport`, `nas:Airport`. | Long historical weather reconstruction unless snapshots were preserved; operational weather briefing; causal claims that weather caused a flight delay without supporting source evidence. |
| FAA Aeronautical Data / NASR | Download the fixed 28-day NASR subscription cycle used by the experiment. Parse airports, runways, fixes, ARTCC/TRACON/facility records, and relevant route/fix data. Treat this as deterministic reference data rather than text for LLM extraction. | NAS infrastructure reference layer and entity linking backbone. | `nas:Airport`, `nas:OperationalRunway`, `nas:PhysicalRunway`, `nas:ARTCC`, `nas:TRACON`, `nas:Sector`, `atm:NavigationFix`, `gen:Location`. | Weather, live airport status, real-time operational suitability, flight trajectories, delay causes. |
| FAA NAS Status / ATCSCC advisories | First run a scraper feasibility check for the selected 7- to 14-day window. Save advisory/event HTML and extracted text. Focus on Ground Stops, Ground Delay Programs, Route advisories, Airspace Flow Programs, CTOP Programs, and Other advisories. Use LLM extraction here because advisories are text-rich and TMI concepts are in ATMONTO. | Traffic management initiatives, advisory text, impacted airports/facilities, time windows, stated impacting conditions. | `atm:TrafficManagementInitiative`, `atm:GroundStopTMI`, `atm:GroundDelayProgramTMI`, `atm:ReRouteTMI`, `atm:AirspaceFlowProgramTMI`, `atm:controlledNASelement`, `atm:impactingCondition`, `atm:issuedTime`, `atm:effectiveStartTime`, `atm:effectiveEndTime`. | Bulk historical reconstruction without confirmed access; live operational decision support; inferring unstated causes or impacts beyond the advisory text. |

### Phase 2 Extension Sources

| Source family | How to use | Use scope | ATMONTO targets | Do not use for |
| --- | --- | --- | --- | --- |
| FAA Aircraft Registry | Download the releasable aircraft database and documentation. Parse Aircraft Registration Master, Aircraft Reference, Engine Reference, and Mode S / N-number fields. Use deterministic parsing and sample only records needed for the experiment. | Aircraft/equipment metadata and optional aircraft identity linking. | `eqp:Aircraft`, `eqp:AircraftModel`, `eqp:AircraftType`, `eqp:AircraftEngine`, `eqp:registrationNumber`, `eqp:modeSCode`, `eqp:numberOfEngines`, `eqp:manufactureYear`. | Flight operations, trajectory, schedule, airport event status, private-owner inference beyond releasable fields. |
| BTS TranStats On-Time Performance | Download a fixed month and selected airport/carrier subset. Use structured fields such as `FlightDate`, `Origin`, `Dest`, `CRSDepTime`, `DepTime`, `ArrDelay`, `WeatherDelay`, and `NASDelay`. Link airports to NASR entities. | Scheduled commercial flight performance and delay context. | `atm:Flight`, `atm:departureAirport`, `atm:arrivalAirport`, `atm:plannedDepartureTime`, `atm:actualDepartureTime`, `nas:AirCarrier`. | Real-time flight status; aircraft trajectory; proving a specific advisory or weather report caused a specific delay without additional evidence. |

### Phase 3 Optional Source

| Source family | How to use | Use scope | ATMONTO targets | Do not use for |
| --- | --- | --- | --- | --- |
| OpenSky Network | Use only if the experiment needs ADS-B state vectors or aircraft trajectory samples. Prefer small spatial/time windows and document API or research-access constraints. Link ICAO24/Mode S to FAA registry only where matching is reliable. | Aircraft state vectors, track points, route reconstruction experiments. | `atm:AircraftTrackPoint`, `atm:ActualFlightRoute`, `eqp:modeSCode`. | FAA/NASA-official claims; commercial schedules, delay data, passenger data, origin/destination certainty unless independently inferred and validated. |

### Recommended First Snapshot

Use this minimal first run before scaling:

- Airports: KATL, KORD, KJFK, KDFW, KLAX.
- Window: 7 days.
- AviationWeather: METAR + TAF + station info for all five airports.
- NASR: one fixed effective cycle covering the experiment window.
- ATCSCC/NAS Status: all advisories/events that mention the five airports,
  their ARTCCs, or relevant route/TMI categories.
- Registry/BTS/OpenSky: disabled for the first run unless Phase 1 succeeds.

### Source-Specific Evaluation Roles

- AviationWeather provides structured silver labels for weather-condition
  extraction and airport-weather linking.
- NASR provides the authoritative entity backbone for airport, runway, fix, and
  facility linking.
- ATCSCC/NAS Status provides the primary text-rich LLM extraction target.
- FAA Aircraft Registry tests the `eqp` module only after the core KG works.
- BTS tests flight-performance integration only after airport and advisory
  linking are stable.
- OpenSky tests trajectory/track concepts only as a separate optional extension.

## Corpus Definition

The recommended first reproducible corpus is a 7- to 14-day retrospective sample
centered on 5-8 major U.S. airports:

- KATL, KORD, KJFK, KDFW, KLAX as the minimum set.
- Optional: KDEN, KSFO, KSEA for weather/geography diversity.

For each airport and time window, collect:

- NASR airport/runway/facility records.
- AviationWeather METAR/TAF records.
- AviationWeather PIREP/AIREP records where available.
- NAS Status or ATCSCC advisories mentioning the airport or associated ARTCC/TRACON where available.
- Aircraft registry only if the experiment includes aircraft/equipment linking.
- BTS or OpenSky only if the experiment includes flight-level tracking or schedule questions.

Store every source record with:

- `source_id`
- `source_url`
- `retrieved_at`
- `source_effective_date`
- `raw_payload_hash`
- `license_or_access_note`
- `parser_version`

## Ontology Profile

The NASA upstream files are OWL/XML. The project should not feed them directly
into existing RDF/Turtle-oriented tools. Create a project runtime profile:

- `data/ontology/curated/nasa_atmonto_profile.ttl`
- `configs/extraction_profile_nasa_atmonto.yaml`
- `data/ontology/mappings/nasa_atmonto_mapping_rules.yaml`
- `data/ontology/mappings/atmonto_airm_alignment.jsonl`

AIRM-O is an external ATM interoperability reference ontology, not a replacement
for NASA ATMONTO. The AIRM-O integration stage downloads the AIRM-O ontology and
the ATMONTO2AIRM reference alignments, then writes a normalized mapping JSONL for
profile coverage, mapping-rule review, and extension-gap analysis:

```bash
uv run python scripts/collect_airm_o_pipeline.py --snapshot-date 2026-06-01
```

Use AIRM-O domain/range information to audit candidate terms and relationships,
but keep NASA ATMONTO as the primary schema constraint for extraction and
validation. Alignment records are schema-level references; they are not ABox
facts and they do not prove extracted triple truth.

The runtime profile should include only terms required by the experiment:

| Module | Core classes | Core object properties | Core data properties |
| --- | --- | --- | --- |
| `gen` | `Location`, `PointLocation`, `GeographicRegion`, `Sequence` | `centerpoint`, `hasNextItem`, `hasSequencedItem` | `latitude`, `longitude`, `altitude`, `sequenceNumber` |
| `nas` | `Airport`, `OperationalRunway`, `PhysicalRunway`, `ARTCC`, `TRACON`, `Sector`, `AirCarrier`, `AirportRoute`, `FederalAirway` | `hasRunway`, `airportLocation`, `locatedInCenter`, `includesARTCC`, `hasTRACONlayer`, `hasAirportRoute` | `icaoAirportCode`, `iataAirportCode`, `faaAirportCode`, `airportName`, `runwayID`, `runwayLengthInFeet`, `runwayWidthInFeet` |
| `data` | `MeteorologicalReport`, `WeatherCondition`, `SurfaceWindCondition`, `VisibilityCondition`, `SkyCondition`, `CloudLayer`, `AirportStatisticsData` | `hasMeteorologicalReport`, `hasWeatherCondition`, `hasSurfaceWindCondition`, `hasVisibilityCondition`, `hasSkyCondition`, `forecastingAirport` | `metarReportString`, `tafReportString`, `surfaceWindSpeed`, `surfaceGustSpeed`, `windDirectionFixed`, `limitedVisibilityDistance`, `ceiling`, `weatherPhenomenon` |
| `atm` | `Flight`, `NavigationFix`, `TrafficManagementInitiative`, `GroundStopTMI`, `GroundDelayProgramTMI`, `ReRouteTMI`, `AirspaceFlowProgramTMI`, `AircraftTrackPoint` | `arrivalAirport`, `departureAirport`, `controlledNASelement`, `includesAirport`, `excludesAirport`, `referenceFix`, `hasActualRoute`, `hasPlannedRoute` | `callSign`, `advisoryNumber`, `issuedTime`, `impactingCondition`, `effectiveStartTime`, `effectiveEndTime`, `actualArrivalTime`, `actualDepartureTime` |
| `eqp` | `Aircraft`, `AircraftModel`, `AircraftType`, `AircraftEngine`, `AircraftWakeCategory`, `AircraftWeightClass` | `hasAircraftModel`, `manufacturedBy`, `hasAircraftEngineType`, `hasAircraftWakeCategory`, `hasComponent` | `registrationNumber`, `modeSCode`, `aircraftSerialNumber`, `numberOfEngines`, `numberOfSeats`, `manufactureYear` |

## Extraction Conditions

Run the same sampled records through multiple conditions:

| Condition | Description | Purpose |
| --- | --- | --- |
| **C0 Source-only baseline** | No KG. Answer/query from raw source records and vector/text retrieval only. | Downstream QA baseline. |
| **C1 Unconstrained LLM extraction** | LLM extracts entities/triples from text without ontology terms. | Measure hallucinated schema and free-form drift. |
| **C2 Prompt-only ontology guidance** | Prompt lists allowed classes/properties, but no validator gate. | Test whether prompting alone is enough. |
| **C3 JSON schema gate** | LLM must emit strict JSON with class/property fields and provenance. | Test format control. |
| **C4 ATMONTO domain/range gate** | C3 plus unsupported term, domain, and range validation. | Test formal TBox constraints. |
| **C5 Mapping-rule resolver** | C4 plus explicit source-to-ontology mapping rules. | Test cross-source normalization and linking. |
| **C6 Repair loop** | Invalid C5 outputs are returned to the model once with validator errors. | Test whether constrained self-repair improves valid yield. |
| **C7 Deterministic translator upper bound** | For structured sources, deterministic parsers map fields to ATMONTO. | Establish a non-LLM ceiling for parseable data. |

For METAR/TAF, use both raw text and parsed API fields. The raw text supports
LLM extraction; parsed fields support silver labels and deterministic upper
bound checks.

For ATCSCC/NAS Status advisories, use semi-structured advisory text. This is the
best primary target for LLM extraction because TMIs are text-rich and directly
covered by `atm` classes.

## Mapping Rules

Create a versioned mapping file where every accepted triple type has a source
pattern and ontology target:

```yaml
rule_id: MR_METAR_WIND_001
source_family: aviationweather_metar
input_fields:
  - raw_metar
  - station_id
target_subject_class: data:MeteorologicalReport
target_predicate: data:hasSurfaceWindCondition
target_object_class: data:SurfaceWindCondition
required_provenance:
  - source_id
  - retrieved_at
  - evidence_text
  - source_url
```

The experiment should report which triples were accepted by which rule. This
makes failures inspectable and avoids treating LLM output as direct ontology
instantiation.

## Gold And Silver Labels

Use a mixed gold/silver strategy:

- **Silver labels from structured sources**: AviationWeather parsed JSON/XML,
  NASR structured records, aircraft registry CSV fields, and BTS fields where
  used.
- **Manual gold labels**: ATCSCC/NAS Status advisories, ambiguous METAR/TAF raw
  text samples, cross-source competency questions.
- **Review sample**: manually inspect at least 100 accepted triples and 50
  rejected triples, stratified by source family and extraction condition.

Recommended first benchmark size:

- 500 METAR records.
- 200 TAF records.
- 100 PIREP/AIREP or SIGMET/G-AIRMET records if available.
- 100 NASR airport/runway/facility records.
- 100 ATCSCC/NAS Status advisory/event records.
- 100 aircraft registry records if using `eqp`.
- 50 cross-source competency questions.

If time is limited, prioritize METAR/TAF + NASR + ATCSCC advisories because
those best cover `data`, `nas`, and `atm`.

## Competency Questions

Design CQs before running downstream QA. Examples:

- Which sampled airports have weather-reporting stations and active runways in
  the NASR snapshot?
- Which sampled airports had METAR reports with low visibility during the
  experiment window?
- Which airports had a ground stop or ground delay advisory, and what impacting
  condition was stated?
- For a selected airport and day, what weather conditions and TMI advisories are
  linked to the same airport?
- Which advisories mention an ARTCC or airport that can be resolved to NASR
  entities?
- Which extracted weather conditions failed to link to a known airport/station?
- Which source records should the system abstain from answering because the
  required source family was not collected?

CQs must be labeled by required source family:

- single-source weather;
- single-source NAS infrastructure;
- single-source advisory/TMI;
- cross-source airport-weather;
- cross-source airport-advisory;
- unsupported/no-answer.

## Metrics

### Ontology And Schema Metrics

- OWL/XML source inventory.
- Runtime TTL parse validity.
- class/property count in the runtime profile.
- domain/range coverage for selected predicates.
- mapping-rule coverage by source family.

### Extraction Metrics

- schema-valid triple rate.
- unsupported class count.
- unsupported property count.
- domain/range violation count.
- valid-yield rate: accepted triples / attempted triples.
- triple precision, recall, and F1 against gold/silver labels.
- entity linking precision and recall.
- hallucinated ontology term rate.
- rejected triple rate and rejection reason distribution.
- provenance completeness.
- evidence-in-source rate.

### Integration Metrics

- airport/station linking accuracy.
- runway-to-airport linking accuracy.
- advisory-to-airport or advisory-to-ARTCC linking accuracy.
- duplicate entity rate.
- cross-source join success rate.
- orphan entity count.

### Retrieval And QA Metrics

- CQ answer exact match or rubric score.
- citation precision and citation recall.
- source-family coverage.
- KG evidence coverage.
- abstention correctness on unsupported CQs.
- false-answer rate.
- graph path coverage for cross-source CQs.

### Efficiency Metrics

- cost per 100 records.
- latency per 100 records.
- validator rejection and repair overhead.
- deterministic translator throughput.

Do not collapse these metrics into one overall score.

## Analysis Plan

Use paired comparisons wherever possible because every condition processes the
same record sample:

- C1 vs C2: effect of prompt-only ontology guidance.
- C2 vs C4: effect of formal validation.
- C4 vs C5: effect of mapping rules.
- C5 vs C6: effect of repair loop.
- C5/C6 vs C7: gap to deterministic upper bound on structured sources.
- C0 vs KG-enabled QA: downstream effect on evidence-traceable answers.

Report:

- bootstrap 95% confidence intervals for precision, recall, F1, valid-yield,
  and citation metrics;
- McNemar-style paired error comparison for valid/invalid decisions where
  appropriate;
- per-source-family breakdowns, not only aggregate scores;
- negative results, especially recall loss from strict validation.

## Expected Results

Expected but not guaranteed:

- C1 will have the highest schema drift and hallucinated class/property rate.
- C2 will reduce obvious schema drift but still emit invalid terms or wrong
  domains/ranges.
- C4 will sharply reduce invalid triples, probably at the cost of recall.
- C5 should improve cross-source linking and provenance interpretability.
- C6 may improve valid-yield, but only if repair prompts include concrete
  validator errors.
- C7 should outperform LLM extraction on structured source fields; this is not
  a weakness, because the research contribution is identifying where LLM
  translation is useful and where deterministic translation is better.

## Threats To Validity

- Public source availability changes over time.
- AviationWeather API recent-history limits can make exact reruns impossible
  unless snapshots are stored.
- ATCSCC/NAS Status historical depth may be limited.
- NASA ATMONTO files are available locally but are OWL/XML, so conversion or a
  loader is required before using existing project validators.
- SHACL/domain/range conformance does not prove semantic truth.
- OpenSky is useful for tracks but is not an official FAA/NASA source.
- Strict validation can create false negatives when the ontology lacks a needed
  term.
- Manual gold labels are thesis/course-project evidence unless externally
  reviewed.

## Required Artifacts

- `data/ontology/curated/nasa_atmonto_profile.ttl`
- `data/ontology/mappings/nasa_atmonto_mapping_rules.yaml`
- `data/ontology/mappings/atmonto_airm_alignment.jsonl`
- `data/ontology/external/airm_o/manifest.json`
- `configs/extraction_profile_nasa_atmonto.yaml`
- `configs/nasa_atmonto_experiment.yaml`
- `data/raw/nasa_atmonto/<snapshot_date>/manifest.json`
- `data/processed/nasa_atmonto/*.jsonl`
- `data/kg/nasa_atmonto.kg.jsonl`
- `data/kg/nasa_atmonto.kg.ttl`
- `data/cqs/nasa_atmonto_cqs.gold.json`
- `reports/stages/nasa_atmonto_source_inventory.json`
- `reports/stages/nasa_atmonto_ontology_profile.json`
- `reports/stages/airm_o_ontology_alignment.json`
- `reports/stages/nasa_atmonto_extraction_comparison.json`
- `reports/stages/nasa_atmonto_integration_validation.json`
- `reports/stages/nasa_atmonto_cq_evaluation.json`
- `reports/stages/nasa_atmonto_error_analysis.md`

## Milestones

1. **Ontology profile**: convert or summarize required NASA ATMONTO classes and
   properties into runtime Turtle/profile files.
2. **Source feasibility**: download small snapshots from AviationWeather, NASR,
   FAA registry, and ATCSCC/NAS Status.
3. **Mapping rules**: define source-to-ontology mapping rules for METAR, NASR,
   advisory, and optional aircraft records.
4. **Extraction baselines**: implement C1-C6 for text-rich records and C7 for
   structured records.
5. **Gold/silver labels**: generate silver labels and manually review advisory
   and CQ samples.
6. **KG build and validation**: produce JSONL and TTL KG artifacts with
   provenance and rejection reports.
7. **CQ/QA evaluation**: compare source-only and KG-enabled answering.
8. **Error analysis**: classify failures by missing ontology term, source
   ambiguity, parser error, LLM hallucination, linking error, and unsupported
   question.

## Safe Thesis Wording

Supported target wording:

> This thesis evaluates a NASA ATMONTO-constrained pipeline for retrospective
> aviation data integration. The system uses official or public aviation data
> snapshots, maps source records into an ontology-aligned KG, validates extracted
> triples against schema and domain/range constraints, and evaluates whether the
> KG improves evidence traceability and cross-source competency-question
> answering.

Avoid:

- "The system proves semantic correctness."
- "NASA ATMONTO is complete ground truth for aviation."
- "The prototype supports operational flight decisions."
- "LLM extraction is better than deterministic parsing for structured data."
- "GraphRAG universally improves retrieval."
