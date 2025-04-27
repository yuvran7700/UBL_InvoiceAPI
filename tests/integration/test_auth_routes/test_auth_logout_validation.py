from fastapi.testclient import TestClient
from src.main import app
from src.repositories.v1.user_repository import delete_all_users
from tests.utils.utils_test import delete_all_session_items
from tests.conftest import sample_user_json, sample_session_json # noqa: F401

client = TestClient(app)

def test_logout_missing(sample_session_json, sample_user_json): # noqa: F811

    delete_all_users()
    delete_all_session_items()

    client.post("/v1/users/register", json=sample_user_json) 

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json=sample_session_json) 
    JWT = response.json()['JWT']

    response = client.get("/v1/users/auth/validate/login", 
                          params={"JWT": JWT})
    assert response.status_code == 200

    response = client.post("/v1/users/auth/logout", 
                           json={"JWT": JWT})
    assert response.status_code == 200

    response = client.get("/v1/users/auth/validate/logout", 
                          params={"JWT" : ""})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "token_missing"
    assert response.json()["error"]["message"] == "Token is missing from the request."

def test_logout_invalid_still_login(sample_session_json, sample_user_json): # noqa: F811

    delete_all_users()
    delete_all_session_items()

    client.post("/v1/users/register", json=sample_user_json)

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json=sample_session_json)
    JWT = response.json()['JWT']

    response = client.get("/v1/users/auth/validate/login", 
                          params={"JWT": JWT})
    assert response.status_code == 200

    response = client.get("/v1/users/auth/validate/logout", 
                          params={"JWT": JWT})
    assert response.status_code == 401

def test_logout_valid(sample_session_json, sample_user_json): # noqa: F811

    delete_all_users()
    delete_all_session_items()

    client.post("/v1/users/register", json=sample_user_json)

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", json=sample_session_json)

    JWT = response.json()['JWT']

    response = client.get("/v1/users/auth/validate/login", 
                          params={"JWT": JWT})
    assert response.status_code == 200

    response = client.post("/v1/users/auth/logout", 
                           json={"JWT": JWT})
    assert response.status_code == 200

    response = client.get("/v1/users/auth/validate/logout", 
                          params={"JWT": JWT})
    assert response.status_code == 500
