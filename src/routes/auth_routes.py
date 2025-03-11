from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from src.services.auth_service import register_user

router = APIRouter(prefix="/v1/users/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    businessName: str
    email: EmailStr
    password: str
    abn: str

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
