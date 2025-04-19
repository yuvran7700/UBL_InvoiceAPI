"""
Exception classes related to invoice operations and rules.
"""

from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from src.exceptions.base_exceptions import APIBaseException


class InvoiceNotFoundError(APIBaseException):
    def __init__(self, invoice_id: str):
        super().__init__(
            message=f"Invoice with ID '{invoice_id}' was not found.",
            status_code=HTTP_404_NOT_FOUND,
            code="invoice_not_found"
        )


class InvalidInvoiceFormatError(APIBaseException):
    def __init__(self, details: str = "Unsupported file type. Only XML and JSON are supported."):
        super().__init__(
            message=details,
            status_code=HTTP_400_BAD_REQUEST,
            code="invalid_invoice_format"
        )


class InvoiceUpdateNotAllowedError(APIBaseException):
    def __init__(self, invoice_id: str):
        super().__init__(
            message=f"Invoice '{invoice_id}' is not in draft status and cannot be updated.",
            status_code=HTTP_403_FORBIDDEN,
            code="update_not_allowed"
        )


class InvoiceCompletionError(APIBaseException):
    def __init__(self, details: str = "Invoice is missing required fields and cannot be completed."):
        super().__init__(
            message=details,
            status_code=HTTP_400_BAD_REQUEST,
            code="invoice_completion_failed"
        )


class InvoiceDownloadError(APIBaseException):
    def __init__(self, details: str = "Only completed invoices can be downloaded."):
        super().__init__(
            message=details,
            status_code=HTTP_400_BAD_REQUEST,
            code="download_not_allowed"
        )
