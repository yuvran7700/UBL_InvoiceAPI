# tests/unit/test_order_extraction.py
"""
Unit tests for order XML extraction and order creation.
Tests verify that header fields are renamed and that invoice_lines are used.
"""

import pytest
from src.utils.order_xml_extractor import OrderXmlExtractor
from src.order_type_creation.order_director import OrderDirector
from src.models.order_type import OrderType

# Test extraction of header data with updated keys.
def test_extract_header(sample_order_xml):
    data = OrderXmlExtractor.extract(sample_order_xml)
    header = data.get("header")
    assert header is not None
    # Updated header keys.
    assert "order_reference" in header and header["order_reference"] != ""
    assert "buyer_reference" in header

# Test extraction of buyer data remains unchanged.
def test_extract_buyer(sample_order_xml):
    data = OrderXmlExtractor.extract(sample_order_xml)
    buyer = data.get("buyer")
    assert buyer is not None
    # Check required buyer fields.
    assert "buyer_name" in buyer and buyer["buyer_name"] != ""
    assert "buyer_account_customer_id" in buyer and buyer["buyer_account_customer_id"] != ""
    assert "buyer_account_supplier_id" in buyer and buyer["buyer_account_supplier_id"] != ""
    assert "buyer_address" in buyer and buyer["buyer_address"] != ""
    assert "buyer_electronic_address" in buyer
    assert "buyer_scheme_id" in buyer
    assert "buyer_country" in buyer

# Test extraction of seller data remains unchanged.
def test_extract_seller(sample_order_xml):
    data = OrderXmlExtractor.extract(sample_order_xml)
    seller = data.get("seller")
    assert seller is not None
    assert "seller_name" in seller and seller["seller_name"] != ""
    assert "seller_account" in seller and seller["seller_account"] != ""
    assert "seller_address" in seller and seller["seller_address"] != ""

# Test extraction of payment terms remains unchanged.
def test_extract_payment_terms(sample_order_xml):
    data = OrderXmlExtractor.extract(sample_order_xml)
    payment_terms = data.get("payment_terms")
    if payment_terms:
        assert isinstance(payment_terms, str)

# Test extraction of invoice lines.
def test_extract_invoice_lines(sample_order_xml):
    data = OrderXmlExtractor.extract(sample_order_xml)
    invoice_lines = data.get("invoice_lines")
    assert invoice_lines is not None
    assert len(invoice_lines) > 0
    first_line = invoice_lines[0]
    assert "line_id" in first_line and first_line["line_id"] != ""
    assert "quantity" in first_line and first_line["quantity"] > 0

# Test full order creation using the Director.
def test_full_order_creation(sample_order_xml):
    order = OrderDirector.construct_order_from_xml(sample_order_xml)
    print(order)
    assert isinstance(order, OrderType)
    # Updated assertions for new field names.
    assert order.order_reference != ""
    assert order.buyer_reference != ""
    assert order.AccountingCustomerParty is not None
    assert order.AccountingSupplierParty is not None
    # Check that invoice lines were parsed.
    assert isinstance(order.invoice_lines, list)
    assert len(order.invoice_lines) > 0

# Test to print all extracted data for inspection.
def test_extract_all_data(sample_order_xml):
    extracted_data = OrderXmlExtractor.extract(sample_order_xml)
    print("\nExtracted Data:")
    for key, value in extracted_data.items():
        print(f"{key}: {value}")
    
    # Header assertions with updated keys.
    header = extracted_data.get("header")
    assert header is not None
    assert header.get("order_reference") == "AEG012345", f"Expected order_reference 'AEG012345', got {header.get('order_reference')}"
    assert header.get("buyer_reference") == "CON0095678", f"Expected buyer_reference 'CON0095678', got {header.get('buyer_reference')}"
    assert header.get("note") == "sample"
    
    # Buyer assertions.
    buyer = extracted_data.get("buyer")
    assert buyer is not None
    assert buyer.get("buyer_name") == "IYT Corporation"
    assert buyer.get("buyer_account_customer_id") == "XFB01"
    assert buyer.get("buyer_account_supplier_id") == "GT00978567"
    assert "Avon Way" in buyer.get("buyer_address")
    assert buyer.get("buyer_electronic_address") is None
    assert buyer.get("buyer_scheme_id") is None
    assert buyer.get("buyer_country") == "GB"
    
    buyer_contact = buyer.get("buyer_contact")
    assert buyer_contact is not None
    assert buyer_contact.name == "Mr Fred Churchill"
    assert buyer_contact.telephone == "0127 2653214"
    assert buyer_contact.telefax == "0127 2653215"
    assert buyer_contact.electronic_mail == "fred@iytcorporation.gov.uk"
    
    buyer_tax_scheme = buyer.get("buyer_tax_scheme")
    assert buyer_tax_scheme is not None
    assert buyer_tax_scheme.registration_name == "Bridgtow District Council"
    assert buyer_tax_scheme.company_id == "12356478"
    assert buyer_tax_scheme.exemption_reason == "Local Authority"
    nested_tax = buyer_tax_scheme.tax_scheme
    assert nested_tax is not None
    assert nested_tax.id == "UK VAT"
    assert nested_tax.tax_type_code == "VAT"
    
    # Seller assertions.
    seller = extracted_data.get("seller")
    assert seller is not None
    assert seller.get("seller_account") == "CO001"
    assert seller.get("seller_name") == "Consortial"
    assert "Busy Street" in seller.get("seller_address")
    
    seller_contact = seller.get("seller_contact")
    assert seller_contact is not None
    assert seller_contact.name == "Mrs Bouquet"
    assert seller_contact.telephone == "0158 1233714"
    assert seller_contact.telefax == "0158 1233856"
    assert seller_contact.electronic_mail == "bouquet@fpconsortial.co.uk"
    
    seller_tax_scheme = seller.get("seller_tax_scheme")
    assert seller_tax_scheme is not None
    assert seller_tax_scheme.registration_name == "Farthing Purchasing Consortium"
    assert seller_tax_scheme.company_id == "175 269 2355"
    assert seller_tax_scheme.exemption_reason == "N/A"
    nested_seller_tax = seller_tax_scheme.tax_scheme
    assert nested_seller_tax is not None
    assert nested_seller_tax.id == "VAT"
    assert nested_seller_tax.tax_type_code == "VAT"
    
    # Payment terms.
    payment_terms = extracted_data.get("payment_terms")
    assert payment_terms == "order response required; payment is by BACS or by cheque"
    
    # Invoice lines assertions.
    invoice_lines = extracted_data.get("invoice_lines")
    assert invoice_lines is not None
    assert len(invoice_lines) == 1
    order_line = invoice_lines[0]
    assert order_line.get("note") == "this is an illustrative order line"
    assert order_line.get("line_id") == "1"
    assert float(order_line.get("quantity")) == 100.0
    assert float(order_line.get("unit_price")) == 100.00
    assert order_line.get("item_description") == "Acme beeswax"
    assert order_line.get("item_name") == "beeswax"
    assert order_line.get("buyers_item_id") == "6578489"
    assert order_line.get("sellers_item_id") == "17589683"
