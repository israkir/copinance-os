"""Unit tests for stock repository implementation."""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from copinanceos.domain.models.stock import Stock, StockData
from copinanceos.domain.ports.storage import Storage
from copinanceos.infrastructure.repositories.stock.repository import StockRepositoryImpl


@pytest.mark.unit
class TestStockRepositoryImpl:
    """Test StockRepositoryImpl."""

    def test_initialization_with_default_storage(self) -> None:
        """Test initialization with default storage."""
        with patch(
            "copinanceos.infrastructure.repositories.stock.repository.create_storage"
        ) as mock_create_storage:
            mock_storage = MagicMock(spec=Storage)
            mock_storage.get_collection = MagicMock(return_value={})
            mock_create_storage.return_value = mock_storage

            repository = StockRepositoryImpl()

            assert repository._storage is mock_storage
            mock_storage.get_collection.assert_called_once_with("stocks", Stock)
            assert repository._stock_data == {}

    def test_initialization_with_custom_storage(self) -> None:
        """Test initialization with custom storage."""
        mock_storage = MagicMock(spec=Storage)
        mock_storage.get_collection = MagicMock(return_value={})

        repository = StockRepositoryImpl(storage=mock_storage)

        assert repository._storage is mock_storage
        mock_storage.get_collection.assert_called_once_with("stocks", Stock)
        assert repository._stock_data == {}

    async def test_get_by_symbol_found(self) -> None:
        """Test getting stock by symbol when it exists."""
        mock_storage = MagicMock(spec=Storage)
        stock1 = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        stock2 = Stock(symbol="MSFT", name="Microsoft", exchange="NASDAQ")
        mock_storage.get_collection = MagicMock(return_value={stock1.id: stock1, stock2.id: stock2})

        repository = StockRepositoryImpl(storage=mock_storage)
        result = await repository.get_by_symbol("AAPL")

        assert result is not None
        assert result.symbol == "AAPL"
        assert result.name == "Apple Inc."

    async def test_get_by_symbol_not_found(self) -> None:
        """Test getting stock by symbol when it doesn't exist."""
        mock_storage = MagicMock(spec=Storage)
        mock_storage.get_collection = MagicMock(return_value={})

        repository = StockRepositoryImpl(storage=mock_storage)
        result = await repository.get_by_symbol("NONEXISTENT")

        assert result is None

    async def test_get_by_symbol_case_insensitive(self) -> None:
        """Test that get_by_symbol is case insensitive."""
        mock_storage = MagicMock(spec=Storage)
        stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        mock_storage.get_collection = MagicMock(return_value={stock.id: stock})

        repository = StockRepositoryImpl(storage=mock_storage)

        # Test lowercase
        result1 = await repository.get_by_symbol("aapl")
        assert result1 is not None
        assert result1.symbol == "AAPL"

        # Test mixed case
        result2 = await repository.get_by_symbol("AaPl")
        assert result2 is not None
        assert result2.symbol == "AAPL"

    async def test_search_by_symbol(self) -> None:
        """Test searching stocks by symbol."""
        mock_storage = MagicMock(spec=Storage)
        stock1 = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        stock2 = Stock(symbol="MSFT", name="Microsoft", exchange="NASDAQ")
        stock3 = Stock(symbol="GOOGL", name="Alphabet", exchange="NASDAQ")
        mock_storage.get_collection = MagicMock(
            return_value={stock1.id: stock1, stock2.id: stock2, stock3.id: stock3}
        )

        repository = StockRepositoryImpl(storage=mock_storage)
        results = await repository.search("AAPL")

        assert len(results) == 1
        assert results[0].symbol == "AAPL"

    async def test_search_by_name(self) -> None:
        """Test searching stocks by company name."""
        mock_storage = MagicMock(spec=Storage)
        stock1 = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        stock2 = Stock(symbol="MSFT", name="Microsoft Corporation", exchange="NASDAQ")
        stock3 = Stock(symbol="GOOGL", name="Alphabet Inc.", exchange="NASDAQ")
        mock_storage.get_collection = MagicMock(
            return_value={stock1.id: stock1, stock2.id: stock2, stock3.id: stock3}
        )

        repository = StockRepositoryImpl(storage=mock_storage)
        results = await repository.search("Apple")

        assert len(results) == 1
        assert results[0].symbol == "AAPL"
        assert "Apple" in results[0].name

    async def test_search_case_insensitive(self) -> None:
        """Test that search is case insensitive."""
        mock_storage = MagicMock(spec=Storage)
        stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        mock_storage.get_collection = MagicMock(return_value={stock.id: stock})

        repository = StockRepositoryImpl(storage=mock_storage)

        # Test lowercase search
        results1 = await repository.search("apple")
        assert len(results1) == 1

        # Test uppercase search
        results2 = await repository.search("AAPL")
        assert len(results2) == 1

        # Test mixed case search
        results3 = await repository.search("ApPlE")
        assert len(results3) == 1

    async def test_search_partial_match(self) -> None:
        """Test that search matches partial strings."""
        mock_storage = MagicMock(spec=Storage)
        stock1 = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        stock2 = Stock(symbol="MSFT", name="Microsoft", exchange="NASDAQ")
        mock_storage.get_collection = MagicMock(return_value={stock1.id: stock1, stock2.id: stock2})

        repository = StockRepositoryImpl(storage=mock_storage)

        # Partial symbol match
        results1 = await repository.search("AAP")
        assert len(results1) == 1
        assert results1[0].symbol == "AAPL"

        # Partial name match
        results2 = await repository.search("Micro")
        assert len(results2) == 1
        assert results2[0].symbol == "MSFT"

    async def test_search_respects_limit(self) -> None:
        """Test that search respects the limit parameter."""
        mock_storage = MagicMock(spec=Storage)
        stocks = [
            Stock(symbol=f"STOCK{i}", name=f"Company {i}", exchange="NASDAQ") for i in range(20)
        ]
        mock_storage.get_collection = MagicMock(return_value={stock.id: stock for stock in stocks})

        repository = StockRepositoryImpl(storage=mock_storage)
        results = await repository.search("STOCK", limit=5)

        assert len(results) == 5

    async def test_search_returns_empty_list_when_no_matches(self) -> None:
        """Test that search returns empty list when no matches found."""
        mock_storage = MagicMock(spec=Storage)
        stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        mock_storage.get_collection = MagicMock(return_value={stock.id: stock})

        repository = StockRepositoryImpl(storage=mock_storage)
        results = await repository.search("NONEXISTENT")

        assert results == []

    async def test_save_stock(self) -> None:
        """Test saving a stock."""
        mock_storage = MagicMock(spec=Storage)
        stocks_dict: dict = {}
        mock_storage.get_collection = MagicMock(return_value=stocks_dict)
        mock_storage.save = MagicMock()

        repository = StockRepositoryImpl(storage=mock_storage)
        stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")

        result = await repository.save(stock)

        assert result is stock
        assert stocks_dict[stock.id] is stock
        mock_storage.save.assert_called_once_with("stocks")

    async def test_save_stock_updates_existing(self) -> None:
        """Test that save updates an existing stock."""
        mock_storage = MagicMock(spec=Storage)
        stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        stocks_dict = {stock.id: stock}
        mock_storage.get_collection = MagicMock(return_value=stocks_dict)
        mock_storage.save = MagicMock()

        repository = StockRepositoryImpl(storage=mock_storage)

        # Update the stock
        stock.name = "Apple Inc. Updated"
        result = await repository.save(stock)

        assert result is stock
        assert stocks_dict[stock.id].name == "Apple Inc. Updated"
        mock_storage.save.assert_called_once_with("stocks")

    async def test_save_multiple_stocks(self) -> None:
        """Test saving multiple stocks."""
        mock_storage = MagicMock(spec=Storage)
        stocks_dict: dict = {}
        mock_storage.get_collection = MagicMock(return_value=stocks_dict)
        mock_storage.save = MagicMock()

        repository = StockRepositoryImpl(storage=mock_storage)
        stock1 = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        stock2 = Stock(symbol="MSFT", name="Microsoft", exchange="NASDAQ")

        await repository.save(stock1)
        await repository.save(stock2)

        assert len(stocks_dict) == 2
        assert stocks_dict[stock1.id] is stock1
        assert stocks_dict[stock2.id] is stock2
        assert mock_storage.save.call_count == 2

    async def test_get_stock_data_empty(self) -> None:
        """Test getting stock data when none exists."""
        mock_storage = MagicMock(spec=Storage)
        mock_storage.get_collection = MagicMock(return_value={})

        repository = StockRepositoryImpl(storage=mock_storage)
        result = await repository.get_stock_data("AAPL")

        assert result == []

    async def test_get_stock_data_with_data(self) -> None:
        """Test getting stock data when data exists."""
        mock_storage = MagicMock(spec=Storage)
        mock_storage.get_collection = MagicMock(return_value={})

        repository = StockRepositoryImpl(storage=mock_storage)

        # Add stock data manually (since there's no save method for StockData)
        stock_data1 = StockData(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 1, tzinfo=UTC),
            open_price=Decimal("150.00"),
            close_price=Decimal("151.00"),
            high_price=Decimal("152.00"),
            low_price=Decimal("149.00"),
            volume=1000000,
        )
        stock_data2 = StockData(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 2, tzinfo=UTC),
            open_price=Decimal("151.00"),
            close_price=Decimal("152.00"),
            high_price=Decimal("153.00"),
            low_price=Decimal("150.00"),
            volume=1100000,
        )
        repository._stock_data["AAPL"] = [stock_data1, stock_data2]

        result = await repository.get_stock_data("AAPL")

        assert len(result) == 2
        assert result[0] is stock_data1
        assert result[1] is stock_data2

    async def test_get_stock_data_case_insensitive(self) -> None:
        """Test that get_stock_data is case insensitive."""
        mock_storage = MagicMock(spec=Storage)
        mock_storage.get_collection = MagicMock(return_value={})

        repository = StockRepositoryImpl(storage=mock_storage)
        stock_data = StockData(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 1, tzinfo=UTC),
            open_price=Decimal("150.00"),
            close_price=Decimal("151.00"),
            high_price=Decimal("152.00"),
            low_price=Decimal("149.00"),
            volume=1000000,
        )
        repository._stock_data["AAPL"] = [stock_data]

        # Test lowercase
        result1 = await repository.get_stock_data("aapl")
        assert len(result1) == 1

        # Test uppercase
        result2 = await repository.get_stock_data("AAPL")
        assert len(result2) == 1

        # Test mixed case
        result3 = await repository.get_stock_data("AaPl")
        assert len(result3) == 1

    async def test_get_stock_data_respects_limit(self) -> None:
        """Test that get_stock_data respects the limit parameter."""
        mock_storage = MagicMock(spec=Storage)
        mock_storage.get_collection = MagicMock(return_value={})

        repository = StockRepositoryImpl(storage=mock_storage)

        # Add multiple stock data entries
        stock_data_list = [
            StockData(
                symbol="AAPL",
                timestamp=datetime(2024, 1, i, tzinfo=UTC),
                open_price=Decimal("150.00"),
                close_price=Decimal("151.00"),
                high_price=Decimal("152.00"),
                low_price=Decimal("149.00"),
                volume=1000000,
            )
            for i in range(1, 21)
        ]
        repository._stock_data["AAPL"] = stock_data_list

        result = await repository.get_stock_data("AAPL", limit=5)

        assert len(result) == 5
        assert result == stock_data_list[:5]

    async def test_get_stock_data_different_symbols(self) -> None:
        """Test that get_stock_data returns data for correct symbol only."""
        mock_storage = MagicMock(spec=Storage)
        mock_storage.get_collection = MagicMock(return_value={})

        repository = StockRepositoryImpl(storage=mock_storage)

        # Add data for different symbols
        aapl_data = StockData(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 1, tzinfo=UTC),
            open_price=Decimal("150.00"),
            close_price=Decimal("151.00"),
            high_price=Decimal("152.00"),
            low_price=Decimal("149.00"),
            volume=1000000,
        )
        msft_data = StockData(
            symbol="MSFT",
            timestamp=datetime(2024, 1, 1, tzinfo=UTC),
            open_price=Decimal("300.00"),
            close_price=Decimal("301.00"),
            high_price=Decimal("302.00"),
            low_price=Decimal("299.00"),
            volume=2000000,
        )
        repository._stock_data["AAPL"] = [aapl_data]
        repository._stock_data["MSFT"] = [msft_data]

        aapl_result = await repository.get_stock_data("AAPL")
        msft_result = await repository.get_stock_data("MSFT")

        assert len(aapl_result) == 1
        assert aapl_result[0].symbol == "AAPL"
        assert len(msft_result) == 1
        assert msft_result[0].symbol == "MSFT"

    async def test_search_returns_stocks_matching_symbol_or_name(self) -> None:
        """Test that search matches both symbol and name."""
        mock_storage = MagicMock(spec=Storage)
        stock1 = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        stock2 = Stock(symbol="MSFT", name="Microsoft", exchange="NASDAQ")
        stock3 = Stock(symbol="GOOGL", name="Alphabet", exchange="NASDAQ")
        mock_storage.get_collection = MagicMock(
            return_value={stock1.id: stock1, stock2.id: stock2, stock3.id: stock3}
        )

        repository = StockRepositoryImpl(storage=mock_storage)

        # Search should match both symbol and name
        results = await repository.search("Apple")
        assert len(results) == 1
        assert results[0].symbol == "AAPL"

        results = await repository.search("MSFT")
        assert len(results) == 1
        assert results[0].symbol == "MSFT"

    async def test_get_by_symbol_with_multiple_stocks(self) -> None:
        """Test get_by_symbol when multiple stocks exist."""
        mock_storage = MagicMock(spec=Storage)
        stock1 = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        stock2 = Stock(symbol="MSFT", name="Microsoft", exchange="NASDAQ")
        stock3 = Stock(symbol="GOOGL", name="Alphabet", exchange="NASDAQ")
        mock_storage.get_collection = MagicMock(
            return_value={stock1.id: stock1, stock2.id: stock2, stock3.id: stock3}
        )

        repository = StockRepositoryImpl(storage=mock_storage)

        result = await repository.get_by_symbol("MSFT")
        assert result is not None
        assert result.symbol == "MSFT"
        assert result.name == "Microsoft"

    async def test_save_preserves_stock_id(self) -> None:
        """Test that save preserves the stock ID."""
        mock_storage = MagicMock(spec=Storage)
        stocks_dict: dict = {}
        mock_storage.get_collection = MagicMock(return_value=stocks_dict)
        mock_storage.save = MagicMock()

        repository = StockRepositoryImpl(storage=mock_storage)
        stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        original_id = stock.id

        result = await repository.save(stock)

        assert result.id == original_id
        assert stocks_dict[original_id].id == original_id
