import uuid
import logging
from passlib.context import CryptContext
from src.models.user_models import (
    UpdateEmailRequest, 
    UpdatePasswordRequest, 
    UpdateUsernameRequest, 
    UserIn, 
    UserInDB)
from src.repositories.user_repository import (
    get_user, 
    save_user, 
    update_email_in_db, 
    update_user_password_in_db, 
    update_username_in_db
    )
from src.utils.user_helpers import  hash_password
from src.validators.user_validator import (
    check_user_exists, 
    validate_abn, 
    check_email_exists, 
    validate_password)

logger = logging.getLogger(__name__)

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(user_in: UserIn) -> UserInDB:
    """
    Register a new user with validation and error handling.
    
    Args:
        request_data (model): User In
        
    Returns:
        dict: User In DB
    """
    # Validate all required fields
    validate_abn(user_in.abn)
    print(user_in.abn)
    check_email_exists(user_in.email)
    validate_password(user_in.password)

    hashed_password = hash_password(user_in.password)

    user_id = str(uuid.uuid4())

    user_in_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password, user_id=user_id)
    save_user(user_in_db)
    return(user_in_db)

def update_user_password(request: UpdatePasswordRequest):
    """
    Update a user's password.
    """
    check_user_exists(request.email)
    new_password = request.new_password
    validate_password(new_password)
    
    new_hashed_password = hash_password(new_password)

    user = get_user(request.email)
    user_id = user.user_id

    update_user_password_in_db(user_id, new_hashed_password)

def update_user_business_name(request: UpdateUsernameRequest):
    """
    Update a username.
    """
    check_user_exists(request.email)
    new_business_name = request.new_business_name

    user = get_user(request.email)
    user_id = user.user_id

    update_username_in_db(user_id, new_business_name)

def update_user_email(request: UpdateEmailRequest):
    """
    Update a username.
    """
    check_user_exists(request.email)
    check_email_exists(request.new_email)
    new_email = request.new_email

    user = get_user(request.email)
    user_id = user.user_id

    update_email_in_db(user_id, new_email)
