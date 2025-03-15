"""
Domain-specific exceptions for orders and invoices.
These exceptions handle various scenarios related to business domain operations.
"""

from src.exceptions.base_exceptions import ValidationError, ProcessingError

class DocumentValidationError(ValidationError):
    """Base class for document validation errors."""
    def __init__(self, domain: str, field: str = None, message: str = None, details: str = None):
        super().__init__(domain, field, message, details)

class DocumentProcessingError(ProcessingError):
    """Base class for document processing errors."""
    def __init__(self, domain: str, operation: str, message: str = None, details: str = None):
        super().__init__(domain, operation, message, details)

class LineItemError(DocumentProcessingError):
    """Base class for line item processing errors."""
    def __init__(self, domain: str, line_id: str, message: str = None, details: str = None):
        self.line_id = line_id
        message = message or f"Line item processing failed for {line_id}"
        super().__init__(domain, "process_line", message, details)

# Order-specific exceptions
class OrderValidationError(DocumentValidationError):
    """Raised when order validation fails."""
    def __init__(self, field: str = None, message: str = None, details: str = None):
        super().__init__("Order", field, message, details)

class OrderProcessingError(DocumentProcessingError):
    """Raised when order processing fails."""
    def __init__(self, operation: str, message: str = None, details: str = None):
        super().__init__("Order", operation, message, details)

class OrderLineError(LineItemError):
    """Raised when processing order line items fails."""
    def __init__(self, line_id: str, message: str = None, details: str = None):
        super().__init__("Order", line_id, message, details)

# Invoice-specific exceptions
class InvoiceValidationError(DocumentValidationError):
    """Raised when invoice validation fails."""
    def __init__(self, field: str = None, message: str = None, details: str = None):
        super().__init__("Invoice", field, message, details)

class InvoiceProcessingError(DocumentProcessingError):
    """Raised when invoice processing fails."""
    def __init__(self, operation: str, message: str = None, details: str = None):
        super().__init__("Invoice", operation, message, details)

class InvoiceLineError(LineItemError):
    """Raised when processing invoice line items fails."""
    def __init__(self, line_id: str, message: str = None, details: str = None):
        super().__init__("Invoice", line_id, message, details)

class InvoiceCreationError(InvoiceProcessingError):
    """Raised when invoice creation from order fails."""
    def __init__(self, order_id: str, details: str = None):
        super().__init__("create", f"Failed to create from order {order_id}", details) 