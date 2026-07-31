# ATMONTO Competency-Query Data Supplement

This deterministic sidecar fills flight, aircraft-type, weather, and sector-trajectory data gaps without entering the authoritative evidence store or public Query Agent runtime.

## Results

| Query | Executed form | Result |
|---|---|---:|
| F1 | Modern May 2026 proxy | 616 actual departures (624 BTS records) |
| F3S | Modern KATL temporal association | 81 flights |
| S4 | NASA 2014 sample, hour 02 UTC | KLGAairportSector: 12 flights / 146 track-point bindings |
| S1S | NASA 2014 sample, ZTLsector040 | 3 pairs |

## Interpretation boundaries

- F1 and F3S are modern proxy executions because the original 2012 KATL dataset is not publicly available in the recovered bundle.
- F3S is a symmetric time association around explicit rain observations; it is not a causal claim.
- S4 reports both distinct flights and the appendix's track-point binding count.
- NASA 2014 flight-track data remains a local, checksum-bound source and is not redistributed by this repository.
- FAA aircraft-registry processing retains only tail-to-manufacturer/model fields; owner and address fields are not materialized.

## Pinned sources

| Source | Role | SHA-256 |
|---|---|---|
| bts_on_time_2026_05 | public_flight_operation_records | `4e7b96999440afec8c92dd23bfbc68a5852e14d9a56c3d0d366f884542ea80b3` |
| faa_aircraft_registry_2026_07_28 | non_personal_aircraft_manufacturer_model_lookup | `8e42c757a3db24cfcd76638f04d151aa2843bd77d5358f7f847fa661331efe7a` |
| faa_nasr_2026_05_14 | airport_to_artcc_reference_snapshot | `db4793352229c1fd74e9b3d924762376abfa224fe6388768cad25d084c7aeed3` |
| iem_katl_metar_2026_05_14_22 | historical_katl_metar_routine_and_special_observations | `be6ef673b82cf39779aacaa57008372464f1a81951c692e08a09689223371f85` |
| nasa_atmonto_plus | published_2014_flight_track_and_sector_sample | `93dc9675772649079bef11fe3519e6d99fe0d549318a6696af888b7f2b74df47` |
