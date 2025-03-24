"""Initial testing for main to ensure connection with API."""
from fastapi.testclient import TestClient
from src.main import app  # Import the app instance from main.py

client = TestClient(app)  # Use the app instance to create a test client


def test_hello_world():
    """Testing for main API connection"""
    response = client.get("/")  # Send a GET request to the root URL
    assert response.status_code == 200
    assert response.json() == {"message": "UBL Invoice API is running!"}
