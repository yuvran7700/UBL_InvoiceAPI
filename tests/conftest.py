# tests/conftest.py
import sys
import os
import pytest

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fixtures.user_fixtures import sample_user_json