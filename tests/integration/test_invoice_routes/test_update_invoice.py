import copy
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.services.auth_service import get_current_user_id

# Override dependency for testing
app.dependency_overrides[get_current_user_id] = lambda: "test-user"
client = TestClient(app)

@pytest.mark.integration
def test_update_invoice_success(sample_order_json):
    """
    Integration test:
      1. Upload a draft invoice using sample_order_json.
      2. Update the invoice (e.g., change buyer_reference).
      3. Verify that the updated invoice reflects the changes and returns a missing fields report.
    """
    # Step 1: Upload invoice
    upload_response = client.post(
        "/v1/user/invoices/upload",
        files={"file": ("order.json", sample_order_json, "application/json")},
        headers={"Authorization": "Bearer test-token"}
    )
    assert upload_response.status_code == 200
    draft = upload_response.json()
    invoice_id = draft["invoice_id"]
    assert invoice_id is not None
    assert draft["status"] == "draft"
    
    # Step 2: Update the invoice with new data (e.g., update buyer_reference)
    update_payload = {"buyer_reference": "UPDATED_REF"}
    update_response = client.patch(f"/v1/user/invoices/{invoice_id}", json=update_payload)
    assert update_response.status_code == 200
    updated_invoice = update_response.json()
    # Expect that the invoice buyer_reference has been updated
    assert updated_invoice["invoice"]["buyer_reference"] == "UPDATED_REF"
    # Missing fields report is included in the response (could be empty or list missing fields)
    assert "missing_fields_report" in updated_invoice

@pytest.mark.integration
def test_update_invoice_not_found():
    """
    Attempt to update an invoice that does not exist.
    """
    update_payload = {"buyer_reference": "UPDATED_REF"}
    response = client.patch("/v1/user/invoices/INV-NONEXISTENT", json=update_payload)
    assert response.status_code == 404
    data = response.json()

@pytest.mark.integration
def test_update_completed_invoice(sample_invoice_json):
    """
    Test that once an invoice is complete, further edits are not allowed.
    Workflow:
      1. Complete an invoice using the complete endpoint.
      2. Attempt to update (PATCH) the completed invoice.
      3. Verify that the update is rejected with a 403 error.
    """
    # Step 1: Complete an invoice. 
    # (Assume sample_invoice_json is complete enough for completion.)
    complete_response = client.post("/v1/user/invoices/complete", json=sample_invoice_json)
    assert complete_response.status_code == 200
    completed_invoice = complete_response.json()
    invoice_id = completed_invoice["invoice_id"]
    assert invoice_id is not None
    assert completed_invoice["status"] == "completed"
    
    # Step 2: Attempt to update the now-completed invoice.
    update_payload = {"buyer_reference": "NEW_REF"}
    update_response = client.patch(f"/v1/user/invoices/{invoice_id}", json=update_payload)
    
    # Expect a 403 Forbidden because only draft invoices can be updated.
    assert update_response.status_code == 403
    data = update_response.json()