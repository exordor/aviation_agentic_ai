# Pi-Style Hybrid Query Agent Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the exact-question `agent-system ask` experiment with an
always-activated, bounded LLM query Agent that dynamically selects deterministic
Corpus, graph, and vector-retrieval tools for arbitrary natural-language
questions.

**Architecture:** Keep corpus v2 as the authoritative read store and retain the
existing case-scoped graph and Chroma index as rebuildable read views. Adapt the
official [Pi agent-loop](https://github.com/earendil-works/pi/tree/main/packages/agent)
pattern—model action, validated tool execution, observation, and evidence-bound
final response—without adding Pi as a dependency or exposing file, shell,
network, or graph-write tools. The first implementation permits at
most four provider turns and six total read-only tool calls. Each turn may
either request tools or return the final typed answer; tool observations are
appended before the next turn so a query can first resolve a case and then
retrieve its evidence.

**Tech Stack:** Python 3.12, Pydantic v2, LangChain message/tool contracts,
existing `ToolCallingModel`, corpus v2 JSONL store, `CorpusGraphView`, Chroma
case index, Click, pytest, Ruff.

## Implementation Status

Implemented in the isolated `codex/pi-style-hybrid-query-agent` worktree. The
fixed-question runtime was removed, the six bounded HybridRAG tools and
always-on query loop were added, and the v2 live evaluator now scores the
current query role.

Real-provider acceptance used DeepSeek `deepseek-v4-pro`, temperature `0.0`,
thinking disabled, no automatic retries, and no response replay or local model
cache. The 12-cycle experiment recorded 120/120 successful real calls. The
current GDP `138` query passed 12/12 measurements; the unchanged Assembly tasks
failed 48/48 measurements, exposing a separate compatibility gap rather than a
query-regression failure.

## Global Constraints

- Public `agent-system ask` always activates the configured LLM. Missing
  credentials, provider failure, or malformed model output returns `blocked`;
  there is no deterministic answer fallback.
- Natural-language wording is not matched against a registry. English,
  Chinese, paraphrases, and multi-evidence questions share the same Agent
  entry point.
- Tool selection is model-driven; data access and calculations remain
  deterministic.
- All tools are read-only, corpus-bound, schema-validated, and limited to the
  current CLI scope. The Agent cannot write the corpus, RDF, Neo4j, Chroma, or
  source objects.
- Tool results separate compact model-visible `content` from structured
  `details` retained for evidence validation.
- At least one retrieval tool must execute before an answer can be `ok`.
- Each final statement cites only case, fact, profile-gap,
  context-association, observation, graph-edge, similarity-match, and source
  IDs returned during the current query. ID-subset checking is reference
  integrity; statement kinds and claim-boundary validation provide the
  additional semantic support check.
- Weather remains non-causal. BTS remains a source-qualified public
  observation, not FAA demand, capacity, AAR, EDCT, causal proof, or an
  operational recommendation.
- GS 123 remains `profile_gap`, GDP 138 remains formal `weather`, and GDP 020
  remains `missing`.
- Corpus v2, the Formal Publication Kernel, build-corpus, RDF/Turtle and Neo4j
  exports, and case-index representation are not changed by this batch.
- Offline scripted models are allowed only to verify software behavior. They
  must not be reported as model or Agent performance.
- The historical live-evaluation reports remain immutable evidence. Their
  analysis trial is migrated to the new `query` role; old results are not
  rewritten.
- This research-prototype batch does not add a general planner, conversational
  memory, streaming UI, unbounded ReAct loop, PDF tools, flight/sector data, or
  recommendation logic.

---

## Task 1: Define the Hybrid Query contracts and Agent loop

**Files:**

- Create:
  `src/aviation_agentic_ai/agent_system/hybrid_query_agent.py`
- Modify:
  `src/aviation_agentic_ai/agent_system/contracts.py`
- Test:
  `tests/test_agent_system_hybrid_query_agent.py`

### Required interfaces

```python
class HybridQueryScope(StrictModel):
    event_id: str | None
    event_type_iri: str | None
    facility_id: str | None
    reason_status: Literal["formal", "profile_gap", "missing"] | None
    reason_value: str | None
    candidate_scope: Literal["archive", "prior"]
    offset: int
    limit: int


class HybridQueryEvidence(StrictModel):
    case_ids: tuple[str, ...]
    fact_ids: tuple[str, ...]
    profile_gap_ids: tuple[str, ...]
    context_association_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    graph_path_ids: tuple[str, ...]
    source_ids: tuple[str, ...]


class HybridQuerySupportRecord(StrictModel):
    kind: Literal[
        "source_fact",
        "non_causal_context",
        "public_observation",
        "similarity",
    ]
    case_ids: tuple[str, ...]
    fact_ids: tuple[str, ...]
    profile_gap_ids: tuple[str, ...]
    context_association_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    graph_path_ids: tuple[str, ...]
    source_ids: tuple[str, ...]


class HybridQueryToolObservation(StrictModel):
    status: Literal["ok", "insufficient", "blocked"]
    content: str
    details: HybridQueryEvidence
    support_records: tuple[HybridQuerySupportRecord, ...]
    similarity_matches: tuple[CaseSimilarityMatch, ...]
    limitation: str


class HybridQueryStatement(StrictModel):
    kind: Literal[
        "source_fact",
        "non_causal_context",
        "public_observation",
        "similarity",
    ]
    text: str
    support_case_ids: tuple[str, ...]
    support_fact_ids: tuple[str, ...]
    support_profile_gap_ids: tuple[str, ...]
    support_context_association_ids: tuple[str, ...]
    support_observation_ids: tuple[str, ...]
    support_graph_path_ids: tuple[str, ...]
    support_source_ids: tuple[str, ...]


class HybridQueryAnswer(StrictModel):
    status: Literal["ok", "insufficient"]
    statements: tuple[HybridQueryStatement, ...]
    limitations: tuple[str, ...]


def run_hybrid_query_agent(
    *,
    question: str,
    scope: HybridQueryScope,
    tools: list[BaseTool],
    model_factory: Callable[[list[BaseTool]], ToolCallingModel],
) -> QueryToolOutcome:
    ...
```

### TDD steps

- [ ] Add failing tests proving the first provider turn is required for every
  question, including a known English fixture, a paraphrase, and a Chinese
  query.
- [ ] Add a failing no-`event_id` test whose first turn calls `find_cases`,
  whose second turn uses the observed canonical event ID to call Weather and
  BTS tools, and whose third turn answers.
- [ ] Add a failing test for a model-selected batch of two or three tools and
  assert that every matching `ToolMessage` remains in subsequent turns.
- [ ] Add failing tests for zero tool calls, more than three tool calls,
  more than six total tool calls, unknown tools, invalid arguments, provider
  errors, and exceeding four provider turns; all must return `blocked`.
- [ ] Add failing tests that malformed answer JSON, unsupported evidence IDs,
  an `ok` answer with no retrieval, and an `ok` answer when every tool was
  insufficient are rejected.
- [ ] Add failing per-statement tests that non-causal Weather context cannot be
  presented as causation, BTS observations cannot be presented as FAA
  demand/capacity, and similarity cannot be presented as a recommendation.
- [ ] Add a failing test that an honest evidence-backed `insufficient` answer
  is preserved.
- [ ] Add the minimal contracts to `contracts.py`. Remove the obsolete
  `analysis_artifact_dir` field from `QueryToolOutcome`; model and tool ledgers
  remain in the outcome.
- [ ] Implement the loop in `hybrid_query_agent.py`:
  `SystemMessage + HumanMessage -> model action -> ToolMessages -> repeat or
  final_answer`.
- [ ] Enforce at most four provider turns, three calls per turn, six calls
  total, and at least one successful retrieval before `ok`.
- [ ] Parse one compact JSON answer envelope and validate every support ID
  against the current turn's tool observations.
- [ ] Validate each statement kind against typed tool support records, keeping
  each evidence ID bound to its own source IDs rather than validating against
  one global union, and reject
  causal, demand/capacity, effectiveness, or recommendation language outside
  the project's claim boundary.
- [ ] Merge tool details into the existing `QueryToolOutcome` fields without
  treating answer prose as evidence.
- [ ] Run:

  ```bash
  uv run pytest -q tests/test_agent_system_hybrid_query_agent.py
  ```

- [ ] Self-review the loop for accidental model-memory fallback, unbounded
  calls, and evidence IDs copied from the prompt rather than tool observations.

**Suggested commit:** `feat(agent-system): add bounded hybrid query agent loop`

---

## Task 2: Expose Corpus, graph, and Chroma as bounded HybridRAG tools

**Files:**

- Create:
  `src/aviation_agentic_ai/agent_system/hybrid_query_tools.py`
- Modify:
  `src/aviation_agentic_ai/agent_system/corpus_query.py`
- Test:
  `tests/test_agent_system_hybrid_query_tools.py`

### Tool registry

```text
find_cases
  exact catalog filters and bounded paging

read_case_facts
  formal facts, declared-reason state, profile-gap wording, and evidence IDs

read_weather_context
  TAF/METAR associations plus admitted report facts; always non-causal

read_public_observations
  BTS observations by baseline/active/recovery phase

read_case_graph
  bounded case-scoped formal graph edges, with optional entity/predicate filter

find_similar_cases
  exact candidate filters followed by the corpus-bound Chroma index
```

### Required implementation

```python
class HybridQueryGateway:
    def __init__(
        self,
        *,
        store: CorpusQueryStore,
        scope: HybridQueryScope,
    ) -> None:
        ...

    def find_cases(...) -> HybridQueryToolObservation: ...
    def read_case_facts(...) -> HybridQueryToolObservation: ...
    def read_weather_context(...) -> HybridQueryToolObservation: ...
    def read_public_observations(...) -> HybridQueryToolObservation: ...
    def read_case_graph(...) -> HybridQueryToolObservation: ...
    def find_similar_cases(...) -> HybridQueryToolObservation: ...


def build_hybrid_query_tools(
    gateway: HybridQueryGateway,
) -> list[BaseTool]:
    ...
```

### TDD steps

- [ ] Add failing tests for all six tools using a temporary corpus, asserting
  Pydantic argument validation and bounded result sizes.
- [ ] Add failing tests that an explicit CLI `event_id` prevents every
  event-scoped tool from reading another event.
- [ ] Add failing tests that catalog and similarity filters cannot broaden the
  CLI-provided event type, facility, reason, candidate scope, offset, or limit.
- [ ] Add failing tests that `read_case_facts` distinguishes formal reason,
  profile gap with source wording, and genuinely missing reason.
- [ ] Add failing tests that Weather observations are labelled non-causal and
  BTS rows are labelled public observations rather than decision inputs.
- [ ] Add a failing test that graph edges come only from the selected case and
  that optional entity/predicate filters cannot escape it.
- [ ] Add failing tests for a missing case index and a corrupt/mismatched case
  index; return `insufficient` and `blocked`, respectively.
- [ ] Implement strict input models and the corpus-bound gateway.
- [ ] Build LangChain tools over gateway methods. Return compact content to the
  model while retaining structured details for the Agent support checker.
- [ ] Move reusable deterministic selection code out of question-specific
  answer builders in `corpus_query.py`; tools must operate on explicit
  arguments, never on normalized question text.
- [ ] Replace the fixed
  `get_reconstructed_case_evidence_paths()` traversal with a general bounded
  case-graph read surface; no runtime graph helper may encode one old
  competency question.
- [ ] Run:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_hybrid_query_tools.py \
    tests/test_agent_system_case_retrieval_search.py
  ```

- [ ] Self-review source IDs, profile gaps, Weather associations, observations,
  graph paths, and similarity matches for corpus binding.

**Suggested commit:** `feat(agent-system): expose corpus hybrid retrieval tools`

---

## Task 3: Cut public `ask` over to the Agent and delete fixed-question runtime

**Files:**

- Modify:
  `src/aviation_agentic_ai/agent_system/corpus_query.py`
- Modify:
  `src/aviation_agentic_ai/cli_agent_system.py`
- Modify:
  `configs/prompts/decision_case_agents_v1.yaml`
- Modify:
  `src/aviation_agentic_ai/agent_system/prompts.py`
- Modify:
  `src/aviation_agentic_ai/agent_system/decision_case_contracts.py`
- Modify:
  `src/aviation_agentic_ai/agent_system/corpus_graph.py`
- Delete:
  `src/aviation_agentic_ai/agent_system/query_registry.py`
- Delete:
  `src/aviation_agentic_ai/agent_system/query_plan.py`
- Delete:
  `src/aviation_agentic_ai/agent_system/case_analysis.py`
- Delete:
  `src/aviation_agentic_ai/agent_system/case_analysis_tools.py`
- Delete obsolete tests:
  `tests/test_agent_system_query_registry.py`
- Delete obsolete tests:
  `tests/test_agent_system_case_analysis.py`
- Delete obsolete tests:
  `tests/test_agent_system_case_analysis_tools.py`
- Delete obsolete tests:
  `tests/test_agent_system_case_analysis_limits.py`
- Delete obsolete tests:
  `tests/test_agent_system_case_analysis_readers.py`
- Modify:
  `tests/test_agent_system_decision_case_contracts.py`
- Modify:
  `tests/test_agent_system_corpus_store.py`
- Modify:
  `tests/test_agent_system_multisource_context.py`
- Modify:
  `tests/test_cli_agent_system.py`
- Modify:
  `tests/test_agent_system_prompt_catalog.py`

### Public behavior

```text
agent-system ask
  --corpus-dir <corpus>
  --question <free natural-language question>
  [--event-id <scope hint>]
  [existing exact filter, candidate-scope, offset and limit hints]
```

There is no `--allow-live-model` option for `ask`: invoking the command is the
explicit request to use the configured model.

### TDD steps

- [ ] Replace fixed-question tests with failing end-to-end tests in which an
  injected tool-calling model chooses tools for:
  - a formal event-fact question;
  - a Chinese declared-reason question;
  - a paraphrased Weather-context question;
  - a Weather plus BTS multi-tool question;
  - a historical-similarity question;
  - an unsupported causal or recommendation question that returns an explicit
    limitation.
- [ ] Add a failing test proving each public `answer_corpus_question` call
  records at least one provider invocation, including `insufficient` answers.
- [ ] Add a failing CLI test proving `--allow-live-model` is no longer accepted
  by `ask`.
- [ ] Add a failing CLI test proving missing provider credentials return
  `ask BLOCKED` rather than a deterministic answer.
- [ ] Reduce `answer_corpus_question` to:
  1. validate/load `CorpusQueryStore`;
  2. construct `HybridQueryScope`;
  3. construct gateway and tools;
  4. require a model factory;
  5. run `run_hybrid_query_agent`.
- [ ] Change the CLI help from “registered corpus question” to free
  natural-language corpus query, always constructing the `query` model role.
- [ ] Replace the `query` prompt with a short Pi-style policy:
  choose bounded tools over multiple turns, inspect observations, answer in the
  user's language, cite returned IDs per statement, preserve limitations, and
  return the compact answer envelope.
- [ ] Update the catalog language policy and `ROLE_KEYS`; active construction
  outputs remain English, while public Query Agent answers follow the user's
  language.
- [ ] Remove the `decision_case_analysis` prompt role and all exact question
  constants, normalized-question gates, immutable registered plans, fixed
  operation sequences, and fixed answer-format branches.
- [ ] Delete the four obsolete runtime modules and their fixed-path tests.
- [ ] Delete obsolete `CaseAnalysisTask`, plan-bound `QueryEvidenceBundle`,
  fixed-analysis `QueryToolTrace`, and sealing helpers from
  `decision_case_contracts.py`, plus their dedicated contract tests. Keep only
  contracts still used by construction or the new Hybrid Query path.
- [ ] Delete the fixed reconstruction evidence-path helper from
  `corpus_graph.py`; retain and test the general case-scoped graph view.
- [ ] Keep former English questions only as literal competency examples inside
  tests/data; they must not be imported by runtime code.
- [ ] Re-run repository searches and require zero runtime hits for:

  ```text
  classify_registered_question
  QueryIntent
  AnalysisIntent
  compile_query_plan
  execute_bound_query_step
  REGISTERED_*_QUESTION
  decision_case_analysis
  ```

- [ ] Run:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_hybrid_query_agent.py \
    tests/test_agent_system_hybrid_query_tools.py \
    tests/test_agent_system_corpus_store.py \
    tests/test_agent_system_multisource_context.py \
    tests/test_cli_agent_system.py \
    tests/test_agent_system_prompt_catalog.py
  ```

- [ ] Self-review the public path by tracing one arbitrary question from Click
  through model selection, deterministic tools, final synthesis, and support
  validation.

**Suggested commit:** `refactor(agent-system): replace fixed questions with agentic query routing`

---

## Task 4: Migrate live-evaluation plumbing and align project documentation

**Files:**

- Modify:
  `src/aviation_agentic_ai/agent_system/live_agent_evaluation.py`
- Modify:
  `src/aviation_agentic_ai/agent_system/live_agent_experiment.py`
- Modify:
  `data/evaluation/agent_system/live_agent_smoke_v1.yaml`
- Modify:
  `tests/test_agent_system_live_evaluation.py`
- Modify:
  `tests/test_agent_system_live_experiment.py`
- Modify:
  `README.md`
- Modify:
  `GOALS.md`
- Modify:
  `RESEARCH_AUDIT.md`
- Modify:
  `TODO.md`
- Modify:
  `REPRODUCIBILITY.md`
- Modify:
  `docs/multi_agent_kg_system_design.md`
- Modify:
  `AGENTS.md`

### Required changes

- [ ] Add failing live-harness unit tests that classify the query sample as
  role `query`, score actual model/tool calls from the new outcome, and never
  invoke the removed fixed plan.
- [ ] Change the evaluation trial role from `decision_case_analysis` to
  `query`. Preserve the question as a frozen sample, not a runtime registry
  entry.
- [ ] Keep the four Assembly trials unchanged and keep historical report files
  unchanged.
- [ ] Update the repeated real-provider experiment to construct the `query`
  model role and capture both query turns through the existing provider-call
  observer.
- [ ] Replace the removed analysis artifact with an evaluator-owned,
  gitignored `hybrid_query_run.json` containing the parsed answer, query tool
  traces, model-call metadata, corpus ID, and checksums of the associated raw
  and parsed trial records. Public `ask` remains read-only and does not write
  this artifact.
- [ ] Update documentation to describe:
  - always-on LLM routing for public natural-language queries;
  - deterministic Corpus/KG/Chroma tools;
  - at most four provider turns, three calls per turn, and six total tool calls;
  - deterministic evidence support validation;
  - no deterministic answer fallback;
  - offline tests versus live model evaluation;
  - remaining limitations of metadata-conditioned similarity.
- [ ] Remove all claims that `ask` is zero-model, exact-registered,
  deterministic question routing.
- [ ] Keep deterministic zero-call behavior only for build preflight and
  deterministic construction paths where it remains true.
- [ ] Search active code and documentation for stale terminology:

  ```bash
  git grep -nE \
    'exact registered|registered question|Decision Case Analysis|zero-chat-model|zero model calls' \
    -- ':!reports/**'
  ```

- [ ] Run focused tests:

  ```bash
  uv run pytest -q \
    tests/test_agent_system_live_evaluation.py \
    tests/test_agent_system_live_experiment.py \
    tests/test_readme_commands.py
  ```

- [ ] If configured credentials are available, run one clearly labelled
  `live_smoke` query through the new public Agent path and report the actual
  provider result. If credentials are unavailable, report `NOT EXECUTED`;
  never replace it with a fake response.
- [ ] Perform one bounded final review, then run the repository verification
  exactly once:

  ```bash
  uv run ruff check .
  uv run pytest -q
  uv build
  git diff --check
  ```

- [ ] Note separately that the isolated worktree baseline contains one
  environment-dependent test requiring the gitignored NASR snapshot. Either
  make that snapshot available without committing it or report the baseline
  environmental failure unchanged.

All “every query invokes the model” assertions apply after the corpus has
validated and a provider can be constructed. Corpus-integrity or credential
failures are `blocked_before_model`; they are not counted as model
invocations.

**Suggested commit:** `docs(agent-system): document agent-routed hybrid queries`

---

## Acceptance Matrix

| Scenario | Expected result |
| --- | --- |
| Known English question | LLM selects tool; no string registry |
| English paraphrase | Same Agent path; relevant tool selected |
| Chinese question | Same Agent path; answer may be Chinese |
| Event facts plus Weather plus BTS | Two or three tools in one selection turn |
| Similar historical case | Chroma tool selected after exact filtering |
| Missing reason | `insufficient`; Weather/BTS cannot fill it |
| GS 123 reason | Profile-gap wording remains outside formal facts |
| GDP 138 reason | Formal `weather` fact remains available |
| GDP 020 reason | Missing remains missing |
| “Why did Weather cause this?” | Evidence-bound limitation; no causal claim |
| “What should ATCSCC do?” | Limitation; no recommendation |
| Missing credentials | `blocked`; no deterministic answer |
| Invalid model tool request | `blocked`; no tool execution outside scope |
| Unsupported answer citation | `blocked`; answer not published |

## Completion Definition

The batch is complete only when:

1. the detailed plan and implementation agree;
2. public `ask` invokes the model for every question;
3. tools and observations, not fixed phrases, determine the retrieval path;
4. the fixed registry, fixed query-plan compiler, and old Decision Case
   Analysis runtime are absent;
5. existing corpus and publication semantics are unchanged;
6. offline tests are reported only as software evidence;
7. focused checks and one final repository verification have been run; and
8. no merge or push occurs without a separate user request.
