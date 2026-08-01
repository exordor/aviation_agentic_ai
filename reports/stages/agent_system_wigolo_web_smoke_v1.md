# Wigolo Web Evidence Smoke v1

Evaluation mode: `live_smoke` (compatibility and storage-boundary check, not a benchmark).

## Observed run

- Sidecar: Wigolo `0.2.1`, REST at `http://127.0.0.1:3333`, synthesis disabled.
- Initial collection: 3 real fetches, 3 returned `ok`, 0 failures, 3 immutable source versions and one full-record anchor per version.
- Initial SQLite knowledge revision: 3.
- FTS5 query (`Glossary`, `web_document`): 1 match.
- Repeat check: 1 real fetch returned `ok`; `changed_urls=[]`; source-version count remained 3 and knowledge revision remained 3.
- Latency probe: 3 real fetches returned `ok`; 6.38–249.25 ms, mean 150.18 ms, median 194.91 ms.
- Sidecar-stop check: the daemon was stopped and its health endpoint became unreachable; 50 focused TMI/Flight/Airspace/web tests still passed.

The accepted pages were the FAA Pilot/Controller Glossary, the official NASA
aeronautics page, and the FAA Aeronautical Information Manual page. The direct
historical `data.nasa.gov/ontologies/atmonto/` probe returned `http_500`, so it
was recorded as blocked rather than silently treated as a successful ATMONTO
document.

## Artifact integrity

The ignored runtime artifacts are listed in
`agent_system_wigolo_web_smoke_v1.json`:

- raw summary: `data/evaluation_runs/agent_system/wigolo_web_smoke_v1/raw_sidecar_responses.jsonl`
- parsed outputs: `data/evaluation_runs/agent_system/wigolo_web_smoke_v1/parsed_trial_outputs.jsonl`

They contain sanitized status, URL, checksum, source-version, span, and timing
metadata only. Page bodies, headers, tokens, prompts, and reasoning are not
stored. The controlled changed-content check is explicitly labelled an offline
storage fixture; it is not counted as a live sidecar result.

## Boundary conclusion

The web adapter can turn an allowlisted public page into an immutable SQLite
source version and searchable source chunk, while repeated content is
deduplicated and changed content receives a new version. Web pages remain
source evidence: they do not become ATCSCC reasons, causal explanations,
recommendations, or formal graph roots without an independently accepted
SQLite binding.
