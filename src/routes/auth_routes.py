from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from src.services.auth_service import register_user, authenticate_user, get_JWT

router = APIRouter(prefix="/v1/users/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    businessName: str
    email: EmailStr
    password: str
    abn: str

class SessionRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(request: RegisterRequest):
    try:
        result = register_user(request.dict())  # Call service layer
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/login")
async def login_user(request: SessionRequest):
    """Authenticate the user and return a session token."""
    try:
        JWT = authenticate_user(request.dict())
        if not JWT:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials"
            )

        return JSONResponse(
                status_code=status.HTTP_201_CREATED, 
                content={"JWT": JWT}
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/login/validate", response_model=dict)
async def login_validation(JWT: str = Query(...)):
    """Authenticate the user and return a session token."""
    try:
        if not JWT:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED, 
                detail = "Token missing"
            )
        response = get_JWT(JWT)
        return JSONResponse(status_code = status.HTTP_201_CREATED, content = response)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = f"An error occurred: {str(e)}"
        )   