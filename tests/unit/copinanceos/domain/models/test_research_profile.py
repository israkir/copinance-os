"""Unit tests for ResearchProfile domain model."""

import pytest

from copinanceos.domain.models.research_profile import FinancialLiteracy, ResearchProfile


@pytest.mark.unit
class TestResearchProfileModel:
    """Test ResearchProfile domain model."""

    def test_create_profile(self) -> None:
        """Test creating a research profile."""
        profile = ResearchProfile(
            financial_literacy=FinancialLiteracy.INTERMEDIATE,
            display_name="Test Investor",
        )

        assert profile.financial_literacy == FinancialLiteracy.INTERMEDIATE
        assert profile.display_name == "Test Investor"
        assert isinstance(profile.preferences, dict)

    def test_profile_default_literacy(self) -> None:
        """Test profile with default literacy level."""
        profile = ResearchProfile()

        assert profile.financial_literacy == FinancialLiteracy.BEGINNER
