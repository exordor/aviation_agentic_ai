# NASA ATMONTO Temporal Alignment

- Snapshot date: 2026-05-14
- Policy: fixed historical UTC window selected before retrieval
- Aligned window: 2026-05-14T00:00:00Z to 2026-05-21T00:00:00Z
- Boundary rule: inclusive for instant records; interval records are included when they intersect the window

## Source Coverage

- aviationweather_metar: 2026-05-14T00:00:00Z to 2026-05-21T00:00:00Z (AviationWeather METAR query window; individual records are filtered by reportTime)
- aviationweather_taf: 2026-05-14T00:00:00Z to 2026-05-21T00:00:00Z (AviationWeather TAF query timestamps covering fixed window; records are filtered by validity interval)
- faa_nasr: 2026-05-14T00:00:00Z to 2026-06-11T00:00:00Z (28-day effective cycle)
- atcscc_advisories: 2026-05-14T00:00:00Z to 2026-05-21T00:00:00Z (advisory database dates covering fixed alignment window)

## Aligned Outputs

- aviationweather_metar: 518 records, `data/processed/nasa_atmonto/aligned/2026-05-14/aviationweather_metar.jsonl`
- aviationweather_taf: 87 records, `data/processed/nasa_atmonto/aligned/2026-05-14/aviationweather_taf.jsonl`
- aviationweather_stationinfo: 3 records, `data/processed/nasa_atmonto/aligned/2026-05-14/aviationweather_stationinfo.jsonl`
- faa_nasr_zip_inventory: 147 records, `data/processed/nasa_atmonto/aligned/2026-05-14/faa_nasr_zip_inventory.jsonl`
- atcscc_advisories: 718 records, `data/processed/nasa_atmonto/aligned/2026-05-14/atcscc_advisories.jsonl`
- temporal_alignment_manifest: 1 records, `data/processed/nasa_atmonto/aligned/2026-05-14/temporal_alignment_manifest.json`

## Limitations

- The aligned window is a fixed past UTC window selected before retrieval and verified against each source coverage.
- NASR is cycle-valid reference data; every zip member is attached as the reference layer covering the aligned window.
- ATCSCC advisory intervals are parsed from public HTML text and should be reviewed before treating them as gold timestamps.
