import boto3
import os

# Load AWS region from environment variables (default to us-east-1)
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)


# Reference the "Users" table
user_table = dynamodb.Table("users")


def check_dynamodb_connection():
    try:
        print("Checking DynamoDB connection...")
        print("Users Table Status:", user_table.table_status)
    except Exception as e:
        print("Error connecting to DynamoDB:", str(e))


# Call this function at startup to verify
check_dynamodb_connection()

# Reference the "invoices" table
invoice_table = dynamodb.Table("invoices")

# Reference the "users" table
user_table = dynamodb.Table("users")

# Reference the "sessions" table
session_table = dynamodb.Table("sessions")


def initialize_invoice_dynamodb():
    """
    Initializes and tests the connection to DynamoDB.
    """
    try:
        print("Checking DynamoDB connection...")
        print("Invoices Table Status:", invoice_table.table_status)
    except Exception as e:
        print("Error connecting to DynamoDB:", str(e))


def initialize_session_dynamodb():
    """
    Initializes and tests the connection to DynamoDB.
    """
    try:
        print("Checking DynamoDB connection...")
        print("Invoices Table Status:", user_table.table_status)
    except Exception as e:
        print("Error connecting to DynamoDB:", str(e))
