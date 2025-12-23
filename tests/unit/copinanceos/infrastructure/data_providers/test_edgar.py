"""Unit tests for EDGAR data provider implementation."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from copinanceos.infrastructure.data_providers.edgar import EdgarFundamentalProvider


@pytest.mark.unit
class TestEdgarFundamentalProvider:
    """Test EdgarFundamentalProvider."""

    def test_initialization(self) -> None:
        """Test provider initialization."""
        provider = EdgarFundamentalProvider()
        assert provider.base_url == "https://data.sec.gov"
        assert provider.user_agent is not None
        assert provider.rate_limit_delay == 0.1

    def test_initialization_with_custom_params(self) -> None:
        """Test provider initialization with custom parameters."""
        provider = EdgarFundamentalProvider(user_agent="custom/1.0", rate_limit_delay=0.5)
        assert provider.user_agent == "custom/1.0"
        assert provider.rate_limit_delay == 0.5

    def test_get_provider_name(self) -> None:
        """Test getting provider name."""
        provider = EdgarFundamentalProvider()
        assert provider.get_provider_name() == "edgar"

    @pytest.mark.asyncio
    async def test_is_available_success(self) -> None:
        """Test is_available returns True when EDGAR is accessible."""
        with patch("copinanceos.infrastructure.data_providers.edgar.logger"):
            provider = EdgarFundamentalProvider()
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            provider._client = mock_client

            result = await provider.is_available()

            assert result is True
            mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_available_failure(self) -> None:
        """Test is_available returns False when EDGAR is not accessible."""
        with patch("copinanceos.infrastructure.data_providers.edgar.logger"):
            provider = EdgarFundamentalProvider()
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Connection error"))
            provider._client = mock_client

            result = await provider.is_available()

            assert result is False

    @pytest.mark.asyncio
    async def test_get_client_creates_client(self) -> None:
        """Test that _get_client creates HTTP client."""
        provider = EdgarFundamentalProvider()
        provider._client = None

        with patch(
            "copinanceos.infrastructure.data_providers.edgar.httpx.AsyncClient"
        ) as mock_client:
            mock_client_instance = MagicMock()
            mock_client.return_value = mock_client_instance

            result = await provider._get_client()

            assert result == mock_client_instance
            mock_client.assert_called_once()
            assert "User-Agent" in mock_client.call_args[1]["headers"]

    @pytest.mark.asyncio
    async def test_get_client_reuses_existing_client(self) -> None:
        """Test that _get_client reuses existing client."""
        provider = EdgarFundamentalProvider()
        existing_client = MagicMock()
        provider._client = existing_client

        result = await provider._get_client()

        assert result == existing_client
