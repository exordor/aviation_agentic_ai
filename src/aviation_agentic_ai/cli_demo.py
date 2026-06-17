"""End-to-end ATCSCC advisory demonstration command.

Threads a single FAA ATCSCC advisory through the full thesis pipeline using
precomputed artifacts, so the demo runs offline (no LLM/API keys required):

    advisory text
      -> S0 rule-only deterministic backbone
      -> S4 hybrid graph facts (with evidence spans)
      -> KG-RAG vs vector-only retrieval + answer (with citations)

This is the live, reproducible counterpart of the thesis method figure. It
reads only from tracked artifacts under
``data/experiments/nasa_atmonto/formal/`` and the S7 answer-generation report.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from aviation_agentic_ai.paths import PROJECT_ROOT

# Default demo source: ATCSCC oceanic-route-closure advisory ADVZY 032. It has a
# full S0/S4 artifact chain and both KG-RAG and vector-only retrieval arms in
# the S7 answer-generation report, so the whole pipeline is observable.
DEFAULT_DEMO_SOURCE_ID = "2026-05-19:032"
FORMAL_DIR = PROJECT_ROOT / "data" / "experiments" / "nasa_atmonto" / "formal"
S7_ANSWER_REPORT = PROJECT_ROOT / "reports" / "stages" / "nasa_atmonto_s7_answer_generation.json"


def _read_jsonl_first(path: Path, source_id: str) -> dict | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("source_id") == source_id:
                return record
    return None


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _truncate(text: str, limit: int) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit].rstrip() + " ..."


@click.command(name="demo")
@click.option(
    "--source-id",
    default=DEFAULT_DEMO_SOURCE_ID,
    show_default=True,
    help="ATCSCC advisory source_id to trace through the pipeline.",
)
@click.option(
    "--kg-mode",
    default="routed_token_matched_live_tfidf_graphrag",
    show_default=True,
    help="KG-RAG retrieval mode to display.",
)
@click.option(
    "--vector-mode",
    default="token_matched_live_tfidf_vector",
    show_default=True,
    help="Vector-only retrieval mode to display as the matched baseline.",
)
def demo(source_id: str, kg_mode: str, vector_mode: str) -> None:
    """Trace one ATCSCC advisory through extraction -> KG -> KG-RAG answer.

    Runs entirely on precomputed artifacts; no LLM or API key is required, so
    it is safe for live presentation.
    """
    click.echo("=" * 78)
    click.echo(f"ATCSCC advisory end-to-end demo  |  source_id: {source_id}")
    click.echo("=" * 78)

    # Stage 1: advisory source text.
    input_record = _read_jsonl_first(FORMAL_DIR / "input_records.jsonl", source_id)
    if input_record is None:
        raise click.ClickException(
            f"No input record for source_id={source_id!r} in "
            f"{FORMAL_DIR / 'input_records.jsonl'}."
        )
    click.echo("\n[1] Advisory source text (FAA ATCSCC retrospective notice)")
    click.echo(f"    sample_id : {input_record.get('sample_id')}")
    click.echo(f"    class     : {input_record.get('candidate_subject_class')}")
    click.echo(f"    url       : {input_record.get('source_url')}")
    click.echo(f"    text      : {_truncate(input_record.get('source_text_excerpt', ''), 200)}")

    # Stage 2: S0 deterministic backbone (rule-only).
    s0 = _read_jsonl_first(FORMAL_DIR / "s0_rule_only_predictions.jsonl", source_id)
    click.echo("\n[2] S0 rule-only deterministic backbone")
    if s0 is None:
        click.echo("    (no S0 artifact)")
    else:
        facts = s0.get("facts", []) or []
        click.echo(
            f"    {len(facts)} deterministic facts | schema_valid={s0.get('schema_valid')} "
            f"| accepted={s0.get('accepted_fact_count')}"
        )
        _print_fact_samples(facts, limit=3, label="deterministic")

    # Stage 3: S4 hybrid graph facts (the materialized event graph).
    s4 = _read_jsonl_first(FORMAL_DIR / "s4_hybrid_backbone_enrichment_predictions.jsonl", source_id)
    click.echo("\n[3] S4 hybrid enrichment -> advisory event graph (evidence-linked facts)")
    if s4 is None:
        click.echo("    (no S4 artifact)")
    else:
        facts = s4.get("facts", []) or []
        quarantine = s4.get("quarantine") or {}
        click.echo(
            f"    {len(facts)} graph facts | schema_valid={s4.get('schema_valid')} "
            f"| backbone={s4.get('backbone_fact_count')} | quarantine={len(quarantine)}"
        )
        _print_fact_samples(facts, limit=5, label="graph")

    # Stage 4: KG-RAG vs vector-only retrieval + answer (with citations).
    if not S7_ANSWER_REPORT.exists():
        raise click.ClickException(
            f"S7 answer-generation report not found at {S7_ANSWER_REPORT}. "
            "Run scripts/build_nasa_atmonto_s7_answer_generation.py first."
        )
    s7 = _read_json(S7_ANSWER_REPORT)
    records = [r for r in s7.get("records", []) if r.get("source_id") == source_id]
    if not records:
        raise click.ClickException(
            f"No S7 retrieval record for source_id={source_id!r}."
        )
    click.echo("\n[4] KG-RAG vs vector-only retrieval and grounded answer")
    click.echo(f"    {len(records)} competency question(s) answered for this advisory.")
    for record in records[:3]:
        click.echo(f"\n    Q [{record.get('template_id')}]: {record.get('question')}")
        click.echo(f"      expected answer-set: {record.get('answer_set')}")
        _print_answer_arm(record, kg_mode, "KG-RAG")
        _print_answer_arm(record, vector_mode, "Vector-only")

    click.echo("\n" + "=" * 78)
    click.echo("Pipeline: advisory -> S0 backbone -> S4 event graph -> KG-RAG answer.")
    click.echo("Boundary: retrospective, source-bounded diagnostics; not operational ATC support.")
    click.echo("=" * 78)


def _print_fact_samples(facts: list, *, limit: int, label: str) -> None:
    shown = 0
    for fact in facts:
        if shown >= limit:
            break
        if not isinstance(fact, dict):
            continue
        predicate = fact.get("predicate") or fact.get("fact_id")
        value = fact.get("value")
        evidence = fact.get("evidence_text") or ""
        method = fact.get("extraction_method") or fact.get("hybrid_role") or ""
        click.echo(f"    - [{label}] {predicate} = {_truncate(str(value), 40)}")
        if evidence:
            click.echo(f"        evidence: {_truncate(evidence, 90)}")
        if method:
            click.echo(f"        method  : {method}")
        shown += 1
    remaining = len(facts) - limit
    if remaining > 0:
        click.echo(f"    ... (+{remaining} more {label} facts)")


def _print_answer_arm(record: dict, mode: str, arm_label: str) -> None:
    result = record.get("results", {}).get(mode)
    if not result:
        click.echo(f"      {arm_label:12s} ({mode}): (mode not present)")
        return
    answer = result.get("answer") or ""
    chunks = result.get("fused_chunks", []) or []
    triples = result.get("graph_triples", []) or []
    route = result.get("evidence_route") or ""
    click.echo(
        f"      {arm_label:12s} ({mode}): "
        f"{len(chunks)} chunks | {len(triples)} graph triples | route={route}"
    )
    click.echo(f"        answer  : {_truncate(answer, 160)}")
    if triples:
        sample_triple = triples[0]
        if isinstance(sample_triple, dict):
            click.echo(
                "        triple  : "
                f"{sample_triple.get('predicate')} = {sample_triple.get('object')}"
            )
