import copy
import pytest
import io
import json

def test_complete_invoice_success(client, sample_invoice_json):
    """
    Test completing a valid invoice successfully via /v2/invoices/{org_id}/complete
    """
    org_id = "test-org-id"
    complete_url = f"/v2/invoices/{org_id}/complete"

    payload = copy.deepcopy(sample_invoice_json)

    response = client.post(
        complete_url,
        json=payload,
    )

    print("\nCompleted Invoice Response:")
    print(json.dumps(response.json(), indent=2))

    assert response.status_code == 200
    data = response.json()

    # Unified response structure
    assert "invoice_id" in data
    assert "invoice" in data
    assert "status" in data
    assert data["status"] == "completed"
    assert data["missing_fields_report"] is None
