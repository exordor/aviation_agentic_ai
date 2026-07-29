"""Focused contracts for the resumable corpus-first batch builder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusBuildManifest,
    CorpusBuildResult,
)
from aviation_agentic_ai.agent_system.corpus_batch import (
    BatchCaseExecution,
    BatchResources,
    build_corpus_batch,
)
from aviation_agentic_ai.agent_system.agent_usage import AgentUsageRecord


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
    assert "agent_usage" not in manifest["artifacts"]
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
    assert (
        output / "agent_usage" / "agent_usage.jsonl"
    ).read_text(encoding="utf-8") == ""
    usage_manifest = json.loads(
        (
            output / "agent_usage" / "agent_usage_manifest.json"
        ).read_text(encoding="utf-8")
    )
    assert usage_manifest["record_count"] == 0
    assert usage_manifest["totals"]["provider_call_count"] == 0
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


def test_resume_replaces_blocked_usage_rows_without_duplicating_terminal_rows(
    tmp_path: Path,
) -> None:
    advisories = [_advisory("ok:one"), _advisory("blocked:two")]
    attempts: dict[str, int] = {}

    def usage(source_id: str, *, outcome: str) -> tuple[AgentUsageRecord, ...]:
        return tuple(
            AgentUsageRecord(
                source_id=source_id,
                event_id=f"event:{source_id}",
                task_id=f"task:{scope}:{source_id}",
                role=("decision_case_assembly" if scope == "decision_case" else "semantic_resolution"),
                task_scope=scope,
                execution_mode="deterministic_bypass",
                outcome=outcome,
                detail_status=("blocked" if outcome == "blocked" else "accepted"),
                activation_reason="test",
            )
            for scope in ("facility", "terminology", "decision_case")
        )

    def run_case(advisory, resources, staging_dir, allow_live_model):  # type: ignore[no-untyped-def]
        _ = resources, allow_live_model
        attempt = attempts.get(advisory.source_id, 0) + 1
        attempts[advisory.source_id] = attempt
        blocked = advisory.source_id == "blocked:two" and attempt == 1
        if blocked:
            raise RuntimeError("scripted workflow failure")
        status = "blocked" if blocked else "ok"
        return BatchCaseExecution(
            result=CorpusBuildResult(source_id=advisory.source_id, status=status),
            run_dir=staging_dir if status == "ok" else None,
            agent_usage_records=usage(
                advisory.source_id,
                outcome=("blocked" if blocked else "accepted"),
            ),
        )

    def finalizer(run_dirs, output_dir, *, build_results):  # type: ignore[no-untyped-def]
        _ = run_dirs, build_results
        manifest = CorpusBuildManifest(
            corpus_id="corpus:resume",
            run_count=2,
            case_count=2,
            fact_count=0,
            source_binding_count=0,
            source_object_count=0,
            artifacts={},
        )
        Path(output_dir, "corpus_manifest.json").write_text(
            manifest.model_dump_json() + "\n",
            encoding="utf-8",
        )
        return manifest

    output = tmp_path / "corpus"
    config = _config(advisories, tmp_path / "advisories.jsonl")
    first = build_corpus_batch(
        config,
        output,
        resource_loader=lambda config: _resources(),
        case_runner=run_case,
        corpus_normalizer=finalizer,
    )
    assert first.blocked_count == 1
    assert not (output / "agent_usage").exists()
    staged_rows = [
        json.loads(line)
        for line in (
            output / ".staging" / "agent_usage.jsonl"
        ).read_text(encoding="utf-8").splitlines()
    ]
    blocked_rows = [
        row for row in staged_rows if row["source_id"] == "blocked:two"
    ]
    assert len(blocked_rows) == 3
    assert all(row["execution_mode"] == "not_reached" for row in blocked_rows)
    assert all(row["outcome"] == "blocked" for row in blocked_rows)

    resumed = build_corpus_batch(
        config,
        output,
        resume=True,
        resource_loader=lambda config: _resources(),
        case_runner=run_case,
        corpus_normalizer=finalizer,
    )
    usage_bytes = (output / "agent_usage" / "agent_usage.jsonl").read_bytes()
    repeated = build_corpus_batch(
        config,
        output,
        resume=True,
        resource_loader=lambda config: _resources(),
        case_runner=run_case,
        corpus_normalizer=finalizer,
    )

    rows = [
        json.loads(line)
        for line in usage_bytes.decode("utf-8").splitlines()
    ]
    assert resumed.blocked_count == repeated.blocked_count == 0
    assert len(rows) == 6
    assert len(
        {
            (row["source_id"], row["role"], row["task_scope"])
            for row in rows
        }
    ) == 6
    assert all(row["outcome"] == "accepted" for row in rows)
    assert (output / "agent_usage" / "agent_usage.jsonl").read_bytes() == usage_bytes


def test_pending_ok_and_blocked_executions_get_exact_fixed_usage_rows(
    tmp_path: Path,
) -> None:
    advisories = [_advisory("ok:empty"), _advisory("blocked:partial")]

    def run_case(advisory, resources, staging_dir, allow_live_model):  # type: ignore[no-untyped-def]
        _ = resources, allow_live_model
        if advisory.source_id == "ok:empty":
            return BatchCaseExecution(
                result=CorpusBuildResult(
                    source_id=advisory.source_id,
                    status="ok",
                ),
                run_dir=staging_dir,
            )
        return BatchCaseExecution(
            result=CorpusBuildResult(
                source_id=advisory.source_id,
                status="blocked",
            ),
            agent_usage_records=(
                AgentUsageRecord(
                    source_id=advisory.source_id,
                    event_id=None,
                    task_id="task:partial",
                    role="semantic_resolution",
                    task_scope="facility",
                    execution_mode="deterministic_bypass",
                    outcome="accepted",
                    detail_status="accepted",
                    activation_reason="partial_test_record",
                ),
            ),
        )

    output = tmp_path / "corpus"
    summary = build_corpus_batch(
        _config(advisories, tmp_path / "advisories.jsonl"),
        output,
        resource_loader=lambda config: _resources(),
        case_runner=run_case,
        corpus_normalizer=_normalizer,
    )

    rows = [
        json.loads(line)
        for line in (
            output / ".staging" / "agent_usage.jsonl"
        ).read_text(encoding="utf-8").splitlines()
    ]
    assert summary.ok_count == 1
    assert summary.blocked_count == 1
    assert len(rows) == 6
    expected = {
        ("semantic_resolution", "facility"),
        ("semantic_resolution", "terminology"),
        ("decision_case_assembly", "decision_case"),
    }
    for source_id in ("ok:empty", "blocked:partial"):
        source_rows = [row for row in rows if row["source_id"] == source_id]
        assert {
            (row["role"], row["task_scope"]) for row in source_rows
        } == expected
        assert all(row["execution_mode"] == "not_reached" for row in source_rows)
        assert all(row["outcome"] == "blocked" for row in source_rows)
        assert all(
            row["activation_reason"] == "workflow_usage_missing_or_invalid"
            for row in source_rows
        )
    assert not (output / "agent_usage").exists()


def test_resume_rejects_expanding_a_finalized_source_subset(tmp_path: Path) -> None:
    advisories = [_advisory("ok:one"), _advisory("ok:two")]
    attempts: list[str] = []

    def run_case(advisory, resources, staging_dir, allow_live_model):  # type: ignore[no-untyped-def]
        _ = resources, allow_live_model
        attempts.append(advisory.source_id)
        return BatchCaseExecution(
            result=CorpusBuildResult(source_id=advisory.source_id, status="ok"),
            run_dir=staging_dir,
        )

    def finalize_subset(run_dirs, output_dir, *, build_results):  # type: ignore[no-untyped-def]
        _ = run_dirs, build_results
        manifest = CorpusBuildManifest(
            corpus_id="finalized-subset",
            run_count=1,
            case_count=1,
            fact_count=0,
            source_binding_count=0,
            source_object_count=0,
            artifacts={},
        )
        Path(output_dir, "corpus_manifest.json").write_text(
            manifest.model_dump_json() + "\n",
            encoding="utf-8",
        )
        return manifest

    output = tmp_path / "corpus"
    config = _config(advisories, tmp_path / "advisories.jsonl")
    build_corpus_batch(
        config,
        output,
        source_ids=("ok:one",),
        resource_loader=lambda config: _resources(),
        case_runner=run_case,
        corpus_normalizer=finalize_subset,
    )
    published_manifest = (output / "corpus_manifest.json").read_bytes()
    published_results = (output / "build_results.jsonl").read_bytes()

    with pytest.raises(
        ValueError,
        match="cannot expand a finalized corpus with --resume",
    ):
        build_corpus_batch(
            config,
            output,
            source_ids=("ok:one", "ok:two"),
            resume=True,
            resource_loader=lambda config: _resources(),
            case_runner=run_case,
            corpus_normalizer=finalize_subset,
        )

    assert attempts == ["ok:one"]
    assert (output / "corpus_manifest.json").read_bytes() == published_manifest
    assert (output / "build_results.jsonl").read_bytes() == published_results
