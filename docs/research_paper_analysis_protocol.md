# Research Paper Analysis Protocol

This protocol defines the default way to use external papers in this project.
It prevents thesis planning from relying only on abstracts or high-level paper
summaries. A paper can influence the experiment design only after it has a
curated stage report grounded in full-text, figures, methods, metrics, and
limitations.

## Scope

Use this protocol for papers that may affect:

- thesis positioning;
- NASA ATMONTO / ATCSCC experiment design;
- ontology engineering methodology;
- KG extraction or validation methods;
- GraphRAG retrieval / answer-generation evaluation;
- report figures, tables, or thesis chapter structure.

Do not use this protocol for a quick citation lookup where the paper will not
shape the project design.

## Default Workflow

### Step 1: Register The Paper

Record the citation and local status in `data/papers/README.md`.

Downloaded PDFs stay local and ignored by Git. Curated analysis belongs in
`reports/stages/`.

Minimum record:

- title;
- authors;
- venue / year;
- DOI or stable URL;
- local ignored PDF filename when available;
- intended role in the project.

### Step 2: Prepare A PDF Evidence Pack

Run:

```bash
scripts/inspect_paper_pdf.sh <paper.pdf> [slug]
```

This writes ignored artifacts under `tmp/pdfs/<slug>/`:

- `metadata.txt`;
- `extracted.txt`;
- `figure_table_metric_mentions.txt`;
- `image_inventory.txt`;
- rendered page images;
- extracted embedded images when available.

The rendered pages and embedded images must be inspected for papers where
figures, tables, diagrams, or visual experiment design matter.

### Step 3: Refresh The Figure Gallery

After creating or updating any PDF evidence pack, run:

```bash
uv run python scripts/build_paper_figure_gallery.py
```

This refreshes:

- `reports/stages/paper_figure_gallery.html`;
- `reports/stages/paper_figure_gallery_manifest.json`.

Use the gallery as the default visual comparison surface for figure/table
design across papers. The default view shows only figure/table candidates and
hides full page renders, tiny PDF icons, masks, and other extraction artifacts.
The `All raw` view remains available for debugging extraction quality. The
gallery indexes ignored local assets from `tmp/pdfs/`, so it is reproducible
from the PDF evidence packs rather than a replacement for them.

### Optional Step 3b: Run MinerU For Difficult Figure/Table Extraction

Use MinerU only when Poppler/`pdfimages` extraction produces unusable assets
such as masks, color blocks, tiny icons, or page-level renderings without
separate figure/table candidates.

Keep MinerU isolated because it has a large dependency and model footprint:

```bash
/Users/jlw/.local/bin/uv venv --python 3.12 tmp/mineru_smoke/.venv
/Users/jlw/.local/bin/uv pip install --python tmp/mineru_smoke/.venv/bin/python -U "mineru[all]"
tmp/mineru_smoke/.venv/bin/mineru-models-download -s huggingface -m pipeline
tmp/mineru_smoke/.venv/bin/mineru -p <paper.pdf> -o tmp/mineru_smoke/<slug> -b pipeline -m txt -l en
```

Then import MinerU's table/image assets into the ignored PDF evidence pack and
refresh the gallery:

```bash
/Users/jlw/.local/bin/uv run python scripts/import_mineru_gallery_assets.py \
  tmp/mineru_smoke/<slug>/<paper_name>/txt/<paper_name>_content_list.json \
  <slug>
/Users/jlw/.local/bin/uv run python scripts/build_paper_figure_gallery.py
```

MinerU-imported assets appear as `mineru_extract` cards in the gallery. Treat
them as visual evidence for method analysis, not as a substitute for reading
the paper text and captions.

### Step 4: Produce A Stage Report

Create a curated report under `reports/stages/` using
`templates/research_paper_analysis_report.md`.

The report should cover:

1. material passport;
2. thesis relevance;
3. method pipeline;
4. figure and table inventory;
5. metrics and evaluation design;
6. transferable ideas;
7. weaknesses not to copy;
8. adaptation plan for this project;
9. claim-safety boundaries;
10. follow-up actions.

The report must distinguish:

- what the paper actually shows;
- what is inferred by us;
- what is only a possible adaptation;
- what should not be used as evidence for aviation claims.

### Step 5: Decide The Paper's Project Role

Assign one or more roles:

- `primary_method_reference`: can shape method design;
- `evaluation_reference`: can shape metric/report design;
- `figure_design_reference`: can shape thesis visuals;
- `background_citation`: useful related work only;
- `negative_reference`: useful mainly as a limitation or anti-pattern;
- `deferred`: interesting, but not used in the current experiment.

Only `primary_method_reference`, `evaluation_reference`, and
`figure_design_reference` papers should change experiment plans.

### Step 6: Link To Experiment Artifacts

If the paper changes project direction, update the relevant protocol or report:

- `docs/experiment_workflow.md`;
- `docs/experiment_protocol.md`;
- `docs/nasa_atmonto_experiment_design.md`;
- a focused `reports/stages/*_paper_adaptation.md` or
  `reports/stages/*_figures_analysis.md` file.

Do not silently move a paper idea into the thesis claim. The link from paper to
experiment change must be visible in a stage report or protocol note.

## Analysis Rubric

### Method Transfer

Ask:

- What are the paper's source data, ontology/schema, extraction method, KG
  construction method, retrieval method, and generation method?
- Which parts are implemented versus only described?
- Which parts require human annotation, expert review, or manual correction?
- What are the hidden assumptions?

### Figure/Table Transfer

Ask:

- What function does each figure/table serve?
- Is it a workflow, schema, taxonomy, example graph, metric chart, or failure
  analysis?
- Is the figure readable and reproducible?
- Does it expose sample size, metric definition, statistical uncertainty, and
  failure cases?
- What would the equivalent aviation/ATCSCC figure need to add?

### Evaluation Transfer

Ask:

- What is the actual unit of evaluation: answer text, triple, record, relation,
  path, citation, or question?
- Are metrics aligned with the paper's claims?
- Are text-similarity metrics being used as a proxy for factual correctness?
- Are confidence intervals, statistical tests, or per-item failures visible?
- Can the same metric be computed on our frozen source/gold artifacts?

### Claim-Safety Transfer

Ask:

- Does the paper's domain evidence transfer to aviation, or only its method?
- Does the paper treat ontology/schema validity as semantic truth?
- Does it evaluate KG construction separately from RAG answer quality?
- Would borrowing this claim overstate our current evidence?

## Default Output Names

Use stable, descriptive stage report names:

```text
reports/stages/<paper_slug>_paper_analysis.md
reports/stages/<paper_slug>_figures_analysis.md
reports/stages/<paper_slug>_paper_adaptation.md
```

Use one combined report for small papers and separate reports for papers that
strongly affect the thesis design.

## Quality Gate

A paper analysis is considered project-usable only when all of the following are
true:

- full text or equivalent reliable source was inspected;
- figures/tables were visually checked when relevant;
- methods and metrics are summarized with the correct unit of analysis;
- transferable ideas are separated from non-transferable claims;
- adaptation steps are mapped to local artifacts or marked as future work;
- limitations and threats to validity are recorded.

If these conditions are not met, the paper remains a background citation.

## Current Example

The current reference example is:

- `reports/stages/claim_kg_graphrag_paper_adaptation.md`
- `reports/stages/claim_kg_graphrag_figures_analysis.md`

That analysis treats the source paper as a cross-domain method and figure-design
reference, not as aviation evidence.
