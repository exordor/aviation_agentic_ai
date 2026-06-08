# Master Project Scope Confirmation

日期：2026-06-06

用途：给 mentor 快速确认项目方向。目标是让对方能直接回答：
**Yes, this is what I expect** 或 **No, change direction**。

## 1. Working Title

**Agentic KG-RAG for Evidence-Grounded Question Answering over FAA ATCSCC
Advisories**

Alternative conservative title:

**An Agentic RAG Prototype for Schema-Constrained, Evidence-Grounded Analysis
of Aviation Operational Advisories**

## 2. One-Sentence Goal

This project builds a small end-to-end agentic RAG prototype that extracts,
validates, retrieves, and answers evidence-grounded questions over FAA ATCSCC
advisories, using ATMONTO only as a lightweight domain schema / validation
backbone.

## 3. Motivation / Why This Data

ATCSCC advisories are real FAA aviation operational texts. They contain
semi-structured traffic management information such as Ground Stops, Ground
Delay Programs, route advisories, airports, causes, time windows, status, and
source advisory identifiers.

This makes them suitable for an agentic RAG prototype: the agent can parse
operational text, extract structured facts, route questions to Vector / Graph /
Hybrid retrieval, collect evidence, and produce answers with source support.

## 4. Data Scope

- Main corpus: FAA ATCSCC advisories.
- Prototype scale: about 100 manually reviewed advisories.
- Background references: FAA manuals, AIM, FAA orders, NASA ATMONTO material,
  NASR / facility reference data.
- Boundary: background references may support terminology, schema design, or
  entity canonicalization, but they are not the main extraction corpus unless
  the project direction is explicitly changed.

## 5. Ontology Scope

Ontology engineering is **not** the main contribution of this project.

ATMONTO is used only as a lightweight domain backbone / guardrail:

- define useful entity and event types, such as `Airport`, `ARTCC`,
  `TrafficManagementInitiative`, `GroundStopTMI`, `GroundDelayProgramTMI`, and
  `ReRouteTMI`;
- support validation constraints for extracted facts;
- help normalize KG facts for graph-based retrieval;
- keep provenance requirements explicit.

The project may add lightweight advisory-facing extraction relations where
needed, such as `affectsLocation`, `hasCause`, `hasStatus`,
`hasTimeCondition`, `supportedByAdvisory`, and `mentionedInSection`.

The project will not claim to build a full aviation ontology, extend ATMONTO as
a research contribution, or fully populate ATMONTO.

## 6. System Boundary

Advisory ingestion and fact construction:

```text
FAA ATCSCC advisories
  -> section / line parser
  -> extraction agent
  -> schema / provenance validation agent
  -> lightweight KG / fact store
```

Question answering:

```text
User question
  -> query understanding agent
  -> retrieval router
       -> Vector RAG
       -> GraphRAG
       -> Hybrid RAG
  -> evidence collector
  -> answer agent
  -> verifier / citation checker
```

Minimal systems:

- S0 rule-only extraction baseline;
- S1 LLM-only extraction;
- S2 agentic extraction + lightweight schema validation;
- optional S3 validation / repair agent;
- Vector RAG vs GraphRAG vs Hybrid RAG for source-grounded advisory QA.

## 7. Evaluation Plan

Extraction / KG fact evaluation:

- precision, recall, F1;
- JSON validity;
- schema violation rate;
- unsupported fact / hallucination rate;
- provenance coverage.

Agentic RAG evaluation:

- retrieval strategy selected by the router;
- retrieval hit rate;
- answer correctness;
- evidence support / faithfulness;
- answer completeness;
- hallucination rate;
- citation correctness.

Example questions:

- Which advisories mention JFK / ORD / ZNY?
- Which advisories describe weather-related GDPs or Ground Stops?
- What are the affected location, reason, status, and valid time?
- Which source advisories support the answer?
- Does this question require text retrieval, graph retrieval, or hybrid
  retrieval?

## 8. Out Of Scope

This project does not aim to build a complete aviation ontology, perform
ontology engineering as the main contribution, deliver real-time ATC decision
support, predict delays, build a production chatbot, build a passenger-facing
flight assistant, perform large-scale multi-source ATM integration, extract
complete PDF manuals, or invent a new RAG algorithm.

GraphRAG is evaluated as one retrieval strategy inside an agentic assistant, not
assumed to be universally better than Vector RAG.

## 9. Questions For Confirmation

Could you confirm whether this scope is acceptable?

1. Should the main contribution be an Agentic RAG / KG-RAG assistant rather than
   ontology engineering?
2. Should FAA ATCSCC advisories be the main extraction and QA corpus?
3. Should ATMONTO be used only as a lightweight schema / validation backbone
   rather than a fixed extraction schema or ontology-engineering target?
4. Should FAA PDF manuals and orders remain background references, or should
   they become the main data source?
5. Is the RAG comparison expected as a lightweight agentic retrieval-routing
   evaluation rather than a large-scale GraphRAG benchmark?
6. Is the proposed scale, about 100 advisories and 20-30 evaluation questions,
   appropriate for the Master project?

Mentor decision:

- [ ] Scope accepted.
- [ ] Scope accepted with changes.
- [ ] Direction should change.
