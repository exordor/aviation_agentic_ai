"""Focused contracts for the resumable corpus-first batch builder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from aviation_agentic_ai.agent_system.corpus_store import CorpusBuildResult
from aviation_agentic_ai.agent_system.corpus_batch import (
    BatchCaseExecution,
    BatchResources,
    build_corpus_batch,
)


def _advisory(
    source_id: str,
    *,
    event: str = "GS",
    complete: bool = True,
) -> dict[str, str]:
    if event == "unsupported":
        text = "ATCSCC ADVZY 001 JFK/ZNY 05/19/2026 ROUTE ADVISORY"
    elif complete:
        term = "GROUND STOP" if event == "GS" else "GROUND DELAY PROGRAM"
        text = (
            f"ATCSCC ADVZY 001 JFK/ZNY 05/19/2026 {term} "
            "CTL ELEMENT: JFK GROUND STOP PERIOD: 19/2100Z - 19/2245Z"
        )
    else:
        text = "ATCSCC ADVZY 001 JFK/ZNY 05/19/2026 GROUND STOP"
    return {"source_id": source_id, "text": text, "title": source_id}


def _config(
    advisories: list[dict[str, str]],
    advisory_path: Path,
    *,
    expected_cohort_count: int | None = None,
) -> dict[str, Any]:
    advisory_path.write_text(
        "".join(json.dumps(row) + "\n" for row in advisories), encoding="utf-8"
    )
    return {
        "cohort": {
            "airport_codes": ["JFK"],
            "expected_record_count": expected_cohort_count or len(advisories),
        },
        "sources": {"atcscc_advisories": str(advisory_path)},
    }


def _resources() -> BatchResources:
    return BatchResources(
        guide=object(),
        authority_catalog=object(),
        facility_candidates=[],
        term_candidates=[],
        weather_sources=[],
        bts_rows=[],
        bts_source=None,
        bts_manifest_binding=None,
    )


def _normalizer(run_dirs, output_dir, *, build_results):  # type: ignore[no-untyped-def]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "corpus_manifest.json").write_text("{}\n", encoding="utf-8")
    return {"run_dirs": tuple(run_dirs), "results": tuple(build_results)}


def test_cohort_batch_preflights_26_records_without_running_models(tmp_path: Path) -> None:
    advisories = [
        *[_advisory(f"ok:{number:02d}") for number in range(42)],
        *[_advisory(f"unsupported:{number:02d}", event="unsupported") for number in range(23)],
        *[_advisory(f"incomplete:{number:02d}", complete=False) for number in range(3)],
        *[
            _advisory(f"outside-cohort:{number:03d}", event="unsupported")
            | {"text": "ATCSCC ADVZY 001 LAX/ZLA 05/19/2026 ROUTE ADVISORY"}
            for number in range(650)
        ],
    ]
    resource_loads = 0
    executions: list[tuple[str, int]] = []

    def load_resources(config: dict[str, Any]) -> BatchResources:
        nonlocal resource_loads
        _ = config
        resource_loads += 1
        return _resources()

    def run_case(advisory, resources, staging_dir, allow_live_model):  # type: ignore[no-untyped-def]
        _ = staging_dir, allow_live_model
        executions.append((advisory.source_id, id(resources)))
        return BatchCaseExecution(
            result=CorpusBuildResult(
                source_id=advisory.source_id,
                status="ok",
                event_id=f"event:{advisory.source_id}",
                case_id=f"case:{advisory.source_id}",
                provider_call_count=1,
            ),
            run_dir=staging_dir,
        )

    output = tmp_path / "corpus"
    summary = build_corpus_batch(
        _config(
            advisories,
            tmp_path / "advisories.jsonl",
            expected_cohort_count=68,
        ),
        output,
        resource_loader=load_resources,
        case_runner=run_case,
        corpus_normalizer=_normalizer,
    )

    assert summary.selected_count == 68
    assert summary.ok_count == 42
    assert summary.insufficient_count == 26
    assert summary.blocked_count == 0
    assert resource_loads == 1
    assert len(executions) == 42
    assert len({resource_id for _, resource_id in executions}) == 1
    results = [
        json.loads(line)
        for line in (output / "build_results.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(results) == 68
    assert sum(row["status"] == "insufficient" for row in results) == 26
    assert sum(row["provider_call_count"] for row in results if row["status"] == "insufficient") == 0


def test_all_insufficient_batch_publishes_valid_empty_corpus(tmp_path: Path) -> None:
    advisories = [
        _advisory("unsupported:one", event="unsupported"),
        _advisory("unsupported:two", event="unsupported"),
    ]
    output = tmp_path / "corpus"

    summary = build_corpus_batch(
        _config(advisories, tmp_path / "advisories.jsonl"),
        output,
    )

    assert summary.selected_count == 2
    assert summary.insufficient_count == 2
    assert summary.blocked_count == 0
    manifest = json.loads(
        (output / "corpus_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["manifest_version"] == "decision-case-corpus-v2"
    assert manifest["run_count"] == 0
    assert manifest["case_count"] == 0
    assert manifest["fact_count"] == 0
    results = [
        json.loads(line)
        for line in (output / "build_results.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert [row["status"] for row in results] == [
        "insufficient",
        "insufficient",
    ]
    for name in (
        "artifacts.jsonl",
        "source_bindings.jsonl",
        "cases.jsonl",
        "facts.jsonl",
        "case_facts.jsonl",
        "evidence_links.jsonl",
        "profile_gaps.jsonl",
        "context_associations.jsonl",
        "observations.jsonl",
        "kg.jsonl",
        "kg.ttl",
        "neo4j_nodes.jsonl",
        "neo4j_relationships.jsonl",
    ):
        assert (output / name).read_text(encoding="utf-8") == ""
    assert list((output / "source_objects").iterdir()) == []


def test_blocked_case_does_not_stop_the_batch_or_publish_manifest(tmp_path: Path) -> None:
    advisories = [_advisory("ok:one"), _advisory("blocked:two"), _advisory("ok:three")]
    calls: list[str] = []

    def run_case(advisory, resources, staging_dir, allow_live_model):  # type: ignore[no-untyped-def]
        _ = resources, staging_dir, allow_live_model
        calls.append(advisory.source_id)
        status = "blocked" if advisory.source_id == "blocked:two" else "ok"
        return BatchCaseExecution(
            result=CorpusBuildResult(source_id=advisory.source_id, status=status),
            run_dir=staging_dir if status == "ok" else None,
        )

    output = tmp_path / "corpus"
    summary = build_corpus_batch(
        _config(advisories, tmp_path / "advisories.jsonl"),
        output,
        resource_loader=lambda config: _resources(),
        case_runner=run_case,
        corpus_normalizer=_normalizer,
    )

    assert calls == ["ok:one", "blocked:two", "ok:three"]
    assert summary.blocked_count == 1
    assert not (output / "corpus_manifest.json").exists()


def test_resume_withholds_old_manifest_when_new_block_is_persisted(
    tmp_path: Path,
) -> None:
    advisories = [
        _advisory("ok:existing"),
        _advisory("blocked:new"),
        _advisory("interrupted:new"),
    ]
    output = tmp_path / "corpus"
    output.mkdir()
    (output / "corpus_manifest.json").write_text("{}\n", encoding="utf-8")
    (output / "build_results.jsonl").write_text(
        CorpusBuildResult(source_id="ok:existing", status="ok").model_dump_json()
        + "\n",
        encoding="utf-8",
    )

    def run_case(advisory, resources, staging_dir, allow_live_model):  # type: ignore[no-untyped-def]
        _ = resources, staging_dir, allow_live_model
        if advisory.source_id == "interrupted:new":
            raise KeyboardInterrupt
        return BatchCaseExecution(
            result=CorpusBuildResult(source_id=advisory.source_id, status="blocked")
        )

    with pytest.raises(KeyboardInterrupt):
        build_corpus_batch(
            _config(advisories, tmp_path / "advisories.jsonl"),
            output,
            resume=True,
            resource_loader=lambda config: _resources(),
            case_runner=run_case,
            corpus_normalizer=_normalizer,
        )

    persisted = [
        json.loads(line)
        for line in (output / "build_results.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert any(
        row["source_id"] == "blocked:new" and row["status"] == "blocked"
        for row in persisted
    )
    assert not (output / "corpus_manifest.json").exists()


def test_resume_retries_only_blocked_cases_and_is_idempotent(tmp_path: Path) -> None:
    advisories = [_advisory("ok:one"), _advisory("blocked:two"), _advisory("ok:three")]
    attempts: list[str] = []
    blocked_attempts = 0

    def run_case(advisory, resources, staging_dir, allow_live_model):  # type: ignore[no-untyped-def]
        nonlocal blocked_attempts
        _ = resources, staging_dir, allow_live_model
        attempts.append(advisory.source_id)
        status = "ok"
        if advisory.source_id == "blocked:two" and blocked_attempts == 0:
            status = "blocked"
            blocked_attempts += 1
        return BatchCaseExecution(
            result=CorpusBuildResult(source_id=advisory.source_id, status=status),
            run_dir=staging_dir if status == "ok" else None,
        )

    output = tmp_path / "corpus"
    config = _config(advisories, tmp_path / "advisories.jsonl")
    build_corpus_batch(
        config,
        output,
        resource_loader=lambda config: _resources(),
        case_runner=run_case,
        corpus_normalizer=_normalizer,
    )
    resumed = build_corpus_batch(
        config,
        output,
        resume=True,
        resource_loader=lambda config: _resources(),
        case_runner=run_case,
        corpus_normalizer=_normalizer,
    )
    repeated = build_corpus_batch(
        config,
        output,
        resume=True,
        resource_loader=lambda config: _resources(),
        case_runner=run_case,
        corpus_normalizer=_normalizer,
    )

    assert attempts == ["ok:one", "blocked:two", "ok:three", "blocked:two"]
    assert resumed.blocked_count == 0
    assert repeated.blocked_count == 0
    assert (output / "corpus_manifest.json").exists()
    results = (output / "build_results.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(results) == 3
