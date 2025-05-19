# Uses yfinance library to fetch stock data from Yahoo Finance
import time
import yfinance as yf
import pandas as pd
from typing import List, Dict, Any
from data_collector.data_source_base import BaseDataSource
from utils.logger import get_logger
logger = get_logger(__name__)


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
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Delay between retries in seconds (default: 2)
        """
        self.proxy = kwargs.get('proxy', None)
        self.timeout = kwargs.get('timeout', 10)
        self.max_retries = kwargs.get('max_retries', 3)
        self.retry_delay = kwargs.get('retry_delay', 2)
        logger.info(f"Initialized Yahoo Finance data source")

        # Check if yfinance is available
        try:
            import yfinance
            self.available = True
        except ImportError:
            logger.error("yfinance package not installed. Please install it with 'pip install yfinance'")
            self.available = False

    def _with_retry(self, operation_name: str, func, *args, **kwargs):
        """
        Execute a function with retry logic for handling transient errors.
        
        Args:
            operation_name: Name of the operation for logging
            func: Function to execute
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the function call
            
        Raises:
            Exception: If all retry attempts fail
        """
        if not self.available:
            logger.error(f"Cannot perform {operation_name}: yfinance package not available")
            return None

        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            try:
                logger.info(f"Attempting {operation_name} (attempt {attempt+1}/{self.max_retries})")
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Successfully completed {operation_name} after {attempt+1} attempts")
                return result
            
            except Exception as e:
                last_error = e
                attempt += 1
                
                # Log the error with appropriate level based on attempt
                if attempt < self.max_retries:
                    logger.warning(f"Error during {operation_name} (attempt {attempt}/{self.max_retries}): {str(e)}")
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed {operation_name} after {self.max_retries} attempts. Last error: {str(e)}")
        
        # If we get here, all retries failed
        raise last_error

    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest price for a specific stock symbol from Yahoo Finance.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')

        Returns:
            Dict with price information or empty dict if unsuccessful

        Raises:
            Exception: When all retry attempts fail
        """
        if not self.validate_symbol(symbol):
            logger.error(f"Invalid symbol: {symbol}")
            return {}

        try:
            def _fetch_latest():
                ticker = yf.Ticker(symbol)
                # Get the most recent data
                hist = ticker.history(period="1d", interval="1m", proxy=self.proxy, timeout=self.timeout)

                if hist.empty:
                    logger.warning(f"No data returned for symbol {symbol}")
                    return {}

                # Get the latest row
                latest = hist.iloc[-1]

                logger.info(f"Retrieved latest price for {symbol}: {latest['Close']}")
                return {
                    'symbol': symbol,
                    'timestamp': hist.index[-1].to_pydatetime(),
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'close': float(latest['Close']),
                    'volume': int(latest['Volume'])
                }

            return self._with_retry(f"get_latest_price({symbol})", _fetch_latest)

        except Exception as e:
            # Propagate the exception instead of catching it
            # This allows test_retry_exhaustion to catch the exception
            raise

    def get_historical_data(self, symbol: str, interval: str = '5m', period: str = '1d') -> pd.DataFrame:
        """
        Get historical price data for a specific stock symbol from Yahoo Finance.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            interval: Time interval between data points (default: '5m' for 5 minutes)
            period: Time period to fetch data for (default: '1d' for 1 day)

        Returns:
            Pandas DataFrame with historical price data
        """
        if not self.validate_symbol(symbol):
            logger.error(f"Invalid symbol: {symbol}")
            return pd.DataFrame()

        try:
            def _fetch_historical():
                # Validate interval
                if interval not in self.get_supported_intervals():
                    logger.warning(f"Unsupported interval: {interval}. Using '5m' instead.")
                    _interval = '5m'
                else:
                    _interval = interval

                # Fetch data
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, interval=_interval, proxy=self.proxy, timeout=self.timeout)
                
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

                logger.info(f"Retrieved {len(hist)} historical data points for {symbol}")
                return hist[available_columns]
            
            return self._with_retry(f"get_historical_data({symbol}, {interval}, {period})", _fetch_historical)
        
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_batch_data(self, symbols: List[str], interval: str = '5m') -> Dict[str, pd.DataFrame]:
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
            def _fetch_batch():
                # Filter out invalid symbols
                valid_symbols = [s for s in symbols if self.validate_symbol(s)]
                
                if not valid_symbols:
                    logger.error("No valid symbols provided for batch data request")
                    return {}

                logger.info(f"Fetching batch data for {len(valid_symbols)} symbols with interval {interval}")
                
                # Download data for all symbols at once
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

                logger.info(f"Successfully retrieved batch data for {len(result)}/{len(valid_symbols)} symbols")
                return result
            
            return self._with_retry("get_batch_data", _fetch_batch)
        
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