# tests/unit/test_order_extraction.py
"""
Unit tests for UBL Order document extraction for XML and JSON formats.
Modules Tested: InvoiceMarshaller, OrderParsingStrategy, JsonOrderParser, XmlOrderParser
"""
import pytest
from src.marshallers.strategies.xml_order_parser import XmlOrderParser
from src.marshallers.strategies.json_order_parser import JsonOrderParser
from src.marshallers.invoice_marshaller import InvoiceMarshaller


def test_invoice_director_construct_invoice_json(sample_order_json):
    """
    Test that InvoiceMarshaller builds the InvoiceUpdateModel correctly from JSON.
    """
    extractor = JsonOrderParser()
    marshaller = InvoiceMarshaller(extractor)

    invoice = marshaller.marshal(sample_order_json)

    #print("\n--- Constructed Invoice from JSON ---")
    #print(invoice.json(indent=4))

    # Invoice Header assertions
    assert invoice.customization_id == "urn:oasis:names:specification:ubl:xpath:Order-2.0:sbs-1.0-draft"
    assert invoice.profile_id == "bpid:urn:oasis:names:draft:bpss:ubl-2-sbs-order-with-simple-response-draft"
    assert invoice.id == "AEG012345"
    assert invoice.issue_date.isoformat() == "2005-06-20"
    assert invoice.invoice_type_code == "380"
    assert invoice.document_currency_code == "AUD"
    assert invoice.buyer_reference == "CON0095678"

    # Supplier Party assertions
    supplier = invoice.accounting_supplier_party
    assert supplier.party_name.name == "Consortial"
    assert supplier.postal_address.street_name == "Busy Street"
    assert supplier.postal_address.city_name == "Farthing"
    assert supplier.postal_address.country.identification_code == "GB"
    assert supplier.party_tax_scheme.company_id == "175 269 2355"
    assert supplier.party_tax_scheme.tax_scheme_id == "VAT"
    assert supplier.contact.name == "Mrs Bouquet"
    assert supplier.contact.telephone == "0158 1233714"
    assert supplier.contact.electronic_mail == "bouquet@fpconsortial.co.uk"

    # Customer Party assertions
    customer = invoice.accounting_customer_party
    assert customer.party_name.name == "IYT Corporation"
    assert customer.postal_address.street_name == "Avon Way"
    assert customer.postal_address.city_name == "Bridgtow"
    assert customer.postal_address.country.identification_code == "GB"
    assert customer.party_tax_scheme.company_id == "12356478"
    assert customer.party_tax_scheme.tax_scheme_id == "UK VAT"
    assert customer.contact.name == "Mr Fred Churchill"
    assert customer.contact.telephone == "0127 2653214"
    assert customer.contact.electronic_mail == "fred@iytcorporation.gov.uk"

    # Invoice Lines assertion
    assert len(invoice.invoice_lines) == 1
    line = invoice.invoice_lines[0]
    assert line.id == "1"
    assert line.invoiced_quantity == 100.0
    assert line.item.name == "beeswax"
    assert line.item.description == "Acme beeswax"
    assert line.item.buyers_item_id == "6578489"
    assert line.item.sellers_item_id == "17589683"
    assert line.price.price_amount == 100.0
    assert line.line_extension_amount == line.invoiced_quantity * line.price.price_amount

    # Monetary Total assertion
    assert invoice.legal_monetary_total.line_extension_amount == 10000.0


def test_invoice_director_construct_invoice_xml(sample_order_xml):
    """
    Test that InvoiceMarshaller builds the InvoiceUpdateModel correctly from JSON.
    """
    extractor = XmlOrderParser()
    marshaller = InvoiceMarshaller(extractor)

    invoice = marshaller.marshal(sample_order_xml)

    print("\n--- Constructed Invoice from XML ---")
    print(invoice.json(indent=4))

    # Invoice Header assertions
    assert invoice.customization_id == "urn:oasis:names:specification:ubl:xpath:Order-2.0:sbs-1.0-draft"
    assert invoice.profile_id == "bpid:urn:oasis:names:draft:bpss:ubl-2-sbs-order-with-simple-response-draft"
    assert invoice.id == "AEG012345"
    assert invoice.issue_date.isoformat() == "2005-06-20"
    assert invoice.invoice_type_code == "380"
    assert invoice.document_currency_code == "AUD"
    assert invoice.buyer_reference == "CON0095678"

    # Supplier Party assertions
    supplier = invoice.accounting_supplier_party
    assert supplier.party_name.name == "Consortial"
    assert supplier.postal_address.street_name == "Busy Street"
    assert supplier.postal_address.city_name == "Farthing"
    assert supplier.postal_address.country.identification_code == "GB"
    assert supplier.party_tax_scheme.company_id == "175 269 2355"
    assert supplier.party_tax_scheme.tax_scheme_id == "VAT"
    assert supplier.contact.name == "Mrs Bouquet"
    assert supplier.contact.telephone == "0158 1233714"
    assert supplier.contact.electronic_mail == "bouquet@fpconsortial.co.uk"

    # Customer Party assertions
    customer = invoice.accounting_customer_party
    assert customer.party_name.name == "IYT Corporation"
    assert customer.postal_address.street_name == "Avon Way"
    assert customer.postal_address.city_name == "Bridgtow"
    assert customer.postal_address.country.identification_code == "GB"
    assert customer.party_tax_scheme.company_id == "12356478"
    assert customer.party_tax_scheme.tax_scheme_id == "UK VAT"
    assert customer.contact.name == "Mr Fred Churchill"
    assert customer.contact.telephone == "0127 2653214"
    assert customer.contact.electronic_mail == "fred@iytcorporation.gov.uk"

    # Invoice Lines assertion
    assert len(invoice.invoice_lines) == 1
    line = invoice.invoice_lines[0]
    assert line.id == "1"
    assert line.invoiced_quantity == 100.0
    assert line.item.name == "beeswax"
    assert line.item.description == "Acme beeswax"
    assert line.item.buyers_item_id == "6578489"
    assert line.item.sellers_item_id == "17589683"
    assert line.price.price_amount == 100.0
    assert line.line_extension_amount == line.invoiced_quantity * line.price.price_amount

    # Monetary Total assertion
    assert invoice.legal_monetary_total.line_extension_amount == 10000.0

