"""Unit tests for prompt manager implementation."""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from copinanceos.infrastructure.analyzers.llm.resources.prompt_manager import PromptManager


@pytest.mark.unit
class TestPromptManager:
    """Test PromptManager."""

    def test_initialization_without_custom_dir(self) -> None:
        """Test initialization without custom directory."""
        with (
            patch(
                "copinanceos.infrastructure.analyzers.llm.resources.prompt_manager.logger"
            ) as mock_logger,
            patch("pathlib.Path.exists") as mock_exists,
        ):
            mock_exists.return_value = False
            manager = PromptManager()

            assert manager._custom_resources_dir is None
            assert manager._use_package_data is True
            assert manager._prompts_cache == {}
            mock_logger.info.assert_called_once()

    def test_initialization_with_custom_dir(self) -> None:
        """Test initialization with custom directory."""
        custom_dir = Path("/tmp/custom_prompts")
        with patch(
            "copinanceos.infrastructure.analyzers.llm.resources.prompt_manager.logger"
        ) as mock_logger:
            manager = PromptManager(resources_dir=custom_dir)

            assert manager._custom_resources_dir == custom_dir
            assert manager._use_package_data is True
            assert manager._prompts_cache == {}
            mock_logger.info.assert_called_once()

    def test_initialization_with_use_package_data_false(self) -> None:
        """Test initialization with use_package_data=False."""
        custom_dir = Path("/tmp/custom_prompts")
        manager = PromptManager(resources_dir=custom_dir, use_package_data=False)

        assert manager._custom_resources_dir == custom_dir
        assert manager._use_package_data is False

    def test_initialization_uses_user_prompts_dir_if_exists(self) -> None:
        """Test initialization uses user prompts directory if it exists."""
        with (
            patch("pathlib.Path.exists") as mock_exists,
            patch("pathlib.Path.home") as mock_home,
            patch(
                "copinanceos.infrastructure.analyzers.llm.resources.prompt_manager.logger"
            ) as mock_logger,
        ):
            mock_home.return_value = Path("/home/user")
            mock_exists.return_value = True

            manager = PromptManager()

            expected_dir = Path("/home/user/.copinance/prompts")
            assert manager._custom_resources_dir == expected_dir
            mock_logger.info.assert_called()

    def test_validate_prompt_data_valid(self) -> None:
        """Test _validate_prompt_data with valid data."""
        manager = PromptManager()
        prompt_data = {
            "system_prompt": "You are a helpful assistant.",
            "user_prompt": "Analyze this data: {data}",
        }

        # Should not raise
        manager._validate_prompt_data(prompt_data, "test_prompt")

    def test_validate_prompt_data_not_dict(self) -> None:
        """Test _validate_prompt_data with non-dict data."""
        manager = PromptManager()
        with pytest.raises(ValueError, match="must contain a JSON object"):
            manager._validate_prompt_data("not a dict", "test_prompt")

    def test_validate_prompt_data_missing_system_prompt(self) -> None:
        """Test _validate_prompt_data with missing system_prompt."""
        manager = PromptManager()
        prompt_data = {"user_prompt": "Test prompt"}
        with pytest.raises(
            ValueError, match="must contain 'system_prompt' and 'user_prompt' fields"
        ):
            manager._validate_prompt_data(prompt_data, "test_prompt")

    def test_validate_prompt_data_missing_user_prompt(self) -> None:
        """Test _validate_prompt_data with missing user_prompt."""
        manager = PromptManager()
        prompt_data = {"system_prompt": "Test prompt"}
        with pytest.raises(
            ValueError, match="must contain 'system_prompt' and 'user_prompt' fields"
        ):
            manager._validate_prompt_data(prompt_data, "test_prompt")

    def test_load_prompt_file_from_custom_dir(self, tmp_path: Path) -> None:
        """Test loading prompt from custom directory."""
        prompt_file = tmp_path / "test_prompt.json"
        prompt_data = {
            "system_prompt": "You are a helpful assistant.",
            "user_prompt": "Analyze: {data}",
        }
        prompt_file.write_text(json.dumps(prompt_data), encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path)
        result = manager._load_prompt_file("test_prompt")

        assert result == prompt_data
        assert "test_prompt" in manager._prompts_cache

    def test_load_prompt_file_caches_result(self, tmp_path: Path) -> None:
        """Test that loaded prompts are cached."""
        prompt_file = tmp_path / "test_prompt.json"
        prompt_data = {
            "system_prompt": "System",
            "user_prompt": "User",
        }
        prompt_file.write_text(json.dumps(prompt_data), encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path)

        # Load first time
        result1 = manager._load_prompt_file("test_prompt")

        # Delete file
        prompt_file.unlink()

        # Load second time - should use cache
        result2 = manager._load_prompt_file("test_prompt")

        assert result1 == result2
        assert result1 == prompt_data

    def test_load_prompt_file_invalid_json_in_custom_dir(self, tmp_path: Path) -> None:
        """Test loading prompt with invalid JSON from custom directory falls back to package."""
        prompt_file = tmp_path / "test_prompt.json"
        prompt_file.write_text("invalid json", encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path, use_package_data=True)

        with patch.object(manager, "_load_from_package") as mock_load_package:
            mock_load_package.return_value = {
                "system_prompt": "System",
                "user_prompt": "User",
            }
            result = manager._load_prompt_file("test_prompt")

            assert result["system_prompt"] == "System"
            mock_load_package.assert_called_once_with("test_prompt")

    def test_load_prompt_file_falls_back_to_package(self, tmp_path: Path) -> None:
        """Test loading prompt falls back to package data when not in custom dir."""
        manager = PromptManager(resources_dir=tmp_path, use_package_data=True)

        with patch.object(manager, "_load_from_package") as mock_load_package:
            mock_load_package.return_value = {
                "system_prompt": "System",
                "user_prompt": "User",
            }
            result = manager._load_prompt_file("test_prompt")

            assert result["system_prompt"] == "System"
            mock_load_package.assert_called_once_with("test_prompt")

    def test_load_prompt_file_not_found_anywhere(self, tmp_path: Path) -> None:
        """Test loading prompt when not found in custom dir or package."""
        manager = PromptManager(resources_dir=tmp_path, use_package_data=True)

        with patch.object(manager, "_load_from_package") as mock_load_package:
            mock_load_package.side_effect = FileNotFoundError("Not found")

            with pytest.raises(FileNotFoundError, match="not found"):
                manager._load_prompt_file("nonexistent_prompt")

    def test_load_prompt_file_not_found_with_use_package_data_false(self, tmp_path: Path) -> None:
        """Test loading prompt when use_package_data=False and file not in custom dir."""
        manager = PromptManager(resources_dir=tmp_path, use_package_data=False)

        with pytest.raises(FileNotFoundError, match="not found"):
            manager._load_prompt_file("nonexistent_prompt")

    def test_load_from_package_success(self) -> None:
        """Test loading prompt from package data."""
        manager = PromptManager()

        with (
            patch("importlib.resources.files") as mock_files,
            patch("importlib.resources.as_file") as mock_as_file,
        ):
            mock_resource_path = MagicMock()
            mock_files.return_value = mock_resource_path
            mock_resource_path.__truediv__.return_value = mock_resource_path

            mock_file_path = MagicMock()
            mock_file_path.__enter__ = Mock(return_value=Path("/tmp/test.json"))
            mock_file_path.__exit__ = Mock(return_value=None)
            mock_as_file.return_value = mock_file_path

            prompt_data = {
                "system_prompt": "System",
                "user_prompt": "User",
            }

            with patch("builtins.open", mock_open(read_data=json.dumps(prompt_data))):
                result = manager._load_from_package("test_prompt")

            assert result == prompt_data

    def test_load_from_package_file_not_found(self) -> None:
        """Test loading prompt from package when file doesn't exist."""
        manager = PromptManager()

        with patch("importlib.resources.files") as mock_files:
            mock_files.side_effect = FileNotFoundError("Not found")

            with pytest.raises(FileNotFoundError, match="not found in package data"):
                manager._load_from_package("nonexistent_prompt")

    def test_load_from_package_invalid_json(self) -> None:
        """Test loading prompt from package with invalid JSON."""
        manager = PromptManager()

        with (
            patch("importlib.resources.files") as mock_files,
            patch("importlib.resources.as_file") as mock_as_file,
        ):
            mock_resource_path = MagicMock()
            mock_files.return_value = mock_resource_path
            mock_resource_path.__truediv__.return_value = mock_resource_path

            mock_file_path = MagicMock()
            mock_file_path.__enter__ = Mock(return_value=Path("/tmp/test.json"))
            mock_file_path.__exit__ = Mock(return_value=None)
            mock_as_file.return_value = mock_file_path

            with patch("builtins.open", mock_open(read_data="invalid json")):
                with pytest.raises(ValueError, match="Invalid JSON"):
                    manager._load_from_package("test_prompt")

    def test_get_prompt_with_variables(self, tmp_path: Path) -> None:
        """Test get_prompt with variable substitution."""
        prompt_file = tmp_path / "test_prompt.json"
        prompt_data = {
            "system_prompt": "You are analyzing {type}.",
            "user_prompt": "Analyze this: {data}",
        }
        prompt_file.write_text(json.dumps(prompt_data), encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path)
        system, user = manager.get_prompt("test_prompt", type="SEC filing", data="10-K text")

        assert system == "You are analyzing SEC filing."
        assert user == "Analyze this: 10-K text"

    def test_get_prompt_without_variables(self, tmp_path: Path) -> None:
        """Test get_prompt without variables."""
        prompt_file = tmp_path / "test_prompt.json"
        prompt_data = {
            "system_prompt": "You are a helpful assistant.",
            "user_prompt": "Analyze this data.",
        }
        prompt_file.write_text(json.dumps(prompt_data), encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path)
        system, user = manager.get_prompt("test_prompt")

        assert system == "You are a helpful assistant."
        assert user == "Analyze this data."

    def test_get_prompt_missing_variable(self, tmp_path: Path) -> None:
        """Test get_prompt with missing variable raises KeyError."""
        prompt_file = tmp_path / "test_prompt.json"
        prompt_data = {
            "system_prompt": "You are analyzing {type}.",
            "user_prompt": "Analyze this: {data}",
        }
        prompt_file.write_text(json.dumps(prompt_data), encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path)
        with pytest.raises(KeyError):
            manager.get_prompt("test_prompt", type="SEC filing")  # Missing 'data'

    def test_get_system_prompt(self, tmp_path: Path) -> None:
        """Test get_system_prompt."""
        prompt_file = tmp_path / "test_prompt.json"
        prompt_data = {
            "system_prompt": "You are analyzing {type}.",
            "user_prompt": "Analyze this: {data}",
        }
        prompt_file.write_text(json.dumps(prompt_data), encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path)
        system = manager.get_system_prompt("test_prompt", type="SEC filing")

        assert system == "You are analyzing SEC filing."

    def test_get_user_prompt(self, tmp_path: Path) -> None:
        """Test get_user_prompt."""
        prompt_file = tmp_path / "test_prompt.json"
        prompt_data = {
            "system_prompt": "You are analyzing {type}.",
            "user_prompt": "Analyze this: {data}",
        }
        prompt_file.write_text(json.dumps(prompt_data), encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path)
        user = manager.get_user_prompt("test_prompt", data="10-K text")

        assert user == "Analyze this: 10-K text"

    def test_get_prompt_custom_dir_takes_precedence(self, tmp_path: Path) -> None:
        """Test that custom directory prompts take precedence over package data."""
        # Create custom prompt
        custom_file = tmp_path / "test_prompt.json"
        custom_data = {
            "system_prompt": "Custom system",
            "user_prompt": "Custom user",
        }
        custom_file.write_text(json.dumps(custom_data), encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path, use_package_data=True)

        with patch.object(manager, "_load_from_package") as mock_load_package:
            result = manager._load_prompt_file("test_prompt")

            assert result == custom_data
            # Should not call package loader
            mock_load_package.assert_not_called()

    def test_load_prompt_file_handles_module_not_found_error(self, tmp_path: Path) -> None:
        """Test that ModuleNotFoundError is handled when loading from package."""
        manager = PromptManager(resources_dir=tmp_path, use_package_data=True)

        with patch.object(manager, "_load_from_package") as mock_load_package:
            # _load_from_package converts ModuleNotFoundError to FileNotFoundError
            mock_load_package.side_effect = FileNotFoundError("not found in package data")

            with pytest.raises(FileNotFoundError):
                manager._load_prompt_file("test_prompt")

    def test_load_prompt_file_handles_attribute_error(self, tmp_path: Path) -> None:
        """Test that AttributeError is handled when loading from package."""
        manager = PromptManager(resources_dir=tmp_path, use_package_data=True)

        with patch.object(manager, "_load_from_package") as mock_load_package:
            # _load_from_package converts AttributeError to FileNotFoundError
            mock_load_package.side_effect = FileNotFoundError("not found in package data")

            with pytest.raises(FileNotFoundError):
                manager._load_prompt_file("test_prompt")

    def test_get_prompt_with_special_characters(self, tmp_path: Path) -> None:
        """Test get_prompt with special characters in variables."""
        prompt_file = tmp_path / "test_prompt.json"
        prompt_data = {
            "system_prompt": "System: {text}",
            "user_prompt": "User: {text}",
        }
        prompt_file.write_text(json.dumps(prompt_data), encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path)
        system, user = manager.get_prompt("test_prompt", text="Special: {braces} & <tags>")

        assert system == "System: Special: {braces} & <tags>"
        assert user == "User: Special: {braces} & <tags>"

    def test_get_prompt_with_empty_strings(self, tmp_path: Path) -> None:
        """Test get_prompt with empty string variables."""
        prompt_file = tmp_path / "test_prompt.json"
        prompt_data = {
            "system_prompt": "System: {text}",
            "user_prompt": "User: {text}",
        }
        prompt_file.write_text(json.dumps(prompt_data), encoding="utf-8")

        manager = PromptManager(resources_dir=tmp_path)
        system, user = manager.get_prompt("test_prompt", text="")

        assert system == "System: "
        assert user == "User: "

    def test_load_from_package_handles_module_not_found(self) -> None:
        """Test _load_from_package handles ModuleNotFoundError."""
        manager = PromptManager()

        with patch("importlib.resources.files") as mock_files:
            mock_files.side_effect = ModuleNotFoundError("Module not found")

            with pytest.raises(FileNotFoundError, match="not found in package data"):
                manager._load_from_package("test_prompt")

    def test_load_from_package_handles_attribute_error(self) -> None:
        """Test _load_from_package handles AttributeError."""
        manager = PromptManager()

        with patch("importlib.resources.files") as mock_files:
            mock_files.side_effect = AttributeError("Attribute error")

            with pytest.raises(FileNotFoundError, match="not found in package data"):
                manager._load_from_package("test_prompt")

    def test_load_from_package_handles_file_not_found(self) -> None:
        """Test _load_from_package handles FileNotFoundError."""
        manager = PromptManager()

        with (
            patch("importlib.resources.files") as mock_files,
            patch("importlib.resources.as_file") as mock_as_file,
        ):
            mock_resource_path = MagicMock()
            mock_files.return_value = mock_resource_path
            mock_resource_path.__truediv__.return_value = mock_resource_path

            mock_file_path = MagicMock()
            mock_file_path.__enter__ = Mock(side_effect=FileNotFoundError("File not found"))
            mock_as_file.return_value = mock_file_path

            with pytest.raises(FileNotFoundError, match="not found in package data"):
                manager._load_from_package("test_prompt")
