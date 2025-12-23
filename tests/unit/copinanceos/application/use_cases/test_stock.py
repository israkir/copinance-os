"""Unit tests for stock use cases."""

import builtins
import sys
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from copinanceos.application.use_cases.stock import (
    GetStockDataRequest,
    GetStockDataUseCase,
    GetStockRequest,
    GetStockUseCase,
    SearchStocksRequest,
    SearchStocksUseCase,
    SearchType,
)
from copinanceos.domain.models.stock import Stock, StockData
from copinanceos.domain.ports.data_providers import MarketDataProvider
from copinanceos.domain.ports.repositories import StockRepository


@pytest.mark.unit
class TestGetStockUseCase:
    """Test GetStockUseCase."""

    def test_initialization(self) -> None:
        """Test use case initialization."""
        mock_repository = MagicMock(spec=StockRepository)
        use_case = GetStockUseCase(stock_repository=mock_repository)
        assert use_case._stock_repository is mock_repository

    @pytest.mark.asyncio
    async def test_execute_stock_found(self) -> None:
        """Test execute when stock is found."""
        mock_repository = AsyncMock(spec=StockRepository)
        stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        mock_repository.get_by_symbol = AsyncMock(return_value=stock)

        use_case = GetStockUseCase(stock_repository=mock_repository)
        request = GetStockRequest(symbol="AAPL")
        response = await use_case.execute(request)

        assert response.stock is not None
        assert response.stock.symbol == "AAPL"
        mock_repository.get_by_symbol.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    async def test_execute_stock_not_found(self) -> None:
        """Test execute when stock is not found."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_repository.get_by_symbol = AsyncMock(return_value=None)

        use_case = GetStockUseCase(stock_repository=mock_repository)
        request = GetStockRequest(symbol="NONEXISTENT")
        response = await use_case.execute(request)

        assert response.stock is None
        mock_repository.get_by_symbol.assert_called_once_with("NONEXISTENT")


@pytest.mark.unit
class TestSearchStocksUseCase:
    """Test SearchStocksUseCase."""

    def test_initialization_without_provider(self) -> None:
        """Test initialization without market data provider."""
        mock_repository = MagicMock(spec=StockRepository)
        use_case = SearchStocksUseCase(stock_repository=mock_repository)
        assert use_case._stock_repository is mock_repository
        assert use_case._market_data_provider is None

    def test_initialization_with_provider(self) -> None:
        """Test initialization with market data provider."""
        mock_repository = MagicMock(spec=StockRepository)
        mock_provider = MagicMock(spec=MarketDataProvider)
        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )
        assert use_case._stock_repository is mock_repository
        assert use_case._market_data_provider is mock_provider

    @pytest.mark.asyncio
    async def test_fetch_stock_from_provider_no_provider(self) -> None:
        """Test _fetch_stock_from_provider when no provider is set."""
        mock_repository = MagicMock(spec=StockRepository)
        use_case = SearchStocksUseCase(stock_repository=mock_repository)

        result = await use_case._fetch_stock_from_provider("AAPL")
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_stock_from_provider_not_available(self) -> None:
        """Test _fetch_stock_from_provider when provider is not available."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=False)

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        result = await use_case._fetch_stock_from_provider("AAPL")
        assert result is None
        mock_provider.is_available.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_stock_from_provider_with_yfinance_success(self) -> None:
        """Test _fetch_stock_from_provider with yfinance successfully."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)
        mock_provider.get_quote = AsyncMock(
            return_value={
                "symbol": "AAPL",
                "exchange": "NASDAQ",
                "current_price": Decimal("150.0"),
            }
        )

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        # Mock yfinance
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_ticker = MagicMock()
            mock_ticker.info = {
                "longName": "Apple Inc.",
                "shortName": "Apple",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "marketCap": 2500000000000,
                "website": "https://www.apple.com",
                "country": "United States",
                "currency": "USD",
                "phone": "408-996-1010",
                "city": "Cupertino",
                "state": "CA",
                "enterpriseValue": 2600000000000,
                "sharesOutstanding": 16000000000,
                "floatShares": 15000000000,
                "beta": 1.2,
                "dividendYield": 0.5,
                "fullTimeEmployees": 164000,
            }
            mock_loop.run_in_executor = AsyncMock(side_effect=[mock_ticker, mock_ticker.info])
            mock_get_loop.return_value = mock_loop

            result = await use_case._fetch_stock_from_provider("AAPL")

            assert result is not None
            assert result.symbol == "AAPL"
            assert result.name == "Apple Inc."
            assert result.exchange == "NASDAQ"
            assert result.data_provider == "yfinance"
            mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_stock_from_provider_invalid_symbol(self) -> None:
        """Test _fetch_stock_from_provider with invalid symbol."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)
        mock_provider.get_quote = AsyncMock(
            return_value={"symbol": "INVALID", "exchange": "NASDAQ"}
        )

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        # Mock yfinance returning empty/invalid data
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_ticker = MagicMock()
            mock_ticker.info = {}  # Empty info indicates invalid symbol
            mock_loop.run_in_executor = AsyncMock(side_effect=[mock_ticker, mock_ticker.info])
            mock_get_loop.return_value = mock_loop

            result = await use_case._fetch_stock_from_provider("INVALID")
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_stock_from_provider_no_company_name(self) -> None:
        """Test _fetch_stock_from_provider when no company name is found."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)
        mock_provider.get_quote = AsyncMock(return_value={"symbol": "TEST", "exchange": "NASDAQ"})

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        # Mock yfinance with no company name
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_ticker = MagicMock()
            mock_ticker.info = {"exchange": "NASDAQ"}  # No longName or shortName
            mock_loop.run_in_executor = AsyncMock(side_effect=[mock_ticker, mock_ticker.info])
            mock_get_loop.return_value = mock_loop

            result = await use_case._fetch_stock_from_provider("TEST")
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_stock_from_provider_yfinance_not_available(self) -> None:
        """Test _fetch_stock_from_provider when yfinance is not available."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)
        mock_provider.get_quote = AsyncMock(return_value={"symbol": "AAPL", "exchange": "NASDAQ"})

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        # Test the ImportError path by patching the import inside the method
        # We'll simulate ImportError by patching sys.modules and the import
        # Store original state
        yfinance_in_modules = "yfinance" in sys.modules
        original_yfinance = sys.modules.get("yfinance")

        # Remove yfinance to simulate it not being installed
        if "yfinance" in sys.modules:
            del sys.modules["yfinance"]

        try:
            # Create a mock import that raises ImportError for yfinance
            original_import = builtins.__import__

            def import_side_effect(name, *args, **kwargs):
                if name == "yfinance":
                    raise ImportError("No module named yfinance")
                # For other modules, check if already loaded
                if name in sys.modules:
                    return sys.modules[name]
                # Use original import for non-yfinance
                return original_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=import_side_effect):
                result = await use_case._fetch_stock_from_provider("AAPL")
                # Should fall back to quote data if exchange is available
                assert result is not None
                assert result.symbol == "AAPL"
                assert result.exchange == "NASDAQ"
        finally:
            # Restore yfinance if it was originally loaded
            if yfinance_in_modules and original_yfinance:
                sys.modules["yfinance"] = original_yfinance
            elif not yfinance_in_modules and "yfinance" in sys.modules:
                del sys.modules["yfinance"]

    @pytest.mark.asyncio
    async def test_fetch_stock_from_provider_handles_exception(self) -> None:
        """Test _fetch_stock_from_provider handles exceptions."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)
        mock_provider.get_quote = AsyncMock(side_effect=Exception("API error"))

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        result = await use_case._fetch_stock_from_provider("AAPL")
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_found_in_repository(self) -> None:
        """Test execute when stocks are found in repository."""
        mock_repository = AsyncMock(spec=StockRepository)
        stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        mock_repository.search = AsyncMock(return_value=[stock])

        use_case = SearchStocksUseCase(stock_repository=mock_repository)
        request = SearchStocksRequest(query="Apple", limit=10)
        response = await use_case.execute(request)

        assert len(response.stocks) == 1
        assert response.stocks[0].symbol == "AAPL"
        mock_repository.search.assert_called_once_with("Apple", 10)

    @pytest.mark.asyncio
    async def test_execute_auto_symbol_search(self) -> None:
        """Test execute with AUTO search type detecting symbol."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_repository.search = AsyncMock(return_value=[])
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)
        mock_provider.get_quote = AsyncMock(return_value={"symbol": "AAPL", "exchange": "NASDAQ"})

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        # Mock successful yfinance fetch
        with patch.object(use_case, "_fetch_stock_from_provider") as mock_fetch:
            stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
            mock_fetch.return_value = stock

            request = SearchStocksRequest(query="AAPL", limit=10, search_type=SearchType.AUTO)
            response = await use_case.execute(request)

            assert len(response.stocks) == 1
            assert response.stocks[0].symbol == "AAPL"
            mock_fetch.assert_called_once_with("AAPL")

    @pytest.mark.asyncio
    async def test_execute_auto_general_search(self) -> None:
        """Test execute with AUTO search type detecting general search."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_repository.search = AsyncMock(return_value=[])
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)
        mock_provider.search_stocks = AsyncMock(
            return_value=[
                {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
                {"symbol": "MSFT", "name": "Microsoft", "exchange": "NASDAQ"},
            ]
        )

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        # Mock successful fetch for each symbol
        with patch.object(use_case, "_fetch_stock_from_provider") as mock_fetch:
            stock1 = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
            stock2 = Stock(symbol="MSFT", name="Microsoft", exchange="NASDAQ")
            mock_fetch.side_effect = [stock1, stock2]

            request = SearchStocksRequest(query="apple", limit=10, search_type=SearchType.AUTO)
            response = await use_case.execute(request)

            assert len(response.stocks) == 2
            assert response.stocks[0].symbol == "AAPL"
            assert response.stocks[1].symbol == "MSFT"
            mock_provider.search_stocks.assert_called_once_with("apple", limit=10)

    @pytest.mark.asyncio
    async def test_execute_explicit_symbol_search(self) -> None:
        """Test execute with explicit SYMBOL search type."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_repository.search = AsyncMock(return_value=[])
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        with patch.object(use_case, "_fetch_stock_from_provider") as mock_fetch:
            stock = Stock(symbol="aapl", name="Apple Inc.", exchange="NASDAQ")
            mock_fetch.return_value = stock

            request = SearchStocksRequest(query="aapl", limit=10, search_type=SearchType.SYMBOL)
            response = await use_case.execute(request)

            assert len(response.stocks) == 1
            mock_fetch.assert_called_once_with("AAPL")  # Should be uppercased

    @pytest.mark.asyncio
    async def test_execute_explicit_general_search(self) -> None:
        """Test execute with explicit GENERAL search type."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_repository.search = AsyncMock(return_value=[])
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)
        mock_provider.search_stocks = AsyncMock(
            return_value=[{"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"}]
        )

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        with patch.object(use_case, "_fetch_stock_from_provider") as mock_fetch:
            stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
            mock_fetch.return_value = stock

            request = SearchStocksRequest(query="AAPL", limit=10, search_type=SearchType.GENERAL)
            response = await use_case.execute(request)

            assert len(response.stocks) == 1
            mock_provider.search_stocks.assert_called_once_with("AAPL", limit=10)

    @pytest.mark.asyncio
    async def test_execute_general_search_respects_limit(self) -> None:
        """Test execute general search respects limit."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_repository.search = AsyncMock(return_value=[])
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)
        mock_provider.search_stocks = AsyncMock(
            return_value=[
                {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
                {"symbol": "MSFT", "name": "Microsoft", "exchange": "NASDAQ"},
                {"symbol": "GOOGL", "name": "Alphabet", "exchange": "NASDAQ"},
            ]
        )

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        with patch.object(use_case, "_fetch_stock_from_provider") as mock_fetch:
            stocks = [
                Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ"),
                Stock(symbol="MSFT", name="Microsoft", exchange="NASDAQ"),
                Stock(symbol="GOOGL", name="Alphabet", exchange="NASDAQ"),
            ]
            mock_fetch.side_effect = stocks

            request = SearchStocksRequest(query="tech", limit=2, search_type=SearchType.GENERAL)
            response = await use_case.execute(request)

            assert len(response.stocks) == 2
            assert response.stocks[0].symbol == "AAPL"
            assert response.stocks[1].symbol == "MSFT"

    @pytest.mark.asyncio
    async def test_execute_no_provider_no_results(self) -> None:
        """Test execute when no provider and no repository results."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_repository.search = AsyncMock(return_value=[])

        use_case = SearchStocksUseCase(stock_repository=mock_repository)
        request = SearchStocksRequest(query="NONEXISTENT", limit=10)
        response = await use_case.execute(request)

        assert len(response.stocks) == 0

    @pytest.mark.asyncio
    async def test_execute_general_search_no_results(self) -> None:
        """Test execute general search when provider returns no results."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_repository.search = AsyncMock(return_value=[])
        mock_provider = AsyncMock(spec=MarketDataProvider)
        mock_provider.is_available = AsyncMock(return_value=True)
        mock_provider.search_stocks = AsyncMock(return_value=[])

        use_case = SearchStocksUseCase(
            stock_repository=mock_repository, market_data_provider=mock_provider
        )

        request = SearchStocksRequest(query="nonexistent", limit=10, search_type=SearchType.GENERAL)
        response = await use_case.execute(request)

        assert len(response.stocks) == 0
        mock_provider.search_stocks.assert_called_once_with("nonexistent", limit=10)


@pytest.mark.unit
class TestGetStockDataUseCase:
    """Test GetStockDataUseCase."""

    def test_initialization(self) -> None:
        """Test use case initialization."""
        mock_repository = MagicMock(spec=StockRepository)
        use_case = GetStockDataUseCase(stock_repository=mock_repository)
        assert use_case._stock_repository is mock_repository

    @pytest.mark.asyncio
    async def test_execute_with_data(self) -> None:
        """Test execute when stock data exists."""
        mock_repository = AsyncMock(spec=StockRepository)
        stock_data = [
            StockData(
                symbol="AAPL",
                timestamp=datetime(2024, 1, 1, tzinfo=UTC),
                open_price=Decimal("150.0"),
                close_price=Decimal("151.0"),
                high_price=Decimal("152.0"),
                low_price=Decimal("149.0"),
                volume=1000000,
            )
        ]
        mock_repository.get_stock_data = AsyncMock(return_value=stock_data)

        use_case = GetStockDataUseCase(stock_repository=mock_repository)
        request = GetStockDataRequest(symbol="AAPL", limit=100)
        response = await use_case.execute(request)

        assert len(response.data) == 1
        assert response.data[0].symbol == "AAPL"
        mock_repository.get_stock_data.assert_called_once_with("AAPL", 100)

    @pytest.mark.asyncio
    async def test_execute_no_data(self) -> None:
        """Test execute when no stock data exists."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_repository.get_stock_data = AsyncMock(return_value=[])

        use_case = GetStockDataUseCase(stock_repository=mock_repository)
        request = GetStockDataRequest(symbol="AAPL", limit=100)
        response = await use_case.execute(request)

        assert len(response.data) == 0
        mock_repository.get_stock_data.assert_called_once_with("AAPL", 100)

    @pytest.mark.asyncio
    async def test_execute_with_default_limit(self) -> None:
        """Test execute with default limit."""
        mock_repository = AsyncMock(spec=StockRepository)
        mock_repository.get_stock_data = AsyncMock(return_value=[])

        use_case = GetStockDataUseCase(stock_repository=mock_repository)
        request = GetStockDataRequest(symbol="AAPL")
        await use_case.execute(request)

        mock_repository.get_stock_data.assert_called_once_with("AAPL", 100)
