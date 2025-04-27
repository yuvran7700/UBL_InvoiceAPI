# tests/integration/test_email_routes/test_send_email.py

import pytest
import copy
from fastapi.testclient import TestClient
from src.testing_main import app

client = TestClient(app)

@pytest.mark.integration
def test_email_missing_fields(sample_email_missing_fields_xml, sample_invoice_json):
    organisation_id = "test-org-id"

    payload = copy.deepcopy(sample_invoice_json)
    complete_response = client.post(f"/v2/invoices/{organisation_id}/complete", json=payload)
    assert complete_response.status_code == 200
    invoice_id = complete_response.json()["invoice_id"]

    response = client.post(f"/v1/email/{organisation_id}/{invoice_id}/send", json=sample_email_missing_fields_xml)
    assert response.status_code == 422

    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "missing_email_fields"
    assert "Missing required fields" in body["error"]["message"]  # <-- Change this line


@pytest.mark.integration
def test_email_invalid_file_type(sample_email_invalid_filetype, sample_invoice_json):
    organisation_id = "test-org-id"

    payload = copy.deepcopy(sample_invoice_json)
    complete_response = client.post(f"/v2/invoices/{organisation_id}/complete", json=payload)
    assert complete_response.status_code == 200
    invoice_id = complete_response.json()["invoice_id"]

    response = client.post(f"/v1/email/{organisation_id}/{invoice_id}/send", json=sample_email_invalid_filetype)
    assert response.status_code == 415

    body = response.json()
    assert body["error"]["code"] == "invalid_email_filetype"

@pytest.mark.integration
def test_email_not_complete(sample_email_not_complete, sample_order_json):
    organisation_id = "test-org-id"

    upload_response = client.post(
        f"/v2/invoices/{organisation_id}/upload",
        files={"file": ("order.json", sample_order_json, "application/json")}
    )
    assert upload_response.status_code == 200
    invoice_id = upload_response.json()["invoice_id"]

    response = client.post(f"/v1/email/{organisation_id}/{invoice_id}/send", json=sample_email_not_complete)
    assert response.status_code == 400

    body = response.json()
    assert body["error"]["code"] == "email_not_allowed"

@pytest.mark.integration
def test_email_json_success(sample_email_json, sample_invoice_json):
    organisation_id = "test-org-id"

    payload = copy.deepcopy(sample_invoice_json)
    complete_response = client.post(f"/v2/invoices/{organisation_id}/complete", json=payload)
    assert complete_response.status_code == 200
    invoice_id = complete_response.json()["invoice_id"]

    response = client.post(f"/v1/email/{organisation_id}/{invoice_id}/send", json=sample_email_json)
    assert response.status_code == 202

@pytest.mark.integration
def test_email_xml_success(sample_email_xml, sample_invoice_json):
    organisation_id = "test-org-id"

    payload = copy.deepcopy(sample_invoice_json)
    complete_response = client.post(f"/v2/invoices/{organisation_id}/complete", json=payload)
    assert complete_response.status_code == 200
    invoice_id = complete_response.json()["invoice_id"]

    response = client.post(f"/v1/email/{organisation_id}/{invoice_id}/send", json=sample_email_xml)
    assert response.status_code == 202




@pytest.mark.integration
def test_multiple_recipients_json(sample_email_multiple_recipients_json, sample_invoice_json):
    organisation_id = "test-org-id"

    payload = copy.deepcopy(sample_invoice_json)
    complete_response = client.post(f"/v2/invoices/{organisation_id}/complete", json=payload)
    assert complete_response.status_code == 200
    invoice_id = complete_response.json()["invoice_id"]

    response = client.post(f"/v1/email/{organisation_id}/{invoice_id}/send", json=sample_email_multiple_recipients_json)
    assert response.status_code == 202
