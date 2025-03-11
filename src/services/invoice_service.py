"""
Invoice service.
Handles the persistence (CRUD) operations for invoices.
"""

from src.db.dynamodb_client import invoices_table
from src.models.invoice_type import InvoiceType
from src.utils.dynamodb_data_converter import convert_data_for_dynamodb
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.models.order_type import OrderType  # Ensure proper import based on PYTHONPATH

def create_invoice_helper(invoice: InvoiceType) -> None:
    """
    Stores the invoice in the DynamoDB table.
    Converts date fields and float values to DynamoDB-compatible types.
    
    Args:
        invoice (InvoiceType): The invoice to store.
    
    Raises:
        Exception: If storing the invoice fails.
    """
    invoice_dict = invoice.dict()
    invoice_dict = convert_data_for_dynamodb(invoice_dict)
    
    try:
        invoices_table.put_item(Item=invoice_dict)
    except Exception as e:
        raise Exception(f"Failed to store invoice in DynamoDB: {e}")

def create_invoice(order: OrderType) -> InvoiceType:
    """
    Creates an invoice from an order and stores it.
    
    Args:
        order (OrderType): The enriched order data.
    
    Returns:
        InvoiceType: The created invoice.
    """
    invoice = InvoiceMarshaller.marshall_order_to_invoice(order)
    create_invoice_helper(invoice)
    return invoice

