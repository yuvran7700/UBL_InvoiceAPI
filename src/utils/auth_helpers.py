from passlib.context import CryptContext

from fastapi import HTTPException, status

from src.db.dynamodb_client import user_table
#hash-password helper function 


# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash the user's password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(password: str) -> str:
    """Verify the user's password has been hashed"""
    hash = hash_password(password)
    return pwd_context.verify(password,hash)

def save_user_to_dynamodb(user_item: dict):
    """Save user data to DynamoDB"""
    try:
        user_table.put_item(Item=user_item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving user to DynamoDB: {str(e)}"
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

def cleanup_database():
    """
    yield  # This yield statement is used to pause the function execution and allow the test to run before cleaning up the database.

    This function is intended to be used as a fixture in testing frameworks like pytest.
    It uses a generator pattern with `yield` to perform setup before the test and cleanup after the test.
    The `yield` statement allows the test to run, and after the test completes, the code after `yield` is executed to clean up the database.
    """
    yield
    # Delete all test users after each test
    scan = user_table.scan()
    with user_table.batch_writer() as batch:
        for item in scan['Items']:
            batch.delete_item(Key={'email': item['email']})
