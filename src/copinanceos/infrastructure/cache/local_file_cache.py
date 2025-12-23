"""Local file-based cache backend implementation."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import structlog

from copinanceos.domain.ports.storage import CacheBackend, CacheEntry
from copinanceos.infrastructure.repositories.storage.factory import create_storage
from copinanceos.infrastructure.repositories.storage.file import JsonFileStorage

logger = structlog.get_logger(__name__)


class LocalFileCacheBackend(CacheBackend):
    """Local file-based cache backend.

    Stores cache entries as JSON files in a directory structure.
    """

    def __init__(self, cache_dir: Path | str | None = None) -> None:
        """Initialize local file cache backend.

        Args:
            cache_dir: Cache directory path. If None, uses same base path as storage (.copinance/cache).
        """
        if cache_dir is None:
            # Use same base path as storage (typically .copinance in current directory)
            storage = create_storage()
            if isinstance(storage, JsonFileStorage):
                base_path = storage._base_path
            else:
                base_path = Path(".copinance")
            cache_dir = base_path / "cache"
        elif isinstance(cache_dir, str):
            cache_dir = Path(cache_dir)

        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Initialized local file cache", cache_dir=str(self._cache_dir))

    def get_backend_name(self) -> str:
        """Get backend name."""
        return "local_file"

    def _get_cache_file_path(self, key: str) -> Path:
        """Get file path for cache key.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Create a safe filename from the key
        # Use hash to avoid filesystem issues with special characters
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self._cache_dir / f"{key_hash}.json"

    async def get(self, key: str) -> CacheEntry | None:
        """Get cached entry by key.

        Args:
            key: Cache key

        Returns:
            CacheEntry if found, None otherwise
        """
        cache_file = self._get_cache_file_path(key)
        if not cache_file.exists():
            return None

        try:
            with cache_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Parse cached_at as datetime
            cached_at_str = data.get("cached_at")
            if isinstance(cached_at_str, str):
                cached_at = datetime.fromisoformat(cached_at_str)
            else:
                cached_at = datetime.now(UTC)

            entry = CacheEntry(
                data=data.get("data"),
                cached_at=cached_at,
                tool_name=data.get("tool_name", ""),
                cache_key=data.get("cache_key", key),
                metadata=data.get("metadata", {}),
            )

            logger.debug("Cache hit", key=key, tool_name=entry.tool_name)
            return entry
        except Exception as e:
            logger.warning("Failed to read cache entry", key=key, error=str(e))
            return None

    async def set(self, key: str, entry: CacheEntry) -> None:
        """Store cache entry.

        Args:
            key: Cache key
            entry: Cache entry to store
        """
        cache_file = self._get_cache_file_path(key)
        try:
            data = {
                "data": entry.data,
                "cached_at": entry.cached_at.isoformat(),
                "tool_name": entry.tool_name,
                "cache_key": entry.cache_key,
                "metadata": entry.metadata,
            }

            with cache_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.debug("Cached entry", key=key, tool_name=entry.tool_name)
        except Exception as e:
            logger.error("Failed to write cache entry", key=key, error=str(e))
            raise

    async def delete(self, key: str) -> bool:
        """Delete cache entry.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted, False if not found
        """
        cache_file = self._get_cache_file_path(key)
        if cache_file.exists():
            try:
                cache_file.unlink()
                logger.debug("Deleted cache entry", key=key)
                return True
            except Exception as e:
                logger.warning("Failed to delete cache entry", key=key, error=str(e))
                return False
        return False

    async def clear(self, tool_name: str | None = None) -> int:
        """Clear cache entries.

        Args:
            tool_name: Optional tool name to clear only entries for that tool.
                      If None, clears all entries.

        Returns:
            Number of entries deleted
        """
        deleted_count = 0

        if tool_name:
            # Clear entries for specific tool
            for cache_file in self._cache_dir.glob("*.json"):
                try:
                    with cache_file.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("tool_name") == tool_name:
                            cache_file.unlink()
                            deleted_count += 1
                except Exception:
                    # Skip files that can't be read
                    continue
        else:
            # Clear all entries
            for cache_file in self._cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.warning(
                        "Failed to delete cache file", file=str(cache_file), error=str(e)
                    )

        logger.info("Cleared cache", tool_name=tool_name, deleted_count=deleted_count)
        return deleted_count

    async def exists(self, key: str) -> bool:
        """Check if cache entry exists.

        Args:
            key: Cache key

        Returns:
            True if entry exists, False otherwise
        """
        cache_file = self._get_cache_file_path(key)
        return cache_file.exists()
