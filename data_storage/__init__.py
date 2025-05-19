# data_storage/__init__.py
import os
from data_storage.storage import DatabaseStorage

# Global singleton instance
_db_instance = None

def get_db():
    """
    Get database instance with lazy initialization.
    Uses a singleton with thread-safe operations.
    """
    global _db_instance
    if _db_instance is None:
        # For tests, use in-memory database
        if "PYTEST_CURRENT_TEST" in os.environ:
            _db_instance = DatabaseStorage(db_path=":memory:")
        else:
            _db_instance = DatabaseStorage()
    return _db_instance

# For backwards compatibility with existing code
class LazyDB:
    def __getattr__(self, name):
        return getattr(get_db(), name)

# Replace the direct initialization with lazy-loaded version
db = LazyDB()

# Export the main classes and functions
__all__ = ['DatabaseStorage', 'db', 'get_db']