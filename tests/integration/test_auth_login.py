from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch
from tests.fixtures.session_fixtures import sample_session
from tests.fixtures.user_fixtures import sample_user

client = TestClient(app)

# Mocking DynamoDB methods
@patch("src.db.dynamodb_client.user_table.query")
@patch("src.db.dynamodb_client.user_table.put_item")
@patch("src.db.dynamodb_client.user_table.get_item")
def test_login_user(mock_query, mock_get_item, mock_put_item, sample_session, sample_user):
    # Mock DynamoDB responses 
    # No item for email, meaning email doesn't exist
    mock_put_item.return_value = {}
    mock_query.return_value = {"Items": [{"email": sample_session["email"], "hashed_password": "hashed_correct_password"}]}
    mock_get_item.return_value = {}
    print(f"Mocked query response: {response}")

    response = client.post("/v1/users/auth/register", json=sample_user)
    
    print("hello")
    print(response.text)

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json=sample_session)
    
    print(response.text)

    print("Response JSON:", response.json())
    # Assert the response status code is 201 (Created)
    assert response.status_code == 201, f"Expected status 201, got {response.status_code}"  # noqa: E501

    data = response.json()

    # Check for success message in the response
    assert "message" in data, "Missing message in response"
    assert data["message"] == "User registered successfully", f"Unexpected message: {data['message']}"  # noqa: E501
