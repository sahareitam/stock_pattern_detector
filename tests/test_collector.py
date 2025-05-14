import os
os.environ["PYTEST_CURRENT_TEST"] = "true"
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock, patch
from data_collector.data_source_base import BaseDataSource
from data_collector.data_sources.yahoo_finance import YahooFinanceDataSource
from data_collector.collector import DataCollector
from config.config import STOCKS
import data_storage  # Needed to patch the singleton db
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

    def test_collect_all_latest(self):
        """Test collecting latest prices for all stocks"""
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

        self.assertEqual(result, len(STOCKS))
        prices = self.temp_db.get_prices(STOCKS[0])
        self.assertEqual(len(prices), 1)
        self.assertAlmostEqual(prices.iloc[0]['close'], 153.0)

    @patch('data_collector.collector.datetime')
    def test_is_trading_hours(self, mock_datetime):
        """Test trading hours check functionality"""
        collector = DataCollector(db_instance=self.temp_db)

        # Time within trading hours
        mock_time = datetime(2023, 1, 1, 17, 30)
        mock_datetime.now.return_value = mock_time
        self.assertTrue(collector.is_trading_hours())

        # Time outside trading hours
        mock_time = datetime(2023, 1, 1, 15, 30)
        mock_datetime.now.return_value = mock_time
        self.assertFalse(collector.is_trading_hours())

        # Boundary test at start of trading hours
        mock_time = datetime(2023, 1, 1, 16, 30)
        mock_datetime.now.return_value = mock_time
        self.assertTrue(collector.is_trading_hours())

        # Boundary test at end of trading hours
        mock_time = datetime(2023, 1, 1, 23, 0)
        mock_datetime.now.return_value = mock_time
        self.assertTrue(collector.is_trading_hours())
