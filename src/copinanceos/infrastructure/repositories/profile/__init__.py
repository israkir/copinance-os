"""Research profile repository implementation."""

from copinanceos.infrastructure.repositories.profile.current_profile import CurrentProfile
from copinanceos.infrastructure.repositories.profile.repository import (
    ResearchProfileRepositoryImpl,
)

__all__ = ["ResearchProfileRepositoryImpl", "CurrentProfile"]
