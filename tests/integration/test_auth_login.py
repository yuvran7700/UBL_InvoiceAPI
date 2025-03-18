from fastapi.testclient import TestClient
import pytest
from src.main import app
from tests.conftest import sample_user_json, sample_session_json # noqa: F401
from tests.utils.utils_test import ( 
                                    delete_all_session_items, 
                                    reset_too_many_attemps)
from src.repositories.user_repository import delete_all_users
client = TestClient(app)



def test_login_user_wrong_password(sample_user_json): # noqa: F811

    delete_all_users()
    delete_all_session_items()

    response = client.post("/v1/users/register", 
                           json=sample_user_json) # noqa: F811
    assert response.status_code == 200

    sample_session = {
        "email": "test1@example.com",
        "password": "wrong_password"
    }

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", 
                           json=sample_session) # noqa: F811
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_user_wrong_email(sample_user_json): # noqa: F811

    delete_all_users()
    delete_all_session_items()

    client.post("/v1/users/register", json = sample_user_json) # noqa: F811

    sample_session = {
        "email": "unknown@example.com",
        "password": "securepassword123"
    }

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json = sample_session) # noqa: F811
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_login_failed_attempt(sample_user_json): # noqa: F811

    delete_all_users()
    delete_all_session_items()

    client.post("/v1/users/register", json = sample_user_json) # noqa: F811

    sample_session = {
        "email": "test1@example.com",
        "password": "wrong_password"
    }

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", 
                           json=sample_session) # noqa: F811
    assert response.status_code == 401

    response = client.post("/v1/users/auth/login", 
                           json=sample_session) # noqa: F811
    assert response.status_code == 401

    response = client.post("/v1/users/auth/login", 
                           json=sample_session) # noqa: F811
    assert response.status_code == 401

    response = client.post("/v1/users/auth/login", 
                           json=sample_session) # noqa: F811
    assert response.status_code == 403
    assert response.json()["detail"] == "Too many attempts, try again later."

def test_login_failed_reset_success(sample_user_json, sample_session_json): # noqa: F811

    delete_all_users()
    delete_all_session_items()

    client.post("/v1/users/register", json = sample_user_json) # noqa: F811

    sample_session = {
        "email": "test1@example.com",
        "password": "Wrong_password"
    }

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", 
                           json=sample_session) # noqa: F811
    assert response.status_code == 401

    response = client.post("/v1/users/auth/login", 
                           json=sample_session) # noqa: F811
    assert response.status_code == 401

    response = client.post("/v1/users/auth/login", 
                           json=sample_session) # noqa: F811
    assert response.status_code == 401

    response = client.post("/v1/users/auth/login", 
                           json=sample_session) # noqa: F811
    assert response.status_code == 403
    assert response.json()["detail"] == "Too many attempts, try again later."

    reset_too_many_attemps("test1@example.com")

    response = client.post("/v1/users/auth/login", 
                           json=sample_session_json) # noqa: F811
    assert response.status_code == 201
    assert "JWT" in response.json()

@pytest.mark.login
def test_login_user_success(sample_session_json, sample_user_json): # noqa: F811

    delete_all_users()
    delete_all_session_items()
    response = client.post("/v1/users/register", 
                           json=sample_user_json) # noqa: F811

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", 
                           json=sample_session_json) # noqa: F811
    print(response.json())

    assert response.status_code == 201
    assert "JWT" in response.json()

def test_login_different_tokens(sample_session_json, sample_user_json): # noqa: F811

    sample1 = {
        "business_name": "Test1 Business",
        "email": "test2@example.com",
        "password": "Securepassword123",
        "abn": "51824753556"
    }

    sample2 = {
        "email": "test2@example.com",
        "password": "Securepassword123"
    }

    delete_all_users()
    # delete_all_session_items()
    client.post("/v1/users/register", json=sample_user_json) # noqa: F811
    client.post("/v1/users/register", json=sample1)

    # Send POST request to login the user
    response1 = client.post("/v1/users/auth/login", 
                            json=sample_session_json) # noqa: F811
    response2 = client.post("/v1/users/auth/login", json=sample2)
    assert response1.status_code == 201
    assert "JWT" in response1.json()

    assert response2.status_code == 201
    assert "JWT" in response2.json()

    data1 = response1.json()
    data2 = response2.json()

    assert data1["JWT"] != data2["JWT"]
