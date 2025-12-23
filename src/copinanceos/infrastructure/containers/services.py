"""Domain service container configuration."""

from dependency_injector import providers

from copinanceos.domain.services import ProfileManagementService


def configure_services(
    research_profile_repository: providers.Provider,
) -> dict[str, providers.Provider]:
    """Configure domain service providers.

    Args:
        research_profile_repository: Research profile repository provider

    Returns:
        Dictionary of domain service providers
    """
    return {
        "profile_management_service": providers.Factory(
            ProfileManagementService,
            profile_repository=research_profile_repository,
        ),
    }
