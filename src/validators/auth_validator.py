"""
Vaildation methods to assist with auth services
"""
from datetime import datetime, timezone
import abn
from fastapi import HTTPException, status
# This file handles all the validation required for account creation


# Validates the given ABN
def validate_abn(abn_value: str):
    """
        Validates users abn.
        
        Args:
            abn_value (str): users abn
            
        Raises:
            HTTPException: If ABN is in an invalid format
            
    """
    if not abn.validate(abn_value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ABN format"
        )


def session_validation(response: dict):
    """
        Validates users sessions by ensuring its valid and not expired.
        
        Args:
            response (dict): JWT 
            
        Raises:
            HTTPException: If token is invalid or expired
            
    """
    if not response:
        raise HTTPException(status_code=401, detail="Invalid token")

    expiration_time = response["expires_at"]
    if expiration_time and (
        datetime.fromisoformat(expiration_time) < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=401, detail="Token expired")
