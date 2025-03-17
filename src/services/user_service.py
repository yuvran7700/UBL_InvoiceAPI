import uuid
from fastapi import HTTPException, status
from passlib.context import CryptContext

from src.models.user_models import UserIn, UserInDB
from src.utils.auth_helpers import  hash_password
from src.repositories.auth_repository import user
from src.validators.user_validator import validate_abn, check_email_exists, validate_password
from src.models.auth_models import RegisterRequest, UpdateEmailRequest, UpdatePasswordRequest, update_username_request
from src.db.dynamodb_client import user_table


# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db


def create_user(user_in: UserIn):
    """
    Register a new user with validation and error handling.
    
    Args:
        request_data (dict): User registration data
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If validation fails or database operations fail
    """
    try:
        # Validate all required fields
        validate_abn(user_in.abn)
        check_email_exists(user_in.email)
        validate_password(user_in.password)
        hashed_password = hash_password(user_in.password)
        user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)

    except HTTPException:
        raise  # Re-raise HTTP exceptions as they are already properly formatted
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
        
    return user_in_db

def update_password(self, request_data: UpdatePasswordRequest):
    """
    Update a user's password.
    
    Args:
        request_data (UpdatePasswordRequest): User data including current and new password
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If validation fails or database operations fail
    """
    try:
        # Get the user from DynamoDB
        user_data = user.get(request_data.email)
        
        # Verify the current password is correct
        if not pwd_context.verify(request_data.password, user_data.get('hashed_password')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Validate the new password
        validate_password(request_data.updated_password)
    
        # Hash the new password
        new_hashed_password = hash_password(request_data.updated_password)
        
        # Update the user's password in DynamoDB using the generalized update function
        result = user.update_user(
            user_id=user_data['user_id'],
            update_data={'hashed_password': new_hashed_password}
        )

        return {
            "message": "Password updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating password: {str(e)}"
        )

def update_email(self, request_data: UpdateEmailRequest): 
    """
    Update a user's email.
    
    Args:
        request_data (UpdateEmailRequest): User data including current and new email
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If validation fails or database operations fail
    """
    try:
        # Get the user from DynamoDB
        user_data = user.get(request_data.email)
        
        # Validate the new email does not exist
        check_email_exists(request_data.updated_email)
    
        # Update the user's email in DynamoDB
        result = user.update_user(
            user_id=user_data['user_id'],
            update_data={'email': request_data.updated_email}
        )

        if not result.get('message'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update email"
            )

        return {"message": "Email updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating email: {str(e)}"
        )
    
def update_username(self, request_data: update_username_request):   
    """
    Update a user's username.
    
    Args:
        request_data (update_username_request): User data including current and new username
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If validation fails or database operations fail
    """
    try:
        # Get the user from DynamoDB
        user_data = user.get(request_data.email)
        
        # Update the user's username in DynamoDB
        result = user.update_user(
            user_id=user_data['user_id'],
            update_data={'businessName': request_data.updated_username}
        )

        if not result.get('message'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update username"
            )

        return {"message": "Username updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating username: {str(e)}"
        )