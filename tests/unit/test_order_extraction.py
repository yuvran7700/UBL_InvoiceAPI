# tests/unit/test_order_extraction.py
"""
Unit tests for order XML extraction and order creation.
Tests verify that header fields are renamed and that invoice_lines are used.
"""

from datetime import date
from src.marshallers.strategies.xml_order_parser import XmlOrderParser
from src.marshallers.strategies.json_order_parser import JsonOrderParser



# Test extraction of header data with updated keys.
def test_extract_header_from_xml(sample_order_xml):
    unmarshaller = XmlOrderParser()
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


def test_extract_buyer_party_from_xml(sample_order_xml):
    """
    Test the unmarshal_party method to extract buyer party data from XML.
    """
    unmarshaller = XmlOrderParser()
    buyer_party = unmarshaller.unmarshal_party(sample_order_xml, "BuyerCustomerParty")
    
    # Validate buyer party fields
    assert buyer_party.party_name == "IYT Corporation"
    assert buyer_party.postal_address["street"] == "Avon Way"
    assert buyer_party.postal_address["city"] == "Bridgtow"
    assert buyer_party.party_legal_entity["registration_name"] == "Bridgtow District Council"
    
    # Validate contact extraction
    assert buyer_party.contact is not None
    assert buyer_party.contact.name == "Mr Fred Churchill"
    assert buyer_party.contact.telephone == "0127 2653214"
    assert buyer_party.contact.telefax == "0127 2653215"
    assert buyer_party.contact.electronic_mail == "fred@iytcorporation.gov.uk"
    
    # Validate tax scheme extraction
    assert buyer_party.party_tax_scheme is not None
    assert buyer_party.party_tax_scheme.company_id == "12356478"
    assert buyer_party.party_tax_scheme.exemption_reason == "Local Authority"
    
    # Validate the tax scheme inside party_tax_scheme
    assert buyer_party.party_tax_scheme.tax_scheme is not None
    assert buyer_party.party_tax_scheme.tax_scheme.id == "UK VAT"
    assert buyer_party.party_tax_scheme.tax_scheme.tax_type_code == "VAT"



def test_extract_seller_party_from_xml(sample_order_xml):
    """
    Test the unmarshal_party method to extract seller party data from XML.
    """
    unmarshaller = XmlOrderParser()
    seller_party = unmarshaller.unmarshal_party(sample_order_xml, "SellerSupplierParty")
    
    # Validate seller party fields
    assert seller_party.party_name == "Consortial"
    assert seller_party.postal_address["street"] == "Busy Street"
    assert seller_party.postal_address["city"] == "Farthing"
    assert seller_party.contact.name == "Mrs Bouquet"
    assert seller_party.party_legal_entity["registration_name"] == "Farthing Purchasing Consortium"

#Test case for extracting header from JSON
def test_extract_header_from_json(sample_order_json):
    unmarshaller = JsonOrderParser()
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
    
    # Test to verify buyer party extraction from JSON
def test_extract_buyer_party_from_json(sample_order_json):
    """
    Test the unmarshal_party method to extract buyer party data from JSON.
    """
    unmarshaller = JsonOrderParser()
    buyer_party = unmarshaller.unmarshal_party(sample_order_json, "BuyerCustomerParty")

    # Assert the extracted buyer party fields
    assert buyer_party.party_name == "IYT Corporation"
    assert buyer_party.postal_address["street"] == "Avon Way"
    assert buyer_party.postal_address["city"] == "Bridgtow"
    assert buyer_party.contact.name == "Mr Fred Churchill"
    
    # Assert party legal entity and tax scheme details
    assert buyer_party.party_legal_entity["registration_name"] == "Bridgtow District Council"
    assert buyer_party.party_tax_scheme.company_id == "12356478"
    assert buyer_party.party_tax_scheme.tax_scheme.id == "UK VAT"
    assert buyer_party.party_tax_scheme.tax_scheme.tax_type_code == "VAT"
    
    assert buyer_party.party_tax_scheme.exemption_reason == "Local Authority"
    #test contact extraction
    assert buyer_party.contact.name == "Mr Fred Churchill"
    assert buyer_party.contact.telephone == "0127 2653214"
    assert buyer_party.contact.telefax == "0127 2653215"
    assert buyer_party.contact.electronic_mail == "fred@iytcorporation.gov.uk"

    
    


def test_unmarshal_invoice_lines(sample_order_json):
    """
    Test unmarshal_invoice_lines() correctly parses the OrderLine into InvoiceLine models.
    """
    unmarshaller = JsonOrderParser()
    invoice_lines = unmarshaller.unmarshal_invoice_lines(sample_order_json)

    # Ensure we have the expected number of lines
    assert len(invoice_lines) == 1

    line = invoice_lines[0]
    # Validate fields
    assert line.id == "1"
    assert line.invoiced_quantity == 100
    assert line.item.name == "beeswax"
    assert line.item.description == "Acme beeswax"
    assert line.price["price_amount"] == 100.00