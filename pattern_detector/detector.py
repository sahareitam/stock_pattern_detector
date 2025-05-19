# Main pattern detector module

from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta

from pattern_detector.patterns.pattern_base import PatternBase
from pattern_detector.patterns.cup_and_handle import CupAndHandlePattern
from data_storage import get_db

from utils.logger import get_logger
logger = get_logger(__name__)


class PatternDetector:
    """
    Main pattern detector class that coordinates pattern detection
    for different stock symbols and pattern types.
    """

    def __init__(self):
        """
        Initialize the pattern detector with available pattern detectors.
        """
        # Initialize pattern detectors
        self.pattern_detectors = {
            "cup_and_handle": CupAndHandlePattern()
        }

        # Database instance - this is lazily loaded only if needed
        self._db = None

    @property
    def db(self):
        """Lazy-loaded database instance"""
        if self._db is None:
            self._db = get_db()
        return self._db

    def detect_pattern(self, symbol: str, pattern_type: str = "cup_and_handle",
                       days: int = 3, custom_data: Optional[pd.DataFrame] = None) -> bool:
        """
        Detect if a specific pattern exists for a given stock symbol.

        Args:
            symbol: Stock symbol to analyze
            pattern_type: Type of pattern to detect (default: "cup_and_handle")
            days: Number of days of data to analyze (default: 3)
            custom_data: Optional pre-loaded DataFrame to use instead of fetching from DB

        Returns:
            bool: True if pattern is detected, False otherwise
        """
        # Check if pattern type is supported
        if pattern_type not in self.pattern_detectors:
            logger.error(f"Unsupported pattern type: {pattern_type}")
            return False

        # Get the appropriate pattern detector
        pattern_detector = self.pattern_detectors[pattern_type]

        # Get the data - either from custom_data or from the database
        if custom_data is not None:
            data = custom_data
        else:
            # Calculate start time (now - days)
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)

            try:
                # Get data from database
                data = self.db.get_prices(symbol, start_time, end_time)
            except Exception as e:
                logger.error(f"Error retrieving data for {symbol}: {str(e)}")
                return False

        # Check if we have data
        if data is None or data.empty:
            logger.warning(f"No data available for {symbol}")
            return False

        # Detect pattern
        try:
            result = pattern_detector.detect(data)
            if result:
                logger.info(f"Pattern '{pattern_type}' detected for {symbol}")
            else:
                logger.info(f"Pattern '{pattern_type}' not detected for {symbol}")
            return result
        except Exception as e:
            logger.error(f"Error detecting pattern for {symbol}: {str(e)}")
            return False

    def get_available_patterns(self) -> List[str]:
        """
        Get a list of available pattern types.

        Returns:
            List[str]: List of available pattern type names
        """
        return list(self.pattern_detectors.keys())

    def detect_all_patterns(self, symbol: str, days: int = 3) -> Dict[str, bool]:
        """
        Detect all available patterns for a given stock symbol.

        Args:
            symbol: Stock symbol to analyze
            days: Number of days of data to analyze (default: 3)

        Returns:
            Dict[str, bool]: Dictionary mapping pattern types to detection results
        """
        results = {}

        # Calculate start time (now - days)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        try:
            # Get data once for all pattern detections
            data = self.db.get_prices(symbol, start_time, end_time)

            # If no data, return all patterns as False
            if data is None or data.empty:
                logger.warning(f"No data available for {symbol}")
                return {pattern: False for pattern in self.pattern_detectors.keys()}

            # Detect each pattern
            for pattern_type, detector in self.pattern_detectors.items():
                try:
                    results[pattern_type] = detector.detect(data)
                except Exception as e:
                    logger.error(f"Error detecting {pattern_type} for {symbol}: {str(e)}")
                    results[pattern_type] = False
        except Exception as e:
            logger.error(f"Error retrieving data for {symbol}: {str(e)}")
            results = {pattern: False for pattern in self.pattern_detectors.keys()}

        return results

    def register_pattern_detector(self, pattern_type: str, detector: PatternBase) -> None:
        """
        Register a new pattern detector.

        Args:
            pattern_type: Type name for the pattern
            detector: Pattern detector instance
        """
        if not isinstance(detector, PatternBase):
            raise TypeError("Pattern detector must be an instance of PatternBase")

        self.pattern_detectors[pattern_type] = detector
        logger.info(f"Registered pattern detector for '{pattern_type}'")


# Singleton instance
_detector_instance = None


def get_detector():
    """
    Get the singleton pattern detector instance.

    Returns:
        PatternDetector: Singleton instance
    """
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = PatternDetector()
    return _detector_instance