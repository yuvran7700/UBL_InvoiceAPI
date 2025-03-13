#tests/fixtures/user_fixtures

import os
import pytest
import json

@pytest.fixture
def sample_user_json():
    """
    Loads the sample user data JSON file from the test_data folder.
    Ensures it works regardless of the test execution directory.
    """
    # __file__ is in tests/fixtures, so we go up three levels to reach the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(project_root, "test_data", "user.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test data file not found: {file_path}")

    with open(file_path, "r") as f:
        return f.read()