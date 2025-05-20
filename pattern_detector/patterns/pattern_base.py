# Abstract base class for stock pattern detection

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class PatternBase(ABC):
    """
    Abstract base class for stock pattern detection.
    All stock pattern detectors should inherit from this class and implement the required methods.
    """

    def __init__(self, **kwargs):
        """
        Initialize pattern detector with pattern-specific parameters.

        Args:
            **kwargs: Parameters specific to the pattern detection algorithm.
        """
        self.parameters = kwargs

    @abstractmethod
    def detect(self, data: pd.DataFrame) -> bool:
        """
        Detect if the pattern exists in the provided price data.

        Args:
            data: DataFrame containing price data with columns:
                 ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        Returns:
            bool: True if pattern is detected, False otherwise
        """
        pass

    @abstractmethod
    def get_pattern_name(self) -> str:
        """
        Get the name of this pattern.

        Returns:
            str: Name of the pattern this detector identifies
        """
        pass

    def get_pattern_details(self) -> Dict[str, Any]:
        """
        Get detailed information about the detected pattern.
        Default implementation returns basic info, can be overridden for more specific details.

        Returns:
            Dict[str, Any]: Details about the detected pattern
        """
        return {
            "pattern_name": self.get_pattern_name(),
            "parameters": self.parameters
        }

    @staticmethod
    def validate_data(data: pd.DataFrame) -> bool:
        """
        Validate that the provided data meets the requirements for pattern detection.

        Args:
            data: DataFrame to validate

        Returns:
            bool: True if data is valid, False otherwise
        """
        if not isinstance(data, pd.DataFrame) or data.empty:
            return False

        required_columns = ['timestamp', 'open', 'high', 'low', 'close']
        for col in required_columns:
            if col not in data.columns:
                return False

        return True