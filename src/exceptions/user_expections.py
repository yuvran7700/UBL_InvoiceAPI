from fastapi import HTTPException, status
from validation_exceptions import ValidationError
class ABNValiError(ValidationError):
    """Raised when the ABN is invalid."""
    def __init__(self, field_name: str = None, message: str = None):
        self.field_name = field_name
        if not message:
            message = f"ABN validation failed"
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

class PasswordValidationError(HTTPException):
    """Raised when the password does not meet the requirements."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class DatabaseError(HTTPException):
    """Raised when a database operation fails."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {detail}"
        )
