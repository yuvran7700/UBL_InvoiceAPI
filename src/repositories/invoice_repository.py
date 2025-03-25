"""
Invoice repository module.
Encapsulates all interactions with DynamoDB for invoice operations using query operators.
"""

from typing import List
from boto3.dynamodb.conditions import Key
from src.models.invoice import Invoice
from src.utils.dynamodb_data_converter import convert_data_for_dynamodb
from src.db.dynamodb_client import invoices_table


def save_invoice(invoice: Invoice, user_id: str) -> None:
    """
    Saves the invoice to the DynamoDB table after converting its data.

    Args:
        invoice (InvoiceType): The invoice to be saved.

    Raises:
        Exception: If there is an error storing the invoice in DynamoDB.
    """
    invoice_dict = invoice.dict()
    invoice_dict = convert_data_for_dynamodb(invoice_dict)
    invoice_dict['user_id'] = user_id
    invoice_dict['invoice_id'] = invoice.header.invoice_id

    try:
        invoices_table.put_item(Item=invoice_dict)
    except Exception as e:
        raise Exception(f"Failed to store invoice in DynamoDB: {e}")


def get_invoice_by_id(invoice_id: str) -> Invoice:
    """
    Retrieves an invoice from DynamoDB by its unique identifier.

    Args:
        invoice_id (str): The unique invoice identifier.

    Returns:
        InvoiceType: The retrieved invoice if found, otherwise None.
    """
    response = invoices_table.query(
        IndexName="invoice_id-index",  # Ensure your GSI is set up
        KeyConditionExpression=Key("invoice_id").eq(invoice_id),
    )

    items = response.get("Items", [])
    if items:
        return InvoiceType.parse_obj(items[0])
    return None


def get_invoices_by_user(user_id: str) -> List[Invoice]:
    """
    Retrieves all invoices belonging to a specific user from DynamoDB.

    Args:
        user_id (str): The user ID.

    Returns:
        List[InvoiceType]: The retrieved invoices.
    """
    response = invoices_table.query(
        KeyConditionExpression=Key("user_id").eq(
            user_id
        )  # Query by partition key (user_id)
    )

    items = response.get("Items", [])
    return [InvoiceType.parse_obj(item) for item in items]


def update_invoice_fields(user_id: str, invoice_id: str, updates: dict) -> dict:
    """
    Updates the invoice in DynamoDB.
    """
    update_expr, expr_values, expr_names = get_update_params(updates)
    response = invoices_table.update_item(
        Key={"user_id": user_id, "invoice_id": invoice_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ExpressionAttributeNames=expr_names,
        ConditionExpression="attribute_exists(invoice_id)",
        ReturnValues="ALL_NEW"
    )
    return response.get("Attributes")
