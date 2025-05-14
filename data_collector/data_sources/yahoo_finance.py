# Uses yfinance library to fetch stock data from Yahoo Finance
import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional, Union
import logging
from data_collector.data_source_base import BaseDataSource

# Configure logging
logger = logging.getLogger(__name__)


class YahooFinanceDataSource(BaseDataSource):
    """
    Implementation of BaseDataSource that fetches data from Yahoo Finance
    using the yfinance library.
    """

    def __init__(self, **kwargs):
        """
        Initialize the Yahoo Finance data source.

        Kwargs:
            proxy: Proxy server URL, if needed
            timeout: Request timeout in seconds (default: 10)
        """
        self.proxy = kwargs.get('proxy', None)
        self.timeout = kwargs.get('timeout', 10)
        logger.info("Initialized Yahoo Finance data source")

        # Check if yfinance is available
        try:
            import yfinance
            self.available = True
        except ImportError:
            logger.error("yfinance package not installed. Please install it with 'pip install yfinance'")
            self.available = False

    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest price for a specific stock symbol from Yahoo Finance.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Dict with price information
        """
        if not self.available:
            logger.error("yfinance package not available")
            return {}

        if not self.validate_symbol(symbol):
            logger.error(f"Invalid symbol: {symbol}")
            return {}

        try:
            ticker = yf.Ticker(symbol)
            # Get the most recent data
            hist = ticker.history(period="1d", interval="1m", proxy=self.proxy)

            if hist.empty:
                logger.warning(f"No data returned for symbol {symbol}")
                return {}

            # Get the latest row
            latest = hist.iloc[-1]

            return {
                'symbol': symbol,
                'timestamp': hist.index[-1].to_pydatetime(),
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'close': float(latest['Close']),
                'volume': int(latest['Volume'])
            }

        except Exception as e:
            logger.error(f"Error getting latest price for {symbol}: {str(e)}")
            return {}

    def get_historical_data(self,symbol: str,interval: str = '5m',period: str = '1d') -> pd.DataFrame:
        """
        Get historical price data for a specific stock symbol from Yahoo Finance.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            interval: Time interval between data points (default: '5m' for 5 minutes)
            period: Time period to fetch data for (default: '1d' for 1 day)

        Returns:
            Pandas DataFrame with historical price data
        """
        if not self.available:
            logger.error("yfinance package not available")
            return pd.DataFrame()

        if not self.validate_symbol(symbol):
            logger.error(f"Invalid symbol: {symbol}")
            return pd.DataFrame()

        try:
            # Validate interval
            if interval not in self.get_supported_intervals():
                logger.warning(f"Unsupported interval: {interval}. Using '5m' instead.")
                interval = '5m'

            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval, proxy=self.proxy)

            if hist.empty:
                logger.warning(f"No historical data returned for symbol {symbol}")
                return pd.DataFrame()

            # Rename columns to match our expected format
            hist = hist.reset_index()
            hist = hist.rename(columns={
                'Date': 'timestamp',
                'Datetime': 'timestamp',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Ensure timestamp is properly converted to datetime
            if 'timestamp' in hist.columns:
                hist['timestamp'] = pd.to_datetime(hist['timestamp'])

            # Select and return only the columns we need
            required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            available_columns = [col for col in required_columns if col in hist.columns]

            return hist[available_columns]

        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_batch_data(self,symbols: List[str],interval: str = '5m') -> Dict[str, pd.DataFrame]:
        """
        Get latest data for multiple stock symbols in one batch request.

        Args:
            symbols: List of stock ticker symbols (e.g., ['AAPL', 'MSFT'])
            interval: Time interval between data points (default: '5m' for 5 minutes)

        Returns:
            Dict mapping each symbol to its DataFrame of price data
        """
        if not self.available:
            logger.error("yfinance package not available")
            return {}

        if not symbols:
            logger.error("No symbols provided")
            return {}

        try:
            # Filter out invalid symbols
            valid_symbols = [s for s in symbols if self.validate_symbol(s)]

            if not valid_symbols:
                logger.error("No valid symbols provided")
                return {}

            # Download data for all symbols at once
            # yfinance supports this batch operation which is more efficient
            tickers_data = yf.download(
                tickers=' '.join(valid_symbols),
                period='1d',  # We just need the most recent day
                interval=interval,
                group_by='ticker',
                auto_adjust=True,
                prepost=False,
                proxy=self.proxy,
                timeout=self.timeout
            )

            # Process the results
            result = {}

            # Handle single symbol case differently
            if len(valid_symbols) == 1:
                symbol = valid_symbols[0]
                if not tickers_data.empty:
                    # Rename columns
                    df = tickers_data.reset_index()
                    df = df.rename(columns={
                        'Datetime': 'timestamp',
                        'Date': 'timestamp',
                        'Open': 'open',
                        'High': 'high',
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    })

                    # Ensure timestamp is datetime
                    if 'timestamp' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])

                    # Get required columns
                    required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                    available_columns = [col for col in required_columns if col in df.columns]

                    result[symbol] = df[available_columns]
            else:
                # Multiple symbols case
                for symbol in valid_symbols:
                    if symbol in tickers_data.columns.levels[0]:
                        # Extract data for this symbol
                        df = tickers_data[symbol].reset_index()
                        # Rename columns
                        df = df.rename(columns={
                            'Datetime': 'timestamp',
                            'Date': 'timestamp',
                            'Open': 'open',
                            'High': 'high',
                            'Low': 'low',
                            'Close': 'close',
                            'Volume': 'volume'
                        })

                        # Ensure timestamp is datetime
                        if 'timestamp' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['timestamp'])

                        # Get required columns
                        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                        available_columns = [col for col in required_columns if col in df.columns]

                        result[symbol] = df[available_columns]
                    else:
                        logger.warning(f"No data for symbol {symbol}")

            return result

        except Exception as e:
            logger.error(f"Error getting batch data: {str(e)}")
            return {}

    def get_supported_intervals(self) -> List[str]:
        """
        Return the time intervals supported by Yahoo Finance.

        Returns:
            List of interval strings
        """
        # Yahoo Finance supports the following intervals
        return ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a symbol is properly formatted for Yahoo Finance.

        Args:
            symbol: Stock ticker symbol to validate

        Returns:
            True if symbol is valid, False otherwise
        """
        # Basic validation for Yahoo Finance symbols
        if not isinstance(symbol, str) or not symbol:
            return False

        # Yahoo Finance symbols are typically uppercase alphanumeric
        # They may contain dots, dashes, or underscores
        # This is a basic validation and may need refinement
        return True