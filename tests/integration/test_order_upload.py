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
    
    # Since InvoiceType now includes OrderType via composition,
    # check the nested order fields instead of top-level fields.
    assert "order" in data, "Missing order data in invoice response"
    order_data = data["order"]
    
    # Validate that the order_id was correctly mapped.
    assert order_data.get("order_id") == "AEG012345", f"Unexpected order_id: {order_data.get('order_id')}"
    
    # Validate that the sales_order_id (acting as buyer reference) was mapped correctly.
    assert order_data.get("sales_order_id") == "CON0095678", f"Unexpected sales_order_id: {order_data.get('sales_order_id')}"
    
    # Verify that invoice_lines are present and contain at least one line.
    #assert "invoice_lines" in data, "Missing invoice_lines in response"
    #assert isinstance(data["invoice_lines"], list) and len(data["invoice_lines"]) >= 1, "Invoice lines not properly mapped"
