# tests/test_logger.py
import os
import logging
import tempfile
from datetime import datetime
from utils.logger import get_logger


def test_get_logger():
    """Test that get_logger returns a properly configured logger instance."""
    # Get a logger with a unique name for this test
    logger_name = f"test_logger_{datetime.now().timestamp()}"
    logger = get_logger(logger_name)

    # Check that it's a Logger instance
    assert isinstance(logger, logging.Logger)

    # Check that it has the correct name
    assert logger.name == logger_name

    # Check that it has at least two handlers (console and file)
    assert len(logger.handlers) >= 2

    # Check handler types
    handler_types = [type(h) for h in logger.handlers]
    assert logging.StreamHandler in handler_types

    # At least one should be a file handler
    file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
    assert len(file_handlers) > 0


def test_logger_writes_to_file():
    """Test that the logger actually writes to a log file."""
    # Create a temporary directory for the test logs
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Override the logs directory for this test
        original_logs_dir = os.environ.get('LOGS_DIR')
        try:
            os.environ['LOGS_DIR'] = tmpdirname

            # Force reset of logger system for test
            # This is needed because loggers are cached
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)

            # Import here to ensure we get the updated logs_dir
            import sys
            if 'utils.logger.logger' in sys.modules:
                del sys.modules['utils.logger.logger']
            if 'utils.logger' in sys.modules:
                del sys.modules['utils.logger']

            from utils.logger import get_logger

            # Get a logger with a unique name
            logger_name = f"test_file_logger_{datetime.now().timestamp()}"
            logger = get_logger(logger_name)

            # Write a test message
            test_message = f"Test log message at {datetime.now().isoformat()}"
            logger.info(test_message)

            # Close all handlers before checking files
            # This is critical to avoid permission issues on Windows
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

            # Check that the message was written to a file
            log_files = [f for f in os.listdir(tmpdirname) if f.endswith('.log')]
            assert len(log_files) > 0

            # Read the file and check for the message
            log_file_path = os.path.join(tmpdirname, log_files[0])
            with open(log_file_path, 'r') as f:
                log_content = f.read()
                assert test_message in log_content

        finally:
            # Restore the original environment
            if original_logs_dir:
                os.environ['LOGS_DIR'] = original_logs_dir
            else:
                os.environ.pop('LOGS_DIR', None)

            # Reset logger system
            for handler in logging.root.handlers[:]:
                # Close handlers before removing them
                handler.close()
                logging.root.removeHandler(handler)