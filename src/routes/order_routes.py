# routes/order_routes.py
"""
API route handler for order upload.
This endpoint accepts a UBL XML order document, extracts its data,
and creates a draft invoice.
"""

from fastapi import APIRouter, UploadFile, File
import magic
from src.services.invoice_service import InvoiceService



router = APIRouter()
invoice_service = InvoiceService()


@router.post("/upload")
async def upload_order(file: UploadFile = File(...)):
    """
    Handles the upload of a UBL order document (XML or JSON),
    detects content type, and delegates to the service layer for processing.
    """
    # Read the uploaded file once
    content = await file.read()

    # MIME type detection happens in the route (HTTP layer concern)
    file_type = magic.Magic(mime=True).from_buffer(content)

    # Delegate to the service with content and MIME type
    result = invoice_service.generate_draft_invoice(content, file_type)

    return result