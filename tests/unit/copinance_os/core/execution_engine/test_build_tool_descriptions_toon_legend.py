"""_build_tool_descriptions: the TOON format legend only appears when the
COPINANCEOS_TOON_TABULAR_ENABLED flag is set — Gemini's only source of tool
docs is this prose (see tool_result_serialization.py), so an unconditional
legend would waste tokens on every provider while TOON stays off by default."""

from __future__ import annotations

import pytest

from copinance_os.core.execution_engine.question_driven_analysis import (
    QuestionDrivenAnalysisExecutor,
)
from copinance_os.core.pipeline.tools.context_tools import GetCurrentDateTool


def _executor() -> QuestionDrivenAnalysisExecutor:
    return QuestionDrivenAnalysisExecutor()


def test_no_toon_legend_when_flag_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("COPINANCEOS_TOON_TABULAR_ENABLED", raising=False)
    tools_description, _examples = _executor()._build_tool_descriptions(
        [GetCurrentDateTool()], symbol="AAPL", current_date="2026-01-01"
    )
    assert "TOON" not in tools_description


def test_toon_legend_present_when_flag_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COPINANCEOS_TOON_TABULAR_ENABLED", "true")
    tools_description, _examples = _executor()._build_tool_descriptions(
        [GetCurrentDateTool()], symbol="AAPL", current_date="2026-01-01"
    )
    assert "TOON" in tools_description
    assert "never write TOON yourself" in tools_description
