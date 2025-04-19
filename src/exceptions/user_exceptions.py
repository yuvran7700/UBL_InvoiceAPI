# src.exceptions/user.py

from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from .base_exceptions import APIBaseException

class ABNValidationError(APIBaseException):
    def __init__(self, abn: str):
        super().__init__(
            message=f"The ABN '{abn}' is invalid. It must be 11 digits and pass ABN checksum validation.",
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            code="invalid_abn"
        )

class EmailAlreadyRegisteredError(APIBaseException):
    def __init__(self, email: str):
        super().__init__(
            message=f"Email '{email}' is already registered.",
            status_code=HTTP_409_CONFLICT,
            code="email_exists"
        )

class PasswordValidationError(APIBaseException):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Password is invalid: {reason}",
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            code="invalid_password"
        )

class UserNotFoundError(APIBaseException):
    def __init__(self, email: str):
        super().__init__(
            message=f"User with email '{email}' was not found.",
            status_code=HTTP_404_NOT_FOUND,
            code="user_not_found"
        )
