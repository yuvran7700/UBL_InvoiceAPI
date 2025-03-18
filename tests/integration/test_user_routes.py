from fastapi.testclient import TestClient
from src.main import app
import pytest
from tests.conftest import sample_user_json
from src.repositories.user_repository import delete_all_users, get_user

client = TestClient(app)

@pytest.fixture(autouse=True)
def auto_cleanup():
    """
    Automatically clean up the database after each test
    """
    return delete_all_users()

def test_invalid_abn(sample_user_json):
    """
    Test that the user registration endpoint correctly handles an invalid ABN.
    """  
    sample_user_json['abn'] = '12345678901'
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid ABN format"

def test_invalid_password(sample_user_json):
    """
    Test that the user registration endpoint correctly handles an invalid password.
    """
    sample_user_json['password'] = 'PasswordS'
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 400
    assert response.json()["detail"] == "Password must contain at least one number"

@pytest.mark.hash
def test_password_hashed(sample_user_json):
    """
    Test that the user registration endpoint correctly hashes the user's password.
    """
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 200

    user = response.json()
    assert "password" not in user  

# @pytest.mark.update_tests
# def test_update_password(sample_user_json):
#     """
#     Test that the update password endpoint correctly updates the user's password.
#     """
#     # Register a new user
#     response = client.post("/v1/users/register", json=sample_user_json)
#     assert response.status_code == 201

#     # Define the new password payload with all required fields
#     new_password_payload = {
#         "email": sample_user_json["email"],
#         "password": sample_user_json["password"],  # Current password
#         "updated_password": "NewSecurePassword123"  # New password
#     }

#     # Update the user's password
#     response = client.put("/v1/users/auth/update-password", json=new_password_payload)
#     print("Update password response:", response.json())
#     assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
#     data = response.json()
#     assert "message" in data, "Missing message in response"
#     assert data["message"] == "Password updated successfully", f"Unexpected message: {data['message']}"

# @pytest.mark.update_tests
# def test_update_email(sample_user_json):
#     """
#     Test that the update email endpoint correctly updates the user's email.
#     """ 
#     # Register a new user
#     response = client.post("/v1/users/register", json=sample_user_json)
#     assert response.status_code == 201

#     # Define the new email payload with all required fields
#     new_email_payload = {
#         "email": sample_user_json["email"],
#         "updated_email": "newEmail@gmail.com"
#     }       

#     response = client.put("/v1/users/auth/update-email", json=new_email_payload)
#     print("Update email response:", response.json())
#     assert response.status_code == 200, f"Expected status 200, got {response.status_code}" 
#     data = response.json()
#     assert "message" in data, "Missing message in response"
#     assert data["message"] == "Email updated successfully", f"Unexpected message: {data['message']}"

#     curr_user = get_user("newEmail@gmail.com")
#     assert curr_user is not None, "Updated user not found"
#     assert curr_user["email"] == "newEmail@gmail.com"

# @pytest.mark.update_tests
# def test_update_username(sample_user_json):
#     """
#     Test that the update username endpoint correctly updates the user's username.
#     """
#     # Register a new user
#     response = client.post("/v1/users/register", json=sample_user_json)
#     assert response.status_code == 201

#     # Define the new username payload with all required fields
#     new_username_payload = {
#         "email": sample_user_json["email"],
#         "updated_username": "newUsername"
#     }

#     response = client.put("/v1/users/auth/update-username", json=new_username_payload)
#     print("Update username response:", response.json())
#     assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
#     data = response.json()
#     assert "message" in data, "Missing message in response"
#     assert data["message"] == "Username updated successfully", f"Unexpected message: {data['message']}"

#     curr_user = user.get(sample_user_json["email"])
#     assert curr_user is not None, "Updated user not found"
#     assert curr_user["email"] == sample_user_json["email"]
#     assert curr_user["businessName"] == "newUsername"
#     assert curr_user["abn"] == sample_user_json["abn"]
#     assert "hashed_password" in curr_user
#     assert "user_id" in curr_user