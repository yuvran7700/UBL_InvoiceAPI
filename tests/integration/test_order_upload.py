from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_upload_order(sample_order_xml):
    """
    Test that the upload route processes the sample order XML correctly,
    maps the fields as expected using the new naming conventions (order_reference and buyer_reference),
    and returns a draft invoice with invoice_lines.
    """
    files = {
        "file": ("example_order.xml", sample_order_xml, "application/xml")
    }
    response = client.post("/v1/admin/order/upload", files=files)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    data = response.json()
    # Check that an invoice_id is present.
    assert "invoice_id" in data, "Missing invoice_id in response"
    
    # Check nested order data.
    assert "order" in data, "Missing order data in invoice response"
    order_data = data["order"]
    
    # Validate that order_reference and buyer_reference are mapped correctly.
    assert order_data.get("order_reference") == "AEG012345", f"Unexpected order_reference: {order_data.get('order_reference')}"
    assert order_data.get("buyer_reference") == "CON0095678", f"Unexpected buyer_reference: {order_data.get('buyer_reference')}"
    
    # Verify that invoice_lines are present and contain at least one line.
    assert "invoice_lines" in order_data, "Missing invoice_lines in order data"
    invoice_lines = order_data["invoice_lines"]
    assert isinstance(invoice_lines, list) and len(invoice_lines) > 0, "No invoice lines found in order data"
