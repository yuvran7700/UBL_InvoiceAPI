# src/invoice_type_creation/invoice_marshaller.py
from nanoid import generate
from datetime import date
from src.models.order_type import OrderType
from src.models.invoice_type import InvoiceType

class InvoiceMarshaller:
    @staticmethod
    def marshall_order_to_invoice(order: OrderType) -> InvoiceType:
        # For example, assume the total invoice amount is the anticipated_payable_amount.
        total = order.anticipated_payable_amount
        
        # Generate a unique invoice ID.
        invoice_id = generate(size=10)

        
        # Create and return an InvoiceType that composes the order data.
        return InvoiceType(
            invoice_id=invoice_id,
            issue_date=date.today(),
            invoice_type_code="380",  # Example code for a commercial invoice.
            legal_monetary_total=total,
            payment_means=order.payment_terms,
            order=order,  # Composition: embed the entire order data.
            status="draft"
        )
