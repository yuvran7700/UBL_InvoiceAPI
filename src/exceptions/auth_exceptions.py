"""
Exception classes specific to authentication-related errors.
"""

from starlette.status import HTTP_401_UNAUTHORIZED
from src.exceptions.base_exceptions import APIBaseException


class InvalidCredentialsError(APIBaseException):
    def __init__(self, details: str = "Invalid credentials provided."):
        super().__init__(
            message=details,
            status_code=HTTP_401_UNAUTHORIZED,
            code="invalid_credentials"
        )


class MissingTokenError(APIBaseException):
    def __init__(self):
        super().__init__(
            message="Token is missing from the request.",
            status_code=HTTP_401_UNAUTHORIZED,
            code="token_missing"
        )


class TokenExpiredError(APIBaseException):
    def __init__(self):
        super().__init__(
            message="The token has expired.",
            status_code=HTTP_401_UNAUTHORIZED,
            code="token_expired"
        )


class TokenStillActiveError(APIBaseException):
    def __init__(self):
        super().__init__(
            message="Token is still active. Logout not confirmed.",
            status_code=HTTP_401_UNAUTHORIZED,
            code="token_still_active"
        )
