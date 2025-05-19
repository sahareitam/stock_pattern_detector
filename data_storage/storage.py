# data_storage/storage.py
import os
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import threading

from config.config import DATABASE, DATA_RETENTION_DAYS
from data_storage.models import create_tables, timestamp_to_db, db_to_timestamp


class DatabaseStorage:
    """
    Handles all database operations for storing and retrieving stock price data.
    Uses SQLite as the backend database.
    """

    def __init__(self, db_path=None):
        """
        Initialize the database connection.

        Args:
            db_path: Optional path to the SQLite database file.
                    If not provided, uses the path from config.
        """
        if db_path is None:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(DATABASE["path"]), exist_ok=True)
            db_path = DATABASE["path"]

        self.db_path = db_path
        self.conn = None
        self._lock = threading.RLock()  # Add a lock for thread safety
        self._connect()

    def _connect(self):
        """Establish a connection to the SQLite database and create tables if needed."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Configure for better concurrent access
        self.conn.execute("PRAGMA journal_mode = WAL")
        # Create tables if they don't exist
        create_tables(self.conn)

    def _ensure_connection(self):
        """Ensure there is an active database connection."""
        if self.conn is None:
            self._connect()

    def insert_price(self, symbol, timestamp, open_price=None, high=None, low=None, close=None, volume=None):
        """
        Insert a new stock price record into the database.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            timestamp: Datetime object or Unix timestamp for the price data
            open_price: Opening price
            high: Highest price
            low: Lowest price
            close: Closing price
            volume: Trading volume

        Example:
            db.insert_price('AAPL', datetime.now(), 150.25, 152.30, 149.80, 151.95, 1200000)
        """
        self._ensure_connection()

        # Use lock to ensure thread safety
        with self._lock:
            cursor = self.conn.cursor()

            # Convert timestamp to Unix timestamp if it's a datetime
            ts = timestamp_to_db(timestamp)

            # Get current time for created_at
            now = int(datetime.now().timestamp())

            cursor.execute('''
            INSERT INTO stock_prices 
            (symbol, timestamp, open, high, low, close, volume, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, ts, open_price, high, low, close, volume, now))

            self.conn.commit()
            return cursor.lastrowid

    def get_prices(self, symbol, start_time=None, end_time=None):
        """
        Retrieve price data for a specific stock within a time range.

        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            start_time: Start of the time range (datetime or Unix timestamp)
            end_time: End of the time range (datetime or Unix timestamp)

        Returns:
            DataFrame: Pandas DataFrame with the price data
        """
        self._ensure_connection()

        # Convert datetime objects to Unix timestamps if needed
        if start_time is not None:
            start_time = timestamp_to_db(start_time)
        if end_time is not None:
            end_time = timestamp_to_db(end_time)

        # Build the query based on provided parameters
        query = "SELECT symbol, timestamp, open, high, low, close, volume FROM stock_prices WHERE symbol = ?"
        params = [symbol]

        if start_time is not None:
            query += " AND timestamp >= ?"
            params.append(start_time)

        if end_time is not None:
            query += " AND timestamp <= ?"
            params.append(end_time)

        # Order by timestamp to ensure chronological order
        query += " ORDER BY timestamp ASC"

        # Use lock to ensure thread safety
        with self._lock:
            # Execute query and fetch all results
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        if not rows:
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # Convert to DataFrame and fix data types
        df = pd.DataFrame(rows, columns=['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # Convert timestamp column to datetime objects
        df['timestamp'] = df['timestamp'].apply(db_to_timestamp)

        return df

    def delete_old_data(self, retention_days=None):
        """
        Delete price data older than the specified retention period.

        Args:
            retention_days: Number of days to keep data for (default: uses config value)

        Returns:
            int: Number of records deleted
        """
        self._ensure_connection()

        if retention_days is None:
            retention_days = DATA_RETENTION_DAYS

        # Calculate cutoff timestamp
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        cutoff_timestamp = timestamp_to_db(cutoff_date)

        # Use lock to ensure thread safety
        with self._lock:
            # Delete records older than cutoff
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM stock_prices WHERE timestamp < ?", (cutoff_timestamp,))
            deleted_count = cursor.rowcount
            self.conn.commit()

        return deleted_count

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Destructor to ensure connection is closed when object is deleted."""
        self.close()