from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from src.models.user_models import UpdatePasswordRequest, UpdateUsernameRequest, UserIn, UserOut
from src.services.user_service import create_user, update_business_name, update_user_password

router = APIRouter(prefix="/v1/users", tags=["user"])



@router.post("/register", response_model=UserOut)
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

# @router.put("/update-password")
# async def update_password(request: UpdatePasswordRequest):
#     try:
#         print(f"Received request: {request.dict()}")  # Debugging
#         update_user_password(request)  # Call service layer
#         return {"message": "Password updated successfully"}
#     except HTTPException as e:
#         print(f"HTTP Exception: {e.detail}")
#         raise e
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {str(e)}"
#         )

@router.put("/update-password")
async def update_password(request: UpdatePasswordRequest):
    try:
        update_user_password(request)  # Call service layer
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    return {"message": "Password updated successfully"}

@router.put("/update-business_name")
async def update_username(request: UpdateUsernameRequest):
    try:
        update_business_name(request)  # Call service layer
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    return {"message": "Business name updated successfully"}


# @router.put("/update-email")
# def updateEmail(request: UpdateEmailRequest):
#     try:
#         service = user_service()  
#         result =  service.update_email(request)  # Call service layer
#         return JSONResponse(status_code=status.HTTP_200_OK, content=result)
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {str(e)}"
#         )

# @router.put("/update-username")
# def updateUsername(request: update_username_request):
#     try:
#         service = user_service()  
#         result =  service.update_username(request)  # Call service layer
#         return JSONResponse(status_code=status.HTTP_200_OK, content=result)
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {str(e)}"
#         )