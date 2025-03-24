"""
This module contains unit tests for verifying business rules and the process
of building draft invoices using the InvoiceDirector and related components.
"""


from fastapi import HTTPException
import pytest
from src.marshallers.order_unmarshaller_factory import OrderUnmarshaller
from src.marshallers.order_xml_unmarshaller_factory import OrderXmlUnmarshaller
from src.marshallers.order_json_unmarshaller_factory import OrderJsonUnmarshaller
from src.draft_invoice_creation.invoice_director import InvoiceDirector
from src.utils.missing_field_checker import find_missing_fields



def test_invoice_director_construct_invoice_xml(sample_order_xml):
    """
    Test that InvoiceDirector builds the Invoice object correctly from XML.
    """
    unmarshaller = OrderXmlUnmarshaller()
    director = InvoiceDirector(unmarshaller)

    invoice = director.construct_invoice_from_data(sample_order_xml)

    # Print the built Invoice
    print("\n--- Constructed Invoice from XML ---")
    #print(invoice.model_dump_json(indent=4))

    # Basic assertions
    assert invoice.header.buyer_reference == "CON0095678"
    assert invoice.supplier_party.party_name == "Consortial"
    assert invoice.customer_party.party_name == "IYT Corporation"

    # Check line extension amount calculation
    for line in invoice.invoice_lines:
        assert line.line_extension_amount == line.invoiced_quantity * line.price["price_amount"]


def test_invoice_director_construct_invoice_json(sample_order_json):
    """
    Test that InvoiceDirector builds the Invoice object correctly from JSON.
    """
    unmarshaller = OrderJsonUnmarshaller()
    director = InvoiceDirector(unmarshaller)

    invoice = director.construct_invoice_from_data(sample_order_json)

    # Print the built Invoice
    print("\n--- Constructed Invoice from JSON ---")
    #print(invoice.model_dump_json(indent=4))

    # Basic assertions
    assert invoice.header.buyer_reference == "CON0095678"
    assert invoice.supplier_party.party_name == "Consortial"
    assert invoice.customer_party.party_name == "IYT Corporation"

    # Check line extension amount calculation
    for line in invoice.invoice_lines:
        assert line.line_extension_amount == line.invoiced_quantity * line.price["price_amount"]


def test_missing_fields_from_xml(sample_order_xml):
    """
    Test that find_missing_fields() detects missing fields in an XML order.
    """
    unmarshaller = OrderXmlUnmarshaller()
    director = InvoiceDirector(unmarshaller)

    # Build the invoice (your sample XML has some missing fields)
    invoice = director.construct_invoice_from_data(sample_order_xml)

    # Run the missing field detection
    missing = find_missing_fields(invoice)

    # ✅ Print for debugging
    print("\n--- Missing Fields from XML ---")
    print(missing)
