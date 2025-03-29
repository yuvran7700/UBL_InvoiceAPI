#src/routes/user_routes.py
from fastapi import APIRouter, HTTPException, status
from src.models.user_models import (
    UpdateEmailRequest,
    UpdatePasswordRequest,
    UpdateUsernameRequest,
    UserIn,
    UserOut,
)
from src.services.user_service import (
    create_user,
    update_user_business_name,
    update_user_email,
    update_user_password,
)

router = APIRouter(prefix="/v1/users", tags=["user"])


@router.post("/register", response_model=UserOut)
async def register(user_in: UserIn):
    """
    Registers a new user.

    Args:
        user_in (UserIn): The user input data containing registration details.

    Returns:
        UserOut: The registered user details.

    Raises:
        HTTPException: If an error occurs during user creation.
    """
    try:
        user = create_user(user_in)  # Call service layer
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
    return user


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
    try:
        update_user_password(request)  # Call service layer
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
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
    try:
        update_user_business_name(request)  # Call service layer
        return {"message": "Business name updated successfully"}
    except HTTPException as e:
        print(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


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
    try:
        update_user_email(request)  # Call service layer
        return {"message": "Email updated successfully"}
    except HTTPException as e:
        print(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
