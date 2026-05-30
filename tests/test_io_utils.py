import json
from pathlib import Path

from aviation_agentic_ai.utils.io import (
    JSONDocumentReadError,
    read_json_document,
    read_json_document_or_none,
    write_json_document,
)


def test_json_document_helpers_read_missing_object_and_list(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    assert read_json_document_or_none(missing) is None

    path = tmp_path / "payload.json"
    path.write_text("[1, 2]\n", encoding="utf-8")

    assert read_json_document(path) == [1, 2]
    assert read_json_document_or_none(path) == [1, 2]


def test_json_document_helpers_report_decode_errors_with_path(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text('{"value": ', encoding="utf-8")

    try:
        read_json_document(path)
    except JSONDocumentReadError as exc:
        message = str(exc)
        assert isinstance(exc, json.JSONDecodeError)
        assert "Invalid JSON document" in message
        assert "broken.json" in message
        assert "Expecting value" in message
    else:
        raise AssertionError("Malformed JSON should fail with JSONDocumentReadError")


def test_write_json_document_uses_stable_format_and_optional_order(tmp_path: Path) -> None:
    sorted_path = write_json_document({"b": 2, "a": 1}, tmp_path / "sorted.json")
    unsorted_path = write_json_document(
        {"b": 2, "a": 1},
        tmp_path / "unsorted.json",
        sort_keys=False,
    )

    assert sorted_path.read_text(encoding="utf-8") == '{\n  "a": 1,\n  "b": 2\n}\n'
    assert unsorted_path.read_text(encoding="utf-8") == '{\n  "b": 2,\n  "a": 1\n}\n'
