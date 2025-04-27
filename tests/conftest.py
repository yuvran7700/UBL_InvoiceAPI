# tests/conftest.py

"""This file modifies the Python path to include the project root, ensuring that the tests can 
access the necessary modules from the root of the project.

Modules imported here will be available across all test modules without needing to adjust 
the PYTHONPATH environment variable.

Usage:
- Automatically adds the project root to the Python path before running tests, so that import
 statements can reference the project's modules.
"""

import sys
import os
import pytest

from fastapi.testclient import TestClient
from src.testing_main import app  # your lightweight testing app
from src.dependencies.auth import check_permission, auth  # ✅ import auth
from tests.fixtures.user_fixtures import sample_user_json  # noqa
from tests.fixtures.session_fixtures import sample_session_json  # noqa
from tests.fixtures.data_fixtures import (
    sample_order_xml,
    sample_order_json,
    sample_invoice_xml,
    sample_invoice_json,
    valid_token
)
from tests.fixtures.email_fixture import (
    sample_email_json,
    sample_email_xml,
    sample_email_pdf,
    sample_email_missing_fields_xml,
    sample_email_invalid_filetype,
    sample_email_not_complete,
    sample_email_multiple_recipients_json)

from tests.fixtures.order_fixture import (
    sample_order_upload_json,
    sample_order_upload_wrong_format,
    sample_order_upload_empty,
    sample_order_missing_fields
)

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class FakeOrgMembership:
    def __init__(self, org_id: str, role: str = "Admin"):
        self.org_id = org_id
        self.user_assigned_role = role
        self.org_name = f"Fake Org {org_id}"

class FakeUser:
    def __init__(self, user_id="test-user-id", org_memberships=None):
        self.user_id = user_id
        self.email = f"{user_id}@example.com"
        self.first_name = "Test"
        self.last_name = "User"
        self.org_memberships = org_memberships or []

    def get_org(self, org_id):
        for org in self.org_memberships:
            if org.org_id == org_id:
                return org
        return None

    def get_orgs(self):
        return self.org_memberships
    
@pytest.fixture(autouse=True)
def override_auth_and_permission_dependency():
    """
    Overrides both:
    - PropelAuth auth.require_user
    - check_permission
    to inject FakeUser during tests.
    """
    fake_orgs = [FakeOrgMembership(org_id="test-org-id", role="Admin")]

    #app.dependency_overrides[check_permission] = lambda: lambda org_id: FakeUser(org_memberships=fake_orgs)
    app.dependency_overrides[check_permission] = lambda: FakeUser(org_memberships=fake_orgs)
    app.dependency_overrides[auth.require_user] = lambda: FakeUser(org_memberships=fake_orgs)
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client():
    return TestClient(app)
