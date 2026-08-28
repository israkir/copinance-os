"""Model-facing serialization for tool results: TOON/compact JSON with a real size budget.

Fixes defects shared by every provider's tool-calling loop (``openai.py``,
``gemini.py``, ``ollama.py``):

- ``json.dumps(..., indent=2)`` on every tool result sent back to the model.
  Indentation is pure overhead here — the model does not care about
  whitespace, only the token budget does.
- The existing 100-item truncation (``serialized_data[:100]``) was only ever
  applied to a *recorded* copy used for the returned/logged ``tool_calls_made``
  entry. The actual payload appended to the conversation as the tool result
  message used the raw, untruncated data. A single large options chain or XBRL
  statement table could consume the entire iteration budget on its own, and the
  truncation only ever fired for a bare top-level list — never for the large
  dict-shaped payloads (``get_options_chain``, ``get_sec_xbrl_statement_table``)
  that actually blow past reasonable size in practice.

**TOON tabularization** (default OFF — see ``toon_tabular_enabled``) applies
before compaction/truncation and, per the design doc's measurements, gets
further ahead than compaction alone (~72% vs ~32% token reduction on a
250-contract options chain) by declaring a uniform array's field names once
instead of repeating them per row. It is gated three ways, all deliberately
conservative until the Phase 4 eval A/B proves no accuracy regression per
provider:

1. ``COPINANCEOS_TOON_TABULAR_ENABLED`` env flag — off by default.
2. ``TOON_NEVER_TOOLS`` — an explicit denylist of tools whose result is a
   single nested object, not a table (``get_signal_study``,
   ``get_positioning_context``, ``get_market_regime_indicators``,
   ``get_macro_regime_indicators``, ``get_watchlist_context``,
   ``get_market_quote``), even if some sub-field of one of them happened to
   look tabular.
3. A structural eligibility gate (``_is_tabular_eligible``): only a list of
   >=8 uniform dict rows with >=3 columns tabularizes. Anything smaller, or
   non-uniform, stays plain JSON — TOON's own docs and independent
   benchmarking agree it can *lose* to JSON below that density.

This is a stopgap ahead of a real per-tool ``max_result_tokens`` budget and a
declarative ``ToolSpec.tabular_fields`` allowlist (see the "faster, more
reliable AI tool system" design doc, Phase 1 of the runtime rewrite). Until
that lands, tabularization is applied structurally (any eligible top-level
list, not a hand-maintained per-tool field name) rather than per-field, and one
flat character budget applies to whatever's left that's still too large,
keeping head+tail context (not just a head slice, so a date-ordered series
still shows its most recent entries) plus an explicit omitted count instead of
silent data loss.
"""

from __future__ import annotations

import json
import os
from typing import Any

from copinance_os.ai.llm.toon_encoding import encode_toon_table

# ~4k tokens at a ~4-chars/token rule of thumb — generous headroom for a single
# tool result before it starts crowding out everything else in the budget.
DEFAULT_MAX_RESULT_CHARS = 16_000

_LIST_MIN_SIZE_TO_TRUNCATE = 20

_MIN_ROWS_FOR_TABULAR = 8
_MIN_COLUMNS_FOR_TABULAR = 3

# Tools whose result is a single nested object (verdict/positioning/regime
# summary, a quote), never a table — excluded by name rather than relying
# solely on the structural gate, since e.g. a quote's nested `reference` block
# could coincidentally contain a short list.
TOON_NEVER_TOOLS: frozenset[str] = frozenset(
    {
        "get_signal_study",
        "get_positioning_context",
        "get_market_regime_indicators",
        "get_macro_regime_indicators",
        "get_watchlist_context",
        "get_market_quote",
    }
)


def toon_tabular_enabled() -> bool:
    raw = os.environ.get("COPINANCEOS_TOON_TABULAR_ENABLED", "")
    return raw.strip().lower() in ("1", "true", "yes")


def compact_json(obj: Any) -> str:
    """Dense JSON (no indentation) for a model-facing payload."""
    return json.dumps(obj, separators=(",", ":"), default=str)


def _is_tabular_eligible(rows: list[Any]) -> bool:
    if len(rows) < _MIN_ROWS_FOR_TABULAR:
        return False
    if not all(isinstance(r, dict) for r in rows):
        return False
    columns = {k for r in rows for k in r}
    return len(columns) >= _MIN_COLUMNS_FOR_TABULAR


def _maybe_tabularize(data: Any, tool_name: str) -> Any:
    if not toon_tabular_enabled() or tool_name in TOON_NEVER_TOOLS:
        return data

    if isinstance(data, list):
        if _is_tabular_eligible(data):
            return encode_toon_table(tool_name or "items", data)
        return data

    if isinstance(data, dict):
        out: dict[str, Any] | None = None
        for key, value in data.items():
            if isinstance(value, list) and _is_tabular_eligible(value):
                if out is None:
                    out = dict(data)
                out[key] = encode_toon_table(key, value)
        return out if out is not None else data

    return data


def _truncate_list(items: list[Any], *, head: int, tail: int) -> tuple[list[Any], int]:
    if len(items) <= head + tail:
        return items, 0
    kept = items[:head] + items[-tail:] if tail else items[:head]
    return kept, len(items) - len(kept)


def budget_tool_result(
    data: Any, *, tool_name: str = "", max_chars: int = DEFAULT_MAX_RESULT_CHARS
) -> Any:
    """Downsample ``data`` so its compact JSON stays near ``max_chars``.

    Tabularizes eligible arrays into TOON first (see module docstring; no-op
    unless ``COPINANCEOS_TOON_TABULAR_ENABLED`` is set), then, if still over
    budget:

    - A bare list truncates to a head+tail window with ``_truncated``/
      ``_total_items``/``_items_shown``/``_omitted`` markers, same shape as the
      old top-level-list truncation (so downstream consumers of that shape keep
      working) plus the ``_omitted`` count it was missing.
    - A dict truncates whichever top-level list-valued fields are large enough
      to matter (``calls``/``puts`` on an options chain, row lists on a
      statement table, filing lists, ...) — each gets its own
      ``_truncated_fields[key]`` entry rather than the whole dict being
      replaced or left untouched.
    - Anything else (a scalar, a TOON-encoded string, or a dict/list already
      under budget) passes through unchanged.
    """
    data = _maybe_tabularize(data, tool_name)

    if len(compact_json(data)) <= max_chars:
        return data

    if isinstance(data, list):
        kept, omitted = _truncate_list(data, head=60, tail=20)
        if omitted <= 0:
            return data
        return {
            "_truncated": True,
            "_total_items": len(data),
            "_items_shown": len(kept),
            "_omitted": omitted,
            "data": kept,
            "note": (
                f"Response truncated: showing {len(kept)} of {len(data)} items "
                "(first 60, last 20)."
            ),
        }

    if isinstance(data, dict):
        list_keys = [
            k
            for k, v in data.items()
            if isinstance(v, list) and len(v) > _LIST_MIN_SIZE_TO_TRUNCATE
        ]
        if not list_keys:
            return data
        out = dict(data)
        truncated_fields: dict[str, Any] = {}
        for key in list_keys:
            items = data[key]
            kept, omitted = _truncate_list(items, head=40, tail=10)
            if omitted <= 0:
                continue
            out[key] = kept
            truncated_fields[key] = {
                "total_items": len(items),
                "items_shown": len(kept),
                "omitted": omitted,
            }
        if truncated_fields:
            out["_truncated"] = True
            out["_truncated_fields"] = truncated_fields
        return out

    return data
