# test_service_invoice.py

from unittest.mock import patch
import pytest
from datetime import date
from src.services.invoice_service import InvoiceService
from src.repositories.invoice_repository import get_invoices_by_user
from src.domain.models.invoice_response_models import InvoiceResponse, InvoiceStatus
from src.domain.models.invoice_update import InvoiceUpdateModel


#Testing the service method
@pytest.mark.unit
@patch("src.services.invoice_service.get_invoices_by_user")  # Mocking the service method
def test_list_filtered_invoices_service(mock_repo):
    mock_repo.return_value = [
        (InvoiceUpdateModel(id="INV-1", issue_date=date(2022, 1, 1)), InvoiceStatus.DRAFT),
        (InvoiceUpdateModel(id="INV-2", issue_date=date(2022, 2, 1)), InvoiceStatus.COMPLETED)
    ]

    service = InvoiceService()

    # No filters
    results = service.list_filtered_invoices("test-user", None, None, None)
    assert len(results) == 2

    # Filter by date range
    results = service.list_filtered_invoices("test-user", None, date(2022, 1, 1), date(2022, 1, 31))
    assert len(results) == 1
    assert results[0].invoice_id == "INV-1"

    # Filter by status (should skip repo optimization in mock, but service should still work)
    results = service.list_filtered_invoices("test-user", InvoiceStatus.DRAFT, None, None)
    assert results[0].status == InvoiceStatus.DRAFT



#testing the repository method
@pytest.mark.unit
@patch("src.db.dynamodb_client.invoices_table.query")
def test_get_invoices_by_user_with_status(mock_query):
    # Simulate DynamoDB GSI query
    mock_query.return_value = {
        "Items": [
            {"invoice_id": "INV-1", "status": "draft", "issue_date": "2022-01-01"},
            {"invoice_id": "INV-2", "status": "draft", "issue_date": "2022-02-01"}
        ]
    }

    results = get_invoices_by_user("test-user", status=InvoiceStatus.DRAFT)
    assert len(results) == 2
