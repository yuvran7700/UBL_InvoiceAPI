"""
Invoice repository module.
Encapsulates all interactions with DynamoDB for invoice operations using query operators.
"""

from typing import List, Optional
from boto3.dynamodb.conditions import Key
from src.domain.models.invoice_update import InvoiceUpdateModel
from src.domain.models.invoice_response_models import InvoiceStatus
from src.exceptions.db_exceptions import DatabaseWriteError
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
        raise DatabaseWriteError(f"Failed to store invoice in DynamoDB: {e}")


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


def get_invoices_by_user(
    user_id: str,
    status: Optional[InvoiceStatus],
) -> List[tuple[InvoiceUpdateModel, str]]:
    """
    Retrieves invoices for a user, optionally filtered by status using GSI.

    Args:
        user_id (str): The user ID.
        status (InvoiceStatus | None): Optional status filter.

    Returns:
        List of (InvoiceUpdateModel, status) tuples.
    """
    if status:
        # Use status_filter_index: PK = user_id, SK = status
        response = invoices_table.query(
            IndexName="status_filter_index",
            KeyConditionExpression=Key("user_id").eq(user_id) & Key("status").eq(status.value)
        )
    else:
        # No status filter: fall back to base table
        response = invoices_table.query(
            KeyConditionExpression=Key("user_id").eq(user_id)
        )

    items = response.get("Items", [])
    results = []

    for item in items:
        status_val = item.get("status", "unknown")
        invoice = InvoiceUpdateModel.parse_obj(item)
        results.append((invoice, status_val))

    return results

def delete_invoices_by_id(invoice_ids: List[str], user_id: str) -> None:
    """
    Batch deletes multiple invoices from DynamoDB for a given user.
    Assumes the provided invoice IDs are already validated to be in draft status.
    Uses batch_writer() for efficient deletion.
    """
    try:
        with invoices_table.batch_writer() as batch:
            for invoice_id in invoice_ids:
                batch.delete_item(
                    Key={
                        "user_id": user_id,
                        "invoice_id": invoice_id
                    }
                )
    except Exception as e:
        raise DatabaseWriteError(f"Failed to batch delete invoices: {e}")
    