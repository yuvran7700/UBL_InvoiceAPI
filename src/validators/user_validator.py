import abn
from fastapi import HTTPException, status
from src.db.dynamodb_client import user_table

#This file handles all the validation required for account creation

#Validates the given ABN
def validate_abn(abn_value: str):
    """Validate Australian Business Number format."""
    if not abn.validate(abn_value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ABN format"
        )

#Checks if the user's email exists in the database
def check_email_exists(email: str):
    """Check if email is already registered."""
    try:
        # Scan for email instead of getting by primary key
        response = user_table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email}
        )
        if response.get('Items'):
            logger.warning(f"Email already registered: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            logger.error(f"Error checking email: {str(e)}")
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking email: {str(e)}"
        )
    
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

