"""
src/routes/user_routes_v2.py
========================
User management routes for version 2 of the API.
Uses external authentication and user profile management via PropelAuth.
"""

from fastapi import APIRouter, Depends, HTTPException
from propelauth_fastapi import User
from src.dependencies.auth import auth  # Your auth instance (initialized from PropelAuth)

router = APIRouter(
    prefix="/v2/users",
    tags=["User Profile Management"],
)


@router.get("/me")
def get_user_profile(user: User = Depends(auth.require_user)):
    """
    Get information about the currently authenticated user.

    **Returns:**
    - `user_id`: ID of the authenticated user.
    - `email`: User's email address.
    - `full_name`: User's full name (if available).
    - `orgs`: List of organisations the user belongs to.
    """
    return {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": f"{user.first_name} {user.last_name}" if user.first_name else None,
        "orgs": user.get_orgs(),  # List of organizations the user belongs to
    }

@router.get("/me/orgs")
def list_user_orgs(user: User = Depends(auth.require_user)):
    """
    List all organisations the user is a member of.

    **Returns:**
    - A list of organisation names the user belongs to.
    """
    return [org.org_name for org in user.get_orgs()]

@router.get("/me/org/{org_id}")
def get_user_org_membership_details(org_id: str, user: User = Depends(auth.require_user)):
    """
    Get information about the user's membership in a specific organisation.

    **Args:**
    - `org_id` (str): The ID of the organisation.

    **Returns:**
    - `org_name`: Name of the organisation.
    - `my_role`: The user's assigned role within the organisation.

    **Raises:**
    - `HTTPException (403)`: If the user is not a member of the specified organisation.
    """
    org = user.get_org(org_id)
    if org is None:
        raise HTTPException(status_code=403, detail="Not a member of this organisation")
    return {
        "org_name": org.org_name,
        "my_role": org.user_assigned_role
    }