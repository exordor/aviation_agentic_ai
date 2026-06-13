from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report
from aviation_agentic_ai.reporting.atmonto.s7.retrieval import (
    aggregate_abstention_correctness,
    aggregate_answer_set_metrics,
)

DEFAULT_S7_RETRIEVAL_REPORT_PATH = Path("reports/stages/nasa_atmonto_s7_retrieval.json")
GRAPH_HEALTH_MODES: tuple[str, ...] = (
    "graph_only",
    "hybrid_graphrag",
    "routed_graphrag",
    "routed_token_matched_live_tfidf_graphrag",
    "routed_token_matched_dense_graphrag",
)


def build_nasa_atmonto_s7_graph_health(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    s7_retrieval_report_path: str | Path = DEFAULT_S7_RETRIEVAL_REPORT_PATH,
    modes: tuple[str, ...] = GRAPH_HEALTH_MODES,
) -> dict[str, Any]:
    root = Path(repo_root)
    report_path = resolve_report_path(root, s7_retrieval_report_path)
    source_report = read_json_object_or_empty(report_path)
    records = [
        record for record in source_report.get("records", []) if isinstance(record, dict)
    ]
    metadata = source_report.get("metadata", {})
    return {
        "source_family": "nasa_atmonto_s7_graph_health",
        "status": "s7_graph_health_evaluated",
        "metadata": {
            "s7_retrieval_report_path": project_relative_path(report_path, root),
            "source_status": source_report.get("status"),
            "retrieval_case_count": len(records),
            "modes": list(modes),
            "graph_source_node_count": metadata.get("graph_source_node_count"),
            "graph_fact_node_count": metadata.get("graph_fact_node_count"),
            "graph_edge_count": metadata.get("graph_edge_count"),
            "boundary": (
                "Graph-health diagnostics over frozen S7 retrieval records. "
                "These metrics describe path and context availability by CQ group; "
                "they do not certify semantic truth or operational readiness."
            ),
        },
        "aggregate_by_mode": aggregate_graph_health_by_mode(records, modes),
        "aggregate_by_template": aggregate_graph_health_by_template(records, modes),
        "aggregate_by_route": aggregate_graph_health_by_route(records, modes),
        "claim_boundary": (
            "Graph health is reported as topology, graph-context availability, "
            "path-support rate, answer-set recovery, and abstention behavior. "
            "It is a diagnostic layer, not a proof that graph context is always "
            "better than source or vector retrieval."
        ),
    }


def resolve_report_path(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def aggregate_graph_health_by_mode(
    records: list[dict[str, Any]],
    modes: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    return {mode: aggregate_graph_health_items(mode_items(records, mode)) for mode in modes}


def aggregate_graph_health_by_template(
    records: list[dict[str, Any]],
    modes: tuple[str, ...],
) -> dict[str, dict[str, dict[str, Any]]]:
    by_template: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_template[str(record.get("template_id") or "")].append(record)
    return {
        template_id: {
            mode: aggregate_graph_health_items(mode_items(items, mode)) for mode in modes
        }
        for template_id, items in sorted(by_template.items())
    }


def aggregate_graph_health_by_route(
    records: list[dict[str, Any]],
    modes: tuple[str, ...],
) -> dict[str, dict[str, dict[str, Any]]]:
    by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_route[str(record.get("route") or "unknown")].append(record)
    return {
        route: {mode: aggregate_graph_health_items(mode_items(items, mode)) for mode in modes}
        for route, items in sorted(by_route.items())
    }


def mode_items(records: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for record in records:
        mode_result = record.get("modes", {}).get(mode)
        if isinstance(mode_result, dict):
            items.append(mode_result)
    return items


def aggregate_graph_health_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    graph_counts = [
        int(item.get("context_budget", {}).get("graph_context_count") or 0) for item in items
    ]
    source_counts = [
        int(item.get("context_budget", {}).get("source_context_count") or 0) for item in items
    ]
    context_tokens = [
        int(item.get("context_budget", {}).get("estimated_context_tokens") or 0)
        for item in items
    ]
    path_values = [
        float(item["path_support"]["path_support_rate"])
        for item in items
        if isinstance(item.get("path_support"), dict)
        and item["path_support"].get("path_support_rate") is not None
    ]
    target_hits = [bool(item.get("target_source_retrieved")) for item in items]
    answer_sets = [
        item.get("answer_set", {}) for item in items if isinstance(item.get("answer_set"), dict)
    ]
    decisions = Counter(
        str(item.get("graph_use_decision", {}).get("decision") or "unknown")
        for item in items
    )
    underlying_modes = Counter(str(item.get("underlying_mode") or "unknown") for item in items)
    graph_context_cases = sum(1 for count in graph_counts if count > 0)
    cases = len(items)
    return {
        "cases": cases,
        "graph_context_cases": graph_context_cases,
        "graph_context_case_rate": round(graph_context_cases / cases, 4) if cases else None,
        "avg_graph_context_count": round(sum(graph_counts) / cases, 4) if cases else None,
        "avg_source_context_count": round(sum(source_counts) / cases, 4) if cases else None,
        "avg_context_tokens": round(sum(context_tokens) / cases, 2) if cases else None,
        "path_support_observed_cases": len(path_values),
        "avg_path_support_rate": round(sum(path_values) / len(path_values), 4)
        if path_values
        else None,
        "target_source_hit_rate": round(sum(int(hit) for hit in target_hits) / cases, 4)
        if cases
        else None,
        "answer_set": aggregate_answer_set_metrics(answer_sets) if answer_sets else {},
        "abstention_correctness": aggregate_abstention_correctness(answer_sets),
        "graph_use_decisions": dict(sorted(decisions.items())),
        "underlying_modes": dict(sorted(underlying_modes.items())),
    }


def write_nasa_atmonto_s7_graph_health_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S7 Graph Health by CQ Group",
        "",
        "## Scope",
        "",
        f"- Status: `{result['status']}`",
        f"- Retrieval cases: {result['metadata']['retrieval_case_count']}",
        f"- Modes: {', '.join(f'`{mode}`' for mode in result['metadata']['modes'])}",
        f"- Boundary: {result['metadata']['boundary']}",
        (
            "- Materialized graph: "
            f"{result['metadata']['graph_source_node_count']} source nodes, "
            f"{result['metadata']['graph_fact_node_count']} fact nodes, "
            f"{result['metadata']['graph_edge_count']} edges"
        ),
        "",
        "## Aggregate Graph Health by Mode",
        "",
        (
            "| Mode | Cases | Graph-context rate | Avg graph contexts | Path support | "
            "Answer F1 | Abstention correct | Target hit | Avg context tokens |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode, metrics in result["aggregate_by_mode"].items():
        lines.append(graph_health_row(mode, metrics))
    lines.extend(
        [
            "",
            "## CQ Template Graph Health",
            "",
            (
                "| Template | Mode | Cases | Graph-context rate | Avg graph contexts | "
                "Path support | Answer F1 | Abstention correct |"
            ),
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for template_id, modes in result["aggregate_by_template"].items():
        for mode, metrics in modes.items():
            lines.append(
                f"| `{template_id}` | `{mode}` | {metrics['cases']} | "
                f"{display_metric(metrics['graph_context_case_rate'])} | "
                f"{display_metric(metrics['avg_graph_context_count'])} | "
                f"{display_metric(metrics['avg_path_support_rate'])} | "
                f"{display_metric(metrics.get('answer_set', {}).get('micro_f1'))} | "
                f"{display_metric(metrics['abstention_correctness'])} |"
            )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            result["claim_boundary"],
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def graph_health_row(mode: str, metrics: dict[str, Any]) -> str:
    return (
        f"| `{mode}` | {metrics['cases']} | "
        f"{display_metric(metrics['graph_context_case_rate'])} | "
        f"{display_metric(metrics['avg_graph_context_count'])} | "
        f"{display_metric(metrics['avg_path_support_rate'])} | "
        f"{display_metric(metrics.get('answer_set', {}).get('micro_f1'))} | "
        f"{display_metric(metrics['abstention_correctness'])} | "
        f"{display_metric(metrics['target_source_hit_rate'])} | "
        f"{display_metric(metrics['avg_context_tokens'])} |"
    )


def display_metric(value: object) -> object:
    return "n/a" if value is None else value


def write_nasa_atmonto_s7_graph_health(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    s7_retrieval_report_path: str | Path = DEFAULT_S7_RETRIEVAL_REPORT_PATH,
    report_name: str = "nasa_atmonto_s7_graph_health",
    modes: tuple[str, ...] = GRAPH_HEALTH_MODES,
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_graph_health(
        repo_root=repo_root,
        s7_retrieval_report_path=s7_retrieval_report_path,
        modes=modes,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "nasa_atmonto_s7_graph_health"
    json_path = write_json_report(result, output / f"{stem}.json", sort_keys=False)
    md_path = write_nasa_atmonto_s7_graph_health_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
