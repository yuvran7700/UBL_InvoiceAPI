# src/routes/email_routes.py

from fastapi import APIRouter, Depends, status, Path
from src.domain.models.email_models import SendEmailModel
from src.services.email_service import EmailService
from propelauth_fastapi import User
from src.dependencies.auth import check_permission

router = APIRouter(prefix="/v1/email")

email_service = EmailService()

@router.post("/{org_id}/{invoice_id}/send", status_code=status.HTTP_202_ACCEPTED, tags=["Invoice Download and Delivery"])
async def send_invoice_email(
    org_id: str = Path(..., description="Organisation ID"),
    invoice_id: str = Path(..., description="Invoice ID"),
    email_data: SendEmailModel = None,
    user: User = Depends(check_permission(allowed_roles=["Owner", "Admin", "Member"]))
):
    """
    Sends an invoice to an external email recipient with attachment.
    """
    return await email_service.send_invoice_email(
        organisation_id=org_id,
        invoice_id=invoice_id,
        user_id=user.user_id,
        email_data=email_data
    )