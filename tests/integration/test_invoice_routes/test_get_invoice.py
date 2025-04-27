import io
import json

def test_get_draft_invoice_after_upload(client, sample_order_json):
    org_id = "test-org-id"

    upload_url = f"/v2/invoices/{org_id}/upload"
    files = {
        "file": ("order.json", io.BytesIO(sample_order_json), "application/json")
    }

    upload_response = client.post(upload_url, files=files)
    assert upload_response.status_code == 200
    draft = upload_response.json()

    invoice_id = draft["invoice_id"]
    assert invoice_id is not None
    assert draft["status"] == "draft"

    get_url = f"/v2/invoices/{org_id}/{invoice_id}"

    get_response = client.get(get_url)
    assert get_response.status_code == 200

    result = get_response.json()

    print("\nRetrieved Invoice:")
    print(json.dumps(result, indent=2))

    assert result["invoice_id"] == invoice_id
    assert result["status"] == "draft"
    assert "invoice" in result
