"""
API route handler for order upload.
This endpoint accepts a UBL XML order document, extracts its data,
generates a draft invoice, and stores it in DynamoDB.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.order_parser import OrderParser
from services.invoice_service import generate_and_store_invoice
from models.invoice_type import InvoiceType

router = APIRouter()

@router.post("/upload", response_model=InvoiceType)
async def upload_order(file: UploadFile = File(...)):
    """
    Upload a UBL XML order document and generate a draft invoice.

    Args:
        file (UploadFile): The uploaded UBL order file in XML format.

    Returns:
        InvoiceType: The generated draft invoice with header, party, line items, tax, and payment details.

    Raises:
        HTTPException: If the file is not XML or parsing fails.
    """
    if file.content_type not in ["application/xml", "text/xml"]:
        raise HTTPException(
            status_code=415,
            detail="Unsupported Media Type. Only XML is supported in this implementation."
        )

    content = await file.read()

    # Parse the XML order document into an enriched OrderType.
    order = OrderParser.parse_xml_order(content)

    # Generate the draft invoice from the order data and store it in DynamoDB.
    invoice = generate_and_store_invoice(order)

    return invoice
