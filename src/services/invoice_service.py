"""
Invoice service.
Maps extracted OrderType data to a draft InvoiceType and stores the invoice in DynamoDB.
"""

from datetime import date
import random
from decimal import Decimal
import uuid
from models.order_type import OrderType
from models.invoice_type import InvoiceType, Party, InvoiceLine, ClassifiedTaxCategory
from db.dynamodb_client import invoices_table  # Import the pre-configured DynamoDB table

def generate_and_store_invoice(order: OrderType) -> InvoiceType:
    """
    Generate a draft invoice from the provided order data and store it in DynamoDB.

    Args:
        order (OrderType): The enriched order data extracted from the XML order document.

    Returns:
        InvoiceType: The generated draft invoice.
    """
    # Map seller and buyer using details from the order.
    seller = Party(
        name=order.seller_name,
        account=order.seller_account,
        address=order.seller_address,
        tax_identifier="GST12345678",  # Example value; ideally, use seller master data.
        electronic_address="supplier@example.com"
    )
    buyer = Party(
        name=order.buyer_name,
        account=order.buyer_account,
        address=order.buyer_address,
        tax_identifier="GST87654321",  # Example value; ideally, use buyer master data.
        electronic_address="buyer@example.com"
    )
    
    # Map order lines to invoice lines.
    invoice_lines = []
    line_total = 0.0
    for idx, order_line in enumerate(order.order_lines, start=1):
        # Use buyer's item ID as the product code.
        product_code = order_line.buyers_item_id
        
        # Compute tax rate and create a ClassifiedTaxCategory if tax info is available.
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

    # Generate a unique invoice_id using uuid.
    invoice_id = str(uuid.uuid4())

    # Payment terms mapping (if available from order.payment_terms).
    payment_means = order.payment_terms

    # Create the invoice with mapped header and line item fields.
    invoice = InvoiceType(
        invoice_id=invoice_id,
        issue_date=date.today(),
        invoice_type_code="380",  # Example code: "380" for a commercial invoice.
        buyer_reference=order.sales_order_id,  # Using SalesOrderID as buyer reference.
        order_reference=order.order_id,
        due_date=None,  # Optionally, compute or map the due date.
        payment_means=payment_means,
        seller=seller,
        buyer=buyer,
        invoice_lines=invoice_lines,
        legal_monetary_total=line_total
    )
    
    # Store the generated invoice in DynamoDB.
    store_invoice_in_dynamodb(invoice)
    
    return invoice

def convert_floats_to_decimal(obj):
    """
    Recursively convert float values in a structure (dict or list)
    to Decimal objects.
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    else:
        return obj

def store_invoice_in_dynamodb(invoice: InvoiceType) -> None:
    """
    Stores the generated draft invoice in the DynamoDB table.
    Converts date fields to ISO strings and floats to Decimals because
    DynamoDB does not support native date or float types.

    Args:
        invoice (InvoiceType): The generated draft invoice.

    Raises:
        Exception: If storing the invoice in DynamoDB fails.
    """
    invoice_dict = invoice.dict()

    # Convert date fields to ISO format strings.
    if invoice_dict.get("issue_date") and isinstance(invoice_dict["issue_date"], date):
        invoice_dict["issue_date"] = invoice_dict["issue_date"].isoformat()
    if invoice_dict.get("due_date") and isinstance(invoice_dict["due_date"], date):
        invoice_dict["due_date"] = invoice_dict["due_date"].isoformat()

    # Recursively convert float values to Decimal.
    invoice_dict = convert_floats_to_decimal(invoice_dict)

    try:
        invoices_table.put_item(Item=invoice_dict)
    except Exception as e:
        raise Exception(f"Failed to store invoice in DynamoDB: {e}")