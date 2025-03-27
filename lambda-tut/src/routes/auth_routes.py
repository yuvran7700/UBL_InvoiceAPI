"""
API route handler for user assoicated routes.
"""

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from src.services.auth_service import (
    authenticate_user,
    get_JWT,
    remove_JWT,
    token_logout_valid,
)
from src.models.auth_models import LogOutRequest, SessionRequest

router = APIRouter(prefix="/v1/users/auth", tags=["auth"])


@router.post("/login")
async def login_user(request: SessionRequest):
    """
    Authenticate the user and return a session token.

    :param file: Session Request.
    :return: String.
    :raises HTTPException: If there is a server error or invalid credentials

    """
    try:
        JWT = authenticate_user(request.dict())  # pylint: disable = invalid-name
        print(f"JWT generated: {JWT}")
        if not JWT:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"JWT": JWT})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.get("/validate/login", response_model=dict)
async def login_validation(JWT: str = Query(...)):  # pylint: disable = C0103
    """
    Validates if the user is logged in.

    :param file: JWT (str)
    :return: String.
    :raises HTTPException: If there is a server error or the token is missing

    """
    try:
        if not JWT:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing"
            )
        response = get_JWT(JWT)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.post("/logout")
async def logout_user(request: LogOutRequest):
    """
    Invalidates current user session and logs user out.

    :param file: LogOutRequest
    :return: String.
    :raises HTTPException: If there is a server error or the token is missing

    """
    try:
        if not request.JWT:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing"
            )
        response = remove_JWT(request.JWT)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.get("/validate/logout", response_model=dict)
async def logout_validation(JWT: str = Query(...)):  # pylint: disable = invalid-name
    """
    Validates that the user logged out.

    :param file: JWT (str)
    :return: String.
    :raises HTTPException: If there is a server error or the token is missing

    """
    try:
        if not JWT:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing"
            )
        response = token_logout_valid(JWT)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=response)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
