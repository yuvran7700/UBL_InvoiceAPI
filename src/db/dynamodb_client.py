#src/db/dynamodb_client.py
"""
DynamoDB client initialization and connection testing.
"""

import os
import boto3

from src.services.health_service import HealthService


# Load AWS region from environment variables (default to us-east-1)
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

# Reference tables
invoices_table = dynamodb.Table("invoices")
user_table = dynamodb.Table("users")
session_table = dynamodb.Table("sessions")


def check_table_status(table, table_name: str, readiness: HealthService):
    try:
        _ = table.table_status
        print(f"{table_name} is reachable.")
        readiness.set_ready(f"dynamo.{table_name}", True)
    except Exception as e:
        print(f"{table_name} check failed: {e}")


def initialise_dynamodb(readiness: HealthService):
    """
    Initializes and tests the connection to all required DynamoDB tables.
    """
    check_table_status(invoices_table, "invoices", readiness)
    check_table_status(user_table, "users", readiness)
    check_table_status(session_table, "sessions", readiness)
