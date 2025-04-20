"""
Tests 'get invoice' endpoint 
Modules Tested: invoice_routes.py, invoice_service.py, invoice_repository.py
"""
import copy
import json
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.services.auth_service import get_current_user_id

# Override dependency to avoid real auth
app.dependency_overrides[get_current_user_id] = lambda: "test-user"
client = TestClient(app)

def test_get_draft_invoice_after_upload(sample_order_json):
    """
    Upload a UBL order (draft), then retrieve the saved draft invoice by ID.
    """
    upload_response = client.post(
        "/v1/user/invoices/upload",
        files={"file": ("order.json", sample_order_json, "application/json")}
    )

    assert upload_response.status_code == 200
    draft = upload_response.json()

    invoice_id = draft["invoice_id"]
    assert invoice_id is not None
    assert draft["status"] == "draft"

    # Now retrieve using GET
    get_response = client.get(f"/v1/user/invoices/{invoice_id}")
    assert get_response.status_code == 200

    result = get_response.json()
    print("\nRetrieved Invoice:")
    print(json.dumps(result, indent=2))
    assert result["invoice_id"] == invoice_id
    assert result["status"] == "draft"
    assert "invoice" in result

def test_get_invoice_not_found():
    invalid_id = "INV-FAKE123"
    response = client.get(f"/v1/user/invoices/{invalid_id}")
    assert response.status_code == 404
