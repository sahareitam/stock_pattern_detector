# utils/logger/advanced_logging.py
import functools
import inspect
import time
from typing import Callable, Any
from utils.logger import get_logger


def log_function_call(logger_name: str = None):
    """
    Decorator that logs function calls including parameters,
    execution time, and detailed error information.

    Args:
        logger_name: Optional name for the logger. If None, uses the module name.
    """

    def decorator(func: Callable) -> Callable:
        # Get logger - use provided name or module name
        if logger_name:
            logger = get_logger(logger_name)
        else:
            # Get the module name of the function
            module_name = func.__module__
            logger = get_logger(module_name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function info
            func_name = func.__name__

            # Get file and line info
            frame = inspect.currentframe()
            file_info = inspect.getframeinfo(frame)
            file_path = file_info.filename
            line_no = file_info.lineno

            # Format args for logging (avoid too verbose output)
            args_str = ", ".join([str(a) if len(str(a)) < 50 else f"{str(a)[:47]}..." for a in args])
            kwargs_str = ", ".join([f"{k}={v}" if len(str(v)) < 50 else f"{k}={str(v)[:47]}..."
                                    for k, v in kwargs.items()])

            logger.debug(f"Starting call to {func_name}({args_str}, {kwargs_str}) at {file_path}:{line_no}")

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(f"Successfully completed {func_name} after {elapsed:.3f} seconds")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Failed in {func_name} after {elapsed:.3f} seconds. Error: {str(e)}",
                    exc_info=True
                )
                raise

        return wrapper

    return decorator


def log_method_call(method: Callable) -> Callable:
    """
    Decorator for class methods that logs method calls including class name,
    parameters, execution time, and detailed error information.
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # Get class and method info
        method_name = method.__name__
        class_name = self.__class__.__name__

        # Get logger using class name
        logger = get_logger(f"{self.__class__.__module__}.{class_name}")

        # Get file and line info
        frame = inspect.currentframe()
        file_info = inspect.getframeinfo(frame)
        file_path = file_info.filename
        line_no = file_info.lineno

        # Format args for logging
        args_str = ", ".join([str(a) if len(str(a)) < 50 else f"{str(a)[:47]}..." for a in args])
        kwargs_str = ", ".join([f"{k}={v}" if len(str(v)) < 50 else f"{k}={str(v)[:47]}..."
                                for k, v in kwargs.items()])

        logger.debug(f"Starting call to {class_name}.{method_name}({args_str}, {kwargs_str}) at {file_path}:{line_no}")

        start_time = time.time()
        try:
            result = method(self, *args, **kwargs)
            elapsed = time.time() - start_time
            logger.debug(f"Successfully completed {class_name}.{method_name} after {elapsed:.3f} seconds")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Failed in {class_name}.{method_name} after {elapsed:.3f} seconds. Error: {str(e)}",
                exc_info=True
            )
            raise

    return wrapper


def log_error(logger, message: str, exception: Exception = None, include_location: bool = True):
    """
    Enhanced error logging with location information.

    Args:
        logger: The logger to use
        message: The error message
        exception: Optional exception to log
        include_location: Whether to include file/line information
    """
    if include_location:
        # Get caller information (1 level up)
        frame = inspect.currentframe().f_back
        filename = inspect.getframeinfo(frame).filename
        lineno = inspect.getframeinfo(frame).lineno
        function_name = inspect.getframeinfo(frame).function

        location_info = f"[{filename}:{lineno} in {function_name}]"
        log_message = f"{location_info} {message}"
    else:
        log_message = message

    if exception:
        logger.error(f"{log_message}: {str(exception)}", exc_info=True)
    else:
        logger.error(log_message)