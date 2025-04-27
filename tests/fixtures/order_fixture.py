#tests/fixtures/order_fixtures

import os
import pytest
import json

@pytest.fixture
def sample_order_upload_json():
    """
    Loads the sample UBL JSON file from the test_data folder.
    Ensures it works regardless of the test execution directory.
    """
    # __file__ is in tests/fixtures, so we go up three levels to reach the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, "test_data", "sample_order_order_route.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "rb") as f:
        return f.read()
    
@pytest.fixture
def sample_order_upload_wrong_format():
    """
    Loads the sample UBL XML file from the test_data folder.
    Ensures it rejects format.
    """
    # __file__ is in tests/fixtures, so we go up three levels to reach the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, "test_data", "sample_order_order_route_xml.xml")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "rb") as f:
        return f.read()

@pytest.fixture
def sample_order_upload_empty():
    """
    Loads the empty JSON file from the test_data folder.
    Ensures it fails due to being empty.
    """
    # __file__ is in tests/fixtures, so we go up three levels to reach the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, "test_data", "empty.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "rb") as f:
        return f.read()
    
@pytest.fixture
def sample_order_missing_fields():
    """
    Loads the empty JSON file from the test_data folder.
    Ensures it fails due to being empty.
    """
    # __file__ is in tests/fixtures, so we go up three levels to reach the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, "test_data", "sample_order_missing_fields.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "rb") as f:
        return f.read()
    