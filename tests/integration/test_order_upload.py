from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_upload_order(sample_order_xml):
    """
    Test that the upload route processes the sample order XML correctly,
    maps the fields as expected, and returns a draft invoice.
    """
    files = {
        "file": ("example_order.xml", sample_order_xml, "application/xml")
    }
    response = client.post("/v1/admin/order/upload", files=files)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    data = response.json()
    # Check that an invoice_id (our partition key) is present.
    assert "invoice_id" in data, "Missing invoice_id in response"
    
    # Validate that the order_reference was correctly mapped from the order XML.
    # According to your example_order.xml, order_id is "AEG012345".
    assert data["order_reference"] == "AEG012345", f"Unexpected order_reference: {data['order_reference']}"
    
    # Validate that buyer_reference was mapped correctly from the SalesOrderID.
    # In your example_order.xml, SalesOrderID is "CON0095678".
    assert data["buyer_reference"] == "CON0095678", f"Unexpected buyer_reference: {data['buyer_reference']}"
    
    # Verify that invoice_lines are present and contain at least one line.
    assert "invoice_lines" in data, "Missing invoice_lines in response"
    assert isinstance(data["invoice_lines"], list) and len(data["invoice_lines"]) >= 1, "Invoice lines not properly mapped"
