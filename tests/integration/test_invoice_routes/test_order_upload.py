"""
Test order upload endpoint for JSON and XML files.
Modules Tested: InvoiceRoutes, InvoiceService, InvoiceMarshaller, OrderParsingStrategy
"""
import json
from fastapi.testclient import TestClient
from src.main import app
from src.services.auth_service import get_current_user_id


app.dependency_overrides[get_current_user_id] = lambda: "test-user"
client = TestClient(app)

def test_order_upload_json_success(sample_order_json):
    """
    Test successful JSON order upload and draft invoice generation.
    """
    response = client.post(
        "/v1/user/invoices/upload",
        files={"file": ("order.json", sample_order_json, "application/json")},
        headers={"Authorization": "Bearer test-token"}  # Optional if auth is enabled
    )

    assert response.status_code == 200
    result = response.json()

    # Validate unified API response structure explicitly
    assert "invoice_id" in result
    assert "invoice" in result
    assert "missing_fields_report" in result
    assert "status" in result

    # Check explicitly generated invoice_id even for drafts
    assert result["invoice_id"] is not None
    assert result["status"] == "draft"

    # Validate types explicitly
    assert isinstance(result["invoice"], dict)
    assert isinstance(result["missing_fields_report"]["missing_invoice_fields"], list)
    assert isinstance(result["missing_fields_report"]["missing_invoice_lines"], list)

    # Optional field validation explicitly
    assert result["invoice"]["id"] == result["invoice_id"]
    assert result["invoice"]["accounting_supplier_party"]["party_name"]["name"] == "Consortial"

    # Print result explicitly for review
    print("\nAPI Response (JSON):")
    print(json.dumps(result, indent=2))

def test_order_upload_xml_success(sample_order_xml):
    """
    Test successful XML order upload and draft invoice generation.
    """
    response = client.post(
        "/v1/user/invoices/upload",
        files={"file": ("order.xml", sample_order_xml, "application/xml")},
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 200
    result = response.json()

    # Validate unified API response structure explicitly
    assert "invoice_id" in result
    assert "invoice" in result
    assert "missing_fields_report" in result
    assert "status" in result

    # Check explicitly generated invoice_id even for drafts
    assert result["invoice_id"] is not None
    assert result["status"] == "draft"

    # Validate types explicitly
    assert isinstance(result["invoice"], dict)
    assert isinstance(result["missing_fields_report"]["missing_invoice_fields"], list)

    # Optional field validation explicitly (adapt as needed based on sample data)
    assert result["invoice"]["id"] == result["invoice_id"]

    # Print result explicitly for debugging
    print("\nAPI Response (XML):")
    print(json.dumps(result, indent=2))

def test_order_upload_invalid_file_type():
    """
    Test upload with unsupported file type returns 415 error.
    """
    response = client.post(
        "/v1/user/invoices/upload",
        files={"file": ("order.txt", b"Random Text", "text/plain")},
        headers={"Authorization": "Bearer test-token"}
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported file type. Only XML and JSON are supported."
