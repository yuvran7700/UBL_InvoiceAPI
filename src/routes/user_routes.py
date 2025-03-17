from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from src.models.user_models import UserIn, UserOut
from src.services.user_service import create_user
from src.models.user_models import RegisterRequest, UpdatePasswordRequest, UpdateEmailRequest, update_username_request

router = APIRouter(prefix="/v1/users/", tags=["user"])


@app.post("/register", response_model=UserOut)
async def register(user_in: UserIn):
    try:
        user =  create_user(user_in)  # Call service layer
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    return user

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

@router.put("/update-username")
def updateUsername(request: update_username_request):
    try:
        service = user_service()  
        result =  service.update_username(request)  # Call service layer
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )