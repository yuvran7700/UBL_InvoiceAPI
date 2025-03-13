import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional

class DynamoDBService:
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.table.put_item(Item=user_data)
            return user_data
        except ClientError as e:
            raise Exception(f"Error creating user: {str(e)}")

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.get_item(Key={'id': user_id})
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Error getting user: {str(e)}")

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
            expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
            expression_attribute_values = {f":{k}": v for k, v in update_data.items()}

            response = self.table.update_item(
                Key={'id': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
            return response['Attributes']
        except ClientError as e:
            raise Exception(f"Error updating user: {str(e)}")

    def delete_user(self, user_id: str) -> bool:
        try:
            self.table.delete_item(Key={'id': user_id})
            return True
        except ClientError as e:
            raise Exception(f"Error deleting user: {str(e)}") 