from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.evaluation.cost_latency import cost_latency_block
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import write_json_report
from aviation_agentic_ai.reporting.nasa_atmonto_answer_benchmark import (
    build_answer_eval_benchmark,
    load_query_manifest,
    query_templates,
    read_jsonl_objects,
    resolve_path,
)
from aviation_agentic_ai.reporting.nasa_atmonto_answer_scoring import (
    ANSWER_MODES,
    aggregate_mode,
    build_generation_records,
    facts_by_source,
    gate_s4_facts,
    graph_use_gate_summary,
)
from aviation_agentic_ai.reporting.nasa_atmonto_cq_queries import DEFAULT_GOLD_PATH

DEFAULT_S4_PREDICTION_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s4_hybrid_backbone_enrichment_predictions.jsonl"
)
DEFAULT_QUERY_MANIFEST_PATH = Path("data/evaluation/nasa_atmonto/atcscc_cq_query_templates.json")
DEFAULT_BENCHMARK_PATH = Path("data/evaluation/nasa_atmonto/atcscc_answer_eval_benchmark.json")
# Keep this scoped to the answer-generation section. The comprehensive S7
# experiment chapter draft is assembled by later reports and should not be
# overwritten by this narrower command.
DEFAULT_CHAPTER_PATH = Path("reports/stages/nasa_atmonto_answer_generation_chapter_section.md")


def build_nasa_atmonto_answer_generation(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    s4_prediction_path: str | Path = DEFAULT_S4_PREDICTION_PATH,
    query_manifest_path: str | Path | None = DEFAULT_QUERY_MANIFEST_PATH,
    max_cases_per_template: int = 3,
) -> dict[str, Any]:
    root = Path(repo_root)
    gold_file = resolve_path(root, gold_path)
    s4_file = resolve_path(root, s4_prediction_path)
    query_manifest = load_query_manifest(root, query_manifest_path, DEFAULT_QUERY_MANIFEST_PATH)
    gold_records = read_jsonl_objects(gold_file)
    s4_records = read_jsonl_objects(s4_file)
    benchmark = build_answer_eval_benchmark(
        gold_records=gold_records,
        query_manifest=query_manifest,
        max_cases_per_template=max_cases_per_template,
    )
    gated_facts_by_source, critic_gate = gate_s4_facts(facts_by_source(s4_records))
    records, scored_by_mode = build_generation_records(benchmark, gated_facts_by_source)
    aggregate_by_mode = {mode: aggregate_mode(items) for mode, items in scored_by_mode.items()}
    cost_latency = {
        "provider": "none",
        "model": "deterministic_scaffold",
        **cost_latency_block(
            elapsed_seconds=0.0,
            questions_total=len(benchmark["labels"]),
            cases_total=len(records),
            kg_path=s4_file,
            token_usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        ),
    }
    result: dict[str, Any] = {
        "source_family": "nasa_atmonto_answer_generation",
        "status": "answer_generation_evaluated",
        "metadata": {
            "gold_path": project_relative_path(gold_file, root),
            "s4_prediction_path": project_relative_path(s4_file, root),
            "query_manifest_path": project_relative_path(
                query_manifest_path or DEFAULT_QUERY_MANIFEST_PATH
            ),
            "template_count": len(query_templates(query_manifest)),
            "benchmark_label_count": len(benchmark["labels"]),
            "modes": list(ANSWER_MODES),
            "generation_policy": "deterministic_answer_scaffold_no_live_llm",
            "boundary": "Retrospective ATCSCC advisory GraphRAG answer evaluation only.",
        },
        "benchmark": benchmark,
        "critic_gate": critic_gate,
        "records": records,
        "answer_quality": {
            "aggregate_by_mode": aggregate_by_mode,
            "secondary_metrics": {
                "cost_latency": cost_latency,
                "graph_use_gate": graph_use_gate_summary(records),
            },
            "metric_policy": (
                "Answer correctness, evidence faithfulness, unsupported claim rate, "
                "citation precision/recall, and abstention correctness are reported separately."
            ),
        },
    }
    result["experiment_chapter_draft"] = experiment_chapter_draft(result)
    return result


def experiment_chapter_draft(result: dict[str, Any]) -> dict[str, Any]:
    hybrid = result["answer_quality"]["aggregate_by_mode"].get("hybrid_graphrag", {})
    return {
        "title": (
            "Schema-constrained Agentic KG-RAG for evidence-grounded FAA ATCSCC "
            "advisory question answering"
        ),
        "claim_boundary": (
            "The experiment is retrospective and source-bounded. NASA ATMONTO-derived "
            "terms are used as a lightweight application schema, not as a complete "
            "aviation ontology or ground truth. The thesis evaluates schema-constrained "
            "event extraction, agentic validation/refinement, KG-RAG grounding, and "
            "failure/human-review boundaries as separate layers; it does not make live "
            "operational ATC decision-support claims."
        ),
        "research_questions": [
            (
                "RQ1: Can schema-constrained LLM extraction produce valid and "
                "evidence-linked event records from ATCSCC advisories?"
            ),
            (
                "RQ2: Does an agentic validation-refinement loop reduce schema "
                "violations and unsupported relations?"
            ),
            (
                "RQ3: Does KG-RAG improve evidence grounding and citation quality "
                "compared with vector-only RAG?"
            ),
            (
                "RQ4: What failure types remain, and where does human review remain "
                "necessary?"
            ),
        ],
        "schema_role": (
            "The ATCSCC profile is an application schema for bounded advisory-event "
            "extraction. It constrains accepted fields, relation names, evidence spans, "
            "and validation checks, but it is not evaluated as a complete aviation "
            "ontology."
        ),
        "experiments": [
            {
                "id": "A",
                "heading": "Experiment A: Schema-constrained advisory event extraction",
                "summary": (
                    "Compare rule-only, schema-slice LLM, validator-repair, and hybrid S4 "
                    "outputs against reviewed ATCSCC advisory facts, keeping structural "
                    "schema validity, evidence support, and semantic scores separate."
                ),
            },
            {
                "id": "B",
                "heading": "Experiment B: Agentic validation and CQ queryability",
                "summary": (
                    "Use validator/refiner/critic artifacts plus CQ query templates to "
                    "measure whether graph outputs recover source-bounded answer sets "
                    "with evidence and fewer unsupported relations."
                ),
            },
            {
                "id": "C",
                "heading": "Experiment C: KG-RAG grounding and answer generation",
                "summary": (
                    "Generate deterministic source-only, vector proxy, graph-only, and "
                    "hybrid GraphRAG answers over the answer-eval benchmark with a critic "
                    "gate before S4 evidence enters graph/hybrid answers. Report citation, "
                    "faithfulness, unsupported-claim, and abstention metrics separately."
                ),
                "hybrid_answer_correctness": hybrid.get("answer_correctness"),
                "hybrid_evidence_faithfulness": hybrid.get("evidence_faithfulness"),
            },
            {
                "id": "D",
                "heading": "Experiment D: Failure analysis and human-review boundary",
                "summary": (
                    "Classify remaining extraction, retrieval, profile/gold-boundary, "
                    "and answer-overreach failures, and keep automated diagnostics "
                    "separate from human or expert review."
                ),
            },
        ],
    }


def write_nasa_atmonto_answer_generation_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO GraphRAG Answer Generation",
        "",
        "## Scope",
        "",
        f"- Status: `{result['status']}`",
        f"- Benchmark labels: {result['metadata']['benchmark_label_count']}",
        f"- Modes: {', '.join(f'`{mode}`' for mode in result['metadata']['modes'])}",
        f"- Boundary: {result['metadata']['boundary']}",
        f"- Critic gate rejected facts: {result['critic_gate']['rejected_fact_count']}",
        "",
        "## Aggregate Answer Quality",
        "",
        (
            "| Mode | Answers | Correctness | Citation P | Citation R | Evidence faithful | "
            "Unsupported claim rate | Abstention correct | Avg context tokens | Avg target tokens |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode, metrics in result["answer_quality"]["aggregate_by_mode"].items():
        target_context = metrics["avg_target_context_tokens"]
        lines.append(
            f"| `{mode}` | {metrics['answers_total']} | {metrics['answer_correctness']} | "
            f"{metrics['citation_precision']} | {metrics['citation_recall']} | "
            f"{metrics['evidence_faithfulness']} | {metrics['unsupported_claim_rate']} | "
            f"{metrics['abstention_correctness']} | {metrics['avg_estimated_context_tokens']} | "
            f"{target_context if target_context is not None else 'n/a'} |"
        )
    gate = result["answer_quality"]["secondary_metrics"]["graph_use_gate"]
    lines.extend(
        [
            "",
            "## S7 Graph-Use Gate",
            "",
            f"- Status: `{gate['status']}`",
            f"- Policy: {gate['policy']}",
            f"- Decision counts: {gate['decision_counts']}",
            f"- Boundary: {gate['boundary']}",
            "",
            "## Critic Gate",
            "",
            f"- Policy: {result['critic_gate']['policy']}",
            f"- Rejected values: {', '.join(result['critic_gate']['rejected_values']) or 'none'}",
            "",
            "## Claim Boundary",
            "",
            result["experiment_chapter_draft"]["claim_boundary"],
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_experiment_chapter_draft_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    draft = result["experiment_chapter_draft"]
    lines = [
        f"# {draft['title']}",
        "",
        "## Claim Boundary",
        "",
        draft["claim_boundary"],
        "",
        "## Research Questions",
        "",
        *[f"- {question}" for question in draft["research_questions"]],
        "",
        "## Schema Role",
        "",
        draft["schema_role"],
        "",
    ]
    for experiment in draft["experiments"]:
        lines.extend(
            [
                f"## {experiment['heading']}",
                "",
                experiment["summary"],
                "",
            ]
        )
        if experiment["id"] == "C":
            lines.extend(
                [
                    f"- Hybrid answer correctness: {experiment['hybrid_answer_correctness']}",
                    f"- Hybrid evidence faithfulness: {experiment['hybrid_evidence_faithfulness']}",
                    "",
                ]
            )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_nasa_atmonto_answer_generation(
    *,
    output_dir: str | Path,
    benchmark_path: str | Path = DEFAULT_BENCHMARK_PATH,
    chapter_path: str | Path = DEFAULT_CHAPTER_PATH,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    s4_prediction_path: str | Path = DEFAULT_S4_PREDICTION_PATH,
    query_manifest_path: str | Path | None = DEFAULT_QUERY_MANIFEST_PATH,
    report_name: str = "nasa_atmonto_answer_generation",
    max_cases_per_template: int = 3,
) -> tuple[Path, Path, Path, Path, dict[str, Any]]:
    root = Path(repo_root)
    result = build_nasa_atmonto_answer_generation(
        repo_root=root,
        gold_path=gold_path,
        s4_prediction_path=s4_prediction_path,
        query_manifest_path=query_manifest_path,
        max_cases_per_template=max_cases_per_template,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "nasa_atmonto_answer_generation"
    json_path = write_json_report(result, output / f"{stem}.json", sort_keys=False)
    md_path = write_nasa_atmonto_answer_generation_markdown(result, output / f"{stem}.md")
    benchmark_json = write_json_report(
        result["benchmark"], resolve_path(root, benchmark_path), sort_keys=False
    )
    chapter_md = write_experiment_chapter_draft_markdown(result, resolve_path(root, chapter_path))
    return json_path, md_path, benchmark_json, chapter_md, result
