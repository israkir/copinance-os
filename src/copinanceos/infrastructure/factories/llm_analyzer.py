"""Factory for creating LLM analyzers."""

from copinanceos.domain.ports.analyzers import LLMAnalyzer
from copinanceos.infrastructure.analyzers.llm.llm import LLMAnalyzerImpl
from copinanceos.infrastructure.analyzers.llm.providers.factory import LLMProviderFactory
from copinanceos.infrastructure.config import get_settings


class LLMAnalyzerFactory:
    """Factory for creating LLM analyzer instances.

    This factory creates provider-agnostic analyzer instances using the generic
    LLMAnalyzerImpl class. For direct instantiation of provider-specific analyzers,
    use convenience classes like GeminiLLMAnalyzer.
    """

    @staticmethod
    def create(provider_name: str | None = None) -> LLMAnalyzer:
        """Create LLM analyzer for a specific provider.

        This method uses the generic LLMAnalyzerImpl class to maintain
        provider-agnostic behavior. For convenience classes like GeminiLLMAnalyzer,
        instantiate them directly.

        Args:
            provider_name: Name of the LLM provider. If None, uses default from settings.

        Returns:
            LLM analyzer instance (LLMAnalyzerImpl wrapping the provider)

        Example:
            ```python
            # Framework usage (provider-agnostic)
            analyzer = LLMAnalyzerFactory.create("gemini")

            # Direct usage (convenience)
            from copinanceos.infrastructure.analyzers import GeminiLLMAnalyzer
            analyzer = GeminiLLMAnalyzer(api_key="...")
            ```
        """
        settings = get_settings()
        if provider_name is None:
            provider_name = settings.llm_provider
        provider = LLMProviderFactory.create_provider(provider_name, settings)
        return LLMAnalyzerImpl(provider)

    @staticmethod
    def create_for_workflow(workflow_type: str) -> LLMAnalyzer:
        """Create LLM analyzer for a specific workflow type.

        Args:
            workflow_type: Type of workflow (e.g., "static", "agentic")

        Returns:
            LLM analyzer instance configured for the workflow
        """
        settings = get_settings()
        provider_name = LLMProviderFactory.get_provider_for_workflow(
            workflow_type, settings, default_provider=settings.llm_provider
        )
        return LLMAnalyzerFactory.create(provider_name)
