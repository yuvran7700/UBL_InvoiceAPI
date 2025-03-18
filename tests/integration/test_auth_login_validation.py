from fastapi.testclient import TestClient
from src.main import app
from tests.conftest import sample_user_json, sample_session_json # noqa: F401
from tests.utils.utils_test import (delete_all_user_items, 
                                    delete_all_session_items, 
                                    create_expired_token)

client = TestClient(app)

def test_login_invalid(sample_session_json, sample_user_json): # noqa: F811

    delete_all_user_items()
    delete_all_session_items()

    response = client.post("/v1/users/register", 
                           json=sample_user_json) # noqa: F811
    assert response.status_code == 200

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", 
                           json=sample_session_json) # noqa: F811
    assert response.status_code == 201

    response = client.get("/v1/users/auth/validate/login", 
                          params={"JWT": "wrong"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

def test_login_expired(sample_user_json): # noqa: F811

    delete_all_user_items()
    delete_all_session_items()

    response = client.post("/v1/users/register", 
                           json=sample_user_json) # noqa: F811
    assert response.status_code == 200
    
    token = create_expired_token()

    response = client.get("/v1/users/auth/validate/login", 
                          params={"JWT": token})
    assert response.status_code == 401
    assert response.json() == {"detail": "Token expired"}

def test_login_missing(sample_session_json, sample_user_json): # noqa: F811

    delete_all_user_items()
    delete_all_session_items()

    response = client.post("/v1/users/register", 
                           json=sample_user_json) # noqa: F811
    assert response.status_code == 200

    # Send POST request to login the user
    response = client.post("/v1/users/auth/login", 
                           json=sample_session_json) # noqa: F811
    assert response.status_code == 201

    response = client.get("/v1/users/auth/validate/login", 
                          params={ "JWT" : "" })
    assert response.status_code == 401
    assert response.json() == {"detail": "Token missing"}

def test_login_user_success(sample_session_json, sample_user_json): # noqa: F811

    delete_all_user_items()
    delete_all_session_items()
    
    response = client.post("/v1/users/register", 
                           json=sample_user_json) # noqa: F811

    # Send POST request to login the user
    token = client.post("/v1/users/auth/login", 
                        json=sample_session_json) # noqa: F811
    assert token.status_code == 201
    assert "JWT" in token.json()

    response = client.get("/v1/users/auth/validate/login", 
                          params={"JWT": token.json()["JWT"]})
    assert response.status_code == 201
    assert response.json() == {"valid": True}
