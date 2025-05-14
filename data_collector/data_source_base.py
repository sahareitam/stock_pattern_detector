# Base class for all data sources in the system
# Defines the common interface that all data sources must implement

from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Any


class BaseDataSource(ABC):
    """
    Abstract base class for all stock data sources.
    Any data source (Yahoo Finance, Alpha Vantage, etc.) should inherit from this class
    and implement the required methods.
    """

    @abstractmethod
    def __init__(self, **kwargs):
        """
        Initialize the data source with optional parameters.
        """
        pass

    @abstractmethod
    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest price for a specific stock symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Dict with price information: {
                'symbol': str,
                'timestamp': datetime,
                'open': float,
                'high': float,
                'low': float,
                'close': float,
                'volume': int
            }
        """
        pass

    @abstractmethod
    def get_historical_data(self,symbol: str,interval: str = '5m',period: str = '1d') -> pd.DataFrame:
        """
        Get historical price data for a specific stock symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            interval: Time interval between data points (default: '5m' for 5 minutes)
            period: Time period to fetch data for (default: '1d' for 1 day)

        Returns:
            Pandas DataFrame with historical price data
            Expected columns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        """
        pass

    @abstractmethod
    def get_batch_data(self,symbols: List[str],interval: str = '5m') -> Dict[str, pd.DataFrame]:
        """
        Get latest data for multiple stock symbols in one batch request.
        This can be more efficient than making separate requests for each symbol.

        Args:
            symbols: List of stock ticker symbols (e.g., ['AAPL', 'MSFT'])
            interval: Time interval between data points (default: '5m' for 5 minutes)

        Returns:
            Dict mapping each symbol to its DataFrame of price data
        """
        pass

    def get_supported_intervals(self) -> List[str]:
        """
        Return the time intervals supported by this data source.
        Default implementation returns common intervals.
        Override in derived classes if needed.

        Returns:
            List of interval strings (e.g., ['1m', '5m', '15m', '1h', '1d'])
        """
        return ['1m', '5m', '15m', '30m', '60m', '1h', '1d']

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a symbol is properly formatted.
        Basic implementation just checks if it's a non-empty string.
        Override in derived classes for more specific validation.

        Args:
            symbol: Stock ticker symbol to validate

        Returns:
            True if symbol is valid, False otherwise
        """
        return isinstance(symbol, str) and len(symbol) > 0