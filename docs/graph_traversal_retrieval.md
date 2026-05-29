# Graph Traversal Retrieval

## Why lexical KG search is a baseline

The original KG retrieval path scores every extracted triple by lexical overlap with the
question, then returns the chunks attached to the highest-scoring triples. This is useful
as a transparent baseline, but it does not use graph structure. A `graph_hops` value of 1,
2, or 3 cannot change the neighborhood because lexical scoring treats each triple as an
independent text record.

## Ontology-guided bounded traversal

Traversal retrieval builds a directed `networkx.MultiDiGraph` from extracted KG triples.
Normalized entity labels become node ids, and directed edges preserve the extracted
subject-to-object relation. Edge metadata keeps provenance fields such as `triple_id`,
`predicate`, `chunk_id`, `page`, `evidence_text`, and `confidence`.

Given linked seed entities from a question, traversal runs breadth-first search over
outgoing KG edges. `graph_hops` is the maximum path length:

- `graph_hops=1` returns only one-edge neighborhoods.
- `graph_hops=2` can return two-edge chains such as entity -> intermediate -> target.
- `graph_hops=3` can return three-edge chains, still bounded to avoid path explosion.

Cycles are skipped by refusing to revisit a node already present in the candidate path.
Reverse traversal is supported by the traversal primitive as an explicit parameter, but it
is not enabled by default in retrieval.

## Entity linking

Entity linking normalizes the question and matches normalized graph node labels as
phrases. It also loads optional aliases from `configs/entity_aliases.yaml`; for example,
`AOA` links to `angle of attack`, and `CP` links to `center of pressure`.

If no exact label or alias match is found, the linker falls back to the graph nodes with
the highest lexical overlap with the question. Fallback seeds are marked in path metadata
so reports can distinguish direct entity links from weaker seed choices.

## Path scoring

Each candidate path receives a transparent score combining:

- entity label overlap with question terms
- predicate intent matching using aviation relation keywords
- evidence text overlap
- average edge confidence
- a small penalty for longer paths

The score is used only for ranking returned graph chunks, triples, and paths. It is not a
claim that traversal improves retrieval quality; report metrics must support any such
claim.

## Difference from vector retrieval

Vector retrieval searches chunk text by semantic similarity. Traversal retrieval searches
the extracted KG topology and returns chunks attached to KG paths. Hybrid mode can fuse
vector hits with graph hits, but retrieval metrics, KG evidence metrics, and path metrics
remain separate.

## Limitations

- Sparse KG extraction can leave useful chunks unreachable from linked entities.
- Entity-linking errors can start traversal from the wrong node or miss a good seed.
- Noisy triples can create misleading paths even when traversal is structurally valid.
- Larger KGs can produce path explosion; traversal is bounded by hop count and path count.
- Direction matters: default traversal follows subject -> object edges and will not use
  incoming edges unless reverse traversal is explicitly enabled by lower-level callers.
