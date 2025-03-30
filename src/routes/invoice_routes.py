# routes/invoice_routes.py
"""
API route handler for processing UBL Order UBL documents and then generating UBL Invoices.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi import Depends
from src.models.invoice_response_models import InvoiceResponse
from src.models.invoice_update import InvoiceUpdateModel
from src.services.invoice_service import InvoiceService
from src.services.auth_service import get_current_user_id


router = APIRouter()
invoice_service = InvoiceService()


@router.post("/v1/user/invoices/upload", response_model=InvoiceResponse)
async def upload_invoice_order(
    file: UploadFile = File(...), user_id: str = Depends(get_current_user_id)
):
    """
    Handles the upload of a UBL order document (XML or JSON),
    detects content type, and delegates to the service layer for processing.
    """
    # Read the uploaded file once
    content = await file.read()

    # MIME type detection happens in the route (HTTP layer concern)
    filename = file.filename.lower()
    if filename.endswith(".xml"):
        file_type = "application/xml"
    elif filename.endswith(".json"):
        file_type = "application/json"
    else:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Only XML and JSON are supported."
        )

    # Delegate to the service with content and MIME type
    return invoice_service.generate_draft_invoice(content, file_type, user_id)


@router.post("/v1/user/invoices/complete", response_model=InvoiceResponse)
async def complete_invoice_route(
    invoice_data: InvoiceUpdateModel,
    user_id: str = Depends(get_current_user_id)
):
    """
    Completes the draft invoice by performing validation, calculations, and storage.

    :param invoice_data: A InvoiceUpdateModel with mandatory missing fields provided.
    """
    return invoice_service.complete_invoice(invoice_data, user_id)


@router.get("/v1/user/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Retrieves a specific invoice by ID for the current user.
    Returns the invoice data along with its current status.
    """
    return invoice_service.get_invoice(invoice_id, user_id)
