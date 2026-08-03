"""Artifact integrity for the generic real-provider ontology KG recorder."""

from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
from aviation_agentic_ai.agent_system.kg_live_experiment import (
    KGLiveExperimentRecorder,
)


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def test_kg_live_experiment_writes_bound_raw_and_parsed_artifacts(
    tmp_path: Path,
) -> None:
    recorder = KGLiveExperimentRecorder(
        output_dir=tmp_path / "run",
        source_version_id="source-version:ontology-kg",
        expected_ner_chunk_ids=("chunk:1",),
        mode="offline_software_test",
        minimum_successful_calls=1,
    )
    call_id = recorder.record_provider_call(
        trial_id="chunk:1:ner",
        chunk_id="chunk:1",
        stage="ner",
        phase="extract_entities",
        record=ModelCallRecord(
            agent="kg_entity_extraction",
            raw_response='{"status":"accepted"}',
            provider="deepseek",
            model="deepseek-v4-flash",
            prompt_set_id="ontology-grounded-kg-v1",
            prompt_version="schema-ner-v2",
            temperature=0.0,
            input_tokens=101,
            output_tokens=12,
            latency_ms=25.0,
        ),
        native_response={
            "content": '{"status":"accepted"}',
            "usage_metadata": {
                "input_tokens": 101,
                "output_tokens": 12,
                "input_token_details": {"cache_read": 0},
            },
        },
    )
    raw_path = tmp_path / "run" / "raw_provider_responses.jsonl"
    assert len(_jsonl(raw_path)) == 1
    recorder.record_parsed_output(
        trial_id="chunk:1:ner",
        chunk_id="chunk:1",
        source_unit_id="18-1-1",
        stage="ner",
        status="accepted",
        provider_call_ids=(call_id,),
        payload={"mentions": [{"surface_text": "ATCSCC"}]},
    )
    parsed_path = tmp_path / "run" / "parsed_extraction_outputs.jsonl"
    assert len(_jsonl(parsed_path)) == 1

    manifest = recorder.finalize(
        eligible_re_chunk_ids=(),
        knowledge_revision=7,
        publication_count=3,
        construction_status="ok",
        entity_candidate_count=5,
        resolved_entity_count=4,
        unmapped_mention_count=1,
        relation_candidate_count=2,
        validated_relation_count=1,
        abstained_chunk_count=0,
        blocked_chunk_count=0,
        published_fact_count=8,
        published_evidence_link_count=9,
    )

    assert manifest.mode == "offline_software_test"
    assert manifest.integrity_status == "verified"
    assert manifest.attempted_real_calls == 1
    assert manifest.successful_real_calls == 1
    assert manifest.failed_real_calls == 0
    assert manifest.input_tokens == 101
    assert manifest.output_tokens == 12
    assert manifest.cache_read_tokens == 0
    assert manifest.ner_call_count == 1
    assert manifest.re_call_count == 0
    assert manifest.construction_status == "ok"
    assert manifest.entity_candidate_count == 5
    assert manifest.resolved_entity_count == 4
    assert manifest.unmapped_mention_count == 1
    assert manifest.relation_candidate_count == 2
    assert manifest.validated_relation_count == 1
    assert manifest.published_fact_count == 8
    assert manifest.published_evidence_link_count == 9
    assert manifest.missing_ner_chunk_ids == ()
    assert manifest.raw_response_sha256
    assert manifest.parsed_output_sha256
    raw_rows = _jsonl(Path(manifest.raw_response_artifact))
    parsed_rows = _jsonl(Path(manifest.parsed_output_artifact))
    assert raw_rows[0]["native_response"] is not None
    assert parsed_rows[0]["provider_call_ids"] == [call_id]
    assert "api_key" not in json.dumps(raw_rows).lower()


def test_live_experiment_is_incomplete_below_call_or_chunk_coverage_gate(
    tmp_path: Path,
) -> None:
    recorder = KGLiveExperimentRecorder(
        output_dir=tmp_path / "run",
        source_version_id="source-version:ontology-kg",
        expected_ner_chunk_ids=("chunk:1", "chunk:2"),
        mode="live_experiment",
        minimum_successful_calls=100,
    )

    manifest = recorder.finalize(
        eligible_re_chunk_ids=("chunk:1",),
        knowledge_revision=0,
        publication_count=0,
        construction_status="blocked",
        entity_candidate_count=0,
        resolved_entity_count=0,
        unmapped_mention_count=0,
        relation_candidate_count=0,
        validated_relation_count=0,
        abstained_chunk_count=0,
        blocked_chunk_count=2,
        published_fact_count=0,
        published_evidence_link_count=0,
    )

    assert manifest.runner_status == "incomplete"
    assert manifest.missing_ner_chunk_ids == ("chunk:1", "chunk:2")
    assert manifest.missing_re_chunk_ids == ("chunk:1",)
    assert "successful_call_threshold_not_met" in manifest.detail_codes


def test_recorder_uses_configured_provider_metadata_for_generic_domains(
    tmp_path: Path,
) -> None:
    recorder = KGLiveExperimentRecorder(
        output_dir=tmp_path / "run",
        source_version_id="source-version:generic-domain",
        expected_ner_chunk_ids=("chunk:1",),
        mode="offline_software_test",
        minimum_successful_calls=1,
        provider="example-provider",
        model="example-model",
        temperature=0.2,
    )
    recorder.record_provider_call(
        trial_id="chunk:1:ner",
        chunk_id="chunk:1",
        stage="ner",
        phase="extract_entities",
        record=ModelCallRecord(
            agent="kg_entity_extraction",
            raw_response='{"status":"accepted"}',
            provider="example-provider",
            model="example-model",
            temperature=0.2,
        ),
        native_response={"content": '{"status":"accepted"}'},
    )
    manifest = recorder.finalize(
        eligible_re_chunk_ids=(),
        knowledge_revision=1,
        publication_count=1,
        construction_status="ok",
        entity_candidate_count=1,
        resolved_entity_count=1,
        unmapped_mention_count=0,
        relation_candidate_count=0,
        validated_relation_count=0,
        abstained_chunk_count=0,
        blocked_chunk_count=0,
        published_fact_count=1,
        published_evidence_link_count=1,
    )

    assert manifest.provider == "example-provider"
    assert manifest.model == "example-model"
    assert manifest.temperature == 0.2
    assert manifest.successful_real_calls == 1
