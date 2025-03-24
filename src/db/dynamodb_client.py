"""
DynamoDB client initialization and connection testing.
"""

import os
import boto3


# Load AWS region from environment variables (default to us-east-1)
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

# Reference tables
invoices_table = dynamodb.Table("invoices")
users_table = dynamodb.Table("users")
sessions_table = dynamodb.Table("sessions")


def check_table_status(table, table_name):
    """
    Generic function to check and print table status.
    """
    try:
        print(f"Checking DynamoDB connection for '{table_name}'...")
        print(f"{table_name} Table Status: {table.table_status}")
    except Exception as e:
        print(f"Error connecting to {table_name} table:", str(e))


def initialize_dynamodb():
    """
    Initializes and tests the connection to all required DynamoDB tables.
    """
    check_table_status(invoices_table, "invoices")
    check_table_status(users_table, "users")
    check_table_status(sessions_table, "sessions")


# Call on startup
if __name__ == "__main__":
    initialize_dynamodb()