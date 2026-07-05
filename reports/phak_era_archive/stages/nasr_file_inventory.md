# FAA NASR File Inventory

Source archive: `data/raw/nasa_atmonto/2026-05-14/faa_nasr/28DaySubscription_Effective_2026-05-14.zip`

Cycle semantics:

- Effective date: `2026-05-14`.
- Modeled source validity window: `[2026-05-14T00:00:00Z, 2026-06-11T00:00:00Z)`.
- The package is a complete NASR cycle snapshot, not a 7-day event stream.
- The README notes that this is a 56 Day Major Cycle subscriber set issued under the newer 28-day subscription cadence. Some enroute resources such as `ARB`, `ATS`, `AWY`, `CDR`, `MTR`, `PFR`, `PJA`, `STARDP`, and `WXL` may update on the 56-day charting basis.
- Legacy text geodetic coordinates should be treated as NAD 83 unless a specific file says otherwise.

## Top-Level Structure

| Path | Role | Project use |
| --- | --- | --- |
| `README.txt` | Release notes, effective date, cycle/cutoff notes, datum notes, and format-change warnings. | Keep as provenance and cycle interpretation evidence. |
| `*.txt` | Legacy subscriber data files, mostly fixed-width records. `CDR.txt` is comma-delimited legacy text. | Useful for cross-checking, but not the preferred parsing route because FAA is sunsetting legacy `.txt` files. |
| `Layout_Data/*_rf.txt` | Record layouts for legacy `.txt` files. | Use only when parsing legacy text is required. |
| `CSV_Data/14_May_2026_CSV.zip` | Main modern CSV subscriber package. | Preferred source for KG construction. |
| `State_&_Country_Codes/STATE.txt` | State code lookup table. | Normalize state references. |
| `State_&_Country_Codes/COUNTRY.txt` | Country code lookup table. | Normalize country references. |
| `Additional_Data/AIXM/AIXM_5.1/XML-Subscriber-Files/*.zip` | AIXM XML versions for selected NASR products. | Alternative source if using AIXM-native parsing. |
| `Additional_Data/AIXM/AIXM_5.1/mappings/*.xls` | Mapping from FAA subscriber files to AIXM 5.1. | Useful for ontology/schema mapping decisions. |
| `Additional_Data/AIXM/AIXM_5.1/FAQs/*.doc` | AIXM product-specific FAQ documents. | Supporting documentation. |
| `Additional_Data/AIXM/AIXM_5.1/AIXM/xsd/**` | AIXM 5.1, GML, ISO 19136/19139, xlink, and message schemas. | XML validation and schema reference, not primary KG records. |
| `Additional_Data/AIXM/AIXM_5.1/AIXM/extension/*.xsd` | FAA subscriber-file AIXM extension schemas for Airport, Airway, AWOS, Navaid, and subscriber wrapper messages. | Schema reference for AIXM ingestion. |
| `Additional_Data/AIXM/SAA-AIXM_5_Schema/*` | Special Activity Airspace AIXM schema, subscriber zip, and text-to-AIXM mapping. | Relevant if modeling special-use/activity airspace. |
| `Additional_Data/Shape_Files/Class_Airspace.*` | Shapefile set for class airspace geometry: `.shp`, `.shx`, `.dbf`, `.prj`. | Best geometry source for controlled-airspace polygons. |

## Legacy Subscriber Files

These are top-level legacy files. The corresponding `Layout_Data/*_rf.txt` file explains record types, positions, and field lengths.

| File | Approx. records/lines | Role |
| --- | ---: | --- |
| `AFF.txt` | 7,304 | ARTCC facilities and communications: RCAG, ARSR, secondary radar, CERAP, frequencies, and remarks under U.S. area of responsibility. |
| `APT.txt` | 151,398 | Landing facility data: airports, heliports, seaplane bases, runways, runway ends, contacts, remarks, services, and facility attributes. |
| `ARB.txt` | 2,688 | ARTCC boundary segment descriptions. Useful for center boundary geometry. |
| `ATS.txt` | 4,148 | ATS airway data. Includes non-regulatory/special route information. |
| `AWOS.txt` | 2,916 | ASOS/AWOS weather observation station metadata. |
| `AWY.txt` | 36,542 | Airway definitions and segment altitude information. |
| `CDR.txt` | 41,213 | Coded Departure Routes. This legacy file is comma-delimited and route-oriented rather than fixed-width. |
| `COM.txt` | 1,057 | Flight service station communications facilities. |
| `FIX.txt` | 201,735 | Radio fixes/reporting points, charting uses, and navaid relationships. |
| `FSS.txt` | 93 | Flight service stations. |
| `HPF.txt` | 44,923 | Holding pattern definitions, charting information, speed/altitude notes, and remarks. |
| `ILS.txt` | 10,751 | ILS systems and components: localizer, glide slope, DME, markers, and remarks. |
| `LID.txt` | 22,315 | Location identifiers and the facility/service types using each identifier. |
| `MAA.txt` | 960 | Miscellaneous Activity Areas: base data, polygon coordinates, times of use, user/contact data, NOTAM notes, and remarks. |
| `MTR.txt` | 30,856 | Military Training Routes: route points, widths, terrain notes, SOP text, and agency data. |
| `NAV.txt` | 8,250 | Navaids: VOR, NDB, TACAN, DME, status, coordinates, service data, checkpoints, and remarks. |
| `PFR.txt` | 87,492 | Preferred routes and route segment strings. |
| `PJA.txt` | 1,746 | Parachute Jump Areas and associated contact/frequency data. |
| `STARDP.txt` | 37,289 | Standard Terminal Arrivals and Departure Procedures in the legacy combined format. |
| `TWR.txt` | 25,837 | Terminal communications services, including tower/terminal facility service data. |
| `WXL.txt` | 3,434 | Weather reporting locations and weather services. |

## CSV Package

Use `CSV_Data/14_May_2026_CSV.zip` as the primary machine-readable input. Every table that contains `EFF_DATE` should be treated as cycle-effective reference data. `*_CSV_DATA_STRUCTURE.csv` files describe the table schemas. `* DATA LAYOUT.pdf` files provide human-readable layouts. `CSV_README.pdf`, `CSV_CHG_RPT_README.pdf`, and `16_Apr_2026_CSV-14_May_2026_CSV.zip` document CSV usage and cycle-to-cycle changes.

### Airport And Landing Facilities

| CSV file | Rows | Role |
| --- | ---: | --- |
| `APT_BASE.csv` | 19,410 | Primary landing-facility table: airport/site identity, name, location, ownership/use, coordinates, elevation, certification, and operational attributes. |
| `APT_RWY.csv` | 23,185 | Runway-level data: runway identifiers, dimensions, surface, condition, lighting, and related runway attributes. |
| `APT_RWY_END.csv` | 39,876 | Runway-end data: alignment, traffic pattern, lighting/marking, thresholds, approach aids, and displaced/declared-distance style attributes. |
| `APT_CON.csv` | 38,898 | Airport contacts and administrative contact records. |
| `APT_RMK.csv` | 89,934 | Airport remarks linked back to base/runway/runway-end fields. |
| `APT_ATT.csv` | 18,004 | Airport attendance/service schedule records by month/day/hour. |
| `APT_ARS.csv` | 465 | Aircraft arresting-system information by airport/runway end. |
| `CLS_ARSP.csv` | 961 | Class B/C/D/E airspace indicators and hours associated with airports. |
| `MIL_OPS.csv` | 197 | Military operations service data at airports. |

### Air Traffic And Communications

| CSV file | Rows | Role |
| --- | ---: | --- |
| `ATC_BASE.csv` | 3,617 | ATC facility base table: facility IDs, ICAO IDs, names, tower/ATC operator data, and location attributes. |
| `ATC_SVC.csv` | 1,071 | ATC control-service records attached to ATC facilities. |
| `ATC_ATIS.csv` | 616 | ATIS descriptions, hours, and phone numbers. |
| `ATC_RMK.csv` | 3,176 | Remarks for ATC facilities and services. |
| `FRQ.csv` | 40,767 | Facility/service frequencies, including serviced facility, ARTCC/FSS context, CPDLC indicator, and coordinates. |
| `COM.csv` | 1,822 | Communications outlets/facilities, commonly linked to navaids, FSS, or service locations. |
| `FSS_BASE.csv` | 75 | Flight Service Station base records. |
| `FSS_RMK.csv` | 29 | FSS remarks. |
| `RDR.csv` | 373 | Radar facility data and radar-hour notes. |

### Navigation Points, Navaids, And Instrument Systems

| CSV file | Rows | Role |
| --- | ---: | --- |
| `NAV_BASE.csv` | 1,634 | Navaid base records: ID/type/status/name/location/frequency/service and detailed technical attributes. |
| `NAV_CKPT.csv` | 189 | Navaid checkpoint records. |
| `NAV_RMK.csv` | 2,000 | Navaid remarks. |
| `FIX_BASE.csv` | 70,003 | Fix/reporting-point base records with coordinates, ICAO region, state/country, and fix metadata. |
| `FIX_NAV.csv` | 26,729 | Fix-to-navaid relationships, including bearing and distance. |
| `FIX_CHRT.csv` | 105,002 | Fix charting-use classifications. |
| `ILS_BASE.csv` | 1,558 | ILS base records by airport/runway end/localizer/system type. |
| `ILS_DME.csv` | 922 | ILS-associated DME component data. |
| `ILS_GS.csv` | 1,380 | ILS glide-slope component data. |
| `ILS_MKR.csv` | 402 | ILS marker component data. |
| `ILS_RMK.csv` | 3,039 | ILS remarks by component or system field. |
| `LID.csv` | 31,046 | Location identifier registry connecting IDs to facility types, names, cities, ARTCC/FSS references, and groups. |

### Routes, Procedures, And Flow-Management References

| CSV file | Rows | Role |
| --- | ---: | --- |
| `AWY_BASE.csv` | 1,519 | Airway base records and airway strings. |
| `AWY_SEG_ALT.csv` | 19,318 | Airway segment points, altitude constraints, courses, MEA/MAA-style values, and ARTCC context. |
| `CDR.csv` | 41,212 | Coded Departure Routes: origin, destination, departure fix, route string, center coordination fields, navigation equipment, and length. |
| `PFR_BASE.csv` | 13,309 | Preferred route base records by origin/destination/type/route number and area/altitude/aircraft metadata. |
| `PFR_SEG.csv` | 74,182 | Preferred route segments and segment types. |
| `PFR_RMT_FMT.csv` | 13,309 | Route Management Tool style preferred-route format. |
| `DP_BASE.csv` | 1,192 | Departure procedure base records. |
| `DP_APT.csv` | 6,413 | Airports/runways served by departure procedures. |
| `DP_RTE.csv` | 12,221 | Departure procedure route points and transitions. |
| `STAR_BASE.csv` | 686 | Standard terminal arrival base records. |
| `STAR_APT.csv` | 3,356 | Airports/runways served by STARs. |
| `STAR_RTE.csv` | 17,527 | STAR route points and transitions. |
| `HPF_BASE.csv` | 15,565 | Holding-pattern base data. |
| `HPF_CHRT.csv` | 16,208 | Holding-pattern charting classifications. |
| `HPF_SPD_ALT.csv` | 17,914 | Holding-pattern speed and altitude constraints. |
| `HPF_RMK.csv` | 141 | Holding-pattern remarks. |

### Airspace, Activity Areas, And Special Operations

| CSV file | Rows | Role |
| --- | ---: | --- |
| `ARB_BASE.csv` | 38 | ARTCC boundary base records. |
| `ARB_SEG.csv` | 2,687 | ARTCC boundary segment coordinates. |
| `MAA_BASE.csv` | 172 | Miscellaneous Activity Area base records. |
| `MAA_SHP.csv` | 507 | MAA polygon point coordinates. |
| `MAA_CON.csv` | 3 | MAA contact/frequency records. |
| `MAA_RMK.csv` | 93 | MAA remarks. |
| `MTR_BASE.csv` | 518 | Military Training Route base records and time-of-use information. |
| `MTR_PT.csv` | 5,884 | MTR route points and segment text. |
| `MTR_AGY.csv` | 1,036 | MTR agency/contact records. |
| `MTR_SOP.csv` | 20,787 | MTR special operating procedure text. |
| `MTR_TERR.csv` | 979 | MTR terrain text. |
| `MTR_WDTH.csv` | 1,651 | MTR width text. |
| `PJA_BASE.csv` | 688 | Parachute Jump Area base records. |
| `PJA_CON.csv` | 150 | PJA contact/frequency records. |

### Weather And Observation Infrastructure

| CSV file | Rows | Role |
| --- | ---: | --- |
| `AWOS.csv` | 2,647 | ASOS/AWOS station records with type, commissioning date, navaid flag, and coordinates. |
| `WXL_BASE.csv` | 3,363 | Weather reporting location base records. |
| `WXL_SVC.csv` | 10,725 | Weather service types and affected areas. |

## Documentation And Schema Files In CSV Package

| File pattern | Role |
| --- | --- |
| `*_CSV_DATA_STRUCTURE.csv` | Machine-readable schema for each CSV product group: table name, column name, max length, data type, and nullability. |
| `* DATA LAYOUT.pdf` | Human-readable layout documentation for the corresponding product group. |
| `CSV_README.pdf` | General CSV package usage notes. |
| `CSV_CHG_RPT_README.pdf` | Change-report documentation. |
| `16_Apr_2026_CSV-14_May_2026_CSV.zip` | Cycle-to-cycle CSV change report from the previous cycle to the current effective cycle. |

## KG/Ontology Relevance

Recommended ingestion order for the project KG:

1. Airport core: `APT_BASE`, `APT_RWY`, `APT_RWY_END`, `APT_ATT`, `APT_ARS`, `CLS_ARSP`.
2. Navigation core: `NAV_BASE`, `FIX_BASE`, `FIX_NAV`, `FIX_CHRT`, `ILS_*`, `AWOS`, `WXL_*`.
3. Airspace and route structure: `AWY_*`, `DP_*`, `STAR_*`, `PFR_*`, `CDR`, `HPF_*`.
4. Operations/control context: `ATC_*`, `FRQ`, `COM`, `FSS_*`, `RDR`.
5. Special-use/activity context: `MAA_*`, `MTR_*`, `PJA_*`, `ARB_*`, `Class_Airspace.shp`.
6. Remarks: `*_RMK` tables should be retained, but usually indexed as textual evidence rather than treated as clean structured truth.

Candidate ontology entities and relations:

- `Airport`, `Runway`, `RunwayEnd`, `AirspaceClass`, `ATCFacility`, `Frequency`, `Navaid`, `Fix`, `ILSSystem`, `WeatherStation`, `Airway`, `RouteSegment`, `DepartureProcedure`, `ArrivalProcedure`, `PreferredRoute`, `HoldingPattern`, `ActivityArea`, `MilitaryTrainingRoute`, `ParachuteJumpArea`.
- Useful relations include `hasRunway`, `hasRunwayEnd`, `servedBy`, `locatedIn`, `hasFrequency`, `usesNavaid`, `fixDefinedByNavaid`, `routeHasSegment`, `procedureServesAirport`, `airwayContainsFix`, `areaHasBoundaryPoint`, and `effectiveDuringCycle`.

Parsing recommendation:

- Prefer CSV tables over legacy `.txt`.
- Preserve `EFF_DATE` on every structured node or relation.
- Treat `[2026-05-14T00:00:00Z, 2026-06-11T00:00:00Z)` as the NASR cycle interval.
- Use CSV structure files for schema validation and field typing.
- Use AIXM mapping files only if a later phase needs AIXM-compatible export or semantic crosswalks.
