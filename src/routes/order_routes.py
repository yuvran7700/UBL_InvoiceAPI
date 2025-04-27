from fastapi import APIRouter, UploadFile, File, Depends
from propelauth_fastapi import User
from src.dependencies.auth import check_permission
from src.services.order_service import order_to_invoice

router = APIRouter(prefix="/v1/orders")

@router.post("/{org_id}/upload", tags=["Invoice Creation"])
async def upload_order_to_invoice(
    org_id: str,
    file: UploadFile = File(...),
    user: User = Depends(check_permission(allowed_roles=["Owner", "Admin", "Member"]))
):
    """
    Upload an order data file to generate a draft invoice.

    This endpoint uses an external API to process the uploaded order data and create a draft invoice 
    inside the specified organisation. A complete UBL Order document is **not required**; 
    lightweight order information is sufficient.

    **Args:**
    - `org_id` (str): Organisation ID where the draft invoice will be created.
    - `file` (UploadFile): Order data file (typically JSON or simplified XML).

    **Returns:**
    - Draft invoice data generated from the uploaded order.

    **Permissions:**
    - Requires `Owner`, `Admin`, or `Member` role.
    """
    return order_to_invoice(file, org_id, user.user_id)
