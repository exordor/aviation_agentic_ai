# Optional Wigolo Web Evidence Operations

Status: optional acquisition and read-only query integration

This document describes how the project can use a separately running Wigolo
sidecar to collect or inspect allowlisted public web documents. It is an
adapter boundary, not a replacement for the persistent aviation evidence
store, the ATMONTO publication profiles, or the Query Agent's support rules.

## Boundary and lifecycle

```text
operator-approved URL seed
        |
        v
Wigolo 0.2.1 sidecar (loopback REST)
        |
        v
project-owned web adapter
  URL policy + response contract + span validation
        |
        v
SQLite source asset/version/anchor/chunk records
        |
        +--> FTS5 and source-record Chroma (rebuildable)
        |
        +--> optional read-only web_search/web_fetch/web_extract tools
```

The sidecar only acquires or reads a document. The project owns canonical
source identity, content checksums, immutable versions, evidence anchors,
provenance, and support validation. A fetched page does not become an ATCSCC
fact, a Weather fact, a causal explanation, or a recommendation merely because
it was retrieved.

SQLite remains authoritative. The source-record FTS5 and Chroma views include
`web_document` source chunks alongside other admitted textual source versions.
The `tmi_events_v1` collection is built only from admitted TMI event
publications; a web document is not inserted into the event collection just
because it mentions a TMI.

RDF/Turtle, JSONL KG, and Neo4j exports are offline projections of SQLite
formal facts and their evidence links. Web source records appear in an export
only when an accepted formal fact or qualified evidence record already binds
to that source version. A standalone fetched page is not materialized as a
formal graph root by the web adapter.

## Sidecar installation and version boundary

The project does not vendor Wigolo and does not import its Python package.
Install and run the upstream sidecar according to its pinned release
documentation:

- [Wigolo repository](https://github.com/KnockOutEZ/wigolo)
- [REST tools](https://github.com/KnockOutEZ/wigolo/blob/main/docs/tools.md)
- [SDK and server usage](https://github.com/KnockOutEZ/wigolo/blob/main/docs/sdks.md)
- [Installation](https://github.com/KnockOutEZ/wigolo/blob/main/docs/installation.md)

The adapter is currently written against the documented Wigolo `0.2.1` REST
surface:

```text
GET  /health
POST /v1/search
POST /v1/fetch
POST /v1/extract
POST /v1/diff
```

The adapter owns a small project contract so an upstream response cannot
directly write to SQLite. If the sidecar changes its response shape or route
contract, the run is `blocked` until the adapter is updated and tested; it is
not silently treated as a successful collection.

Wigolo is licensed under AGPL-3.0. The repository keeps the integration at an
HTTP process boundary and does not copy upstream source or add Wigolo to the
runtime dependency set. This is a project distribution policy, not legal
advice; any redistribution of a modified or combined service should receive a
separate license review. See the [upstream license](https://raw.githubusercontent.com/KnockOutEZ/wigolo/main/LICENSE).

## Loopback REST operation

Run the sidecar separately and expose it on a local or otherwise controlled
endpoint. The tracked configuration uses:

```yaml
sources:
  web_evidence:
    enabled: false
    base_url: http://127.0.0.1:3333
    token_env: WIGOLO_API_TOKEN
```

The default is disabled. A normal `ingest`, including `--domain all`, makes
zero web calls while it is disabled. To activate it, use a local configuration
overlay with `enabled: true`, an explicit seed list, and an allowlist, then
provide the second runtime authorization flag:

```bash
uv run aviation-ai agent-system ingest \
  --config /path/to/local/web-enabled-aviation-knowledge.yaml \
  --store-dir data/stores/aviation/aviation-knowledge-web-v1 \
  --domain web \
  --allow-live-web
```

For query-time access, the corresponding opt-in is:

```bash
uv run aviation-ai agent-system ask \
  --config /path/to/local/web-enabled-aviation-knowledge.yaml \
  --store-dir data/stores/aviation/aviation-knowledge-web-v1 \
  --question "Find the relevant FAA reference and quote the supporting section." \
  --allow-live-web
```

Query-time web tools are read-only and are exposed as one optional `web`
capability family. `web_search` returns candidates only. `web_fetch` and
`web_extract` can return source-version/anchor support, but they do not write
to SQLite during an `ask`. The Query Agent still must satisfy the normal
statement-level support and claim-boundary checks.

## URL allowlist and seed policy

Every seed has an authority, document role, parser profile, and one or more
allowed domains. The global allowlist is an additional restriction; it cannot
expand a seed's domains. URL normalization removes fragments, rejects
credentials, preserves query parameters, and rejects hosts outside both
allowlists.

Keep the seed list small and explicit. A seed should identify a stable public
document or index that the research task actually needs. Do not use a broad
search result page as proof of an aviation fact. Search candidates must be
fetched and anchored before they can support a statement.

The sidecar token is read only from the configured environment variable. Do
not put tokens in YAML, command history, tracked reports, or source metadata.

## External scheduling

The project does not include a scheduler or daemon. A researcher may run
periodic collection from an external scheduler (for example, cron, launchd,
CI, or an orchestration service) using the same explicit command and a local
configuration overlay. Each invocation should:

1. verify that the sidecar health endpoint is reachable;
2. use a fixed allowlist and adapter version;
3. run `ingest --domain web --allow-live-web`;
4. inspect the summary and SQLite knowledge revision;
5. run `reindex` when source chunks changed and a vector view is required;
6. retain the sidecar and project logs outside Git.

Scheduling is an operational convenience, not part of the canonical data
model. A failed scheduled run must not delete or supersede the last accepted
source version.

## Failure states and recovery

The web domain uses the same compact outcome vocabulary as the rest of the
ingestion pipeline:

| State | Meaning | Store effect |
| --- | --- | --- |
| `ok` | Fetch passed URL, checksum, and evidence-span validation. | Append or reuse an immutable source version and source chunk. |
| `insufficient` | The sidecar returned no usable content or required fields. | Preserve prior accepted versions; write no replacement. |
| `blocked` | Policy, transport, challenge, contract, or normalization failure. | Preserve prior accepted versions; write no replacement. |
| `disabled` | Configuration is off. | No sidecar client or network call is created. |
| `unauthorized` | Configuration is enabled but `--allow-live-web` is absent. | No sidecar client or network call is created. |

If the sidecar is down, first check `/health`, then inspect the CLI reason. Do
not loosen the domain allowlist, enable research/answer synthesis tools, or
replace a blocked result with copied HTML. Retry after the sidecar or adapter
is corrected. Existing TMI and Flight/Airspace publications remain queryable
because web collection is an isolated domain.

## What is deliberately not included

- no vendored Wigolo code or mandatory Wigolo dependency;
- no unrestricted browser or general web-search agent;
- no automatic ontology expansion from a page;
- no conversion of web prose into a declared ATCSCC reason;
- no causal or recommendation claims from web context;
- no scheduler, crawler, or background daemon in the core project;
- no web-only facts in RDF/Neo4j without an accepted SQLite evidence binding.

For the active architecture and command surface, see
[`README.md`](../README.md),
[`REPRODUCIBILITY.md`](../REPRODUCIBILITY.md), and the
[normative design](multi_agent_kg_system_design.md).
