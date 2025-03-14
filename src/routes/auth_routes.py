from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from src.services.auth_service import UserService
from src.models.auth_models import RegisterRequest

router = APIRouter(prefix="/v1/users/auth", tags=["auth"])


@router.post("/register")
async def register(request: RegisterRequest):
    try:
        user_service = UserService()  
        result = await user_service.register_user(request)  # Call service layer
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/delete")
async def updatePassword(request: RegisterRequest):
    pass

