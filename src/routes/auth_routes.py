"""
API route handler for user assoicated authentication routes.
"""

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from src.exceptions.auth_exceptions import InvalidCredentialsError, MissingTokenError
from src.services.auth_service import (
    authenticate_user,
    get_JWT,
    remove_JWT,
    token_logout_valid,
)
from src.domain.models.auth_models import LogOutRequest, SessionRequest

router = APIRouter(prefix="/v1/users/auth")


@router.post("/login", tags=["User Authentication"])
async def login_user(request: SessionRequest):
    """
    Authenticate the user and return a session token.

    :param file: Session Request.
    :return: String.
    :raises HTTPException: If there is a server error or invalid credentials

    """
    JWT = authenticate_user(request.dict())  # pylint: disable = invalid-name
    print(f"JWT generated: {JWT}")
    if not JWT:
        raise InvalidCredentialsError()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"JWT": JWT})

@router.get("/validate/login", response_model=dict, tags=["User Token Validation"])
async def login_validation(JWT: str = Query(...)):  # pylint: disable = C0103
    """
    Validates if the user is logged in.

    :param file: JWT (str)
    :return: String.
    :raises HTTPException: If there is a server error or the token is missing

    """
    if not JWT:
        raise MissingTokenError()
    response = get_JWT(JWT)
    return JSONResponse(status_code=200, content=response)


@router.post("/logout", tags=["User Authentication"])
async def logout_user(request: LogOutRequest):
    """
    Invalidates current user session and logs user out.

    :param file: LogOutRequest
    :return: String.
    :raises HTTPException: If there is a server error or the token is missing

    """
    if not request.JWT:
        raise MissingTokenError()
    response = remove_JWT(request.JWT)
    return JSONResponse(status_code=200, content=response)


@router.get("/validate/logout", response_model=dict,tags=["User Token Validation"])
async def logout_validation(JWT: str = Query(...)):  # pylint: disable = invalid-name
    """
    Validates that the user logged out.

    :param file: JWT (str)
    :return: String.
    :raises HTTPException: If there is a server error or the token is missing

    """
    if not JWT:
        raise MissingTokenError()
    response = token_logout_valid(JWT)
    return JSONResponse(status_code=200, content=response)
