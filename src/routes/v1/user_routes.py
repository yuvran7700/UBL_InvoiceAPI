#src/routes/user_routes.py

"""
user_routes.py
This module defines the API routes for user account creation and management.
It includes endpoints for user registration, password updates, business name updates,
and email updates.
"""
from fastapi import APIRouter, HTTPException, status
from src.domain.models.user_models import (
    UpdateEmailRequest,
    UpdatePasswordRequest,
    UpdateUsernameRequest,
    UserIn,
    UserOut,
)
from src.services.v1.user_service import (
    create_user,
    update_user_business_name,
    update_user_email,
    update_user_password,
)

router = APIRouter(prefix="/v1/users", tags=["Account Creation and Management (v1) - deprecated"])



@router.post("/register", response_model=UserOut)
async def register(user_in: UserIn):
    """
    Registers a new user.

    **Args:**
        user_in (UserIn): The user input data containing registration details.

    **Returns:**
        UserOut: The registered user details.

    **Raises:**
        Custom Exception Errors: If an error occurs during user creation.
    """
    return create_user(user_in)


@router.put("/update-password")
async def update_password(request: UpdatePasswordRequest):
    """
    Updates the password of an existing user.

    Args:
        request (UpdatePasswordRequest): The request containing the new password details.

    Returns:
        dict: A success message.

    Raises:
        HTTPException: If an error occurs during the password update.
    """
    update_user_password(request)
    return {"message": "Password updated successfully"}


@router.put("/update-business-name")
async def update_business_name(request: UpdateUsernameRequest):
    """
    Updates the business name of an existing user.

    Args:
        request (UpdateUsernameRequest): The request containing the new business name.

    Returns:
        dict: A success message.

    Raises:
        HTTPException: If an error occurs during the business name update.
    """
    update_user_business_name(request)
    return {"message": "Business name updated successfully"}


@router.put("/update-email")
async def update_email(request: UpdateEmailRequest):
    """
    Updates the email address of an existing user.

    Args:
        request (UpdateEmailRequest): The request containing the new email address.

    Returns:
        dict: A success message.

    Raises:
        HTTPException: If an error occurs during the email update.
    """
    update_user_email(request)
    return {"message": "Email updated successfully"}
