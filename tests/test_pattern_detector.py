import os

from utils.logger import logger

os.environ["PYTEST_CURRENT_TEST"] = "true"  # Ensure we're using test mode
import pytest
import pandas as pd
import numpy as np
from pattern_detector.patterns.cup_and_handle import CupAndHandlePattern
from pattern_detector.detector import PatternDetector
from utils.logger import logger


class TestCupAndHandlePattern:
    """
    Test suite for the Cup and Handle pattern detector.
    """
    
    def setup_method(self):
        """Set up test environment before each test method."""
        logger.get_logger(" Setting up test method")

        self.detector = CupAndHandlePattern()

    def test_initialization(self):
        """Test that the detector initializes correctly with default parameters."""
        assert self.detector.cup_depth_min == 0.1
        assert self.detector.cup_depth_max == 0.60
        assert self.detector.handle_depth_min == 0.1
        assert self.detector.handle_depth_max == 0.6
        assert self.detector.handle_length_max == 0.7

        # Test custom parameters
        custom_detector = CupAndHandlePattern(
            cup_depth_min=0.10,
            cup_depth_max=0.40,
            handle_depth_min=0.15,
            handle_depth_max=0.30,
            handle_length_max=0.3
        )
        assert custom_detector.cup_depth_min == 0.10
        assert custom_detector.cup_depth_max == 0.40
        assert custom_detector.handle_depth_min == 0.15
        assert custom_detector.handle_depth_max == 0.30
        assert custom_detector.handle_length_max == 0.3

    def test_validation(self):
        """Test data validation functionality."""
        # Valid data
        data = pd.DataFrame({
            'timestamp': pd.date_range(start='2023-01-01', periods=20),
            'open': np.random.random(20),
            'high': np.random.random(20),
            'low': np.random.random(20),
            'close': np.random.random(20),
            'volume': np.random.randint(1000, 10000, 20)
        })
        assert self.detector.validate_data(data) is True
        
        # Invalid data - missing columns
        invalid_data = pd.DataFrame({
            'timestamp': pd.date_range(start='2023-01-01', periods=20),
            'close': np.random.random(20)
        })
        assert self.detector.validate_data(invalid_data) is False
        
        # Empty data
        empty_data = pd.DataFrame()
        assert self.detector.validate_data(empty_data) is False

    def test_positive_pattern_detection(self):
        """Test detection of a clear Cup and Handle pattern."""
        # Create a more pronounced cup and handle pattern
        # with clearer peaks and troughs
        prices = [100] * 3  # Initial stable price
        # Left side of cup (declining more steeply)
        for i in range(1, 11):
            prices.append(100 - i * 2)  # More pronounced decline

        prices += [80] * 3  # Cup bottom (more flat)

        # Right side of cup (rising more steeply)
        for i in range(1, 11):
            prices.append(80 + i * 2)  # More pronounced rise

        prices += [100] * 3  # Stable at the rim

        # Handle with clearer drop
        for i in range(1, 6):
            prices.append(100 - i * 2)  # Clear drop for handle

        prices += [90] * 3  # Handle bottom

        # Rising from handle
        for i in range(1, 8):
            prices.append(90 + i)

        # Generate timestamps with the exact number of periods needed
        timestamps = pd.date_range(start='2023-01-01', periods=len(prices), freq='5min')

        data = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices,
            'high': [p + 1 for p in prices],
            'low': [p - 1 for p in prices],
            'close': prices,
            'volume': [10000] * len(prices)
        })

        # Test detection
        result = self.detector.detect(data)
        assert result is True, "Failed to detect a clear Cup and Handle pattern"

    def test_negative_pattern_detection(self):
        """Test that non-patterns are not detected as Cup and Handle."""
        prices = [100 - i for i in range(50)]

        timestamps = pd.date_range(start='2023-01-01', periods=len(prices), freq='5min')

        data = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices,
            'high': [p + 1 for p in prices],
            'low': [p - 1 for p in prices],
            'close': prices,
            'volume': [10000] * len(prices)
        })

        # Test detection
        result = self.detector.detect(data)
        assert result is False, "Incorrectly detected Cup and Handle in a downtrend"

    def test_v_shape_not_detected(self):
        """Test that a V-shape is not detected as Cup and Handle (need U-shape)."""
        prices = [100] * 5
        prices += [100 - i * 2 for i in range(1, 11)]  # Sharp decline
        prices += [80 + i * 2 for i in range(1, 11)]  # Sharp rise
        prices += [100] * 5
        prices += [100 - i for i in range(1, 6)]  # Handle part
        prices += [95 + i for i in range(1, 15)]  # Final rise

        timestamps = pd.date_range(start='2023-01-01', periods=len(prices), freq='5min')

        data = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices,
            'high': [p + 1 for p in prices],
            'low': [p - 1 for p in prices],
            'close': prices,
            'volume': [10000] * len(prices)
        })

        # V-shapes should not be detected as Cup and Handle
        result = self.detector.detect(data)
        assert result is False, "Incorrectly detected Cup and Handle in a V-shape"

    def test_handle_too_deep(self):
        """Test that patterns with too deep handles are not detected."""
        prices = [100] * 5
        prices += [100 - i for i in range(1, 16)]  # Left side of cup
        prices += [85] * 5  # Cup bottom
        prices += [85 + i for i in range(1, 16)]  # Right side of cup
        prices += [100] * 5
        # Handle that's too deep (more than 50% of cup depth)
        prices += [100 - i for i in range(1, 9)]  # Handle drop (deeper than allowed)
        prices += [92] * 3  # Handle bottom
        prices += [92 + i for i in range(1, 9)]  # Rising from handle

        timestamps = pd.date_range(start='2023-01-01', periods=len(prices), freq='5min')

        data = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices,
            'high': [p + 1 for p in prices],
            'low': [p - 1 for p in prices],
            'close': prices,
            'volume': [10000] * len(prices)
        })

        result = self.detector.detect(data)
        assert result is False, "Incorrectly detected Cup and Handle with handle too deep"
        
    def test_insufficient_data(self):
        """Test behavior with insufficient data points."""
        # Only 5 data points - not enough for pattern detection
        timestamps = pd.date_range(start='2023-01-01', periods=5, freq='5min')
        prices = [100, 95, 90, 95, 100]
        
        data = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices,
            'high': [p + 1 for p in prices],
            'low': [p - 1 for p in prices],
            'close': prices,
            'volume': [10000] * len(prices)
        })
        
        result = self.detector.detect(data)
        assert result is False, "Should not detect pattern with insufficient data"


class TestPatternDetector:
    """
    Test suite for the main PatternDetector class.
    """
    
    def setup_method(self):
        """Set up test environment before each test method."""
        self.detector = PatternDetector()
        
    def test_initialization(self):
        """Test that the detector initializes correctly."""
        assert "cup_and_handle" in self.detector.pattern_detectors
        assert isinstance(self.detector.pattern_detectors["cup_and_handle"], CupAndHandlePattern)
        
    def test_get_available_patterns(self):
        """Test retrieving available pattern types."""
        patterns = self.detector.get_available_patterns()
        assert "cup_and_handle" in patterns

    def test_detect_pattern_with_custom_data(self):
        """Test pattern detection with custom data."""
        prices = [100] * 5
        prices += [100 - i for i in range(1, 16)]  # Left side of cup
        prices += [85] * 5  # Cup bottom
        prices += [85 + i for i in range(1, 16)]  # Right side of cup
        prices += [100] * 5
        prices += [100 - i for i in range(1, 6)]  # Handle
        prices += [95] * 3  # Handle bottom
        prices += [95 + i for i in range(1, 7)]  # Rising from handle

        timestamps = pd.date_range(start='2023-01-01', periods=len(prices), freq='5min')

        data = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices,
            'high': [p + 1 for p in prices],
            'low': [p - 1 for p in prices],
            'close': prices,
            'volume': [10000] * len(prices)
        })

        # Test with custom data
        result = self.detector.detect_pattern(
            symbol="TEST",
            pattern_type="cup_and_handle",
            custom_data=data
        )
        assert result is True

    def test_detect_all_patterns(self):
        """Test detection of all available patterns."""
        prices = [100] * 5
        prices += [100 - i for i in range(1, 16)]  # Left side of cup
        prices += [85] * 5  # Cup bottom
        prices += [85 + i for i in range(1, 16)]  # Right side of cup
        prices += [100] * 5
        prices += [100 - i for i in range(1, 6)]  # Handle
        prices += [95] * 3  # Handle bottom
        prices += [95 + i for i in range(1, 7)]  # Rising from handle

        timestamps = pd.date_range(start='2023-01-01', periods=len(prices), freq='5min')

        data = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices,
            'high': [p + 1 for p in prices],
            'low': [p - 1 for p in prices],
            'close': prices,
            'volume': [10000] * len(prices)
        })

        # Mock the database method to return our test data
        self.detector.db.get_prices = lambda symbol, start_time, end_time: data

        # Test detect_all_patterns
        results = self.detector.detect_all_patterns(symbol="TEST")
        assert "cup_and_handle" in results
        assert results["cup_and_handle"] is True
        
    def test_register_pattern_detector(self):
        """Test registering a custom pattern detector."""
        # Create a mock pattern detector
        class MockPatternDetector(CupAndHandlePattern):
            def get_pattern_name(self):
                return "Mock Pattern"
                
        mock_detector = MockPatternDetector()
        
        # Register the mock detector
        self.detector.register_pattern_detector("mock_pattern", mock_detector)
        
        # Verify it was registered
        assert "mock_pattern" in self.detector.pattern_detectors
        assert self.detector.pattern_detectors["mock_pattern"] is mock_detector
        
        # Verify it appears in available patterns
        patterns = self.detector.get_available_patterns()
        assert "mock_pattern" in patterns


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
