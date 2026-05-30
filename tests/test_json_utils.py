import pytest

from aviation_agentic_ai.utils.json import extract_json_object, extract_json_payload


def test_extract_json_payload_handles_fenced_and_embedded_json() -> None:
    assert extract_json_payload('```json\n{"ok": true}\n```') == '{"ok": true}'
    assert extract_json_payload('before {"ok": true} after') == '{"ok": true}'


def test_extract_json_object_requires_object_payload() -> None:
    assert extract_json_object('The answer is {"ok": true}.') == {"ok": True}
    with pytest.raises(ValueError):
        extract_json_object("[1, 2, 3]")
