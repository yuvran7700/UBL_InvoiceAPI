"""
Validates information required for successful user creation
"""

import abn
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
        raise ABNValidationError(abn_value)


def validate_password(password: str):
    """Validate password strength."""
    if len(password) < 8:
        raise PasswordValidationError("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        raise PasswordValidationError("Password must contain at least one number.")
    if not any(char.isupper() for char in password):
        raise PasswordValidationError("Password must contain at least one uppercase letter.")
    if not any(char.islower() for char in password):
        raise PasswordValidationError("Password must contain at least one lowercase letter.")



# Checks if the user's email exists in the database
def check_email_exists(email: str):
    """Check if email is already registered.

    Args:
        email (str): The email to check for registration.

    Raises:
        EmailAlreadyRegisteredError: If the email is already registered in the system.
    """

    # Use get_user to check if user exists by email.
    user = get_user(email)

    if user:
        # If get_user succeeds, it means the user exists, so raise EmailAlreadyRegisteredError
       raise EmailAlreadyRegisteredError(email)



def check_user_exists(email: str):
    """checks user exists in db

    args: email

    rasises:
    usernotfounderror

    """

    user = get_user(email)

    if not user:
        raise UserNotFoundError(email)
    return user.user_id
