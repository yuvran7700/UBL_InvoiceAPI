# tests/integration/test_invoice_routes/test_download_invoice.py

import pytest
import copy
from fastapi.testclient import TestClient
from src.main import app
from src.services.auth_service import get_current_user_id

# Override auth for test isolation
app.dependency_overrides[get_current_user_id] = lambda: "test-user"
client = TestClient(app)


@pytest.mark.integration
def test_download_invoice_json_success(sample_invoice_json):
    """
    Test completing and downloading an invoice in JSON format.
    """
    payload = copy.deepcopy(sample_invoice_json)

    # Complete invoice
    complete_response = client.post("/v1/user/invoices/complete", json=payload)
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    invoice_id = complete_data["invoice_id"]

    # Download as JSON
    response = client.get(f"/v1/user/invoices/{invoice_id}/download?format=json")
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
    payload = copy.deepcopy(sample_invoice_json)

    # Complete invoice
    complete_response = client.post("/v1/user/invoices/complete", json=payload)
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    invoice_id = complete_data["invoice_id"]

    # Download as XML
    response = client.get(f"/v1/user/invoices/{invoice_id}/download?format=xml")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/xml"
    assert f"filename={invoice_id}.xml" in response.headers["Content-Disposition"]
    assert b"<Invoice" in response.content

    print("\n✅ XML Download Response Content:\n")
    print(response.content.decode("utf-8"))

    with open("tmp_download_xml.xml", "wb") as f:
        f.write(response.content)
