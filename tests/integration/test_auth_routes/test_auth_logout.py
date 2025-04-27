from fastapi.testclient import TestClient
from src.main import app
from src.repositories.v1.user_repository import delete_all_users
from tests.conftest import sample_user_json, sample_session_json # noqa: F401
from tests.utils.utils_test import (
                                    delete_all_session_items, 
                                    create_expired_token)

client = TestClient(app)

def test_logout_invalid(sample_session_json, sample_user_json): # noqa: F811

    delete_all_users()

    client.post("/v1/users/register", json=sample_user_json) # noqa: F811

    # Send POST request to login the user
    client.post("/v1/users/auth/login", json=sample_session_json) # noqa: F811

    response = client.post("/v1/users/auth/logout", json={"JWT": "wrong"})
    assert response.status_code == 401

def test_logout_expired(sample_session_json, sample_user_json): # noqa: F811

    delete_all_users()

    client.post("/v1/users/register", json=sample_user_json) # noqa: F811

    token = create_expired_token()

    response = client.post("/v1/users/auth/logout", json={"JWT": token})
    assert response.status_code == 401

def test_logout_missing(sample_session_json, sample_user_json): # noqa: F811

    delete_all_users()
    delete_all_session_items()

    client.post("/v1/users/register", json=sample_user_json) # noqa: F811

    # Send POST request to login the user
    client.post("/v1/users/auth/login", json=sample_session_json) # noqa: F811

    response = client.post("/v1/users/auth/logout", json={"JWT": ""})
    assert response.status_code == 401


def test_logout_user_success(sample_session_json, sample_user_json): # noqa: F811

    delete_all_session_items()
    delete_all_users()

    response = client.post("/v1/users/register", 
                           json = sample_user_json) # noqa: F811

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", 
                           json = sample_session_json) # noqa: F811
    token = response.json()["JWT"]

    response = client.post("/v1/users/auth/logout", json={"JWT": token})
    assert response.status_code == 200
    assert "JWT" not in response.json()
