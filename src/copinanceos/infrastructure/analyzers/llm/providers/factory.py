"""LLM provider factory for creating providers from configuration."""

from typing import Any

import structlog

from copinanceos.infrastructure.analyzers.llm.providers.base import LLMProvider
from copinanceos.infrastructure.analyzers.llm.providers.gemini import GeminiProvider
from copinanceos.infrastructure.analyzers.llm.providers.ollama import OllamaProvider
from copinanceos.infrastructure.config import Settings, get_settings

logger = structlog.get_logger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM providers from configuration."""

    @staticmethod
    def create_provider(
        provider_name: str,
        settings: Settings | None = None,
        **override_kwargs: Any,
    ) -> LLMProvider:
        """Create an LLM provider from configuration.

        Args:
            provider_name: Name of the provider (e.g., "gemini", "ollama", "openai")
            settings: Settings instance. If None, will create a new one.
            **override_kwargs: Override any configuration values

        Returns:
            LLMProvider instance

        Raises:
            ValueError: If provider_name is not supported
        """
        if settings is None:
            settings = get_settings()

        provider_name_lower = provider_name.lower()

        if provider_name_lower == "gemini":
            return GeminiProvider(
                api_key=override_kwargs.get("api_key", settings.gemini_api_key),
                model_name=override_kwargs.get("model_name", settings.gemini_model),
                temperature=override_kwargs.get("temperature", settings.llm_temperature),
                max_output_tokens=override_kwargs.get("max_output_tokens", settings.llm_max_tokens),
            )

        elif provider_name_lower == "ollama":
            return OllamaProvider(
                base_url=override_kwargs.get("base_url", settings.ollama_base_url),
                model_name=override_kwargs.get("model_name", settings.ollama_model),
                temperature=override_kwargs.get("temperature", settings.llm_temperature),
                max_output_tokens=override_kwargs.get("max_output_tokens", settings.llm_max_tokens),
            )

        # TODO: Add OpenAI and Anthropic providers when implemented
        elif provider_name_lower == "openai":
            raise ValueError(
                "OpenAI provider is not yet implemented. "
                "Please use 'gemini' or 'ollama' for now."
            )
        elif provider_name_lower == "anthropic":
            raise ValueError(
                "Anthropic provider is not yet implemented. "
                "Please use 'gemini' or 'ollama' for now."
            )

        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Supported providers: gemini, ollama"
            )

    @staticmethod
    def parse_workflow_provider_mapping(
        mapping_str: str | None,
    ) -> dict[str, str]:
        """Parse workflow:provider mapping string.

        Args:
            mapping_str: Comma-separated string like "static:ollama,agentic:gemini"

        Returns:
            Dictionary mapping workflow_type -> provider_name
        """
        if not mapping_str:
            return {}

        mapping: dict[str, str] = {}
        for pair in mapping_str.split(","):
            pair = pair.strip()
            if ":" in pair:
                workflow_type, provider_name = pair.split(":", 1)
                mapping[workflow_type.strip()] = provider_name.strip()
            else:
                logger.warning(
                    "Invalid workflow:provider mapping format",
                    pair=pair,
                    expected_format="workflow_type:provider_name",
                )

        return mapping

    @staticmethod
    def get_provider_for_workflow(
        workflow_type: str,
        settings: Settings | None = None,
        default_provider: str | None = None,
    ) -> str:
        """Get the provider name for a specific workflow.

        Args:
            workflow_type: The workflow type (e.g., "static", "agentic", "fundamentals")
            settings: Settings instance. If None, will create a new one.
            default_provider: Default provider to use if no mapping is found

        Returns:
            Provider name to use for this workflow
        """
        if settings is None:
            settings = get_settings()

        # Parse workflow provider mapping
        workflow_mapping = LLMProviderFactory.parse_workflow_provider_mapping(
            settings.workflow_llm_providers
        )

        # Check if there's a specific mapping for this workflow
        if workflow_type in workflow_mapping:
            return workflow_mapping[workflow_type]

        # Fall back to default provider or global llm_provider setting
        return default_provider or settings.llm_provider
