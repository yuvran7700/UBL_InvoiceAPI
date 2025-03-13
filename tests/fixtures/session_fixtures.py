import pytest
import json
import os

# Define the path to the session data JSON file
SESSION_DATA_PATH = os.path.join(os.path.dirname(__file__), '../../test_data/session.json')

@pytest.fixture
def sample_session():
    """Fixture to load sample session data from the JSON file."""
    with open(SESSION_DATA_PATH, 'r') as file:
        session_data = json.load(file)
    return session_data
