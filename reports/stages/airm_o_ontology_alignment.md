# AIRM-O Ontology Alignment

- Snapshot date: 2026-06-01
- Retrieved at: 2026-06-01T03:02:53+00:00
- Role: `external_reference_ontology`
- Boundary: `external_reference_not_experiment_ground_truth`
- Manifest: `data/ontology/external/airm_o/manifest.json`
- Alignment JSONL: `data/ontology/mappings/atmonto_airm_alignment.jsonl`

## AIRM-O Inventory

- Classes: 915
- Object properties: 1761
- Datatype properties: 494
- Named individuals: 3727
- Domain axioms: 2255
- Range axioms: 2230

## ATMONTO Alignment

- Mapping records: 115
- `atmonto_subclass_of_airm`: 41
- `atmonto_superclass_of_airm`: 42
- `equivalent`: 32

## Use In Project Pipeline

- Use NASA ATMONTO as the primary schema constraint.
- Use AIRM-O as an external ATM interoperability reference.
- Use the alignment JSONL for profile coverage, mapping audits, and extension-gap analysis.
- Do not treat AIRM-O or the alignment records as ABox facts or experiment ground truth.
