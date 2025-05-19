import os

os.environ["PYTEST_CURRENT_TEST"] = "true"
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock, patch, call
from data_collector.data_source_base import BaseDataSource
from data_collector.data_sources.yahoo_finance import YahooFinanceDataSource
from data_collector.collector import DataCollector
from config.config import STOCKS
from data_storage.storage import DatabaseStorage


class TestYahooFinanceDataSource(unittest.TestCase):
    """
    Unit tests for YahooFinanceDataSource implementation.
    """

    @patch('yfinance.Ticker')
    def test_initialization(self, mock_ticker):
        """Test that the YahooFinanceDataSource can be initialized"""
        data_source = YahooFinanceDataSource()
        self.assertIsNotNone(data_source)
        self.assertIsInstance(data_source, BaseDataSource)

    @patch('yfinance.Ticker')
    def test_get_latest_price(self, mock_ticker):
        """Test getting the latest price for a stock"""
        # Set up mock history DataFrame
        mock_history = pd.DataFrame({
            'Open': [150.0],
            'High': [155.0],
            'Low': [148.0],
            'Close': [153.0],
            'Volume': [1000000]
        }, index=[pd.Timestamp('2023-01-01 12:00:00')])

        # Mock Ticker behavior
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_history
        mock_ticker.return_value = mock_ticker_instance

        # Call get_latest_price
        data_source = YahooFinanceDataSource()
        result = data_source.get_latest_price('AAPL')

        # Verify output
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['open'], 150.0)
        self.assertEqual(result['high'], 155.0)
        self.assertEqual(result['low'], 148.0)
        self.assertEqual(result['close'], 153.0)
        self.assertEqual(result['volume'], 1000000)
        self.assertIsInstance(result['timestamp'], datetime)

    @patch('yfinance.download')
    def test_get_batch_data(self, mock_download):
        """Test getting batch data for multiple stocks"""
        # Mock yfinance DataFrame with MultiIndex columns
        index = pd.date_range(start='2023-01-01 12:00:00', periods=1, freq='5T')
        columns = pd.MultiIndex.from_product(
            [['AAPL', 'MSFT'], ['Open', 'High', 'Low', 'Close', 'Volume']],
            names=['Symbols', 'Attributes']
        )
        data = [[150.0, 155.0, 148.0, 153.0, 1000000, 250.0, 255.0, 248.0, 253.0, 2000000]]
        mock_data = pd.DataFrame(data, index=index, columns=columns)
        mock_download.return_value = mock_data

        # Call get_batch_data
        data_source = YahooFinanceDataSource()
        result = data_source.get_batch_data(['AAPL', 'MSFT'])

        # Verify output
        self.assertIn('AAPL', result)
        self.assertIn('MSFT', result)
        self.assertIsInstance(result['AAPL'], pd.DataFrame)
        self.assertIsInstance(result['MSFT'], pd.DataFrame)
        self.assertAlmostEqual(result['AAPL'].iloc[0]['close'], 153.0, places=1)
        self.assertAlmostEqual(result['MSFT'].iloc[0]['close'], 253.0, places=1)

    def test_validate_symbol(self):
        """Test symbol validation logic"""
        data_source = YahooFinanceDataSource()
        self.assertTrue(data_source.validate_symbol('AAPL'))
        self.assertTrue(data_source.validate_symbol('MSFT'))
        self.assertTrue(data_source.validate_symbol('BRK.A'))
        self.assertTrue(data_source.validate_symbol('BF-B'))
        self.assertFalse(data_source.validate_symbol(''))
        self.assertFalse(data_source.validate_symbol(123))
        self.assertFalse(data_source.validate_symbol(None))

    @patch('yfinance.Ticker')
    def test_retry_mechanism_succeeds_eventually(self, mock_ticker):
        """Test that the retry mechanism works when an operation fails first but succeeds later."""
        # Create data source with faster retry settings for testing
        data_source = YahooFinanceDataSource(max_retries=3, retry_delay=0.01)

        # Mock history DataFrame for successful attempt
        mock_history = pd.DataFrame({
            'Open': [150.0],
            'High': [155.0],
            'Low': [148.0],
            'Close': [153.0],
            'Volume': [1000000]
        }, index=[pd.Timestamp('2023-01-01 12:00:00')])

        # Set up mock to fail twice and then succeed
        mock_ticker_instance = MagicMock()

        # This side_effect will raise exceptions twice, then return the successful DataFrame
        side_effects = [
            Exception("API rate limit exceeded"),
            Exception("Connection error"),
            mock_history
        ]

        mock_ticker_instance.history.side_effect = side_effects
        mock_ticker.return_value = mock_ticker_instance

        # Call get_latest_price, which should retry and eventually succeed
        result = data_source.get_latest_price('AAPL')

        # Verify the function was called exactly 3 times
        self.assertEqual(mock_ticker_instance.history.call_count, 3)

        # Verify we got the expected result on the third try
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['close'], 153.0)

    @patch('yfinance.Ticker')
    def test_retry_exhaustion(self, mock_ticker):
        """Test that the function gives up and raises exception after all retries are exhausted."""
        # Create data source with faster retry settings for testing
        data_source = YahooFinanceDataSource(max_retries=2, retry_delay=0.01)

        # Set up mock to always fail
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.side_effect = Exception("Persistent API error")
        mock_ticker.return_value = mock_ticker_instance

        # Call get_latest_price, which should retry and then fail
        with self.assertRaises(Exception) as context:
            data_source.get_latest_price('AAPL')

        # Verify the error message
        self.assertIn("Persistent API error", str(context.exception))

        # Verify the function was called exactly max_retries times
        self.assertEqual(mock_ticker_instance.history.call_count, data_source.max_retries)

    @patch('data_collector.data_sources.yahoo_finance.time.sleep')
    @patch('yfinance.download')
    def test_retry_with_sleep(self, mock_download, mock_sleep):
        """Test that retry mechanism includes sleep between attempts."""
        # Create data source with faster retry settings for testing
        data_source = YahooFinanceDataSource(max_retries=3, retry_delay=0.5)

        # Set up mock to fail twice and then succeed
        mock_download.side_effect = [
            Exception("Network error"),
            Exception("Timeout error"),
            pd.DataFrame()  # Empty but valid result
        ]

        # Call method that should trigger retries
        data_source.get_batch_data(['AAPL'])

        # Verify sleep was called twice (after first and second failures)
        self.assertEqual(mock_sleep.call_count, 2)

        # Verify sleep was called with the correct delay
        mock_sleep.assert_has_calls([
            call(0.5),
            call(0.5)
        ])


class TestDataCollector(unittest.TestCase):
    """
    Unit tests for the DataCollector implementation using in-memory DB.
    """

    def setUp(self):
        # Create in-memory database for testing
        self.temp_db = DatabaseStorage(db_path=":memory:")

        # Override the global singleton instance directly
        import data_storage
        data_storage._db_instance = self.temp_db

    def test_initialization(self):
        """Test that the DataCollector can be initialized"""
        collector = DataCollector(db_instance=self.temp_db)
        self.assertIsNotNone(collector)
        self.assertIsInstance(collector.data_source, YahooFinanceDataSource)

        # Test custom data source injection
        mock_data_source = MagicMock(spec=BaseDataSource)
        collector = DataCollector(data_source=mock_data_source, db_instance=self.temp_db)
        self.assertEqual(collector.data_source, mock_data_source)

    @patch('data_collector.collector.DataCollector.is_trading_hours')
    def test_collect_all_latest(self, mock_is_trading_hours):
        """Test collecting latest prices for all stocks"""
        # Set up the mock to return True
        mock_is_trading_hours.return_value = True

        mock_data_source = MagicMock(spec=BaseDataSource)
        data_dict = {}
        for symbol in STOCKS:
            df = pd.DataFrame({
                'timestamp': [datetime.now()],
                'open': [150.0],
                'high': [155.0],
                'low': [148.0],
                'close': [153.0],
                'volume': [1000000]
            })
            data_dict[symbol] = df
        mock_data_source.get_batch_data.return_value = data_dict

        collector = DataCollector(data_source=mock_data_source, db_instance=self.temp_db)
        result = collector.collect_all_latest()

        # Verify mock_is_trading_hours was called
        mock_is_trading_hours.assert_called_once()

        # Verify results
        self.assertEqual(result, len(STOCKS))
        prices = self.temp_db.get_prices(STOCKS[0])
        self.assertEqual(len(prices), 1)
        self.assertAlmostEqual(prices.iloc[0]['close'], 153.0)

    @patch('data_collector.collector.datetime')
    def test_is_trading_hours(self, mock_datetime):
        """Test trading hours check functionality"""
        collector = DataCollector(db_instance=self.temp_db)

        # Create a mock that returns real datetime objects with our specified values

        # Time within trading hours - Monday 17:30
        monday_time = datetime(2023, 5, 15, 17, 30)  # Monday, 17:30
        mock_datetime.now.return_value = monday_time
        self.assertTrue(collector.is_trading_hours())

        # Time outside trading hours - Monday 15:30
        monday_early = datetime(2023, 5, 15, 15, 30)  # Monday, 15:30
        mock_datetime.now.return_value = monday_early
        self.assertFalse(collector.is_trading_hours())

        # Boundary test at start of trading hours - Monday 16:30
        monday_start = datetime(2023, 5, 15, 16, 30)  # Monday, 16:30
        mock_datetime.now.return_value = monday_start
        self.assertTrue(collector.is_trading_hours())

        # Boundary test at end of trading hours - Monday 23:00
        monday_end = datetime(2023, 5, 15, 23, 0)  # Monday, 23:00
        mock_datetime.now.return_value = monday_end
        self.assertTrue(collector.is_trading_hours())

        # Weekend test - Saturday 17:30
        saturday = datetime(2023, 5, 20, 17, 30)  # Saturday, 17:30
        mock_datetime.now.return_value = saturday
        self.assertFalse(collector.is_trading_hours())

    @patch('data_collector.collector.DataCollector.is_trading_hours')
    def test_collect_during_trading_hours(self, mock_is_trading_hours):
        """Test that collection occurs only during trading hours"""
        # Mock batch collection
        mock_data_source = MagicMock(spec=BaseDataSource)
        mock_data_source.get_batch_data.return_value = {}

        collector = DataCollector(data_source=mock_data_source, db_instance=self.temp_db)

        # Test when outside trading hours
        mock_is_trading_hours.return_value = False
        result = collector.collect_all_latest()

        # Should return 0 and not call data source
        self.assertEqual(result, 0)
        mock_data_source.get_batch_data.assert_not_called()

        # Test when inside trading hours
        mock_is_trading_hours.return_value = True
        collector.collect_all_latest()

        # Should call data source
        mock_data_source.get_batch_data.assert_called_once()

    @patch('data_collector.collector.DataCollector.is_trading_hours')
    def test_fallback_to_individual_collection(self, mock_is_trading_hours):
        """Test fallback to individual collection when batch collection fails"""
        mock_is_trading_hours.return_value = True

        # Mock data source with batch collection that fails
        mock_data_source = MagicMock(spec=BaseDataSource)
        mock_data_source.get_batch_data.side_effect = Exception("API error")

        # Mock successful individual collection
        mock_df = pd.DataFrame({
            'timestamp': [datetime.now()],
            'open': [150.0],
            'high': [155.0],
            'low': [148.0],
            'close': [153.0],
            'volume': [1000000]
        })
        mock_data_source.get_historical_data.return_value = mock_df

        # Create collector and test
        collector = DataCollector(data_source=mock_data_source, db_instance=self.temp_db)
        result = collector.collect_all_latest()

        # Should fall back to individual collection
        self.assertEqual(result, len(STOCKS))
        self.assertEqual(mock_data_source.get_historical_data.call_count, len(STOCKS))

    @patch('data_collector.collector.logger')
    @patch('data_collector.collector.DataCollector.is_trading_hours')
    def test_error_logging(self, mock_is_trading_hours, mock_logger):
        """Test that errors are properly logged"""
        mock_is_trading_hours.return_value = True

        # Mock data source that raises an exception
        mock_data_source = MagicMock(spec=BaseDataSource)
        mock_data_source.get_batch_data.side_effect = Exception("Test error")
        mock_data_source.get_historical_data.side_effect = Exception("Another test error")

        # Test collect_all_latest error logging
        collector = DataCollector(data_source=mock_data_source, db_instance=self.temp_db)
        collector.collect_all_latest()

        # Check that errors were logged
        mock_logger.error.assert_called()

        # Reset mock for historical collection test
        mock_logger.reset_mock()

        # Test error logging in historical collection
        collector.collect_historical(days=1)
        mock_logger.error.assert_called()


if __name__ == '__main__':
    unittest.main()