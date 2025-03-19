# routes/order_routes.py
"""
API route handler for order upload.
This endpoint accepts a UBL XML order document, extracts its data,
and creates a draft invoice.
"""

import json
import xml.etree.ElementTree as ET
from fastapi import APIRouter, UploadFile, File, HTTPException
import magic
from src.services.invoice_service import create_invoice
from src.models.order import OrderUploadRequest
from src.order_type_creation.invoice_director import InvoiceDirector

router = APIRouter()


@router.post("/upload", response_model=InvoiceType)
async def upload_order(file: UploadFile = File(...)):
    """
    Handle the upload of a UBL order document (XML or JSON), extract data, and generate a draft invoice.
    """
    
    # Check if it's an XML file
    content = await file.read()

    # Use python-magic to check the MIME type of the file
    file_type = magic.Magic(mime=True).from_buffer(content)


    # Validate the MIME type
    if file_type == "application/xml":
        draft_invoice = InvoiceDirector.construct_invoice_from_data(content, "xml")
    elif file_type == "application/json":
        draft_invoice = InvoiceDirector.construct_invoice_from_data(content, "json")
    else:
        raise HTTPException(status_code=415, detail="Unsupported file type. Only XML and JSON are supported.")
    
    # Generate the invoice from the parsed order
    invoice = create_invoice(draft_invoice)
    return invoice