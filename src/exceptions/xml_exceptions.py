"""
XML-specific exceptions.
These exceptions handle various scenarios related to XML processing.
"""

from src.exceptions.base_exceptions import ProcessingError, ValidationError


class XMLValidationError(ValidationError):
    """Base class for XML validation errors."""

    def __init__(
        self,
        field: str = None,
        message: str = None,
        xpath: str = None,
        details: str = None,
    ):
        self.xpath = xpath
        if xpath and details:
            details = f"{details} (xpath: {xpath})"
        elif xpath:
            details = f"xpath: {xpath}"
        super().__init__("XML", field, message, details)


class XMLProcessingError(ProcessingError):
    """Base class for XML processing errors."""

    def __init__(self, operation: str, message: str = None, details: str = None):
        super().__init__("XML", operation, message, details)


class XMLParseError(XMLProcessingError):
    """Raised when XML parsing fails."""

    def __init__(self, details: str = None):
        super().__init__("parse", "Invalid XML content", details)


class XMLSchemaError(XMLValidationError):
    """Raised when XML does not conform to schema."""

    def __init__(self, schema_name: str, details: str = None):
        super().__init__(
            message=f"Does not conform to schema: {schema_name}", details=details
        )


class XMLRequiredFieldError(XMLValidationError):
    """Raised when a required field is missing in XML."""

    def __init__(self, field: str, xpath: str = None):
        super().__init__(field=field, message="Missing required field", xpath=xpath)


class XMLInvalidValueError(XMLValidationError):
    """Raised when a field contains an invalid value."""

    def __init__(self, field: str, details: str = None, xpath: str = None):
        super().__init__(
            field=field, message="Invalid value", xpath=xpath, details=details
        )


class XMLNamespaceError(XMLProcessingError):
    """Raised when there are XML namespace issues."""

    def __init__(self, namespace: str = None, details: str = None):
        message = "Namespace error"
        if namespace:
            message += f" for {namespace}"
        super().__init__("validate_namespace", message, details)
