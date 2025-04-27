
"""
src/dependencies/auth.py
========================
Purpose:
- Protects endpoints (require_user)
- Provides role-based permission checks (check_permission)
"""
from propelauth_fastapi import TokenVerificationMetadata, init_auth, User
from fastapi import Depends, HTTPException, status

# You can find your Verifier Key under Backend Integration in the dashboard.
#   This skips a network request to fetch the key on startup.
auth = init_auth(
    "https://39356306333.propelauthtest.com",  # <--- Auth URL
    "28a55c0641fe65f80561bd6a5d9cdeb0481c595dd1d94079dc06e18dd1d4fed17d927df8f4ec55942a79f9b44e18fb39",  # <--- API Key
    TokenVerificationMetadata(
        verifier_key="""
            -----BEGIN PUBLIC KEY-----
            MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3hn/Oqf1HTisSKUgKNhy
            zEpQx/Hv/xumJcxa+HGs0rjtUthIFT83EXAR0lDK+eHSldvZYMc3TLse1vOiEsc8
            kP/YgKiKm2ME8askq3TL/9//nB7j4jJHhD/PG/flFZ/K688eymZGkknfknNpQ+eH
            3oq2d6kQLiVbxfALiqos203mANGmCHKDv4w6GxB1VmqP1blz9TQS37Y9F6zqSR9f
            8jkqgYg0O6twlzJRRJtQBE1LsmwXsT6v3Eu4T+TAbdmx9vwqTnTl0F4bpJsKzpcY
            vk9BHkRfrKzymvKfbeXu1t4JEQDz5IbZHTKa/mXFQklc3EdOosarU7xNQSMydJJF
            5QIDAQAB
            -----END PUBLIC KEY-----""",  # <--- Full Public Key
        issuer="https://39356306333.propelauthtest.com",  # <--- Issuer (same as Auth URL)
    ),
)


def check_permission(allowed_roles: list[str]):
    """
    Decorator to check if the user has the required role in the organisation.
    """
    async def permission_checker(
            org_id: str,
            user: User = Depends(auth.require_user)
    ):
        org = user.get_org(org_id)

        if not org:  
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this organisation."
            )

        if not org.user_assigned_role in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{org.user_assigned_role}' is not allowed. Allowed roles: {allowed_roles}"
            )

        return user
    return permission_checker
