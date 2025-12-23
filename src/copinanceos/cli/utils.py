"""CLI utility functions and decorators."""

import asyncio
import functools
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def async_command(func: F) -> F:
    """Decorator to handle async CLI commands.

    This decorator wraps async CLI command functions and automatically
    runs them using asyncio.run(), eliminating the need for nested
    async functions and manual asyncio.run() calls.

    Usage:
        @research_app.command("create")
        @async_command
        async def create_research(symbol: str):
            # Async code here
            response = await use_case.execute(request)
            ...

    Args:
        func: Async function to wrap

    Returns:
        Synchronous wrapper function that runs the async function
    """
    if not asyncio.iscoroutinefunction(func):
        raise TypeError(f"async_command decorator can only be used on async functions, got {func}")

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Synchronous wrapper that runs the async function."""
        return asyncio.run(func(*args, **kwargs))

    return wrapper  # type: ignore[return-value]
