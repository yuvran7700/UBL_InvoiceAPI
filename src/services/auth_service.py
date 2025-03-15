import uuid
from fastapi import HTTPException, status
from src.utils.auth_helpers import get_user_from_dynamo, hash_password, save_user_to_dynamodb, update_user_in_dynamo, verify_password
from src.validators.auth_validator import validate_abn, check_email_exists, validate_password
from src.models.auth_models import RegisterRequest, UpdatePasswordRequest
from src.db.dynamodb_client import user_table
from passlib.context import CryptContext

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        
    def update_password(self, request_data: UpdatePasswordRequest):
        """
        Update a user's password.
        
        Args:
            request_data (UpdatePasswordRequest): User data including current and new password
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If validation fails or database operations fail
        """
        try:
            # Get the user from DynamoDB
            user = get_user_from_dynamo(request_data.email)
            
            # Verify the current password is correct
            if not pwd_context.verify(request_data.password, user.get('hashed_password')):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current password is incorrect"
                )
            
            # Validate the new password
            validate_password(request_data.updated_password)
        
            # Hash the new password
            new_hashed_password = hash_password(request_data.updated_password)
            # Update the user's password in DynamoDB
            result = user_table.update_item(
                Key={'email': request_data.email},
                UpdateExpression="SET hashed_password = :new_password",
                ExpressionAttributeValues={
                    ':new_password': new_hashed_password
                },
                ReturnValues="UPDATED_NEW"
            )

            if 'Attributes' not in result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update the password"
                )

            return {
                "message": "Password updated successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating password: {str(e)}"
            )
