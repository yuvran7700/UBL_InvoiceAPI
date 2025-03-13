import uuid
from passlib.context import CryptContext
import boto3
from fastapi import HTTPException
from utils.auth_helpers import (hash_password, 
                                save_user_to_dynamodb, 
                                save_session_to_dynamodb, 
                                get_user)
from src.validators.auth_validator import validate_abn, check_email_exists
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AWS DynamoDB Configuration
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")  # Set your AWS region
users_table = dynamodb.Table("Users")

# Session Expiration Time (in minutes)
SESSION_EXPIRE_MINUTES = 60

# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def register_user(request_data: dict):
    try:
        validate_abn(request_data['abn'])
        check_email_exists(request_data['email'])

        hashed_password = hash_password(request_data['password'])

        user_id = str(uuid.uuid4())

        user_item = {
            'user_id': user_id,
            'email': request_data['email'],
            'businessName': request_data['businessName'],
            'abn': request_data['abn'],
            'hashed_password': hashed_password,
        }

        save_user_to_dynamodb(user_item)

        return {"message": "User registered successfully"}

    except HTTPException as e:
            raise e  # Let FastAPI handle the HTTPException properly
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    
def create_session(email: str):
    try:
        session_id = str(uuid.uuid4())  # Generate a unique session token
        expiration_time = (datetime.now(timezone.utc) + 
                           timedelta(minutes=SESSION_EXPIRE_MINUTES))

        session_item = {
            "session_id": session_id,  # Ensure "S" for string
            "expires_at": expiration_time.isoformat(),
        }

        # Store session in DynamoDB
        save_session_to_dynamodb(email, session_item)

        return session_id

    except HTTPException as e:
            raise e  # Let FastAPI handle the HTTPException properly
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def authenticate_user(request_data: dict):
    """Validate user credentials and return a session token if successful."""
    response = get_user(request_data['email'])
    if not response:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(request_data['password'], response['hashed_password']):
        return None

    return create_session(response["email"])