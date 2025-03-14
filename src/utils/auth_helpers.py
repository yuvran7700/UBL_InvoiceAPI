from passlib.context import CryptContext
from fastapi import HTTPException, status
from src.db.dynamodb_client import user_table
#hash-password helper function 


# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash the user's password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(password: str) -> str:
    """Verify the user's password has been hashed"""
    hash = hash_password(password)
    return pwd_context.verify(password,hash)

def save_user_to_dynamodb(user_item: dict):
    """Save user data to DynamoDB"""
    try:
        user_table.put_item(Item=user_item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving user to DynamoDB: {str(e)}"
        )
