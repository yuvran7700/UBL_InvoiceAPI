from fastapi.testclient import TestClient
from src.main import app
import pytest
from tests.conftest import sample_user_json
from src.repositories.user_repository import delete_all_users

client = TestClient(app)


@pytest.fixture(autouse=True)
def auto_cleanup():
    """
    Automatically clean up the database after each test
    """
    return delete_all_users()


# ----------------------------------------------------------------
# Tests for the /register endpoint
# ----------------------------------------------------------------


@pytest.mark.routes
def test_invalid_abn(sample_user_json):
    """
    Test that the user registration endpoint correctly handles an invalid ABN.
    """
    sample_user_json["abn"] = "12345678901"
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid ABN format"


@pytest.mark.routes
def test_invalid_password_missing_number(sample_user_json):
    """
    Test that the user registration endpoint correctly handles a password without a number.
    """
    sample_user_json["password"] = "PasswordS"
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 400
    assert response.json()["detail"] == "Password must contain at least one number"


@pytest.mark.routes
def test_invalid_password_too_short(sample_user_json):
    """
    Test that the user registration endpoint correctly handles a password that is too short.
    """
    sample_user_json["password"] = "Pa1"
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 400
    assert response.json()["detail"] == "Password must be at least 8 characters long"


@pytest.mark.routes
def test_invalid_password_no_uppercase(sample_user_json):
    """
    Test that the user registration endpoint correctly handles a password without uppercase letters.
    """
    sample_user_json["password"] = "password1"
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Password must contain at least one uppercase letter"
    )


@pytest.mark.routes
def test_invalid_password_no_lowercase(sample_user_json):
    """
    Test that the user registration endpoint correctly handles a password without lowercase letters.
    """
    sample_user_json["password"] = "PASSWORD1"
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Password must contain at least one lowercase letter"
    )


@pytest.mark.routes
def test_password_hashed(sample_user_json):
    """
    Test that the user registration endpoint correctly hashes the user's password.
    """
    response = client.post("/v1/users/register", json=sample_user_json)
    assert response.status_code == 200

    user = response.json()
    assert "password" not in user


@pytest.mark.routes
def test_register_missing_field():
    # Sending a payload missing a required field (e.g. email)
    payload = {
        "password": "password123",
        "business_name": "Test Business",
        "abn": "123456789",
    }
    response = client.post("/v1/users/register", json=payload)
    # FastAPI will return 422 Unprocessable Entity for validation errors.
    assert response.status_code == 422


# ----------------------------------------------------------------
# Tests for the /update-password endpoint
# ----------------------------------------------------------------


def test_update_password_missing_field():
    # Missing the old_password field.
    payload = {
        "email": "test@example.com",
    }
    response = client.put("/v1/users/update-password", json=payload)
    assert response.status_code == 422


# ----------------------------------------------------------------
# Tests for the /update-business-name endpoint
# ----------------------------------------------------------------


def test_update_business_name_missing_field():
    # Missing the email field.
    payload = {"new_business_name": "New Business Name"}
    response = client.put("/v1/users/update-business-name", json=payload)
    assert response.status_code == 422


# ----------------------------------------------------------------
# Tests for the /update-email endpoint
# ----------------------------------------------------------------


def test_update_email_missing_field():
    # Missing the original email field.
    payload = {"new_email": "new@example.com"}
    response = client.put("/v1/users/update-email", json=payload)
    assert response.status_code == 422
