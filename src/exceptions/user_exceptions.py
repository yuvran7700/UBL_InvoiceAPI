from fastapi import HTTPException, status
from src.exceptions.validation_exceptions import ValidationError

'''ValidationError in validation_expections
class ValidationError(Exception):
    """Base class for validation exceptions."""

    def __init__(self, message="Validation failed"):
        self.message = message
        super().__init__(self.message)

'''
class ABNValidationError(ValidationError):
    """Raised when the ABN is invalid."""
    def __init__(self, field_name: str = None, message: str = None):
        self.field_name = field_name
        if not message:
            message = f"ABN validation failed"
            if field_name:
                message += f" for field: {field_name}"
        super().__init__(message)

class PasswordValidationError(ValidationError):
    """Raised when the password does not meet the requirements."""
    def __init__(self, field_name: str = None, message: str = None):
        self.field_name = field_name
        if not message:
            message = f"Password validation failed"
            if field_name:
                message += f" for field: {field_name}"
        super().__init__(message)

class EmailAlreadyRegisteredError(HTTPException):
    """Raised when the email is already registered."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
