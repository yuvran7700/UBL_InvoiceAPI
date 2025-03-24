"""
This module contains unit tests for verifying business rules and the process
of building draft invoices using the InvoiceMarshaller and related components.
"""


from fastapi import HTTPException
import pytest
from src.marshallers.strategies.order_parsing_strategy import OrderParsingStrategy
from src.marshallers.strategies.xml_order_parser import XmlOrderParser
from src.marshallers.strategies.json_order_parser import JsonOrderParser
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.utils.missing_field_checker import find_missing_fields



def test_invoice_director_construct_invoice_xml(sample_order_xml):
    """
    Test that InvoiceMarshaller builds the Invoice object correctly from XML.
    """
    unmarshaller = XmlOrderParser()
    director = InvoiceMarshaller(unmarshaller)

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
    Test that InvoiceMarshaller builds the Invoice object correctly from JSON.
    """
    unmarshaller = JsonOrderParser()
    director = InvoiceMarshaller(unmarshaller)

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
    unmarshaller = XmlOrderParser()
    director = InvoiceMarshaller(unmarshaller)

    # Build the invoice (your sample XML has some missing fields)
    invoice = director.construct_invoice_from_data(sample_order_xml)

    # Run the missing field detection
    missing = find_missing_fields(invoice)

    # ✅ Print for debugging
    print("\n--- Missing Fields from XML ---")
    print(missing)
