# tests/test_scheduler.py
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from scheduler.scheduler import AppScheduler


class TestAppScheduler(unittest.TestCase):
    """
    Test suite for the AppScheduler implementation.
    """

    def setUp(self):
        """Set up test environment before each test method."""
        self.scheduler = AppScheduler()

    def tearDown(self):
        """Clean up after tests."""
        if self.scheduler.running:
            self.scheduler.stop()

    def test_initialization(self):
        """Test that the scheduler initializes correctly."""
        self.assertIsNotNone(self.scheduler)
        self.assertFalse(self.scheduler.running)
        self.assertEqual(str(self.scheduler.scheduler.timezone), 'Asia/Jerusalem')

    def test_start_stop(self):
        """Test starting and stopping the scheduler."""
        # Test starting
        result = self.scheduler.start()
        self.assertTrue(result)
        self.assertTrue(self.scheduler.running)

        # Test starting again (should return False)
        result = self.scheduler.start()
        self.assertFalse(result)

        # Test stopping
        result = self.scheduler.stop()
        self.assertTrue(result)
        self.assertFalse(self.scheduler.running)

        # Test stopping again (should return False)
        result = self.scheduler.stop()
        self.assertFalse(result)

    @patch('scheduler.scheduler.datetime')
    @patch('scheduler.scheduler.collect_data')
    def test_collect_data_if_trading_hours(self, mock_collect, mock_datetime):
        """Test the data collection function during trading hours."""

        # Mock the current time to be within trading hours
        mock_now = MagicMock()
        mock_now.strftime.return_value = '17:00'
        mock_now.weekday.return_value = 0  # Monday
        mock_datetime.now.return_value = mock_now

        # Ensure that is_within_trading_hours returns True
        with patch.object(self.scheduler, 'is_within_trading_hours', return_value=True):
            self.scheduler._collect_data_if_trading_hours()
            mock_collect.assert_called_once()

        mock_collect.reset_mock()

        # Mock the current time to be outside trading hours
        mock_now = MagicMock()
        mock_now.strftime.return_value = '15:00'
        mock_now.weekday.return_value = 0  # Monday
        mock_datetime.now.return_value = mock_now

        # Ensure that is_within_trading_hours returns False
        with patch.object(self.scheduler, 'is_within_trading_hours', return_value=False):
            self.scheduler._collect_data_if_trading_hours()
            mock_collect.assert_not_called()

    @patch('scheduler.scheduler.get_db')
    def test_cleanup_old_data(self, mock_get_db):
        """Test the data cleanup function."""
        mock_db = MagicMock()
        mock_db.delete_old_data.return_value = 10
        mock_get_db.return_value = mock_db

        # Run cleanup
        self.scheduler._cleanup_old_data()

        # Verify the database delete method was called
        mock_db.delete_old_data.assert_called_once()

        # Test exception handling
        mock_db.delete_old_data.side_effect = Exception("Test error")
        self.scheduler._cleanup_old_data()  # Should not raise exception

    def test_is_within_trading_hours(self):
        """Test checking if current time is within trading hours."""

        # Test during trading hours on a weekday
        weekday_trading = datetime(2023, 4, 17, 17, 0)  # יום שני, 17:00
        self.assertTrue(self.scheduler.is_within_trading_hours(weekday_trading))

        # Test outside trading hours on a weekday
        weekday_non_trading = datetime(2023, 4, 17, 15, 0)  # יום שני, 15:00
        self.assertFalse(self.scheduler.is_within_trading_hours(weekday_non_trading))

        # Test on the weekend
        weekend = datetime(2023, 4, 22, 17, 0)  # יום שבת, 17:00
        self.assertFalse(self.scheduler.is_within_trading_hours(weekend))

    def test_trading_hours_edge_cases(self):
        """Test edge cases for trading hours."""

        # Exactly at the start of trading hours
        start_time = datetime(2023, 4, 17, 16, 30)  # 16:30
        self.assertTrue(self.scheduler.is_within_trading_hours(start_time))

        # One minute before trading hours begin
        before_start = datetime(2023, 4, 17, 16, 29)  # 16:29
        self.assertFalse(self.scheduler.is_within_trading_hours(before_start))

        # Exactly at the end of trading hours
        end_time = datetime(2023, 4, 17, 23, 0)  # 23:00
        self.assertTrue(self.scheduler.is_within_trading_hours(end_time))

        # One minute after trading hours end
        after_end = datetime(2023, 4, 17, 23, 1)  # 23:01
        self.assertFalse(self.scheduler.is_within_trading_hours(after_end))

    def test_schedule_data_cleanup(self):
        """Test scheduling of the daily data cleanup job."""

        # Create a mock for the internal scheduler instance
        mock_scheduler = MagicMock()
        self.scheduler.scheduler = mock_scheduler  # Replace the real scheduler with the mock

        # Call the method under test
        self.scheduler.schedule_data_cleanup()

        # Verify that add_job was called once
        self.assertEqual(mock_scheduler.add_job.call_count, 1)

        # Get the call arguments
        args, kwargs = mock_scheduler.add_job.call_args

        # Check that the first argument is the cleanup function
        self.assertEqual(args[0], self.scheduler._cleanup_old_data)

        # Check that the job ID and name are correct in the keyword arguments
        self.assertEqual(kwargs.get('id'), 'data_cleanup')
        self.assertEqual(kwargs.get('name'), 'Clean Old Data')


