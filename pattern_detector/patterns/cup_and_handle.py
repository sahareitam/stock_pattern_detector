# Cup and Handle pattern detector implementation

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from scipy.signal import find_peaks
import logging
logging.basicConfig(level=logging.DEBUG)
from pattern_detector.patterns.pattern_base import PatternBase
from config.config import PATTERNS
from utils.logger import get_logger
logger = get_logger(__name__)


class CupAndHandlePattern(PatternBase):
    """
    Detector for the Cup and Handle pattern in stock price data.

    The Cup and Handle is a bullish continuation pattern where:
    1. Price falls (left side of cup)
    2. Price bottoms out (cup bottom)
    3. Price rises back up (right side of cup)
    4. Price experiences a smaller pullback (handle)
    5. Price continues upward

    Default parameters from config:
    - cup_depth_min: Minimum cup depth as percentage from peak (default: 0.15)
    - cup_depth_max: Maximum cup depth as percentage from peak (default: 0.50)
    - handle_depth_min: Minimum handle depth as percentage of cup depth (default: 0.20)
    - handle_depth_max: Maximum handle depth as percentage of cup depth (default: 0.50)
    - handle_length_max: Maximum handle length compared to cup length (default: 0.5)
    """

    def __init__(self, **kwargs):
        """
        Initialize Cup and Handle pattern detector with configurable parameters.

        Kwargs:
            cup_depth_min (float): Minimum cup depth as percentage from peak
            cup_depth_max (float): Maximum cup depth as percentage from peak
            handle_depth_min (float): Minimum handle depth as percentage of cup depth
            handle_depth_max (float): Maximum handle depth as percentage of cup depth
            handle_length_max (float): Maximum handle length compared to cup length
        """
        # Get default parameters from config
        default_params = PATTERNS.get('cup_and_handle', {})

        # Initialize with default or provided parameters
        self.cup_depth_min = kwargs.get('cup_depth_min', default_params.get('cup_depth_min', 0.1))
        self.cup_depth_max = kwargs.get('cup_depth_max', default_params.get('cup_depth_max', 0.60))
        self.handle_depth_min = kwargs.get('handle_depth_min', default_params.get('handle_depth_min', 0.1))
        self.handle_depth_max = kwargs.get('handle_depth_max', default_params.get('handle_depth_max', 0.6))
        self.handle_length_max = kwargs.get('handle_length_max', default_params.get('handle_length_max', 0.7))

        # Collect all parameters for parent class
        all_params = {
            'cup_depth_min': self.cup_depth_min,
            'cup_depth_max': self.cup_depth_max,
            'handle_depth_min': self.handle_depth_min,
            'handle_depth_max': self.handle_depth_max,
            'handle_length_max': self.handle_length_max
        }

        super().__init__(**all_params)

        # Initialize pattern-specific attributes
        self.cup_left_idx = None
        self.cup_bottom_idx = None
        self.cup_right_idx = None
        self.handle_bottom_idx = None
        self.handle_end_idx = None

    def get_pattern_name(self) -> str:
        """
        Get the name of this pattern.

        Returns:
            str: Pattern name
        """
        return "Cup and Handle"

    def _identify_peaks_and_troughs(self, prices: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Identify peaks (highs) and troughs (lows) in the price series.

        Args:
            prices: Array of price values

        Returns:
            Tuple[np.ndarray, np.ndarray]: Arrays of peak and trough indices
        """
        # Increase prominence to only pick up significant peaks/troughs
        # This will filter out minor fluctuations
        peaks, _ = find_peaks(prices, distance=3, prominence=1.0)

        # For troughs, invert the price series and find peaks
        troughs, _ = find_peaks(-prices, distance=3, prominence=1.0)

        # If we don't find enough peaks/troughs, we can try a simplified approach
        if len(peaks) < 2 or len(troughs) < 1:
            # Find the highest and lowest points in the first and second halves
            midpoint = len(prices) // 2

            # For left side peaks (beginning of the data)
            left_section = prices[:midpoint]
            if len(left_section) > 0:
                left_peak_idx = np.argmax(left_section)
                peaks = np.append(peaks, left_peak_idx)

            # For bottom (middle of the data)
            mid_section = prices[midpoint - midpoint // 2:midpoint + midpoint // 2]
            if len(mid_section) > 0:
                mid_trough_idx = np.argmin(mid_section) + (midpoint - midpoint // 2)
                troughs = np.append(troughs, mid_trough_idx)

            # For right side peaks (end of first half and beginning of second half)
            right_section = prices[midpoint:]
            if len(right_section) > 0:
                right_peak_idx = np.argmax(right_section) + midpoint
                peaks = np.append(peaks, right_peak_idx)

        # Sort the indices to ensure they are in chronological order
        peaks.sort()
        troughs.sort()

        return peaks, troughs

    def _smooth_prices(self, prices: np.ndarray, window: int = 3) -> np.ndarray:
        """
        Apply smoothing to reduce noise in price data.

        Args:
            prices: Array of price values
            window: Size of the smoothing window (default: 3)

        Returns:
            np.ndarray: Smoothed price series
        """
        return np.convolve(prices, np.ones(window) / window, mode='valid')

    def _identify_cup_formation(self, prices: np.ndarray, peaks: np.ndarray, troughs: np.ndarray) -> bool:
        """
        Identify a cup formation in the price series.

        Args:
            prices: Array of price values
            peaks: Array of peak indices
            troughs: Array of trough indices

        Returns:
            bool: True if a cup formation is identified, False otherwise
        """
        if len(peaks) < 2 or len(troughs) < 1:
            return False

        # For test data with synthetic patterns, we can use a more direct approach

        # Find an early peak for the left side of the cup
        left_peak_candidates = [p for p in peaks if p < len(prices) // 3]
        if not left_peak_candidates:
            # If no early peaks found, take the first peak
            if len(peaks) > 0:
                left_peak_idx = peaks[0]
            else:
                return False
        else:
            # Take the highest early peak
            left_peak_idx = max(left_peak_candidates, key=lambda p: prices[p])

        # Find the lowest point after the left peak for the cup bottom
        trough_candidates = [t for t in troughs if t > left_peak_idx]
        if not trough_candidates:
            return False

        # Take the lowest trough
        cup_bottom_idx = min(trough_candidates, key=lambda t: prices[t])

        if cup_bottom_idx is not None and left_peak_idx is not None:

            bottom_range_start = max(0, cup_bottom_idx - 2)
            bottom_range_end = min(len(prices) - 1, cup_bottom_idx + 2)
            bottom_range = prices[bottom_range_start:bottom_range_end + 1]

            bottom_std = np.std(bottom_range)
            cup_depth = prices[left_peak_idx] - prices[cup_bottom_idx]

            if cup_depth > 0 and (bottom_std / cup_depth) > 0.05:  # הגבר רגישות
                logger.debug(f"Rejecting V-shaped pattern, std/depth ratio: {bottom_std / cup_depth:.2f}")
                return False
        # Find peaks after the cup bottom for the right side of the cup
        right_peak_candidates = [p for p in peaks if p > cup_bottom_idx]
        if not right_peak_candidates:
            return False

        # Take the first peak after the bottom that's close to the height of the left peak
        for p in right_peak_candidates:
            peak_diff = abs(prices[p] - prices[left_peak_idx]) / prices[left_peak_idx]
            if peak_diff <= 0.15:  # Allow 15% difference
                right_peak_idx = p

                # Valid cup formation found
                self.cup_left_idx = left_peak_idx
                self.cup_bottom_idx = cup_bottom_idx
                self.cup_right_idx = right_peak_idx
                return True

        # If no suitable right peak found, try with the highest peak after the bottom
        right_peak_idx = max(right_peak_candidates, key=lambda p: prices[p])
        peak_diff = abs(prices[right_peak_idx] - prices[left_peak_idx]) / prices[left_peak_idx]
        if peak_diff <= 0.2:  # Allow 20% difference for fallback
            # Valid cup formation found
            self.cup_left_idx = left_peak_idx
            self.cup_bottom_idx = cup_bottom_idx
            self.cup_right_idx = right_peak_idx
            return True

        return False



    def _identify_handle_formation(self, prices: np.ndarray, troughs: np.ndarray) -> bool:
        """
        Identify a handle formation after the cup.

        Args:
            prices: Array of price values
            troughs: Array of trough indices

        Returns:
            bool: True if a handle formation is identified, False otherwise
        """
        if self.cup_right_idx is None:
            logger.debug("No cup formation detected, cannot identify handle")
            return False

        # Handle should form after the right side of the cup
        handle_troughs = [t for t in troughs if t > self.cup_right_idx]

        if not handle_troughs:
            logger.debug("No troughs found after cup formation for handle")
            return False

        cup_right_price = prices[self.cup_right_idx]
        cup_bottom_price = prices[self.cup_bottom_idx]
        cup_depth = cup_right_price - cup_bottom_price

        # Cup length in number of price points
        cup_length = self.cup_right_idx - self.cup_left_idx

        logger.debug(
            f"Looking for handle after cup. Cup right price: {cup_right_price}, Cup right idx: {self.cup_right_idx}")
        logger.debug(f"Available troughs after cup: {handle_troughs}")

        for trough_idx in handle_troughs:
            handle_bottom_price = prices[trough_idx]

            # Calculate handle depth as a percentage of cup depth
            handle_depth_abs = cup_right_price - handle_bottom_price
            handle_depth_ratio = handle_depth_abs / cup_depth if cup_depth != 0 else 0

            logger.debug(f"Potential handle bottom: {handle_bottom_price} at {trough_idx}")
            logger.debug(
                f"Handle depth ratio: {handle_depth_ratio}, required: {self.handle_depth_min} to {self.handle_depth_max}")

            if handle_depth_ratio > 0.5:
                logger.debug(f"Handle too deep: {handle_depth_ratio:.2f} > 0.5")
                continue

            # Handle should be shallower than the cup, but still significant
            if self.handle_depth_min <= handle_depth_ratio <= self.handle_depth_max:
                # Handle should not be too long compared to cup
                handle_length = trough_idx - self.cup_right_idx
                handle_to_cup_ratio = handle_length / cup_length

                logger.debug(f"Handle length ratio: {handle_to_cup_ratio}, should be <= {self.handle_length_max}")

                if handle_to_cup_ratio <= self.handle_length_max:
                    # Check if price recovers after handle
                    # Get data points after handle bottom
                    if trough_idx < len(prices) - 1:
                        # Find the highest point after the handle
                        post_handle_max = max(prices[trough_idx + 1:])

                        logger.debug(f"Post handle maximum: {post_handle_max}, should be >= {cup_right_price * 0.95}")

                        # If price recovers to at least the cup's right peak level
                        if post_handle_max >= cup_right_price * 0.95:
                            self.handle_bottom_idx = trough_idx
                            self.handle_end_idx = len(prices) - 1
                            logger.info(f"Handle formation detected! Bottom: {trough_idx}")
                            return True

        logger.debug("No valid handle formation found")
        return False


    def detect(self, data: pd.DataFrame) -> bool:
        """
        Detect if the Cup and Handle pattern exists in the provided price data.

        Algorithm steps:
        1. Validate and prepare the data
        2. Identify peaks and troughs in the price series
        3. Look for a cup formation (U-shape)
        4. Look for a handle formation after the cup
        5. Validate the complete pattern

        Args:
            data: DataFrame containing price data with columns:
                 ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        Returns:
            bool: True if Cup and Handle pattern is detected, False otherwise
        """
        logger.setLevel(logging.DEBUG)

        # Reset pattern points
        self.cup_left_idx = None
        self.cup_bottom_idx = None
        self.cup_right_idx = None
        self.handle_bottom_idx = None
        self.handle_end_idx = None

        # Validate data
        if not self.validate_data(data):
            logger.warning("Invalid data format for Cup and Handle detection")
            return False

        if len(data) < 10:  # Need sufficient data points for a pattern
            logger.info("Insufficient data points for Cup and Handle detection")
            return False

        # Use close prices for pattern detection
        prices = data['close'].values

        # Apply smoothing to reduce noise
        if len(prices) > 5:
            smoothed_prices = self._smooth_prices(prices)
            # Adjust data to account for smoothing window
            offset = len(prices) - len(smoothed_prices)
            prices = smoothed_prices
            # Need to account for this offset in all indices
        else:
            offset = 0

        # Identify peaks and troughs
        peaks, troughs = self._identify_peaks_and_troughs(prices)

        # Look for cup formation
        if not self._identify_cup_formation(prices, peaks, troughs):
            logger.debug("No cup formation detected")
            return False

        # Look for handle formation
        if not self._identify_handle_formation(prices, troughs):
            logger.debug("Cup detected but no handle formation")
            return False

        # If we got here, we found a valid Cup and Handle pattern
        logger.info(
            f"Cup and Handle pattern detected. Cup: {self.cup_left_idx + offset}-{self.cup_bottom_idx + offset}-{self.cup_right_idx + offset}, Handle: {self.handle_bottom_idx + offset}")
        return True

    def get_pattern_details(self) -> Dict[str, Any]:
        """
        Get detailed information about the detected pattern.

        Returns:
            Dict[str, Any]: Details about the detected Cup and Handle pattern
        """
        details = super().get_pattern_details()

        if self.cup_left_idx is not None:
            details.update({
                "cup_left_index": self.cup_left_idx,
                "cup_bottom_index": self.cup_bottom_idx,
                "cup_right_index": self.cup_right_idx,
                "handle_bottom_index": self.handle_bottom_idx,
                "handle_end_index": self.handle_end_idx,
                "cup_to_handle_ratio": (self.cup_right_idx - self.cup_left_idx) /
                                       (self.handle_end_idx - self.cup_right_idx) if self.handle_end_idx else None
            })

        return details