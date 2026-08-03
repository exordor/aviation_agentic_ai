# Same-Date Source Completeness Gate

Audit date: 2026-08-02
Target date: 2014-07-15
Geographic scope: KJFK, KEWR, KLGA and the associated ZNY/NYC control scope
Model: `deepseek-v4-flash`
Model calls made during this audit: **0**

This gate separates source acquisition from the later LLM-to-KG experiment.
The NASA `atmontoPlus` package remains a processed RDF/Turtle reference ABox;
it is not counted as source-native input for the extraction experiment.

## Source matrix

| Source family | Required role | Source-native artifact | Status | Evidence of coverage |
|---|---|---|---|---|
| FAA ATCSCC advisories | decision/TMI text and lifecycle fields | `data/raw/atmonto_reconstruction/2014-07-15-nyc/atcscc/` | **complete** | Full dated advisory index plus 33 NYC/ZNY detail pages; index SHA-256 `a5ff9ef523faa792467c1a2f3413e04ac15dc9b34d3e7e593ab4690e33f608f9` |
| METAR | observed weather | `weather/iem/{JFK,EWR,LGA}_2014-07-15.csv` | **complete** | 49 + 43 + 41 source rows, all dated 2014-07-15; raw METAR strings retained |
| TAF | forecast context | `weather/iem_taf/{KJFK,KEWR,KLGA}_2014-07-15.csv` | **complete** | 109 + 114 + 81 source rows and 42 distinct products across the three stations |
| FAA NASR | airport, navaid, fix, airway, SID/STAR and reference geometry | `nasr/subsc_29_May_2014_effdate.zip` | **complete for reference scope** | 2014-05-29 effective-cycle archive, SHA-256 `55ef12054467309fd165d9a5112e35678b37808e5949b36eb53b67aae0c18a18`; archive contains APT, AWOS, AWY, FIX, ILS, NAV, STARDP, TWR, WXL and shape-file members |
| BTS On-Time | public flight operation/outcome observations | `bts/On_Time_Reporting_Carrier_On_Time_Performance_1987_2014_7.zip` | **complete for operational observations** | July 2014 source ZIP, SHA-256 `bde5f2c417d54102389cbc5d1bc5bb9e9e67b16cc12a70f61efff681d8e5e521`; 17,395 rows for 2014-07-15 and 592/681/657 rows touching JFK/EWR/LGA |
| NASA ATMONTO/ATMGRAPH sample | comparison ABox and competency-question baseline | `data/raw/nasa_atmonto_prototype/allFilesTTL.zip` | **reference only** | Checksum-pinned processed RDF/Turtle; not raw input and not included in the LLM prompt |
| ASDI/flight tracks | raw trajectory and flight-plan evidence | `asdi/asdi_2014_07_01.csv.bz2` | **acquired, but not target-date complete** | Sandia/Tracktable source-native ASDI sample; 4,735,143 records spanning 2014-07-01 06:00:00 through 2014-07-04 07:43:36; 62,478 records fall in the NYC bounding box. It does not cover 2014-07-15. |
| ASPM flight-level/airport-hour data | airport performance and demand/capacity context | no captured 2014 source-native export; official 2014 capacity profiles under `aspm/official_capacity_profiles/` | **raw export blocked; official derivative acquired** | The public ASPM query was probed and the POST endpoint returned a server error. FAA documentation says detailed Data Download and restricted flight-level areas require access, while public Airport Analysis is available after finalization. The PDFs are official derivative reports, not daily ASPM rows. |
| Historical aircraft registry | date-valid tail-to-model mapping | `aircraft_registry/ReleasableAircraft.2014.zip` | **acquired annual snapshot, not point-in-time complete** | FAA yearly archive replay; ZIP integrity passed, with `MASTER.TXT`, `AcftRef.TXT` and `Dereg.TXT`; 426,502 `MASTER.TXT` rows. It is a 2014 annual archive, not a registry snapshot captured on 2014-07-15. |

## Gate decision

The five source families needed for a bounded **TMI + weather + facility + public
operations** extraction slice are locally present. Two previously missing source
families now have bounded acquisitions: a source-native ASDI sample and a 2014
annual FAA registry archive. Neither is same-date complete for 2014-07-15. A raw
historical ASPM export is still not captured; the downloaded FAA capacity profiles
are official derivative documents only. The same-date NASA-alignment experiment
is therefore **NOT READY**. These gaps must not be silently filled with the
processed NASA ABox, current registry data, or an undocumented trajectory
substitute.

The LLM experiment therefore remains closed:

```text
source completeness gate = NOT PASSED
DeepSeek V4 Flash calls = 0
```

## Accepted completion paths for the blocked layers

1. Obtain a source covering the target date (2014-07-15) for ASDI and a
   point-in-time registry snapshot, and obtain the historical ASPM export under
   an approved access arrangement; or
2. Move the experiment date to the acquired ASDI window and reacquire the
   advisory/weather/TAF/BTS sources for that date, while retaining the annual
   registry and official ASPM derivative as explicitly bounded evidence; or
3. Explicitly narrow the research question to the acquired source families and
   declare raw ASPM and same-date flight/registry alignment out of scope; or
4. Approve an identified public substitute (for example, OpenSky) as a separate
   source family, with its own temporal/coverage audit. It must not be presented
   as FAA ASDI or silently joined to the NASA reference ABox.

Only after one of these paths is recorded will the next stage create sealed
evidence cards and authorize `deepseek-v4-flash` candidate-fact generation.

## Source references

- FAA advisory archive: <https://www.fly.faa.gov/adv/advADB.jsp>
- FAA 2014 NASR archive: <https://aeronav.faa.gov/Upload_313-d/blind_data/July_NASR_Subscriber_Files/2004_2023_July_NASR_Subscribers/2014/>
- BTS TranStats archive: <https://www.transtats.bts.gov/PREZIP/>
- IEM ASOS/METAR request service: <https://mesonet.agron.iastate.edu/request/download.phtml>
- IEM TAF request service: <https://mesonet.agron.iastate.edu/request/taf.phtml>
- Sandia/Tracktable Purdue ASDI sample: <https://tracktable.sandia.gov/purdue/>
- FAA current aircraft registry download description: <https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download>
- FAA 2014 annual registry archive replay: <https://web.archive.org/web/20240926172725id_/https://registry.faa.gov/database/yearly/ReleasableAircraft.2014.zip>
- FAA ASPM data documentation: <https://www.aspm.faa.gov/aspmhelp/index/Aviation_System_Performance_Metrics_%28ASPM%29.html>
- FAA 2014 airport capacity profiles: <https://www.faa.gov/airports/planning_capacity/profiles>
- NASA ATMONTO release: <https://data.nasa.gov/docs/ontologies/atmonto/index.html>
