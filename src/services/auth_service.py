"""
Users service.
Handles the persistence (CRUD) operations for users.
"""
import uuid
from datetime import datetime, timezone
from passlib.context import CryptContext
from fastapi import HTTPException
from src.utils.auth_helpers import (
    hash_password,
    create_access_token,
    decode_token,
)
from src.validators.auth_validator import validate_abn, session_validation
from src.repositories.auth_repository import (
    save_user_to_dynamodb,
    save_session_to_dynamodb,
    get_user,
    get_token,
    remove_session_from_dynamodb,
    check_email_exists,
    add_failed_attempts,
    reset_failed_attempts
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Session Expiration Time (in minutes)
SESSION_EXPIRE_MINUTES = 60


# Function to verify password
def verify_password(plain_password: str, hashed_password: str):
    """
        Verifies that two passwords are the same, considering hashing.
        
        Args:
            plain_password (str): Non-hashed password
            hashed_password (str): Hashed password
            
        Returns:
            Boolean
            
    """
    return pwd_context.verify(plain_password, hashed_password)


def register_user(request_data: dict):
    """
        Creates a new user.
        
        Args:
            request_data (dict): User registration data
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If validation fails or database operations fail
    """
    try:
        validate_abn(request_data["abn"])
        check_email_exists(request_data["email"])

        hashed_password = hash_password(request_data["password"])

        user_id = str(uuid.uuid4())

        user_item = {
            "user_id": user_id,
            "email": request_data["email"],
            "businessName": request_data["businessName"],
            "abn": request_data["abn"],
            "hashed_password": hashed_password,
        }

        save_user_to_dynamodb(user_item)

        return {"message": "User registered successfully"}

    except HTTPException as e:
        raise e  # Let FastAPI handle the HTTPException properly
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def create_session(request_data: dict):
    """
        Creates a new session by creating a JWT.
        
        Args:
            request_data (dict): User registration data
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If validation fails or database operations fail
    """

    try:
        JWT = create_access_token(request_data) # pylint: disable = invalid-name
        save_session_to_dynamodb(request_data["email"], JWT)
        return JWT
    except HTTPException as e:
        raise e  # Let FastAPI handle the HTTPException properly
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def authenticate_user(request_data: dict):
    """
        Validate user credentials and return a session token if successful.
        
        Args:
            request_data (dict): Session request data
            
        Returns:
            str: JWT
            
        Raises:
            HTTPException: If user is not found, too many attempts
    """
    response = get_user(request_data["email"])
    if not response:
        raise HTTPException(status_code=404, detail="User not found")
    failed_attempts = response.get("failed_attempts", 0)
    lockout_until = response.get("lockout_until")

    if lockout_until:
        lockout_time = datetime.fromisoformat(lockout_until)
        if lockout_time > datetime.now(timezone.utc):
            raise HTTPException(status_code=403,
                                detail="Too many attempts, try again later.")

    if not verify_password(request_data["password"], response["hashed_password"]):
        add_failed_attempts(request_data["email"], failed_attempts + 1)
        return None

    reset_failed_attempts(request_data["email"])

    return create_session(request_data)

def get_JWT(JWT: str): # pylint: disable = invalid-name
    """
        Find the JWT.
        
        Args:
            JWT (str): JSON Web token
            
        Returns:
            str: JWT
            
        Raises:
            HTTPException: If user is not found, too many attempts
    """
    response = get_token(JWT)
    if not response:
        raise HTTPException(status_code=401, detail="Invalid token")
    decoded_JWT = decode_token(JWT) # pylint: disable = invalid-name
    session_validation(decoded_JWT)
    return {"valid": True}


def remove_JWT(JWT: str): # pylint: disable = invalid-name
    """
        Removes the JWT from the database and logs out user.
        
        Args:
            JWT (str): JSON Web token
            
                Returns:
            dict: Success message
            
    """
    decoded = decode_token(JWT)
    session_validation(decoded)
    remove_session_from_dynamodb(JWT)

    return {"message": "Successfully logged out"}


def token_logout_valid(JWT: str): # pylint: disable = invalid-name
    """
        Checks if the user is logged out.
        
        Args:
            JWT (str): JSON Web token
            
        Returns:
            dict: Success message
            
    """
    response = get_token(JWT)
    if response:
        raise HTTPException(
            status_code=401, detail = "Invalid token - user still logged in"
        )
    return {"valid": True}
