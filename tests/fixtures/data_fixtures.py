#tests/fixtures/data_fixtures

import os
import pytest

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
