"""
Base exceptions for the application.
These serve as parent classes for more specific domain exceptions.
"""


class BaseError(Exception):
    """Base class for all application exceptions."""

    def __init__(self, message: str, details: str = None):
        self.message = message
        if details:
            self.message += f": {details}"
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class DomainError(BaseError):
    """Base class for domain-specific errors."""

    def __init__(self, domain: str, message: str, details: str = None):
        self.domain = domain
        super().__init__(f"{domain} error - {message}", details)


class ValidationError(DomainError):
    """Base class for validation errors."""

    def __init__(
        self, domain: str, field: str = None, message: str = None, details: str = None
    ):
        self.field = field
        message = message or "Validation failed"
        if field:
            message = f"{message} for field: {field}"
        super().__init__(domain, message, details)


class ProcessingError(DomainError):
    """Base class for processing/parsing errors."""

    def __init__(
        self, domain: str, operation: str, message: str = None, details: str = None
    ):
        self.operation = operation
        message = message or f"Failed to {operation}"
        super().__init__(domain, message, details)


class StorageError(DomainError):
    """Base class for storage/database related errors."""

    def __init__(self, storage_type: str, operation: str, details: str = None):
        self.storage_type = storage_type
        self.operation = operation
        message = f"Failed to {operation} in {storage_type}"
        super().__init__("Storage", message, details)
