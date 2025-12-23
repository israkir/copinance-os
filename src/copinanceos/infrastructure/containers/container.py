"""Main dependency injection container configuration.

This module composes all container modules into a single Container class.
It replaces the global state pattern with proper dependency injection for better
testability and lifecycle management.
"""

from dependency_injector import containers, providers

from copinanceos.infrastructure.containers.data_providers import configure_data_providers
from copinanceos.infrastructure.containers.repositories import configure_repositories
from copinanceos.infrastructure.containers.services import configure_services
from copinanceos.infrastructure.containers.storage import configure_storage
from copinanceos.infrastructure.containers.use_cases import configure_use_cases


class Container(containers.DeclarativeContainer):
    """Dependency injection container for Copinance OS.

    This container composes providers from modular configuration modules:
    - Storage backend
    - Repositories
    - Domain services
    - Data providers
    - Use cases
    """

    # Configuration
    config = providers.Configuration()

    # Storage backend (singleton, configured from settings)
    storage_backend = configure_storage()

    # Repositories (singletons, use shared storage backend)
    # Note: We need to assign providers directly, not from dict
    # So we'll call configure_repositories and assign individually
    _repositories_config = configure_repositories(storage_backend)
    stock_repository = _repositories_config["stock_repository"]
    research_repository = _repositories_config["research_repository"]
    research_profile_repository = _repositories_config["research_profile_repository"]
    current_profile = _repositories_config["current_profile"]

    # Domain services
    _services_config = configure_services(research_profile_repository)
    profile_management_service = _services_config["profile_management_service"]

    # Data providers (singletons, can be overridden)
    _data_providers_config = configure_data_providers()
    market_data_provider = _data_providers_config["market_data_provider"]
    fundamental_data_provider = _data_providers_config["fundamental_data_provider"]
    sec_filings_provider = _data_providers_config["sec_filings_provider"]
    cache_manager = _data_providers_config["cache_manager"]
    llm_analyzer = _data_providers_config["llm_analyzer"]
    llm_analyzer_for_workflow = _data_providers_config["llm_analyzer_for_workflow"]

    # Use cases
    _use_cases_config = configure_use_cases(
        stock_repository=stock_repository,
        research_repository=research_repository,
        research_profile_repository=research_profile_repository,
        current_profile=current_profile,
        market_data_provider=market_data_provider,
        fundamental_data_provider=fundamental_data_provider,
        sec_filings_provider=sec_filings_provider,
        cache_manager=cache_manager,
        profile_management_service=profile_management_service,
    )
    get_stock_use_case = _use_cases_config["get_stock_use_case"]
    search_stocks_use_case = _use_cases_config["search_stocks_use_case"]
    get_stock_data_use_case = _use_cases_config["get_stock_data_use_case"]
    create_research_use_case = _use_cases_config["create_research_use_case"]
    get_research_use_case = _use_cases_config["get_research_use_case"]
    set_research_context_use_case = _use_cases_config["set_research_context_use_case"]
    create_profile_use_case = _use_cases_config["create_profile_use_case"]
    get_current_profile_use_case = _use_cases_config["get_current_profile_use_case"]
    set_current_profile_use_case = _use_cases_config["set_current_profile_use_case"]
    delete_profile_use_case = _use_cases_config["delete_profile_use_case"]
    get_profile_use_case = _use_cases_config["get_profile_use_case"]
    list_profiles_use_case = _use_cases_config["list_profiles_use_case"]
    research_stock_fundamentals_use_case = _use_cases_config["research_stock_fundamentals_use_case"]
    workflow_executors = _use_cases_config["workflow_executors"]
    execute_research_use_case = _use_cases_config["execute_research_use_case"]


# Global container instance (can be overridden for testing)
_container: Container | None = None


def get_container() -> Container:
    """Get the global dependency injection container.

    Returns:
        Container instance
    """
    global _container
    if _container is None:
        _container = Container()
    return _container


def set_container(container: Container) -> None:
    """Set a custom container (useful for testing).

    Args:
        container: Container instance to use
    """
    global _container
    _container = container


def reset_container() -> None:
    """Reset the global container (useful for testing)."""
    global _container
    _container = None


# Expose container instance for convenience
container = get_container()
