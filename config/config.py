# Configuration file for Stock Pattern Detector POC
# Contains global constants and settings

# List of stocks to track
STOCKS = [
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "GOOGL", # Alphabet
    "AMZN",  # Amazon
    "NVDA",  # Nvidia
    "META",  # Meta
    "TSLA",  # Tesla
]

# Trading hours (Israel time)
TRADING_HOURS = {
    "start": "16:30",  # 16:30 Israel time
    "end": "23:00",    # 23:00 Israel time
}

# Data retention period (in days)
DATA_RETENTION_DAYS = 3

# Data collection interval (in minutes)
COLLECTION_INTERVAL_MINUTES = 5

# Database settings
DATABASE = {
    "path": "data_storage/stock_data.sqlite",
    "name": "stock_data.sqlite"
}

# Pattern detection parameters
PATTERNS = {
    "cup_and_handle": {
        "cup_depth_min": 0.10,    # Minimum cup depth (10% from peak, was 15%)
        "cup_depth_max": 0.60,    # Maximum cup depth (60% from peak, was 50%)
        "handle_depth_min": 0.10, # Handle should be at least 10% of cup depth (was 20%)
        "handle_depth_max": 0.60, # Handle should be at most 60% of cup depth (was 50%)
        "handle_length_max": 0.7, # Handle length compared to cup length (was 0.5)
    }

    # Future patterns can be added here
}

# API settings
API = {
    "host": "localhost",
    "port": 5000,
    "debug": True
}

LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "stock_pattern_detector.log",
    "log_dir": "logs"
}
