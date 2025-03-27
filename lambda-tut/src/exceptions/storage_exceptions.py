"""
Storage-specific exceptions.
These exceptions handle various scenarios related to database operations.
"""

from src.exceptions.base_exceptions import StorageError


class DatabaseError(StorageError):
    """Base class for database errors."""

    def __init__(self, operation: str, details: str = None):
        super().__init__("Database", operation, details)


class DynamoDBError(DatabaseError):
    """Raised for DynamoDB specific errors."""

    def __init__(self, operation: str, details: str = None, table_name: str = None):
        self.table_name = table_name
        if table_name:
            details = (
                f"Table {table_name}: {details}" if details else f"Table {table_name}"
            )
        super().__init__(operation, details)


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, details: str = None):
        super().__init__("connect", details)


class DatabaseWriteError(DatabaseError):
    """Raised when writing to database fails."""

    def __init__(self, operation: str = "write", details: str = None):
        super().__init__(operation, details)


class DatabaseReadError(DatabaseError):
    """Raised when reading from database fails."""

    def __init__(self, operation: str = "read", details: str = None):
        super().__init__(operation, details)


class StorageQuotaError(StorageError):
    """Raised when storage quota is exceeded."""

    def __init__(self, resource: str, details: str = None):
        super().__init__(
            "Quota",
            "exceed_limit",
            f"Resource: {resource}" + (f", {details}" if details else ""),
        )
