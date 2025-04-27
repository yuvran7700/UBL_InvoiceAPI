import pytest
import json
from fastapi.testclient import TestClient
from src.testing_main import app

client = TestClient(app)

@pytest.mark.integration
def test_order_upload_json_success(sample_order_upload_json):
    """
    Test successful JSON order upload and draft invoice generation.
    """
    organisation_id = "test-org-id"

    response = client.post(
        f"/v2/orders/{organisation_id}/upload",
        files={"file": ("order.json", sample_order_upload_json, "application/json")},
    )

    assert response.status_code == 200
    result = response.json()

    # Validate unified API response structure
    assert "invoice_id" in result
    assert "invoice" in result
    assert "missing_fields_report" in result
    assert "status" in result

    assert result["invoice_id"] is not None
    assert result["status"] == "draft"

    assert isinstance(result["invoice"], dict)
    assert isinstance(result["missing_fields_report"]["missing_invoice_fields"], list)
    assert isinstance(result["missing_fields_report"]["missing_invoice_lines"], list)

    # Optional field check
    assert result["invoice"]["invoice_id"] == result["invoice_id"]

    print("\n✅ API Response (Draft Invoice Generated from Order):")
    print(json.dumps(result, indent=2))


@pytest.mark.integration
def test_order_upload_missing_fields(sample_order_missing_fields):
    """
    Test upload of an order missing required fields should return validation error.
    """
    organisation_id = "test-org-id"

    response = client.post(
        f"/v2/orders/{organisation_id}/upload",
        files={"file": ("order.json", sample_order_missing_fields, "application/json")},
    )

    assert response.status_code == 400
    result = response.json()

    assert "error" in result
    assert result["error"]["message"].startswith('{"error":"Validation Error')
    
    print("\n✅ Missing Field Error Response:")
    print(json.dumps(result, indent=2))


@pytest.mark.integration
def test_order_upload_empty(sample_order_upload_empty):
    """
    Test upload of an empty order file should return error.
    """
    organisation_id = "test-org-id"

    response = client.post(
        f"/v2/orders/{organisation_id}/upload",
        files={"file": ("order.json", sample_order_upload_empty, "application/json")},
    )

    assert response.status_code == 400
    result = response.json()

    assert "error" in result
    assert result["error"]["message"] == "Uploaded file is empty."

    print("\n✅ Empty File Upload Error Response:")
    print(json.dumps(result, indent=2))


@pytest.mark.integration
def test_order_upload_invalid_format(sample_order_upload_wrong_format):
    """
    Test upload of wrong file type (XML) for order upload.
    """
    organisation_id = "test-org-id"

    response = client.post(
        f"/v2/orders/{organisation_id}/upload",
        files={"file": ("order.xml", sample_order_upload_wrong_format, "application/xml")},
    )

    assert response.status_code == 415
    result = response.json()

    assert result["error"]["code"] == "invalid_invoice_format"
    assert result["error"]["message"] == "Unsupported file type. Only JSON are supported for order upload."

    print("\n✅ Invalid File Format Error Response:")
    print(json.dumps(result, indent=2))
