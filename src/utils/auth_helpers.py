from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import BaseModel
from src.db.dynamodb_client import user_table, session_table
from datetime import datetime, timedelta, timezone
from jose import jwt
#hash-password helper function 

SECRET_KEY = "a3eddf3292bac4ac269ed39a74e6760ed3c34ff3a15f4cb17c61520da8c88b05"
ALGORITHM = "HS256"
SESSION_EXPIRE_MINUTES = 60
class Token(BaseModel):
    access_token: str
    token_type: str

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash the user's password using bcrypt"""
    return pwd_context.hash(password)

def save_user_to_dynamodb(user_item: dict):
    """Save user data to DynamoDB"""
    try:
        user_table.put_item(Item=user_item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving user to DynamoDB: {str(e)}"
        )

def save_session_to_dynamodb(email: str, JWT: dict):
    """Save session data to DynamoDB"""
    try:
        session_table.put_item(
                Item={
                    "JWT": JWT,
                    "email": email
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating item: {str(e)}"
        )    

def get_user(email: str):
    try:
        response = user_table.get_item(Key={"email": email})
        return response["Item"]
    except Exception:
        return {}

def create_access_token(data: dict):
    to_encode = {"email": data["email"]}
    expiration_time = (datetime.now(timezone.utc) + 
                           timedelta(minutes=SESSION_EXPIRE_MINUTES))
    to_encode["expires_at"] = expiration_time.isoformat() 
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
