import boto3
import os

# Load AWS region from environment variables (default to us-east-1)
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

# Reference the "invoices" table
invoice_table = dynamodb.Table("invoices")

# Reference the "sessions" table
session_table = dynamodb.Table("sessions")

# Reference the "sessions" table
user_table = dynamodb.Table("users")

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
        print("Invoices Table Status:", session_table.table_status)
    except Exception as e:
        print("Error connecting to DynamoDB:", str(e))