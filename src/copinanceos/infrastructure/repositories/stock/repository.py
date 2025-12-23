"""Stock repository implementation."""

from copinanceos.domain.models.stock import Stock, StockData
from copinanceos.domain.ports.repositories import StockRepository
from copinanceos.domain.ports.storage import Storage
from copinanceos.infrastructure.repositories.storage.factory import create_storage


class StockRepositoryImpl(StockRepository):
    """Implementation of StockRepository.

    This repository uses the Storage interface, hiding the underlying
    storage implementation. The storage technology is not exposed
    to consumers of this repository.
    """

    def __init__(self, storage: Storage | None = None) -> None:
        """Initialize repository.

        Args:
            storage: Optional storage backend. If None, creates default storage.
                     Should implement the Storage interface.
        """
        if storage is None:
            storage = create_storage()
        self._storage = storage
        self._stocks = self._storage.get_collection("stocks", Stock)
        # Stock data is stored separately as it's a list per symbol
        self._stock_data: dict[str, list[StockData]] = {}

    async def get_by_symbol(self, symbol: str) -> Stock | None:
        """Get stock by symbol."""
        # Find stock by symbol (stocks are keyed by UUID, need to search)
        for stock in self._stocks.values():
            # Type narrowing: storage returns dict[UUID, Any], but we know it's Stock
            if isinstance(stock, Stock) and stock.symbol.upper() == symbol.upper():
                return stock
        return None

    async def search(self, query: str, limit: int = 10) -> list[Stock]:
        """Search stocks by query."""
        query_lower = query.lower()
        results = [
            stock
            for stock in self._stocks.values()
            if query_lower in stock.symbol.lower() or query_lower in stock.name.lower()
        ]
        return results[:limit]

    async def save(self, stock: Stock) -> Stock:
        """Save or update stock."""
        self._stocks[stock.id] = stock
        self._storage.save("stocks")
        return stock

    async def get_stock_data(self, symbol: str, limit: int = 100) -> list[StockData]:
        """Get historical stock data."""
        data = self._stock_data.get(symbol.upper(), [])
        return data[:limit]
