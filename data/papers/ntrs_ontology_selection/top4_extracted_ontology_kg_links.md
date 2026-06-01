# Extracted ontology, KG, and data-source links from top-priority NTRS PDFs

Scope: priority 1-4 items from the NTRS ontology selection:

- `20170006095_nasa_air_traffic_management_ontology.pdf`
- `20190000227_ontologies_for_aviation_data_management.pdf`
- `20190000452_nasa_atm_ontology_semantic_integration_querying.pdf`
- `20160007964_semantic_representation_integrated_atm_data.pdf`

Note: These are links mentioned in the PDFs or direct modern equivalents for old
PDF links. Some FAA/NASA links in the papers are historical and may now return
404 or have moved.

## Most relevant for Aviation Agentic AI

| Resource | Link | Type | Mentioned in | Notes |
| --- | --- | --- | --- | --- |
| NASA ATM Ontology namespace: general | http://atmweb.arc.nasa.gov/ontology/general# | Ontology namespace | 20170006095 | Namespace URI for general temporal, spatial, and sequencing classes. The host did not respond during a live check. |
| NASA ATM Ontology namespace: equipment | http://atmweb.arc.nasa.gov/ontology/eqp# | Ontology namespace | 20170006095 | Namespace URI for aircraft and equipment concepts. The host did not respond during a live check. |
| NASA ATM Ontology namespace: NAS | http://atmweb.arc.nasa.gov/ontology/nas# | Ontology namespace | 20170006095 | Namespace URI for NAS infrastructure concepts. The host did not respond during a live check. |
| NASA ATM Ontology namespace: ATM | http://atmweb.arc.nasa.gov/ontology/atm# | Ontology namespace | 20170006095 | Namespace URI for ATM flight, route, advisory, and constraint concepts. The host did not respond during a live check. |
| NASA ATM Ontology namespace: data | http://atmweb.arc.nasa.gov/ontology/data# | Ontology namespace | 20170006095 | Namespace URI for METAR, TAF, ASPM, and airport data classes. The host did not respond during a live check. |
| FIXM | https://www.fixm.aero/ | Aviation exchange model | 20190000227, 20190000452 | Flight Information Exchange Model. |
| AIXM | https://www.aixm.aero/ | Aviation exchange model | 20190000227, 20190000452 | Aeronautical Information Exchange Model. |
| WXXM | http://www.wxxm.aero/public/subsite_homepage/homepage.html | Aviation weather exchange model | 20190000227, 20190000452 | Historical PDF link for Weather Information Exchange Model. |
| FAA SWIM | http://www.faa.gov/nextgen/programs/swim/ | Aviation data/service framework | 20190000227, 20190000452 | System Wide Information Management. |
| FAA NAS Service Registry and Repository | https://nsrr.faa.gov/ | Service registry | 20190000227 | PDF-listed NSRR link. The host did not respond during a live check. |

## Public or semi-public aviation data sources

| Resource | PDF link | Current/usable link checked | Type | Mentioned in | Notes |
| --- | --- | --- | --- | --- | --- |
| OpenFlights airline data | http://openflights.org/data.html#airline | https://openflights.org/data.php | Open airline data | 20170006095 | PDF link returned 404 during a live check; current data page responded. |
| OpenFlights airport data | http://openflights.org/data.html#airport | https://openflights.org/data.php | Open airport data | 20170006095 | PDF link returned 404 during a live check; current data page responded. |
| FAA Aircraft Registry releasable aircraft download | https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download/ | same | Public aircraft registration data | 20170006095 | Used by the ATM ontology for aircraft instance properties. |
| FAA NFDC portal / NASR source | https://nfdc.faa.gov | https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/ | FAA aeronautical data | 20170006095 | PDF mentions NFDC and the 56-Day NASR subscription for domestic airport data. |
| FAA ASPM | http://aspm.faa.gov | same | Airport/flight performance metrics | 20170006095, 20190000452 | PDF uses ASPM airport data and airport arrival-rate examples. |
| FAA ASDI | http://www.fly.faa.gov/ASDI/asdi.html | same | Aircraft Situation Display to Industry | 20160007964, 20190000452 | Used as flight track/source data in the ATM semantic integration prototype. |
| NOAA/NWS METAR | https://www.aviationweather.gov/adds/metars | https://aviationweather.gov/data/api/ | Aviation weather observations | 20160007964, 20170006095, 20190000452 | PDF link returned 403 during a live check; the AviationWeather data API responded. |
| FAA advisories | http://www.fly.faa.gov/adv/advADB.jsp | same | ATCSCC advisories/TMIs | 20160007964, 20190000452 | Used as a TMI/advisory source in the ATM ontology/triple-store prototype. |
| CAST/ICAO IACIS Aircraft Taxonomy | http://www.intlaviationstandards.org | same | Aircraft taxonomy | 20170006095, 20190000227 | Used for aircraft model/type taxonomy alignment. |
| IATA Airline Industry Data Model | http://www.iata.org/whatwedo/passenger/pages/industry-data-model.aspx | http://www.iata.org | Airline data model | 20190000227 | PDF line wrap exposes the IATA root plus old AIDM path. |

## Ontology and semantic-web references

| Resource | Link | Type | Mentioned in | Notes |
| --- | --- | --- | --- | --- |
| RDF 1.1 Concepts | http://www.w3.org/TR/rdf11-concepts/ | Semantic web standard | 20170006095, 20190000227 | Base data model for triples. |
| RDF Schema | http://www.w3.org/TR/rdf-schema/ | Semantic web standard | 20170006095 | PDF 20190000227 also gives the older-looking `rdfschema` URL. |
| OWL 2 Overview | https://www.w3.org/TR/owl2-overview/ | Ontology standard | 20170006095, 20190000227 | Web Ontology Language reference. |
| SPARQL 1.1 Query | https://www.w3.org/TR/sparql11-query/ | KG query language | 20190000227, 20190000452 | Used for querying ontology/triple-store data. |
| SPIN Modeling Vocabulary | https://www.w3.org/Submission/2011/SUBM-spin-modeling-20110222/ | Semantic modeling vocabulary | 20190000227 | Mentioned as a semantic-web modeling reference. |
| SWRL | https://www.w3.org/Submission/SWRL/ | Semantic rule language | 20190000227 | Mentioned in ontology/semantic-web references. |

## KG and triple-store tools

| Resource | Link | Type | Mentioned in | Notes |
| --- | --- | --- | --- | --- |
| AllegroGraph | http://franz.com/agraph/allegrograph/ | RDF graph database / triple store | 20160007964 | The ATM integration prototype used AllegroGraph. |
| GraphDB | http://ontotext.com/products/graphdb/ | RDF graph database / triple store | 20160007964 | Evaluated as a triple-store product. |
| Cray Urika-GD | http://www.cray.com/products/analytics/urika-gd | Graph analytics appliance | 20160007964 | Historical graph-discovery appliance reference. |

## Historical SWAT/FAA semantic artifacts from references

These are PDF URLs reconstructed from the line-wrapped references in
`20190000227`. During a live check on 2026-06-01, these FAA media URLs returned
404, so treat them as historical references rather than reliable current links.

| Resource | Historical URL |
| --- | --- |
| NASA ATM Ontology for SWAT revised | https://www.faa.gov/nextgen/programs/swim/governance/servicesemantics/media/NASA%20ATM%20Ontology%20for%20SWAT%20revised.pdf |
| TMI Ontology | https://www.faa.gov/nextgen/programs/swim/governance/servicesemantics/media/SWAT_TMIOntology_24Aug2015.pdf |
| EIM at the FAA | https://www.faa.gov/nextgen/programs/swim/governance/servicesemantics/media/EIM%20at%20the%20FAA%20SWAT%202015.pdf |
| FAA WSDOM Introduction | https://www.faa.gov/nextgen/programs/swim/governance/servicesemantics/media/FAA%20WSDOM%20Introduction.pdf |
| SWIM Controlled Vocabulary | https://www.faa.gov/nextgen/programs/swim/governance/servicesemantics/media/SWIM%20Controlled%20Vocabulary%20SWAT%208-24-2015.pdf |
| SemNOTAM SWAT | https://www.faa.gov/nextgen/programs/swim/governance/servicesemantics/media/2015-08-24_semNOTAM_swat.pdf |
| CrOSS Organization Semantic and More | https://www.faa.gov/nextgen/programs/swim/governance/servicesemantics/media/CrOSS%20Organization%20Semantic%20and%20More%20SWAT%202015.pdf |
| Safety Cases | https://www.faa.gov/nextgen/programs/swim/governance/servicesemantics/media/Safety%20Cases.pdf |

## Important negative finding

The top-four PDFs do not expose a direct downloadable public dump of NASA's ATM
Ontology TTL files or the integrated ATM triple-store/KG data. They list
namespace URIs, ontology file names, and source-data types, but the NASA Ames
ATM Data Warehouse / Sherlock prototype and its integrated semantic data store
are described as prototype/internal resources rather than a public KG dataset.
