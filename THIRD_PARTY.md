# Third-Party Sources And Dependencies

## Runtime Dependencies

The complete runtime dependency declaration is maintained in `pyproject.toml`.
The active system uses LangGraph/LangChain, ChromaDB, Sentence Transformers,
RDFLib, Neo4j, Docling/PyMuPDF, and Scrapy. Generated indexes, local services,
and model artifacts are not tracked.

## External Semantic Authority

The active semantic authority includes six checksum-pinned NASA ATMONTO OWL
modules mirrored from the MIT-licensed
[ICARUS ontology](https://github.com/UCY-LINC-LAB/icarus-ontology). They are
stored in `data/ontology/external/icarus_ontology/NASA/` and are bound by the
curated application profile through recorded checksums. These modules provide
the external TBox reference for the active ATMONTO-aligned profile; they are
not an imported ATMGRAPH dataset or a claim of complete aviation coverage.

## Optional Web Evidence Service

[Wigolo](https://github.com/KnockOutEZ/wigolo) is accessed through a separately
running HTTP sidecar when web-evidence ingestion is explicitly enabled. It is
not vendored and is not required by the core runtime.

## Local Research Sources

Downloaded FAA PDFs, papers, raw source snapshots, local stores, and provider
artifacts are ignored. Their active use is governed by the source-version,
checksum, and anchor metadata recorded by the ingestion pipeline.
