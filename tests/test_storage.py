import unittest
import tempfile
import os
from datetime import datetime, timedelta
from data_storage.storage import DatabaseStorage


class TestDatabaseStorage(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db = DatabaseStorage(self.temp_db.name)

    def tearDown(self):
        # Clean up the temporary file after tests
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_insert_and_get_prices(self):
        # Test inserting data and reading it back
        now = datetime.now()
        self.db.insert_price("AAPL", now, 150.0, 155.0, 148.0, 153.0, 1000000)

        # Retrieve the data
        df = self.db.get_prices("AAPL")

        # Verify the results
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['close'], 153.0)

    def test_delete_old_data(self):
        # Insert old and new data
        old_time = datetime.now() - timedelta(days=4)
        now = datetime.now()

        self.db.insert_price("AAPL", old_time, 140.0, 145.0, 138.0, 143.0, 900000)
        self.db.insert_price("AAPL", now, 150.0, 155.0, 148.0, 153.0, 1000000)

        # Check that there are 2 records
        df_before = self.db.get_prices("AAPL")
        self.assertEqual(len(df_before), 2)

        # Delete old data
        deleted = self.db.delete_old_data(3)
        self.assertEqual(deleted, 1)

        # Check that only one record remains
        df_after = self.db.get_prices("AAPL")
        self.assertEqual(len(df_after), 1)
        self.assertAlmostEqual(df_after.iloc[0]['close'], 153.0)

    def test_get_prices_by_time_range(self):
        # Test filtering by time range
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)

        # Insert 3 data points
        self.db.insert_price("AAPL", two_days_ago, 140.0, 145.0, 138.0, 143.0, 900000)
        self.db.insert_price("AAPL", yesterday, 145.0, 150.0, 143.0, 148.0, 950000)
        self.db.insert_price("AAPL", now, 150.0, 155.0, 148.0, 153.0, 1000000)

        # Filter by time
        df = self.db.get_prices("AAPL", yesterday, now)
        self.assertEqual(len(df), 2)

        # Verify that the correct data was returned
        self.assertAlmostEqual(df.iloc[0]['close'], 148.0)
        self.assertAlmostEqual(df.iloc[1]['close'], 153.0)
