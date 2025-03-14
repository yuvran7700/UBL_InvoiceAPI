import boto3
import os

# Load AWS region from environment variables (default to us-east-1)
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

# Reference the "Users" table
user_table = dynamodb.Table("Users")

def check_dynamodb_connection():
    try:
        print("Checking DynamoDB connection...")
        print("Users Table Status:", user_table.table_status)
    except Exception as e:
        print("Error connecting to DynamoDB:", str(e))

# Call this function at startup to verify
check_dynamodb_connection()

# def user_table():
#     try:
#         print("Checking DynamoDB connection...")
#         print("Users Table Status:", user_table.table_status)
#         return dynamodb.Table("Users")
#     except Exception as e:
#         print("Error connecting to DynamoDB:", str(e))
#         return None