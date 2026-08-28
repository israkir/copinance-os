"""encode_toon_table: the tabular TOON encoder used behind COPINANCEOS_TOON_TABULAR_ENABLED."""

from __future__ import annotations

from copinance_os.ai.llm.toon_encoding import encode_toon_table


def test_header_declares_row_count_and_first_seen_column_order() -> None:
    rows = [{"strike": 100, "bid": 1.2}, {"strike": 105, "bid": 0.9}]
    out = encode_toon_table("calls", rows)
    lines = out.splitlines()
    assert lines[0] == "calls[2]{strike,bid}:"
    assert lines[1] == "  100,1.2"
    assert lines[2] == "  105,0.9"


def test_missing_column_renders_empty_cell_not_an_error() -> None:
    rows = [{"strike": 100, "bid": 1.2}, {"strike": 105}]
    out = encode_toon_table("calls", rows)
    assert out.splitlines()[2] == "  105,"


def test_value_with_comma_is_quoted_and_doubled_quotes_escaped() -> None:
    rows = [{"note": 'contains, a comma and a "quote"'}]
    out = encode_toon_table("rows", rows)
    assert out.splitlines()[1] == '  "contains, a comma and a ""quote"""'


def test_none_renders_as_empty_cell() -> None:
    rows = [{"a": None, "b": 1}]
    out = encode_toon_table("rows", rows)
    assert out.splitlines()[1] == "  ,1"


def test_bool_renders_lowercase() -> None:
    rows = [{"active": True}, {"active": False}]
    out = encode_toon_table("rows", rows)
    assert out.splitlines()[1] == "  true"
    assert out.splitlines()[2] == "  false"


def test_column_order_matches_first_appearance_across_rows() -> None:
    rows = [{"a": 1}, {"b": 2, "a": 1}, {"c": 3}]
    out = encode_toon_table("rows", rows)
    assert out.splitlines()[0] == "rows[3]{a,b,c}:"
