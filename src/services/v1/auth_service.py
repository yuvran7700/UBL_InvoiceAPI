"""
Auth service.
Handles the persistence (CRUD) operations for users.
"""

#FastApI imports
from datetime import datetime, timezone
from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Utils imports
from src.exceptions.base_exceptions import APIBaseException
from src.utils.auth_helpers import (
    create_access_token,
    decode_token,
)

# Validator and Exception imports
from src.exceptions.auth_exceptions import (
    InvalidCredentialsError,
    TokenStillActiveError,
)
from src.exceptions.user_exceptions import UserNotFoundError
from src.validators.auth_validator import session_validation

# Repository imports
from src.repositories.v1.auth_repository import (
    save_session_to_dynamodb,
    get_token,
    remove_session_from_dynamodb,
    add_failed_attempts,
    reset_failed_attempts,
)

from src.repositories.v1.user_repository import get_user_item

# Initialize the security scheme
security = HTTPBearer()
DEFAULT_TEST_JWT = "test-token"

# Initialize the security scheme
security = HTTPBearer()
DEFAULT_TEST_JWT = "test-token"

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

    JWT = create_access_token(request_data)  # pylint: disable = invalid-name
    save_session_to_dynamodb(request_data["email"], JWT)
    return JWT


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
    response = get_user_item(request_data["email"])
    if not response:
        raise UserNotFoundError(request_data["email"])
    
    failed_attempts = response.get("failed_attempts", 0)
    lockout_until = response.get("lockout_until")

    if lockout_until:
        lockout_time = datetime.fromisoformat(lockout_until)
        if lockout_time > datetime.now(timezone.utc):
            raise InvalidCredentialsError("Too many login attempts. Try again after 15 minutes.")

    if not verify_password(request_data["password"], response["hashed_password"]):
        add_failed_attempts(request_data["email"], failed_attempts + 1)
        raise InvalidCredentialsError("Incorrect password. Check your credentials.")

    reset_failed_attempts(request_data["email"])

    return create_session(request_data)


def get_JWT(JWT: str):  # pylint: disable = invalid-name
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
        raise InvalidCredentialsError("Invalid Token")
    decoded_JWT = decode_token(JWT)  # pylint: disable = invalid-name
    session_validation(decoded_JWT)
    return {"valid": True}


def remove_JWT(JWT: str):  # pylint: disable = invalid-name
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


def token_logout_valid(JWT: str):  # pylint: disable = invalid-name
    """
    Checks if the user is logged out.

    Args:
        JWT (str): JSON Web token

    Returns:
        dict: Success message

    """
    response = get_token(JWT)
    if response:
        raise TokenStillActiveError()
    return {"valid": True}


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to extract the user_id or email from the JWT token.

    :param Authorization: Bearer token from the Authorization header.
    :return: user_id or email of the authenticated user.
    :raises HTTPException: If the token is invalid or expired.

    
    """

    try:
        token = credentials.credentials

        #allow default test token for easier Swagger testing
        if token == DEFAULT_TEST_JWT:
            return "test-user-id"
        
        decoded = decode_token(token)  # Use your team's JWT decoding utility
        session_validation(decoded)  # Optional: check expiry, validity
        user_id = decoded.get("user_id") or decoded.get("email")
        
        if not user_id:
            raise UserNotFoundError(email="unknown or missing from token")

        return user_id
    
    except APIBaseException:
        raise 
    except Exception:
         raise InvalidCredentialsError("Invalid Token or Expired Token")
