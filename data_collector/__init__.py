# data_sources/__init__.py
import os

from data_collector.data_source_base import BaseDataSource
from data_collector.data_sources.yahoo_finance import YahooFinanceDataSource
from data_collector.collector import DataCollector

# Only create the singleton if not running tests
if "PYTEST_CURRENT_TEST" not in os.environ:
    collector = DataCollector()


# Helper functions that use the singleton
def collect_data():
    """
    Utility function to collect data using the singleton collector instance.

    Returns:
        int: Number of stocks collected
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Starting data collection")
    return collector.collect_all_latest()


def collect_historical_data(days=3):
    """
    Utility function to collect historical data using the singleton collector instance.

    Args:
        days: Number of days of historical data to collect

    Returns:
        int: Number of data points collected
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Starting historical data collection for {days} days")
    return collector.collect_historical(days)


def create_collector():
    """
    Factory function to create a new DataCollector instance with default settings.

    Returns:
        DataCollector: A configured collector instance
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Creating new DataCollector instance")
    return DataCollector(data_source=YahooFinanceDataSource())


# Export the main classes and functions
__all__ = ['BaseDataSource', 'YahooFinanceDataSource', 'DataCollector',
           'collector', 'collect_data', 'collect_historical_data', 'create_collector']