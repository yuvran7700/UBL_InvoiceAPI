from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta
from src.db.dynamodb_client import user_table, session_table

MAX_FAILED_ATTEMPTS = 3
LOCKOUT_DURATION = timedelta(minutes=15)

def check_email_exists(email: str):
    response = user_table.get_item(Key={"user_id": user_id})
    if "Item" in response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )


def save_user_to_dynamodb(user_item: dict):
    """Save user data to DynamoDB"""
    try:
        user_table.put_item(Item=user_item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving user to DynamoDB: {str(e)}",
        )


def save_session_to_dynamodb(email: str, JWT: dict):
    """Save session data to DynamoDB"""
    try:
        session_table.put_item(Item={"JWT": JWT, "email": email})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating item: {str(e)}",
        )


def get_token(JWT: str):
    try:
        response = session_table.get_item(Key={"JWT": JWT})
        return response["Item"]
    except Exception:
        return {}


def remove_session_from_dynamodb(JWT: str):
    """remove session data from DynamoDB"""
    try:
        session_table.delete_item(Key={"JWT": JWT})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating item: {str(e)}",
        )

def add_failed_attempts(email: str, attempts: int):
    lockout_until = None
    if attempts >= MAX_FAILED_ATTEMPTS:
        lockout_until = (datetime.now(timezone.utc) + LOCKOUT_DURATION).isoformat()
    
    user = get_user(email)
    user_id = user.user_id

    user_table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="SET failed_attempts = :attempts, lockout_until = :lockout",
        ExpressionAttributeValues={
            ":attempts": attempts,
            ":lockout": lockout_until
        }
    )

def reset_failed_attempts(email: str):

    user = get_user(email)
    user_id = user.user_id

    user_table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="REMOVE failed_attempts, lockout_until"
    )
