# from fastapi.testclient import TestClient
# from src.main import app  

# client = TestClient(app)

# import pytest

# def test_register_user(sample_user):
#     """Test the user registration with the sample user data."""
#     # sample_user will be passed as an argument automatically by pytest

#     assert sample_user['email'] == "test@example.com"
#     assert sample_user['password'] == "securepassword123"
#     assert sample_user['businessName'] == "Test Business"

# # from fastapi.testclient import TestClient
# # from unittest.mock import patch
# # from src.main import app  
# # client = TestClient(app)

# # @patch("src.auth_service.user_table.put_item")  # Mocking DynamoDB's put_item
# # def test_register_user(sample_user, mock_put_item):
# #     """Test the user registration with the sample user data."""
# #     mock_put_item.return_value = {}  # Mock successful DynamoDB save

# #     # Use the sample user fixture to pass the user data
# #     response = client.post("/v1/users/auth/register", json=sample_user)

# #     # Assert the response code and response body
# #     assert response.status_code == 201
# #     assert response.json() == {"message": "User registered successfully"}

from fastapi.testclient import TestClient
from src.main import app
import pytest
from unittest.mock import patch
from tests.fixtures.user_fixtures import sample_user  # Import the fixture
from src.services.auth_service import register_user


client = TestClient(app)

# Mocking DynamoDB methods
@patch("src.services.auth_service.user_table.put_item")
@patch("src.services.auth_service.user_table.get_item")
def test_register_user(mock_get_item, mock_put_item, sample_user):
    """
    Test that the registration route processes the sample user data correctly,
    validates the ABN, checks email uniqueness, and returns the correct response.
    """

    # Mock DynamoDB responses
    mock_get_item.return_value = {}  # No item for email, meaning email doesn't exist
    mock_put_item.return_value = {}

    # Send POST request to register the user
    response = client.post("/v1/users/auth/register", json=sample_user)
    
    print(response.text)

    # Assert the response status code is 201 (Created)
    assert response.status_code == 201, f"Expected status 201, got {response.status_code}"

    data = response.json()

    # Check for success message in the response
    assert "message" in data, "Missing message in response"
    assert data["message"] == "User registered successfully", f"Unexpected message: {data['message']}"

    # Mock the `get_item` to simulate an existing user for the same email
    mock_get_item.return_value = {"Item": {"email": sample_user["email"]}}

    # Send a second registration attempt with the same email (it should fail)
    response = client.post("/v1/users/auth/register", json=sample_user)

    # Assert the response status code is 400 (Bad Request) due to email duplication
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
    assert response.json()["detail"] == "Email already registered", f"Unexpected error message: {response.json()['detail']}"

    # Validate the ABN format, for testing purposes we'll use an invalid ABN
    invalid_user_data = sample_user.copy()
    invalid_user_data["abn"] = "invalid_abn"

    # Send a registration attempt with an invalid ABN (it should fail)
    response = client.post("/v1/users/auth/register", json=invalid_user_data)

    # Assert the response status code is 400 (Bad Request) due to invalid ABN
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
    assert response.json()["detail"] == "Invalid ABN format", f"Unexpected error message: {response.json()['detail']}"