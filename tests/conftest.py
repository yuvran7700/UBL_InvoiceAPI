# tests/conftest.py
import sys
import pytest

from fixtures.user_fixtures import sample_user_json

# Re-export the fixture
sample_user_json = pytest.fixture(sample_user_json)