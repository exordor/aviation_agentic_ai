"""Corpus-first formal projection contracts."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from aviation_agentic_ai.agent_system.corpus_store import build_corpus


_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "corpus_projection_fixture",
    Path(__file__).with_name("test_agent_system_corpus_store.py"),
)
assert _FIXTURE_SPEC is not None and _FIXTURE_SPEC.loader is not None
_fixture = importlib.util.module_from_spec(_FIXTURE_SPEC)
_FIXTURE_SPEC.loader.exec_module(_fixture)


def test_corpus_projection_contains_formal_facts_but_not_context_associations(
    tmp_path: Path,
) -> None:
    """A projection that drops facts or promotes context associations is invalid."""

    run_dir = tmp_path / "run"
    _fixture._fixture_module._write_context_layer(run_dir)
    corpus_dir = tmp_path / "corpus"
    manifest = build_corpus([run_dir], corpus_dir)

    projected_facts = {
        json.loads(line)["triple_id"]
        for line in (corpus_dir / "kg.jsonl").read_text(encoding="utf-8").splitlines()
    }
    formal_facts = {
        json.loads(line)["fact_id"]
        for line in (corpus_dir / "facts.jsonl").read_text(encoding="utf-8").splitlines()
    }
    association_ids = {
        json.loads(line)["association_id"]
        for line in (corpus_dir / "context_associations.jsonl").read_text(encoding="utf-8").splitlines()
    }

    assert projected_facts == formal_facts
    assert not projected_facts.intersection(association_ids)
    assert manifest.artifacts["neo4j_nodes"].count > 0
    assert manifest.artifacts["neo4j_relationships"].count > 0
