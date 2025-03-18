import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.repositories.user_repository import delete_all_users, get_user
from src.utils.user_helpers import  verify_password
from tests.conftest import sample_user_json

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_database():
    """
    Fixture to clean up the database before and after each test
    """
    delete_all_users()  # Clean before test
    yield
    delete_all_users()   # Clean after test

@pytest.mark.user_db_tests
def test_user_registration1(sample_user_json):
    """
    Test the full registration process, including validating the user in DynamoDB.
    """
    # Make the API request to register the user
    response = client.post("/v1/users/register", json=sample_user_json)

    # Assert the API responds with a success status code 201
    assert response.status_code == 200
    user = response.json()

    # Check that the response contains user data (matching UserOut model)
    assert user["email"] == sample_user_json["email"]
    assert user["business_name"] == sample_user_json["business_name"]
    assert user["abn"] == sample_user_json["abn"]
    assert "user_id" not in user  
    assert "password" not in user  

    # Ensure the user is correctly stored in the database with hashed password
    user_in_db = get_user(sample_user_json["email"])
    #convert UserInDB model into json
    stored_user = user_in_db.model_dump()
    assert stored_user is not None
    assert stored_user["email"] == sample_user_json["email"]
    assert stored_user["business_name"] == sample_user_json["business_name"]
    assert stored_user["abn"] == sample_user_json["abn"]
    assert "hashed_password" in stored_user  # Check that the password is hashed
    assert "user_id" in stored_user  # Ensure that user_id is stored in the database
