# tests/conftest.py
import sys
import os
from tests.fixtures.user_fixtures import sample_user_json  # noqa: F401


# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)