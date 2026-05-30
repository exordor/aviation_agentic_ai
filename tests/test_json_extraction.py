import pytest

from aviation_agentic_ai.utils.json_extraction import (
    JSONPayloadExtractionError,
    extract_json_object,
    extract_json_payload,
    parse_json_payload,
)


def test_extract_json_payload_handles_fenced_json_object() -> None:
    assert extract_json_payload('```json\n{"ok": true}\n```') == '{"ok": true}'
    assert parse_json_payload('```json\n{"ok": true}\n```') == {"ok": True}


def test_extract_json_payload_handles_fenced_json_array() -> None:
    assert extract_json_payload("```json\n[1, 2, 3]\n```") == "[1, 2, 3]"
    assert parse_json_payload("```json\n[1, 2, 3]\n```") == [1, 2, 3]


def test_extract_json_payload_handles_fenced_block_without_language() -> None:
    assert extract_json_payload('```\n{"ok": true}\n```') == '{"ok": true}'


def test_extract_json_payload_handles_bare_json() -> None:
    assert parse_json_payload('{"ok": true}') == {"ok": True}
    assert parse_json_payload("[1, 2]") == [1, 2]


def test_extract_json_payload_handles_json_embedded_in_prose() -> None:
    assert extract_json_object('The answer is {"ok": true}.') == {"ok": True}


def test_parse_json_payload_reports_malformed_json() -> None:
    with pytest.raises(JSONPayloadExtractionError, match="Invalid JSON payload"):
        parse_json_payload('{"ok": ')


def test_parse_json_payload_reports_empty_string() -> None:
    with pytest.raises(JSONPayloadExtractionError, match="No JSON payload"):
        parse_json_payload("")
    assert extract_json_payload("") == ""


def test_extract_json_payload_skips_invalid_brace_like_sections() -> None:
    text = "Ignore {not json} and use {\"ok\": true, \"items\": [1, 2]}."
    assert extract_json_payload(text) == '{"ok": true, "items": [1, 2]}'
