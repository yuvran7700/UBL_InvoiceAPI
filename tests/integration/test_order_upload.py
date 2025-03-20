from fastapi.testclient import TestClient
from src.main import app
from tests.fixtures.data_fixtures import sample_order_json
import pytest
import os

client = TestClient(app)

def test_upload_order(sample_order_json):
    """
    Test that the upload route processes the sample order XML correctly,
    maps the fields as expected using the new naming conventions (order_reference and buyer_reference),
    and returns a draft invoice with invoice_lines.
    """
    files = {
        "file": ("example_order.json", sample_order_json, "application/json")
    }
    response = client.post("/v1/admin/order/upload", files=files)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    
    data = response.json()

    # Validate the Invoice fields (partial checks)
    assert data["header"]["customization_id"] == "urn:oasis:names:specification:ubl:xpath:Order-2.0:sbs-1.0-draft"
    assert data["supplier_party"]["party_name"] == "Consortial"
    assert data["customer_party"]["party_name"] == "IYT Corporation"
    assert len(data["invoice_lines"]) == 1
    assert data["invoice_lines"][0]["item"]["name"] == "beeswax"
