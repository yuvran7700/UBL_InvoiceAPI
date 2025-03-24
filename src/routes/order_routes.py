# routes/order_routes.py
"""
API route handler for order upload.
This endpoint accepts a UBL XML order document, extracts its data,
and creates a draft invoice.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import magic
from src.marshallers.order_xml_unmarshaller_factory import OrderXmlUnmarshaller
from src.marshallers.order_json_unmarshaller_factory import OrderJsonUnmarshaller
from src.models.invoice import Invoice
from src.draft_invoice_creation.invoice_director import InvoiceDirector
from src.utils.missing_field_checker import find_missing_fields


router = APIRouter()


@router.post("/upload", response_model=Invoice)
async def upload_order(file: UploadFile = File(...)):
    """
    Handle the upload of a UBL order document (XML or JSON), extract data, and generate a invoice object.
    """
    
    # Read the content of the uploaded file
    content = await file.read()

    # Use python-magic to check the MIME type of the file
    file_type = magic.Magic(mime=True).from_buffer(content)

   # Choose the correct unmarshaller based on MIME
    if file_type == "application/xml":
        unmarshaller = OrderXmlUnmarshaller()
    elif file_type == "application/json":
        unmarshaller = OrderJsonUnmarshaller()
    else:
        raise HTTPException(status_code=415, detail="Unsupported file type. Only XML and JSON are supported.")

    # Build the draft invoice using the director
    director = InvoiceDirector(unmarshaller)
    draft_invoice = director.construct_invoice_from_data(content)

    # Check for missing required fields
    missing_fields = find_missing_fields(draft_invoice)

    # Optionally: attach missing fields to the response or wrap the invoice in a response model
    return {
        "invoice": draft_invoice,
        "missing_fields": missing_fields
    }