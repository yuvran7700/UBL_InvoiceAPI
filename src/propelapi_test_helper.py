
# tests/utils/propel_api_helper.py
from fastapi import APIRouter
from src.dependencies.auth_client import auth_client

# --------------------------------------------
# Helper function to create test tokens
# --------------------------------------------
def create_test_access_token(user_id: str, active_org_id: str = None, duration_in_minutes: int = 60):
    token_response = auth_client.create_access_token(
        user_id=user_id,
        duration_in_minutes=duration_in_minutes,
        active_org_id=active_org_id  # Optional: sets active org if multi-tenant
    )
    return token_response.access_token

# --------------------------------------------
# FastAPI Router for testing
# --------------------------------------------
test_router = APIRouter(
    prefix="/v1/test",
    tags=["Testing Utilities (Internal Only)"]
)

@test_router.get("/generate-token")
def generate_token(user_id: str, org_id: str = None):
    """
    Generate a test access token for a user/org combo.

    **Usage Instructions:**

    - **User ID**: `ac5b71f7-f6f1-422c-9b47-f5ac9cbb81ed`
    - **Organisation ID**: `7303f5fd-063b-41bc-85ae-cc21b3676688`

    **Returns:**

    - JWT Access Token → COPY PASTE THIS TOKEN INTO THE AUTHORIZATION HEADER
    """
    token = create_test_access_token(user_id=user_id, active_org_id=org_id)
    return {"access_token": token}
