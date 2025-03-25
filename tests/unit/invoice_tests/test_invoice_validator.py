import pytest
from fastapi import HTTPException
from src.validators.invoice_validator import InvoiceValidator
from src.models.invoice import Invoice
from src.marshallers.strategies.json_order_parser import JsonOrderParser
from src.marshallers.invoice_marshaller import InvoiceMarshaller

def test_invoice_with_future_issue_date(sample_invoice_json):
    invoice = Invoice(**sample_invoice_json)
    # Validation (raises if invalid)
    InvoiceValidator.raise_if_invalid(invoice)

    # if no exception is raised, validation passed
    assert True
    
def test_invalid_invoice_fails_validation(sample_invalid_invoice_json):
    invoice = Invoice(**sample_invalid_invoice_json)

    with pytest.raises(Exception) as exc_info:
        InvoiceValidator.raise_if_invalid(invoice)

    # Access the validation errors list directly
    errors = exc_info.value.detail['validation_errors']
    assert "IssueDate cannot be in the future." in errors
    assert "DueDate cannot be earlier than IssueDate." in errors
    assert "Invoice Line 1: InvoicedQuantity must be positive." in errors
    assert "Invoice Line 1: PriceAmount cannot be negative." in errors
    assert "Invoice Line 1: VAT percent must be between 0 and 100." in errors


