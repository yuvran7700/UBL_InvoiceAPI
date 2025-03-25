#tests/fixtures/data_fixtures

import os
import pytest
import json


@pytest.fixture
def sample_order_xml():
    """
    Loads the sample UBL XML file from the test_data folder.
    Ensures it works regardless of the test execution directory.
    """
    # __file__ is in tests/fixtures, so we go up three levels to reach the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, "test_data", "example_order.xml")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "rb") as f:
        return f.read()
    
@pytest.fixture
def sample_order_json():
    """
    Loads the sample UBL JSON file from the test_data folder.
    Ensures it works regardless of the test execution directory.
    """
    # __file__ is in tests/fixtures, so we go up three levels to reach the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, "test_data", "example_order.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "rb") as f:
        return f.read()
    
@pytest.fixture
def sample_invoice_xml():
    """
    Loads the sample UBL XML file from the test_data folder.
    Ensures it works regardless of the test execution directory.
    """
    # __file__ is in tests/fixtures, so we go up three levels to reach the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, "test_data", "example_invoice.xml")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "rb") as f:
        return f.read()
    
@pytest.fixture
def sample_invoice_json():
    """
    Loads the valid sample invoice JSON data for validator tests.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, "test_data", "valid_invoice.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "r") as f:
        return json.load(f)

@pytest.fixture
def sample_invalid_invoice_json():
    """
    Loads the valid sample invoice JSON data for validator tests.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, "test_data", "invalid_invoice.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "r") as f:
        return json.load(f)
