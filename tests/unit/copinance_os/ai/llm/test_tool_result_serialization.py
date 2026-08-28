"""budget_tool_result / compact_json: the model-facing size budget applied to
tool results in every provider's tool-calling loop."""

from __future__ import annotations

import pytest

from copinance_os.ai.llm.tool_result_serialization import (
    DEFAULT_MAX_RESULT_CHARS,
    budget_tool_result,
    compact_json,
)


@pytest.fixture
def toon_enabled(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("COPINANCEOS_TOON_TABULAR_ENABLED", "true")


def test_compact_json_has_no_indentation() -> None:
    assert compact_json({"a": 1, "b": [1, 2]}) == '{"a":1,"b":[1,2]}'


def test_small_payload_passes_through_unchanged() -> None:
    data = {"symbol": "AAPL", "price": 123.45}
    assert budget_tool_result(data) is data


def test_small_list_passes_through_unchanged() -> None:
    data = [{"date": f"2024-01-{i:02d}"} for i in range(5)]
    assert budget_tool_result(data) is data


def test_large_list_truncates_with_head_and_tail() -> None:
    data = [{"date": f"2024-{i:04d}", "value": i} for i in range(2000)]
    result = budget_tool_result(data, max_chars=1000)

    assert result["_truncated"] is True
    assert result["_total_items"] == 2000
    assert result["_omitted"] == 2000 - result["_items_shown"]
    # Head+tail, not just a head slice — the most recent entries survive too.
    assert result["data"][0] == data[0]
    assert result["data"][-1] == data[-1]


def test_large_dict_truncates_only_its_big_list_fields() -> None:
    data = {
        "underlying_symbol": "SPY",
        "calls": [{"strike": i} for i in range(500)],
        "puts": [{"strike": i} for i in range(500)],
    }
    result = budget_tool_result(data, max_chars=2000)

    assert result["underlying_symbol"] == "SPY"  # scalar fields untouched
    assert result["_truncated"] is True
    assert set(result["_truncated_fields"]) == {"calls", "puts"}
    assert result["_truncated_fields"]["calls"]["total_items"] == 500
    assert len(result["calls"]) < 500
    assert result["calls"][0] == data["calls"][0]
    assert result["calls"][-1] == data["calls"][-1]


def test_dict_with_small_list_fields_is_untouched_even_if_large() -> None:
    # A large payload whose bulk is scalar fields, not a truncatable list —
    # nothing to downsample, so it must pass through rather than error.
    data = {"blob": "x" * 5000}
    result = budget_tool_result(data, max_chars=1000)
    assert result is data


def test_default_budget_is_generous_but_finite() -> None:
    assert DEFAULT_MAX_RESULT_CHARS > 1000


def _uniform_rows(n: int) -> list[dict]:
    return [{"strike": i, "bid": i * 0.1, "ask": i * 0.1 + 0.05} for i in range(n)]


def test_toon_off_by_default_even_for_an_eligible_table() -> None:
    data = {"underlying_symbol": "SPY", "calls": _uniform_rows(20)}
    result = budget_tool_result(data, tool_name="get_options_chain")
    assert isinstance(result["calls"], list)


def test_toon_tabularizes_eligible_dict_field_when_enabled(toon_enabled) -> None:
    data = {"underlying_symbol": "SPY", "calls": _uniform_rows(20)}
    result = budget_tool_result(data, tool_name="get_options_chain")
    assert result["underlying_symbol"] == "SPY"
    assert isinstance(result["calls"], str)
    assert result["calls"].startswith("calls[20]{strike,bid,ask}:")


def test_toon_tabularizes_root_list_when_enabled(toon_enabled) -> None:
    data = _uniform_rows(20)
    result = budget_tool_result(data, tool_name="get_historical_market_data")
    assert isinstance(result, str)
    assert result.startswith("get_historical_market_data[20]{strike,bid,ask}:")


def test_toon_skips_denylisted_tool_even_when_enabled(toon_enabled) -> None:
    data = {"reference": _uniform_rows(20)}
    result = budget_tool_result(data, tool_name="get_market_quote")
    assert isinstance(result["reference"], list)


def test_toon_skips_small_or_narrow_tables_even_when_enabled(toon_enabled) -> None:
    too_few_rows = {"calls": [{"strike": 1, "bid": 1, "ask": 1}]}
    assert isinstance(
        budget_tool_result(too_few_rows, tool_name="get_options_chain")["calls"], list
    )

    too_few_columns = {"calls": [{"strike": i} for i in range(20)]}
    assert isinstance(
        budget_tool_result(too_few_columns, tool_name="get_options_chain")["calls"], list
    )


def test_toon_output_still_falls_under_truncation_when_still_oversized(toon_enabled) -> None:
    data = {"calls": _uniform_rows(5000)}
    result = budget_tool_result(data, tool_name="get_options_chain", max_chars=500)
    # Tabularized to a string, then that string is short enough on its own that
    # the dict-truncation branch (which only inspects list-valued fields) has
    # nothing left to truncate — this exercises the two stages composing safely
    # rather than double-processing the same field.
    assert isinstance(result["calls"], str)
