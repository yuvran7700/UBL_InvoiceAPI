#marshallers/invoice_marshaller.py
"""
Invoice Marshaller.
Handles the transformation (marshalling) of an OrderType into an InvoiceType.
"""

from datetime import date
import random
import uuid
from src.models.order_type import OrderType
from src.models.invoice_type import InvoiceType, Party, InvoiceLine, ClassifiedTaxCategory

class InvoiceMarshaller:
    @staticmethod
    def marshall_order_to_invoice(order: OrderType) -> InvoiceType:
        """
        Marshalls an OrderType object into an InvoiceType object.
        
        Args:
            order (OrderType): The enriched order data.
            
        Returns:
            InvoiceType: The draft invoice generated from the order.
        """
        # Map seller and buyer details.
        seller = Party(
            name=order.seller_name,
            account=order.seller_account,
            address=order.seller_address,
            tax_identifier="GST12345678",  # Ideally retrieved from seller master data.
            electronic_address="supplier@example.com"
        )
        buyer = Party(
            name=order.buyer_name,
            account=order.buyer_account,
            address=order.buyer_address,
            tax_identifier="GST87654321",  # Ideally retrieved from buyer master data.
            electronic_address="buyer@example.com"
        )

        # Map order lines to invoice lines.
        invoice_lines = []
        line_total = 0.0
        for idx, order_line in enumerate(order.order_lines, start=1):
            product_code = order_line.buyers_item_id  # Use buyer's item ID as product code.
            
            classified_tax_category = None
            if order_line.line_extension_amount > 0 and order_line.total_tax_amount > 0:
                tax_rate = (order_line.total_tax_amount / order_line.line_extension_amount) * 100
                classified_tax_category = ClassifiedTaxCategory(
                    tax_category_code="S",  # "S" indicates standard rate (adjust as needed)
                    tax_rate=round(tax_rate, 2),
                    tax_scheme="GST"
                )
            
            invoice_line = InvoiceLine(
                id=idx,
                description=order_line.item_description or order_line.item_name,
                product_code=product_code,
                quantity=order_line.quantity,
                unit_price=order_line.unit_price,
                line_extension_amount=order_line.line_extension_amount,
                classified_tax_category=classified_tax_category
            )
            invoice_lines.append(invoice_line)
            line_total += order_line.line_extension_amount

        # Generate a unique invoice_id.
        invoice_id = str(uuid.uuid4())

        # Payment terms mapping.
        payment_means = order.payment_terms

        # Create and return the InvoiceType.
        return InvoiceType(
            invoice_id=invoice_id,
            issue_date=date.today(),
            invoice_type_code="380",  # Example: "380" for a commercial invoice.
            buyer_reference=order.sales_order_id,
            order_reference=order.order_id,
            due_date=None,  # Optionally compute or map due date.
            payment_means=payment_means,
            seller=seller,
            buyer=buyer,
            invoice_lines=invoice_lines,
            legal_monetary_total=line_total,
            status = "draft"
        )
