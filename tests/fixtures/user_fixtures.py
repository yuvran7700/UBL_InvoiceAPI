import pytest
import json
import os

# Define the path to the user data JSON file
USER_DATA_PATH = os.path.join(os.path.dirname(__file__), '../../test_data/user.json')

@pytest.fixture
def sample_user():
    """Fixture to load sample user data from the JSON file."""
    with open(USER_DATA_PATH, 'r') as file:
        user_data = json.load(file)
    return user_data
