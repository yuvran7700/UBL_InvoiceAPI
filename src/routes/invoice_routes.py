# routes/invoice_routes.py
"""
API route handler for processing UBL Order UBL documents and then generating UBL Invoices.
"""

from typing import List, Optional, Literal
from datetime import date
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi import Depends
from fastapi.responses import JSONResponse, StreamingResponse
from src.models.invoice_response_models import InvoiceResponse, InvoiceStatus, DeleteInvoicesRequest
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


@router.get("/v1/user/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    status: Optional[InvoiceStatus] = Query(None, description="Filter invoices by status"),
    issue_date_from: Optional[date] = Query(None, description="Start of issue date range (YYYY-MM-DD)"),
    issue_date_to: Optional[date] = Query(None, description="End of issue date range (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Lists all invoices for the current user, optionally filtered by status and issue date range.
    """
    return invoice_service.list_filtered_invoices(
        user_id=user_id,
        status=status,
        issue_date_from=issue_date_from,
        issue_date_to=issue_date_to,
    )

@router.delete("/v1/user/invoices", response_model=dict)
async def delete_invoices(
    request: DeleteInvoicesRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Deletes one or more invoices for the current user.
    Only invoices in draft status are permitted to be deleted.
    Returns a summary with the list of successfully deleted invoices and errors for failures.
    """
    result = invoice_service.delete_user_invoices(request.invoice_ids, user_id)
    return result


@router.patch("/v1/user/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice_route(
    invoice_id: str,
    invoice_update: InvoiceUpdateModel,
    user_id: str = Depends(get_current_user_id)
):
    """
    Partially updates a draft invoice with new data provided by the user.
    Returns the updated invoice along with a missing fields report.
    """
    return invoice_service.update_draft_invoice(invoice_id, invoice_update, user_id)


@router.get("/v1/user/invoices/{invoice_id}/download")
async def download_invoice(
    invoice_id: str,
    format: Literal["json", "xml"] = Query("json"),
    user_id: str = Depends(get_current_user_id)
):
    """
    Downloads a completed invoice in the requested format (JSON or XML).
    Only completed invoices are downloadable.
    """
    try:
        file_bytes, media_type, filename = invoice_service.generate_invoice_download(invoice_id, format, user_id)
        return StreamingResponse(
            content=iter([file_bytes]),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException as e:
        raise e

