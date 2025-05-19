# tests/test_api.py
import os

os.environ["PYTEST_CURRENT_TEST"] = "true"  # Ensure we're using test mode

import pytest
from unittest.mock import patch, MagicMock

from api.app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the health check endpoint returns 200 and correct format"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert "status" in data
    assert data["status"] == "ok"


def test_symbols_endpoint(client):
    """Test the symbols endpoint returns list of configured symbols"""
    response = client.get('/symbols')
    assert response.status_code == 200
    data = response.get_json()
    assert "symbols" in data
    assert isinstance(data["symbols"], list)
    assert len(data["symbols"]) > 0
    # Test for some expected symbols
    assert "AAPL" in data["symbols"]
    assert "MSFT" in data["symbols"]


@patch('api.app.get_detector')
def test_pattern_endpoint_success(mock_get_detector, client):
    """Test the pattern endpoint with a valid symbol and successful detection"""
    # Mock the detector and its detect_pattern method
    mock_detector = MagicMock()
    mock_detector.detect_pattern.return_value = True
    mock_get_detector.return_value = mock_detector

    # Call the endpoint
    response = client.get('/pattern/AAPL')

    # Check the response
    assert response.status_code == 200
    data = response.get_json()
    assert "pattern_detected" in data
    assert data["pattern_detected"] is True

    # Verify the mock was called correctly
    mock_detector.detect_pattern.assert_called_once_with(symbol="AAPL")


@patch('api.app.get_detector')
def test_pattern_endpoint_no_pattern(mock_get_detector, client):
    """Test the pattern endpoint when no pattern is detected"""
    # Mock the detector to return False (no pattern)
    mock_detector = MagicMock()
    mock_detector.detect_pattern.return_value = False
    mock_get_detector.return_value = mock_detector

    # Call the endpoint
    response = client.get('/pattern/MSFT')

    # Check the response
    assert response.status_code == 200
    data = response.get_json()
    assert "pattern_detected" in data
    assert data["pattern_detected"] is False


def test_pattern_endpoint_invalid_symbol(client):
    """Test the pattern endpoint with an invalid symbol"""
    response = client.get('/pattern/INVALID')
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


@patch('api.app.get_detector')
def test_pattern_query_endpoint(mock_get_detector, client):
    """Test the pattern query endpoint with a valid symbol"""
    # Mock the detector
    mock_detector = MagicMock()
    mock_detector.detect_pattern.return_value = True
    mock_get_detector.return_value = mock_detector

    # Call the endpoint with query param
    response = client.get('/api/pattern?symbol=AAPL')

    # Check the response
    assert response.status_code == 200
    data = response.get_json()
    assert "pattern_detected" in data
    assert data["pattern_detected"] is True


def test_pattern_query_endpoint_missing_symbol(client):
    """Test the pattern query endpoint without a symbol parameter"""
    response = client.get('/api/pattern')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


@patch('api.app.get_detector')
def test_pattern_endpoint_service_error(mock_get_detector, client):
    """Test the pattern endpoint when an error occurs in the service"""
    # Mock the detector to raise an exception
    mock_detector = MagicMock()
    mock_detector.detect_pattern.side_effect = Exception("Test error")
    mock_get_detector.return_value = mock_detector

    # Call the endpoint
    response = client.get('/pattern/AAPL')

    # Check the response
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data