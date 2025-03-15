# services/invoice_service.py
"""
Invoice service.
Handles the persistence (CRUD) operations for invoices.
"""

from src.models.invoice_type import InvoiceType
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.models.order_type import OrderType
from src.repositories.invoice_repository import (
    save_invoice,
)  # Import repository function


def create_invoice(order: OrderType) -> InvoiceType:
    """
    Creates an invoice from an order and persists it using the repository.
    """
    invoice = InvoiceMarshaller.marshall_order_to_invoice(order)
    save_invoice(invoice)  # Use repository to persist the invoice
    return invoice
