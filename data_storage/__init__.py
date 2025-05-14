# data_storage/__init__.py
# This module handles database operations for stock price data
from data_storage.storage import DatabaseStorage

# Create a singleton instance for global use
db = DatabaseStorage()

# Export the main classes and functions
__all__ = ['DatabaseStorage', 'db']