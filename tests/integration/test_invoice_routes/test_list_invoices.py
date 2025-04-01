import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from src.main import app
from src.services.auth_service import get_current_user_id

# Override dependency so that get_current_user_id always returns "test-user"
app.dependency_overrides[get_current_user_id] = lambda: "test-user"
client = TestClient(app)

@pytest.mark.integration
def test_list_invoices_without_filters():
    """
    Test listing all invoices for 'test-user' without any filters.
    Assumes that the test environment has been seeded with invoice data.
    """
    response = client.get("/v1/user/invoices")
    assert response.status_code == 200
    invoices = response.json()
    assert isinstance(invoices, list)
    
    for invoice in invoices:
        assert "invoice_id" in invoice
        assert "invoice" in invoice
        assert "status" in invoice

@pytest.mark.integration
def test_list_invoices_with_filters():
    """
    Test listing invoices for 'test-user' with status and issue date range filters.
    Assumes that the test environment contains at least one invoice with:
      - status 'draft'
      - an issue_date between 2022-01-01 and 2022-12-31.
    """
    response = client.get(
        "/v1/user/invoices",
        params={
            "status": "draft",
            "issue_date_from": "2022-01-01",
            "issue_date_to": "2022-12-31"
        }
    )
    assert response.status_code == 200
    invoices = response.json()
    assert isinstance(invoices, list)
    
    # Check that returned invoices meet the filter criteria.
    for invoice in invoices:
        assert "invoice_id" in invoice
        assert "invoice" in invoice
        assert "status" in invoice
        assert invoice["status"] == "draft"
        
        # Checking issue_date range is correct
        issue_date_str = invoice["invoice"].get("issue_date")
        assert issue_date_str is not None, "Expected issue_date to be present"
        issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d").date()
        start_date = datetime.strptime("2022-01-01", "%Y-%m-%d").date()
        end_date = datetime.strptime("2022-12-31", "%Y-%m-%d").date()
        assert start_date <= issue_date <= end_date, (
            f"Issue date {issue_date} is not within range {start_date} to {end_date}"
        )
