# Define data models and database schema for the stock price data
import sqlite3
from datetime import datetime


def create_tables(conn):
    """
    Create the necessary tables for storing stock price data if they don't exist.

    Args:
        conn: SQLite connection object

    This creates:
    1. stock_prices - Stores OHLCV data for each stock at specific timestamps
    """
    cursor = conn.cursor()

    # Create stock_prices table with all necessary fields and indexes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        created_at INTEGER NOT NULL
    )
    ''')

    # Create indexes for faster querying
    # Index for symbol+timestamp searches (our most common query pattern)
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_stock_timestamp 
    ON stock_prices (symbol, timestamp)
    ''')

    # Index for timestamp only (used for cleanup of old data)
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_timestamp 
    ON stock_prices (timestamp)
    ''')

    conn.commit()


def timestamp_to_db(dt):
    """
    Convert a datetime object to Unix timestamp (seconds since epoch)
    for storage in SQLite.

    Args:
        dt: datetime object

    Returns:
        int: Unix timestamp in seconds
    """
    if isinstance(dt, datetime):
        return int(dt.timestamp())
    return dt  # Assume it's already a timestamp if not a datetime


def db_to_timestamp(ts):
    """
    Convert a Unix timestamp from database to a datetime object.

    Args:
        ts: int Unix timestamp in seconds

    Returns:
        datetime: datetime object
    """
    return datetime.fromtimestamp(ts)