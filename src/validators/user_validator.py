'''
    Validates information required for successful user creation
'''
import abn
from src.exceptions.error_handler import ErrorContext, ValidationErrorHandler
from src.exceptions.user_exceptions import (
    ABNValidationError,
    EmailAlreadyRegisteredError,
    PasswordValidationError,
    UserNotFoundError,
)
from src.repositories.user_repository import get_user


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
    
    Args:
        email (str): The email to check for registration.
    
    Raises:
        EmailAlreadyRegisteredError: If the email is already registered in the system.
    """
    try:
        # Use get_user to check if user exists by email.
        user = get_user(email)
        
        # If get_user succeeds, it means the user exists, so raise EmailAlreadyRegisteredError
        error_handler = ErrorContext(ValidationErrorHandler())
        error_handler.handle_error(EmailAlreadyRegisteredError(f"Email {email} is already registered."))
        raise EmailAlreadyRegisteredError(f"Email {email} is already registered.")

    except UserNotFoundError():
        # If UserNotFoundError is raised, the email is not registered, so do nothing
        pass

    except Exception as e:
        # Handle any unexpected errors and log them
        error_handler = ErrorContext(ValidationErrorHandler())
        error_handler.handle_error(Exception(f"Unexpected error while checking email: {str(e)}"))
        raise  # Re-raise the exception after handling it