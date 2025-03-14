import uuid
from fastapi import HTTPException, status
from src.utils.auth_helpers import hash_password, save_user_to_dynamodb
from src.validators.auth_validator import validate_abn, check_email_exists, validate_password
from src.models.auth_models import RegisterRequest

class UserService: 
    def register_user(self, request_data: RegisterRequest):
        """
        Register a new user with validation and error handling.
        
        Args:
            request_data (dict): User registration data
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If validation fails or database operations fail
        """
        try:
            # Validate all required fields
            validate_abn(request_data.abn)
            check_email_exists(request_data.email)
            validate_password(request_data.password)

            # Create user record
            user_item = {
                'user_id': str(uuid.uuid4()),
                'email': request_data.email,
                'businessName': request_data.businessName,
                'abn': request_data.abn,
                'hashed_password': hash_password(request_data.password),
            }

            # Save to database
            save_user_to_dynamodb(user_item)

            return {
                "message": "User registered successfully",
                    "user": {
                        "email": user_item["email"],
                        "businessName": user_item["businessName"],
                        "abn": user_item["abn"]
                    }
            }

        except HTTPException:
            raise  # Re-raise HTTP exceptions as they are already properly formatted
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
