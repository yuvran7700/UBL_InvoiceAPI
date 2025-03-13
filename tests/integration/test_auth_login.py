from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch
from tests.fixtures.session_fixtures import sample_session
from tests.fixtures.user_fixtures import sample_user
from tests.utils.utils_test import delete_all_user_items

client = TestClient(app)

def test_login_user_success(sample_session, sample_user):
    # Mock DynamoDB responses 
    # No item for email, meaning email doesn't exist

    delete_all_user_items()

    response = client.post("/v1/users/auth/register", json=sample_user)

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json=sample_session)
    assert response.status_code == 201
    assert "session_token" in response.json()

def test_login_user_wrong_password(sample_user):
    # Mock DynamoDB responses 
    # No item for email, meaning email doesn't exist

    delete_all_user_items()

    response = client.post("/v1/users/auth/register", json=sample_user)

    sample_session = {
        "email": "test1@example.com",
        "password": "wrong_password"
    }

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json=sample_session)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_user_wrong_password(sample_user):
    # Mock DynamoDB responses 
    # No item for email, meaning email doesn't exist

    delete_all_user_items()

    response = client.post("/v1/users/auth/register", json = sample_user)

    sample_session = {
        "email": "unknown@example.com",
        "password": "any_password"
    }

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json = sample_session)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
