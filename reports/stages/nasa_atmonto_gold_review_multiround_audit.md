# NASA ATMONTO Gold Review Multi-Round Audit

## Material Passport

- Artifact: multi-perspective audit record for assisted ATCSCC gold review.
- Scope: frozen reviewed gold annotations, with recorded audits for
  `session_06`, `session_07`, `session_08`, `session_09`, `session_10`,
  `session_11`, `session_12`, `session_13`, `session_14`, `session_15`, and
  `session_16`, `session_17`, `session_18`, `session_19`, `session_20`,
  `session_21`, and `session_22`.
- Decision files:
  - `data/evaluation/nasa_atmonto/review_decisions/batch_01.jsonl`
  - `data/evaluation/nasa_atmonto/review_decisions/batch_02.jsonl`
  - `data/evaluation/nasa_atmonto/review_decisions/batch_03.jsonl`
  - `data/evaluation/nasa_atmonto/review_decisions/batch_04.jsonl`
  - `data/evaluation/nasa_atmonto/review_decisions/batch_05.jsonl`
  - `data/evaluation/nasa_atmonto/review_decisions/batch_06.jsonl`
  - `data/evaluation/nasa_atmonto/review_decisions/batch_07.jsonl`
  - `data/evaluation/nasa_atmonto/review_decisions/batch_08.jsonl`
  - `data/evaluation/nasa_atmonto/review_decisions/batch_09.jsonl`
  - `data/evaluation/nasa_atmonto/review_decisions/batch_10.jsonl`
- Protocol: `docs/experiment_protocol.md`
- Annotation guide: `docs/nasa_atmonto_gold_annotation_guide.md`

## Review Roles

| Round | Perspective | Purpose | Gold-Set Rule |
| --- | --- | --- | --- |
| 1 | Primary model screening | Propose valid facts, rejected decisions, and missing facts from S0-S3 candidates. | Suggestions are not gold truth. |
| 2 | Source-evidence audit | Check whether every accepted fact has a tight advisory evidence span. | Revise or remove facts with over-broad evidence. |
| 3 | Adversarial ontology/profile audit | Challenge normalization, profile-gap labels, and schema-valid cross-system facts. | Do not accept profile extensions or normalized values without policy. |
| 4 | Consistency audit | Apply the same predicate decision across earlier reviewed sessions. | Similar `MODERATE` cases must be handled the same way. |
| 5 | User adjudication | Resolve only conflicts, low-confidence calls, and profile-extension choices. | Keep unresolved records pending. |

## Session 06 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-015` | `extensionProbability=MEDIUM` was not literal source text; source says `PROBABILITY OF EXTENSION: MODERATE`. | Directly accepting model-generated `MEDIUM` is defensible only under a reviewed normalization policy. | Removed normalized probability from `valid_cross_system_fact_ids`; added corrected manual fact with `raw_value=MODERATE`, `value=MEDIUM`, `value_normalization=reviewed_enum_mapping_moderate_to_medium`, and tight evidence. |
| `ATCSCC-GOLD-016` | Same `MODERATE` versus `MEDIUM` issue; other S3 reroute facts were source-supported, but some evidence spans were broad. | Keep values only when evidence is tight or the fact is explicitly corrected. | Removed normalized probability from `valid_cross_system_fact_ids`; added corrected manual probability fact. Kept other source-supported reroute facts and recorded the broad-evidence risk for future review. |
| `ATCSCC-GOLD-028` | S0 accepted facts are supported by the advisory; `impactingConditionMessage` is source-supported but rejected by current profile. | GroundStop `impactingConditionMessage` is a profile gap, not an accepted gold fact. | Kept decision as `profile_gap`. |
| `ATCSCC-GOLD-054` | S0 accepted facts are supported; source typo in comments is literal source text. | GroundStop condition message remains a profile gap; source typo should not be silently corrected. | Kept decision as `profile_gap`; kept literal `GROUN STOP EXTENDED.` comment. |

## Session 07 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-017` | Accepted BNA ground-delay facts match the source, including `EFFECTIVE TIME: 191854-200459`, `STAFFING / STAFFING`, and comments. | `impactingCondition=staffing` is source-supported but outside the current allowed values. | Kept source-supported S0 facts, preserved the raw staffing message, and adjudicated the rejected normalized condition as `profile_gap`. |
| `ATCSCC-GOLD-020` | Accepted SFO ground-delay facts match the source, including `EFFECTIVE TIME: 152258-160759`, `STAFFING / STAFFING`, and comments. | S3 `impactingCondition=other`, broad comments, bad parsed time, and broad departure scope were not reliable gold facts. | Kept source-supported S0 facts and adjudicated staffing as `profile_gap`; did not copy cross-system over-normalized or over-broad candidates. |
| `ATCSCC-GOLD-027` | Accepted ORD ground-stop facts match the source, including `EFFECTIVE TIME: 192111-192245`, `PROBABILITY OF EXTENSION: MEDIUM`, and `WEATHER / THUNDERSTORMS`. | GroundStop `impactingConditionMessage` remains a current domain/profile gap. | Kept S0 advisory/time/control/weather/comments facts and did not copy cross-system ground-stop-period times that differed from explicit effective time. |
| `ATCSCC-GOLD-059` | Accepted generic TMI advisory/time facts match the source; the accepted S3 comments fact is source-supported. | `USERS`, `CAN`, `INTO`, and `THE` are parser artifacts; `ZMP ARTCC` is source-supported but outside the current controlled-element profile path. | Marked parser artifacts invalid, copied the source-supported delay/holding sentence as comments, and adjudicated ZMP as `profile_gap`. |

## Session 08 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-004` | Accepted generic TMI advisory/time facts match the source; parser artifacts `USERS`, `CAN`, `INTO`, and `AND` are not valid control elements. | `ZNY ARTCC` is source-supported but remains outside the current controlled-element range. | Marked parser artifacts invalid, added the Newark arrival-delay sentence as manual comments, and adjudicated ZNY as `profile_gap`. |
| `ATCSCC-GOLD-013` | Accepted reroute advisory/time facts and manual `RQD`, `ROUTE`, `WEATHER`, `MODERATE`, and remarks facts are source-supported. | The `MODERATE -> MEDIUM` probability mapping follows the reviewed normalization policy; the rejected S0 probability is an extractor normalization bug, not a semantic false positive. | Added manual ReRoute facts because no schema-valid S1-S3 cross-system options were available in the decision review context; entered normalized probability with `raw_value=MODERATE`. |
| `ATCSCC-GOLD-032` | Accepted IAD ground-stop facts match the source; S3 candidates duplicate accepted S0 facts. | GroundStop `impactingConditionMessage` remains a profile gap; S3 `controlledNASelement` is broader than the accepted S0 airport-typed control element. | Kept S0 facts and adjudicated the message fact as `profile_gap`; did not copy duplicate or broader S3 facts. |
| `ATCSCC-GOLD-055` | Accepted PHL ground-stop facts match the source; S2 duplicates are not needed, and ground-stop-period times differ from explicit `EFFECTIVE TIME`. | GroundStop `impactingConditionMessage` remains a profile gap; S2 control element is broader than the accepted S0 airport-typed control element. | Kept S0 facts, used explicit `EFFECTIVE TIME`, and adjudicated the message fact as `profile_gap`. |

## Session 09 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-009` | Accepted reroute advisory/time facts plus S3 `RQD`, `ROUTE`, and `WEATHER` facts are source-supported; source says `PROBABILITY OF EXTENSION: MODERATE`. | The direct S3 `MEDIUM` probability must remain unaccepted; the reviewed `MODERATE -> MEDIUM` policy requires a manual normalized fact with raw provenance. | Kept S0 advisory/time facts, copied source-supported S3 reroute status/type/reason, and added manual normalized probability with `raw_value=MODERATE`. |
| `ATCSCC-GOLD-026` | STL ground-stop advisory/time/control/probability/weather facts are source-supported; `COMMENTS:` is empty. | GroundStop `impactingConditionMessage` remains a profile gap; empty comments bleed-through is an extractor artifact. | Marked the S0 comments fact invalid and adjudicated the message fact as `profile_gap`. |
| `ATCSCC-GOLD-053` | STL ground-stop advisory/time/control/probability/weather facts are source-supported; `COMMENTS:` is empty. | GroundStop `impactingConditionMessage` remains a profile gap; S2 ground-stop-period times are not accepted under the explicit `EFFECTIVE TIME` policy. | Marked the S0 comments fact invalid, skipped S2 comments/time alternatives, and adjudicated the message fact as `profile_gap`. |
| `ATCSCC-GOLD-058` | DCA ground-stop advisory/time/control/probability/weather facts and `LACK OF ROUTES...` comments are source-supported. | GroundStop `impactingConditionMessage` remains a profile gap; S2 candidates are duplicates or ground-stop-period alternates. | Kept S0 facts and comments, skipped S2 duplicates/period times, and adjudicated the message fact as `profile_gap`. |

## Session 10 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-002` | Advisory number, signature time, explicit `EFFECTIVE TIME`, and manual arrival-delay comments are source-supported; `USERS`, `CAN`, `INTO`, `SAN`, and `DIEGO` are parser artifacts from free text. | `ZLA` is a source-supported ARTCC constrained facility but remains outside the current controlled-element range. | Kept advisory/time facts, added exact manual `initiativeComments`, marked parser artifacts invalid, and adjudicated ZLA as `profile_gap`. |
| `ATCSCC-GOLD-008` | Advisory/time facts and the full South Florida arrival-delay/airport-scope comment are source-supported; `USERS`, `CAN`, `INTO`, `THE`, and `SOUTH` are parser artifacts. | `ZMA` is a source-supported ARTCC constrained facility but remains outside the current controlled-element range; S2 airport candidates use the wrong TMI class for this record. | Kept advisory/time facts, added exact manual `initiativeComments`, marked parser artifacts invalid, and adjudicated ZMA as `profile_gap`. |
| `ATCSCC-GOLD-025` | DTW ground-stop advisory/time/control/probability/weather facts and `ZID REMOVED FROM STOP.` comments are source-supported. | GroundStop `impactingConditionMessage` remains a profile gap. | Kept S0 facts and comments, skipped duplicate S2 control fact, and adjudicated the message fact as `profile_gap`. |
| `ATCSCC-GOLD-029` | DEN ground-stop advisory/time/control/probability/weather facts are source-supported; `COMMENTS:` is empty. | GroundStop `impactingConditionMessage` remains a profile gap; empty comments bleed-through is an extractor artifact. | Kept S0 facts, marked the S0 comments fact invalid, skipped duplicate or comment-like S2 alternatives, and adjudicated the message fact as `profile_gap`. |
| `ATCSCC-GOLD-031` | SFO ground-stop advisory/time/control/probability/other-condition facts and runway-construction comments are source-supported. | GroundStop `impactingConditionMessage` remains a profile gap; S3 ground-stop-period times are not accepted under the explicit `EFFECTIVE TIME` policy. | Kept S0 facts and comments, skipped duplicate or alternate-time S3 candidates, and adjudicated the message fact as `profile_gap`. |

## Session 11 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-003` | Accepted advisory/time facts and manual LAS arrival-delay comments are source-supported; `USERS`, `CAN`, `INTO`, `LAS`, and `VEGAS` are parser artifacts from free text. | `ZLA` is a source-supported ARTCC constrained facility but remains outside the current controlled-element range. | Kept advisory/time facts, added exact manual `initiativeComments`, marked parser artifacts invalid, and adjudicated ZLA as `profile_gap`. |
| `ATCSCC-GOLD-039` | The advisory is explicitly `ZMA SWAP_FYI` and planning-oriented; generic TMI advisory number and planning comments are source-supported. | Reviewers disagreed on whether generic-only gold was too conservative. The final boundary accepts only narrow ReRouteTMI `FYI` status and `WEATHER` rationale while rejecting GroundStopTMI, inferred probability, ZMA-as-Airport, and speculative `reRouteType` candidates. | Kept S0 `GroundStopTMI` invalid, added corrected generic TMI facts, copied narrow FYI/weather ReRoute facts, and recorded the planning-versus-reroute conflict as a policy-sensitive adjudication. |
| `ATCSCC-GOLD-098` | Accepted S0 facts match advisory number, signature time, explicit `EFFECTIVE TIME: 202000-210200`, and `PROBABILITY OF EXTENSION: NONE`; reroute status/type/reason/comments are source-supported. | Cross-system effective-time candidates that parse DDHHMM as clock text are invalid; constrained `ZOB` remains an ARTCC/profile issue rather than accepted control element. | Kept S0 timing/probability facts, copied RQD/ROUTE/WEATHER and `15 MIT VIA NOVON` comments, and skipped alternate-time and controlled-element candidates. |
| `ATCSCC-GOLD-082` | Accepted S0 facts match advisory number, signature time, explicit `EFFECTIVE TIME: 202100-210000`, and `PROBABILITY OF EXTENSION: LOW`; one initial WEATHER candidate had an over-loose title-only evidence span. | ReRoute status/type/reason/comments are appropriate; `allowedRoute` payloads and ARTCC/airspace control elements need a dedicated normalization/profile policy before gold acceptance. | Replaced the WEATHER fact with the equivalent candidate whose evidence includes `REASON: WEATHER`, kept RQD/ROUTE/comments, and skipped route-object/control-element candidates. |

## Session 12 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-036` | Accepted SFO proposed GDP facts match advisory number, signature time, explicit `EFFECTIVE TIME: 171247-171359`, `CTL ELEMENT: SFO`, `OTHER / OTHER`, and comments. | `SFO` as `Airport` is valid for `controlledNASelement`; skipped departure-scope candidates remain unsettled `AirportSpec` normalization/profile work. | Kept all S0 facts, used explicit `EFFECTIVE TIME` instead of estimated/program-period times, and did not copy evidence-missing or schema-invalid cross-system alternatives. |
| `ATCSCC-GOLD-037` | Accepted SFO GDP facts match advisory number, signature time, explicit `EFFECTIVE TIME: 141238-142359`, control element, condition, and runway/construction comments. | S0 profile fit is valid; departureScope list-object candidates should remain excluded until a reviewed `AirportSpec` policy exists. | Kept all S0 facts, skipped ADL and estimated/program-period alternate times, and recorded departureScope as out of current gold scope. |
| `ATCSCC-GOLD-044` | Advisory number and FYI status are source-supported; initial S3 `WEATHER` and `CDR` values were correct but carried overly broad evidence spans. | ReRoute `FYI`, `reRouteReason`, `reRouteType`, and comments fit the profile; `ZAU` remains an ARTCC controlled-element profile gap and event-window times are semantic/time-policy choices. | Replaced broad-evidence S3 `WEATHER` and `CDR` facts with manual facts using tight evidence spans, added exact source-body comments, and skipped event-window, tail timestamp, unsupported probability, and ARTCC control candidates. |
| `ATCSCC-GOLD-065` | Advisory number, signature time, explicit `EFFECTIVE TIME: 162039-170130`, and capping/tunneling comments are source-supported. | Generic `TrafficManagementInitiative` timing/comments are valid; FYI status is a generic-domain/profile gap, `ZDV` is an ARTCC profile gap, and `DEN/KDEN` controlled-element candidates are semantic overreach. | Kept S0 timing facts, added exact source-body comments, skipped title-boilerplate S3 comments, and clarified skipped FYI/control-element rationale. |

## Session 13 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-035` | Accepted EWR proposed GDP facts are source-supported; source reviewer challenged whether `ARRIVALS ESTIMATED FOR` / `ANTICIPATED CUMULATIVE PROGRAM PERIOD` is a stronger operational window than explicit `EFFECTIVE TIME: 201648-201759`. | GDP profile fit is valid, and skipping program-period times is consistent with the current explicit-`EFFECTIVE TIME` gold timing policy. | Kept all S0 facts, recorded the program-period challenge as a timing-policy item, and did not copy duplicate or alternate-time cross-system facts. |
| `ATCSCC-GOLD-074` | The volcanic bulletin is source-supported; S0 `issuedTime=18:57` comes from internal `VA ADVISORY DTG`, while the ATCSCC signature says `18:59`. | Generic `TrafficManagementInitiative` plus manual full-body `initiativeComments` is an acceptable fallback; title-only comments and `14:00` effective-time parses are semantic exclusions. | Marked S0 issuedTime invalid, accepted S2 signature-based issuedTime, kept explicit `EFFECTIVE TIME: 140000-140000` as midnight, and added exact volcanic bulletin body as manual comments. |
| `ATCSCC-GOLD-081` | Accepted LAS GDP facts match source fields including signature, explicit `EFFECTIVE TIME: 180619-180859`, `CTL ELEMENT: LAS`, `WEATHER / WIND`, and comments. | `GROUND STOP CANCELLED` appears inside comments and is not a class correction; cross-system facts are duplicates. | Kept all S0 facts and skipped duplicate cross-system facts. |
| `ATCSCC-GOLD-092` | The source is a BOS `CDM GROUND STOP`; source reviewer challenged whether `GROUND STOP PERIOD: 15/2059Z - 15/2215Z` should override explicit `EFFECTIVE TIME: 152115-152315`. | Class correction to `GroundStopTMI` is required; S3 probability/weather/comments are profile-compatible, but S3 `controlledNASelement` uses a too-broad object type. | Marked all S0 `GroundDelayProgramTMI` facts invalid, kept explicit `EFFECTIVE TIME` as current timing policy, added corrected manual `GroundStopTMI` advisory/time and airport-typed BOS control facts, accepted S3 probability/weather/comments, and kept `impactingConditionMessage` as a profile gap. |

## Session 14 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-038` | Accepted LGA GDP facts match source fields including title, signature, explicit `EFFECTIVE TIME: 201857-210459`, `CTL ELEMENT: LGA`, `WEATHER / THUNDERSTORMS`, and comments. | `GroundDelayProgramTMI`, `Airport`-typed LGA, `impactingCondition`, and `impactingConditionMessage` fit the current GDP profile; S2/S3 candidates duplicate S0 or expose out-of-scope GDP details. | Kept all S0 facts, used explicit `EFFECTIVE TIME` rather than arrivals-estimated/program-period windows, and skipped duplicate or profile-outside cross-system facts. |
| `ATCSCC-GOLD-061` | S0 `issuedTime=08:45` comes from the internal volcanic-ash advisory DTG while its evidence cites ATCSCC `SIGNATURE: 08:47`; the full volcanic bulletin body is source-supported. | Generic `TrafficManagementInitiative` plus manual full-body `initiativeComments` is the right fallback; Kilauea is a volcano, not an airport/NAS control element, and the S2 `15:00` end-time parse is not the midnight zero-duration `EFFECTIVE TIME`. | Marked S0 issuedTime invalid, accepted the S2 signature-based issuedTime, kept explicit `EFFECTIVE TIME: 150000-150000` as midnight, added exact volcanic bulletin body as manual comments, and skipped Kilauea control and title-only comments. |
| `ATCSCC-GOLD-064` | Source reviewer found the manual `DFW` controlled-element evidence initially lacked the exact `DFW` token; title evidence contains the exact airport token and supports the corrected evidence span. | Generic `TrafficManagementInitiative` is appropriate for airport arrival delays; do not promote the record to `GroundDelayProgramTMI`. `DFW` as `Airport` is profile-valid through the generic TMI control-element range, while S3 GDP weather/control facts use the wrong class. | Kept S0 advisory/time facts, tightened manual DFW evidence to the title, added source-body `initiativeComments`, skipped S3 GDP facts, and recorded weather/thunderstorm reason as a profile-boundary issue for generic arrival-delay TMIs. |
| `ATCSCC-GOLD-084` | Accepted ZNY SWAP_FYI advisory/time/status facts are source-supported; `reRouteReason=WEATHER` is supported by forecasted/severe-weather avoidance text, and full-body planning comments are direct source text. | `ReRouteTMI` with `implementationStatus=FYI` and `reRouteReason=WEATHER` is consistent with prior SWAP_FYI decisions. The text describes possible reroutes/CDRs, so a single clean `reRouteType` enum is not forced; `ZNY` remains an ARTCC/profile-gap control element. | Kept all S0 facts, added manual WEATHER reason and full planning comments, skipped `reRouteType`, extension probability, and ZNY controlled-element candidates. |
| `ATCSCC-GOLD-091` | Accepted IAH ground-stop facts match title, signature, explicit `EFFECTIVE TIME: 191746-191945`, `CTL ELEMENT: IAH`, `PROBABILITY OF EXTENSION: MEDIUM`, and comments; `RWY-TAXI / DISABLED AIRCRAFT` supports `impactingCondition=runway`. | `GroundStopTMI` is correct, airport-typed IAH is preferred over broad `TFMcontrolElement` candidates, and `impactingCondition=runway` fits the GroundStop profile. `GROUND STOP PERIOD` and `ADL TIME` stay excluded under current explicit-`EFFECTIVE TIME` and signature-issued-time policy. | Kept all S0 facts, copied the S2 `impactingCondition=runway` fact, skipped ground-stop-period alternate times, ADL-issued-time, broad control-element duplicates, and `impactingConditionMessage`. |

## Session 15 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-100` | Advisory number, signature-based issued time, explicit `EFFECTIVE TIME: 170000-170000`, and full Reventador volcanic bulletin body are source-supported. | Generic `TrafficManagementInitiative` is the correct volcanic-bulletin fallback; S2 `17:00` effective-time parses and title-only comments are semantic exclusions. | Marked S0 internal-VA-DTG issued time invalid, accepted the S2 signature issued time, kept midnight zero-duration effective times, and added exact full-body `initiativeComments`. |
| `ATCSCC-GOLD-050` | Advisory number, explicit `EFFECTIVE TIME: 190000-190000`, ATCSCC `SIGNATURE: 14:25`, and full Fuego bulletin body are source-supported. | Generic TMI plus manual signature `issuedTime` and full bulletin `initiativeComments` is consistent; no schema-valid cross-system signature candidate was available in the decision context. | Marked S0 internal-VA-DTG issued time invalid, added manual signature issued time and full-body comments, and skipped title-only comments plus `19:00` effective-time parses. |
| `ATCSCC-GOLD-077` | Advisory number, explicit `EFFECTIVE TIME: 190000-190000`, ATCSCC `SIGNATURE: 00:11`, and full Popocatepetl bulletin body are source-supported. | Same volcanic-bulletin generic TMI policy applies; title-only comments and alternate parsed times remain excluded. | Marked S0 internal-VA-DTG issued time invalid, added manual signature issued time and full-body comments, and kept midnight zero-duration effective times. |
| `ATCSCC-GOLD-045` | Title, signature, explicit `EFFECTIVE TIME: 202121-212300`, `_FYI`, and the full Starship pre-mission body are source-supported. | The profile reviewer challenged the initial `ReRouteTMI` class as over-specialized because the source is a planning advisory about possible future initiatives, not a current reroute; follow-up review passed the corrected generic TMI decision. | Rejected all S0 `ReRouteTMI` facts, added corrected generic TMI advisory/time/comments facts, and skipped FYI status, route type/reason, ZHU control, and event-time intervals as profile or timing-policy exclusions. |
| `ATCSCC-GOLD-068` | Advisory number, signature time, explicit `EFFECTIVE TIME: 182033-190103`, `CTL ELEMENT: STL`, and empty-comments bleed-through diagnosis are source-supported. | `CDM GS CNX` is a cancellation notice, so generic TMI is more defensible than active `GroundStopTMI`; inferred probability/condition facts are not accepted. | Kept S0 advisory/time/STL control facts, marked footer/effective-time `initiativeComments` invalid, and skipped GroundStop/probability/condition alternatives. |

## Session 16 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-067` | Kilauea volcanic bulletin advisory number, zero-duration explicit `EFFECTIVE TIME: 150000-150000`, ATCSCC `SIGNATURE: 12:25`, and full bulletin body are source-supported. | Generic `TrafficManagementInitiative` remains the correct volcanic-bulletin fallback; internal VA advisory DTG is not the ATCSCC issued time. | Kept source-supported advisory/effective-time facts, rejected the S0 internal-DTG `issuedTime`, and added manual signature `issuedTime` plus full-body `initiativeComments`. |
| `ATCSCC-GOLD-072` | `ORD MDW CDRS_FYI`, `ZAU IS IMPLEMENTING CDRS DUE TO WEATHER`, explicit effective time, and signature time are source-supported. | Generic base TMI plus narrow `ReRouteTMI` sidecar facts is acceptable; ORD/MDW/ZAU control facts remain conservative exclusions under the current profile boundary. | Kept S0 advisory/time facts, added FYI/CDR/WEATHER/comments sidecar facts, and skipped DDHHMM event-window parses plus broad control-element candidates. |
| `ATCSCC-GOLD-096` | Fuego volcanic bulletin advisory number, zero-duration explicit `EFFECTIVE TIME: 150000-150000`, ATCSCC `SIGNATURE: 23:24`, and full bulletin body are source-supported. | Generic volcanic-bulletin TMI policy applies; S0 internal VA DTG is not the ATCSCC signature time, while the S2 signature-based `issuedTime` is valid. | Kept S0 advisory/effective-time facts, rejected the internal-DTG `issuedTime`, accepted S2 signature `issuedTime`, and added full-body comments. |
| `ATCSCC-GOLD-073` | DFW `CDM GROUND STOP`, explicit `EFFECTIVE TIME: 200020-200215`, `CTL ELEMENT: DFW`, `PROBABILITY OF EXTENSION: MEDIUM`, and `RWY-TAXI / CONSTRUCTION` are source-supported; `COMMENTS:` is empty. | `GroundStopTMI` plus airport-typed DFW is correct; `impactingCondition=runway` fits the current profile, but empty comments and departure-scope list objects remain out of accepted gold. | Kept S0 ground-stop facts, accepted the S2 runway condition fact, rejected empty-comments bleed-through, and skipped alternate period times/departure scope. |
| `ATCSCC-GOLD-062` | Fuego correction bulletin advisory number, zero-duration explicit `EFFECTIVE TIME: 200000-200000`, ATCSCC `SIGNATURE: 02:12`, and full bulletin body are source-supported. | Generic volcanic-bulletin TMI policy applies; corrected internal VA advisory DTG is not the ATCSCC signature time. | Kept S0 advisory/effective-time facts, rejected the internal-DTG `issuedTime`, and added manual signature `issuedTime` plus full-body `initiativeComments`. |

## Session 17 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-086` | Bezymianny volcanic bulletin advisory number, zero-duration explicit `EFFECTIVE TIME: 160000-160000`, ATCSCC `SIGNATURE: 15:38`, and full bulletin body are source-supported. | Generic `TrafficManagementInitiative` is the right volcanic-bulletin fallback; internal VA advisory DTG `15:36` is not the ATCSCC issued time. | Kept source-supported advisory/effective-time facts, rejected the S0 internal-DTG `issuedTime`, and added manual signature `issuedTime` plus full-body comments. |
| `ATCSCC-GOLD-089` | Hotline issue-request page activation text, explicit `EFFECTIVE TIME: 160909-170200`, and `SIGNATURE: 09:09` are source-supported. | The source is a generic TCA/hotline page status notice, not a reroute initiative; ReRouteTMI would over-specialize the event. | Rejected all S0 `ReRouteTMI` facts, accepted S2 generic advisory/issued-time facts, and added corrected generic TMI effective interval plus full-body comments. |
| `ATCSCC-GOLD-041` | Oceanic route closure title/body, explicit `EFFECTIVE TIME: 181357-181630`, `SIGNATURE: 13:57`, `_RQD`, and route-closure body are source-supported. | `ReRouteTMI` is justified; `ZNY` remains an ARTCC constrained facility profile gap rather than accepted `controlledNASelement`. | Kept S0 ReRouteTMI advisory/time/RQD facts and added manual `reRouteType=ROUTE`, `reRouteReason=WEATHER`, and exact route-closure comments. |
| `ATCSCC-GOLD-063` | ORD airport arrival-delay title, explicit `EFFECTIVE TIME: 161303-161830`, `SIGNATURE: 13:03`, and arrival-delay message are source-supported. | Generic `TrafficManagementInitiative` is appropriate for airport arrival delay; ORD as an airport is acceptable, while `ZAU` ARTCC remains a profile-boundary exclusion. | Kept S0 generic TMI advisory/time facts, added manual ORD airport control and exact arrival-delay comments, and skipped duplicate S3 timing/comment facts. |
| `ATCSCC-GOLD-093` | STL diversion-recovery activation title/body, explicit `EFFECTIVE TIME: 181444-181830`, `SIGNATURE: 14:44`, and STL airport body text are source-supported. | The source is a diversion-recovery notice; mentions of GDP or ground stop are contextual warnings, not the initiative class. | Rejected all S0 `GroundDelayProgramTMI` facts, accepted S2 generic timing facts, and added corrected generic TMI advisory number, STL airport control, and exact diversion-recovery comments. |

## Session 18 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-051` | Santa Maria volcanic bulletin advisory number, zero-duration explicit `EFFECTIVE TIME: 140000-140000`, ATCSCC `SIGNATURE: 08:36`, and full bulletin body are source-supported; the S0 `issuedTime=08:34` used the internal VA advisory DTG. | Generic `TrafficManagementInitiative` remains the correct volcanic-bulletin fallback, and VA advisory DTG is not the ATCSCC issued time. | Kept source-supported advisory/effective-time facts, rejected the S0 internal-DTG `issuedTime`, accepted S2 signature `issuedTime`, and added full-body comments. |
| `ATCSCC-GOLD-088` | SFO GDP cancellation facts match title, signature, explicit `EFFECTIVE TIME: 180507-180945`, `CTL ELEMENT: SFO`, and `COMMENTS: OBJECTIVES MET`. | `CDM GROUND DELAY PROGRAM CNX` stays in the `GroundDelayProgramTMI` lifecycle; duplicate cross-system facts and `impactingCondition=other` are not needed gold facts. | Kept all source-supported S0 GDP cancellation facts and skipped duplicate or overbroad cross-system alternatives. |
| `ATCSCC-GOLD-042` | Oceanic route closure title/body, explicit `EFFECTIVE TIME: 200051-200330`, `SIGNATURE: 00:51`, `_RQD`, and thunderstorm closure text are source-supported. | `ReRouteTMI` is justified; `ZMA` is an ARTCC constrained facility and must not be accepted as an `Airport` controlled element. | Kept S0 ReRouteTMI advisory/time/RQD facts and added manual `reRouteType=ROUTE`, `reRouteReason=WEATHER`, and exact route-closure comments. |
| `ATCSCC-GOLD-071` | EWR arrival-delay advisory/time facts plus the arrival-delay body and title airport token are source-supported. | Generic `TrafficManagementInitiative` is appropriate; canonical airport `EWR` is accepted, while `ZNY` ARTCC remains outside the current controlled-element profile. | Kept S0 advisory/time facts and added manual EWR airport control plus exact arrival-delay comments. |
| `ATCSCC-GOLD-034` | SAN diversion-recovery activation title/body, explicit `EFFECTIVE TIME: 141513-142330`, `SIGNATURE: 15:13`, and SAN airport text are source-supported. | Consistent with `ATCSCC-GOLD-093`, diversion recovery is a generic `TrafficManagementInitiative`, not a `GroundDelayProgramTMI`; contextual GDP/ground-stop mentions are warnings. | Rejected all S0 GDP-class facts, accepted S3 generic advisory/time facts, and added SAN airport control plus exact diversion-recovery comments. |
| `ATCSCC-GOLD-079` | Oceanic route closures title/body, explicit `EFFECTIVE TIME: 151735-152030`, `SIGNATURE: 17:35`, `_RQD`, and thunderstorm closure text are source-supported. | `ReRouteTMI` is justified; `L451/L453/L455` AirspaceRoute control facts need route-object normalization/profile policy before gold acceptance. | Kept S0 ReRouteTMI advisory/time/RQD facts and added manual route type, weather reason, and exact route-closures comments; held route-object control facts out of gold. |

## Session 19 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-083` | LGA/JFK ground-stop cancellation title/body, explicit `EFFECTIVE TIME: 200052-200200`, `SIGNATURE: 00:52`, destination airports, and cancellation remarks are source-supported. | Consistent with GS CNX policy from `ATCSCC-GOLD-068`, this cancellation notice should not be treated as an active `GroundStopTMI`; inferred GroundStop probability/condition and withinARTCC facts are not accepted. | Rejected all S0 `GroundStopTMI` facts, added corrected generic TMI advisory/time facts, LGA/JFK airport controls, and exact cancellation body comments. |
| `ATCSCC-GOLD-076` | ORD `CDM GS CNX` advisory/time/control facts are source-supported, while `COMMENTS:` is empty and the extractor captured following effective-time/signature/footer text. | `CDM GS CNX` remains generic `TrafficManagementInitiative`, not active `GroundStopTMI`; inferred `extensionProbability=NONE` and `impactingCondition=other` are not accepted. | Kept S0 generic TMI advisory/time/ORD control facts, rejected empty-comments bleed-through, and skipped GroundStopTMI cross-system alternatives. |
| `ATCSCC-GOLD-078` | Fuego volcanic bulletin advisory number, zero-duration explicit `EFFECTIVE TIME: 200000-200000`, ATCSCC `SIGNATURE: 02:00`, and full bulletin body are source-supported. | Generic volcanic-bulletin TMI policy applies; S0 internal VA advisory DTG `01:58` is not the ATCSCC signature time. | Kept source-supported advisory/effective-time facts, rejected S0 internal-DTG `issuedTime`, and added manual signature `issuedTime` plus full-body comments. |
| `ATCSCC-GOLD-060` | DCA `CDM GS CNX` advisory/time/control facts and non-empty scheduling-delay comments are source-supported. | The record stays generic `TrafficManagementInitiative`; GroundStopTMI period/probability/condition alternatives are model inferences outside the accepted cancellation profile. | Kept all source-supported S0 generic TMI facts and skipped GroundStopTMI cross-system alternatives. |
| `ATCSCC-GOLD-087` | DEN scheduling-delay advisory/time facts, DEN title token, and exact scheduling-delay body are source-supported. | Generic `TrafficManagementInitiative` is appropriate for airport scheduling delay; DEN is accepted as airport control, while `ZDV` ARTCC remains outside the current control profile. | Kept S0 advisory/time facts, added DEN airport control, and added exact scheduling-delay comments. |
| `ATCSCC-GOLD-066` | Reventador volcanic bulletin advisory number, zero-duration explicit `EFFECTIVE TIME: 170000-170000`, ATCSCC `SIGNATURE: 09:12`, and full bulletin body are source-supported. | Generic volcanic-bulletin TMI policy applies; internal VA advisory DTG `09:10` is not the ATCSCC issued time, and S2 `17:00` effective-time parses are semantic exclusions. | Kept source-supported advisory/effective-time facts, rejected the S0 internal-DTG `issuedTime`, accepted S2 signature `issuedTime`, and added full-body comments. |

## Session 20 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-075` | Purace volcanic bulletin advisory number, zero-duration explicit `EFFECTIVE TIME: 180000-180000`, ATCSCC `SIGNATURE: 20:10`, and full bulletin body are source-supported; S0 used VA DTG `20:09`. | Generic volcanic-bulletin TMI policy applies; VA DTG is not ATCSCC issued time. | Kept advisory/effective-time facts, rejected S0 internal-DTG `issuedTime`, added manual signature `issuedTime`, and added full-body comments. |
| `ATCSCC-GOLD-049` | Popocatepetl bulletin fields are source-supported; S0 `issuedTime=06:06` came from VA DTG while ATCSCC signature is `06:09`. | Same volcanic-bulletin boundary as prior sessions. | Kept advisory/effective-time facts, rejected VA-DTG issued time, added manual signature issued time and exact comments. |
| `ATCSCC-GOLD-094` | Sheveluch bulletin fields are source-supported; S0 `issuedTime=15:04` came from VA DTG while ATCSCC signature is `15:06`. | Same volcanic-bulletin boundary; do not infer a NAS control element from volcano name. | Kept generic TMI facts, rejected VA-DTG issued time, and added manual signature/comments facts. |
| `ATCSCC-GOLD-070` | Fuego bulletin fields are source-supported; S2 signature-based issued time matches source. | Generic volcanic-bulletin TMI policy applies; S0 VA-DTG issued time is invalid. | Kept advisory/effective-time facts, rejected S0 internal-DTG issued time, accepted S2 signature time, and added full-body comments. |
| `ATCSCC-GOLD-043` | En route TCA/hotline web page termination body, signature, and effective interval are source-supported. | The source is a hotline/webpage status notice, not a route initiative. | Rejected all S0 `ReRouteTMI` facts and added corrected generic TMI advisory/time/comments facts. |
| `ATCSCC-GOLD-069` | PHL `CDM GS CNX` advisory/time/control facts are source-supported; `COMMENTS:` is empty. | Cancellation notice remains generic TMI; empty comments bleed-through is extractor error. | Kept source-supported generic TMI facts, rejected empty-comments/footer bleed-through, and skipped active GroundStop alternatives. |
| `ATCSCC-GOLD-085` | Reventador bulletin fields are source-supported; S2 signature-based issued time matches source. | Generic volcanic-bulletin TMI policy applies; S3 `19:00` effective-end parse is not the reviewed midnight zero-duration policy. | Kept advisory/effective-time facts, rejected S0 VA-DTG issued time, accepted S2 signature time, and added full-body comments. |

## Session 21 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-033` | LAS GDP cancellation title, signature, explicit effective interval, control element, and cancellation comments are source-supported. | `CDM GROUND DELAY PROGRAM CNX` stays in the GDP lifecycle; empty-comments bleed-through is invalid. | Kept source-supported GDP facts and rejected footer/effective-time bleed-through comments. |
| `ATCSCC-GOLD-047` | Purace bulletin fields are source-supported; S0 `issuedTime=11:00` came from VA DTG while ATCSCC signature is `11:02`. | Same volcanic-bulletin generic TMI boundary. | Kept advisory/effective-time facts, rejected VA-DTG issued time, and added manual signature/comments facts. |
| `ATCSCC-GOLD-080` | BNA `CDM GS CNX` advisory/time/control facts are source-supported; `COMMENTS:` is empty. | Cancellation notice stays generic TMI; do not infer active GroundStop probability/condition. | Kept source-supported generic TMI facts, rejected empty-comments bleed-through, and skipped GroundStop alternatives. |
| `ATCSCC-GOLD-090` | Reroute cancellation body `FCA002:ZHU_ZFW_ZME_TO_NY_SATS HAS BEEN CANCELLED.` is exact source text. | `ReRouteTMI` is appropriate, but current policy does not add unstable cancellation status/type/control extensions. | Kept S0 advisory/time facts and added exact cancellation comments only. |
| `ATCSCC-GOLD-099` | MEM arrival-delay title/body and airport token are source-supported. | Generic TMI is appropriate for airport arrival delay; GDP/weather candidates use the wrong class. | Kept advisory/time facts, added MEM airport control and exact comments, and skipped wrong-class S3 alternatives. |
| `ATCSCC-GOLD-095` | Reroute cancellation title/body and signature/effective interval are source-supported. | `ReRouteTMI` is appropriate; no unreviewed status/type/control extension is accepted. | Kept S0 advisory/time facts and added exact cancellation comments. |
| `ATCSCC-GOLD-046` | Bezymianny bulletin fields are source-supported; S2 signature-based issued time matches source while S0 used VA DTG. | Generic volcanic-bulletin TMI policy applies. | Kept advisory/effective-time facts, rejected S0 VA-DTG issued time, accepted S2 signature time, and added full-body comments. |

## Session 22 Audit Outcome

| Sample | Source-Evidence Finding | Ontology/Profile Finding | Resolution |
| --- | --- | --- | --- |
| `ATCSCC-GOLD-048` | TTCA/hotline web page termination body, signature, and effective interval are source-supported. | The notice is generic TCA/hotline status, not a reroute initiative. | Kept generic TMI advisory/time facts and added exact termination comments. |
| `ATCSCC-GOLD-040` | Reroute cancellation title/body and signature/effective interval are source-supported. | `ReRouteTMI` is appropriate; no unreviewed cancellation status/type/control extension is accepted. | Kept S0 advisory/time facts and added exact cancellation comments. |
| `ATCSCC-GOLD-097` | Reroute cancellation title/body and signature/effective interval are source-supported. | Same conservative `ReRouteTMI` cancellation boundary as sessions 20-21. | Kept S0 advisory/time facts and added exact cancellation comments. |

## Consistency Fix

The `MODERATE -> MEDIUM` finding also applied to previously reviewed ReRoute
records. The following records now use corrected manual normalized facts instead
of directly accepting model-generated `MEDIUM` probability facts:

- `ATCSCC-GOLD-010`
- `ATCSCC-GOLD-011`
- `ATCSCC-GOLD-012`
- `ATCSCC-GOLD-014`
- `ATCSCC-GOLD-015`
- `ATCSCC-GOLD-016`

Each corrected fact retains the raw source value and the reviewed normalization
policy `extensionProbability:MODERATE->MEDIUM`.

## Open Policy Items

- ARTCC constrained-area values such as `ZNY` remain outside accepted gold for
  `controlledNASelement` unless a reviewed ARTCC bridge or alternate property is
  added.
- GroundStop `impactingConditionMessage` remains a profile-gap decision until a
  GroundStop domain extension is reviewed.
- For TrafficManagementInitiative records, parser artifacts caused by
  free-text phrases such as `USERS CAN EXPECT` should be marked invalid, while
  source-supported ARTCC facilities should remain profile gaps unless a reviewed
  bridge is added.
- Empty `COMMENTS:` fields should not produce `initiativeComments`; if the
  extractor captures the following `EFFECTIVE TIME`, signature, or footer text,
  mark that candidate invalid.
- Future multi-round audits should sample both high-rejection and accepted-only
  records so the gold set does not overfit the rejection lane.
