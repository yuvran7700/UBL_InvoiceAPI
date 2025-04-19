#src/exceptions/base_exceptions.py
"""
Base exceptions for the application.
These serve as the parent classes for more specific exceptions.
"""


from starlette.status import HTTP_400_BAD_REQUEST

class APIBaseException(Exception):
    def __init__(self, message: str, status_code: int = HTTP_400_BAD_REQUEST, code: str = "bad_request"):
        self.message = message
        self.status_code = status_code
        self.code = code
