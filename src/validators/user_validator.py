import abn
# from fastapi import HTTPException, status
# from src.db.dynamodb_client import user_table
from src.exceptions.error_handler import ErrorContext, ValidationErrorHandler
from src.exceptions.user_exceptions import (
    ABNValidationError,
    EmailAlreadyRegisteredError,
    PasswordValidationError,
)
from src.repositories.user_repository import get_user

#This file handles all the validation required for account creation

#Validates the given ABN
# def validate_abn(abn_value: str):
#     """Validate Australian Business Number format."""
#     if not abn.validate(abn_value):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid ABN format"
#         )

def validate_abn(abn_value: str):
    """Validate Australian Business Number format."""
    if not abn.validate(abn_value):
        error_handler = ErrorContext(ValidationErrorHandler())
        error_handler.handle_error(ABNValidationError("ABN", "Invalid ABN format"))


def validate_password(password: str):
    """Validate password strength."""

    error_handler = ErrorContext(ValidationErrorHandler())

    if len(password) < 8:
        error_handler.handle_error(PasswordValidationError("Password", "Password must be at least 8 characters long"))

    if not any(char.isdigit() for char in password):
        error_handler.handle_error(PasswordValidationError("Password", "Password must contain at least one number"))

    if not any(char.isupper() for char in password):
        error_handler.handle_error(PasswordValidationError("Password", "Password must contain at least one uppercase letter"))

    if not any(char.islower() for char in password):
        error_handler.handle_error(PasswordValidationError("Password", "Password must contain at least one lowercase letter"))

#Checks if the user's email exists in the database
def check_email_exists(email: str):
    """Check if email is already registered.
        args: email 
        calls db get method that checks user exists 
        raises: user already exists error 
        
    
    """
    try:
        # Use get_user to check if user exists by email.
        user = get_user(email)
        
        # If user exists, raise an EmailAlreadyRegisteredError
        if user:
            error_handler = ErrorContext(ValidationErrorHandler())
            error_handler.handle_error(EmailAlreadyRegisteredError())

    except Exception as e:
        # Handle any unexpected errors and log them
        error_handler = ErrorContext(ValidationErrorHandler())
        error_handler.handle_error(Exception(f"Unexpected error while checking email: {str(e)}"))


''''  
def validate_password(password: str):
    """Validate password strength."""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    if not any(char.isdigit() for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number"
        )
    if not any(char.isupper() for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter"
        )
    if not any(char.islower() for char in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter"
        )

'''