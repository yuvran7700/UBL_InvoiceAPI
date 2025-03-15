from fastapi.testclient import TestClient
from src.main import app
from tests.conftest import sample_user_json, sample_session_json
from tests.utils.utils_test import delete_all_user_items, delete_all_session_items

client = TestClient(app)

def test_login_user_wrong_password(sample_user_json):

    delete_all_user_items()
    delete_all_session_items()

    response = client.post("/v1/users/auth/register", json=sample_user_json)

    sample_session = {
        "email": "test1@example.com",
        "password": "wrong_password"
    }

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json=sample_session)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_user_wrong_email(sample_user_json):

    delete_all_user_items()
    delete_all_session_items()

    client.post("/v1/users/auth/register", json = sample_user_json)

    sample_session = {
        "email": "unknown@example.com",
        "password": "securepassword123"
    }

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json = sample_session)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_login_user_success(sample_session_json, sample_user_json):
    # Mock DynamoDB responses 
    # No item for email, meaning email doesn't exist

    delete_all_user_items()
    delete_all_session_items()
    response = client.post("/v1/users/auth/register", json=sample_user_json)

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json=sample_session_json)
    assert response.status_code == 201
    assert "JWT" in response.json()

def test_login_different_tokens(sample_session_json, sample_user_json):

    sample1 = {
        "businessName": "Test1 Business",
        "email": "test2@example.com",
        "password": "securepassword123",
        "abn": "51824753556"
    }

    sample2 = {
        "email": "test2@example.com",
        "password": "securepassword123"
    }

    delete_all_user_items()
    # delete_all_session_items()
    client.post("/v1/users/auth/register", json=sample_user_json)
    client.post("/v1/users/auth/register", json=sample1)

    # Send POST request to login the user
    response1 = client.post("/v1/users/auth/login", json=sample_session_json)
    response2 = client.post("/v1/users/auth/login", json=sample2)
    assert response1.status_code == 201
    assert "JWT" in response1.json()

    assert response2.status_code == 201
    assert "JWT" in response2.json()

    data1 = response1.json()
    data2 = response2.json()

    assert data1["JWT"] != data2["JWT"]