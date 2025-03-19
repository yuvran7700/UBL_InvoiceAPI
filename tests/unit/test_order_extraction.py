# tests/unit/test_order_extraction.py
"""
Unit tests for order XML extraction and order creation.
Tests verify that header fields are renamed and that invoice_lines are used.
"""

from fastapi import HTTPException
import pytest
from src.marshallers.order_unmarshaller_factory import OrderUnmarshaller
from src.marshallers.order_xml_unmarshaller_factory import OrderXmlUnmarshaller
from src.marshallers.order_json_unmarshaller_factory import OrderJsonUnmarshaller
from src.order_type_creation.invoice_director import InvoiceDirector
from src.order_type_creation.invoice_builder import InvoiceBuilder
from src.models.invoice import Invoice, InvoiceHeader, InvoiceLine, Party, PartyTaxScheme
from src.models.tax import TaxScheme
from datetime import date


# Test extraction of header data with updated keys.
def test_extract_header_from_xml(sample_order_xml):
    unmarshaller = OrderXmlUnmarshaller()
    header = unmarshaller.unmarshal_header(sample_order_xml)
    
    assert header.customization_id == "urn:oasis:names:specification:ubl:xpath:Order-2.0:sbs-1.0-draft"
    assert header.profile_id == "bpid:urn:oasis:names:draft:bpss:ubl-2-sbs-order-with-simple-response-draft"
    assert header.invoice_id is None
    assert header.issue_date == date(2005, 6, 20)
    assert header.due_date is None
    assert header.invoice_type_code == "380"
    assert header.document_currency_code == "AUD"
    assert header.buyer_reference == "CON0095678"
    assert header.order_reference == "AEG012345"


#Test case for extracting header from JSON
def test_extract_header_from_json(sample_order_json):
    unmarshaller = OrderJsonUnmarshaller()
    header = unmarshaller.unmarshal_header(sample_order_json)
    
    assert header.customization_id == "urn:oasis:names:specification:ubl:xpath:Order-2.0:sbs-1.0-draft"
    assert header.profile_id == "bpid:urn:oasis:names:draft:bpss:ubl-2-sbs-order-with-simple-response-draft"
    assert header.invoice_id is None
    assert header.issue_date == date(2005, 6, 20)
    assert header.due_date is None
    assert header.invoice_type_code == "380"
    assert header.document_currency_code == "AUD"
    assert header.buyer_reference == "CON0095678"
    assert header.order_reference == "AEG012345"

# Test case for extracting Party from XML
def test_extract_party_from_xml(sample_order_xml):
    unmarshaller = OrderXmlUnmarshaller()
    party = unmarshaller.unmarshal_party(sample_order_xml)
    
    assert party.party_name == "IYT Corporation"
    assert party.postal_address["street"] == "Avon Way"
    assert party.postal_address["city"] == "Bridgtow"
    assert party.postal_address["postal_code"] == "ZZ99 1ZZ"
    assert party.postal_address["country"] == "GB"

# Test case for extracting Party from JSON
def test_extract_party_from_json(sample_order_json):
    unmarshaller = OrderJsonUnmarshaller()
    party = unmarshaller.unmarshal_party(sample_order_json)
    
    assert party.party_name == "IYT Corporation"
    assert party.postal_address["street"] == "Avon Way"
    assert party.postal_address["city"] == "Bridgtow"
    assert party.postal_address["postal_code"] == "ZZ99 1ZZ"
    assert party.postal_address["country"] == "GB"