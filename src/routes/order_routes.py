#routes/order_routes.py
"""
API route handler for order upload.
This endpoint accepts a UBL XML order document, extracts its data,
and creates a draft invoice.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from src.utils.order_parser import OrderParser
from src.services.invoice_service import create_invoice
from src.models.invoice_type import InvoiceType

router = APIRouter()

@router.post("/upload", response_model=InvoiceType)
async def upload_order(file: UploadFile = File(...)):
    if file.content_type not in ["application/xml", "text/xml"]:
        raise HTTPException(status_code=415, detail="Unsupported Media Type. Only XML is supported.")
    
    content = await file.read()
    order = OrderParser.parse_xml_order(content)
    invoice = create_invoice(order)
    return invoice
