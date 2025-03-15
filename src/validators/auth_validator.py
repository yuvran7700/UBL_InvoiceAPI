import abn
#import boto3
from fastapi import HTTPException, status
from src.db.dynamodb_client import user_table
from datetime import datetime, timezone

#This file handles all the validation required for account creation

#Validates the given ABN
def validate_abn(abn_value: str):
    if not abn.validate(abn_value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ABN format"
        )

def check_email_exists(email: str):
    response = user_table.get_item(Key={'email': email})
    if 'Item' in response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

def session_validation(response: dict):
    if not response:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    expiration_time = response['expires_at']
    if expiration_time and (datetime.fromisoformat(expiration_time) 
                            < datetime.now(timezone.utc)):
        raise HTTPException(status_code=401, detail="Token expired")
    
