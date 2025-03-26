import json
from src.marshallers.strategies.xml_order_parser import XmlOrderParser
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.services.invoice_service import InvoiceService
from src.validators.missing_field_checker import MissingFieldChecker
from src.models.invoice_response_models import DraftInvoiceResponse

def test_generate_draft_invoice_json(sample_order_json):
    service = InvoiceService()
    file_type = "application/json"
    user_id = "test-user"

    result: DraftInvoiceResponse = service.generate_draft_invoice(sample_order_json, file_type, user_id)

    # Print the entire DraftInvoiceResponse in JSON format
    print("\n Full Draft Invoice Response:")
    print(result.json(indent=2))

    # Validate response model
    assert isinstance(result, DraftInvoiceResponse)
    assert isinstance(result.invoice, dict)

    # Sample field checks
    assert result.invoice["customization_id"] == "urn:oasis:names:specification:ubl:xpath:Order-2.0:sbs-1.0-draft"
    assert result.invoice["accounting_supplier_party"]["party_name"]["name"] == "Consortial"
    assert result.invoice["accounting_customer_party"]["party_name"]["name"] == "IYT Corporation"

    # Invoice lines check
    assert "invoice_lines" in result.invoice
    assert result.invoice["invoice_lines"][0]["item"]["name"] == "beeswax"

    # Missing fields structure
    assert isinstance(result.missing_fields_report.missing_invoice_fields, list)
    assert isinstance(result.missing_fields_report.missing_invoice_lines, list)


def test_missing_fields_detected_from_sample_xml(sample_order_xml):
    """
    Validate missing required fields are detected properly from sample XML.
    """
    unmarshaller = XmlOrderParser()
    director = InvoiceMarshaller(unmarshaller)
    invoice = director.marshal(sample_order_xml)

    report = MissingFieldChecker(invoice).run()

    # Pretty print the MissingFieldsReport
    print("\n Full Missing Fields Report:")
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

    # Assert expected missing fields match
    assert set(report.missing_invoice_fields) == set(expected_missing_fields)
    assert set(report.missing_invoice_lines) == set(expected_missing_lines)
