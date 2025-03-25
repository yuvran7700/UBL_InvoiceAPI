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
from tests.fixtures.user_fixtures import sample_user_json  # noqa: F401
from tests.fixtures.session_fixtures import sample_session_json # noqa: F401
from tests.fixtures.data_fixtures import sample_order_xml, sample_order_json, sample_invoice_xml, sample_invoice_json, sample_invalid_invoice_json  # noqa: F401

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
