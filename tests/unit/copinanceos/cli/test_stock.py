"""Unit tests for stock CLI commands."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from copinanceos.application.use_cases.stock import (
    SearchStocksRequest,
    SearchStocksResponse,
    SearchType,
)
from copinanceos.cli.stock import search_stocks
from copinanceos.domain.models.stock import Stock


@pytest.mark.unit
class TestStockCLI:
    """Test stock-related CLI commands."""

    @patch("copinanceos.cli.stock.container.search_stocks_use_case")
    @patch("copinanceos.cli.stock.console")
    def test_search_stocks_with_results(
        self, mock_console: MagicMock, mock_use_case_provider: MagicMock
    ) -> None:
        """Test stock search command with results."""

        # Setup mocks
        mock_stock1 = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        mock_stock2 = Stock(symbol="MSFT", name="Microsoft Corporation", exchange="NASDAQ")
        mock_response = SearchStocksResponse(stocks=[mock_stock1, mock_stock2])

        mock_use_case = AsyncMock()
        mock_use_case.execute = AsyncMock(return_value=mock_response)
        mock_use_case_provider.return_value = mock_use_case

        # Execute
        search_stocks(query="Apple", limit=10, search_type=SearchType.AUTO)

        # Verify
        mock_use_case_provider.assert_called_once()
        mock_use_case.execute.assert_called_once()
        call_args = mock_use_case.execute.call_args[0][0]
        assert isinstance(call_args, SearchStocksRequest)
        assert call_args.query == "Apple"
        assert call_args.limit == 10
        assert call_args.search_type == SearchType.AUTO

        # Verify console.print was called for table (not "No stocks found")
        assert mock_console.print.called
        # Check that "No stocks found" was NOT printed
        print_calls = [str(call) for call in mock_console.print.call_args_list]
        assert not any("No stocks found" in str(call) for call in print_calls)

    @patch("copinanceos.cli.stock.container.search_stocks_use_case")
    @patch("copinanceos.cli.stock.console")
    def test_search_stocks_no_results(
        self, mock_console: MagicMock, mock_use_case_provider: MagicMock
    ) -> None:
        """Test stock search command with no results."""

        # Setup mocks
        mock_response = SearchStocksResponse(stocks=[])
        mock_use_case = AsyncMock()
        mock_use_case.execute = AsyncMock(return_value=mock_response)
        mock_use_case_provider.return_value = mock_use_case

        # Execute
        search_stocks(query="INVALID", limit=10, search_type=SearchType.AUTO)

        # Verify
        mock_use_case.execute.assert_called_once()
        # Verify "No stocks found" was printed
        print_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("No stocks found" in str(call) for call in print_calls)

    @patch("copinanceos.cli.stock.container.search_stocks_use_case")
    @patch("copinanceos.cli.stock.console")
    def test_search_stocks_with_symbol_type(
        self, mock_console: MagicMock, mock_use_case_provider: MagicMock
    ) -> None:
        """Test stock search command with explicit symbol search type."""

        # Setup mocks
        mock_stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        mock_response = SearchStocksResponse(stocks=[mock_stock])
        mock_use_case = AsyncMock()
        mock_use_case.execute = AsyncMock(return_value=mock_response)
        mock_use_case_provider.return_value = mock_use_case

        # Execute with explicit symbol type
        search_stocks(query="AAPL", limit=5, search_type=SearchType.SYMBOL)

        # Verify
        call_args = mock_use_case.execute.call_args[0][0]
        assert call_args.search_type == SearchType.SYMBOL
        assert call_args.query == "AAPL"
        assert call_args.limit == 5

    @patch("copinanceos.cli.stock.container.search_stocks_use_case")
    @patch("copinanceos.cli.stock.console")
    def test_search_stocks_with_general_type(
        self, mock_console: MagicMock, mock_use_case_provider: MagicMock
    ) -> None:
        """Test stock search command with explicit general search type."""

        # Setup mocks
        mock_stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        mock_response = SearchStocksResponse(stocks=[mock_stock])
        mock_use_case = AsyncMock()
        mock_use_case.execute = AsyncMock(return_value=mock_response)
        mock_use_case_provider.return_value = mock_use_case

        # Execute with explicit general type
        search_stocks(query="apple", limit=20, search_type=SearchType.GENERAL)

        # Verify
        call_args = mock_use_case.execute.call_args[0][0]
        assert call_args.search_type == SearchType.GENERAL
        assert call_args.query == "apple"
        assert call_args.limit == 20

    @patch("copinanceos.cli.stock.container.search_stocks_use_case")
    @patch("copinanceos.cli.stock.Table")
    @patch("copinanceos.cli.stock.console")
    def test_search_stocks_table_formatting(
        self,
        mock_console: MagicMock,
        mock_table_class: MagicMock,
        mock_use_case_provider: MagicMock,
    ) -> None:
        """Test that stock search creates a properly formatted table."""

        # Setup mocks
        mock_stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
        mock_response = SearchStocksResponse(stocks=[mock_stock])
        mock_use_case = AsyncMock()
        mock_use_case.execute = AsyncMock(return_value=mock_response)
        mock_use_case_provider.return_value = mock_use_case

        mock_table = MagicMock()
        mock_table_class.return_value = mock_table

        # Execute
        search_stocks(query="Apple", limit=10, search_type=SearchType.AUTO)

        # Verify table was created with correct title
        mock_table_class.assert_called_once()
        call_kwargs = mock_table_class.call_args[1]
        assert call_kwargs["title"] == "Search Results for 'Apple'"

        # Verify columns were added
        assert mock_table.add_column.call_count == 3
        column_calls = [str(call) for call in mock_table.add_column.call_args_list]
        assert any("Symbol" in str(call) for call in column_calls)
        assert any("Name" in str(call) for call in column_calls)
        assert any("Exchange" in str(call) for call in column_calls)

        # Verify rows were added
        mock_table.add_row.assert_called_once_with("AAPL", "Apple Inc.", "NASDAQ")

        # Verify table was printed
        mock_console.print.assert_called()
