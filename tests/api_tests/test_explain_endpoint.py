"""
Unit tests for the /explain API endpoint.
PURPOSE: Test all scenarios of the /explain endpoint including:
- Successful requests
- Invalid inputs (bad FEN, missing fields)
- Error handling
"""

from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from presentation.api.main import app

# Create a TestClient instance
client = TestClient(app)


# TEST CASE 1: Test successful analysis request
def test_explain_endpoint_success():
    """Test successful analysis request."""

    # ARRANGE: Prepare test data
    request_data = {
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",  # Valid starting position
        "moves": ["e7e5"],  # Valid move
        "target_audience": "beginner",  # Valid target audience
    }

    # ACT: Make the API request
    response = client.post("/explain", json=request_data)

    # ASSERT: Verify the response
    assert response.status_code == 200
    assert "success" in response.json()
    assert "explanation" in response.json()


# TEST CASE 2: Test with invalid FEN string
def test_explain_endpoint_invalid_fen():
    """Test with invalid FEN string."""

    # ARRANGE: Prepare test data with INVALID FEN
    request_data = {
        "fen": "invalid_FEN",  # Invalid FEN
        "moves": ["e7e5"],  # Valid move
        "target_audience": "beginner",  # Valid target audience
    }

    # ACT: Make the API request
    response = client.post("/explain", json=request_data)

    # ASSERT: Verify error response
    assert response.status_code == 200
    assert "success" in response.json()
    assert "error" in response.json()
    assert response.json()["error"] is not None


# TEST CASE 3: Test validation error when required field is missing
def test_explain_endpoint_missing_required_field():
    """Test validation error when required field is missing."""

    # ARRANGE: Prepare incomplete request (missing 'fen')
    request_data = {
        "moves": ["e2e4"],  # Valid move
        "target_audience": "beginner",  # Valid target audience
    }

    # ACT: Make the API request
    response = client.post("/explain", json=request_data)

    # ASSERT: Verify Pydantic validation error
    assert response.status_code == 422


# TEST CASE 4: Test with empty moves list
def test_explain_endpoint_empty_moves():
    """Test with empty moves list."""

    # ARRANGE: Prepare request with empty moves
    request_data = {
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",  # Valid starting position
        "moves": [],  # Empty moves list
        "target_audience": "intermediate",  # Valid target audience
    }

    # ACT: Make the API request
    response = client.post("/explain", json=request_data)

    # ASSERT: Verify it still works
    assert response.status_code == 200
    assert "success" in response.json()
    assert "explanation" in response.json()


# TEST CASE 5: Test error handling when use case raises exception
# This test uses MOCKING to simulate errors without breaking real code
@patch("presentation.api.main.Container")
def test_explain_endpoint_use_case_exception(mock_container):
    """Test error handling when use case raises exception."""

    # ARRANGE: Mock the Container to raise an exception
    mock_use_case = Mock()
    mock_use_case.execute.side_effect = ValueError("Test error")
    mock_container.return_value.get_analyze_position_use_case.return_value = (
        mock_use_case
    )

    # ACT: Make the API request
    response = client.post("/explain", json={"fen": "invalid_fen"})

    # ASSERT: Verify graceful error handling
    assert response.status_code == 200
    assert "success" in response.json()
    assert "error" in response.json()
