import os
import pytest
import copy
from fastapi.testclient import TestClient
from src.testing_main import app

client = TestClient(app)

@pytest.mark.integration
def test_download_invoice_pdf_success(sample_invoice_json):
    """
    Test completing and downloading an invoice in PDF format.
    """

    organisation_id = "test-org-id"

    # Complete the invoice
    payload = copy.deepcopy(sample_invoice_json)
    complete_response = client.post(f"/v2/invoices/{organisation_id}/complete", json=payload)
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    invoice_id = complete_data["invoice_id"]


    # Download formatted PDF
    response = client.get(f"/v2/invoices/{organisation_id}/{invoice_id}/formatted-download")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert f"filename={invoice_id}.pdf" in response.headers["Content-Disposition"]


    print("\n✅ PDF Download Response Content:\n")
    print(response.content[:100])

    

    with open("tmp_download_pdf.pdf", "wb") as f:
        f.write(response.content)




"""

@pytest.mark.integration
def test_download_invoice_pdf_success(sample_invoice_json):

    #Test completing and downloading a formatted invoice in PDF format.

    organisation_id = "test-org-id"

    # Complete the invoice
    payload = copy.deepcopy(sample_invoice_json)
    complete_response = client.post(f"/v2/invoices/{organisation_id}/complete", json=payload)
    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    invoice_id = complete_data["invoice_id"]

    # Download formatted PDF
    response = client.get(f"/v2/invoices/{organisation_id}/{invoice_id}/formatted-download")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"
    assert f"filename={invoice_id}.pdf" in response.headers["Content-Disposition"]

    print("\n✅ PDF Download Response Content (first 100 bytes):\n")
    print(response.content[:100])

    # Optionally save it to a temporary file for debugging
    with open("tmp_download_pdf.pdf", "wb") as f:
        f.write(response.content)

 """