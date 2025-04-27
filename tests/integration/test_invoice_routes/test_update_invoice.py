import io
import pytest
import json

@pytest.mark.integration
def test_update_invoice_success(client, sample_order_json):
    """
    Upload a draft invoice, update a field, and verify the update is reflected.
    """
    organisation_id = "test-org-id"

    # Step 1: Upload draft invoice
    upload_url = f"/v2/invoices/{organisation_id}/upload"
    files = {
        "file": ("order.json", io.BytesIO(sample_order_json), "application/json")
    }
    upload_response = client.post(upload_url, files=files)
    assert upload_response.status_code == 200
    draft_invoice = upload_response.json()
    invoice_id = draft_invoice["invoice_id"]

    # Step 2: Update the invoice (e.g., update buyer_reference)
    update_url = f"/v2/invoices/{organisation_id}/{invoice_id}"
    update_payload = {
        "buyer_reference": "UPDATED_REF"
    }
    update_response = client.patch(update_url, json=update_payload)
    assert update_response.status_code == 200
    updated_invoice = update_response.json()

    # Validate that buyer_reference was updated
    assert updated_invoice["invoice"]["buyer_reference"] == "UPDATED_REF"
    assert "missing_fields_report" in updated_invoice


@pytest.mark.integration
def test_update_invoice_not_found(client):
    """
    Try updating a non-existent invoice and expect 404.
    """
    organisation_id = "test-org-id"
    non_existent_invoice_id = "INV-NONEXISTENT"

    update_url = f"/v2/invoices/{organisation_id}/{non_existent_invoice_id}"
    update_payload = {"buyer_reference": "UPDATED_REF"}

    update_response = client.patch(update_url, json=update_payload)

    assert update_response.status_code == 404
    data = update_response.json()
    assert "error" in data or "detail" in data  # depends how your error handler formats it


@pytest.mark.integration
def test_update_completed_invoice(client, sample_invoice_json):
    """
    Upload and complete an invoice, then try updating it (should fail with 403).
    """
    organisation_id = "test-org-id"

    # Step 1: Complete an invoice
    complete_url = f"/v2/invoices/{organisation_id}/complete"
    complete_response = client.post(complete_url, json=sample_invoice_json)
    assert complete_response.status_code == 200
    completed_invoice = complete_response.json()
    invoice_id = completed_invoice["invoice_id"]

    # Step 2: Try updating the completed invoice
    update_url = f"/v2/invoices/{organisation_id}/{invoice_id}"
    update_payload = {
        "buyer_reference": "NEW_REF"
    }
    update_response = client.patch(update_url, json=update_payload)

    assert update_response.status_code == 403
    error = update_response.json()
    assert "error" in error or "detail" in error
