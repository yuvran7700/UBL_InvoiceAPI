"""
Test cases for invoice creation logic
Modules Tested: InvoiceService, InvoiceMarshaller, MissingFieldChecker
"""
import json
from src.marshallers.marshaller_factory import MarshallerFactory
from src.marshallers.strategies.xml_order_parser import XmlOrderParser
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.services.invoice_service import InvoiceService
from src.validators.missing_field_checker import MissingFieldChecker
from src.models.invoice_response_models import InvoiceResponse, InvoiceStatus

def test_generate_draft_invoice_json(sample_order_json):
    service = InvoiceService()
    file_type = "application/json"
    user_id = "test-user"

    result: InvoiceResponse = service.generate_draft_invoice(sample_order_json, file_type, user_id)

    # Print the entire InvoiceResponse in JSON format
    print("\n Full Draft Invoice Response:")
    print(result.json(indent=2))

    # Check explicitly that invoice_id is generated even in draft
    assert result.invoice_id is not None
    assert result.invoice.id == result.invoice_id


    # Status clearly set to draft
    assert result.status == InvoiceStatus.DRAFT

    # Validate response model
    assert isinstance(result, InvoiceResponse)
    assert isinstance(result.invoice, dict) or isinstance(result.invoice, object)

    # Sample field checks
    assert result.invoice.customization_id == "urn:oasis:names:specification:ubl:xpath:Order-2.0:sbs-1.0-draft"
    assert result.invoice.accounting_supplier_party.party_name.name == "Consortial"
    assert result.invoice.accounting_customer_party.party_name.name == "IYT Corporation"

    # Invoice lines check
    assert result.invoice.invoice_lines is not None
    assert result.invoice.invoice_lines[0].item.name == "beeswax"

    # Missing fields structure
    assert isinstance(result.missing_fields_report.missing_invoice_fields, list)
    assert isinstance(result.missing_fields_report.missing_invoice_lines, list)


def test_missing_fields_detected_from_sample_xml(sample_order_xml):
    """
    Validate missing required fields are detected properly from sample XML.
    """
    # Use the new MarshallerFactory explicitly
    marshaller = MarshallerFactory()
    invoice = marshaller.marshal_from_file(sample_order_xml, "application/xml")

    # Check missing fields explicitly
    report = MissingFieldChecker(invoice).run()

    # Pretty print MissingFieldsReport explicitly
    print("\nFull Missing Fields Report:")
    print(report.json(indent=2))

    expected_missing_fields = [
        "accounting_supplier_party.party_legal_entity.registration_name",
        "accounting_customer_party.party_legal_entity.registration_name",
        "legal_monetary_total.payable_amount"
    ]

    expected_missing_lines = [
        "invoice_lines[0].unit_code",
        "invoice_lines[0].item.classified_tax_category.id",
        "invoice_lines[0].item.classified_tax_category.percent",
        "invoice_lines[0].item.classified_tax_category.tax_scheme_id"
    ]

    # Assert explicitly that expected missing fields match
    assert set(report.missing_invoice_fields) == set(expected_missing_fields)
    assert set(report.missing_invoice_lines) == set(expected_missing_lines)