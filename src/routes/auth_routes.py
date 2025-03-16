from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from src.services.auth_service import user_service
from src.models.auth_models import RegisterRequest, UpdatePasswordRequest, UpdateEmailRequest

router = APIRouter(prefix="/v1/users/auth", tags=["auth"])


@router.post("/register")
def register(request: RegisterRequest):
    try:
        service = user_service()  
        result =  service.register_user(request)  # Call service layer
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.put("/update-password")
def updatePassword(request: UpdatePasswordRequest):
    try:
        service = user_service()  
        result =  service.update_password(request)  # Call service layer
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred when updating the password: {str(e)}"
        )
   

    
@router.put("/update-email")
def updateEmail(request: UpdateEmailRequest):
    try:
        service = user_service()  
        result =  service.update_email(request)  # Call service layer
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )