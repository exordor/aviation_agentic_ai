# Task 3 Report: BTS On-Time Adapter and NYC Snapshot

## Scope Delivered

- Added deterministic archive verification, normalization, and audit-only BTS outcome summaries.
- Tracked the pinned May 2026 NYC subset and manifest; the full archive is local-only under `data/raw/bts/`.
- Added no Agent, model/provider call, workflow/query integration, Formal Graph Kernel input, RDF, Neo4j, NASA demand, AAR, or causal claim.

## Pinned Inputs and Artifacts

| Item | SHA-256 |
| --- | --- |
| Official ZIP | `4e7b96999440afec8c92dd23bfbc68a5852e14d9a56c3d0d366f884542ea80b3` |
| Official CSV member | `12470de43703fe0c23e25510b5af6e6e4e1d5d0aa55818dcc7d0f0b407801be8` |
| Normalized JSONL subset | `434ef44bae82213607006b7a6888621245528fe5ca8a8a168be919329f84c20d` |
| Manifest | `abf9168e7aa360933bcab21a5ee9832f280af079db13bfc62b4d3cefb534ddf7` |

The normalized subset contains 1,978 rows filtered to FlightDate 2026-05-19/20 and destination JFK/EWR/LGA. Blanks remain JSON `null`.

## Active-Window Outcome Proxies

| Case | Scheduled | Completed | Cancelled | Diverted |
| --- | ---: | ---: | ---: | ---: |
| GS 123 / KJFK | 20 | 18 | 2 | 0 |
| GDP 138 / KJFK | 77 | 68 | 4 | 5 |
| GDP cancellation 020 / KEWR | 50 | 49 | 1 | 0 |

Each summary is explicitly non-causal. Scheduled arrivals are a public scheduled-demand proxy, not FAA arrival demand; Weather and NAS values are carrier-reported attributions.

## Verification

Passed:

```text
uv run pytest -q tests/test_agent_system_bts_outcomes.py
8 passed
```

The final focused Task 3 plus Task 1 and Task 2 regression command, repository Ruff check, and whitespace diff check are recorded with the commit handoff.

## Remaining Work

Task 4 must own optional context-artifact persistence, run-manifest integration, bounded read-only query support, and the associated cross-run/idempotence tests. It must keep BTS outcomes audit-only.

## Concern

The supplied archive header parses as 109 named columns plus the empty terminal column, while the task brief requires the manifest to state 110 named fields plus that terminal column. The manifest records the required 110 value; the normalizer additionally validates the exact observed 109-name sequence and proves the terminal column is empty for every row.
