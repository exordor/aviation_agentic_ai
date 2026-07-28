"""Deterministic cross-run storage for validated decision-case corpora."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import (
    StrictModel,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.query_tools import QueryGraphStore


_RDF_TYPE_IRI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


class CorpusArtifactMetadata(StrictModel):
    """One content-verified artifact in a corpus build."""

    path: str = Field(min_length=1)
    count: int = Field(ge=0)
    sha256: str = Field(min_length=64, max_length=64)


class CorpusBuildManifest(StrictModel):
    """Stable summary of one materialized cross-run corpus."""

    manifest_version: Literal["decision-case-corpus-v1"] = (
        "decision-case-corpus-v1"
    )
    corpus_id: str = Field(min_length=1)
    run_count: int = Field(ge=0)
    case_count: int = Field(ge=0)
    fact_count: int = Field(ge=0)
    source_binding_count: int = Field(ge=0)
    source_object_count: int = Field(ge=0)
    artifacts: dict[str, CorpusArtifactMetadata]


class CorpusCase(StrictModel):
    """Catalog row for one validated event run."""

    case_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    run_ids: list[str] = Field(min_length=1)
    advisory_source_id: str = Field(min_length=1)
    event_type_iris: list[str] = Field(default_factory=list)
    facility_ids: list[str] = Field(default_factory=list)
    operational_start: str | None = None
    operational_end: str | None = None
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None = None
    fact_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)


class CorpusSourceBinding(StrictModel):
    """Bind one case source to a shared content-addressed object."""

    case_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_family: str = Field(min_length=1)
    source_url: str | None = None
    snapshot_timestamps: list[str] = Field(min_length=1)
    content_sha256: str = Field(min_length=64, max_length=64)
    object_key: str = Field(min_length=64, max_length=64)


class CorpusCaseFact(StrictModel):
    """Membership edge from a case catalog row to a canonical fact."""

    case_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    fact_id: str = Field(min_length=1)


def build_corpus(
    run_dirs: list[str | Path] | tuple[str | Path, ...],
    output_dir: str | Path,
) -> CorpusBuildManifest:
    """Validate runs and merge their sources, cases, and canonical facts."""

    stores = [
        QueryGraphStore(run_dir)
        for run_dir in sorted(run_dirs, key=lambda value: str(Path(value).resolve()))
    ]
    fact_payloads: dict[str, dict[str, object]] = {}
    cases_by_id: dict[str, CorpusCase] = {}
    bindings_by_id: dict[tuple[str, str], CorpusSourceBinding] = {}
    case_facts_by_id: dict[tuple[str, str], CorpusCaseFact] = {}
    source_objects: dict[str, str] = {}

    for store in stores:
        if len(store.event_ids) != 1:
            raise ValueError("each corpus run must contain exactly one event")
        event_id = store.event_ids[0]
        case_id = event_id
        facts = sorted(store.validated_facts, key=lambda fact: fact.fact_id)

        for fact in facts:
            payload = _canonical_fact_payload(fact)
            previous = fact_payloads.get(fact.fact_id)
            if previous is not None and previous != payload:
                raise ValueError(
                    f"conflicting fact content for fact ID: {fact.fact_id}"
                )
            fact_payloads[fact.fact_id] = payload
            membership = CorpusCaseFact(
                case_id=case_id,
                event_id=event_id,
                fact_id=fact.fact_id,
            )
            case_facts_by_id[(case_id, fact.fact_id)] = membership

        event_facts = [
            fact for fact in facts if fact.subject_iri == event_id
        ]
        formal_reasons = sorted(
            {
                fact.object_value
                for fact in event_facts
                if _local_name(fact.predicate_iri) == "impactingCondition"
            }
        )
        reason_gaps = sorted(
            (
                gap
                for gap in store.profile_gaps
                if gap.event_id == event_id
                and gap.field == "impacting_condition"
            ),
            key=lambda gap: gap.profile_gap_id,
        )
        if formal_reasons:
            reason_status = "formal"
            reason_value = formal_reasons[0]
        elif reason_gaps:
            reason_status = "profile_gap"
            reason_value = reason_gaps[0].value
        else:
            reason_status = "missing"
            reason_value = None

        snapshots = sorted(
            store.source_snapshots.snapshots,
            key=lambda snapshot: snapshot.source_id,
        )
        for snapshot in snapshots:
            source_objects.setdefault(
                snapshot.content_sha256,
                snapshot.content,
            )
            binding = CorpusSourceBinding(
                case_id=case_id,
                source_id=snapshot.source_id,
                source_family=snapshot.family.value,
                source_url=snapshot.source_url,
                snapshot_timestamps=[snapshot.snapshot_timestamp],
                content_sha256=snapshot.content_sha256,
                object_key=snapshot.content_sha256,
            )
            binding_key = (case_id, snapshot.source_id)
            previous_binding = bindings_by_id.get(binding_key)
            if previous_binding is not None:
                previous_payload = previous_binding.model_dump(mode="json")
                current_payload = binding.model_dump(mode="json")
                previous_payload.pop("snapshot_timestamps")
                current_payload.pop("snapshot_timestamps")
                if previous_payload != current_payload:
                    raise ValueError(
                        f"conflicting source binding for case: {case_id}"
                    )
                binding = previous_binding.model_copy(
                    update={
                        "snapshot_timestamps": sorted(
                            set(previous_binding.snapshot_timestamps)
                            | set(binding.snapshot_timestamps)
                        )
                    }
                )
            bindings_by_id[binding_key] = binding

        case = CorpusCase(
            case_id=case_id,
            event_id=event_id,
            run_ids=[str(store.manifest["run_id"])],
            advisory_source_id=str(store.manifest["source_id"]),
            event_type_iris=sorted(
                {
                    fact.object_value
                    for fact in event_facts
                    if fact.predicate_iri == _RDF_TYPE_IRI
                }
            ),
            facility_ids=sorted(
                {
                    fact.object_value
                    for fact in event_facts
                    if _local_name(fact.predicate_iri)
                    == "controlledNASelement"
                }
            ),
            operational_start=_first_object(
                event_facts,
                "effectiveStartTime",
            ),
            operational_end=_first_object(
                event_facts,
                "effectiveEndTime",
            ),
            reason_status=reason_status,
            reason_value=reason_value,
            fact_ids=[fact.fact_id for fact in facts],
            source_ids=[snapshot.source_id for snapshot in snapshots],
        )
        previous_case = cases_by_id.get(case_id)
        if previous_case is None:
            cases_by_id[case_id] = case
        else:
            previous_payload = previous_case.model_dump(mode="json")
            current_payload = case.model_dump(mode="json")
            previous_payload.pop("run_ids")
            current_payload.pop("run_ids")
            if previous_payload != current_payload:
                raise ValueError(f"conflicting case content for case ID: {case_id}")
            cases_by_id[case_id] = previous_case.model_copy(
                update={
                    "run_ids": sorted(
                        set(previous_case.run_ids) | set(case.run_ids)
                    )
                }
            )

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    object_dir = output / "source_objects"
    object_dir.mkdir(parents=True, exist_ok=True)

    artifacts: dict[str, CorpusArtifactMetadata] = {}
    for object_key, content in sorted(source_objects.items()):
        object_path = object_dir / f"{object_key}.txt"
        object_path.write_text(content, encoding="utf-8")
        artifacts[f"source_object:{object_key}"] = _artifact_metadata(
            output,
            object_path,
            count=1,
        )

    bindings_path = output / "source_bindings.jsonl"
    cases_path = output / "cases.jsonl"
    facts_path = output / "facts.jsonl"
    case_facts_path = output / "case_facts.jsonl"
    _write_jsonl(
        bindings_path,
        [
            binding.model_dump(mode="json")
            for binding in sorted(
                bindings_by_id.values(),
                key=lambda row: (row.case_id, row.source_id),
            )
        ],
    )
    _write_jsonl(
        cases_path,
        [
            case.model_dump(mode="json")
            for case in sorted(cases_by_id.values(), key=lambda row: row.case_id)
        ],
    )
    _write_jsonl(
        facts_path,
        [
            fact_payloads[fact_id]
            for fact_id in sorted(fact_payloads)
        ],
    )
    _write_jsonl(
        case_facts_path,
        [
            row.model_dump(mode="json")
            for row in sorted(
                case_facts_by_id.values(),
                key=lambda value: (value.case_id, value.fact_id),
            )
        ],
    )
    for name, path, count in (
        ("source_bindings", bindings_path, len(bindings_by_id)),
        ("cases", cases_path, len(cases_by_id)),
        ("facts", facts_path, len(fact_payloads)),
        ("case_facts", case_facts_path, len(case_facts_by_id)),
    ):
        artifacts[name] = _artifact_metadata(output, path, count=count)

    corpus_seed = {
        name: artifact.sha256
        for name, artifact in sorted(artifacts.items())
    }
    corpus_id = hashlib.sha256(
        _canonical_json(corpus_seed).encode("utf-8")
    ).hexdigest()
    manifest = CorpusBuildManifest(
        corpus_id=corpus_id,
        run_count=len(stores),
        case_count=len(cases_by_id),
        fact_count=len(fact_payloads),
        source_binding_count=len(bindings_by_id),
        source_object_count=len(source_objects),
        artifacts=artifacts,
    )
    (output / "corpus_manifest.json").write_text(
        json.dumps(
            manifest.model_dump(mode="json"),
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def load_case_catalog(corpus_dir: str | Path) -> tuple[CorpusCase, ...]:
    """Load the stable case catalog for a materialized corpus."""

    return tuple(
        CorpusCase.model_validate(row)
        for row in _read_jsonl(Path(corpus_dir) / "cases.jsonl")
    )


def load_corpus_facts(
    corpus_dir: str | Path,
    event_id: str | None = None,
) -> tuple[ValidatedFact, ...]:
    """Load canonical facts, optionally restricted to one event's case."""

    root = Path(corpus_dir)
    facts = {
        fact.fact_id: fact
        for fact in (
            ValidatedFact.model_validate(row)
            for row in _read_jsonl(root / "facts.jsonl")
        )
    }
    if event_id is None:
        selected_ids = set(facts)
    else:
        case_ids = {
            case.case_id
            for case in load_case_catalog(root)
            if case.event_id == event_id
        }
        selected_ids = {
            str(row["fact_id"])
            for row in _read_jsonl(root / "case_facts.jsonl")
            if str(row.get("case_id") or "") in case_ids
        }
    return tuple(
        facts[fact_id]
        for fact_id in sorted(selected_ids)
        if fact_id in facts
    )


def _canonical_fact_payload(fact: ValidatedFact) -> dict[str, object]:
    payload = fact.model_dump(mode="json")
    payload["source_ids"] = sorted(payload["source_ids"])
    payload["evidence_texts"] = sorted(payload["evidence_texts"])
    return payload


def _local_name(iri: str) -> str:
    return iri.rsplit("#", 1)[-1]


def _first_object(
    facts: list[ValidatedFact],
    predicate_name: str,
) -> str | None:
    values = sorted(
        {
            fact.object_value
            for fact in facts
            if _local_name(fact.predicate_iri) == predicate_name
        }
    )
    return values[0] if values else None


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    text = "".join(f"{_canonical_json(row)}\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _artifact_metadata(
    root: Path,
    path: Path,
    *,
    count: int,
) -> CorpusArtifactMetadata:
    data = path.read_bytes()
    return CorpusArtifactMetadata(
        path=path.relative_to(root).as_posix(),
        count=count,
        sha256=hashlib.sha256(data).hexdigest(),
    )
