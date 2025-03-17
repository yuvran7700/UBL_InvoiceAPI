import pytest
from src.services.user_service import create_user
from src.utils.user_helpers import hash_password
from src.validators.user_validator import validate_abn, validate_password
from tests.conftest import sample_user_json

@pytest.mark.unit
def test_user_in_db_map_sucess(sample_user_json):
    user_in_db = create_user(sample_user_json)
    assert user_in_db is not None
    assert user_in_db.email == sample_user_json["email"]
    assert user_in_db.businessName == sample_user_json["businessName"]
    assert user_in_db.abn == sample_user_json["abn"]
    assert user_in_db.hashed_password is not None

@pytest.mark.unit
def test_invalid_abn():
    """
    Test that the user registration endpoint correctly handles an invalid ABN.
    """  
    invalid_abn = '12345678901'
    assert validate_abn(invalid_abn) == "Invalid ABN format"

@pytest.mark.unit
def test_invalid_password(): 
    ''' Test that the password function returns correct error messages'''
    assert validate_password('paAsw1') == "Password must be at least 8 characters long"
    assert validate_password('')

@pytest.mark.unit
def test_password_hashed(sample_user_json):
    """
    Test that the user registration endpoint correctly hashes the user's password.
    """
    password = sample_user_json['password'] 
    hashed_password = hash_password(password)
    assert password != hashed_password