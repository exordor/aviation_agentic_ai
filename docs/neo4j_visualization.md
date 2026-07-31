# Neo4j Visualization

> **Historical visualization guide — superseded.** The commands and projection
> shapes below describe the former cross-source snapshot pipeline. Neo4j is now
> an optional rebuildable export from the authoritative SQLite evidence store.
> Use the current `agent-system neo4j-export --store-dir ...` command documented
> in `REPRODUCIBILITY.md`.

The cross-source build keeps Turtle as the semantic/audit representation and
also writes a canonical Neo4j property-graph projection:

- `data/kg/cross_source/<snapshot-set>/neo4j_nodes.jsonl`
- `data/kg/cross_source/<snapshot-set>/neo4j_relationships.jsonl`

Only accepted alignments enter this projection. Quarantined and rejected
decisions remain outside the displayed canonical graph.

The former cross-source export/load commands have been removed. The files and
queries below document the historical projection only; use the current
`agent-system neo4j-export` command for an executable export path.

## Neo4j Browser Queries

Show accepted abbreviation or facility alignments:

```cypher
MATCH p=(m:AcceptedMention)-[:DENOTES]->(target)
RETURN p
LIMIT 100
```

Show advisory-to-weather associations:

```cypher
MATCH p=(a:SourceRecord)-[r:HAS_CONTEMPORANEOUS_OBSERVATION|HAS_OVERLAPPING_FORECAST]->(w:WeatherRecord)
RETURN p
LIMIT 100
```

Show the JFK evidence neighborhood, including facility alignment and linked
weather records:

```cypher
MATCH p=(f:Facility)<-[:DENOTES]-(m:AcceptedMention)-[:DERIVED_FROM]->(a:SourceRecord)
      -[r:HAS_CONTEMPORANEOUS_OBSERVATION|HAS_OVERLAPPING_FORECAST]->(w:WeatherRecord)
WHERE any(code IN f.codes WHERE code IN ['FAA:JFK', 'IATA:JFK', 'ICAO:KJFK'])
RETURN p
LIMIT 200
```

The weather relationships retain facility ID, advisory/evidence intervals,
link method, authority sources, raw evidence text, and `causal_claim=false`.
