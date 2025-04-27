from starlette.status import HTTP_503_SERVICE_UNAVAILABLE, HTTP_415_UNSUPPORTED_MEDIA_TYPE, HTTP_400_BAD_REQUEST
from src.exceptions.base_exceptions import APIBaseException


class LoginError(APIBaseException):
    def __init__(self):
        super().__init__(
            message=f"Order service currently down. We are working on it",
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            code="invoice_not_found"
        )

class InvalidOrderFileError(APIBaseException):
    def __init__(self, details: str = "Unsupported file type. Only JSON are supported for order upload."):
        super().__init__(
            message=details,
            status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            code="invalid_invoice_format"
        )

class OrderValidationError(APIBaseException):
    def __init__(self, details: str):
        super().__init__(
            message=details,
            status_code=HTTP_400_BAD_REQUEST,
            code="invalid_invoice_format"
        )

class InvalidOrderMissingError(APIBaseException):
    def __init__(self, details: str = "Invalid fields provided to create UBL document."):
        super().__init__(
            message=details,
            status_code=HTTP_400_BAD_REQUEST,
            code="invalid_invoice_format"
        )