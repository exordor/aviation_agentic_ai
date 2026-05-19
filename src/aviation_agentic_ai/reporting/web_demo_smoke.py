from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path


def _check(check_id: str, passed: bool, detail: str, **extra: Any) -> dict[str, Any]:
    return {
        "id": check_id,
        "passed": bool(passed),
        "detail": detail,
        **extra,
    }


def _append_api_error(
    checks: list[dict[str, Any]],
    check_id: str,
    exc: Exception,
) -> None:
    checks.append(_check(check_id, False, f"{type(exc).__name__}: {exc}"))


def build_web_demo_smoke(
    project_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    root = Path(project_root)
    checks: list[dict[str, Any]] = []
    payloads: dict[str, Any] = {}

    try:
        from fastapi.testclient import TestClient

        from aviation_agentic_ai.web.app import create_app
    except Exception as exc:  # pragma: no cover - depends on optional extras.
        checks.append(
            _check(
                "web_dependencies_importable",
                False,
                f"{type(exc).__name__}: {exc}",
            )
        )
        return {
            "metadata": {
                "created_at": datetime.now(UTC).isoformat(),
                "project_root": project_relative_path(root),
                "purpose": "offline_fastapi_web_demo_smoke",
            },
            "ready": False,
            "checks": checks,
            "payloads": payloads,
            "notes": [
                "Install web extras before running the FastAPI smoke check.",
            ],
        }

    checks.append(_check("web_dependencies_importable", True, "FastAPI TestClient loaded."))
    client = TestClient(create_app(project_root=root, enable_live_query=False))

    try:
        root_response = client.get("/")
        root_text = root_response.text
        checks.append(
            _check(
                "root_page_served",
                root_response.status_code == 200,
                f"HTTP {root_response.status_code}",
            )
        )
        for token in (
            "question-list",
            "toolbar-group",
            "Demo Narrative",
            "Pipeline Explanation",
            "Why This Result",
            "KG Relationship Graph",
            "Retrieved Chunks",
            "Optional Live Query",
        ):
            checks.append(
                _check(
                    f"root_contains_{token.lower().replace(' ', '_')}",
                    token in root_text,
                    f"Token `{token}` present in static HTML.",
                )
            )
    except Exception as exc:
        _append_api_error(checks, "root_page_served", exc)

    try:
        status_response = client.get("/api/status")
        status = status_response.json()
        payloads["status"] = {
            "ready": status.get("ready"),
            "default_strategy": status.get("default_strategy"),
            "live_query_enabled": status.get("live_query_enabled"),
        }
        checks.extend(
            [
                _check(
                    "status_api_ok",
                    status_response.status_code == 200,
                    f"HTTP {status_response.status_code}",
                ),
                _check(
                    "status_default_strategy_structure_aware",
                    status.get("default_strategy") == "structure_aware",
                    f"default_strategy={status.get('default_strategy')}",
                ),
                _check(
                    "status_live_query_disabled",
                    status.get("live_query_enabled") is False,
                    f"live_query_enabled={status.get('live_query_enabled')}",
                ),
                _check(
                    "status_advisory_boundary_present",
                    bool(status.get("advisory_boundary")),
                    "Advisory boundary returned by API.",
                ),
            ]
        )
    except Exception as exc:
        _append_api_error(checks, "status_api_ok", exc)

    try:
        explanation_response = client.get("/api/demo/explanation")
        explanation = explanation_response.json()
        payloads["explanation"] = {
            "default_path": explanation.get("narrative", {}).get("default_path"),
            "recommended_strategy": explanation.get("strategy_decision", {}).get(
                "recommended"
            ),
            "pipeline_steps": len(explanation.get("pipeline_steps", [])),
        }
        checks.extend(
            [
                _check(
                    "explanation_api_ok",
                    explanation_response.status_code == 200,
                    f"HTTP {explanation_response.status_code}",
                ),
                _check(
                    "explanation_has_pipeline",
                    bool(explanation.get("pipeline_steps")),
                    "Pipeline steps returned.",
                ),
                _check(
                    "explanation_recommends_structure_aware",
                    explanation.get("strategy_decision", {}).get("recommended")
                    == "structure_aware",
                    "Strategy decision available.",
                ),
            ]
        )
    except Exception as exc:
        _append_api_error(checks, "explanation_api_ok", exc)

    first_cq_id: str | None = None
    try:
        questions_response = client.get("/api/questions")
        questions = questions_response.json().get("questions", [])
        first_cq_id = questions[0]["cq_id"] if questions else None
        payloads["questions"] = {
            "count": len(questions),
            "first_cq_id": first_cq_id,
        }
        checks.extend(
            [
                _check(
                    "questions_api_ok",
                    questions_response.status_code == 200,
                    f"HTTP {questions_response.status_code}",
                ),
                _check(
                    "questions_count_10",
                    len(questions) == 10,
                    f"questions={len(questions)}",
                ),
                _check(
                    "questions_have_source_pages",
                    all("source_page" in question for question in questions),
                    "Every question summary exposes source_page.",
                ),
            ]
        )
    except Exception as exc:
        _append_api_error(checks, "questions_api_ok", exc)

    if first_cq_id:
        try:
            detail_response = client.get(f"/api/questions/{first_cq_id}")
            detail = detail_response.json()
            hybrid = (
                detail.get("experiments", {})
                .get("structure_aware", {})
                .get("modes", {})
                .get("hybrid", {})
            )
            checks.extend(
                [
                    _check(
                        "question_detail_api_ok",
                        detail_response.status_code == 200,
                        f"HTTP {detail_response.status_code}",
                    ),
                    _check(
                        "question_detail_has_structure_hybrid",
                        bool(hybrid.get("present")),
                        "Structure-aware hybrid payload is present.",
                    ),
                    _check(
                        "question_detail_has_gold_label",
                        bool(detail.get("gold")),
                        "Gold label returned with question detail.",
                    ),
                ]
            )
        except Exception as exc:
            _append_api_error(checks, "question_detail_api_ok", exc)

        try:
            graph_response = client.get(f"/api/questions/{first_cq_id}/kg-graph")
            graph = graph_response.json()
            vector_response = client.get(
                f"/api/questions/{first_cq_id}/kg-graph?mode=vector"
            )
            vector_graph = vector_response.json()
            payloads["kg_graph"] = {
                "cq_id": first_cq_id,
                "hybrid_edges": graph.get("metadata", {}).get("edge_count"),
                "hybrid_nodes": graph.get("metadata", {}).get("node_count"),
                "vector_edges": vector_graph.get("metadata", {}).get("edge_count"),
            }
            checks.extend(
                [
                    _check(
                        "kg_graph_api_ok",
                        graph_response.status_code == 200,
                        f"HTTP {graph_response.status_code}",
                    ),
                    _check(
                        "kg_graph_hybrid_has_edges",
                        graph.get("metadata", {}).get("edge_count", 0) > 0,
                        f"hybrid_edges={graph.get('metadata', {}).get('edge_count')}",
                    ),
                    _check(
                        "kg_graph_vector_empty_state",
                        vector_response.status_code == 200
                        and vector_graph.get("metadata", {}).get("edge_count") == 0,
                        f"vector_edges={vector_graph.get('metadata', {}).get('edge_count')}",
                    ),
                ]
            )
        except Exception as exc:
            _append_api_error(checks, "kg_graph_api_ok", exc)

    try:
        live_response = client.post(
            "/api/query",
            json={"question": "What affects lift?", "mode": "hybrid"},
        )
        checks.append(
            _check(
                "live_query_disabled_by_default",
                live_response.status_code == 403,
                f"HTTP {live_response.status_code}",
            )
        )
    except Exception as exc:
        _append_api_error(checks, "live_query_disabled_by_default", exc)

    try:
        favicon_response = client.get("/favicon.ico")
        checks.append(
            _check(
                "favicon_no_content",
                favicon_response.status_code == 204,
                f"HTTP {favicon_response.status_code}",
            )
        )
    except Exception as exc:
        _append_api_error(checks, "favicon_no_content", exc)

    return {
        "metadata": {
            "created_at": datetime.now(UTC).isoformat(),
            "project_root": project_relative_path(root),
            "purpose": "offline_fastapi_web_demo_smoke",
            "method": "fastapi_testclient_static_and_api_checks",
        },
        "ready": all(check["passed"] for check in checks),
        "checks": checks,
        "payloads": payloads,
        "notes": [
            "This smoke report verifies local static HTML and offline API behavior.",
            "It does not replace a visual browser screenshot or deployment test.",
            "Live query remains disabled by default for reproducible demonstrations.",
        ],
    }


def write_web_demo_smoke_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_web_demo_smoke_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Web Demo Final Smoke",
        "",
        f"- Ready: {result['ready']}",
        f"- Method: `{result['metadata']['method']}`",
        "",
        "## Checks",
        "",
        "| Check | Passed | Detail |",
        "| --- | ---: | --- |",
    ]
    for check in result["checks"]:
        lines.append(
            f"| `{check['id']}` | {check['passed']} | "
            f"{str(check.get('detail', '')).replace('|', '/')} |"
        )
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in result["notes"])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_web_demo_smoke(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    report_name: str = "web_demo_final_smoke",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_web_demo_smoke(project_root)
    output = Path(output_dir)
    stem = Path(report_name).stem or "web_demo_final_smoke"
    json_path = write_web_demo_smoke_json(result, output / f"{stem}.json")
    md_path = write_web_demo_smoke_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
