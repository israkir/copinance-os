"""Cache management CLI commands."""

import asyncio
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from copinanceos.infrastructure.containers import container

cache_app = typer.Typer(help="Cache management commands")
console = Console()


@cache_app.command("clear")
def clear_cache(
    tool_name: str | None = typer.Option(None, "--tool", help="Clear cache for specific tool only"),
) -> None:
    """Clear cached tool data."""

    async def _clear() -> None:
        cache_manager = container.cache_manager()
        deleted_count = await cache_manager.clear(tool_name)

        if tool_name:
            console.print(
                f"✓ Cleared {deleted_count} cache entries for tool: {tool_name}",
                style="bold green",
            )
        else:
            console.print(f"✓ Cleared {deleted_count} cache entries", style="bold green")

    asyncio.run(_clear())


@cache_app.command("refresh")
def refresh_cache(
    tool_name: str = typer.Argument(..., help="Tool name to refresh"),
    symbol: str | None = typer.Option(None, help="Symbol (for stock-related tools)"),
) -> None:
    """Refresh cached data for a specific tool call.

    This deletes the cache entry, forcing the next call to fetch fresh data.
    """

    async def _refresh() -> None:
        cache_manager = container.cache_manager()

        # Build parameters for cache key
        params: dict[str, Any] = {}
        if symbol:
            params["symbol"] = symbol

        deleted = await cache_manager.delete(tool_name, **params)
        if deleted:
            console.print(
                f"✓ Refreshed cache for {tool_name}" + (f" (symbol: {symbol})" if symbol else ""),
                style="bold green",
            )
        else:
            console.print(
                f"⚠ No cache entry found for {tool_name}"
                + (f" (symbol: {symbol})" if symbol else ""),
                style="bold yellow",
            )

    asyncio.run(_refresh())


@cache_app.command("info")
def cache_info() -> None:
    """Show cache information."""

    async def _info() -> None:
        cache_manager = container.cache_manager()
        backend = cache_manager.get_backend()

        table = Table(title="Cache Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Backend", backend.get_backend_name())
        table.add_row("Cache Directory", str(getattr(backend, "_cache_dir", "N/A")))

        console.print(table)

    asyncio.run(_info())
