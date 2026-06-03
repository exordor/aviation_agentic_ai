from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_s5_s6_agentic_loop import (
    build_nasa_atmonto_s5_s6_agentic_loop,
    write_nasa_atmonto_s5_s6_agentic_loop,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )


def _write_fixture_files(tmp_path: Path) -> dict[str, Path]:
    gold_path = tmp_path / "gold.jsonl"
    gold_record = {
        "source_id": "2026-05-19:032",
        "source_text": "ATCSCC ADVZY 032. EFFECTIVE TIME: 191322-191630.",
        "gold_annotation": {
            "valid_facts": [
                {
                    "fact_type": "datatype_property",
                    "subject_class": "ReRouteTMI",
                    "predicate": "advisoryNumber",
                    "datatype": "xsd:integer",
                    "value": 32,
                    "evidence_text": "ATCSCC ADVZY 032",
                    "source_id": "2026-05-19:032",
                },
                {
                    "fact_type": "datatype_property",
                    "subject_class": "ReRouteTMI",
                    "predicate": "effectiveStartTime",
                    "datatype": "xsd:dateTime",
                    "value": "2026-05-19T13:22:00Z",
                    "evidence_text": "EFFECTIVE TIME: 191322-191630",
                    "source_id": "2026-05-19:032",
                },
            ],
            "missing_facts": [],
        },
    }
    _write_jsonl(gold_path, [gold_record])

    cq_manifest_path = tmp_path / "cq_manifest.json"
    _write_json(
        cq_manifest_path,
        {
            "status": "ready",
            "cqs": [
                {
                    "cq_id": "CQ-D01",
                    "route_label": "deterministic",
                    "graph_use_decision": "avoid_by_default",
                    "required_predicates": ["advisoryNumber"],
                },
                {
                    "cq_id": "CQ-D03",
                    "route_label": "hybrid",
                    "graph_use_decision": "avoid_by_default",
                    "required_predicates": ["effectiveStartTime"],
                },
            ],
        },
    )

    s4_path = tmp_path / "s4.jsonl"
    _write_jsonl(
        s4_path,
        [
            {
                "system_id": "S4_hybrid_backbone_enrichment",
                "source_id": "2026-05-19:032",
                "facts": [
                    {
                        "fact_id": "f1",
                        "fact_type": "datatype_property",
                        "subject_class": "atm:ReRouteTMI",
                        "predicate": "atm:advisoryNumber",
                        "datatype": "xsd:integer",
                        "value": 32,
                        "evidence_text": "ATCSCC ADVZY 032",
                        "source_id": "2026-05-19:032",
                    },
                    {
                        "fact_id": "f2",
                        "fact_type": "datatype_property",
                        "subject_class": "atm:ReRouteTMI",
                        "predicate": "atm:effectiveStartTime",
                        "datatype": "xsd:dateTime",
                        "value": "2026-05-19T13:22:00Z",
                        "evidence_text": "NOT IN SOURCE",
                        "source_id": "2026-05-19:032",
                    },
                ],
            }
        ],
    )

    scoring_path = tmp_path / "scoring.json"
    _write_json(
        scoring_path,
        {
            "systems": [
                {
                    "system_id": "S4_hybrid_backbone_enrichment",
                    "semantic_metrics": {
                        "available": True,
                        "predicted_fact_count": 2,
                        "gold_fact_count": 2,
                        "true_positive_count": 2,
                        "false_positive_count": 0,
                        "false_negative_count": 0,
                        "precision": 1.0,
                        "recall": 1.0,
                        "f1": 1.0,
                        "manual_semantic_correctness": 1.0,
                    },
                }
            ]
        },
    )
    agentic_loop_path = tmp_path / "agentic_loop.json"
    _write_json(agentic_loop_path, {"status": "agentic_loop_ready_with_code_review_triggers"})
    return {
        "gold_path": gold_path,
        "cq_manifest_path": cq_manifest_path,
        "s4_predictions_path": s4_path,
        "scoring_path": scoring_path,
        "agentic_loop_path": agentic_loop_path,
    }


def test_s5_s6_agentic_loop_quarantines_unsupported_evidence(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)

    result = build_nasa_atmonto_s5_s6_agentic_loop(repo_root=tmp_path, **paths)

    assert result["status"] == "s5_s6_agentic_evidence_gate_scored"
    assert result["metadata"]["s5_fact_count"] == 2
    assert result["metadata"]["s6_fact_count"] == 1
    assert result["metadata"]["quarantined_fact_count"] == 1
    assert result["metadata"]["strict_main_metrics_changed"] is False
    assert result["metadata"]["independent_live_llm_run"] is False
    assert result["routing_summary"]["module_counts"]["deterministic_core"] == 1
    assert result["routing_summary"]["module_counts"]["hybrid_semantic"] == 1
    assert result["metrics"]["s5_routed_semantic_metrics"]["f1"] == 0.5
    assert result["metrics"]["s6_evidence_gated_semantic_metrics"]["f1"] == 0.6667
    assert result["evidence_gate"]["quarantine_examples"][0]["fact_id"] == "f2"


def test_write_s5_s6_agentic_loop_outputs_json_and_markdown(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)
    output_dir = tmp_path / "reports"

    json_path, md_path, result = write_nasa_atmonto_s5_s6_agentic_loop(
        output_dir=output_dir,
        repo_root=tmp_path,
        **paths,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["metadata"]["quarantined_fact_count"] == 1
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO S5/S6 Agentic Evidence Loop" in markdown
    assert "S5 routed" in markdown
    assert "S6 evidence-gated" in markdown
    assert "evidence was not contained in the source text" in markdown
