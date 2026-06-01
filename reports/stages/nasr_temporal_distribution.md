# FAA NASR Temporal Distribution

Source archive: `data/raw/nasa_atmonto/2026-05-14/faa_nasr/28DaySubscription_Effective_2026-05-14.zip`

## Main Conclusion

The NASR files do not have separate 7-day windows. They share one cycle-level validity window:

- Cycle effective date: `2026-05-14`.
- Modeled NASR source window: `[2026-05-14T00:00:00Z, 2026-06-11T00:00:00Z)`.
- Experiment alignment window: `[2026-05-14T00:00:00Z, 2026-05-21T00:00:00Z]`.

For the experiment, NASR should therefore be modeled as a cycle-valid reference layer. The 7-day experiment window is only a subset of the NASR cycle used to align dynamic sources such as METAR, TAF, and ATCSCC advisories.

## Cycle-Level Distribution

| Layer | Time meaning | Window |
| --- | --- | --- |
| NASR subscriber package | Whole package effective cycle | `[2026-05-14T00:00:00Z, 2026-06-11T00:00:00Z)` |
| CSV data tables with `EFF_DATE` | Row-level cycle effective date | all rows have `2026/05/14` |
| CSV change report package | Difference between previous and current CSV cycles | `2026-04-16` to `2026-05-14` |
| Experiment alignment | Project-selected dynamic-data alignment window | `[2026-05-14T00:00:00Z, 2026-05-21T00:00:00Z]` |
| Legacy layout docs | Documentation/schema version dates | layout dates range roughly `2012-04-05` to `2026-03-19`; not source data validity |

README notes:

- The files are effective `May 14, 2026`.
- Data published in NFDD through `NFDD 070 dated 04/13/2026` is incorporated.
- This package is a 56 Day Major Cycle subscriber set under the 28-day subscription cadence.
- Some enroute resources may not contain new data in every 28-day set: `ARB`, `ATS`, `AWY`, `CDR`, `MTR`, `PFR`, `PJA`, `STARDP`, and `WXL`.

## CSV `EFF_DATE` Distribution

There are 63 CSV data tables in `CSV_Data/14_May_2026_CSV.zip`.

| Group | Count | Distribution |
| --- | ---: | --- |
| Tables with `EFF_DATE` | 61 | every parsed row has `EFF_DATE = 2026/05/14` |
| Tables without `EFF_DATE` | 2 | `CDR.csv`, `PFR_RMT_FMT.csv` |

Interpretation:

- `EFF_DATE = 2026/05/14` is the cycle effective date, not an observation timestamp.
- Most KG nodes and reference edges derived from CSV should carry `effective_cycle_start = 2026-05-14T00:00:00Z` and `effective_cycle_end_exclusive = 2026-06-11T00:00:00Z`.
- `CDR.csv` and `PFR_RMT_FMT.csv` should inherit the package cycle because they do not carry row-level `EFF_DATE`.

## Internal Historical Date Fields

Some CSV fields contain historical metadata dates. These are not the source validity window; they describe activation dates, survey/source dates, amendment dates, component status dates, or update dates.

| File | Field | Non-empty rows | Approx. date span | Meaning |
| --- | ---: | ---: | --- | --- |
| `APT_BASE.csv` | `ACTIVATION_DATE` | 18,495 | `1902-07` to `2026-04` | Facility activation/opening month. |
| `APT_BASE.csv` | `ARFF_CERT_TYPE_DATE` | 518 | `1972-09` to `2024-10` | ARFF certification type date. |
| `APT_BASE.csv` | `POSITION_SRC_DATE` | 13,424 | `1970-02-27` to `2925-11-07` | Position source/survey date; includes apparent data-quality outliers. |
| `APT_BASE.csv` | `ELEVATION_SRC_DATE` | 11,164 | `1968-08-01` to `2026-04-07` | Elevation source/survey date. |
| `APT_RWY.csv` | `LENGTH_SOURCE_DATE` | 12,826 | `0021-04-28` to `2028-06-25` | Runway length source date; includes apparent data-quality outliers. |
| `APT_RWY_END.csv` | `RWY_END_PSN_DATE` | 22,627 | `0024-01-02` to `2026-04-07` | Runway-end position source date; includes apparent data-quality outliers. |
| `APT_RWY_END.csv` | `RWY_END_ELEV_DATE` | 20,520 | `1968-08-01` to `2026-04-07` | Runway-end elevation source date. |
| `APT_RWY_END.csv` | `RWY_END_DSPL_THR_PSN_DATE` | 2,183 | `0224-03-22` to `2026-03-25` | Displaced-threshold position source date; includes apparent data-quality outliers. |
| `APT_RWY_END.csv` | `RWY_END_DSPL_THR_ELEV_DATE` | 1,950 | `1987-05-07` to `2026-03-25` | Displaced-threshold elevation source date. |
| `APT_RWY_END.csv` | `RWY_END_TDZ_ELEV_DATE` | 10,839 | `0025-04-02` to `2033-03-22` | Touchdown-zone elevation source date; includes apparent data-quality outliers. |
| `APT_RWY_END.csv` | `RWY_END_LAHSO_PSN_DATE` | 194 | `2007-07-11` to `2025-07-29` | LAHSO position source date. |
| `AWOS.csv` | `COMMISSIONED_DATE` | 1,725 | `1983-08-19` to `2026-03-19` | Weather-station commissioning date. |
| `AWY_BASE.csv` | `UPDATE_DATE` | 1,519 | `1979-11-05` to `2026-03-31` | Airway record update date. |
| `COM.csv` | `COMM_STATUS_DATE` | 488 | `1972-05-01` to `2025-05-13` | Communications facility status date. |
| `DP_BASE.csv` | `DP_AMEND_EFF_DATE` | 1,192 | `0202-10-02` to `2026-05-14` | Departure-procedure amendment effective date; includes apparent data-quality outliers. |
| `FSS_BASE.csv` | `UPDATE_DATE` | 75 | `2020-07-13` to `2026-03-26` | Flight Service Station update date. |
| `ILS_BASE.csv` | `COMPONENT_STATUS_DATE` | 1,558 | `1901-01-01` to `2026-03-16` | ILS base component status date. |
| `ILS_DME.csv` | `COMPONENT_STATUS_DATE` | 922 | `1901-01-01` to `2026-03-16` | ILS DME status date. |
| `ILS_GS.csv` | `COMPONENT_STATUS_DATE` | 1,380 | `1901-01-01` to `2026-02-24` | ILS glide-slope status date. |
| `ILS_MKR.csv` | `COMPONENT_STATUS_DATE` | 402 | `1901-01-01` to `2026-02-11` | ILS marker status date. |
| `STAR_BASE.csv` | `STAR_AMEND_EFF_DATE` | 686 | `1993-11-11` to `2026-05-14` | STAR amendment effective date. |

Interpretation:

- These fields should be preserved as properties such as `activationDate`, `sourceSurveyDate`, `statusDate`, `updateDate`, or `procedureAmendmentEffectiveDate`.
- They should not be used to determine whether the row belongs to the `2026-05-14` NASR cycle.
- Values with impossible or future-looking years, for example `0021`, `0024`, `0202`, `2033`, or `2925`, should be flagged during normalization instead of silently trusted.

## Change Report Temporal Window

The nested file `16_Apr_2026_CSV-14_May_2026_CSV.zip` contains 51 change-report files. Its temporal meaning is:

- Previous CSV cycle: `2026-04-16`.
- Current CSV cycle: `2026-05-14`.
- Role: cycle-to-cycle delta report, not the full current snapshot.

Use this package only if the experiment needs provenance such as added/removed/changed NASR rows between cycles. For the current KG baseline, use the full `14_May_2026_CSV.zip` snapshot.

## Legacy Layout Date Distribution

The `Layout_Data/*_rf.txt` files include documentation effective dates. These dates identify layout/documentation versions, not row validity windows.

| Layout file | Information effective date |
| --- | --- |
| `Twr_rf.txt` | `04/05/2012 CHARTING CYCLE` |
| `awos_rf.txt` | `04/05/2012 CHARTING CYCLE` |
| `arb_rf.txt` | `04/05/2012` |
| `fss_rf.txt` | `04/05/2012` |
| `ils_rf.txt` | `04/05/2012` |
| `Stardp_rf.txt` | `02/06/2014` |
| `com_rf.txt` | `02/06/2014` |
| `pja_rf.txt` | `02/06/2014` |
| `maa_rf.txt` | `10/12/2017` |
| `mtr_rf.txt` | `07/19/2018` |
| `pfr_rf.txt` | `07/19/2018` |
| `Wxl_rf.txt` | `6/17/2021 CHARTING CYCLE` |
| `ats_rf.txt` | `6/17/2021` |
| `awy_rf.txt` | `6/17/2021` |
| `nav_rf.txt` | `9/9/2021` |
| `lid_rf.txt` | `09/07/2023` |
| `aff_rf.txt` | `6/13/2024` |
| `apt_rf.txt` | `11/27/2025 CHARTING CYCLE` |
| `fix_rf.txt` | `03/19/2026` |
| `hpf_rf.txt` | `03/19/2026` |
| `Cdr_rf.txt` | no `INFORMATION EFFECTIVE DATE` found in the header |

## Recommended Temporal Model

For KG construction:

1. Attach `nasrCycleEffectiveDate = 2026-05-14` and `effectiveDuringCycle = [2026-05-14T00:00:00Z, 2026-06-11T00:00:00Z)` to NASR-derived nodes and structured relations.
2. Preserve row-level `EFF_DATE` where present; inherit the package cycle for `CDR.csv` and `PFR_RMT_FMT.csv`.
3. Store internal date fields separately with their original field names and semantic role.
4. Flag outlier date values before temporal reasoning or evaluation.
5. Do not align NASR by a 7-day event window; align dynamic sources to the 7-day window while using NASR as the reference cycle layer.
