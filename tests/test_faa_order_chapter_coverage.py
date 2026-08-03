from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = (
    ROOT / "data/ontology/curated/faa_jo_7210_3ee_chapter_coverage_v1.json"
)
SEMANTIC_PATH = ROOT / "data/ontology/curated/atmonto_semantic_coverage_v1.json"
ONTOLOGY_PROFILE_PATH = (
    ROOT / "data/ontology/curated/faa_jo_7210_3ee_ontology_profile_v2.json"
)


def test_jo_7210_3ee_matrix_covers_every_chapter_and_appendix() -> None:
    matrix = json.loads(MATRIX_PATH.read_text())

    assert matrix["scope"]["part_count"] == 7
    assert matrix["scope"]["chapter_count"] == 21
    assert matrix["scope"]["appendix_count"] == 6
    assert [row["chapter"] for row in matrix["chapters"]] == list(range(1, 22))
    assert [row["appendix"] for row in matrix["appendices"]] == list(range(1, 7))
    assert matrix["source"]["effective_date"] == "2025-02-20"
    assert matrix["chapters"][17]["status"] == "active"
    assert matrix["chapters"][17]["active_sections"] == [
        f"18-{number}" for number in range(1, 27)
    ]


def test_jo_7210_3ee_matrix_references_only_known_semantic_terms() -> None:
    matrix = json.loads(MATRIX_PATH.read_text())
    semantic = json.loads(SEMANTIC_PATH.read_text())
    profile = json.loads(ONTOLOGY_PROFILE_PATH.read_text())
    prefixes = matrix["prefixes"]

    semantic_classes: set[str] = set()
    semantic_properties: set[str] = set()
    for term in semantic["terms"]:
        for prefix, namespace in prefixes.items():
            if term["iri"].startswith(namespace):
                value = f"{prefix}:{term['local_name']}"
                if term["kind"] == "class":
                    semantic_classes.add(value)
                else:
                    semantic_properties.add(value)
    profile_classes = {row["prefixed_name"] for row in profile["class_mappings"]}
    profile_properties = {
        row["prefixed_name"] for row in profile["property_mappings"]
    }

    entries = [*matrix["chapters"], *matrix["appendices"]]
    for entry in entries:
        assert entry["status"] in {"active", "planned", "unsupported"}
        for class_group in entry["classes"].values():
            for class_name in class_group:
                assert class_name in semantic_classes | profile_classes
        for signature in entry["property_signatures"]:
            assert signature["status"] in {"active", "planned", "unsupported"}
            assert signature["property"] in semantic_properties | profile_properties
            assert signature["domain"]
            assert signature["range"]
