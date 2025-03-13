from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch
import boto3
client = TestClient(app)

#test helper that clears the table: 

dynamodb = boto3.resource("dynamodb")

def delete_all_user_items():
    """Deletes all items from a DynamoDB table."""
    table_name = "Users"
    table = dynamodb.Table(table_name)
    response = table.scan()  # Get all items
    items = response.get("Items", [])

    while "LastEvaluatedKey" in response:  # Continue if there are more items
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    # Batch delete (DynamoDB limits batch writes to 25 items per request)
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"Item": {"email": item["email"]}})
            

    print(f"Deleted {len(items)} items from {table_name}")    


# @patch("src.db.dynamodb_client.user_table.put_item")
# @patch("src.db.dynamodb_client.user_table.get_item")
# def test_register_user(mock_get_item, mock_put_item, sample_user_json):
#     # Mock DynamoDB responses
#     mock_get_item.return_value = {}
#     mock_put_item.return_value = {}

#     # Test successful registration
#     response = client.post("/v1/users/auth/register", json=sample_user_json)
#     assert response.status_code == 201
#     assert response.json()["message"] == "User registered successfully"

#     # Test email duplication
#     mock_get_item.return_value = {"Item": {"email": sample_user_json["email"]}}
#     response = client.post("/v1/users/auth/register", json=sample_user_json)
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Email already registered"

#     # Test invalid ABN format
#     invalid_user_data = sample_user_json.copy()
#     invalid_user_data["abn"] = "invalid_abn"
#     response = client.post("/v1/users/auth/register", json=invalid_user_data)
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Invalid ABN format"

# Mocking DynamoDB methods
@patch("src.db.dynamodb_client.user_table.put_item")
@patch("src.db.dynamodb_client.user_table.get_item")
def test_register_user(mock_get_item, mock_put_item, sample_user_json):
    # Mock DynamoDB responses 
    # No item for email, meaning email doesn't exist
    mock_get_item.return_value = {}  
    mock_put_item.return_value = {}

    # Send POST request to register the user
    response = client.post("/v1/users/auth/register", json=sample_user_json)
    
    print(response.text)

    # Assert the response status code is 201 (Created)
    assert response.status_code == 201, f"Expected status 201, got {response.status_code}"  # noqa: E501

    data = response.json()

    # Check for success message in the response
    assert "message" in data, "Missing message in response"
    assert data["message"] == "User registered successfully", f"Unexpected message: {data['message']}"  # noqa: E501

    # Mock the `get_item` to simulate an existing user for the same email
    mock_get_item.return_value = {"Item": {"email": sample_user_json["email"]}}

    # Send a second registration attempt with the same email (it should fail)
    response = client.post("/v1/users/auth/register", json=sample_user_json)

    # Assert the response status code is 400 (Bad Request) due to email duplication
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"  # noqa: E501
    assert response.json()["detail"] == "Email already registered", f"Unexpected error message: {response.json()['detail']}"  # noqa: E501

    # Validate the ABN format, for testing purposes we'll use an invalid ABN
    invalid_user_data = sample_user_json.copy()
    invalid_user_data["abn"] = "invalid_abn"

    # Send a registration attempt with an invalid ABN (it should fail)
    response = client.post("/v1/users/auth/register", json=invalid_user_data)

    # Assert the response status code is 400 (Bad Request) due to invalid ABN
    assert response.status_code == 400, f"Expected status 400, got {response.status_code}"  # noqa: E501
    assert response.json()["detail"] == "Invalid ABN format", f"Unexpected error message: {response.json()['detail']}"  # noqa: E501