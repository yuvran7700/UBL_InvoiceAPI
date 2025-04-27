import io

def test_upload_invoice_success(client, sample_order_xml):
    org_id = "test-org-id"
    url = f"/v2/invoices/{org_id}/upload"

    files = {
        "file": ("sample_order.xml", io.BytesIO(sample_order_xml), "application/xml")
    }

    response = client.post(url, files=files)

    assert response.status_code == 200, response.text
    data = response.json()

    assert "invoice_id" in data
    assert "invoice" in data
    assert data["status"] == "draft"
    assert data["invoice"]["invoice_id"].startswith("INV-")
