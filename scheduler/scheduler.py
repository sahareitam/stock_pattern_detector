import threading
from datetime import datetime
import pytz

import apscheduler.schedulers.background
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from config.config import TRADING_HOURS, COLLECTION_INTERVAL_MINUTES, DATA_RETENTION_DAYS
from data_collector import collect_data
from data_storage import get_db
from utils.logger import get_logger
logger = get_logger(__name__)




class AppScheduler:
    """
    Manages scheduled tasks for the application:
    - Data collection during trading hours (every X minutes)
    - Cleanup of old data (daily)

    Uses APScheduler for managing jobs and ensures proper timezone handling.
    """

    def __init__(self):
        """Initialize the scheduler with appropriate configuration"""
        logger.info("Initializing application scheduler")

        # Configure the scheduler with jobstores and executors
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=3)
        }

        # Create and configure the scheduler
        self.scheduler = apscheduler.schedulers.background.BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            timezone=pytz.timezone('Asia/Jerusalem')  # Ensure correct timezone for Israel
        )

        # Initialize flags and locks
        self.running = False
        self.lock = threading.RLock()  # Reentrant lock for thread safety

    def start(self):
        """Start the scheduler if not already running"""
        with self.lock:
            if not self.running:
                logger.info("Starting scheduler")
                self.scheduler.start()
                self.running = True
                return True
            else:
                logger.warning("Scheduler already running")
                return False

    def stop(self):
        """Stop the scheduler if running"""
        with self.lock:
            if self.running:
                logger.info("Stopping scheduler")
                self.scheduler.shutdown()
                self.running = False
                return True
            else:
                logger.warning("Scheduler not running")
                return False

    def schedule_data_collection(self):
        """
        Schedule regular data collection during trading hours.
        Collection happens every COLLECTION_INTERVAL_MINUTES minutes,
        but only between TRADING_HOURS start and end times.
        """
        logger.info(f"Scheduling data collection every {COLLECTION_INTERVAL_MINUTES} minutes")

        # Extract trading hours from config
        start_time = TRADING_HOURS["start"]
        end_time = TRADING_HOURS["end"]

        # Schedule job with a conditional function that checks trading hours
        self.scheduler.add_job(
            self._collect_data_if_trading_hours,
            IntervalTrigger(minutes=COLLECTION_INTERVAL_MINUTES),
            id='data_collection',
            replace_existing=True,
            name='Collect Stock Data'
        )

        logger.info(f"Data collection scheduled during trading hours ({start_time} - {end_time})")

    def schedule_data_cleanup(self):
        """
        Schedule daily cleanup of old data.
        Runs once per day at a specified time (default: midnight).
        """
        logger.info("Scheduling daily data cleanup")

        # Schedule to run at 00:00 every day
        self.scheduler.add_job(
            self._cleanup_old_data,
            CronTrigger(hour=0, minute=0),
            id='data_cleanup',
            replace_existing=True,
            name='Clean Old Data'
        )

        logger.info(f"Data cleanup scheduled daily (retention: {DATA_RETENTION_DAYS} days)")

    def _collect_data_if_trading_hours(self):
        """
        Check if current time is within trading hours and collect data if so.
        This is a wrapper around the actual collection function with time checking.
        """
        try:
            # Check if current time is within trading hours
            if self.is_within_trading_hours():
                logger.info(f"Within trading hours, collecting data")
                collect_data()
            else:
                current_time = datetime.now().strftime('%H:%M')
                logger.info(f"Skipping data collection - outside trading hours (current time: {current_time})")
        except Exception as e:
            logger.error(f"Error in scheduled data collection: {str(e)}", exc_info=True)

    @staticmethod
    def _cleanup_old_data():
        """
        Clean up old data beyond the retention period.
        Calls the database manager's delete_old_data method.
        """
        try:
            logger.info(f"Running scheduled cleanup of data older than {DATA_RETENTION_DAYS} days")
            db = get_db()
            deleted_count = db.delete_old_data(DATA_RETENTION_DAYS)
            logger.info(f"Cleanup complete: {deleted_count} old records deleted")
        except Exception as e:
            logger.error(f"Error in scheduled data cleanup: {str(e)}", exc_info=True)

    @staticmethod
    def is_within_trading_hours(now=None):
        """
        Check if given time (or current time) is within configured trading hours.

        Args:
            now: Optional datetime to check. If None, uses current time.

        Returns:
            bool: True if within trading hours, False otherwise
        """
        # Get current time in Israel timezone if not provided
        israel_tz = pytz.timezone('Asia/Jerusalem')

        # Use current time if no time is provided
        if now is None:
            now = datetime.now(israel_tz)
        elif now.tzinfo is None:
            # If provided time is naive (no timezone), assume it is in Israel timezone
            now = israel_tz.localize(now)
        else:
            # Convert provided time to Israel timezone
            now = now.astimezone(israel_tz)

        # Format time as HH:MM for comparison
        current_time = now.strftime('%H:%M')

        # Retrieve configured trading hours from global config
        start_time = TRADING_HOURS["start"]
        end_time = TRADING_HOURS["end"]
        # Check if it's a weekday (Monday to Friday) 0-4 Monday to Friday
        is_weekday = now.weekday() < 5

        # Return True only if within time range and it's a weekday
        return start_time <= current_time <= end_time and is_weekday

# Singleton instance
_scheduler_instance = None

def get_scheduler():
    """
    Get the singleton scheduler instance.

    Returns:
        AppScheduler: Singleton instance of the scheduler
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = AppScheduler()
    return _scheduler_instance