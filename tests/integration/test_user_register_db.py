import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.repositories.user_repository import delete_all_users, get_user
from src.utils.user_helpers import  verify_password
from tests.conftest import sample_user_json

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_database():
    """
    Fixture to clean up the database before and after each test
    """
    delete_all_users()  # Clean before test
    yield
    delete_all_users()   # Clean after test

@pytest.mark.db
def test_user_registration(sample_user_json):
    """
    Test the full registration process, including validating the user in DynamoDB.
    """
    # Make the API request to register the user
    response = client.post("/v1/users/register", json=sample_user_json)

    # Assert the API responds with a success message and status code 201
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert "user" in data

    # Check that the response contains user data
    user_data = data["user"]
    assert user_data["email"] == sample_user_json["email"]
    assert user_data["business_name"] == sample_user_json["business_name"]
    assert user_data["abn"] == sample_user_json["abn"]
    assert "password" not in user_data

    stored_user = get_user(sample_user_json["email"])
    assert stored_user is not None
    assert stored_user["email"] == sample_user_json["email"]
    assert stored_user["business_name"] == sample_user_json["business_name"]
    assert stored_user["abn"] == sample_user_json["abn"]
    assert "hashed_password" in stored_user
    assert "user_id" in stored_user
