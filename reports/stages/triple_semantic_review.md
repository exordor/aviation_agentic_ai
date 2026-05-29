# Triple Semantic Review Sample

- KG: `data/kg/06_phak_ch4_0.structure_aware.kg.jsonl`
- Triples total: 448
- Sample size: 100
- Semantic correctness claimed: no
- All annotation fields are initialized as `needs_review` for manual review.

## Annotation Fields

- `subject_correct`
- `object_correct`
- `predicate_correct`
- `direction_correct`
- `evidence_supports_triple`
- `too_generic`
- `duplicate_or_near_duplicate`
- `reviewer_notes`

## Sample Preview

- `06_phak_ch4_0-structure_aware-p00-c02-kg00-302d28265e`: Cl_Concept -supportedByEvidence-> Cl_Evidence (chunk `06_phak_ch4_0-structure_aware-p00-c02`)
- `06_phak_ch4_0-structure_aware-p00-c02-kg01-13e9f7b56d`: Cl_Concept -affects-> Cl_AircraftPerformance (chunk `06_phak_ch4_0-structure_aware-p00-c02`)
- `06_phak_ch4_0-structure_aware-p00-c02-kg02-67295bee69`: Cl_Concept -appliesTo-> Cl_Aircraft (chunk `06_phak_ch4_0-structure_aware-p00-c02`)
- `06_phak_ch4_0-structure_aware-p00-c02-kg03-67295bee69`: Cl_Concept -appliesTo-> Cl_Aircraft (chunk `06_phak_ch4_0-structure_aware-p00-c02`)
- `06_phak_ch4_0-structure_aware-p00-c03-kg00-ec85a2e957`: the principles involved -affects-> natural forces (chunk `06_phak_ch4_0-structure_aware-p00-c03`)
- `06_phak_ch4_0-structure_aware-p00-c03-kg01-d8ad94bed4`: natural forces -supportedByEvidence-> the principles involved (chunk `06_phak_ch4_0-structure_aware-p00-c03`)
- `06_phak_ch4_0-structure_aware-p00-c04-kg00-8748d82ca7`: Cl_Atmosphere -hasComponent-> Cl_Air (chunk `06_phak_ch4_0-structure_aware-p00-c04`)
- `06_phak_ch4_0-structure_aware-p00-c04-kg01-898cdb205b`: Cl_Air -hasComponent-> Cl_Fluid (chunk `06_phak_ch4_0-structure_aware-p00-c04`)
- `06_phak_ch4_0-structure_aware-p00-c04-kg02-bf8ee5a3ea`: Cl_Atmosphere -hasQuantity-> Cl_Altitude (chunk `06_phak_ch4_0-structure_aware-p00-c04`)
- `06_phak_ch4_0-structure_aware-p00-c05-kg00-9d032c2a9a`: atmosphere -hasQuantity-> below 35,000 feet altitude (chunk `06_phak_ch4_0-structure_aware-p00-c05`)
- `06_phak_ch4_0-structure_aware-p00-c06-kg00-f932292260`: higher altitude -partOf-> the atmosphere (chunk `06_phak_ch4_0-structure_aware-p00-c06`)
- `06_phak_ch4_0-structure_aware-p00-c06-kg01-313467454a`: oxygen -hasQuantity-> below 35,000 feet altitude (chunk `06_phak_ch4_0-structure_aware-p00-c06`)
- `06_phak_ch4_0-structure_aware-p00-c06-kg02-cb7d201076`: oxygen -partOf-> the atmosphere (chunk `06_phak_ch4_0-structure_aware-p00-c06`)
- `06_phak_ch4_0-structure_aware-p00-c07-kg00-bcf45f34cc`: oxygen -partOf-> atmosphere (chunk `06_phak_ch4_0-structure_aware-p00-c07`)
- `06_phak_ch4_0-structure_aware-p00-c07-kg01-f0020d5879`: oxygen -hasCondition-> below 35,000 feet altitude (chunk `06_phak_ch4_0-structure_aware-p00-c07`)
- `06_phak_ch4_0-structure_aware-p01-c00-kg00-ae6aa92099`: Leading edge of wing -hasComponent-> Microscopic surface of a wing (chunk `06_phak_ch4_0-structure_aware-p01-c00`)
- `06_phak_ch4_0-structure_aware-p01-c00-kg01-c8df9d6f0f`: Microscopic surface of a wing -partOf-> wing (chunk `06_phak_ch4_0-structure_aware-p01-c00`)
- `06_phak_ch4_0-structure_aware-p01-c01-kg00-9af2938ab8`: Air -partOf-> Fluid (chunk `06_phak_ch4_0-structure_aware-p01-c01`)
- `06_phak_ch4_0-structure_aware-p01-c02-kg00-178e9ee3e0`: Cl_Air -partOf-> Cl_Fluid (chunk `06_phak_ch4_0-structure_aware-p01-c02`)
- `06_phak_ch4_0-structure_aware-p01-c02-kg01-a5b105db61`: Cl_Air -supportedByEvidence-> Cl_Fluid (chunk `06_phak_ch4_0-structure_aware-p01-c02`)
- ... 80 additional triples in JSON sample
