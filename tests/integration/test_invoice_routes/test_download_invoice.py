# tests/integration/test_invoice_routes/test_download_invoice.py

import pytest
import copy
from fastapi.testclient import TestClient
from src.testing_main import app

client = TestClient(app)


@pytest.mark.integration
def test_download_invoice_json_success(sample_invoice_json):
    """
    Test completing and downloading an invoice in JSON format.
    """
    organisation_id = "test-org-id"

    payload = copy.deepcopy(sample_invoice_json)

    # Complete the invoice
    complete_response = client.post(f"/v2/invoices/{organisation_id}/complete", json=payload)
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    invoice_id = complete_data["invoice_id"]

    # Download as JSON
    response = client.get(f"/v2/invoices/{organisation_id}/{invoice_id}/download?format=json")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert f"filename={invoice_id}.json" in response.headers["Content-Disposition"]
    assert b"invoice_id" in response.content

    print("\n✅ JSON Download Response Content:\n")
    print(response.content.decode("utf-8"))

    with open("tmp_download_json.json", "wb") as f:
        f.write(response.content)


@pytest.mark.integration
def test_download_invoice_xml_success(sample_invoice_json):
    """
    Test completing and downloading an invoice in XML format.
    """
    organisation_id = "test-org-id"

    payload = copy.deepcopy(sample_invoice_json)

    # Complete the invoice
    complete_response = client.post(f"/v2/invoices/{organisation_id}/complete", json=payload)
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    invoice_id = complete_data["invoice_id"]

    # Download as XML
    response = client.get(f"/v2/invoices/{organisation_id}/{invoice_id}/download?format=xml")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/xml"
    assert f"filename={invoice_id}.xml" in response.headers["Content-Disposition"]
    assert b"<Invoice" in response.content

    print("\n✅ XML Download Response Content:\n")
    print(response.content.decode("utf-8"))

    with open("tmp_download_xml.xml", "wb") as f:
        f.write(response.content)
