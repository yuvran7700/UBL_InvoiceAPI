"""
Vaildation methods to assist with auth services
"""

from datetime import datetime, timezone
from src.exceptions.auth_exceptions import MissingTokenError, TokenExpiredError

# This file handles all the validation required for account creation


def session_validation(response: dict):
    """
    Validates users sessions by ensuring its valid and not expired.

    Args:
        response (dict): JWT

    Raises:
        HTTPException: If token is invalid or expired

    """
    if not response:
        raise MissingTokenError()

    expiration_time = response["expires_at"]
    if expiration_time and (
        datetime.fromisoformat(expiration_time) < datetime.now(timezone.utc)
    ):
        raise TokenExpiredError()
