# Main data collector module that handles fetching stock data
# and saving it to the database

from datetime import datetime

from config.config import STOCKS, COLLECTION_INTERVAL_MINUTES
from data_collector.data_sources.yahoo_finance import YahooFinanceDataSource
from data_storage import get_db

from utils.logger import get_logger

logger = get_logger(__name__)


class DataCollector:
    """
    Main class for collecting stock price data from external sources
    and storing it in the database.
    """

    def __init__(self, data_source=None, db_instance=None):
        """
        Initialize the DataCollector with a data source.

        Args:
            data_source: A BaseDataSource instance. If None, YahooFinanceDataSource is used.
            db_instance: Database connection. If None, the singleton instance is used.
        """
        self.db = db_instance or get_db()

        if data_source is None:
            logger.info("No data source provided, using Yahoo Finance as default")
            self.data_source = YahooFinanceDataSource()
        else:
            self.data_source = data_source

        logger.info(f"DataCollector initialized with {self.data_source.__class__.__name__}")

    def collect_all_latest(self):
        """
        Collect the latest price data for all configured stocks
        and save to the database.

        Returns:
            int: Number of stocks successfully collected
        """
        if not self.is_trading_hours():
            logger.info("Skipping collection as outside trading hours")
            return 0

        logger.info(f"Starting collection for {len(STOCKS)} stocks")
        successful_count = 0

        try:
            # Try to use batch collection for efficiency
            try:
                data_dict = self.data_source.get_batch_data(
                    symbols=STOCKS,
                    interval=f"{COLLECTION_INTERVAL_MINUTES}m"
                )

                if not data_dict:
                    logger.warning("Batch collection returned no data, trying individual collection")
                    data_dict = self._collect_individual_stocks()
            except Exception as e:
                logger.warning(f"Batch collection failed: {str(e)}. Falling back to individual collection.")
                data_dict = self._collect_individual_stocks()

            # Process collected data
            for symbol, df in data_dict.items():
                if df.empty:
                    logger.warning(f"No data returned for {symbol}")
                    continue

                # Only take the latest row if we have multiple
                latest = df.iloc[-1]

                # Save to database
                try:
                    self.db.insert_price(
                        symbol=symbol,
                        timestamp=latest['timestamp'],
                        open_price=latest['open'],
                        high=latest['high'],
                        low=latest['low'],
                        close=latest['close'],
                        volume=latest['volume']
                    )

                    logger.info(f"Saved latest price for {symbol}: {latest['close']}")
                    successful_count += 1
                except Exception as e:
                    logger.error(f"Error saving data for {symbol}: {str(e)}")

        except Exception as e:
            logger.error(f"Error collecting latest prices: {str(e)}")

        logger.info(f"Collection completed: {successful_count} out of {len(STOCKS)} stocks successful")
        return successful_count

    def _collect_individual_stocks(self):
        """
        Fallback method to collect data for each stock individually
        when batch collection fails.

        Returns:
            Dict mapping each symbol to its DataFrame of price data
        """
        logger.info("Using individual collection for each stock")
        result = {}

        for symbol in STOCKS:
            try:
                # Get historical data for just today
                df = self.data_source.get_historical_data(
                    symbol=symbol,
                    interval=f"{COLLECTION_INTERVAL_MINUTES}m",
                    period="1d"
                )

                if not df.empty:
                    result[symbol] = df
                    logger.info(f"Individual collection successful for {symbol}")
                else:
                    logger.warning(f"Individual collection returned no data for {symbol}")
            except Exception as e:
                logger.error(f"Failed individual collection for {symbol}: {str(e)}")

        return result

    def collect_historical(self, days=3):
        """
        Collect historical price data for all configured stocks
        for the specified number of days.

        Args:
            days: Number of days of historical data to collect

        Returns:
            int: Number of data points successfully collected
        """
        logger.info(f"Starting historical data collection for {len(STOCKS)} stocks, {days} days")
        total_data_points = 0

        period = f"{days}d"
        interval = f"{COLLECTION_INTERVAL_MINUTES}m"

        for symbol in STOCKS:
            try:
                logger.info(f"Collecting historical data for {symbol}")

                # Get historical data
                df = self.data_source.get_historical_data(
                    symbol=symbol,
                    interval=interval,
                    period=period
                )

                if df.empty:
                    logger.warning(f"No historical data returned for {symbol}")
                    continue

                # Save each data point to the database
                saved_count = 0
                for _, row in df.iterrows():
                    try:
                        self.db.insert_price(
                            symbol=symbol,
                            timestamp=row['timestamp'],
                            open_price=row['open'],
                            high=row['high'],
                            low=row['low'],
                            close=row['close'],
                            volume=row['volume']
                        )
                        saved_count += 1
                    except Exception as inner_e:
                        logger.error(f"Error saving data point for {symbol}: {str(inner_e)}")

                logger.info(f"Saved {saved_count}/{len(df)} historical data points for {symbol}")
                total_data_points += saved_count

            except Exception as e:
                logger.error(f"Error collecting historical data for {symbol}: {str(e)}")

        logger.info(f"Historical collection completed: {total_data_points} data points saved")
        return total_data_points

    @staticmethod
    def is_trading_hours(timestamp=None):
        """
        Check if the current time (or specified timestamp) is within trading hours.

        Args:
            timestamp: Optional datetime to check. If None, uses current time.

        Returns:
            bool: True if within trading hours, False otherwise
        """
        from config.config import TRADING_HOURS
        import pytz

        if timestamp is None:
            timestamp = datetime.now()

        # Convert to timezone-aware datetime if needed
        israel_tz = pytz.timezone('Asia/Jerusalem')
        if timestamp.tzinfo is None:
            timestamp = israel_tz.localize(timestamp)
        else:
            timestamp = timestamp.astimezone(israel_tz)

        # Format time as HH:MM for comparison
        current_time = timestamp.strftime('%H:%M')

        # Check if it's a weekday (Monday to Friday)
        is_weekday = timestamp.weekday() < 5

        # Retrieve configured trading hours
        start_time = TRADING_HOURS["start"]
        end_time = TRADING_HOURS["end"]

        # Return True only if within time range and it's a weekday
        return start_time <= current_time <= end_time and is_weekday

    def collect_if_trading_hours(self):
        """
        Collect data only if currently within trading hours.

        Returns:
            int or None: Number of stocks collected if within trading hours, None otherwise
        """
        if self.is_trading_hours():
            logger.info("Within trading hours, collecting data")
            return self.collect_all_latest()
        else:
            logger.info("Outside trading hours, skipping collection")
            return None