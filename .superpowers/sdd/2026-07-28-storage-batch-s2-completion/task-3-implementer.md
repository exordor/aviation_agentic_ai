# Task 3 Implementer Report — S2C

## Delivered

- Extended `CorpusQueryStore` with corpus-owned formal facts, decision-context,
  public-observation, and evidence reads.
- Materialized full-corpus JSONL, canonical RDF, and Neo4j projections from
  `CorpusFact` plus `EvidenceLink`; source provenance uses content-addressed
  source-artifact identities. Context associations remain outside RDF/Neo4j.
- Added bounded `export-case` output with only the selected case, retained
  artifacts, source objects, and case Turtle; it creates no replayable run
  manifest or provider ledger.
- Cut over `ask` and `neo4j-export` to `--corpus-dir`; removed the former
  public `ask-corpus` command and run-directory query/export option. Existing
  run-backed CLI query tests are explicitly skipped because that interface is
  intentionally removed.
- Added focused corpus query, projection, and case-export coverage.

## Verification

```text
uv run pytest -q tests/test_agent_system_query_tool_graph.py \
  tests/test_agent_system_corpus_store.py \
  tests/test_agent_system_corpus_projection.py \
  tests/test_cli_agent_system.py \
  tests/test_agent_system_batch_two.py
144 passed, 13 skipped

uv run ruff check .
All checks passed

git diff --check
passed
```

An attempted full suite reached 958 passing tests before one expected obsolete
run-backed `ask` test and one pre-existing missing NASR archive fixture caused
failure. The obsolete test is now skipped with the removed interface; the
missing archive is unrelated to this task/worktree.

## Caveats

- Corpus queries remain deterministic and make zero model calls. The existing
  live Decision Case Analysis path has no corpus-native execution adapter in
  this increment; historical similarity remains insufficient.
- Documentation cutover is intentionally deferred to Task 4.

## Commit

`feat(agent-system): move query and projections to corpus` (local commit)
