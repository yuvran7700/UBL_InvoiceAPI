import pytest
from fastapi import HTTPException, status
from src.exceptions.error_handler import (
    ValidationErrorHandler,
    DatabaseErrorHandler,
    NotFoundErrorHandler,
    ErrorContext,
)


def test_validation_error_handler():
    handler = ValidationErrorHandler()
    with pytest.raises(HTTPException) as exc_info:
        handler.handle("Validation failed")
    exc = exc_info.value
    assert exc.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.detail == "Validation failed"


def test_database_error_handler():
    handler = DatabaseErrorHandler()
    with pytest.raises(HTTPException) as exc_info:
        handler.handle("Some DB error")
    exc = exc_info.value
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    # Note: detail is fixed regardless of the error message
    assert exc.detail == "Database operation failed"


def test_not_found_error_handler():
    handler = NotFoundErrorHandler()
    with pytest.raises(HTTPException) as exc_info:
        handler.handle("Item not found")
    exc = exc_info.value
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail == "Item not found"


def test_error_context_with_validation_handler():
    context = ErrorContext(ValidationErrorHandler())
    with pytest.raises(HTTPException) as exc_info:
        context.handle_error("Context validation error")
    exc = exc_info.value
    assert exc.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.detail == "Context validation error"


def test_error_context_with_database_handler():
    context = ErrorContext(DatabaseErrorHandler())
    with pytest.raises(HTTPException) as exc_info:
        context.handle_error("Context database error")
    exc = exc_info.value
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "Database operation failed"


def test_error_context_with_not_found_handler():
    context = ErrorContext(NotFoundErrorHandler())
    with pytest.raises(HTTPException) as exc_info:
        context.handle_error("Context not found error")
    exc = exc_info.value
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail == "Context not found error"
