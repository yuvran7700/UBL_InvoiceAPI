#tests/unit/invoice_tests/test_invoice_delete.py
import pytest
from datetime import date
from unittest.mock import patch
from src.services.invoice_service import InvoiceService
from src.models.invoice_response_models import InvoiceStatus
from src.models.invoice_update import InvoiceUpdateModel
from src.repositories.invoice_repository import delete_invoices_by_id

# Dummy batch writer to simulate DynamoDB's batch_writer.
class DummyBatchWriter:
    def __init__(self):
        self.calls = []
    def delete_item(self, **kwargs):
        self.calls.append(kwargs)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# --- Service Layer Unit Tests ---

@patch("src.services.invoice_service.delete_invoices_by_id")
@patch("src.services.invoice_service.get_invoices_by_user")
def test_delete_user_invoices_success(mock_get_invoices, mock_delete_invoices_by_id):

    # Prepare a sample draft invoice.
    invoice = InvoiceUpdateModel(id="INV-1", issue_date=date(2022, 1, 1))

    mock_get_invoices.return_value = [(invoice, InvoiceStatus.DRAFT)]
  
    service = InvoiceService()

    result = service.delete_user_invoices(["INV-1", "INV-2"], "test-user")

    assert result["deleted"] == ["INV-1"]
    assert any(err["invoice_id"] == "INV-2" for err in result["errors"])

    mock_delete_invoices_by_id.assert_called_once_with(["INV-1"], "test-user")

@patch("src.services.invoice_service.delete_invoices_by_id", side_effect=Exception("Batch delete error"))
@patch("src.services.invoice_service.get_invoices_by_user")
def test_delete_user_invoices_batch_delete_failure(mock_get_invoices, mock_delete_invoices_by_id):
    # Prepare a valid draft invoice.
    invoice = InvoiceUpdateModel(id="INV-1", issue_date=date(2022, 1, 1))
    mock_get_invoices.return_value = [(invoice, InvoiceStatus.DRAFT)]
    
    service = InvoiceService()

    result = service.delete_user_invoices(["INV-1"], "test-user")
    
    assert result["deleted"] == ["INV-1"]
    assert any("Batch delete error" in err["reason"] for err in result["errors"])

# --- Repository Layer Unit Tests ---

@patch("src.repositories.invoice_repository.invoices_table.batch_writer")
def test_delete_invoices_by_id_success(mock_batch_writer):
    # Use our DummyBatchWriter instead of MagicMock.
    dummy_writer = DummyBatchWriter()
    # Configure the patch so that __enter__ returns our dummy writer.
    mock_batch_writer.return_value.__enter__.return_value = dummy_writer
    
    
    delete_invoices_by_id(["INV-1", "INV-2"], "test-user")
    
    # Verify that delete_item was called once per invoice.
    expected_calls = [
        {"Key": {"user_id": "test-user", "invoice_id": "INV-1"}},
        {"Key": {"user_id": "test-user", "invoice_id": "INV-2"}}
    ]
    for expected in expected_calls:
        assert expected in dummy_writer.calls

@patch("src.repositories.invoice_repository.invoices_table.batch_writer", side_effect=Exception("Batch writer failure"))
def test_delete_invoices_by_id_failure(mock_batch_writer):
    with pytest.raises(Exception) as excinfo:
        delete_invoices_by_id(["INV-1"], "test-user")
    assert "Batch writer failure" in str(excinfo.value)
