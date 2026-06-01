# Data-source analysis for NTRS 20190000452

Source PDF: `20190000452_nasa_atm_ontology_semantic_integration_querying.pdf`

Title: NASA's ATM Ontology: Semantic Integration and Querying Across NAS Data Sources

## What the presentation says

The presentation describes a NASA semantics-based data integration prototype for
airspace operations at KATL on 2012-09-08. NASA Ames' ATM Data Warehouse is
described as archiving historical ATM data collected from FAA, NASA, NOAA, DOT,
and industry. The warehouse captures both live streamed data and published
periodic data, with holdings available back to 2009.

The sampled warehouse holdings named in the slides are:

- ATCSCC advisories.
- Airline Situation Display to Industry (ASDI).
- Air Route Traffic Control Center flight plans and tracks.
- Corridor Integrated Weather Service (CIWS).
- Center-TRACON Automation System (CTAS).
- Exelis commercial track feed.
- METAR.
- AIREP and PIREP.
- Rapid Refresh weather forecast.
- Terminal Aerodrome Forecast (TAF).
- Time-Based Flow Management (TBFM).
- TRACON flight plans and tracks.

The prototype integration diagram specifically shows these source families
feeding an integrated ATM semantic data store:

- ASDI.
- METAR.
- TFM advisories.
- ERAM.
- airline, aircraft, and airport information.
- ASPM.
- other data sources.

## Current usability for this project

| Source family | Current access checked | Practical status | Usefulness for Aviation Agentic AI |
| --- | --- | --- | --- |
| METAR / TAF / PIREP-style weather data | https://aviationweather.gov/data/api/ responded on 2026-06-01 | Directly usable API for aviation weather observations/forecasts. | Strong candidate for an open, reproducible weather-data layer if the project pivots to ATM/NAS data. |
| FAA ATCSCC advisories / TMIs | http://www.fly.faa.gov/adv/advADB.jsp responded on 2026-06-01 | Public web endpoint appears reachable; likely HTML/query oriented rather than a clean bulk API. | Usable for a small reproducible scraper/prototype, with care around historical availability. |
| FAA ASPM | http://aspm.faa.gov responded on 2026-06-01 | Reachable, but likely portal/report oriented and may have access or workflow constraints for bulk extraction. | Potentially useful, but less straightforward than AviationWeather. Verify export/login requirements before depending on it. |
| FAA NASR / NFDC airport and aeronautical data | https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/ responded on 2026-06-01 | Public FAA aeronautical data source; not named directly in this presentation, but matches the airport/infrastructure data path used by the NASA ATM ontology documentation. | Strong candidate for airport/runway/fix/route reference data. |
| Rapid Refresh weather forecast | https://rapidrefresh.noaa.gov/ responded on 2026-06-01 | Public NOAA weather forecast product, but larger and more meteorological than simple METAR/TAF. | Useful later for weather-rich ATM experiments; probably too heavy for the first data route. |
| FAA SWIM | https://www.faa.gov/air_traffic/technology/swim responded on 2026-06-01 | Public program information is reachable; operational service access is not the same as open bulk data. | Good architectural reference, but not a simple data source without access setup. |
| ASDI | http://www.fly.faa.gov/ASDI/asdi.html responded on 2026-06-01 | Page reachable, but ASDI is generally an industry/subscriber feed, not an open historical dataset. | Not a near-term reproducible source unless credentials/access are available. |
| ERAM / ARTCC / TRACON tracks and flight plans | No public bulk endpoint identified from the PDF | Operational FAA/NASA warehouse-style data; likely not openly downloadable. | Treat as internal/prototype evidence, not a current project data source. |
| CIWS / CTAS / TBFM | No public bulk endpoint identified from the PDF | Operational/specialized FAA/NASA systems; likely restricted or not simple to reproduce. | Not near-term usable for a reproducible thesis data pipeline. |
| Exelis commercial track feed | No public open endpoint identified from the PDF | Commercial/proprietary feed. | Not suitable for open reproducible experiments unless separately licensed. |
| NASA Ames ATM Data Warehouse / integrated semantic data store | No public dataset dump identified from the PDF | Described as NASA prototype/internal warehouse; status slide says the ATM Ontology was a prototype and a test version was being deployed at NASA. | Useful as methodological evidence only; not a directly usable KG/dataset source. |

## Recommended data path

For a reproducible Aviation Agentic AI extension, the cleanest path from this
presentation is:

1. Use NASA ATM Ontology / ATMONTO as an external schema reference, not as full
   ground truth.
2. Use AviationWeather API data for METAR/TAF/PIREP-style weather observations.
3. Add FAA NASR/NFDC aeronautical reference data for airport/runway/fix/route
   entities.
4. Optionally add FAA ATCSCC advisories/TMIs if a stable historical retrieval
   route can be verified.
5. Defer ASDI, ERAM, TRACON, CIWS, CTAS, TBFM, and Exelis unless authenticated
   or licensed access is available.

## Bottom line

The presentation is excellent evidence that NASA's ATM ontology was designed for
multi-source semantic integration across NAS/ATM data. It is not, by itself, a
downloadable open KG or dataset release. The immediately usable open-data route
is weather plus aeronautical reference data, with advisories as a possible third
source after scraper/API feasibility is checked.
