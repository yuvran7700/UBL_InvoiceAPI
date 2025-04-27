"""
API route handler for processing UBL Orders and generating UBL Invoices (Multi-tenant v2).
"""

# ---- Standard Libraries ----
from typing import List, Optional, Literal
from datetime import date

# ---- FastAPI Libraries ----
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse

# ---- Third-Party API Libraries ----
from propelauth_fastapi import User
from src.dependencies.auth import check_permission

# ---- Domain Logic/ Business Models ----
from src.domain.models.invoice_response_models import InvoiceResponse, InvoiceStatus, DeleteInvoicesRequest
from src.domain.models.invoice_update import InvoiceUpdateModel

# ---- Service Logic ----
from src.services.invoice_service_v2 import InvoiceService

# ---- Exception Handling ----
from src.exceptions.invoice_exceptions import InvalidInvoiceFormatError

router = APIRouter(prefix="/v2/invoices")
invoice_service = InvoiceService()

# ---- Invoice Upload ----
@router.post("/{org_id}/upload", response_model=InvoiceResponse, tags=["Invoice Creation"])
async def upload_invoice_order(
    org_id: str,
    file: UploadFile = File(...),
    user: User = Depends(check_permission(allowed_roles=["Owner", "Admin", "Member"])),
):
    """
    Upload a UBL Order file (JSON or XML) and generate a draft invoice.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `file` (UploadFile): UBL order file (XML or JSON).

    **Returns:**
    - Draft invoice data.

    **Raises:**
    - `InvalidInvoiceFormatError`: If file is not XML or JSON.
    """
    content = await file.read()
    filename = file.filename.lower()
    if filename.endswith(".xml"):
        file_type = "application/xml"
    elif filename.endswith(".json"):
        file_type = "application/json"
    else:
        raise InvalidInvoiceFormatError()

    return invoice_service.generate_draft_invoice(content, file_type, org_id, user.user_id)

# ---- Complete Draft Invoice ----
@router.post("/{org_id}/complete", response_model=InvoiceResponse, tags=["Invoice Management"])
async def complete_invoice_route(
    org_id: str,
    invoice_data: InvoiceUpdateModel,
    user: User = Depends(check_permission(allowed_roles=["Owner", "Admin", "Member"])),
):
    """
    Complete and finalize a draft invoice.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `invoice_data` (InvoiceUpdateModel): Final invoice details.

    **Returns:**
    - Completed invoice data.
    """
    return invoice_service.complete_invoice(invoice_data, org_id, user.user_id)

# ---- Retrieve Specific Invoice ----
@router.get("/{org_id}/{invoice_id}", response_model=InvoiceResponse, tags=["Invoice Management"])
async def get_invoice(
    org_id: str,
    invoice_id: str,
    user: User = Depends(check_permission(allowed_roles=["Owner", "Admin", "Member"])),
):
    """
    Retrieve a specific invoice by ID.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `invoice_id` (str): Invoice ID.

    **Returns:**
    - Invoice data.
    """
    return invoice_service.get_invoice(invoice_id, org_id)

# ---- List Invoices ----
@router.get("/{org_id}", response_model=List[InvoiceResponse], tags=["Invoice Management"])
async def list_invoices(
    org_id: str,
    status: Optional[InvoiceStatus] = Query(None, description="Filter invoices by status"),
    issue_date_from: Optional[date] = Query(None, description="Start of issue date range (YYYY-MM-DD)"),
    issue_date_to: Optional[date] = Query(None, description="End of issue date range (YYYY-MM-DD)"),
    user: User = Depends(check_permission(allowed_roles=["Owner", "Admin", "Member"])),
):
    """
    List invoices for an organisation, with optional filtering.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `status` (Optional[InvoiceStatus]): Filter by invoice status.
    - `issue_date_from` (Optional[date]): Start of issue date range.
    - `issue_date_to` (Optional[date]): End of issue date range.

    **Returns:**
    - List of filtered invoice objects.
    """
    return invoice_service.list_filtered_invoices(
        organisation_id=org_id,
        status=status,
        issue_date_from=issue_date_from,
        issue_date_to=issue_date_to,
    )

# ---- Delete Invoices (Admin/Owner Only) ----
@router.delete("/{org_id}", response_model=dict, tags=["Invoice Management"])
async def delete_invoices(
    org_id: str,
    request: DeleteInvoicesRequest,
    user: User = Depends(check_permission(allowed_roles=["Owner", "Admin"])),
):
    """
    Delete one or more invoices for an organisation.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `request` (DeleteInvoicesRequest): List of invoice IDs to delete.

    **Returns:**
    - Success message confirming deletion.

    **Permissions:**
    - Requires `Admin` or `Owner` role.
    """
    return invoice_service.delete_user_invoices(request.invoice_ids, org_id)

# ---- Update Draft Invoice ----
@router.patch("/{org_id}/{invoice_id}", response_model=InvoiceResponse, tags=["Invoice Management"])
async def update_invoice_route(
    org_id: str,
    invoice_id: str,
    invoice_update: InvoiceUpdateModel,
    user: User = Depends(check_permission(allowed_roles=["Owner", "Admin", "Member"])),
):
    """
    Update a draft invoice with new information.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `invoice_id` (str): Invoice ID to update.
    - `invoice_update` (InvoiceUpdateModel): New draft fields.

    **Returns:**
    - Updated invoice data.
    """
    return invoice_service.update_draft_invoice(invoice_id, invoice_update, org_id, user.user_id)

# ---- Download Invoice ----
@router.get("/{org_id}/{invoice_id}/download", tags=["Invoice Download and Delivery"])
async def download_invoice(
    org_id: str,
    invoice_id: str,
    format: Literal["json", "xml"] = Query("json"),
    user: User = Depends(check_permission(allowed_roles=["Owner", "Admin", "Member"])),
):
    """
    Download an invoice in either JSON or XML format.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `invoice_id` (str): Invoice ID.
    - `format` (str): Desired download format (`json` or `xml`).

    **Returns:**
    - Downloadable invoice file stream.
    """
    try:
        file_bytes, media_type, filename = invoice_service.generate_invoice_download(invoice_id, format, org_id)
        return StreamingResponse(
            content=iter([file_bytes]),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException as e:
        raise e

@router.get("/{org_id}/{invoice_id}/formatted-download", tags=["Invoice Download and Delivery"])
async def download_invoice_formatted(
    org_id: str,
    invoice_id: str,
    user: User = Depends(check_permission(allowed_roles=["Owner", "Admin", "Member"])),
):
    """
    Download a formatted, professional PDF version of the completed invoice.

    **Args:**
    - `org_id` (str): Organisation ID.
    - `invoice_id` (str): Invoice ID.

    **Returns:**
    - Downloadable PDF stream of the invoice.
    """
    try:
        pdf_bytes, filename = invoice_service.generate_formatted_invoice_download(invoice_id, org_id)
        return StreamingResponse(
            content = pdf_bytes,
            media_type = "application/pdf",
            headers = {"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException as e:
        raise e
