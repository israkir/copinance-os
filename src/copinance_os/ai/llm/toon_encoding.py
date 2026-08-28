"""Minimal TOON tabular encoder for model-facing tool results.

TOON (github.com/toon-format/toon-python) declares a uniform array's field names
once, then rows as bare delimited values — for a rectangular payload (an options
chain, a bar series, a filing list) that consistently beats both `indent=2` JSON
and compact JSON, and edges out an ad-hoc ``{columns, rows}`` JSON shape too
(measured ~72% vs ~71% token reduction on a 250-contract options chain — see the
"faster, more reliable AI tool system" design doc's TOON assessment). Most of the
win is declaring field names once; TOON's syntax adds a smaller final edge.

This is a from-scratch ~40-line encoder, not a dependency on ``toon-python``: we
only ever need to *encode* (tool arguments stay native JSON-schema function
calling; the model is never asked to emit TOON), so pulling in a <1-year-old
package for one function isn't worth it. Revisit if decoding is ever needed.

Independent benchmarking found TOON's structural comprehension is
model-dependent and can rank *below* plain JSON on non-uniform/nested data — see
``tool_result_serialization.py`` for the eligibility gate (uniform rows only,
row/column thresholds, an explicit tool denylist) and the ``COPINANCEOS_TOON_``
env flags that keep this off by default pending the Phase 4 eval A/B.
"""

from __future__ import annotations

from typing import Any


def _toon_scalar(value: Any) -> str:
    """Render one cell. Quoted (CSV-style, `"` doubled) only when the bare form
    would be ambiguous — a delimiter, quote, newline, or the TOON `:` header
    character inside the value, or leading/trailing whitespace."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text != text.strip() or any(ch in text for ch in (",", '"', "\n", ":", "{", "}")):
        return '"' + text.replace('"', '""') + '"'
    return text


def encode_toon_table(name: str, rows: list[dict[str, Any]]) -> str:
    """Encode ``rows`` (uniform dicts) as one TOON table block.

    Column order is first-seen across rows (not alphabetical) so it reads like
    the source data. A row missing a column renders an empty cell rather than
    raising — real tool payloads have optional per-row fields (e.g. missing
    greeks on a far-dated option).
    """
    columns: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                columns.append(key)

    lines = [f"{name}[{len(rows)}]{{{','.join(columns)}}}:"]
    for row in rows:
        lines.append("  " + ",".join(_toon_scalar(row.get(col)) for col in columns))
    return "\n".join(lines)
