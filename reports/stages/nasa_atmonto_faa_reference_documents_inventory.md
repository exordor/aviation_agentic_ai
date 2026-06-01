# NASA ATMONTO FAA Reference Documents

- Snapshot date: 2026-06-01
- Retrieved at: 2026-06-01T02:43:41+00:00
- Source family: `faa_reference_documents`
- Manifest: `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/manifest.json`

## Downloaded Sources

| Source | Group | Role | Format | ATMONTO modules | Local file |
| --- | --- | --- | --- | --- | --- |
| FAA Air Traffic Plans and Publications catalog | `air_traffic_publications` | `catalog` | `html` | atm, nas, gen | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/faa_air_traffic_publications_catalog.html` |
| Aeronautical Information Manual HTML entrypoint | `aim` | `structured_html_entrypoint` | `html` | atm, nas, gen, data | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/aim_html_index.html` |
| Aeronautical Information Manual Basic with Change 1 and 2 | `aim` | `reference_document` | `pdf` | atm, nas, gen, data | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/AIM_Basic_w_Chg_1_and_2_dtd_1-22-26.pdf` |
| Pilot/Controller Glossary HTML entrypoint | `pilot_controller_glossary` | `structured_html_entrypoint` | `html` | atm, nas, data, gen | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/pilot_controller_glossary_html_index.html` |
| Pilot/Controller Glossary Basic with Change 1 and 2 | `pilot_controller_glossary` | `terminology_reference` | `pdf` | atm, nas, data, gen | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/PCG_Bsc_w_Chg_1_and_2_dtd_1-22-26.pdf` |
| Aeronautical Information Publication HTML entrypoint | `aip` | `structured_html_entrypoint` | `html` | atm, nas, gen | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/aip_html_index.html` |
| Aeronautical Information Publication Basic | `aip` | `reference_document` | `pdf` | atm, nas, gen | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/AIP_Basic_dtd_1-22-26.pdf` |
| FAA Order JO 7110.65 Air Traffic Control HTML entrypoint | `jo_7110_65` | `structured_html_entrypoint` | `html` | atm, nas | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/jo_7110_65_atc_html_index.html` |
| FAA Order JO 7110.65BB Air Traffic Control | `jo_7110_65` | `procedure_reference` | `pdf` | atm, nas | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/7110.65BB_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf` |
| FAA Order JO 7210.3 Facility Operation and Administration HTML entrypoint | `jo_7210_3` | `structured_html_entrypoint` | `html` | atm, nas, gen | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/jo_7210_3_foa_html_index.html` |
| FAA Order JO 7210.3EE Facility Operation and Administration | `jo_7210_3` | `facility_reference` | `pdf` | atm, nas, gen | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/7210.3EE_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf` |
| Aviation Weather Handbook FAA detail page | `aviation_weather_handbook` | `catalog` | `html` | data, nas | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/aviation_weather_handbook_detail.html` |
| FAA-H-8083-28B Aviation Weather Handbook | `aviation_weather_handbook` | `weather_reference` | `pdf` | data, nas | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/FAA-H-8083-28B_Aviation_Weather_Handbook.pdf` |
| Aeronautical Chart Users' Guide FAA page | `chart_users_guide` | `catalog` | `html` | nas, gen, atm | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/aeronautical_chart_users_guide_page.html` |
| Aeronautical Chart Users' Guide complete PDF | `chart_users_guide` | `chart_reference` | `pdf` | nas, gen, atm | `data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/cug-complete_20260122.pdf` |

## Boundary

- These documents are reference and terminology sources for ATMONTO alignment.
- ABox event data should still come from AviationWeather, NASR, and ATCSCC snapshots.
- Procedure documents are for retrospective evidence-traceable QA, not operational use.
