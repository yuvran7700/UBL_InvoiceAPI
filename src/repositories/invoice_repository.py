"""
Invoice repository module.
Encapsulates all interactions with DynamoDB for invoice operations using query operators.
"""

from typing import List
from boto3.dynamodb.conditions import Key
from src.models.invoice_update import InvoiceUpdateModel
from src.models.invoice_response_models import InvoiceStatus
from src.utils.dynamodb_data_converter import convert_data_for_dynamodb
from src.db.dynamodb_client import invoices_table


def save_invoice(invoice: InvoiceUpdateModel, user_id: str, status: InvoiceStatus) -> None:
    """
    Saves the invoice to the DynamoDB table after converting its data.

    Args:
        invoice (InvoiceUpdateModel): The invoice to be saved.

    Raises:
        Exception: If there is an error storing the invoice in DynamoDB.
    """
    invoice_dict = invoice.dict(exclude_none=True)
    invoice_dict["user_id"] = user_id
    invoice_dict["invoice_id"] = invoice.id
    invoice_dict["status"] = status.value
    invoice_dict = convert_data_for_dynamodb(invoice_dict)


    try:
        invoices_table.put_item(Item=invoice_dict)
    except Exception as e:
        raise Exception(f"Failed to store invoice in DynamoDB: {e}")


def get_invoice_by_id(invoice_id: str, user_id: str) -> tuple[InvoiceUpdateModel, str] | None:
    """
    Retrieves an invoice from DynamoDB by its unique identifier.

    Args:
        invoice_id (str): The unique invoice identifier.

    Returns:
        InvoiceType: The retrieved invoice if found, otherwise None.
    """
    response = invoices_table.query(
        IndexName="invoice_lookup_index",  # Ensure your GSI is set up
        KeyConditionExpression=Key("invoice_id").eq(invoice_id) & Key("user_id").eq(user_id)
    )

    items = response.get("Items", [])
    if not items:
        return None

    item = items[0]
    status = item.get("status", "unknown")  # fallback if somehow missing
    invoice = InvoiceUpdateModel.parse_obj(item)
    return invoice, status


def get_invoices_by_user(user_id: str) -> List[InvoiceUpdateModel]:
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
        ReturnValues="ALL_NEW",
    )
    return response.get("Attributes")
