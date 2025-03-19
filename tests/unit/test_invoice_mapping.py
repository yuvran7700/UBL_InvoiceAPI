import pytest
from datetime import date
from src.order_type_creation.invoice_director import OrderDirector
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.models.invoice_type import InvoiceType

def test_invoice_mapper(sample_order_xml, capfd):
    """
    Test that an InvoiceType is correctly populated from a sample order XML.
    This test prints out all key fields of the invoice and asserts that each critical field
    is populated as expected.
    """
    # Construct the order from the sample XML.
    order = OrderDirector.construct_order_from_xml(sample_order_xml)
    
    # Create an invoice from the order.
    invoice = InvoiceMarshaller.marshall_order_to_invoice(order)
    
    # Print invoice-level fields.
    print("Invoice Fields:")
    print("  Invoice ID:", invoice.invoice_id)
    print("  Issue Date:", invoice.issue_date)
    print("  Invoice Type Code:", invoice.invoice_type_code)
    print("  Legal Monetary Total:", invoice.legal_monetary_total)
    print("  Payment Means:", invoice.payment_means)
    print("  Status:", invoice.status)
    
    # Print nested Order fields.
    print("\nOrder Fields:")
    print("  Order Reference:", invoice.order.order_reference)
    print("  Buyer Reference:", invoice.order.buyer_reference)
    print("  Note:", invoice.order.note)
    
    print("\nBuyer Details:")
    buyer = invoice.order.AccountingCustomerParty
    print("  Party Name:", buyer.party_name)
    print("  Address:", buyer.address)
    print("  Customer Account ID:", buyer.customer_assigned_account_id)
    
    print("\nSeller Details:")
    seller = invoice.order.AccountingSupplierParty
    print("  Party Name:", seller.party_name)
    print("  Address:", seller.address)
    print("  Supplier Account ID:", seller.supplier_assigned_account_id)
    
    # Print details for each invoice line.
    print("\nInvoice Lines:")
    for idx, line in enumerate(invoice.order.invoice_lines):
        print(f"  Invoice Line {idx+1}:")
        print("    Line ID:", line.line_id)
        print("    Quantity:", line.quantity)
        print("    Unit Price:", line.unit_price)
        print("    Discount:", line.discount)
        print("    Charge:", line.charge)
        print("    Calculated Line Extension Amount:", line.line_extension_amount)
        print("    Total Tax Amount:", line.total_tax_amount)
        print("    Item Description:", line.item_description)
        print("    Item Name:", line.item_name)
        print("    Buyer Item ID:", line.buyers_item_id)
        print("    Seller Item ID:", line.sellers_item_id)
    
    # Assert that the invoice fields are correctly populated.
    assert invoice.invoice_id != "", "Invoice ID is missing."
    assert invoice.issue_date == date.today(), "Issue date is not today."
    assert invoice.invoice_type_code == "380", "Unexpected invoice type code."
    assert invoice.legal_monetary_total > 0, "Legal monetary total must be positive."
    assert invoice.payment_means is not None, "Payment means should be provided."
    assert invoice.status == "draft", "Invoice status should be draft."
    
    # Check that order fields are populated.
    assert invoice.order.order_reference != "", "Order reference is missing."
    assert invoice.order.buyer_reference != "", "Buyer reference is missing."
    
    # Check that at least one invoice line is present.
    assert len(invoice.order.invoice_lines) > 0, "No invoice lines present."
    
    # Optionally, capture and print the output from capfd.
    captured_output = capfd.readouterr().out
    print("Captured Output:\n", captured_output)
    
    # Return the invoice for further interactive inspection if needed.
    return invoice
