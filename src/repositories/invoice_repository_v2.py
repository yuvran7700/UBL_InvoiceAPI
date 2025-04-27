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


def save_invoice(invoice: InvoiceUpdateModel, org_id: str, user_id: str, status: InvoiceStatus) -> None:
    """
    Saves the invoice to the DynamoDB table after converting its data.

    Args:
        invoice (InvoiceUpdateModel): The invoice to be saved.
        org_id (str): The organization ID.
        user_id (str): The ID of the user creating the invoice.
        status (InvoiceStatus): The status of the invoice.

    Raises:
        DatabaseWriteError: If there is an error storing the invoice in DynamoDB.
    """
    invoice_dict = invoice.dict(exclude_none=True)

    # Add metadata
    invoice_dict["user_id"] = user_id
    invoice_dict["organisation_id"] = org_id
    invoice_dict["invoice_id"] = invoice.id
    invoice_dict["status"] = status.value

    invoice_dict = convert_data_for_dynamodb(invoice_dict)

    try:
        invoices_table.put_item(Item=invoice_dict)
    except Exception as e:
        raise DatabaseWriteError(f"Failed to store invoice in DynamoDB: {e}")


def get_invoice_by_id(invoice_id: str, organisation_id: str) -> tuple[InvoiceUpdateModel, str] | None:
    response = invoices_table.query(
        KeyConditionExpression=Key("organisation_id").eq(organisation_id) & Key("invoice_id").eq(invoice_id)
    )

    items = response.get("Items", [])
    if not items:
        return None

    item = items[0]
    status = item.get("status", "unknown")
    invoice = InvoiceUpdateModel.parse_obj(item)
    return invoice, status


def get_invoices_by_organisation(
    organisation_id: str,
    status: Optional[InvoiceStatus],
) -> List[tuple[InvoiceUpdateModel, str]]:
    """
    Retrieves all invoices for an organisation, optionally filtered by status.
    """
    if status:
        response = invoices_table.query(
            IndexName="status_filter_index",
            KeyConditionExpression=Key("organisation_id").eq(organisation_id) & Key("status").eq(status.value)
        )
    else:
        response = invoices_table.query(
            KeyConditionExpression=Key("organisation_id").eq(organisation_id)
        )

    items = response.get("Items", [])
    results = []

    for item in items:
        status_val = item.get("status", "unknown")
        invoice = InvoiceUpdateModel.parse_obj(item)
        results.append((invoice, status_val))

    return results


def delete_invoices_by_id(invoice_ids: List[str], organisation_id: str) -> None:
    """
    Batch deletes multiple invoices from DynamoDB for a given organisation.
    Assumes the provided invoice IDs are already validated to be in draft status.

    Args:
        invoice_ids (List[str]): List of invoice IDs to delete.
        organisation_id (str): The organisation ID.

    Raises:
        DatabaseWriteError: If batch delete fails.
    """
    try:
        with invoices_table.batch_writer() as batch:
            for invoice_id in invoice_ids:
                batch.delete_item(
                    Key={
                        "organisation_id": organisation_id,
                        "invoice_id": invoice_id
                    }
                )
    except Exception as e:
        raise DatabaseWriteError(f"Failed to batch delete invoices: {e}")


