"""
src/routes/organisation.py
==========================
Organisation Management Routes

These routes allow authenticated users to manage organisations and their members.

**Features:**
- Get organisation information
- List organisation members
- Update a member's role
- Remove a member from an organisation
- Invite a user to join an organisation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from src.dependencies.auth import auth, check_permission
from src.dependencies.auth_client import auth_client

from src.services.organisation_service import (
    get_organisation_info,
    list_organisation_members,
    update_member_role,
    remove_member_from_org,
)

from propelauth_fastapi import User

router = APIRouter(prefix="/v1/organisations", tags=["Organisation Management"])

@router.get("/{org_id}")
def get_org(org_id: str, user: User = Depends(auth.require_user)):
    """
    Retrieve details about a specific organisation user is a member of.

    **Args:**
    - `org_id` (str): ID of the organisation to fetch.

    **Returns:**
    - Organisation metadata (name, id, creation date, etc.).
    """
    return get_organisation_info(user, org_id)

@router.get("/{org_id}/members")
def list_members(
    org_id: str,
    user: User = Depends(check_permission(allowed_roles=["Admin", "Owner"]))
):
    """
    List all members of an organisation.

    **Args:**
    - `org_id` (str): ID of the organisation.

    **Returns:**
    - List of members with their roles and emails.

    **Permissions:**
    - Requires `Admin` or `Owner` role.
    """
    return list_organisation_members(org_id)

@router.put("/{org_id}/members/{member_id}/role")
def update_role(
    org_id: str,
    member_id: str,
    new_role: str,
    user: User = Depends(check_permission(allowed_roles=["Admin", "Owner"]))
):
    """
    Update the role of a member within an organisation.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `member_id` (str): Member's user ID.
    - `new_role` (str): New role to assign (e.g., Admin, Member).

    **Returns:**
    - Success message.

    **Permissions:**
    - Requires `Admin` or `Owner` role.
    """
    update_member_role(org_id, member_id, new_role)
    return {"message": "User role updated"}

@router.delete("/{org_id}/members/{member_id}")
def remove_member(
    org_id: str,
    member_id: str,
    user: User = Depends(check_permission(allowed_roles=["Admin", "Owner"]))
):
    """
    Remove a member from an organisation.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `member_id` (str): Member's user ID to remove.

    **Returns:**
    - Success message.

    **Permissions:**
    - Requires `Admin` or `Owner` role.
    """
    remove_member_from_org(org_id, member_id)
    return {"message": "User removed from organisation"}



@router.post("/{org_id}/invite")
def invite_user_to_org(
    org_id: str,
    email: str,
    role: str = "Member",
    user: User = Depends(check_permission(allowed_roles=["Admin", "Owner"]))
):
    """
    Invite a user to join the organisation with a specified role.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `email` (str): Email address of the user to invite.
    - `role` (str, optional): Role to assign upon joining. Defaults to `Member`.

    **Returns:**
    - Success message if the invite was sent.

    **Permissions:**
    - Requires `Admin` or `Owner` role.

    **Raises:**
    - `HTTPException (500)`: If the invitation fails.
    """
    try:
        auth_client.invite_user_to_org(
            email=email,
            org_id=org_id,
            role=role
        )
        return {"message": f"Invitation sent to {email} to join the organisation as {role}"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send invite: {str(e)}"
        )