"""Prompt manager for loading and formatting LLM prompts.

This module uses Python's importlib.resources for loading default prompts
from package data, with support for user overrides via config directory.
"""

import json
from importlib import resources
from pathlib import Path
from typing import Any, cast

import structlog

logger = structlog.get_logger(__name__)

# Package reference for loading default prompts
_PACKAGE = "copinanceos.infrastructure.analyzers.llm.resources"


class PromptManager:
    """Manages LLM prompt templates loaded from resource files.

    Prompts are stored as JSON files with system_prompt and user_prompt fields.
    Templates support variable substitution using {variable_name} syntax.

    The manager supports two sources for prompts:
    1. User overrides: Custom prompts in a user-configurable directory
    2. Package defaults: Default prompts bundled with the package

    User overrides take precedence over package defaults.
    """

    def __init__(
        self,
        resources_dir: Path | None = None,
        use_package_data: bool = True,
    ) -> None:
        """Initialize prompt manager.

        Args:
            resources_dir: Directory containing custom prompt resource files.
                          If None, checks for user prompts in default location,
                          then falls back to package data.
            use_package_data: If True, fall back to package data if custom
                            prompts not found. If False, only use custom directory.
        """
        self._custom_resources_dir = Path(resources_dir) if resources_dir else None
        self._use_package_data = use_package_data
        self._prompts_cache: dict[str, dict[str, str]] = {}

        # Determine default user prompts directory
        if self._custom_resources_dir is None:
            # Check for user prompts in .copinance/prompts/ (similar to storage pattern)
            user_prompts_dir = Path.home() / ".copinance" / "prompts"
            if user_prompts_dir.exists():
                self._custom_resources_dir = user_prompts_dir
                logger.info("Using user prompts directory", path=str(user_prompts_dir))

        if self._custom_resources_dir:
            logger.info(
                "Initialized prompt manager",
                custom_dir=str(self._custom_resources_dir),
                use_package_data=use_package_data,
            )
        else:
            logger.info(
                "Initialized prompt manager",
                source="package_data",
                use_package_data=use_package_data,
            )

    def _load_prompt_file(self, prompt_name: str) -> dict[str, str]:
        """Load a prompt file from resources.

        Tries custom directory first, then falls back to package data.

        Args:
            prompt_name: Name of the prompt file (without .json extension)

        Returns:
            Dictionary with 'system_prompt' and 'user_prompt' keys

        Raises:
            FileNotFoundError: If prompt file doesn't exist in any location
            ValueError: If prompt file is invalid
        """
        if prompt_name in self._prompts_cache:
            return self._prompts_cache[prompt_name]

        # Try custom directory first (user overrides)
        if self._custom_resources_dir:
            custom_file = self._custom_resources_dir / f"{prompt_name}.json"
            if custom_file.exists():
                try:
                    with open(custom_file, encoding="utf-8") as f:
                        prompt_data = cast(dict[str, str], json.load(f))
                    self._validate_prompt_data(prompt_data, prompt_name)
                    self._prompts_cache[prompt_name] = prompt_data
                    logger.debug("Loaded prompt from custom directory", prompt_name=prompt_name)
                    return prompt_data
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(
                        "Failed to load custom prompt, falling back to package data",
                        prompt_name=prompt_name,
                        error=str(e),
                    )

        # Fall back to package data
        if self._use_package_data:
            try:
                prompt_data = self._load_from_package(prompt_name)
                self._prompts_cache[prompt_name] = prompt_data
                logger.debug("Loaded prompt from package data", prompt_name=prompt_name)
                return prompt_data
            except FileNotFoundError:
                pass

        # If we get here, prompt wasn't found anywhere
        raise FileNotFoundError(
            f"Prompt file '{prompt_name}.json' not found. "
            f"Checked: {self._custom_resources_dir if self._custom_resources_dir else 'N/A'}, "
            f"package data: {self._use_package_data}"
        )

    def _load_from_package(self, prompt_name: str) -> dict[str, str]:
        """Load prompt from package data using importlib.resources.

        Uses the modern importlib.resources API (Python 3.9+).

        Args:
            prompt_name: Name of the prompt file (without .json extension)

        Returns:
            Dictionary with 'system_prompt' and 'user_prompt' keys

        Raises:
            FileNotFoundError: If prompt file doesn't exist in package
            ValueError: If prompt file is invalid
        """
        try:
            # Use importlib.resources.files() - modern API (Python 3.9+)
            resource_path = resources.files(_PACKAGE) / f"{prompt_name}.json"

            # as_file() converts Traversable to Path, handling both filesystem and zip imports
            with resources.as_file(resource_path) as prompt_file:
                with open(prompt_file, encoding="utf-8") as f:
                    prompt_data = cast(dict[str, str], json.load(f))

            self._validate_prompt_data(prompt_data, prompt_name)
            return prompt_data

        except (FileNotFoundError, ModuleNotFoundError, AttributeError) as e:
            raise FileNotFoundError(
                f"Prompt file '{prompt_name}.json' not found in package data"
            ) from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in package prompt file {prompt_name}.json: {e}") from e

    def _validate_prompt_data(self, prompt_data: dict[str, Any], prompt_name: str) -> None:
        """Validate prompt data structure.

        Args:
            prompt_data: The loaded prompt data
            prompt_name: Name of the prompt file (for error messages)

        Raises:
            ValueError: If prompt data is invalid
        """
        if not isinstance(prompt_data, dict):
            raise ValueError(f"Prompt file {prompt_name}.json must contain a JSON object")

        if "system_prompt" not in prompt_data or "user_prompt" not in prompt_data:
            raise ValueError(
                f"Prompt file {prompt_name}.json must contain 'system_prompt' and 'user_prompt' fields"
            )

    def get_prompt(
        self,
        prompt_name: str,
        **kwargs: Any,
    ) -> tuple[str, str]:
        """Get formatted prompt with variable substitution.

        Args:
            prompt_name: Name of the prompt file (without .json extension)
            **kwargs: Variables to substitute in the prompt template

        Returns:
            Tuple of (system_prompt, user_prompt) with variables substituted

        Example:
            ```python
            manager = PromptManager()
            system, user = manager.get_prompt(
                "agentic_workflow",
                question="What is the current price of AAPL?",
                tools_description="...",
                tool_examples="...",
                financial_literacy="intermediate",
            )
            ```
        """
        prompt_data = self._load_prompt_file(prompt_name)

        system_prompt = prompt_data["system_prompt"].format(**kwargs)
        user_prompt = prompt_data["user_prompt"].format(**kwargs)

        return system_prompt, user_prompt

    def get_system_prompt(self, prompt_name: str, **kwargs: Any) -> str:
        """Get only the system prompt.

        Args:
            prompt_name: Name of the prompt file
            **kwargs: Variables to substitute

        Returns:
            Formatted system prompt
        """
        prompt_data = self._load_prompt_file(prompt_name)
        return prompt_data["system_prompt"].format(**kwargs)

    def get_user_prompt(self, prompt_name: str, **kwargs: Any) -> str:
        """Get only the user prompt.

        Args:
            prompt_name: Name of the prompt file
            **kwargs: Variables to substitute

        Returns:
            Formatted user prompt
        """
        prompt_data = self._load_prompt_file(prompt_name)
        return prompt_data["user_prompt"].format(**kwargs)
