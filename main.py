#!/usr/bin/env python
# Main application entry point for Stock Pattern Detector POC
# This file initializes all components and serves as the application entrypoint

import os
import sys
import signal
import time
from datetime import datetime

# Add project root to path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import configuration
from config.config import STOCKS, TRADING_HOURS, COLLECTION_INTERVAL_MINUTES

# Import core components
from utils.logger import get_logger
from data_storage import get_db
from data_collector import collector
from pattern_detector import get_detector
from scheduler import get_scheduler

# Initialize logger
logger = get_logger("main")


class MainApplication:
    """
    Main application class that initializes and coordinates all components.
    Serves as the entry point for the Stock Pattern Detector POC.
    """

    def __init__(self):
        """Initialize the main application and all its components."""
        logger.info("Initializing Stock Pattern Detector POC")

        # Initialize flag for graceful shutdown
        self.running = False

        # Initialize database connection
        logger.info("Initializing database connection")
        self.db = get_db()

        # Initialize data collector
        logger.info("Initializing data collector")
        self.data_collector = collector  # Use the singleton instance

        # Initialize pattern detector
        logger.info("Initializing pattern detector")
        self.pattern_detector = get_detector()

        # Initialize scheduler
        logger.info("Initializing scheduler")
        self.scheduler = get_scheduler()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

        logger.info("Application initialization complete")

    def start(self):
        """Start the application and all its components."""
        if self.running:
            logger.warning("Application is already running")
            return False

        logger.info("Starting Stock Pattern Detector application")

        try:
            # Start the scheduler
            scheduler_started = self.scheduler.start()
            if not scheduler_started:
                logger.error("Failed to start scheduler")
                return False

            # Schedule data collection job
            self.scheduler.schedule_data_collection()

            # Schedule data cleanup job
            self.scheduler.schedule_data_cleanup()

            # Perform initial data collection if within trading hours
            current_time = datetime.now()
            formatted_time = current_time.strftime('%H:%M')
            current_day = current_time.strftime('%A')
            logger.info(f"Current time: {formatted_time}, day: {current_day}")

            if self.data_collector.is_trading_hours():
                logger.info("Within trading hours, performing initial data collection")
                collected = self.data_collector.collect_all_latest()
                logger.info(f"Initial collection completed: {collected} stocks")
            else:
                logger.info("Outside trading hours, skipping initial collection")
                logger.info(f"Trading hours are {TRADING_HOURS['start']} - {TRADING_HOURS['end']}")

            self.running = True
            logger.info("Application started successfully")
            return True

        except Exception as e:
            logger.error(f"Error starting application: {str(e)}")
            self.shutdown()
            return False

    def shutdown(self):
        """Shut down the application and all its components gracefully."""
        if not self.running:
            logger.warning("Application is not running")
            return False

        logger.info("Shutting down Stock Pattern Detector application")

        try:
            # Stop the scheduler
            self.scheduler.stop()

            # Close database connection
            self.db.close()

            self.running = False
            logger.info("Application shutdown complete")
            return True

        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
            return False

    def handle_shutdown(self, signum, frame):
        """Signal handler for graceful shutdown."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.shutdown()
        sys.exit(0)

    def run_forever(self):
        """Run the application until interrupted."""
        if not self.start():
            logger.error("Failed to start application")
            return

        logger.info("Application running, press Ctrl+C to exit")

        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.shutdown()


def main():
    """Main entry point function."""
    app = MainApplication()

    # Print startup information
    logger.info("======================================")
    logger.info("Stock Pattern Detector POC")
    logger.info(f"Monitoring {len(STOCKS)} stocks: {', '.join(STOCKS)}")
    logger.info(f"Trading hours: {TRADING_HOURS['start']} - {TRADING_HOURS['end']} (Israel time)")
    logger.info(f"Data collection interval: {COLLECTION_INTERVAL_MINUTES} minutes")
    logger.info("======================================")

    # Run the application
    app.run_forever()


if __name__ == "__main__":
    main()