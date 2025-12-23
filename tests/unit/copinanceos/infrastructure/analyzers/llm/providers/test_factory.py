"""Unit tests for LLM provider factory."""

from unittest.mock import MagicMock, patch

import pytest

from copinanceos.infrastructure.analyzers.llm.providers.factory import LLMProviderFactory
from copinanceos.infrastructure.analyzers.llm.providers.gemini import GeminiProvider
from copinanceos.infrastructure.analyzers.llm.providers.ollama import OllamaProvider
from copinanceos.infrastructure.config import Settings


def create_settings(**kwargs: str) -> Settings:
    """Create Settings instance without reading from environment."""
    defaults = {
        "llm_provider": "gemini",
        "gemini_api_key": None,
        "gemini_model": "gemini-pro",
        "ollama_base_url": "http://localhost:11434",
        "ollama_model": "llama2",
        "llm_temperature": 0.7,
        "llm_max_tokens": None,
        "workflow_llm_providers": None,
    }
    defaults.update(kwargs)
    return Settings.model_construct(**defaults)


@pytest.mark.unit
class TestLLMProviderFactory:
    """Test LLMProviderFactory class."""

    def test_create_provider_gemini(self) -> None:
        """Test creating Gemini provider."""
        settings = create_settings(gemini_api_key="test-key")
        provider = LLMProviderFactory.create_provider("gemini", settings)

        assert isinstance(provider, GeminiProvider)
        assert provider._api_key == "test-key"
        assert provider._model_name == "gemini-pro"

    def test_create_provider_gemini_with_override_kwargs(self) -> None:
        """Test creating Gemini provider with override kwargs."""
        settings = create_settings(gemini_api_key="default-key", gemini_model="default-model")
        provider = LLMProviderFactory.create_provider(
            "gemini", settings, api_key="override-key", model_name="override-model"
        )

        assert isinstance(provider, GeminiProvider)
        assert provider._api_key == "override-key"
        assert provider._model_name == "override-model"

    def test_create_provider_gemini_case_insensitive(self) -> None:
        """Test that provider name is case insensitive."""
        settings = create_settings()
        provider = LLMProviderFactory.create_provider("GEMINI", settings)

        assert isinstance(provider, GeminiProvider)

    @patch("copinanceos.infrastructure.analyzers.llm.providers.ollama.HTTPX_AVAILABLE", True)
    @patch("copinanceos.infrastructure.analyzers.llm.providers.ollama.httpx")
    def test_create_provider_ollama(self, mock_httpx: MagicMock) -> None:
        """Test creating Ollama provider."""
        mock_client = MagicMock()
        mock_httpx.AsyncClient = MagicMock(return_value=mock_client)
        settings = create_settings(ollama_base_url="http://custom:8080", ollama_model="mistral")
        provider = LLMProviderFactory.create_provider("ollama", settings)

        assert isinstance(provider, OllamaProvider)
        assert provider._base_url == "http://custom:8080"
        assert provider._model_name == "mistral"

    @patch("copinanceos.infrastructure.analyzers.llm.providers.ollama.HTTPX_AVAILABLE", True)
    @patch("copinanceos.infrastructure.analyzers.llm.providers.ollama.httpx")
    def test_create_provider_ollama_with_override_kwargs(self, mock_httpx: MagicMock) -> None:
        """Test creating Ollama provider with override kwargs."""
        mock_client = MagicMock()
        mock_httpx.AsyncClient = MagicMock(return_value=mock_client)
        settings = create_settings(
            ollama_base_url="http://default:11434", ollama_model="default-model"
        )
        provider = LLMProviderFactory.create_provider(
            "ollama", settings, base_url="http://override:8080", model_name="override-model"
        )

        assert isinstance(provider, OllamaProvider)
        assert provider._base_url == "http://override:8080"
        assert provider._model_name == "override-model"

    def test_create_provider_ollama_case_insensitive(self) -> None:
        """Test that provider name is case insensitive."""
        with patch(
            "copinanceos.infrastructure.analyzers.llm.providers.ollama.HTTPX_AVAILABLE", True
        ):
            with patch(
                "copinanceos.infrastructure.analyzers.llm.providers.ollama.httpx"
            ) as mock_httpx:
                mock_client = MagicMock()
                mock_httpx.AsyncClient = MagicMock(return_value=mock_client)
                settings = create_settings()
                provider = LLMProviderFactory.create_provider("OLLAMA", settings)

                assert isinstance(provider, OllamaProvider)

    def test_create_provider_openai_raises_error(self) -> None:
        """Test that creating OpenAI provider raises ValueError."""
        settings = create_settings()
        with pytest.raises(ValueError, match="OpenAI provider is not yet implemented"):
            LLMProviderFactory.create_provider("openai", settings)

    def test_create_provider_anthropic_raises_error(self) -> None:
        """Test that creating Anthropic provider raises ValueError."""
        settings = create_settings()
        with pytest.raises(ValueError, match="Anthropic provider is not yet implemented"):
            LLMProviderFactory.create_provider("anthropic", settings)

    def test_create_provider_unsupported_raises_error(self) -> None:
        """Test that creating unsupported provider raises ValueError."""
        settings = create_settings()
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            LLMProviderFactory.create_provider("unsupported", settings)

    def test_create_provider_uses_default_settings_when_none(self) -> None:
        """Test that create_provider uses get_settings when settings is None."""
        with patch(
            "copinanceos.infrastructure.analyzers.llm.providers.factory.get_settings"
        ) as mock_get_settings:
            mock_settings = create_settings(gemini_api_key="env-key")
            mock_get_settings.return_value = mock_settings

            provider = LLMProviderFactory.create_provider("gemini")

            assert isinstance(provider, GeminiProvider)
            mock_get_settings.assert_called_once()

    def test_parse_workflow_provider_mapping_valid(self) -> None:
        """Test parsing valid workflow:provider mapping."""
        mapping_str = "static:ollama,agentic:gemini,fundamentals:gemini"
        result = LLMProviderFactory.parse_workflow_provider_mapping(mapping_str)

        assert result == {
            "static": "ollama",
            "agentic": "gemini",
            "fundamentals": "gemini",
        }

    def test_parse_workflow_provider_mapping_with_spaces(self) -> None:
        """Test parsing mapping with spaces."""
        mapping_str = "static : ollama , agentic : gemini"
        result = LLMProviderFactory.parse_workflow_provider_mapping(mapping_str)

        assert result == {
            "static": "ollama",
            "agentic": "gemini",
        }

    def test_parse_workflow_provider_mapping_empty_string(self) -> None:
        """Test parsing empty mapping string."""
        result = LLMProviderFactory.parse_workflow_provider_mapping("")
        assert result == {}

    def test_parse_workflow_provider_mapping_none(self) -> None:
        """Test parsing None mapping."""
        result = LLMProviderFactory.parse_workflow_provider_mapping(None)
        assert result == {}

    def test_parse_workflow_provider_mapping_invalid_format(self) -> None:
        """Test parsing invalid mapping format (no colon)."""
        with patch(
            "copinanceos.infrastructure.analyzers.llm.providers.factory.logger"
        ) as mock_logger:
            result = LLMProviderFactory.parse_workflow_provider_mapping(
                "static-ollama,agentic:gemini"
            )

            # Should only include valid pairs
            assert result == {"agentic": "gemini"}
            # Should log warning for invalid pair
            assert mock_logger.warning.called

    def test_get_provider_for_workflow_with_mapping(self) -> None:
        """Test getting provider for workflow with mapping configured."""
        settings = create_settings(
            workflow_llm_providers="static:ollama,agentic:gemini",
            llm_provider="gemini",
        )
        result = LLMProviderFactory.get_provider_for_workflow("static", settings)

        assert result == "ollama"

    def test_get_provider_for_workflow_without_mapping(self) -> None:
        """Test getting provider for workflow without mapping."""
        settings = create_settings(llm_provider="gemini")
        result = LLMProviderFactory.get_provider_for_workflow("static", settings)

        assert result == "gemini"

    def test_get_provider_for_workflow_with_default_provider(self) -> None:
        """Test getting provider for workflow with default_provider parameter."""
        settings = create_settings(llm_provider="gemini")
        result = LLMProviderFactory.get_provider_for_workflow(
            "static", settings, default_provider="ollama"
        )

        assert result == "ollama"

    def test_get_provider_for_workflow_default_overrides_settings(self) -> None:
        """Test that default_provider parameter overrides settings.llm_provider."""
        settings = create_settings(llm_provider="gemini")
        result = LLMProviderFactory.get_provider_for_workflow(
            "unknown_workflow", settings, default_provider="ollama"
        )

        assert result == "ollama"

    def test_get_provider_for_workflow_uses_settings_when_none(self) -> None:
        """Test that get_provider_for_workflow uses get_settings when settings is None."""
        with patch(
            "copinanceos.infrastructure.analyzers.llm.providers.factory.get_settings"
        ) as mock_get_settings:
            mock_settings = create_settings(llm_provider="gemini")
            mock_get_settings.return_value = mock_settings

            result = LLMProviderFactory.get_provider_for_workflow("static")

            assert result == "gemini"
            mock_get_settings.assert_called_once()

    def test_get_provider_for_workflow_mapping_takes_precedence(self) -> None:
        """Test that workflow mapping takes precedence over default."""
        settings = create_settings(
            workflow_llm_providers="static:ollama",
            llm_provider="gemini",
        )
        result = LLMProviderFactory.get_provider_for_workflow(
            "static", settings, default_provider="gemini"
        )

        assert result == "ollama"
