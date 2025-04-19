from boto3.dynamodb.conditions import Key
from src.db.dynamodb_client import user_table
from src.exceptions.base_exceptions import APIBaseException
from src.exceptions.db_exceptions import DatabaseReadError, DatabaseWriteError
from src.domain.models.user_models import UserInDB
from src.exceptions.user_exceptions import UserNotFoundError


def save_user(user_in_db: UserInDB) -> None:
    """
    Saves the user to the DynamoDB table after creation.

    Args:
        user (UserInDB): The invoice to be saved.

    Raises:
        Exception: If there is an error storing the user in DynamoDB.
    """
    try:
        user_in_db_dic = user_in_db.dict()
        user_table.put_item(Item=user_in_db_dic)
    except Exception as e:
        raise DatabaseWriteError(f"Failed to save user in save_user(): {str(e)}")


def get_user(email: str) -> UserInDB:
    """
    Retrieves a user from DynamoDB by their email address.

    Args:
        email (str): The email address of the user.

    Returns:
        UserInDB: The retrieved user if found.

    Raises:
        DatabaseReadError: If there is an error reading from the database.
    """
    try:

        response = user_table.query(
            IndexName="email-index",  # Ensure your GSI is set up
            KeyConditionExpression=Key("email").eq(email),
            ConsistentRead=False,
        )

        items = response.get("Items", [])

        if items:
            return UserInDB(**items[0])
        return None
    except Exception as e:
        raise DatabaseReadError(f"Failed to get user by email in get_user(): {str(e)}")


def update_user_password_in_db(user_id: str, new_hashed_password: str):
    """ """
    try:
        user_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set #hashed_password = :n",
            ExpressionAttributeNames={
                "#hashed_password": "hashed_password",
            },
            ExpressionAttributeValues={
                ":n": new_hashed_password,
            },
            ReturnValues="UPDATED_NEW",
        )
    except Exception as e:
        raise DatabaseWriteError(f"Failed to update password in update_user_password_in_db(): {str(e)}")



def update_username_in_db(user_id: str, new_username: str):
    """ """
    try:
        user_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set #business_name = :n",
            ExpressionAttributeNames={
                "#business_name": "business_name",
            },
            ExpressionAttributeValues={
                ":n": new_username,
            },
            ReturnValues="UPDATED_NEW",
        )
    except Exception as e:
        raise DatabaseWriteError(f"Failed to update business name in update_username_in_db(): {str(e)}")



def update_email_in_db(user_id: str, new_email: str):
    """ """
    try:
        user_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="set #email = :n",
            ExpressionAttributeNames={
                "#email": "email",
            },
            ExpressionAttributeValues={
                ":n": new_email,
            },
            ReturnValues="UPDATED_NEW",
        )

    except Exception as e:
        raise DatabaseWriteError(f"Failed to update email in update_email_in_db(): {str(e)}")



def delete_all_users():
    """Deletes all items from the DynamoDB users table."""
    try:
        response = user_table.scan()  # Get all items from the table
        items = response.get("Items", [])

        while "LastEvaluatedKey" in response:  # Continue if there are more items
            response = user_table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        # Batch delete (DynamoDB limits batch writes to 25 items per request)
        with user_table.batch_writer() as batch:
            for item in items:
                print(f"Deleting user with email: {item['email']}")  # Debugging line
                batch.delete_item(Key={"user_id": item["user_id"]})
    except Exception as e:
        raise DatabaseWriteError(f"Failed to delete all users in delete_all_users(): {str(e)}")

def get_user_item(email: str):
    try:
        user = get_user(email)
        if not user:
            raise UserNotFoundError(email=email)
        user_id = user.user_id
        response = user_table.get_item(Key={"user_id": user_id})
        return response["Item"]
    except APIBaseException:
        raise 
    except Exception as e:
        raise DatabaseReadError(f"Failed to get user item in get_user_item(): {str(e)}")
