# Agent System Prompt Engineering

## Objective

Freeze and test the five role prompts used by the aviation event knowledge
system:

1. Advisory Agent;
2. Facility Agent;
3. Terminology Agent;
4. Knowledge Graph Construction Agent;
5. Query Agent.

This is implementation quality assurance for one end-to-end system slice. It
is not a semantic benchmark, a model comparison, or evidence that the complete
718-record corpus is correct.

## Method sources and project adaptations

| Source | Method in the paper | Adopted here | Explicitly not adopted |
| --- | --- | --- | --- |
| Text2Event, Lu et al. (2021), Zotero `TCC4VYND` | Schema-conditioned, reversibly linearized event structure generation | Four-column Graph Patch and compact Schema Guide with meaningful labels | Trie/token-level constrained decoding |
| VerifiNER, Kim et al. (2024), Zotero `HNMU24F4` | Knowledge-grounded candidate comparison and a `NONE` class | Authority-only closed candidates, evidence/context comparison, `abstain` and `profile_gap` | Fallback to model memory and multi-sample voting |
| EA-Agent, Nan et al. (2026), Zotero `DA86A5HB` | Evidence selection, closed candidate alignment, ambiguity-triggered reflection | Compact Evidence Cards and model use only for genuine ambiguity | Learned path planning, policy optimization, and Reflector |
| Self-Refine, Madaan et al. (2023), Zotero `SL8NJBCY` | Task-specific input-output demonstrations and explicit stop conditions | Two fictional contrastive examples per role | Iterative self-feedback and revision |
| CRITIC, Gou et al., Zotero `QSAKG698` | External-tool-grounded feedback is more reliable than unsupported self-critique | FAA/NASA/graph evidence is supplied as delimited data and remains the authority | Open-ended critique/correction loops |

The project adaptation is therefore:

```text
single role objective
-> explicit information boundary
-> closed evidence/schema/candidate space
-> resolved / abstain / profile_gap / blocked stop state
-> short reversible output grammar
-> fictional positive and boundary few-shot examples
```

The examples contain no real advisory ID, real airport code, real operational
term, or `urn:aviation-agentic-ai` identifier.

## Prompt artifacts

- Frozen catalog: `configs/prompts/agent_system_v1.yaml`
- Static contract tests: `tests/test_agent_system_prompt_catalog.py`
- Bounded live QA: `scripts/smoke_agent_system_prompts.py`
- Final prompt set: `multi-agent-aviation-kg-system-prompts-v3`
- Catalog SHA-256:
  `3990d5dfe597eefb332afc98b54c78024dec018d3716182c00ef431d89e6c234`

## Real-model QA

All calls used the same fixed ATCSCC source record
`2026-05-14:002`, requested model `deepseek-v4-pro`, and temperature
`0`. Raw QA artifacts are intentionally stored under `/tmp`, not in the
repository.

| Pass | Calls | Observed result | Action |
| --- | ---: | --- | --- |
| Initial diagnostic | 5 | Advisory omitted the exact source ID; Facility shortened the canonical URI to `KDCA` | Added exact-copy rules and contrastive fictional demonstrations |
| Full v2 confirmation | 5 | Five original automated role checks passed; manual review found a spurious profile gap for an event label already represented by `rdf:type` | Defined the profile-gap boundary and added a deterministic regression assertion |
| KG v3 targeted regression | 1 | Correct four-line Graph Patch and `PROFILE_GAPS / NONE` | Freeze v3 |

Final targeted KG output:

```text
GRAPH_PATCH
urn:aviation-agentic-ai:event:2026-05-14:002 | rdf:type | atm:GroundStopTMI | faa-term:ground-stop
urn:aviation-agentic-ai:event:2026-05-14:002 | atm:controlledNASelement | urn:aviation-agentic-ai:facility:airport:KDCA | 2026-05-14:002, nasr:KDCA
urn:aviation-agentic-ai:event:2026-05-14:002 | atm:effectiveStartTime | "2026-05-14T00:21:00Z" | 2026-05-14:002
urn:aviation-agentic-ai:event:2026-05-14:002 | atm:effectiveEndTime | "2026-05-14T02:30:00Z" | 2026-05-14:002

PROFILE_GAPS
NONE
```

## Acceptance status

- Static prompt-contract tests: `11 passed`.
- Ruff on prompt test and smoke script: passed.
- Whitespace/diff validation: passed.
- Real DeepSeek role calls: 11 total.
- Final modified role regression: passed.
- No best-of-N sampling, majority voting, prompt search, or result selection.
- No provider JSON Schema and no requested or persisted chain-of-thought.

Repository-wide `ruff` passed. Repository-wide `pytest` reached `387 passed`
and one environment failure: the isolated worktree does not contain the ignored
NASR ZIP snapshot required by
`test_real_snapshot_builds_three_airports_and_new_york_artcc`. The snapshot is
present in the original checkout but was not copied into this worktree. This
failure is unrelated to the prompt files and was not hidden with a fabricated
fixture.

The live QA responses reported reasoning tokens because the current generic
DeepSeek adapter used by this standalone QA left provider thinking at its
default. The catalog's intended production setting remains `thinking:
disabled`, `max_retries: 0`. Runtime integration must enforce and record those
settings; this prompt QA does not claim to have validated the runtime adapter.

## Executor boundary

ZCode may load and integrate the frozen prompt catalog, but it must not rewrite
the prompt text or replace the fictional demonstrations. Any proposed prompt
change requires a new prompt-set version, an observed failure, a deterministic
regression check, and Codex review.
