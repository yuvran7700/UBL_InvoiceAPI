# routes/order_routes.py
"""
API route handler for order upload.
This endpoint accepts a UBL XML order document, extracts its data,
and creates a draft invoice.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.invoice_service import create_invoice
from src.models.invoice_type import InvoiceType
from src.order_type_creation.order_director import OrderDirector

router = APIRouter()


@router.post("/upload", response_model=InvoiceType)
async def upload_order(file: UploadFile = File(...)):
    """
    Handle the upload of a UBL XML order document.

    :param file: The uploaded XML file.
    :return: The created draft invoice.
    :raises HTTPException: If the file type is not supported
        or if there is an error parsing the XML.
    """
    if file.content_type not in ["application/xml", "text/xml"]:
        raise HTTPException(
            status_code=415, detail="Unsupported Media Type. Only XML is supported."
        )

    content = await file.read()
    order = OrderDirector.construct_order_from_xml(content)
    invoice = create_invoice(order)
    return invoice
