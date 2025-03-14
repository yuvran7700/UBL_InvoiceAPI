from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from src.services.auth_service import UserService
from src.models.auth_models import RegisterRequest

router = APIRouter(prefix="/v1/users/auth", tags=["auth"])


@router.post("/register")
def register(request: RegisterRequest):
    try:
        user_service = UserService()  
        result =  user_service.register_user(request)  # Call service layer
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/delete")
def updatePassword(request: RegisterRequest):
    try:
        user_service = UserService()  
        result =  user_service.update_password(request)  # Call service layer
        return JSONResponse(status_code=status.HTTP_200_CREATED, content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )