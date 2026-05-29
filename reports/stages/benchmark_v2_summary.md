# Benchmark V2 Summary

- Label set: `phak_ch4_benchmark_v2_thesis_seed`
- Review status: `machine_seeded_requires_manual_review`
- Labels: 120
- Supported labels: 100
- Insufficient-evidence labels: 20
- Span-level labels: 100
- Evidence span validation: 110/110 passed
- Validation passed: True

## Category Distribution

| Question type | Count |
| --- | ---: |
| concept_definition | 15 |
| cross_page | 10 |
| insufficient_evidence | 20 |
| paraphrase | 10 |
| relation_causal | 15 |
| supported_factual | 40 |
| terminology_variation | 10 |

## Missing Fields

| Field | Count |
| --- | ---: |
| none | 0 |

## Warnings

- none

## Sample Labels

### concept_definition

- `bv2-cd-001`: How does PHAK Chapter 4 define or describe atmosphere in the evidence mentioning atmosphere envelope surrounds?
  Answer key: The atmosphere is an envelope of air that surrounds the Earth and rests upon its surface.
- `bv2-cd-002`: How does PHAK Chapter 4 define or describe gases in the evidence mentioning earth differs water?
  Answer key: It is as much a part of the Earth as the seas or the land, but air differs from land and water as it is a mixture of gases.

### cross_page

- `bv2-xp-001`: Across PHAK Chapter 4 pages 1 and 2, what evidence connects fluid properties with fluid?
  Answer key: Both liquids and gasses display these unique fluid properties, even though they differ greatly in density. Often, pressure is measured in pounds of force exerted per square inch of an object, or PSI.
- `bv2-xp-002`: Across PHAK Chapter 4 pages 2 and 3, what evidence connects standard atmosphere with aircraft performance?
  Answer key: An object completely immersed in a fluid will feel pressure uniformly around the entire surface of the object. Since aircraft performance is compared and evaluated with respect to the standard atmosphere, all aircraft instruments are calibrated for the standard atmosphere.

### insufficient_evidence

- `bv2-ie-001-live-metar`: What is the current METAR for KJFK right now, and is it safe for departure?
  Answer key: Insufficient evidence in PHAK Chapter 4. Use current official sources, the aircraft POH/AFM, approved checklists, ATC instructions, regulations, instructor guidance, and pilot judgment as applicable.
- `bv2-ie-002-taf-now`: What does the current TAF predict for thunderstorms at my destination tonight?
  Answer key: Insufficient evidence in PHAK Chapter 4. Use current official sources, the aircraft POH/AFM, approved checklists, ATC instructions, regulations, instructor guidance, and pilot judgment as applicable.

### paraphrase

- `bv2-pp-001`: In plain language, what point does PHAK Chapter 4 make about oil in the evidence mentioning water seems freely?
  Answer key: The water seems to flow freely while the oil flows much more slowly.
- `bv2-pp-002`: In plain language, what point does PHAK Chapter 4 make about air in the evidence mentioning these instruments altimeter?
  Answer key: These instruments are the altimeter, airspeed indicator, vertical speed indicator, and manifold pressure gauge.

### relation_causal

- `bv2-rc-001`: What relationship does PHAK Chapter 4 describe between air and forces in the evidence mentioning examines fundamental physical?
  Answer key: This chapter examines the fundamental physical laws governing the forces acting on an aircraft in flight, and what effect these natural laws and forces have on the performance characteristics of aircraft.
- `bv2-rc-002`: What relationship does PHAK Chapter 4 describe between air and forces in the evidence mentioning control airplane helicopter?
  Answer key: To control an aircraft, be it an airplane, helicopter, glider, or balloon, the pilot must understand the principles involved and learn to use or counteract these natural forces.

### supported_factual

- `bv2-sf-001`: According to PHAK Chapter 4, what source-backed fact connects atmosphere with sea level in the evidence mentioning reason weight atmosphere?
  Answer key: For this reason, the weight of the atmosphere at 18,000 feet is one-half what it is at sea level.
- `bv2-sf-002`: According to PHAK Chapter 4, what source-backed fact connects density altitude with aircraft performance in the evidence mentioning density lower density?
  Answer key: As the density of the air increases (lower density altitude), aircraft performance increases;

### terminology_variation

- `bv2-tv-001`: Using the terminology variation “a related term for air molecules,” what does PHAK Chapter 4 indicate about air molecules in the evidence mentioning molecules surface resist?
  Answer key: Air molecules near the surface of the wing resist motion and have a relative velocity near zero.
- `bv2-tv-002`: Using the terminology variation “air mass,” what does PHAK Chapter 4 indicate about air in the evidence mentioning effect bodies called?
  Answer key: Its effect on bodies within the air is called pressure.
