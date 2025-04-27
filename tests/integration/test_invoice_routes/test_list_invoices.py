import io
import json
from datetime import datetime, timedelta

def test_list_invoices_basic(client, sample_order_xml):
    """
    Upload a draft invoice and verify it appears in the list of invoices for the organisation.
    """

    organisation_id = "test-org-id"

    # Step 1: Upload a draft invoice
    upload_url = f"/v2/invoices/{organisation_id}/upload"
    files = {
        "file": ("sample_order.xml", io.BytesIO(sample_order_xml), "application/xml")
    }

    upload_response = client.post(upload_url, files=files)
    assert upload_response.status_code == 200, upload_response.text

    uploaded_invoice = upload_response.json()
    invoice_id = uploaded_invoice["invoice_id"]

    # Step 2: List invoices without any filters
    list_url = f"/v2/invoices/{organisation_id}"
    list_response = client.get(list_url)
    assert list_response.status_code == 200, list_response.text

    invoices = list_response.json()
    print("\nList All Invoices Response:")
    print(json.dumps(invoices, indent=2))

    # Check that uploaded invoice appears in the list
    assert any(invoice["invoice_id"] == invoice_id for invoice in invoices)

    # Step 3: List invoices filtered by status=draft
    list_response_status = client.get(list_url, params={"status": "draft"})
    assert list_response_status.status_code == 200, list_response_status.text

    invoices_status = list_response_status.json()
    print("\nList Invoices with status=draft Response:")
    print(json.dumps(invoices_status, indent=2))

    # Should find the invoice
    assert any(invoice["invoice_id"] == invoice_id for invoice in invoices_status)

    # Step 4: List invoices filtered by issue_date_from
    old_date = datetime(2000, 1, 1).date()  # <<< earlier than 2005

    list_response_date = client.get(list_url, params={"issue_date_from": old_date.isoformat()})
    assert list_response_date.status_code == 200, list_response_date.text

    invoices_date = list_response_date.json()
    print("\nList Invoices with issue_date_from filter Response:")
    print(json.dumps(invoices_date, indent=2))

    assert any(invoice["invoice_id"] == invoice_id for invoice in invoices_date)

