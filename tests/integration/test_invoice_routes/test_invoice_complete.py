import copy
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models.invoice_update import InvoiceUpdateModel
from src.services.auth_service import get_current_user_id

# Override dependency to avoid real auth
app.dependency_overrides[get_current_user_id] = lambda: "test-user"
client = TestClient(app)


def test_complete_invoice_success(sample_invoice_json):
    """
    Test completing a valid invoice successfully.
    """
    payload = copy.deepcopy(sample_invoice_json)
    response = client.post(
        "/v1/user/invoices/complete",
        json=payload,
    )

    print("\n Response JSON:", response.json()) 
    assert response.status_code == 200
    data = response.json()
    assert "invoice_id" in data
    assert "invoice" in data


def test_complete_invoice_missing_required_field(sample_invoice_json):
    """
    Should fail due to missing required field (supplier registration_name removed)
    """
    payload = copy.deepcopy(sample_invoice_json)
    # Remove required supplier registration_name
    del payload["accounting_supplier_party"]["party_legal_entity"]["registration_name"]

    response = client.post(
        "/v1/user/invoices/complete",
        json=payload,
    )

    assert response.status_code == 400
    data = response.json()
    assert "missing_invoice_fields" in data["detail"]
