# Figure Descriptions for the ATCSCC Thesis Report

This document specifies the **content** of the five figures required by the
thesis Figure Boundary (`RESEARCH_OVERVIEW.md`). It does not
contain rendered images; each entry is a detailed specification to be used as a
prompt or reference for figure generation (e.g., via ChatGPT, a diagramming
tool, or matplotlib).

Each figure entry has: number, location in the thesis, purpose, content
description, data source (so the figure stays consistent with the paper's
numbers), and style guidance.

---

## Figure 1. System Overview (five-block pipeline)

**Location:** §5 Method (after the method introduction, before §5.1).

**Purpose:** Show the end-to-end flow from raw FAA ATCSCC advisories to
grounded answers and citations, so a reader sees the whole system on one page.

**Content description:**

A left-to-right pipeline of five labeled blocks connected by arrows. Each block
is a rounded rectangle; arrows show data flow.

```
┌────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│ 1. ATCSCC       │───▶│ 2. Application    │───▶│ 3. Extraction +      │
│ advisories      │    │ schema / profile  │    │ agentic loop         │
│ (HTML pages)    │    │ (ATMONTO slice)   │    │ deterministic rule baseline–hybrid backbone condition + validator/   │
│                 │    │                   │    │ refiner/critic       │
└────────────────┘    └──────────────────┘    └──────────┬──────────┘
                                                          │
                                                          ▼
┌────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│ 5. Answers +    │◀───│ 4. KG-RAG         │◀───│ Advisory event graph │
│ citations +     │    │ retrieval +       │    │ (facts with evidence │
│ failure review  │    │ answer generation │    │ spans + source ids)  │
└────────────────┘    └──────────────────┘    └─────────────────────┘
```

- **Block 1:** label "FAA ATCSCC advisories (HTML)", sub-label "867 pages →
  100 reviewed gold sample".
- **Block 2:** label "Application schema/profile", sub-label "ATMONTO slice:
  18 classes, 11 obj props, 11 dt props". A small schema icon.
- **Block 3:** label "Extraction + agentic loop", sub-label "deterministic rule baseline rule / canonicalized schema-free LLM condition
  canon / schema-guided LLM condition slice / validator-and-repair condition repair / hybrid backbone condition hybrid". Inside or beside it, a small
  circular sub-diagram: extractor → validator → refiner → critic with a
  "repair/reject" branch.
- **Block 4:** label "KG-RAG retrieval + answer generation", sub-label
  "vector / graph / hybrid / routed". Show two parallel paths (vector-only vs
  graph-augmented) converging into answer generation.
- **Block 5:** label "Answers + citations + failure review", sub-label
  "correctness, unsupported-claim rate, abstention".

**Data source:** §5 method pipeline text; §3.1 sample counts (867/100);
§4 schema counts (18/11/11).

**Style guidance:** Horizontal flow diagram, 5 rounded-rectangle blocks, one
accent color per block, thin arrows with labels. Avoid clutter — this is the
"map" figure. Keep text minimal; details belong in later figures.

---

## Figure 2. ATCSCC Source-to-Fact Example

**Location:** §3 Data and Task Definition (after §3.2 raw format).

**Purpose:** Make concrete how a raw advisory HTML excerpt becomes structured
event facts with evidence spans — the central task of the thesis.

**Content description:**

Two stacked panels.

**Top panel — raw advisory excerpt (annotated):**
A rendered snippet of one ATCSCC advisory HTML table, with key fields
highlighted in different colors:

```
┌──────────────────────────────────────────────────────────┐
│ ATCSCC ADVZY 007 ... CDM GROUND STOP          [header]   │  ← highlight: TMI type
│ MESSAGE:                                                 │
│   GROUND STOP: ALL ZJX ARRIVALS ...           [message]  │  ← highlight: affected NAS element
│   REASON: WEATHER / THUNDERSTORMS             [cause]    │  ← highlight: cause/condition
│ EFFECTIVE TIME: 2026-05-14 1400Z TO 1700Z     [time]     │  ← highlight: time window
│ SIGNATURE: ATCSCC                                         │
└──────────────────────────────────────────────────────────┘
```

Use 4 highlight colors mapping to 4 fact fields.

**Bottom panel — extracted facts table:**

| Field | Value | Evidence span |
|---|---|---|
| tmi_type | GroundStopTMI | header row |
| affected_nas_element | ZJX arrivals | MESSAGE line 1 |
| cause | weather/thunderstorms | REASON line |
| effective_start | 2026-05-14T14:00Z | EFFECTIVE TIME |
| effective_end | 2026-05-14T17:00Z | EFFECTIVE TIME |

Each row's "evidence span" cell uses the same color as the corresponding
highlight in the top panel, connected by thin guide lines or color matching.

**Data source:** `reports/stages/atcscc_data_format_and_processing_flow.md`
(real advisory example); §3.2 task definition.

**Style guidance:** Two-panel figure, top = annotated source text, bottom =
extracted fact table. Color-coded to show the mapping. This is a "worked
example" figure — clarity over aesthetics.

---

## Figure 3. Schema / Profile Slice (ATMONTO → ATCSCC)

**Location:** §4 Application Schema / Profile.

**Purpose:** Show that the thesis uses a *bounded slice* of ATMONTO, not the
full ontology — visualizing the scope boundary that §4 emphasizes.

**Content description:**

A nested/zoom diagram showing four concentric or cascading layers, each smaller
than the last:

```
┌────────────────────────────────────────────────────────────┐
│ NASA ATMONTO full ontology (OWL)                           │  ← outermost, lightest
│   hundreds of classes, full NAS coverage                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Parsed schema catalog                                 │  │
│  │   (parsed axioms, ranges, domains)                    │  │
│  │  ┌────────────────────────────────────────────────┐   │  │
│  │  │ ATCSCC traffic-management schema slice         │   │  │  ← accent color
│  │  │   18 classes, 11 obj props, 11 dt props        │   │  │
│  │  │  ┌──────────────────────────────────────────┐  │   │  │
│  │  │  │ Extraction JSON schema (runtime contract)│  │   │  │  ← innermost, darkest
│  │  │  │   candidate facts + evidence + source ids│  │   │  │
│  │  │  └──────────────────────────────────────────┘  │   │  │
│  │  └────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

Each layer is labeled with its name and a count/scope note. Arrows or labels
indicate "slice", "profile", "runtime" at each boundary.

**Data source:** §4 schema stack text; counts from §4 table
(18/11/11/33 axioms).

**Style guidance:** Cascading/nested rectangles (zoom-in metaphor), each layer
darker or more saturated than the outer. Emphasize the *narrowing* from full
ATMONTO to the extraction contract. The accent color highlights the ATCSCC
slice (the thesis's actual scope).

---

## Figure 4. Agentic Loop (extractor / validator / refiner / critic)

**Location:** §5.2 Agentic loop.

**Purpose:** Show the role-separated loop with its repair/reject branches,
making clear it is an auditable repair framework, not autonomous ontology
construction.

**Content description:**

A circular/loop diagram with four role nodes and two decision branches:

```
                 candidate facts
                       │
                       ▼
              ┌────────────────┐
              │   Extractor     │
              │  (canonicalized schema-free LLM condition/schema-guided LLM condition/hybrid backbone condition)   │
              └───────┬────────┘
                      │ candidate facts
                      ▼
              ┌────────────────┐
              │   Validator     │◀────────────────┐
              │ (schema +       │                 │
              │  evidence check)│                 │
              └───────┬────────┘                 │
                      │                          │
            ┌─────────┴─────────┐                │
            │                   │                │
       valid? ──no──▶ ┌────────────────┐         │
            │         │    Refiner      │─────────┘
            │         │ (LLM repair)    │  repaired
            │         └────────────────┘
           yes
            │
            ▼
      ┌──────────┐
      │  Critic   │───reject──▶ quarantine / review queue
      │ (final    │
      │  gate)    │
      └────┬─────┘
       accept
           │
           ▼
     event graph (accepted fact + evidence)
```

Annotate the reject branch with "profile/gold-boundary gap" and "unsupported
span" labels (the §7.4 failure categories).

**Data source:** §5.2 agentic loop text; §7.2 repair success numbers
(validator-and-repair condition repair 0.8965; hybrid backbone condition repair 1.0, quarantine 0); §7.4 failure categories
(extraction error, unsupported relation, evidence-span miss,
profile/gold-boundary gap, answer overreach, abstention error).

**Style guidance:** Circular flow with 4 role nodes (different shades),
clear accept/reject branches (green/red), the reject branch leading to a
"quarantine" box. Keep it readable — the loop structure is the message.

---

## Figure 5. Results Summary (layered metrics)

**Location:** §7 Experiments and Results (after §7.1, or as a summary at the
end of §7).

**Purpose:** Visualize the two headline result comparisons that tables alone
communicate poorly: (a) the deterministic rule baseline–hybrid backbone condition extraction F1 spread, and (b) the KG-RAG vs
vector-only answer-quality gap.

**Content description:**

A two-panel figure (side by side or stacked).

**Panel (a) — Extraction F1 across systems (§7.1):**

A vertical bar chart, 6 bars, one per system, F1 on the y-axis (0.0–1.0):

| System | F1 | Bar color note |
|---|---|---|
| deterministic rule baseline rule-only | 0.759 | dark (deterministic, strongest) |
| canonicalized schema-free LLM condition LLM canon | 0.224 | light |
| schema-guided LLM condition schema-slice | 0.195 | light |
| validator-and-repair condition validator-repair | 0.171 | light |
| hybrid backbone condition hybrid | 0.727 | dark (deterministic backbone + enrichment) |
| raw schema-free LLM diagnostic LLM-only | 0.000 | hatch (diagnostic only, scored zero vs target schema) |

Add error bars for the systems with bootstrap 95% CIs:
deterministic rule baseline 0.708–0.804; schema-guided LLM condition 0.144–0.240; hybrid backbone condition 0.681–0.763.

Title: "Schema-constrained extraction F1 (100 reviewed advisories)".

**Panel (b) — KG-RAG vs vector-only head-to-head (§7.3.2):**

A grouped bar chart, 2 groups (KG-RAG, Vector-only), 3 bars each:

| Metric | KG-RAG (routed) | Vector-only (tfidf) |
|---|---|---|
| Answer correctness | 0.967 | 0.500 |
| Citation recall | 0.608 | 0.372 |
| Unsupported claim rate | 0.017 | 0.500 |

(For "unsupported claim rate", lower is better — annotate or invert the visual
cue so a reader doesn't misread a tall bar as good.)

Title: "KG-RAG vs vector-only (same 30 questions, same LLM)".

**Data source:** §7.1 extraction table (P/R/F1); §7.3.2 head-to-head table.

**Style guidance:** Clean bar charts, no chart-junk. Two accent colors
(deterministic vs LLM in panel a; KG-RAG vs vector in panel b). Error bars on
panel (a) for systems with CIs. Annotate the raw schema-free LLM diagnostic=0 bar as "diagnostic baseline".
Label axes and units clearly. These are the figures a reviewer will scrutinize
most — accuracy over aesthetics.
