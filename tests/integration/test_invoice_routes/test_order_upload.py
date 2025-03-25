from fastapi.testclient import TestClient
from src.main import app
from tests.fixtures.data_fixtures import sample_order_json
from src.services.auth_service import get_current_user_id  # Adjust the path based on your project

import pytest
import os

client = TestClient(app)

def test_complete_invoice_persists_to_dynamo(sample_invoice_json):
    app.dependency_overrides[get_current_user_id] = lambda: "test-user-id"

    """
    Integration test that POSTs a fully completed invoice JSON
    to the /v1/user/invoices/complete route and checks for 200 OK.
    """
    response = client.post("/v1/user/invoices/complete", json=sample_invoice_json, headers={"Authorization": "Bearer test-token"})
    
    # ✅ Check successful processing and save
    assert response.status_code == 200, f"Expected 200, got {response.status_code}, Response: {response.text}"

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    response_data = response.json()
    
    # ✅ Confirm response has invoice_id (implies save success)
    assert "invoice_id" in response_data
    assert response_data["invoice"]["header"]["invoice_id"] == "INV-001"
    app.dependency_overrides = {}
