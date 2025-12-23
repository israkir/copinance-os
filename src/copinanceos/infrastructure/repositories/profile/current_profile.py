"""Current profile state management - tracks which profile is active."""

import json
from pathlib import Path
from uuid import UUID

from copinanceos.infrastructure.repositories.storage.factory import create_storage
from copinanceos.infrastructure.repositories.storage.file import JsonFileStorage


def _get_config_path() -> Path:
    """Get the path to the config file."""
    # Use same base path as storage
    storage = create_storage()
    # Access _base_path which exists on JsonFileStorage implementation
    if isinstance(storage, JsonFileStorage):
        base_path = storage._base_path
    else:
        base_path = Path(".copinance")
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path / "config.json"


class CurrentProfile:
    """Manages the currently active profile state."""

    def get_current_profile_id(self) -> UUID | None:
        """Get the current profile ID.

        Returns:
            Current profile ID if set, None otherwise.
        """
        config_file = _get_config_path()
        if not config_file.exists():
            return None

        try:
            with open(config_file) as f:
                config = json.load(f)
                current_id = config.get("current_profile_id")
                if current_id:
                    return UUID(current_id)
        except (json.JSONDecodeError, ValueError, KeyError):
            return None

        return None

    def set_current_profile_id(self, profile_id: UUID | None) -> None:
        """Set the current profile ID.

        Args:
            profile_id: Profile ID to set as current, or None to clear.
        """
        config_file = _get_config_path()
        config = {}
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
            except (json.JSONDecodeError, ValueError):
                config = {}

        if profile_id is None:
            config.pop("current_profile_id", None)
        else:
            config["current_profile_id"] = str(profile_id)

        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
