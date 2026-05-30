from pathlib import Path

from aviation_agentic_ai.reporting.io import (
    normalize_report_text,
    read_json_object,
    read_json_object_or_empty,
    read_json_object_or_none,
    write_json_report,
)


def test_reporting_json_helpers_preserve_missing_file_policies(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"

    assert read_json_object_or_empty(missing) == {}
    assert read_json_object_or_none(missing) is None


def test_reporting_json_helpers_preserve_non_object_policies(tmp_path: Path) -> None:
    path = tmp_path / "list.json"
    path.write_text("[1, 2]\n", encoding="utf-8")

    assert read_json_object_or_empty(path) == {}
    assert read_json_object_or_empty(path, wrap_non_object=True) == {"value": [1, 2]}
    assert read_json_object_or_none(path, wrap_non_object=True) == {"value": [1, 2]}
    assert read_json_object_or_none(path, wrap_non_object=False) is None


def test_reporting_json_helpers_raise_for_required_object(tmp_path: Path) -> None:
    path = tmp_path / "scalar.json"
    path.write_text('"not-object"\n', encoding="utf-8")

    try:
        read_json_object(path)
    except ValueError as exc:
        message = str(exc)
    else:  # pragma: no cover - assertion guard.
        raise AssertionError("Expected ValueError")

    assert "Expected object JSON report" in message
    assert "scalar.json" in message


def test_write_json_report_uses_stable_format(tmp_path: Path) -> None:
    path = write_json_report({"b": 2, "a": 1}, tmp_path / "nested" / "report.json")

    assert path.exists()
    assert path.read_text(encoding="utf-8") == '{\n  "a": 1,\n  "b": 2\n}\n'


def test_normalize_report_text_matches_existing_report_wrappers() -> None:
    assert normalize_report_text("  Lift\nAFFECTS   Drag  ") == "lift affects drag"
