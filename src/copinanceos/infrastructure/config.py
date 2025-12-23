"""Configuration management using pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="COPINANCEOS_",
        case_sensitive=False,
    )

    # Application
    app_name: str = Field(default="Copinance OS", description="Application name")
    environment: str = Field(
        default="development", description="Environment (development, staging, production)"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or console)")

    # Workflow settings
    default_workflow_timeout: int = Field(
        default=300, description="Default workflow timeout in seconds"
    )
    enable_agentic_workflows: bool = Field(default=True, description="Enable agentic AI workflows")

    # LLM settings
    # Default/fallback provider (for backward compatibility)
    llm_provider: str = Field(
        default="gemini",
        description="Default LLM provider to use (gemini, openai, anthropic, ollama, etc.)",
    )

    # Gemini configuration
    gemini_api_key: str | None = Field(default=None, description="Google Gemini API key")
    gemini_model: str = Field(
        default="gemini-1.5-pro",
        description="Gemini model to use (e.g., gemini-1.5-pro, gemini-1.5-flash, gemini-pro)",
    )

    # OpenAI configuration
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(
        default="gpt-4", description="OpenAI model to use (e.g., gpt-4, gpt-3.5-turbo)"
    )
    openai_base_url: str | None = Field(
        default=None, description="OpenAI API base URL (for custom endpoints or local proxies)"
    )

    # Anthropic configuration
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-3-opus-20240229", description="Anthropic model to use"
    )

    # Local LLM configuration (Ollama, vLLM, etc.)
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama API base URL"
    )
    ollama_model: str = Field(
        default="llama2", description="Ollama model to use (e.g., llama2, mistral, codellama)"
    )

    # Per-workflow LLM provider mapping (format: "workflow_type:provider_name")
    # Example: "static:ollama,agentic:gemini,fundamentals:openai"
    workflow_llm_providers: str | None = Field(
        default=None,
        description="Comma-separated workflow:provider mappings (e.g., 'static:ollama,agentic:gemini')",
    )

    # Default LLM parameters
    llm_temperature: float = Field(
        default=0.7, description="Default temperature for LLM generation (0.0 to 1.0)"
    )
    llm_max_tokens: int | None = Field(
        default=None, description="Default maximum tokens for LLM generation"
    )

    # Storage configuration
    storage_type: str = Field(
        default="file",
        description="Storage backend type (file, memory). File storage persists data, memory storage is ephemeral.",
    )
    storage_path: str = Field(
        default=".copinance",
        description="Base path for file storage backend. Only used when storage_type is 'file'.",
    )


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()
