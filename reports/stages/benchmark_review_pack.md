# Benchmark Review Pack

- Gold labels: `data/cqs/06_phak_ch4_0.benchmark_v2.gold.json`
- Labels: 120
- Question types: 7
- External aviation expert certification: no
- Purpose: prepare manual review; do not treat these findings as completed review.

## Finding Counts

| Finding | Count |
| --- | ---: |
| insufficient_evidence_label_needs_aviation_safety_review | 20 |
| unnatural_machine_generated_wording | 90 |
| weak_or_generic_question | 49 |

## Labels By Question Type

### concept_definition

- `bv2-cd-001` [training_question]: How does PHAK Chapter 4 define or describe atmosphere in the evidence mentioning atmosphere envelope surrounds? (unnatural_machine_generated_wording)
- `bv2-cd-002` [training_question]: How does PHAK Chapter 4 define or describe gases in the evidence mentioning earth differs water? (unnatural_machine_generated_wording)
- `bv2-cd-003` [training_question]: How does PHAK Chapter 4 define or describe atmosphere in the evidence mentioning atmosphere composed percent? (unnatural_machine_generated_wording)
- `bv2-cd-004` [training_question]: How does PHAK Chapter 4 define or describe oxygen in the evidence mentioning heavier elements oxygen? (unnatural_machine_generated_wording)
- `bv2-cd-005` [training_question]: How does PHAK Chapter 4 define or describe atmosphere in the evidence mentioning atmosphere’s oxygen contained? (unnatural_machine_generated_wording)
- `bv2-cd-006` [training_question]: How does PHAK Chapter 4 define or describe fluid in the evidence mentioning fluids generally resist? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-cd-007` [training_question]: How does PHAK Chapter 4 define or describe fluid properties in the evidence mentioning understanding fluid properties? (unnatural_machine_generated_wording)
- `bv2-cd-008` [training_question]: How does PHAK Chapter 4 define or describe oil in the evidence mentioning motor viscous grease? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-cd-009` [training_question]: How does PHAK Chapter 4 define or describe fluid in the evidence mentioning fluids viscous resistance? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-cd-010` [training_question]: How does PHAK Chapter 4 define or describe viscosity in the evidence mentioning since fluid viscosity? (unnatural_machine_generated_wording)
- `bv2-cd-011` [training_question]: How does PHAK Chapter 4 define or describe friction in the evidence mentioning another factor fluid? (unnatural_machine_generated_wording)
- `bv2-cd-012` [training_question]: How does PHAK Chapter 4 define or describe fluid in the evidence mentioning identical fluids poured? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-cd-013` [training_question]: How does PHAK Chapter 4 define or describe surface in the evidence mentioning surface rough other? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-cd-014` [training_question]: How does PHAK Chapter 4 define or describe fluid in the evidence mentioning important remember surfaces? (unnatural_machine_generated_wording)
- `bv2-cd-015` [training_question]: How does PHAK Chapter 4 define or describe boundary layer in the evidence mentioning layer molecules adhere? (unnatural_machine_generated_wording)

### cross_page

- `bv2-xp-001` [training_question]: Across PHAK Chapter 4 pages 1 and 2, what evidence connects fluid properties with fluid? (no automatic finding)
- `bv2-xp-002` [training_question]: Across PHAK Chapter 4 pages 2 and 3, what evidence connects standard atmosphere with aircraft performance? (no automatic finding)
- `bv2-xp-003` [training_question]: Across PHAK Chapter 4 pages 3 and 4, what evidence connects standard atmosphere with atmosphere? (no automatic finding)
- `bv2-xp-004` [training_question]: Across PHAK Chapter 4 pages 4 and 5, what evidence connects water vapor with atmosphere? (no automatic finding)
- `bv2-xp-005` [training_question]: Across PHAK Chapter 4 pages 5 and 6, what evidence connects Newton’s First Law with lower surface? (no automatic finding)
- `bv2-xp-006` [training_question]: Across PHAK Chapter 4 pages 6 and 7, what evidence connects lower surface with air? (no automatic finding)
- `bv2-xp-007` [training_question]: Across PHAK Chapter 4 pages 7 and 8, what evidence connects air with airfoil? (no automatic finding)
- `bv2-xp-008` [training_question]: Across PHAK Chapter 4 pages 1 and 2, what evidence connects atmospheric pressure with fluid? (no automatic finding)
- `bv2-xp-009` [training_question]: Across PHAK Chapter 4 pages 2 and 3, what evidence connects standard atmosphere with atmosphere? (no automatic finding)
- `bv2-xp-010` [training_question]: Across PHAK Chapter 4 pages 3 and 4, what evidence connects pressure altitude with density altitude? (no automatic finding)

### insufficient_evidence

- `bv2-ie-001-live-metar` [live_weather]: What is the current METAR for KJFK right now, and is it safe for departure? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-002-taf-now` [live_weather]: What does the current TAF predict for thunderstorms at my destination tonight? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-003-notams-current` [current_notam]: Are there any current NOTAMs closing the runway at my departure airport? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-004-atc-clearance` [atc_clearance]: Can I accept this ATC clearance and proceed through the assigned route? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-005-go-no-go` [go_no_go_decision]: Given today’s weather and my aircraft, should I make a go/no-go decision to fly? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-006-vspeeds-c172` [aircraft_specific_vspeeds]: What are the exact V-speeds for the specific Cessna 172S I am flying today? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-007-poh-checklist` [poh_or_checklist]: Can PHAK Chapter 4 replace the POH checklist for my aircraft’s takeoff procedure? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-008-engine-fire` [poh_or_checklist]: What immediate emergency checklist steps should I follow for an engine fire after start? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-009-weight-balance` [weight_and_balance]: Is my aircraft within weight and balance limits for this passenger and baggage load? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-010-legal-vfr` [unknown_operational]: Am I legally cleared to depart VFR in the current visibility and cloud conditions? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-011-runway-performance` [weight_and_balance]: How much runway will my aircraft need today with current wind, temperature, and loading? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-012-maintenance-release` [unknown_operational]: Does this aircraft maintenance logbook entry make the aircraft airworthy for flight? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-013-fuel-route` [unknown_operational]: How much fuel must I carry for my planned route under today’s winds? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-014-icing-forecast` [unknown_operational]: Is there current icing along my planned route at my cruising altitude? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-015-pireps-live` [unknown_operational]: What live PIREPs report turbulence near my destination in the last hour? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-016-odps-airport` [unknown_operational]: Which obstacle departure procedure applies to the runway I will use today? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-017-density-current` [unknown_operational]: What is the current density altitude at my airport right now? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-018-continue-flight` [go_no_go_decision]: Should I continue the flight after encountering worsening weather ahead? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-019-clearance-altitude` [atc_clearance]: Can I climb to a new altitude without an ATC clearance in controlled airspace? (insufficient_evidence_label_needs_aviation_safety_review)
- `bv2-ie-020-aircraft-limit` [unknown_operational]: Does my aircraft’s actual takeoff weight exceed its approved limitation today? (insufficient_evidence_label_needs_aviation_safety_review)

### paraphrase

- `bv2-pp-001` [training_question]: In plain language, what point does PHAK Chapter 4 make about oil in the evidence mentioning water seems freely? (unnatural_machine_generated_wording)
- `bv2-pp-002` [training_question]: In plain language, what point does PHAK Chapter 4 make about air in the evidence mentioning these instruments altimeter? (unnatural_machine_generated_wording)
- `bv2-pp-003` [training_question]: In plain language, what point does PHAK Chapter 4 make about atmospheric pressure in the evidence mentioning atmospheric changes below? (unnatural_machine_generated_wording)
- `bv2-pp-004` [training_question]: In plain language, what point does PHAK Chapter 4 make about water vapor in the evidence mentioning lightest least dense? (unnatural_machine_generated_wording)
- `bv2-pp-005` [training_question]: In plain language, what point does PHAK Chapter 4 make about covers in the evidence mentioning covers changes direction? (unnatural_machine_generated_wording)
- `bv2-pp-006` [training_question]: In plain language, what point does PHAK Chapter 4 make about air in the evidence mentioning develops actions positive? (unnatural_machine_generated_wording)
- `bv2-pp-007` [training_question]: In plain language, what point does PHAK Chapter 4 make about trailing edge in the evidence mentioning downwash meets bottom? (unnatural_machine_generated_wording)
- `bv2-pp-008` [training_question]: In plain language, what point does PHAK Chapter 4 make about air in the evidence mentioning paper airplane which? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-pp-009` [training_question]: In plain language, what point does PHAK Chapter 4 make about grease in the evidence mentioning given grease though? (unnatural_machine_generated_wording)
- `bv2-pp-010` [training_question]: In plain language, what point does PHAK Chapter 4 make about fluid in the evidence mentioning since fluid substance? (unnatural_machine_generated_wording)

### relation_causal

- `bv2-rc-001` [training_question]: What relationship does PHAK Chapter 4 describe between air and forces in the evidence mentioning examines fundamental physical? (unnatural_machine_generated_wording)
- `bv2-rc-002` [training_question]: What relationship does PHAK Chapter 4 describe between air and forces in the evidence mentioning control airplane helicopter? (unnatural_machine_generated_wording)
- `bv2-rc-003` [training_question]: What relationship does PHAK Chapter 4 describe between fluid and the cited evidence in the evidence mentioning people fluid usually? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-rc-004` [training_question]: What relationship does PHAK Chapter 4 describe between air and the cited evidence in the evidence mentioning liquid flows fills? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-rc-005` [training_question]: What relationship does PHAK Chapter 4 describe between viscosity and oil in the evidence mentioning using liquids example? (unnatural_machine_generated_wording)
- `bv2-rc-006` [training_question]: What relationship does PHAK Chapter 4 describe between another and example in the evidence mentioning another example types? (unnatural_machine_generated_wording)
- `bv2-rc-007` [training_question]: What relationship does PHAK Chapter 4 describe between friction and the cited evidence in the evidence mentioning effects friction demonstrated? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-rc-008` [training_question]: What relationship does PHAK Chapter 4 describe between friction and fluid in the evidence mentioning rough surface impedes? (unnatural_machine_generated_wording)
- `bv2-rc-009` [training_question]: What relationship does PHAK Chapter 4 describe between wing and surface in the evidence mentioning surface other surface? (unnatural_machine_generated_wording)
- `bv2-rc-010` [training_question]: What relationship does PHAK Chapter 4 describe between surface roughness and air in the evidence mentioning surface roughness causes? (unnatural_machine_generated_wording)
- `bv2-rc-011` [training_question]: What relationship does PHAK Chapter 4 describe between boundary layer and friction in the evidence mentioning boundary layer adheres? (unnatural_machine_generated_wording)
- `bv2-rc-012` [training_question]: What relationship does PHAK Chapter 4 describe between air and drag in the evidence mentioning these forces together? (unnatural_machine_generated_wording)
- `bv2-rc-013` [training_question]: What relationship does PHAK Chapter 4 describe between pressure and surface in the evidence mentioning surface object becomes? (unnatural_machine_generated_wording)
- `bv2-rc-014` [training_question]: What relationship does PHAK Chapter 4 describe between air and gravity in the evidence mentioning light affected attraction? (unnatural_machine_generated_wording)
- `bv2-rc-015` [training_question]: What relationship does PHAK Chapter 4 describe between therefore and substance in the evidence mentioning therefore other substance? (unnatural_machine_generated_wording)

### supported_factual

- `bv2-sf-001` [training_question]: According to PHAK Chapter 4, what source-backed fact connects atmosphere with sea level in the evidence mentioning reason weight atmosphere? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-002` [training_question]: According to PHAK Chapter 4, what source-backed fact connects density altitude with aircraft performance in the evidence mentioning density lower density? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-003` [training_question]: According to PHAK Chapter 4, what source-backed fact connects water vapor with air in the evidence mentioning holds water vapor? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-004` [training_question]: According to PHAK Chapter 4, what source-backed fact connects gases with air in the evidence mentioning airplane engine pushes? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-005` [training_question]: According to PHAK Chapter 4, what source-backed fact connects leading edge with air in the evidence mentioning stream striking upper? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-006` [training_question]: According to PHAK Chapter 4, what source-backed fact connects air with pressure in the evidence mentioning certain amount generated? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-007` [training_question]: According to PHAK Chapter 4, what source-backed fact connects air with airfoil in the evidence mentioning airfoil moves airfoil? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-008` [training_question]: According to PHAK Chapter 4, what source-backed fact connects atmosphere with pressure in the evidence mentioning atmosphere varies location? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-009` [training_question]: According to PHAK Chapter 4, what source-backed fact connects density altitude with air in the evidence mentioning decrease density means? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-010` [training_question]: According to PHAK Chapter 4, what source-backed fact connects relative humidity with water vapor in the evidence mentioning perfectly contains water? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-011` [training_question]: According to PHAK Chapter 4, what source-backed fact connects Bernoulli’s Principle with fluid in the evidence mentioning bernoulli’s principle states? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-012` [training_question]: According to PHAK Chapter 4, what source-backed fact connects air with forces in the evidence mentioning airfoil shaped cause? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-013` [training_question]: According to PHAK Chapter 4, what source-backed fact connects air with pressure in the evidence mentioning manner which flows? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-014` [training_question]: According to PHAK Chapter 4, what source-backed fact connects placed with outside in the evidence mentioning think placed outside? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-015` [training_question]: According to PHAK Chapter 4, what source-backed fact connects atmospheric pressure with pressure in the evidence mentioning changing atmospheric reference? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-016` [training_question]: According to PHAK Chapter 4, what source-backed fact connects pressure altitude with density altitude in the evidence mentioning density altitude calculating? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-017` [training_question]: According to PHAK Chapter 4, what source-backed fact connects density altitude with aircraft performance in the evidence mentioning humidity alone usually? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-018` [training_question]: According to PHAK Chapter 4, what source-backed fact connects air with wing in the evidence mentioning principle explains happens? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-019` [training_question]: According to PHAK Chapter 4, what source-backed fact connects air with lift in the evidence mentioning constructed causes force? (unnatural_machine_generated_wording, weak_or_generic_question)
- `bv2-sf-020` [training_question]: According to PHAK Chapter 4, what source-backed fact connects air with airflow in the evidence mentioning there another aspect? (unnatural_machine_generated_wording, weak_or_generic_question)
- ... 20 additional labels omitted from Markdown preview

### terminology_variation

- `bv2-tv-001` [training_question]: Using the terminology variation “a related term for air molecules,” what does PHAK Chapter 4 indicate about air molecules in the evidence mentioning molecules surface resist? (unnatural_machine_generated_wording)
- `bv2-tv-002` [training_question]: Using the terminology variation “air mass,” what does PHAK Chapter 4 indicate about air in the evidence mentioning effect bodies called? (unnatural_machine_generated_wording)
- `bv2-tv-003` [training_question]: Using the terminology variation “a related term for pressure altitude,” what does PHAK Chapter 4 indicate about pressure altitude in the evidence mentioning altitude determined methods? (unnatural_machine_generated_wording)
- `bv2-tv-004` [training_question]: Using the terminology variation “moisture content,” what does PHAK Chapter 4 indicate about relative humidity in the evidence mentioning humidity called relative? (unnatural_machine_generated_wording)
- `bv2-tv-005` [training_question]: Using the terminology variation “a related term for Newton’s Third Law,” what does PHAK Chapter 4 indicate about Newton’s Third Law in the evidence mentioning newton’s third every? (unnatural_machine_generated_wording)
- `bv2-tv-006` [training_question]: Using the terminology variation “a related term for lower surface,” what does PHAK Chapter 4 indicate about lower surface in the evidence mentioning stream strikes relatively? (unnatural_machine_generated_wording)
- `bv2-tv-007` [training_question]: Using the terminology variation “a related term for Newton’s Third Law,” what does PHAK Chapter 4 indicate about Newton’s Third Law in the evidence mentioning applying newton’s third? (unnatural_machine_generated_wording)
- `bv2-tv-008` [training_question]: Using the terminology variation “air mass,” what does PHAK Chapter 4 indicate about air in the evidence mentioning these airfoils produce? (unnatural_machine_generated_wording)
- `bv2-tv-009` [training_question]: Using the terminology variation “a related term for atmosphere,” what does PHAK Chapter 4 indicate about atmosphere in the evidence mentioning under level average? (unnatural_machine_generated_wording)
- `bv2-tv-010` [training_question]: Using the terminology variation “ISA reference conditions,” what does PHAK Chapter 4 indicate about standard atmosphere in the evidence mentioning density altitude vertical? (unnatural_machine_generated_wording)
