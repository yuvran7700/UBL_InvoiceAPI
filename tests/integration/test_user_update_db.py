import time
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.utils.user_helpers import verify_password
from tests.conftest import sample_user_json
from src.repositories.user_repository import delete_all_users, get_user

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_database():
    """
    Fixture to clean up the database before and after each test
    """
    delete_all_users()  # Clean before test
    yield
    delete_all_users()  # Clean after test


@pytest.mark.update_tests
def test_update_password(sample_user_json):
    """
    Test the full password update process, including validating the user in DynamoDB.
    """

    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 200
    user = response.json()

    new_password = "NewSecurePassword123"
    update_data = {"email": user["email"], "new_password": new_password}  # New password
    response = client.put("/v1/users/update-password", json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Password updated successfully"

    # Retrieve the updated user from the database
    updated_user_in_db = get_user(sample_user_json["email"])
    assert updated_user_in_db is not None

    # Convert UserInDB model to a dictionary for assertions
    stored_user = updated_user_in_db.model_dump()

    # Assert the user data is correct
    assert stored_user["email"] == sample_user_json["email"]
    assert stored_user["business_name"] == sample_user_json["business_name"]
    assert stored_user["abn"] == sample_user_json["abn"]
    assert "hashed_password" in stored_user  # Check that the password is hashed
    assert "user_id" in stored_user  # Ensure that user_id is stored in the database

    # Verify the new password
    assert verify_password(new_password, stored_user["hashed_password"])


@pytest.mark.update_tests
def test_update_business_name(sample_user_json):
    """
    Test updating the business name of a registered user.
    """
    # Register the user first
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 200
    user = response.json()
    print("This is the user:", user)

    # Update the business name
    new_business_name = "Updated Business Name"
    update_data = {
        "email": user["email"],
        "new_business_name": new_business_name,  # New business name
    }
    response = client.put("/v1/users/update-business-name", json=update_data)
    print("This is the response:", response)
    # Validate response
    assert response.status_code == 200
    assert response.json()["message"] == "Business name updated successfully"

    # Fetch user from DB and verify update
    updated_user = get_user(user["email"])  # Assuming this retrieves the updated user
    assert updated_user.business_name == new_business_name


@pytest.mark.update_email
def test_update_email(sample_user_json):
    # Register the user
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 200
    user = response.json()

    # Update the user's email
    new_email = "Newemail@gmail.com"
    update_data = {"email": user["email"], "new_email": new_email}  # New email
    response = client.put("/v1/users/update-email", json=update_data)
    print("This is the response:", response)
    assert response.status_code == 200
    assert response.json()["message"] == "Email updated successfully"

    # Fetch user from DB and verify update
    updated_user = get_user(new_email)  # Assuming this retrieves the updated user
    assert updated_user.email == new_email


"""
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

    # Check that the email was updated in DynamoDB
    stored_user = user.get(new_email)
    assert stored_user is not None
    assert stored_user["email"] == new_email
    assert stored_user["businessName"] == sample_user_json["businessName"]
    assert stored_user["abn"] == sample_user_json["abn"]
    assert "hashed_password" in stored_user
    assert "user_id" in stored_user 

def test_update_username(sample_user_json):    
    # Register the user
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    assert response.status_code == 201

    # Update the user's username
    new_username = "NewUsername"
    update_data = {
        "email": sample_user_json["email"],
        "updated_username": new_username  # New username
    }
    response = client.put("/v1/users/auth/update-username", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Username updated successfully"                  

    # Check that the username was updated in DynamoDB
    stored_user = user.get(sample_user_json["email"])
    assert stored_user is not None
    assert stored_user["email"] == sample_user_json["email"]
    assert stored_user["abn"] == sample_user_json["abn"]
    assert "hashed_password" in stored_user
    assert "user_id" in stored_user
    assert stored_user["businessName"] == new_username
    """
