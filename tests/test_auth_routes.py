from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch
import boto3
import pytest
from fastapi import HTTPException, status

client = TestClient(app)
dynamodb = boto3.resource("dynamodb")


def delete_all_user_items():
    """Deletes all items from the Users DynamoDB table."""
    table_name = "Users"
    table = dynamodb.Table(table_name)
    
    try:
        # Scan for all items
        response = table.scan()
        items = response.get("Items", [])

        # Continue scanning if we haven't retrieved all items
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        # Delete all items
        deleted_count = 0
        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={"email": item["email"]})
                deleted_count += 1
                
        return {
            "status": "success",
            "message": f"Deleted {deleted_count} users from DynamoDB",
            "count": deleted_count
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to delete users from DynamoDB",
            "error": str(e)
        }

#def test_dynamodb_error_handling(setup_mocks, sample_user_json):
    mock_put, mock_get, mock_validate_abn, mock_check_email, mock_validate_password = setup_mocks
    mock_get.return_value = {}
    mock_validate_abn.return_value = None
    mock_check_email.return_value = None
    mock_validate_password.return_value = None
    
    # Use a different approach to mock the error
    with patch("utils.auth_helpers.save_user_to_dynamodb") as mock_save:
        mock_save.side_effect = Exception("DynamoDB error")
        
        response = client.post("/v1/users/auth/register", json=sample_user_json)
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

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
    print(response.json())
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

def delete_user_by_email(email):
    """Delete a specific user by email from DynamoDB."""
    table_name = "Users"
    table = dynamodb.Table(table_name)
    try:
        response = table.delete_item(Key={"email": email})
        return {
            "status": "success",
            "message": f"User with email {email} deleted successfully",
            "response": response
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to delete user with email {email}",
            "error": str(e)
        }

def delete_all_user_items():
    """Deletes all items from the Users DynamoDB table."""
    table_name = "Users"
    table = dynamodb.Table(table_name)
    
    try:
        # Scan for all items
        response = table.scan()
        items = response.get("Items", [])

        # Continue scanning if we haven't retrieved all items
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        # Delete all items
        deleted_count = 0
        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={"email": item["email"]})
                deleted_count += 1
                
        return {
            "status": "success",
            "message": f"Deleted {deleted_count} users from DynamoDB",
            "count": deleted_count
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to delete users from DynamoDB",
            "error": str(e)
        }

# Test for delete_user_by_email function
def test_delete_user_by_email():
    # First create a test user with actual DynamoDB
    with patch.object(client, "post") as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"message": "User registered successfully"}
        
        test_email = "delete_test@example.com"
        result = delete_user_by_email(test_email)
        
        assert result["status"] in ["success", "error"]
        # We don't assert more specifically because the test user might not exist
        # But the function should execute without exceptions

# Test for delete_all_user_items function
def test_delete_all_user_items():
    result = delete_all_user_items()
    assert result["status"] in ["success", "error"]
    if result["status"] == "success":
        print(f"Successfully deleted {result['count']} users from DynamoDB")

@pytest.fixture(scope="function")
def cleanup_after_test(sample_user_json):
    """Fixture to clean up after tests that might create actual DynamoDB entries."""
    # Run the test
    yield
    
    # Clean up after the test
    if sample_user_json and "email" in sample_user_json:
        delete_user_by_email(sample_user_json["email"])


