# ATMONTO semantic coverage

This is the semantic-control-plane inventory for the active aviation KG. It
is not a source/evidence dataset and it is not a query backend.

The report is rebuilt from the six checksum-pinned NASA OWL/XML modules:

```text
ATM.owl
NAS.owl
data.owl
equipment.owl
general.owl
atmontoCore.owl
```

The generator records:

- declared ATMONTO classes;
- object and datatype properties;
- class-subclass edges;
- property domain/range or datatype signatures;
- functional-property declarations;
- exact/minimum/maximum cardinality restrictions;
- the eight semantic domains used by the project;
- whether each term is active, planned, or unsupported in the current
  application/validation profiles.

The current catalog contains 105 classes, 106 object properties, 176
datatype properties, 83 hierarchy axioms, 282 property signatures, and 13
cardinality constraints. The runtime admits only a subset of these terms:

```text
active       73
planned      19
unsupported  295
```

`planned` is an explicit next-scope list, not an implicit promise that every
upstream term will be implemented. `unsupported` means that the current
source adapters and publication profiles do not admit the term.

## Why this makes a KG necessary

A flat relational representation can store individual fields such as an
airport code, a weather value, or an advisory time. It does not by itself
provide the semantic contract that makes the following path type-safe and
source-traceable:

```text
Flight
  -> departureAirport -> Airport
  -> withinARTCC -> ARTCC
  -> traversesSector -> Sector
  -> hasActualRoute -> Route
  -> associatedWeather -> MeteorologicalReport
  -> subjectToTMI -> TrafficManagementInitiative
```

The value of the KG is therefore not the presence of RDF syntax. It is the
combination of:

1. ontology class hierarchy and property signatures;
2. multi-hop relations across source families;
3. temporal and spatial entities;
4. evidence and derivation links attached to facts;
5. graph-pattern retrieval that can return a supported path instead of a
   manually joined row set.

The report does not claim full OWL/RDFS inference or an exact ATMGRAPH
replica. It measures the semantic surface on which those graph capabilities
can be evaluated.

## Rebuild

```bash
uv run python -m aviation_agentic_ai.agent_system.ontology_coverage \
  --output data/ontology/curated/atmonto_semantic_coverage_v1.json
```

The JSON is deterministic and can be regenerated after changing the pinned
OWL inputs or the curated application profiles.
