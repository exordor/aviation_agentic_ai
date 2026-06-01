# NASA ATMONTO Window Selection

## Decision

- Primary reproducible experiment window: `2026-05-14T00:00:00Z` to `2026-05-21T00:00:00Z`.
- Primary airports: `KJFK`, `KEWR`, `KLGA`.
- NASR reference cycle: FAA NASR `28DaySubscription_Effective_2026-05-14.zip`, valid as a cycle snapshot from `2026-05-14T00:00:00Z` to before `2026-06-11T00:00:00Z`.
- Rationale: NASR is not a 7-day event feed. The experiment takes a 7-day dynamic-data window inside the NASR effective cycle, uses the same New York airport set as the NASA ATMONTO technical documentation instance examples, and remains within the public AviationWeather historical API availability window used by the collector.

## NASA Paper Windows

| Source | Paper window | Scope | Use in this project |
| --- | --- | --- | --- |
| `20170006095_nasa_air_traffic_management_ontology.pdf` | July 2014 | JFK, EWR, LGA; day, flight, METAR, TAF, and traffic-management instance files described in Appendix E | Keep as a NASA-paper replay target if the original instance files can be obtained. Do not claim full replay from current public APIs alone. |
| `20190000452_nasa_atm_ontology_semantic_integration_querying.pdf` | `2012-09-08` | KATL semantic integration prototype queries, including flight, METAR, and ASDI-style examples | Keep as a focused comparison case for query design and expected ontology joins. Treat source reconstruction as partial unless original instance data or archived feeds are found. |

## Feasibility Constraints

- Local ICARUS/NASA ontology files provide ontology schemas, but no local `atmontoPlus` instance files for July 2014 were found.
- AviationWeather historical API access did not support 2012 or 2014 replay in the current collector path; it is therefore unsuitable as the sole source for NASA-paper historical reproduction.
- ATCSCC advisory pages are available for old dates in the public interface, but weather, flight, and NASR historical alignment still require additional archived sources.
- FAA NASR is modeled as a cycle-valid reference layer. The source window is `[2026-05-14T00:00:00Z, 2026-06-11T00:00:00Z)`, while `2026-05-14` to `2026-05-21` is only the experiment alignment window.
- The previous `2026-05-22T00:00:00Z` to `2026-05-29T00:00:00Z` window is superseded for the main experiment because it is not anchored to the available NASR effective-cycle start.

## Experiment Arms

- `E1-public-reproducible`: use `2026-05-14T00:00:00Z` to `2026-05-21T00:00:00Z`, `KJFK/KEWR/KLGA`, AviationWeather, FAA NASR, and ATCSCC advisories. This is the main quantitative experiment window.
- `E2-paper-replay`: use July 2014 `JFK/EWR/LGA` only if NASA ATMONTO instance files or equivalent archived feeds are obtained. This is the direct NASA-document comparison arm.
- `E3-katl-paper-query`: use `2012-09-08` `KATL` as a query-template and qualitative comparison arm unless archived flight/weather feeds are obtained.

## Current Artifacts

- Collection report: `reports/stages/nasa_atmonto_phase1_collection.json`.
- Alignment report: `reports/stages/nasa_atmonto_temporal_alignment.json`.
- Alignment markdown: `reports/stages/nasa_atmonto_temporal_alignment.md`.
- Raw source root: `data/raw/nasa_atmonto/2026-05-14/`.
- Source processed root: `data/processed/nasa_atmonto/source/2026-05-14/`.
- Aligned processed root: `data/processed/nasa_atmonto/aligned/2026-05-14/`.

## Verified Counts

| Aligned source | Records |
| --- | ---: |
| AviationWeather METAR | 518 |
| AviationWeather TAF | 87 |
| AviationWeather station info | 3 |
| FAA NASR zip inventory | 147 |
| ATCSCC advisories | 718 |
