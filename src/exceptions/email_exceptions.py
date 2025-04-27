"""
Exception classes related to email operations and rules.
"""

from typing import List
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_415_UNSUPPORTED_MEDIA_TYPE
from src.exceptions.base_exceptions import APIBaseException
from pydantic import EmailStr

class EmailDoesntExist(APIBaseException):
    def __init__(self, email: EmailStr):
        super().__init__(
            message=f"Email '{email}' doesn't exist.",
            status_code=HTTP_404_NOT_FOUND,
            code="email_not_found"
        )

class EmailInvalidDomain(APIBaseException):
    def __init__(self, domain: str):
        super().__init__(
            message=f"The email domain '{domain}' is not valid.",
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            code="invalid_domain"
        )

class EmailInvalidFormat(APIBaseException):
    def __init__(self, email: EmailStr):
        super().__init__(
            message=f"The '{email}' is not in a valid format.",
            status_code=HTTP_400_BAD_REQUEST,
            code="invalid_email_format"
        )

class EmailInvalidMX(APIBaseException):
    def __init__(self, domain: str):
        super().__init__(
            message=f"The MX record of the domain '{domain}' is not valid.",
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            code="invalid_mx"
        )

class EmailMissingFields(APIBaseException):
    def __init__(self, missing: List[str]):
        missing_no_under = [v.replace('_', ' ') if isinstance(v, str) else v for v in missing.missing_email_fields]
        missing_format = str(missing_no_under)[1:-1]
        super().__init__(
            message=f"Missing required fields - {missing_format}.",
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            code="missing_email_fields"
        )

class EmailInvalidFileType(APIBaseException):
    def __init__(self):
        super().__init__(
            message=f"Unsupported file type. Only XML, JSON and PDF are supported.",
            status_code=HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            code="invalid_email_filetype"
        )

class EmailSendError(APIBaseException):
    def __init__(self, details: str = "Only completed invoices can be emailed."):
        super().__init__(
            message=details,
            status_code=HTTP_400_BAD_REQUEST,
            code="email_not_allowed"
        )