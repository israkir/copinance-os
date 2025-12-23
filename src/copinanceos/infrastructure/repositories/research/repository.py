"""Research repository implementation."""

from pathlib import Path
from uuid import UUID

from copinanceos.domain.models.research import Research
from copinanceos.domain.ports.repositories import ResearchRepository
from copinanceos.domain.ports.storage import Storage
from copinanceos.infrastructure.repositories.storage.factory import create_storage


class ResearchRepositoryImpl(ResearchRepository):
    """Implementation of ResearchRepository.

    This repository uses the Storage interface, hiding the underlying
    storage implementation. The storage technology is not exposed
    to consumers of this repository.
    """

    def __init__(self, storage: Storage | None = None, base_path: Path | str | None = None) -> None:
        """Initialize repository.

        Args:
            storage: Optional storage backend. If None, creates default storage.
                     Should implement the Storage interface.
            base_path: Optional base path for storage. Only used if storage is None.
        """
        if storage is None:
            storage = create_storage(base_path=base_path)
        self._storage = storage
        self._collection = self._storage.get_collection("research", Research)

    async def get_by_id(self, research_id: UUID) -> Research | None:
        """Get research by ID."""
        return self._collection.get(research_id)

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Research]:
        """List all research with pagination."""
        all_research = list(self._collection.values())
        return all_research[offset : offset + limit]

    async def save(self, research: Research) -> Research:
        """Save or update research."""
        self._collection[research.id] = research
        self._storage.save("research")
        return research

    async def delete(self, research_id: UUID) -> bool:
        """Delete research by ID."""
        if research_id in self._collection:
            del self._collection[research_id]
            self._storage.save("research")
            return True
        return False
