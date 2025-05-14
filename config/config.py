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
        "cup_depth_min": 0.15,    # Minimum cup depth (15% from peak)
        "cup_depth_max": 0.50,    # Maximum cup depth (50% from peak)
        "handle_depth_min": 0.20, # Handle should be at least 20% of cup depth
        "handle_depth_max": 0.50, # Handle should be at most 50% of cup depth
        "handle_length_max": 0.5, # Handle length compared to cup length
    }
    # Future patterns can be added here
}

# API settings
API = {
    "host": "localhost",
    "port": 5000,
    "debug": True
}

# Logging settings
LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "stock_pattern_detector.log"
}