import boto3
from src.repositories.v1.auth_repository import save_session_to_dynamodb
from datetime import datetime, timezone
from jose import jwt
import os

from src.repositories.v1.user_repository import get_user

# Load AWS region from environment variables (default to us-east-1)
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

SECRET_KEY = "a3eddf3292bac4ac269ed39a74e6760ed3c34ff3a15f4cb17c61520da8c88b05"
ALGORITHM = "HS256"
SESSION_EXPIRE_MINUTES = 60

def delete_all_user_items():
    """Deletes all items from a DynamoDB table."""
    table_name = "users"
    table = dynamodb.Table(table_name)
    response = table.scan()  # Get all items
    items = response.get("Items", [])

    while "LastEvaluatedKey" in response:  # Continue if there are more items
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    # Batch delete (DynamoDB limits batch writes to 25 items per request)
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"email": item["email"]})  

def delete_all_session_items():
    """Deletes all items from a DynamoDB table."""
    table_name = "sessions"
    table = dynamodb.Table(table_name)
    response = table.scan()  # Get all items
    items = response.get("Items", [])

    while "LastEvaluatedKey" in response:  # Continue if there are more items
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    # Batch delete (DynamoDB limits batch writes to 25 items per request)
    with table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"JWT" : item["JWT"]})  

def create_expired_token():
    expired_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    JWT = jwt.encode(
            {"email": "test1@example.com", 
             "expires_at": expired_time.isoformat()},
            SECRET_KEY,
            algorithm=ALGORITHM
    )
    save_session_to_dynamodb("test1@example.com", JWT)
    return JWT

def reset_too_many_attemps(email: str):

    user = get_user(email)
    user_id = user.user_id
    
    table_name = "users"
    table = dynamodb.Table(table_name)
    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="REMOVE failed_attempts, lockout_until"
    )