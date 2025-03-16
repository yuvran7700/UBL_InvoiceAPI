"""
Module for converting an OrderType into an InvoiceType.
Handles calculation of monetary totals and assigns invoice-specific fields.
"""

from nanoid import generate
from datetime import date
from src.models.order_type import OrderType
from src.models.invoice_type import InvoiceType
from src.utils.invoice_calculations import calculate_line_extension

class InvoiceMarshaller:
    """
    A marshaller class to transform an OrderType into an InvoiceType.
    """

    @staticmethod
    def marshall_order_to_invoice(order: OrderType) -> InvoiceType:
        """
        Converts an OrderType to an InvoiceType by calculating each invoice line's extension amount
        and summing these to get the total invoice amount.

        Args:
            order (OrderType): The order to convert.

        Returns:
            InvoiceType: The resulting invoice with computed totals and current date.
        """
        total_invoice_amount = InvoiceMarshaller._calculate_total_invoice_amount(order)
        invoice_id = generate(size=10)
        return InvoiceType(
            invoice_id=invoice_id,
            issue_date=date.today(),
            invoice_type_code="380",  # Example code for a commercial invoice.
            legal_monetary_total=total_invoice_amount,
            payment_means=order.payment_terms,
            order=order,  # Embed the complete order data.
            status="draft"
        )

    @staticmethod
    def _calculate_total_invoice_amount(order: OrderType) -> float:
        """
        Iterates through each invoice line, calculates its extension amount, updates the DTO,
        and accumulates the total invoice amount.

        Args:
            order (OrderType): The order containing invoice lines.

        Returns:
            float: The total calculated invoice amount.
        """
        total = 0.0
        for line in order.invoice_lines:
            # Use invoiced_quantity if available; otherwise, use quantity.
            quantity = getattr(line, "invoiced_quantity", line.quantity)
            # Use discount and charge if defined; default to 0.0.
            discount = getattr(line, "discount", 0.0)
            charge = getattr(line, "charge", 0.0)
            
            # Calculate and update the line's extension amount.
            line.line_extension_amount = calculate_line_extension(quantity, line.unit_price, discount, charge)
            total += line.line_extension_amount
        return total
