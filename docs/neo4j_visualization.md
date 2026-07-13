# Neo4j Visualization

The cross-source build keeps Turtle as the semantic/audit representation and
also writes a canonical Neo4j property-graph projection:

- `data/kg/cross_source/<snapshot-set>/neo4j_nodes.jsonl`
- `data/kg/cross_source/<snapshot-set>/neo4j_relationships.jsonl`

Only accepted alignments enter this projection. Quarantined and rejected
decisions remain outside the displayed canonical graph.

## Export

```bash
uv run aviation-ai cross-source neo4j-export \
  --config configs/cross_source_v1.yaml
```

## Load into Neo4j

Install the optional official Python driver and set connection details without
putting credentials in repository files or shell history:

```bash
uv sync --extra neo4j
export NEO4J_URI='bolt://localhost:7687'
export NEO4J_USERNAME='neo4j'
export NEO4J_PASSWORD='your-local-password'
export NEO4J_DATABASE='neo4j'
uv run aviation-ai cross-source neo4j-load \
  --config configs/cross_source_v1.yaml \
  --replace-snapshot
```

`--replace-snapshot` removes only nodes carrying the configured snapshot ID
before loading. Omit it to idempotently merge the projection.

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
