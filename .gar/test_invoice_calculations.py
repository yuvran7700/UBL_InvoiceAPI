import pytest
from src.models.order_type import OrderType, OrderLineType
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.models.common.party_attributes import PartyAttributes

def test_line_extension_calculation():
    """
    Test that the InvoiceMarshaller correctly calculates and populates the line extension amount
    for each invoice line. The calculation uses the formula:
    
        line_extension_amount = (quantity * unit_price) - discount + charge
        
    For example, with quantity=10, unit_price=20, discount=5, and charge=2, the expected result is 197.
    """
    # Create a dummy invoice line with known values.
    line = OrderLineType(
        note="Test line",
        line_id="1",
        quantity=10.0,
        line_extension_amount=0.0,  # This will be updated.
        total_tax_amount=0.0,
        unit_price=20.0,
        item_description="Test Item",
        item_name="Test Item",
        buyers_item_id="BID1",
        sellers_item_id="SID1",
        discount=5.0,
        charge=2.0,
    )
    
    # Create dummy buyer and seller PartyAttributes.
    dummy_buyer = PartyAttributes(
        customer_assigned_account_id="dummy1",
        supplier_assigned_account_id="dummy1",
        party_name="Dummy Buyer",
        address="dummy address",
        endpoint_id=None,
        contact=None,
        tax_scheme=None,
    )
    dummy_seller = PartyAttributes(
        customer_assigned_account_id="dummy2",
        supplier_assigned_account_id="dummy2",
        party_name="Dummy Seller",
        address="dummy address",
        endpoint_id=None,
        contact=None,
        tax_scheme=None,
    )
    
    # Create an OrderType instance with the updated field names.
    order = OrderType(
        order_reference="ORDER1",
        buyer_reference="SALES1",
        note="Test order",
        AccountingCustomerParty=dummy_buyer.dict(),
        AccountingSupplierParty=dummy_seller.dict(),
        payment_terms="Net 30",
        invoice_lines=[line],
    )
    
    # Generate an invoice from the order.
    invoice = InvoiceMarshaller.marshall_order_to_invoice(order)
    
    # Expected calculation: (10 * 20) - 5 + 2 = 197.
    calculated_amount = invoice.order.invoice_lines[0].line_extension_amount
    assert calculated_amount == 197.0, f"Expected 197.0, got {calculated_amount}"
    
    # Verify that the invoice's legal monetary total equals the sum of the calculated invoice line amounts.
    total_from_lines = sum(l.line_extension_amount for l in invoice.order.invoice_lines)
    assert invoice.legal_monetary_total == total_from_lines, "Invoice total does not match sum of invoice line amounts"
