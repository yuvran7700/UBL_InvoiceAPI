"""
This file contains unit tests for the user registration logic i.e., model mapping and conversions.

Modules Tested:
    UserIn, UserInDB, create_user, hash_password, validate_abn, validate_password

"""
from fastapi import HTTPException
import pytest
from src.models.user_models import UserIn, UserInDB
from src.services.user_service import create_user
from src.utils.user_helpers import hash_password
from src.validators.user_validator import validate_abn, validate_password
from tests.conftest import sample_user_json


@pytest.mark.unit
def test_user_in_db_map_sucess(sample_user_json):
    user_in = UserIn(**sample_user_json)
    user_id = "142562728920"
    fake_hashed_password = "hhh77snn09"

    user_in_db = UserInDB(
        business_name=user_in.business_name,
        email=user_in.email,
        hashed_password=fake_hashed_password,
        abn=user_in.abn,
        user_id=user_id,
    )

    print(user_in_db.json())
    assert user_in_db is not None
    assert user_in_db.email == sample_user_json["email"]
    assert user_in_db.business_name == sample_user_json["business_name"]
    assert user_in_db.abn == sample_user_json["abn"]
    assert user_in_db.hashed_password == fake_hashed_password
    assert user_in_db.user_id == user_id


@pytest.mark.convert
def test_model_to_dict_conversion(sample_user_json):
    user_in = UserIn(**sample_user_json)
    user_id = "142562728920"
    fake_hashed_password = "hhh77snn09"

    user_in_db = UserInDB(
        business_name=user_in.business_name,
        email=user_in.email,
        hashed_password=fake_hashed_password,
        abn=user_in.abn,
        user_id=user_id,
    )

    user = user_in_db
    user_dict = user.dict()

    result = {
        "business_name": "Test1 Business",
        "email": "test1@example.com",
        "hashed_password": "hhh77snn09",
        "abn": "51824753556",
        "user_id": "142562728920",
    }

    # Assert that the dictionary matches the expected output
    assert user_dict == result


@pytest.mark.unit
def test_invalid_abn():
    """
    Test that the ABN validation correctly handles an invalid ABN.
    """
    invalid_abn = "12345678901"

    # Assuming validate_abn raises HTTPException when ABN is invalid
    with pytest.raises(HTTPException) as exc_info:
        validate_abn(invalid_abn)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid ABN format"


@pytest.mark.unit
def test_invalid_password():
    """Test that the password function returns correct error messages"""
    with pytest.raises(HTTPException) as exc_info:
        validate_password("paAsw1")  # Password is too short
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must be at least 8 characters long"

    # Test for empty password
    with pytest.raises(HTTPException) as exc_info:
        validate_password("")  # Empty password is invalid
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must be at least 8 characters long"

    # Test for password without a number
    with pytest.raises(HTTPException) as exc_info:
        validate_password("PasswordWithoutNumber")  # No digits in password
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Password must contain at least one number"

    # Test for password without an uppercase letter
    with pytest.raises(HTTPException) as exc_info:
        validate_password("password1")  # No uppercase letter
    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail == "Password must contain at least one uppercase letter"
    )

    # Test for password without a lowercase letter
    with pytest.raises(HTTPException) as exc_info:
        validate_password("PASSWORD1")  # No lowercase letter
    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail == "Password must contain at least one lowercase letter"
    )


@pytest.mark.unit
def test_password_hashed(sample_user_json):
    """
    Test that the user registration endpoint correctly hashes the user's password.
    """
    password = sample_user_json["password"]
    hashed_password = hash_password(password)
    assert password != hashed_password
