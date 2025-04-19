from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from .base_exceptions import APIBaseException


class DatabaseReadError(APIBaseException):
    def __init__(self, message: str):
        super().__init__(
            message=f"Database read failed: {message}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code="database_read_error"
        )

class DatabaseWriteError(APIBaseException):
    def __init__(self, message: str):
        super().__init__(
            message=f"Database write failed: {message}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code="database_write_error"
        )
class ItemNotFoundError(APIBaseException):
    def __init__(self, item_type: str, key: str):
        super().__init__(
            message=f"{item_type} with key '{key}' was not found.",
            status_code=HTTP_404_NOT_FOUND,
            code="item_not_found"
        )