from fastapi.testclient import TestClient
from src.main import app
import pytest
from tests.conftest import sample_user_json
from src.utils.auth_helpers import delete_all_user_items
client = TestClient(app)

@pytest.fixture(autouse=True)
def auto_cleanup():
    """
    Automatically clean up the database after each test
    """
    return delete_all_user_items()

def test_user_registration(sample_user_json):
    """
    Test that the user registration endpoint correctly processes the provided user JSON
    and returns a successful response.
    """

    response = client.post("/v1/users/auth/register", json=sample_user_json)
    print(response.json())

    assert response.status_code == 201, f"Expected status 201, got {response.status_code}"
    
    data = response.json()
    
    # Check that the response contains a success message
    assert "message" in data, "Missing message in response"
    assert data["message"] == "User registered successfully", f"Unexpected message: {data['message']}"
    
    # Validate that the user data was correctly processed
    # For example, check that the email is correctly returned
    assert data["user"]["email"] == sample_user_json["email"], f"Unexpected email: {data['user']['email']}"
    
    # Optionally check that the password was hashed (this assumes the password is not returned in plain text)
    assert "password" not in data["user"], "Password should not be returned in the response"

def test_email_already_exists(sample_user_json):
    """
    Test that the user registration endpoint correctly handles the case where the email already exists.
    """

    # Register the user once
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    print(response.json())
    assert response.status_code == 201, f"Expected status 201, got {response.status_code}"
    
    # Attempt to register the same user again
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    print(response.json())
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"
    
    # Check that the response contains an error message
    data = response.json()
    assert "detail" in data, "Missing detail in response"
    assert "Email already registered" in data["detail"], f"Unexpected error message: {data['detail']}"

def test_invalid_abn(sample_user_json):
    """
    Test that the user registration endpoint correctly handles an invalid ABN.
    """  
    sample_user_json['abn'] = '12345678901'
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid ABN format"

def test_invalid_password(sample_user_json):
    """
    Test that the user registration endpoint correctly handles an invalid password.
    """
    sample_user_json['password'] = 'password'
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    assert response.status_code == 400
    assert response.json()["detail"] == "Password must contain at least one number"

def test_password_hashed(sample_user_json):
    """
    Test that the user registration endpoint correctly hashes the user's password.
    """
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    assert response.status_code == 201
    assert "hashed_password" not in response.json()["user"]
    assert response.json()["user"]["email"] == sample_user_json["email"]
    assert response.json()["user"]["businessName"] == sample_user_json["businessName"]

def test_user_update_password(sample_user_json):
    """
    Test that the user update password endpoint correctly updates the user's password.
    """ 
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    assert response.status_code == 201

    new_password = "NewPassword123"
    update_data = {
        "email": sample_user_json["email"],
        "password": new_password
    }
    response = client.post("/v1/users/auth/update/password", json=update_data)
    assert response.status_code == 200
    print(response.json())
    print(sample_user_json)
    assert response.json()["message"] == "Password updated successfully"
    assert response.json()["user"]["email"] == sample_user_json["email"]
    assert response.json()["user"]["businessName"] == sample_user_json["businessName"]
