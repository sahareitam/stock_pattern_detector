# Stock Pattern Detector POC

A local proof-of-concept (POC) system for detecting Cup and Handle patterns in stock price data.

## Overview

This system automatically collects stock price data for 7 major technology companies at 5-minute intervals during market hours, analyzes the data to detect Cup and Handle patterns, and provides a simple REST API to query detection results. It's designed to run entirely locally without cloud dependencies.

**Key Features:**
- Automated price data collection from Yahoo Finance
- 5-minute interval data collection during market hours (16:30-23:00 Israel time)
- 3-day data retention with automatic cleanup
- Cup and Handle pattern detection algorithm
- Local REST API for querying pattern detection results
- Comprehensive logging and error handling
- Modular, maintainable architecture

## Prerequisites (workstation setup)

Before cloning the repository you must **install the tooling stack in the following order**:

1. **Python 3.10 or newer** - download an official installer from [https://www.python.org/downloads/](https://www.python.org/downloads/) and ensure that the *Add Python to PATH* option is selected during installation. Confirm the installation:

   ```bash
   python --version
   ```
2. **pip** - Python 3 installers ship with *pip* out of the box. Verify that it is available:

   ```bash
   python -m pip --version
   ```

   If the command fails, install pip manually with the official [get-pip.py](https://bootstrap.pypa.io/get-pip.py) script.
3. **Pipenv** - the project uses *Pipenv* for dependency management. Install it **once** (globally or per-user) with:

   ```bash
   python -m pip install --user pipenv
   ```
4. **Node.js & npm** (only if you want to run the optional React Frontend)

> **Note** - all subsequent commands assume that `python`, `pip`, and `pipenv` resolve to the Python 3.10+ installation prepared above.

## Key Dependencies

| Library | Purpose | Version |
|---------|---------|---------|
| pandas | Data handling and analysis | 2.2.3+ |
| yfinance | Yahoo Finance data source | 0.2.61+ |
| matplotlib | Visualization | 3.10.3+ |
| scipy | Scientific computing | 1.15.3+ |
| flask | API implementation | Latest |
| waitress | Production WSGI server | 3.0.2+ |
| apscheduler | Task scheduling | Latest |
| numpy | Numerical computing | Latest |
| pytz | Timezone handling | Latest |

### Frontend Dependencies
| Library | Purpose | Version |
|---------|---------|---------|
| React | UI Framework | 18.x |
| Vite | Build tool | 5.x |
| Tailwind CSS | Styling | 3.x |

### Development Packages
| Library | Purpose | Version |
|---------|---------|---------|
| pytest | Testing framework | Latest |
| freezegun | Time mocking for tests | Latest |


## Installation

1. Clone the repository:
```bash
git clone https://github.com/sahareitam/stock_pattern_detector.git
cd stock_pattern_detector
```

2. Install dependencies using Pipenv:
```bash
pipenv install
```

3. Activate the virtual environment:
```bash
pipenv shell
```

4. Create the logs directory (if it doesn't exist):
```bash
mkdir -p logs
```

## Configuration

The system can be configured by editing `config/config.py`:

- `STOCKS`: List of stock symbols to track (default: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA)
- `TRADING_HOURS`: Trading hours in Israel time (default: 16:30-23:00)
- `COLLECTION_INTERVAL_MINUTES`: Data collection interval (default: 5 minutes)
- `DATA_RETENTION_DAYS`: How many days of data to keep (default: 3 days)
- `DATABASE`: Database settings including path
- `API`: API server settings (host, port, debug mode)
- `PATTERNS`: Pattern detection parameters

Example of changing configuration:

```python
# Change stocks to monitor
STOCKS = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "GOOGL",  # Alphabet
    "AMZN",   # Amazon
]

# Modify trading hours
TRADING_HOURS = {
    "start": "16:00",  # 16:00 Israel time
    "end": "22:30",    # 22:30 Israel time
}

# Change database location
DATABASE = {
    "path": "/custom/path/stock_data.sqlite",
    "name": "stock_data.sqlite"
}
```

## Running the Application

### Start the Complete System

To start both the scheduler and API server in a single process:

```bash
python main.py
```

This will:
1. Initialize the database
2. Start the data collection scheduler
3. Start the API server
4. Begin collecting data if within trading hours

You should see output similar to:

```
2025-05-20 10:03:26,961 - data_collector.collector - INFO - No data source provided, using Yahoo Finance as default
2025-05-20 10:03:26,961 - data_collector.data_sources.yahoo_finance - INFO - Initialized Yahoo Finance data source
2025-05-20 10:03:26,962 - data_collector.collector - INFO - DataCollector initialized with YahooFinanceDataSource
2025-05-20 10:03:39,872 - main - INFO - Initializing Stock Pattern Detector POC
2025-05-20 10:03:39,873 - main - INFO - Initializing database connection
2025-05-20 10:03:39,873 - main - INFO - Initializing data collector
2025-05-20 10:03:39,873 - main - INFO - Initializing pattern detector
2025-05-20 10:03:39,874 - main - INFO - Initializing scheduler
2025-05-20 10:03:39,874 - scheduler.scheduler - INFO - Initializing application scheduler
```

Followed by:

```
2025-05-20 10:03:45,317 - main - INFO - ======================================
2025-05-20 10:03:45,317 - main - INFO - Stock Pattern Detector POC
2025-05-20 10:03:45,318 - main - INFO - Monitoring 7 stocks: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA
2025-05-20 10:03:45,318 - main - INFO - Trading hours: 16:30 - 23:00 (Israel time)
2025-05-20 10:03:45,319 - main - INFO - Data collection interval: 5 minutes
2025-05-20 10:03:45,319 - main - INFO - API running on: localhost:5000
2025-05-20 10:03:45,320 - main - INFO - ======================================
2025-05-20 10:03:45,321 - main - INFO - Starting Stock Pattern Detector application
2025-05-20 10:03:45,855 - main - INFO - Application running, press Ctrl+C to exit
2025-05-20 10:03:45,888 - api.app - INFO - Starting API server with waitress on localhost:5000
2025-05-20 10:03:45,900 - waitress - INFO - Serving on http://[::1]:5000
2025-05-20 10:03:45,900 - waitress - INFO - Serving on http://127.0.0.1:5000
```

The application will continue running until stopped with Ctrl+C.

### Load Initial Historical Data

If you want to load historical data for the past 3 days before starting:

```bash
# Run from the project root directory
python -c "from data_collector import create_collector; create_collector().collect_historical(days=3)"
```

### Running Just the API Server

To start only the API server without the scheduler:

```bash
python -m api.app
```

For custom configuration:

```bash
python -c "from api import run_api; run_api(host='127.0.0.1', port=8080, debug=True)"
```

For production deployment with Waitress (which is the default):

```bash
python -c "from api import run_api_production; run_api_production(host='0.0.0.0', port=5000)"
```

Note: The system uses Waitress as the production WSGI server, as seen in the logs.

### 🖼️ Base44 Frontend (Added for Improved UX)

**Note:** Base44 generated **only** the user-interface files to provide a convenient way to use.

Everything else was implemented and refined manually by me:

- Data sampling and collection strategy
- Cup and Handle pattern-detection algorithm
- Symbol validation and normalization
- Flask API design and routing
- Error handling and structured logging
- SQLite storage layer with retention policies
- Interval-based data collection during market hours

After Base44 generated the interface, I:

- Integrated the UI into the repository and aligned paths, imports, and build scripts
- Added missing configuration, helper modules, and environment files so the project runs locally
- Improved the generated components for consistency with project conventions and visual polish


### Running the Frontend

To run the Frontend UI, follow these steps:

1. **First, ensure the API server is running**:
```bash
pipenv run python -m api.app
```

Or for production:
```bash
pipenv run waitress-serve --listen=*:5000 api.app:flask_app
```

2. **Install Frontend dependencies**:
```bash
cd Front
npm install
```

3. **Start the Frontend development server**:
```bash
npm run dev
```

The Vite development server will start and display a URL (typically http://localhost:5173) where you can access the UI.

**Important:** The API server must be running before starting the Frontend, otherwise you'll see "Failed to Fetch" or CORS errors in the browser console.

## API Documentation

The system provides a RESTful API for accessing pattern detection results.

### Testing Specific Endpoints

You can use `curl` commands from the command line to test the API endpoints:

```bash
# Health check endpoint
curl http://localhost:5000/health

# List supported symbols
curl http://localhost:5000/symbols

# Check pattern for a specific stock
curl http://localhost:5000/pattern/AAPL

# Alternative pattern check with query parameter
curl "http://localhost:5000/api/pattern?symbol=MSFT"
```

Expected response formats:

```json
// Health check response
{"status": "ok"}

// Symbols response
{"symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]}

// Pattern check response (positive)
{"pattern_detected": true}

// Pattern check response (negative)
{"pattern_detected": false}

// Error response (invalid symbol)
{"error": "Symbol not supported"}
```

## Running Tests

### Unit Tests

To run all unit tests:

```bash
pytest
```

To run tests for a specific module:

```bash
pytest tests/test_pattern_detector.py
```

To run tests with detailed output:

```bash
pytest -v
```

Example output:
```
============================= test session starts =============================
collecting ... collected 8 items
test_api.py::test_health_endpoint PASSED                                 [ 12%]2025-05-20 10:09:05,321 - api.app - INFO - Health check request received
test_api.py::test_symbols_endpoint PASSED                                [ 25%]2025-05-20 10:09:05,331 - api.app - INFO - Symbols list request received
test_api.py::test_pattern_endpoint_success PASSED                        [ 37%]2025-05-20 10:09:05,338 - api.app - INFO - Pattern check requested for symbol: AAPL
2025-05-20 10:09:05,339 - api.app - INFO - Pattern detection for AAPL: True
test_api.py::test_pattern_endpoint_no_pattern PASSED                     [ 50%]2025-05-20 10:09:05,347 - api.app - INFO - Pattern check requested for symbol: MSFT
2025-05-20 10:09:05,347 - api.app - INFO - Pattern detection for MSFT: False
test_api.py::test_pattern_endpoint_invalid_symbol PASSED                 [ 62%]2025-05-20 10:09:05,355 - api.app - INFO - Pattern check requested for symbol: INVALID
2025-05-20 10:09:05,355 - api.app - WARNING - Invalid symbol requested: INVALID
test_api.py::test_pattern_query_endpoint PASSED                          [ 75%]2025-05-20 10:09:05,366 - api.app - INFO - Pattern check requested for symbol: AAPL
2025-05-20 10:09:05,366 - api.app - INFO - Pattern detection for AAPL: True
test_api.py::test_pattern_query_endpoint_missing_symbol PASSED           [ 87%]2025-05-20 10:09:05,373 - api.app - WARNING - Symbol parameter missing in request
test_api.py::test_pattern_endpoint_service_error PASSED                  [100%]2025-05-20 10:09:05,380 - api.app - INFO - Pattern check requested for symbol: AAPL
2025-05-20 10:09:05,380 - api.app - ERROR - Error detecting pattern for AAPL: Test error
====================== 8 passed, 1945 warnings in 1.02s =======================
```

Note: You might see a large number of warnings when running the tests. These are typically related to dependencies and don't affect the functionality of the tests.

## Visualization Example

The repository includes a utility script to visualize stock data and detected patterns. The script `utils/plot_stock_data.py` can be used to plot the price chart of any monitored stock and highlight Cup and Handle patterns if detected.

### Using the Built-in Visualization Tool

```bash
python utils/plot_stock_data.py AAPL
```

Optional parameters:
- `--days`: Number of days to display (default: 3)

Example:
```bash
python utils/plot_stock_data.py AAPL --days 2
```

This will display a matplotlib window with the stock chart and highlighted pattern (if detected).

### Creating a Custom Visualization Script

You can also create your own custom visualization script based on the example below. Note that the project already includes `utils/plot_stock_data.py` which provides similar functionality.

First, create the examples directory:
```bash
mkdir -p examples
```

Then create a new file `examples/plot_example.py` with this content:

```python
# examples/plot_example.py
import matplotlib.pyplot as plt
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the system path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from data_storage import get_db
from pattern_detector import get_detector

def plot_stock(symbol, days=1):
    # Get database connection
    db = get_db()
    
    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # Get stock data
    data = db.get_prices(symbol, start_time, end_time)
    
    if data.empty:
        print(f"No data found for {symbol}")
        return
    
    # Check if pattern is detected
    detector = get_detector()
    has_pattern = detector.detect_pattern(symbol)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(data['timestamp'], data['close'], label=f'{symbol} Close Price')
    plt.title(f"{symbol} Stock Price - Cup and Handle {'Detected!' if has_pattern else 'Not Detected'}")
    plt.xlabel('Time')
    plt.ylabel('Price ($)')
    plt.grid(True)
    plt.legend()
    
    # Format the time axis
    plt.gcf().autofmt_xdate()
    
    # Show the plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Use command line argument or default to AAPL
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    plot_stock(symbol)
```

Run it with:
```bash
python examples/plot_example.py AAPL
```

## Technical Implementation Details

The pattern detection algorithm relies on several scientific Python libraries:

- **NumPy**: Used for efficient numerical computations and array operations
- **Pandas**: Powers the time series analysis with DataFrames for price data
- **SciPy**: Provides peak detection functionality (`find_peaks`) for identifying significant price points
   
The Cup and Handle pattern detection specifically uses these libraries to:
1. Process the time series data efficiently
2. Detect local maxima and minima in price movements using SciPy's `find_peaks`
3. Analyze pattern characteristics like cup depth, handle size, and their relationships
4. Smooth the price data to reduce noise using moving averages

### NumExpr Configuration

The system uses NumExpr for numerical computations in pattern detection. You might see the following log entry when starting the application:

```
2025-05-20 10:03:23,914 - numexpr.utils - INFO - NumExpr defaulting to 12 threads.
```

This is normal and indicates that NumExpr is using multiple threads for better performance. The number of threads depends on your system's CPU cores.

## Project Structure

```
stock_pattern_detector/
├── api/                      # API server
│   ├── __init__.py
│   └── app.py                # Flask API implementation
├── config/                   # Configuration
│   ├── __init__.py
│   └── config.py             # System configuration
├── data_collector/           # Stock data collection
│   ├── __init__.py
│   ├── collector.py          # Main collector implementation
│   ├── data_source_base.py   # Abstract base class for data sources
│   └── data_sources/         # Concrete data source implementations
│       ├── __init__.py
│       └── yahoo_finance.py  # Yahoo Finance implementation
├── data_storage/             # Data persistence
│   ├── __init__.py
│   ├── models.py             # Database schema
│   └── storage.py            # Database operations
├── pattern_detector/         # Pattern detection
│   ├── __init__.py
│   ├── detector.py           # Main detector implementation
│   └── patterns/             # Pattern implementations
│       ├── __init__.py
│       ├── pattern_base.py   # Abstract base class for patterns
│       └── cup_and_handle.py # Cup and Handle implementation
├── scheduler/                # Scheduling
│   ├── __init__.py
│   └── scheduler.py          # APScheduler implementation
├── utils/                    # Utilities
│   ├── __init__.py
│   ├── logger/               # Logging utilities
│   │   ├── __init__.py
│   │   └── logger.py         # Logging configuration
│   └── plot_stock_data.py    # Stock visualization tool
├── Front/                    # Frontend UI (Base44)
│   ├── node_modules/         # npm dependencies (generated)
│   ├── src/                  # React source files
│   │   ├── Components/       # Reusable components
│   │   │   ├── dashboard/    # Dashboard-specific components
│   │   │   │   └── StockCard.jsx # Individual stock card component
│   │   │   └── ui/           # UI primitives
│   │   │       ├── alert.jsx
│   │   │       ├── button.jsx
│   │   │       ├── Localcard.jsx
│   │   │       ├── separator.jsx
│   │   │       └── use-toast.jsx
│   │   ├── Pages/            # Page components
│   │   │   ├── Dashboard.jsx # Main dashboard page
│   │   │   └── home.jsx      # Home/landing page
│   │   ├── index.css         # Global styles
│   │   ├── Layout.jsx        # Application layout wrapper
│   │   ├── main.jsx          # React entry point
│   │   └── utils.js          # Frontend utilities
│   ├── index.html            # HTML entry point
│   ├── package.json          # Frontend dependencies
│   ├── package-lock.json     # Locked dependencies
│   ├── postcss.config.js     # PostCSS configuration
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   └── vite.config.js        # Vite bundler configuration
├── tests/                    # Unit tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_collector.py
│   ├── test_logger.py
│   ├── test_pattern_detector.py
│   ├── test_scheduler.py
│   └── test_storage.py
├── logs/                     # Log files (created at runtime)
├── main.py                   # Application entry point
├── Pipfile                   # Pipenv dependency definitions
├── Pipfile.lock              # Pipenv locked dependencies
└── README.md                 # This file
```

## Troubleshooting

### Common Issues

#### API Not Starting

**Problem**: The API server fails to start.

**Solution**:
1. Check if another process is using port 5000
2. Ensure the database path exists and is writable
3. Check the logs in the `logs/` directory for specific errors

Example of changing the port:
```python
# In config/config.py
API = {
    "host": "localhost",
    "port": 8080,  # Change to an available port
    "debug": False
}
```

#### No Data Collected

**Problem**: The system is not collecting any data.

**Solution**:
1. Check if you're running during trading hours (16:30-23:00 Israel time)
2. Check internet connectivity
3. Check if Yahoo Finance API is accessible
4. Look for error messages in the logs

To manually trigger data collection:
```bash
python -c "from data_collector import collect_data; collect_data()"
```

#### Pattern Not Detected When Expected

**Problem**: You believe a pattern exists, but it's not being detected.

**Solution**:
1. The pattern detection is based on specific parameters that can be adjusted in `config/config.py`
2. Ensure you have enough data (at least a few hours)
3. Use `utils/plot_stock_data.py` to visualize the data and see if a pattern is visually present

To adjust pattern detection sensitivity:
```python
# In config/config.py
PATTERNS = {
    "cup_and_handle": {
        "cup_depth_min": 0.08,    # Decrease to detect shallower cups
        "cup_depth_max": 0.70,    # Increase to detect deeper cups
        "handle_depth_min": 0.08, # Decrease for shallower handles
        "handle_depth_max": 0.70, # Increase for deeper handles
        "handle_length_max": 0.8  # Increase for longer handles
    }
}
```

#### Database Errors

**Problem**: Database-related errors.

**Solution**:
1. Check if the database directory exists and is writable
2. Try deleting the database file and restart the application
3. Check if SQLite is properly installed

#### Missing `logs` Directory

**Problem**: Error related to missing `logs` directory.

**Solution**: Create the logs directory manually:
```bash
mkdir -p logs
```

#### Frontend Issues

**Problem**: The Frontend UI shows "Failed to Fetch" or CORS errors.

**Solution**:
1. Make sure the API server is running on port 5000 before starting the Frontend
2. Check browser console for specific error messages
3. Ensure you have run `npm install` in the Front directory
4. Verify the API server is accepting connections (try the curl commands above)

## Future Work

This POC demonstrates the core functionality of a stock pattern detection system. Here are potential enhancements for a production environment:

### Microservices Architecture
- Split components into separate microservices:
  - **Data Collection Service**: Responsible for gathering stock data from multiple sources
  - **Pattern Detection Service**: Focused solely on analyzing patterns
  - **API Service**: Handling all external requests
  - **Notification Service**: Alerting users when patterns are detected
- Implement proper service isolation and communication

### Cloud Deployment (GCP)
- Deploy as containerized applications using Google Cloud Run
- Use Cloud SQL for persistent database storage
- Set up Cloud Monitoring for tracking application performance
- Implement Cloud Scheduler for scheduling tasks


### Machine Learning Enhancements
- Improve pattern detection with simple classification models
- Add basic sentiment analysis for complementary signals
- Combine technical indicators for better accuracy

### Advanced Features
- Support for multiple pattern types (Head and Shoulders, Double Top/Bottom, etc.)
- Email notifications for detected patterns
- Web dashboard for visualization
- Backtesting framework for pattern strategies
- Integration with trading platforms via APIs

---

Created by [Sahar Eitam] - 2025