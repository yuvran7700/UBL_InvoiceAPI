import uuid
from passlib.context import CryptContext
from fastapi import HTTPException
from utils.auth_helpers import hash_password, save_user_to_dynamodb
from src.validators.auth_validator import validate_abn, check_email_exists 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def register_user(request_data: dict):
    try:
        validate_abn(request_data['abn'])
        check_email_exists(request_data['email'])

        hashed_password = hash_password(request_data['password'])

        user_id = str(uuid.uuid4())

        user_item = {
            'user_id': user_id,
            'email': request_data['email'],
            'businessName': request_data['businessName'],
            'abn': request_data['abn'],
            'hashed_password': hashed_password,
        }

        save_user_to_dynamodb(user_item)

        return {"message": "User registered successfully"}

    except HTTPException as e:
            raise e  # Let FastAPI handle the HTTPException properly
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
