import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.main import app  # adjust based on your app location
from src.services.auth_service import get_current_user_id

client = TestClient(app)

@patch("src.routes.invoice_routes.InvoiceService.generate_draft_invoice")
def test_upload_invoice_route_with_sample_user_fixture(
    mock_generate_draft,
    sample_user_json,
    sample_order_xml
):
    user_email = sample_user_json["email"]

    mock_generate_draft.return_value = {
        "invoice": {"header": {}, "supplier_party": {}, "customer_party": {}, "invoice_lines": []},
        "missing_fields": []
    }

    # Inject user_id override for FastAPI dependency system
    app.dependency_overrides[get_current_user_id] = lambda: user_email

    files = {
        "file": ("order.xml", sample_order_xml, "application/xml")
    }

    response = client.post("/v1/user/invoices/upload", files=files)

    assert response.status_code == 200
    mock_generate_draft.assert_called_once()
    args, kwargs = mock_generate_draft.call_args
    assert user_email in args

    # ✅ Cleanup override
    app.dependency_overrides = {}
