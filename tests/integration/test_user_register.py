import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.utils.auth_helpers import  verify_password
from tests.conftest import sample_user_json
from src.repositories.auth_repository import user

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_database():
    """
    Fixture to clean up the database before and after each test
    """
    user.delete_all()  # Clean before test
    yield
    user.delete_all()  # Clean after test


def test_user_registration(sample_user_json):
    """
    Test the full registration process, including validating the user in DynamoDB.
    """
    # Make the API request to register the user
    response = client.post("/v1/users/auth/register", json=sample_user_json)

    # Assert the API responds with a success message and status code 201
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert "user" in data

    # Check that the response contains user data
    user_data = data["user"]
    assert user_data["email"] == sample_user_json["email"]
    assert user_data["businessName"] == sample_user_json["businessName"]
    assert user_data["abn"] == sample_user_json["abn"]
    assert "password" not in user_data

    stored_user = user.get(sample_user_json["email"])
    assert stored_user is not None
    assert stored_user["email"] == sample_user_json["email"]
    assert stored_user["businessName"] == sample_user_json["businessName"]
    assert stored_user["abn"] == sample_user_json["abn"]
    assert "hashed_password" in stored_user
    assert "user_id" in stored_user

@pytest.mark.update_tests
def test_update_password(sample_user_json):
    """
    Test the full password update process, including validating the user in DynamoDB.
    """
    # Register the user
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    assert response.status_code == 201

    # Update the user's password
    new_password = "NewSecurePassword123"
    update_data = {
        "email": sample_user_json["email"],
        "password": sample_user_json["password"],  # Current password
        "updated_password": new_password  # New password
    }
    response = client.put("/v1/users/auth/update-password", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password updated successfully"

    # Check that the password was updated in DynamoDB
    stored_user = user.get(sample_user_json["email"])
    assert stored_user is not None
    assert stored_user["email"] == sample_user_json["email"]
    assert stored_user["businessName"] == sample_user_json["businessName"]
    assert stored_user["abn"] == sample_user_json["abn"]
    assert "hashed_password" in stored_user
    assert "user_id" in stored_user

    # Verify the new password
    assert verify_password(new_password, stored_user["hashed_password"])

@pytest.mark.update_tests
def test_update_email(sample_user_json):    
    # Register the user
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    assert response.status_code == 201

    # Update the user's email
    new_email = "Newemail@gmail.com"
    update_data = {
        "email": sample_user_json["email"],
        "updated_email": new_email  # New email
    }
    response = client.put("/v1/users/auth/update-email", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Email updated successfully"                  