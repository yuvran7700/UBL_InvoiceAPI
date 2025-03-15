from passlib.context import CryptContext

from fastapi import HTTPException, status
import pytest

from src.db.dynamodb_client import user_table

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash the user's password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def save_user_to_dynamodb(user_item: dict):
    """Save user data to DynamoDB"""
    try:
        user_table.put_item(Item=user_item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving user to DynamoDB: {str(e)}"
        )

@pytest.mark.unit
def get_user_from_dynamo(email: str):
    """Retrieve user from DynamoDB using the provided email."""
    try:
        # Retrieve the user by email from DynamoDB
        response = user_table.get_item(
            Key={'email': email}  # Assuming 'email' is the primary key of the table
        )
        # Check if the 'Item' key exists in the response, meaning the user was found
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        # Return the retrieved user item
        return response['Item']
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user from DynamoDB: {str(e)}"
        )


def update_user_in_dynamo(email: str, updated_data: dict):
    """Update a user in DynamoDB using the provided email and updated data."""
    try:
        # Update the user in DynamoDB
        response = user_table.update_item(
            Key={'email': email},
            UpdateExpression="SET businessName = :bn, abn = :abn",
            ExpressionAttributeValues={
                ':bn': updated_data['businessName'],
                ':abn': updated_data['abn']
            },
            ReturnValues="ALL_NEW"
        )
        # Return the updated user item
        return response['Attributes']
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user in DynamoDB: {str(e)}"
        )
    

def delete_all_user_items():
    """Deletes all items from the DynamoDB users table."""
    response = user_table.scan()  # Get all items from the table
    items = response.get("Items", [])

    while "LastEvaluatedKey" in response:  # Continue if there are more items
        response = user_table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    # Batch delete (DynamoDB limits batch writes to 25 items per request)
    with user_table.batch_writer() as batch:
        for item in items:
            print(f"Deleting user with email: {item['email']}")  # Debugging line
            batch.delete_item(Key={"email": item["email"]})