import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_liveness_check():
    response = client.get("/health/live")
    
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_readiness_check_ready():
    # Simulate the state where all subsystems are ready
    response = client.get("/health/ready")

    app.state.health_service.set_ready("dynamo.users", True)
    app.state.health_service.set_ready("dynamo.invoices", True)
    app.state.health_service.set_ready("dynamo.sessions", True)

    response = client.get("/health/ready")
    assert response.status_code == 200


def test_readiness_check_not_ready():

    app.state.health_service.set_ready("dynamo.users", False)
    app.state.health_service.set_ready("dynamo.invoices", False)
    app.state.health_service.set_ready("dynamo.sessions", False)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "details": {
            "dynamo.users": False,
            "dynamo.invoices": False,
            "dynamo.sessions": False,
            "external_ready": True,
        }
    }

def test_readiness_check_partial_ready():
    # Set some subsystems ready, but not all
    app.state.health_service.set_ready("dynamo.users", True)
    app.state.health_service.set_ready("dynamo.invoices", True)
    app.state.health_service.set_ready("dynamo.sessions", False)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "details": {
            "dynamo.users": True,
            "dynamo.invoices": True,
            "dynamo.sessions": False,
            "external_ready": True,
        }
    }
