from fastapi import HTTPException, status
from src.db.dynamodb_client import user_table

class UserTable():
    def save(user_item: dict):
        """Save user data to DynamoDB"""
        try:
            user_table.put_item(Item=user_item)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving user to DynamoDB: {str(e)}"
            )

    def get(email: str):
        """Retrieve user from DynamoDB using the provided email."""
        try:
            # Retrieve the user by email from DynamoDB
            response = user_table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            items = response.get('Items', [])
            
            if not items:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            # Return the first matching user
            return items[0]
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving user from DynamoDB: {str(e)}"
            )

    # Update user data in DynamoDB? 
    #TO DO LATER!!!
    # def update(email: str, updated_data: dict):
    #     """Update a user in DynamoDB using the provided email and updated data."""
    #     try:
    #         # Update the user in DynamoDB
    #         response = user_table.update_item(
    #             Key={'email': email},
    #             UpdateExpression="SET businessName = :bn, abn = :abn",
    #             ExpressionAttributeValues={
    #                 ':bn': updated_data['businessName'],
    #                 ':abn': updated_data['abn']
    #             },
    #             ReturnValues="ALL_NEW"
    #         )
    #         # Return the updated user item
    #         return response['Attributes']
        
    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=f"Error updating user in DynamoDB: {str(e)}"
    #         )
        

    def delete_all():
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
                batch.delete_item(Key={"user_id": item["user_id"], "email": item["email"]})
        