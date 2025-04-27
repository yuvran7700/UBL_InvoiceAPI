from fastapi import HTTPException, status
from src.dependencies.auth_client import auth_client  # Your auth instance (initialized from PropelAuth)
from propelauth_fastapi import User

def get_organisation_info(user: User, org_id: str):
    org = user.get_org(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organisation."
        )
    return {
        "org_id": org.org_id,
        "org_name": org.org_name,
        "org_metadata": org.org_metadata,
        "user_role": org.user_assigned_role,
    }

def list_organisation_members(org_id: str):
    try:
        # PropelAuth API call
        members = auth_client.fetch_users_in_org(org_id)
        return members
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organisation members: {str(e)}"
        )

def update_member_role(org_id: str, member_id: str, new_role: str):
    try:
        # PropelAuth API call
        auth_client.change_user_role_in_org(org_id=org_id, user_id=member_id, role=new_role)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )

def remove_member_from_org(org_id: str, member_id: str):
    try:
        # PropelAuth API call
        auth_client.remove_user_from_org(org_id=org_id, user_id=member_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove user from organisation: {str(e)}"
        )
