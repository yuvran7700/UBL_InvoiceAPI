import json
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.services.auth_service import get_current_user_id

# Override dependency to always return "test-user"
app.dependency_overrides[get_current_user_id] = lambda: "test-user"
client = TestClient(app)

@pytest.mark.integration
def test_delete_invoices_route_success(sample_order_json):
    """
    Integration test for deleting a draft invoice:
      1. Upload an invoice using sample_order_json.
      2. Delete that invoice using the DELETE /v1/user/invoices endpoint.
      3. Verify deletion by confirming GET /v1/user/invoices/{invoice_id} returns 404.
    """
    # Step 1: Upload an invoice
    upload_response = client.post(
        "/v1/user/invoices/upload",
        files={"file": ("order.json", sample_order_json, "application/json")},
        headers={"Authorization": "Bearer test-token"}
    )
    assert upload_response.status_code == 200
    draft_invoice = upload_response.json()
    invoice_id = draft_invoice["invoice_id"]
    assert invoice_id is not None
    assert draft_invoice["status"] == "draft"

    # Step 2: Delete the uploaded invoice using client.request with json payload
    payload = {"invoice_ids": [invoice_id]}
    delete_response = client.request("DELETE", "/v1/user/invoices", json=payload)
    assert delete_response.status_code == 200
    result = delete_response.json()

    print("\nDeletion summary:", json.dumps(result, indent=2))

    assert "deleted" in result
    assert invoice_id in result["deleted"]
    # Expect no errors
    assert result["errors"] == []

    # Step 3: Verify deletion - GET should return 404
    get_response = client.get(f"/v1/user/invoices/{invoice_id}")
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Invoice not found."

@pytest.mark.integration
def test_delete_invoices_route_empty_payload():
    """
    Test that providing an empty invoice_ids list returns an empty deletion summary.
    """
    payload = {"invoice_ids": []}
    response = client.request("DELETE", "/v1/user/invoices", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["deleted"] == []
    assert result["errors"] == []

@pytest.mark.integration
def test_delete_invoices_route_invalid_payload():
    """
    Test that an invalid payload (e.g., missing 'invoice_ids' key) returns a 422 error.
    """
    payload = {"wrong_key": ["INV-1"]}
    response = client.request("DELETE", "/v1/user/invoices", json=payload)
    assert response.status_code == 422
