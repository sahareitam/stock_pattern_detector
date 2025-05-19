# utils/plot_stock_data.py
import matplotlib.pyplot as plt
import sys
import os

# Add the project root directory to sys.path to enable imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from data_storage import get_db
from pattern_detector import get_detector


def plot_stock_prices(symbol, days=3):
    """
    Create a plot of stock prices and highlight Cup and Handle patterns if detected.

    Args:
        symbol: Stock symbol (e.g. "AAPL")
        days: Number of days to display (default: 3)
    """
    # Get database and detector instances
    db = get_db()
    detector = get_detector()

    # Get the data for the requested symbol
    # Use the days parameter to limit the data
    from datetime import datetime, timedelta
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    data = db.get_prices(symbol, start_time, end_time)

    if data.empty:
        print(f"No data available for symbol {symbol}")
        return

    # Ensure data is sorted by timestamp
    data = data.sort_values('timestamp')

    # Check if a Cup and Handle pattern exists
    has_pattern = detector.detect_pattern(symbol)

    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(data['timestamp'], data['close'], label=f'{symbol} Close Price')

    # Add a title indicating if a pattern was detected
    title = f'{symbol} Stock Price (Last {days} days)'
    if has_pattern:
        title += " - Cup and Handle Pattern Detected!"
    plt.title(title)

    # Highlight pattern areas if a pattern was detected
    if has_pattern and 'cup_and_handle' in detector.pattern_detectors:
        pattern = detector.pattern_detectors['cup_and_handle']

        # Try to access pattern points if available
        if hasattr(pattern, 'cup_left_idx') and pattern.cup_left_idx is not None:
            try:
                # Highlight the "cup" portion
                cup_start = pattern.cup_left_idx
                cup_bottom = pattern.cup_bottom_idx
                cup_end = pattern.cup_right_idx

                plt.plot(data['timestamp'].iloc[cup_start:cup_end + 1],
                         data['close'].iloc[cup_start:cup_end + 1],
                         'r-', linewidth=3, label='Cup')

                # Mark the cup bottom point
                plt.scatter(data['timestamp'].iloc[cup_bottom],
                            data['close'].iloc[cup_bottom],
                            color='red', s=100, marker='o', label='Cup Bottom')

                # Highlight the "handle" portion
                if hasattr(pattern, 'handle_bottom_idx') and pattern.handle_bottom_idx is not None:
                    handle_bottom = pattern.handle_bottom_idx
                    # Use handle_end_idx if available, otherwise use the last data point
                    handle_end = pattern.handle_end_idx if hasattr(pattern, 'handle_end_idx') else len(data) - 1

                    # Now actually use handle_end in the plot
                    plt.plot(data['timestamp'].iloc[cup_end:handle_bottom + 1],
                             data['close'].iloc[cup_end:handle_bottom + 1],
                             'g-', linewidth=3, label='Handle')

                    # Plot the remaining portion of the handle if applicable
                    if handle_end > handle_bottom:
                        plt.plot(data['timestamp'].iloc[handle_bottom:handle_end + 1],
                                 data['close'].iloc[handle_bottom:handle_end + 1],
                                 'g-', linewidth=3)

                    # Mark the handle bottom point
                    plt.scatter(data['timestamp'].iloc[handle_bottom],
                                data['close'].iloc[handle_bottom],
                                color='green', s=100, marker='o', label='Handle Bottom')
            except Exception as e:
                print(f"Error highlighting pattern: {e}")

    # Add labels and legend
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid(True)

    # Format the time axis for better readability
    import matplotlib.dates as mdates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=4))
    plt.gcf().autofmt_xdate()  # Rotate date labels for better visibility

    # Display the plot
    plt.tight_layout()
    plt.show()


def main():
    """Main function to run the plotting script from command line"""
    import argparse

    parser = argparse.ArgumentParser(description='Display stock price chart and highlight patterns')
    parser.add_argument('symbol', type=str, help='Stock symbol (e.g., AAPL)')
    parser.add_argument('--days', type=int, default=3, help='Number of days to display')

    args = parser.parse_args()

    plot_stock_prices(args.symbol, args.days)


if __name__ == "__main__":
    main()