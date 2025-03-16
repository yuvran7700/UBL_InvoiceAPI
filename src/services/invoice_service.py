"""
Invoice service module.
Handles the creation and persistence of invoices from orders.
"""

from src.models.invoice_type import InvoiceType
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.models.order_type import OrderType
from src.repositories.invoice_repository import save_invoice


def create_invoice(order: OrderType) -> InvoiceType:
    """
    Creates an invoice from an order and persists it using the repository.

    Args:
        order (OrderType): The order to convert into an invoice.

    Returns:
        InvoiceType: The created invoice.
    """
    invoice = InvoiceMarshaller.marshall_order_to_invoice(order)
    save_invoice(invoice)
    return invoice
