from passlib.context import CryptContext
from fastapi import HTTPException, status
from src.db.dynamodb_client import user_table, session_table
from boto3.dynamodb.conditions import Key
import boto3
#hash-password helper function 

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash the user's password using bcrypt"""
    return pwd_context.hash(password)

def save_user_to_dynamodb(user_item: dict):
    """Save user data to DynamoDB"""
    try:
        user_table.put_item(Item=user_item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving user to DynamoDB: {str(e)}"
        )

def save_session_to_dynamodb(session_item: dict):
    """Save session data to DynamoDB"""
    try:
        session_table.put_item(Item=session_item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving session to DynamoDB: {str(e)}"
        )    
    
def get_item_using_email(email: str):
    try:
        response = user_table.query(
            IndexName="email-index",  # Name of the GSI
            KeyConditionExpression=Key("email").eq(email)
        )
        items = response.get("Items", [])
        return {"Items": items[0] if items else {}}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {}
