from fastapi import HTTPException, status
from src.db.dynamodb_client import user_table

class user():
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

    @staticmethod
    def update_user(user_id: str, update_data: dict) -> dict:
        """
        General update function for user data
        
        Args:
            user_id: User's unique identifier (primary key)
            update_data: Dictionary containing fields to update
            
        Returns:
            dict: Updated attributes
            
        Raises:
            HTTPException: If update fails
        """
        try:
            # First, get the complete user data using user_id
            response = user_table.scan(
                FilterExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            items = response.get('Items', [])
            
            if not items:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get the current user data
            current_user_data = items[0]
            current_email = current_user_data['email']
            
            # Special handling for email updates (since email is part of the composite key)
            if 'email' in update_data and update_data['email'] != current_email:
                # Create a new user record with updated data
                new_user_data = current_user_data.copy()
                
                # Update all fields from update_data
                for key, value in update_data.items():
                    new_user_data[key] = value
                
                # Create a new item with the updated email
                user_table.put_item(Item=new_user_data)
                
                # Delete the old item with the old email
                user_table.delete_item(
                    Key={'user_id': user_id, 'email': current_email}
                )
                
                return {
                    'message': 'User updated successfully',
                    'updated_fields': list(update_data.keys())
                }
            else:
                # For updates that don't change the email, use update_item
                # Remove email from update_data if it's the same as current
                if 'email' in update_data and update_data['email'] == current_email:
                    del update_data['email']
                    
                if not update_data:  # If nothing to update after removing email
                    return {
                        'message': 'No changes to update'
                    }
                    
                # Construct the update expression
                update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in update_data.keys())
                expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
                expression_attribute_values = {f":{k}": v for k, v in update_data.items()}

                # Perform the update in DynamoDB
                result = user_table.update_item(
                    Key={'user_id': user_id, 'email': current_email},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                    ReturnValues="UPDATED_NEW"
                )
                
                # Check if the update was successful
                if 'Attributes' not in result:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update user"
                    )
                    
                return {
                    'message': 'User updated successfully',
                    'updated_fields': list(update_data.keys()),
                    'attributes': result['Attributes']
                }
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating user: {str(e)}"
            )

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
        