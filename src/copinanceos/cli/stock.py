"""Stock-related CLI commands."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from copinanceos.application.use_cases.stock import SearchStocksRequest, SearchType
from copinanceos.infrastructure.containers import container

stock_app = typer.Typer(help="Stock information commands")
console = Console()


@stock_app.command("search")
def search_stocks(
    query: str = typer.Argument(..., help="Search query (symbol or company name)"),
    limit: int = typer.Option(10, help="Maximum results"),
    search_type: SearchType = typer.Option(
        SearchType.AUTO,
        "--type",
        help="Search type: auto (detect), symbol (exact symbol), or general (text search)",
    ),
) -> None:
    """Search for stocks by symbol or company name."""

    async def _search() -> None:
        use_case = container.search_stocks_use_case()
        request = SearchStocksRequest(query=query, limit=limit, search_type=search_type)
        response = await use_case.execute(request)

        if not response.stocks:
            console.print("No stocks found", style="yellow")
            return

        table = Table(title=f"Search Results for '{query}'")
        table.add_column("Symbol", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Exchange", style="green")

        for stock in response.stocks:
            table.add_row(stock.symbol, stock.name, stock.exchange)

        console.print(table)

    asyncio.run(_search())
