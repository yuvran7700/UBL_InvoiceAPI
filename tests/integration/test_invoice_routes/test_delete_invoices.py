import io
import json

def test_delete_invoice_success(client, sample_order_xml):
    """
    Upload a draft invoice, delete it, and verify it is deleted successfully.
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

    # Step 2: Confirm invoice is retrievable
    get_url = f"/v2/invoices/{organisation_id}/{invoice_id}"
    get_response = client.get(get_url)
    assert get_response.status_code == 200, get_response.text

    # Step 3: Delete the invoice
    delete_url = f"/v2/invoices/{organisation_id}"
    delete_payload = {
        "invoice_ids": [invoice_id]
    }

    delete_response = client.request("DELETE", delete_url, json=delete_payload)

    assert delete_response.status_code == 200, delete_response.text

    delete_result = delete_response.json()
    print("\nDelete Invoices Response:")
    print(json.dumps(delete_result, indent=2))

    assert invoice_id in delete_result["deleted"]
    assert delete_result["errors"] == []

    # Step 4: Confirm invoice no longer retrievable
    # Step 4: Confirm invoice no longer retrievable
    get_after_delete_response = client.get(get_url)
    assert get_after_delete_response.status_code == 404

