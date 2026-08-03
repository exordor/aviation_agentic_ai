# FAA JO 7210.3EE Adapter For The Document-to-KG Framework

The FAA JO 7210.3EE PDF is treated as a normative order/reference source.
It is not an historical ATCSCC event log and must not be used to claim that a
particular GDP, reroute, or weather condition occurred.

The complete chapter/appendix boundary is maintained in the
[JO 7210.3EE chapter coverage matrix](faa_jo_7210_3ee_chapter_coverage.md).
That matrix records all 21 chapters and six appendices, while this document
describes the currently executable focused path.

## Offline ingestion pipeline

The document follows the standard RAG ingestion path:

```text
PDF
  -> page/paragraph chunking
  -> embedding during `agent-system reindex`
  -> persistent vector collections (Chroma)
```

The ingestion step also records an immutable source version and exact page /
paragraph anchors in the SQLite evidence store. The configured adapter covers
all 26 Chapter 18 sections and 159 numbered paragraphs. The paragraph spans
are recursively bounded into extraction chunks; the PDF is not copied into an
LLM prompt as one large document.

The same chunks are available to SQLite FTS5 for lexical lookup.  Chroma is a
rebuildable embedding index, while the source version and anchors remain the
authoritative evidence records.

## Online inference pipeline

Every valid natural-language question uses the existing bounded Query Agent:

```text
user question
  -> vector/lexical retrieval (top-k candidate chunks)
  -> ontology and source-scope filtering
  -> augmented prompt with quoted evidence and anchors
  -> LLM generation
  -> statement/evidence validation
  -> answer or insufficient evidence
```

Questions about constructed document knowledge are routed to the `knowledge`
capability family. The Agent uses `find_knowledge_roots` to discover matching
published paragraph, rule, or requirement roots and then
`read_knowledge_graph` to retrieve their formal ATMONTO-aligned facts. The
observation carries the same publication,
fact, source-version, and anchor handles used by the other read tools. When a
question also requests exact manual wording, the Agent may select `source`
alongside `knowledge` and follow source discovery with `read_source`.

Retrieval returns candidates. A statement about the FAA Order is accepted only when the
answer cites the exact source version and paragraph anchor returned by the
read-side tools.  The model cannot turn a policy requirement into an observed
event, a causal explanation, or a current operational recommendation.

## Ontology-constrained KG branch

The PDF chunks also form closed tasks for the ontology-constrained KG builder:

```text
anchored paragraph card
  -> four closed task-specific ontology slices
       A: PolicyParagraph -> hasRule -> PolicyRule
       B: PolicyRule -> appliesToTMI / targetsFacility / referencesRouteSegment / requires
       C: PolicyRule -> assignsResponsibilityTo / requiresCoordinationWith
       D: ProcedureRequirement -> requirementText / actionLevel
  -> LLM candidate facts / abstentions / profile gaps per task
  -> deterministic domain/range/datatype checks
  -> deterministic evidence-anchor checks
  -> proposal fusion for the shared PolicyRule root
  -> Formal Publication Kernel
  -> published paragraph, rule, and requirement knowledge roots
```

Each task receives only the class, properties, candidate entities, and evidence
needed for its stage.  The scope and responsibility proposals refer to the
same runtime-owned `PolicyRule` IRI and are fused before publication; they do
not create duplicate rule nodes.  The LLM is a candidate-fact generator only.
It cannot create ontology terms, source identifiers, evidence anchors, or
storage writes. The FAA adapter records rules, procedures, roles, and their links
to ATMONTO TMI/facility concepts; it does not assert that those procedures were
followed in a particular event.

The public construction interface is domain-neutral:

```text
aviation-ai agent-system build-kg \
  --domain document \
  --allow-live-model
```

`document` selects the framework's configured document adapter. The current
configuration binds that adapter to FAA JO 7210.3EE; future document sources
use the same command and publication contract. Without explicit live
authorization the command stops before any provider call and never substitutes
a scripted model.

## Reproduction

With the configured PDF present, run the offline stages in order:

```text
aviation-ai agent-system ingest --domain document
aviation-ai agent-system reindex
aviation-ai agent-system ask --question "What does JO 7210.3EE say about GDP implementation?"
```

The first command registers the PDF and paragraph chunks.  The second creates
the embedding index.  The third performs retrieval, augmentation, and LLM
generation through the normal read-only query path.

The official source is [FAA JO 7210.3EE Basic](https://www.faa.gov/documentLibrary/media/Order/7210.3EE_Basic_dtd_2-20-25.pdf).
