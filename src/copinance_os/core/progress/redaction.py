"""Truncate and stringify tool args/results for progress streams (not full payloads)."""

from __future__ import annotations

import json
from typing import Any

_DEFAULT_MAX_CHARS = 512
_ERROR_MAX_CHARS = 256


def summarize_for_tool_args(data: dict[str, Any], *, max_chars: int = _DEFAULT_MAX_CHARS) -> str:
    """Serialise tool arguments to a single bounded string for UI (no secrets guarantee)."""
    try:
        s = json.dumps(data, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        s = repr(data)
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 3] + "..."


def summarize_tool_result(
    success: bool,
    data: Any | None,
    error: str | None,
    *,
    max_chars: int = _DEFAULT_MAX_CHARS,
) -> str:
    """Short summary of tool outcome for progress streams."""
    if not success and error:
        err = error if len(error) <= _ERROR_MAX_CHARS else error[: _ERROR_MAX_CHARS - 3] + "..."
        return f"error: {err}"
    if data is None:
        return "ok (no data)"
    try:
        s = json.dumps(data, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        s = repr(data)
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 3] + "..."
