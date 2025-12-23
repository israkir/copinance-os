"""Command-line interface for Copinance OS."""

import typer
from rich.console import Console

from copinanceos import __version__
from copinanceos.cli.cache import cache_app
from copinanceos.cli.profile import profile_app
from copinanceos.cli.research import research_app
from copinanceos.cli.stock import stock_app

app = typer.Typer(
    name="copinance",
    help="Copinance OS - Open-source stock research platform",
    no_args_is_help=True,
)

# Register sub-commands
app.add_typer(stock_app, name="stock")
app.add_typer(profile_app, name="profile")
app.add_typer(research_app, name="research")
app.add_typer(cache_app, name="cache")


@app.command()
def version() -> None:
    """Show version information."""
    console = Console()
    console.print(f"Copinance OS v{__version__}", style="bold green")


if __name__ == "__main__":
    app()
