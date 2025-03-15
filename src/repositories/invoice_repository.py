# repository/invoice_repository.py
"""
Handles all DynamoDB interactions for storing invoices.
"""

from src.db.dynamodb_client import invoices_table
from src.utils.dynamodb_data_converter import convert_data_for_dynamodb
from src.models.invoice_type import InvoiceType


def save_invoice(invoice: InvoiceType) -> None:
    """
    Saves the invoice to the DynamoDB table after converting its data.

    :param invoice: The invoice to be saved.
    :raises Exception: If there is an error storing the invoice in DynamoDB.
    """
    invoice_dict = invoice.dict()
    invoice_dict = convert_data_for_dynamodb(invoice_dict)

    try:
        invoices_table.put_item(Item=invoice_dict)
    except Exception as e:
        raise Exception(f"Failed to store invoice in DynamoDB: {e}")
