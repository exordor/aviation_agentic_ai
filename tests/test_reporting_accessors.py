from aviation_agentic_ai.reporting.accessors import nested_value


def test_nested_value_reads_existing_path() -> None:
    assert nested_value({"a": {"b": {"c": 3}}}, "a", "b", "c") == 3


def test_nested_value_returns_default_for_missing_key() -> None:
    assert nested_value({"a": {}}, "a", "missing", default=None) is None


def test_nested_value_returns_default_for_non_object_intermediate() -> None:
    assert nested_value({"a": "not-object"}, "a", "b", default="fallback") == "fallback"


def test_nested_value_uses_report_default() -> None:
    assert nested_value({}, "missing") == "TBD"
