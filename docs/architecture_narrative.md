# Architecture Narrative

## Flagship Positioning

**ATMONTO-Grounded Agentic HybridRAG for Heterogeneous Aviation Knowledge
Integration**

Aviation Agentic AI combines deterministic multi-source ingestion,
ATMONTO-grounded semantic publication, and model-directed HybridRAG retrieval.
It turns heterogeneous aviation records into natural-language answers whose
statements remain traceable to exact source versions and evidence anchors.

## The Research Story

### 1. Problem

Operational aviation knowledge is distributed across sources with different
formats, identifiers, temporal granularity, and authority roles. An ATCSCC
record describes a published Traffic Management Initiative (TMI), NASR and FAA
terminology establish reference identity, METAR and TAF provide time-bounded
Weather reports, and BTS publishes operational observations. No source alone
answers a question that spans the event, its source-declared reason, its
surrounding context, and the available observations.

### 2. Method

The architecture has five planes:

1. **Evidence Plane** — ATCSCC, FAA authority, Weather, and BTS source records.
2. **Deterministic Ingestion Orchestration** — source parsing, versioning,
   normalization, identity resolution, temporal alignment, and evidence
   preparation.
3. **Semantic and Trust Plane** — ATMONTO application profiles, selective
   semantic resolution when ambiguity remains, and the Formal Publication
   Kernel.
4. **Knowledge and Retrieval Plane** — authoritative SQLite knowledge with
   rebuildable graph, lexical, and vector views.
5. **Agent Interaction Plane** — a natural-language Query Agent that selects
   read-only HybridRAG tools, inspects observations, and forms a supported
   answer.

ATMONTO supplies the admitted TBox and publication vocabulary. ATMGRAPH
supplies ABox-construction and cross-source-query principles. Neither is used
as an excuse to collapse distinct evidence roles into one undifferentiated
record.

### 3. What Makes The System Agentic

Agentic behavior belongs to model-directed choice, not to every processing
box. For every valid natural-language query, the LLM Query Agent can select and
sequence exact-store, graph, Weather/BTS, lexical, vector, and exact-source
tools over multiple bounded turns. Search retrieves candidates; an exact
source read supplies final source-record support.

The Semantic Resolution Agent is activated only when deterministic authority
services leave more than one plausible candidate. The ingestion coordinator,
parsers, adapters, indexes, validators, and writers are deterministic services,
not decorative Agents.

### 4. Current Vertical Slice

GDP, Ground Stop, and ReRoute are the implemented TMI families used to
demonstrate the complete architecture. They are not the permanent subject
boundary of the framework. New aviation families should reuse the same source,
semantic-publication, retrieval, and evidence-support contracts rather than
introducing event-specific runtime routes.

## Running Example: Advisory 138

The common walkthrough question is:

> What did ATCSCC publish for JFK in Advisory 138? Verify the
> source-declared reason from the original record, then summarize the
> time-aligned Weather reports and BTS public observations without inferring
> causality.

The supported evidence layers are:

| Evidence role | Supported content |
| --- | --- |
| ATCSCC publication record | GDP for KJFK, retained program period, and the explicitly declared `WEATHER / THUNDERSTORMS` impacting condition. |
| FAA authority | Canonical KJFK facility identity. |
| Weather context | One TAF and five METAR reports retained as time-aligned, non-causal context. |
| BTS public observations | During the event-aligned active window: 77 scheduled, 68 completed, 4 cancelled, and 5 diverted. |

The example demonstrates source-role separation. It does not establish that
Weather caused the GDP, that the GDP caused the BTS observations, that BTS
values are FAA demand or capacity, or that a similar future situation should
receive the same TMI.

## Three-Figure Story

1. **Motivated example** — why one aviation question requires multiple sources
   with different evidence roles.
2. **System architecture** — how the five planes form one extensible HybridRAG
   system.
3. **Query Agent workflow** — how action, observation, candidate verification,
   evidence assembly, and statement-level validation produce an answer.

Together the figures tell one story: heterogeneous evidence is normalized and
published under a shared semantic contract, then an LLM Agent dynamically
retrieves the evidence needed for a user question while deterministic support
validation protects the boundary between source fact, context, observation,
and unsupported inference.
