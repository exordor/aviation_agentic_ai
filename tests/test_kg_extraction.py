from pathlib import Path

from aviation_agentic_ai.chunking.chunks import SourceChunk, write_chunks_jsonl
from aviation_agentic_ai.kg.extraction import (
    KGTriple,
    extract_kg_file,
    validate_kg_file,
    validate_kg_triples,
    write_kg_jsonl,
    write_kg_ttl,
    write_kg_validation_reports,
)


def write_profile(path: Path) -> None:
    path.write_text(
        """
name: test_profile
namespace: "http://www.example.org/aviation/phak#"
instantiable_classes:
  - Cl_Air
  - Cl_Wing
relation_properties:
  - affects
  - hasCondition
provenance_fields:
  - source_document
  - page
  - section
  - chunk_id
  - evidence_text
  - model
  - confidence
  - extracted_at
  - subject
  - predicate
  - object
""",
        encoding="utf-8",
    )


def make_chunk() -> SourceChunk:
    return SourceChunk(
        chunk_id="doc-p00-c00",
        source_document="doc",
        source_path="data/raw/doc.pdf",
        page=0,
        chunk_index=0,
        char_start=0,
        char_end=80,
        text="Air flows over the wing and affects lift.",
    )


def make_triple(**overrides) -> KGTriple:
    data = {
        "triple_id": "t1",
        "subject": "air",
        "predicate": "affects",
        "object": "wing",
        "subject_class": "Cl_Air",
        "object_class": "Cl_Wing",
        "source_document": "doc",
        "page": 0,
        "section": "page-0",
        "chunk_id": "doc-p00-c00",
        "evidence_text": "Air flows over the wing and affects lift.",
        "model": "test",
        "confidence": 0.9,
        "extracted_at": "2026-05-18T00:00:00+00:00",
    }
    data.update(overrides)
    return KGTriple(**data)


def test_kg_validator_rejects_unsupported_property_and_bad_evidence(tmp_path: Path) -> None:
    profile_path = tmp_path / "profile.yaml"
    write_profile(profile_path)
    chunk = make_chunk()
    triple = make_triple(predicate="unsupported", evidence_text="not in chunk")

    from aviation_agentic_ai.kg.extraction import load_extraction_profile

    report = validate_kg_triples([triple], [chunk], load_extraction_profile(profile_path))

    assert not report["valid"]
    assert any(error["field"] == "predicate" for error in report["errors"])
    assert any(error["field"] == "evidence_text" for error in report["errors"])


def test_extract_kg_dry_run_writes_valid_seed_triples(tmp_path: Path) -> None:
    profile_path = tmp_path / "profile.yaml"
    chunks_path = tmp_path / "chunks.jsonl"
    output_path = tmp_path / "kg.jsonl"
    write_profile(profile_path)
    write_chunks_jsonl([make_chunk()], chunks_path)

    path, triples, report = extract_kg_file(
        chunks_path,
        output_path,
        profile_path,
        dry_run=True,
    )

    assert path.exists()
    assert triples
    assert report["valid"]


def test_extract_kg_llm_filters_unsupported_or_bad_evidence(
    tmp_path: Path, monkeypatch
) -> None:
    from aviation_agentic_ai.kg import extraction

    profile_path = tmp_path / "profile.yaml"
    chunks_path = tmp_path / "chunks.jsonl"
    output_path = tmp_path / "kg.jsonl"
    write_profile(profile_path)
    write_chunks_jsonl([make_chunk()], chunks_path)

    monkeypatch.setattr(
        extraction,
        "_invoke_llm_text",
        lambda *_args, **_kwargs: """
{
  "triples": [
    {
      "subject": "air",
      "predicate": "affects",
      "object": "wing",
      "subject_class": "Cl_Air",
      "object_class": "Cl_Wing",
      "evidence_text": "Air flows over the wing and affects lift.",
      "confidence": 0.9
    },
    {
      "subject": "air",
      "predicate": "affects",
      "object": "unknown",
      "subject_class": "Cl_Air",
      "object_class": "Cl_Other",
      "evidence_text": "Air flows over the wing and affects lift.",
      "confidence": 0.9
    },
    {
      "subject": "air",
      "predicate": "affects",
      "object": "wing",
      "subject_class": "Cl_Air",
      "object_class": "Cl_Wing",
      "evidence_text": "not an exact quote",
      "confidence": 0.9
    }
  ]
}
""",
    )

    _path, triples, report = extract_kg_file(chunks_path, output_path, profile_path)

    assert report["valid"]
    assert len(triples) == 1
    assert triples[0].object_class == "Cl_Wing"


def test_validate_kg_file_reports_valid_artifact(tmp_path: Path) -> None:
    profile_path = tmp_path / "profile.yaml"
    chunks_path = tmp_path / "chunks.jsonl"
    kg_path = tmp_path / "kg.jsonl"
    write_profile(profile_path)
    write_chunks_jsonl([make_chunk()], chunks_path)
    write_kg_jsonl([make_triple()], kg_path)

    report = validate_kg_file(kg_path, chunks_path, profile_path)

    assert report["valid"]
    assert report["triples_total"] == 1


def test_write_kg_ttl_exports_reified_evidence(tmp_path: Path) -> None:
    ttl_path = tmp_path / "kg.ttl"

    path = write_kg_ttl([make_triple()], ttl_path)

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "KGTriple_t1" in text
    assert "Air flows over the wing and affects lift." in text
    assert "supportedByEvidence" in text


def test_write_kg_validation_reports(tmp_path: Path) -> None:
    report = {
        "valid": True,
        "kg_path": "data/kg/test.jsonl",
        "chunks_path": "data/chunks/test.jsonl",
        "profile_path": "configs/extraction_profile.yaml",
        "ontology_path": "data/ontology/curated/test.ttl",
        "triples_total": 1,
        "errors_total": 0,
        "errors": [],
    }

    json_path, md_path = write_kg_validation_reports(report, tmp_path)

    assert json_path.exists()
    assert md_path.exists()
    assert "KG Validation Report" in md_path.read_text(encoding="utf-8")


def test_write_kg_validation_reports_supports_report_name(tmp_path: Path) -> None:
    report = {
        "valid": True,
        "kg_path": "data/kg/test.jsonl",
        "chunks_path": "data/chunks/test.jsonl",
        "profile_path": "configs/extraction_profile.yaml",
        "ontology_path": "data/ontology/curated/test.ttl",
        "triples_total": 1,
        "errors_total": 0,
        "errors": [],
    }

    json_path, md_path = write_kg_validation_reports(
        report,
        tmp_path,
        report_name="structure_aware_kg_validation",
    )

    assert json_path.name == "structure_aware_kg_validation.json"
    assert md_path.name == "structure_aware_kg_validation.md"
