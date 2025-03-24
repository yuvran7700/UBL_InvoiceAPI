from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import magic
from src.services.invoice_service import InvoiceService
from src.auth.auth_utils import get_current_user_id 
from typing import Dict

router = APIRouter()
invoice_service = InvoiceService()

@router.post("/v1/user/invoices/complete")
async def complete_draft(invoice_data: dict, user_id: str = Depends(get_current_user_id)):
    """
    Completes the user’s draft invoice by re-validating the user-filled fields.
    """
    result = invoice_service.complete_draft_invoice(invoice_data, user_id)
    return result
