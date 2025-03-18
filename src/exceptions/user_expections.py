from fastapi import HTTPException, status

class InvalidABNError(HTTPException):
    """Raised when the ABN is invalid."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ABN format"
        )

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
