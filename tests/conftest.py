import pytest
from utils.logger import get_logger

@pytest.fixture(scope="session", autouse=True)
def logger_fixture(request):
    logger = get_logger("test_suite")
    request.config._logger = logger
    return logger
