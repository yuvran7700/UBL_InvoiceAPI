from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch
import boto3
import pytest
from fastapi import HTTPException, status

client = TestClient(app)
dynamodb = boto3.resource("dynamodb")

@pytest.fixture(autouse=True)
def setup_mocks():
    """Setup common mocks for all tests"""
    with patch("src.db.dynamodb_client.user_table.put_item") as mock_put, \
         patch("src.db.dynamodb_client.user_table.get_item") as mock_get, \
         patch("src.validators.auth_validator.validate_abn") as mock_validate_abn, \
         patch("src.validators.auth_validator.check_email_exists") as mock_check_email, \
         patch("src.validators.auth_validator.validate_password") as mock_validate_password, \
         patch("utils.auth_helpers.hash_password", return_value="hashed_password"), \
         patch("utils.auth_helpers.save_user_to_dynamodb", return_value=None):
        
        yield mock_put, mock_get, mock_validate_abn, mock_check_email, mock_validate_password

def test_successful_user_registration(setup_mocks, sample_user_json):
    mock_put, mock_get, mock_validate_abn, mock_check_email, mock_validate_password = setup_mocks
    mock_get.return_value = {}  # No existing user
    mock_put.return_value = {}
    # Set up validation mocks to pass
    mock_validate_abn.return_value = None
    mock_check_email.return_value = None
    mock_validate_password.return_value = None
    
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"

def test_duplicate_email_registration(setup_mocks, sample_user_json):
    mock_put, mock_get, mock_validate_abn, mock_check_email, mock_validate_password = setup_mocks
    mock_get.return_value = {"Item": {"email": sample_user_json["email"]}}
    mock_validate_abn.return_value = None
    mock_check_email.side_effect = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered"
    )
    mock_validate_password.return_value = None
    
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_invalid_abn_format(setup_mocks, sample_user_json):
    mock_put, mock_get, mock_validate_abn, mock_check_email, mock_validate_password = setup_mocks
    mock_get.return_value = {}
    mock_validate_abn.side_effect = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid ABN format"
    )
    mock_check_email.return_value = None
    mock_validate_password.return_value = None
    
    invalid_user_data = sample_user_json.copy()
    invalid_user_data["abn"] = "invalid_abn"
    response = client.post("/v1/users/auth/register", json=invalid_user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid ABN format"

def test_missing_required_fields(setup_mocks, sample_user_json):
    mock_put, mock_get, mock_validate_abn, mock_check_email, mock_validate_password = setup_mocks
    mock_get.return_value = {}
    mock_validate_abn.return_value = None
    mock_check_email.return_value = None
    mock_validate_password.return_value = None
    
    missing_fields = sample_user_json.copy()
    del missing_fields["businessName"]
    response = client.post("/v1/users/auth/register", json=missing_fields)
    assert response.status_code == 422

def test_invalid_email_format(setup_mocks, sample_user_json):
    mock_put, mock_get, mock_validate_abn, mock_check_email, mock_validate_password = setup_mocks
    mock_get.return_value = {}
    mock_validate_abn.return_value = None
    mock_check_email.return_value = None
    mock_validate_password.return_value = None
    
    invalid_email = sample_user_json.copy()
    invalid_email["email"] = "not-an-email"
    response = client.post("/v1/users/auth/register", json=invalid_email)
    assert response.status_code == 422

def test_password_validation(setup_mocks, sample_user_json):
    mock_put, mock_get, mock_validate_abn, mock_check_email, mock_validate_password = setup_mocks
    mock_get.return_value = {}
    mock_validate_abn.return_value = None
    mock_check_email.return_value = None
    mock_validate_password.side_effect = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password must be at least 8 characters long"
    )
    
    short_password = sample_user_json.copy()
    short_password["password"] = "123"
    response = client.post("/v1/users/auth/register", json=short_password)
    assert response.status_code == 400
    assert response.json()["detail"] == "Password must be at least 8 characters long"


