import uuid
from passlib.context import CryptContext
import abn
import boto3
from fastapi import HTTPException, status
from utils.auth_helpers import hash_password, save_user_to_dynamodb, save_session_to_dynamodb, get_item_using_email
from src.validators.auth_validator import validate_abn, check_email_exists
from datetime import datetime, timedelta

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
        expiration_time = datetime.now(datetime.timezone.utc)() + timedelta(minutes=SESSION_EXPIRE_MINUTES)

        session_item = {
            "session_id": session_id,  # Ensure "S" for string
            "email": email,  # Ensure "S" for string (or "N" if it's a number)
            "expires_at": expiration_time.isoformat(),
        }

        # Store session in DynamoDB
        save_session_to_dynamodb(session_item)

        return session_id

    except HTTPException as e:
            raise e  # Let FastAPI handle the HTTPException properly
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def authenticate_user(request_data: dict):
    """Validate user credentials and return a session token if successful."""
    response = get_item_using_email(request_data['email'])
    print(request_data)
    print(request_data['email'])
    print(response)
    user = response.get("Item")
    hashed_password = hash_password(request_data['password'])
    print(hashed_password)
    if not user or not verify_password(hashed_password, user["hashed_password"]):
        return None

    return create_session(user["email"])