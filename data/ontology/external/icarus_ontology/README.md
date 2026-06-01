# ICARUS Ontology External Source

Source repository: https://github.com/UCY-LINC-LAB/icarus-ontology

Downloaded commit: `b1d3ee64085ba94e254eaa0900b82e3cc90d6f4e`

License: MIT, see `LICENSE`.

## Local Files

- `ICARUS_Ontology.owl`: main ICARUS aviation dataset ontology.
- `NASA/ATM.owl`: NASA ATMONTO air traffic management module.
- `NASA/NAS.owl`: NASA ATMONTO National Airspace System module.
- `NASA/atmontoCore.owl`: import aggregator for NASA ATMONTO modules.
- `NASA/data.owl`: NASA ATMONTO data/source module.
- `NASA/equipment.owl`: NASA ATMONTO equipment module.
- `NASA/general.owl`: NASA ATMONTO general concepts module.
- `Epidemiology-Ontology/epo.owl`: epidemiology import used by ICARUS.
- `catalog-v001.xml`: Protege/XML catalog mapping ontology IRIs to local files.

## Project Role

These files are kept as an external reference ontology for aviation schema
alignment, vocabulary comparison, and future ontology-expansion proposals.
They do not replace the active PHAK Chapter 4 extraction ontology:
`data/ontology/curated/06_phak_ch4_0.curated.ttl`.

The active project ontology remains deliberately smaller because it constrains
KG extraction for the current PHAK-scoped GraphRAG experiment. ICARUS and
ATMONTO can be used to justify term mappings and candidate extensions, but they
should not be described as current project ground truth.

## Syntax Note

The upstream `.owl` files use OWL/XML syntax. The current project ontology
commands are based on `rdflib.Graph().parse(...)` and expect RDF serializations
such as Turtle or RDF/XML. Treat these files as external source artifacts unless
an OWL/XML adapter or conversion step is added.

## Quick Structural Counts

| File | Ontology IRI | Imports | Classes | Object properties | Data properties | Named individuals |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `ICARUS_Ontology.owl` | `urn:absolute:icarus` | 2 | 67 | 41 | 273 | 63 |
| `NASA/ATM.owl` | `https://data.nasa.gov/ontologies/atmonto/ATM` | 1 | 36 | 49 | 53 | 0 |
| `NASA/NAS.owl` | `https://data.nasa.gov/ontologies/atmonto/NAS` | 1 | 37 | 33 | 39 | 0 |
| `NASA/atmontoCore.owl` | `https://data.nasa.gov/ontologies/atmontoCore` | 5 | 0 | 0 | 0 | 0 |
| `NASA/data.owl` | `https://data.nasa.gov/ontologies/atmonto/data` | 1 | 13 | 11 | 56 | 0 |
| `NASA/equipment.owl` | `https://data.nasa.gov/ontologies/atmonto/equipment` | 1 | 23 | 9 | 20 | 0 |
| `NASA/general.owl` | `https://data.nasa.gov/ontologies/atmonto/general` | 0 | 13 | 4 | 8 | 0 |
