"""
Custom exceptions for data validation.
These exceptions handle various validation scenarios for orders and invoices.
"""


class ValidationError(Exception):
    """Base class for validation exceptions."""

    def __init__(self, message="Validation failed"):
        self.message = message
        super().__init__(self.message)


class OrderValidationError(ValidationError):
    """Raised when order validation fails."""

    def __init__(self, field_name: str = None, message: str = None):
        self.field_name = field_name
        if not message:
            message = f"Order validation failed"
            if field_name:
                message += f" for field: {field_name}"
        super().__init__(message)


class InvoiceValidationError(ValidationError):
    """Raised when invoice validation fails."""

    def __init__(self, field_name: str = None, message: str = None):
        self.field_name = field_name
        if not message:
            message = f"Invoice validation failed"
            if field_name:
                message += f" for field: {field_name}"
        super().__init__(message)


class SchematronValidationError(ValidationError):
    """Raised when Schematron rule validation fails."""

    def __init__(self, rule_id: str, message: str = None):
        self.rule_id = rule_id
        if not message:
            message = f"Failed Schematron rule: {rule_id}"
        super().__init__(message)
