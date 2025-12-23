"""Stock-related use cases."""

import asyncio
from decimal import Decimal
from enum import Enum

import structlog
from pydantic import BaseModel, Field

from copinanceos.application.use_cases.base import UseCase
from copinanceos.domain.models.stock import Stock, StockData
from copinanceos.domain.ports.data_providers import MarketDataProvider
from copinanceos.domain.ports.repositories import StockRepository
from copinanceos.domain.validation import StockSymbolValidator

logger = structlog.get_logger(__name__)


class SearchType(str, Enum):
    """Search type for stock search."""

    AUTO = "auto"  # Auto-detect based on query format
    SYMBOL = "symbol"  # Explicit symbol lookup
    GENERAL = "general"  # General text search (company name, etc.)


class GetStockRequest(BaseModel):
    """Request to get stock information."""

    symbol: str = Field(..., description="Stock symbol")


class GetStockResponse(BaseModel):
    """Response from getting stock information."""

    stock: Stock | None = Field(..., description="Stock entity if found")


class GetStockUseCase(UseCase[GetStockRequest, GetStockResponse]):
    """Use case for retrieving stock information."""

    def __init__(self, stock_repository: StockRepository) -> None:
        """Initialize use case."""
        self._stock_repository = stock_repository

    async def execute(self, request: GetStockRequest) -> GetStockResponse:
        """Execute the get stock use case."""
        stock = await self._stock_repository.get_by_symbol(request.symbol)
        return GetStockResponse(stock=stock)


class SearchStocksRequest(BaseModel):
    """Request to search stocks."""

    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, description="Maximum results to return")
    search_type: SearchType = Field(
        default=SearchType.AUTO,
        description="Search type: auto (detect), symbol (exact symbol), or general (text search)",
    )


class SearchStocksResponse(BaseModel):
    """Response from searching stocks."""

    stocks: list[Stock] = Field(default_factory=list, description="List of matching stocks")


class SearchStocksUseCase(UseCase[SearchStocksRequest, SearchStocksResponse]):
    """Use case for searching stocks."""

    def __init__(
        self,
        stock_repository: StockRepository,
        market_data_provider: MarketDataProvider | None = None,
    ) -> None:
        """Initialize use case.

        Args:
            stock_repository: Repository for stock entities
            market_data_provider: Optional market data provider for fetching stock info
                                 when not found in repository
        """
        self._stock_repository = stock_repository
        self._market_data_provider = market_data_provider

    async def _fetch_stock_from_provider(self, symbol: str) -> Stock | None:
        """Fetch stock information from market data provider.

        Args:
            symbol: Stock symbol to fetch

        Returns:
            Stock entity if found, None otherwise
        """
        if not self._market_data_provider:
            return None

        try:
            # Check if provider is available
            if not await self._market_data_provider.is_available():
                logger.debug("Market data provider not available", symbol=symbol)
                return None

            # Fetch quote which contains company info
            quote = await self._market_data_provider.get_quote(symbol.upper())

            # Extract company name from quote if available
            # Note: get_quote returns a dict, but we need to get full company info
            # For now, we'll create a basic Stock from the quote data
            # In a full implementation, we might want to fetch ticker.info separately

            # Try to get more detailed info if using yfinance
            try:
                import yfinance as yf  # type: ignore[import-untyped]  # noqa: PLC0415

                loop = asyncio.get_event_loop()
                ticker = await loop.run_in_executor(None, lambda: yf.Ticker(symbol.upper()))
                info = await loop.run_in_executor(None, lambda: ticker.info)

                # Validate that we got valid data (yfinance returns empty dict for invalid symbols)
                if not info or not isinstance(info, dict) or len(info) == 0:
                    logger.warning("Invalid symbol or no data from yfinance", symbol=symbol)
                    return None

                # Check for key indicators of valid stock data
                company_name = info.get("longName") or info.get("shortName")
                if not company_name:
                    logger.warning("No company name found for symbol", symbol=symbol)
                    return None

                # Create Stock entity from yfinance info with all fields directly
                stock = Stock(
                    symbol=symbol.upper(),
                    name=company_name,
                    exchange=info.get("exchange", quote.get("exchange", "")),
                    sector=info.get("sector"),
                    industry=info.get("industry"),
                    market_cap=(
                        Decimal(str(info.get("marketCap", 0))) if info.get("marketCap") else None
                    ),
                    # Company information
                    website=info.get("website"),
                    country=info.get("country"),
                    currency=info.get("currency"),
                    phone=info.get("phone"),
                    city=info.get("city"),
                    state=info.get("state"),
                    # Financial metrics
                    enterprise_value=(
                        Decimal(str(info.get("enterpriseValue", 0)))
                        if info.get("enterpriseValue")
                        else None
                    ),
                    shares_outstanding=(
                        int(info.get("sharesOutstanding", 0))
                        if info.get("sharesOutstanding")
                        else None
                    ),
                    float_shares=(
                        int(info.get("floatShares", 0)) if info.get("floatShares") else None
                    ),
                    beta=(
                        Decimal(str(info.get("beta", 0))) if info.get("beta") is not None else None
                    ),
                    dividend_yield=(
                        Decimal(str(info.get("dividendYield", 0)))
                        if info.get("dividendYield") is not None
                        else None
                    ),
                    employees=(
                        int(info.get("fullTimeEmployees", 0))
                        if info.get("fullTimeEmployees")
                        else None
                    ),
                    # Data source
                    data_provider="yfinance",
                )

                # Save to repository for future searches
                await self._stock_repository.save(stock)
                logger.info("Fetched and saved stock from provider", symbol=symbol)
                return stock

            except ImportError:
                # yfinance not available, use quote data only if we have valid quote
                logger.debug("yfinance not available, using quote data only", symbol=symbol)
                # Only create stock if we have valid quote data with exchange
                if quote.get("exchange"):
                    stock = Stock(
                        symbol=symbol.upper(),
                        name=quote.get(
                            "symbol", symbol.upper()
                        ),  # Fallback to symbol if name not available
                        exchange=quote.get("exchange", ""),
                        sector=None,
                        industry=None,
                        market_cap=None,
                        website=None,
                        country=None,
                        currency=None,
                        phone=None,
                        city=None,
                        state=None,
                        enterprise_value=None,
                        shares_outstanding=None,
                        float_shares=None,
                        beta=None,
                        dividend_yield=None,
                        employees=None,
                        data_provider="quote",
                    )
                    await self._stock_repository.save(stock)
                    return stock
                return None
            except Exception as yf_error:
                # Handle yfinance-specific errors (e.g., invalid symbol)
                logger.warning(
                    "Failed to fetch stock info from yfinance",
                    symbol=symbol,
                    error=str(yf_error),
                )
                return None

        except Exception as e:
            logger.warning("Failed to fetch stock from provider", symbol=symbol, error=str(e))
            return None

    async def execute(self, request: SearchStocksRequest) -> SearchStocksResponse:
        """Execute the search stocks use case."""
        # First, search the repository
        stocks = await self._stock_repository.search(request.query, request.limit)

        # If no results found, try fetching from provider
        if not stocks and self._market_data_provider:
            # Determine search strategy based on search_type
            use_symbol_search = False
            use_general_search = False

            if request.search_type == SearchType.SYMBOL:
                # Explicit symbol search
                use_symbol_search = True
                logger.debug("Using explicit symbol search", query=request.query)
            elif request.search_type == SearchType.GENERAL:
                # Explicit general search
                use_general_search = True
                logger.debug("Using explicit general search", query=request.query)
            else:  # SearchType.AUTO
                # Auto-detect: check if query looks like a symbol
                if StockSymbolValidator.looks_like_symbol(request.query):
                    use_symbol_search = True
                    logger.debug("Auto-detected symbol search", query=request.query)
                else:
                    use_general_search = True
                    logger.debug("Auto-detected general search", query=request.query)

            # Execute symbol search (direct fetch by symbol)
            if use_symbol_search:
                logger.debug("No local results, trying to fetch from provider", query=request.query)
                fetched_stock = await self._fetch_stock_from_provider(request.query.upper())
                if fetched_stock:
                    stocks = [fetched_stock]

            # Execute general search (company name, etc.)
            elif use_general_search:
                logger.debug(
                    "No local results, trying to search by name from provider",
                    query=request.query,
                )
                search_results = await self._market_data_provider.search_stocks(
                    request.query, limit=request.limit
                )

                # Convert search results to Stock entities and save them
                for result in search_results:
                    symbol = result.get("symbol", "")
                    if symbol:
                        # Fetch full stock info for the symbol
                        fetched_stock = await self._fetch_stock_from_provider(symbol)
                        if fetched_stock:
                            stocks.append(fetched_stock)
                            # Stop if we've reached the limit
                            if len(stocks) >= request.limit:
                                break

        return SearchStocksResponse(stocks=stocks)


class GetStockDataRequest(BaseModel):
    """Request to get historical stock data."""

    symbol: str = Field(..., description="Stock symbol")
    limit: int = Field(default=100, description="Number of data points to retrieve")


class GetStockDataResponse(BaseModel):
    """Response from getting stock data."""

    data: list[StockData] = Field(default_factory=list, description="Historical stock data")


class GetStockDataUseCase(UseCase[GetStockDataRequest, GetStockDataResponse]):
    """Use case for retrieving historical stock data."""

    def __init__(self, stock_repository: StockRepository) -> None:
        """Initialize use case."""
        self._stock_repository = stock_repository

    async def execute(self, request: GetStockDataRequest) -> GetStockDataResponse:
        """Execute the get stock data use case."""
        data = await self._stock_repository.get_stock_data(request.symbol, request.limit)
        return GetStockDataResponse(data=data)
