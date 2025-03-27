from abc import ABC, abstractmethod
from fastapi import HTTPException, status
import logging

# Configure logger
logger = logging.getLogger(__name__)


# Base error handling strategy
class ErrorHandler(ABC):
    """
    Abstract base class for error-handling strategies.

    This class defines the interface for handling different types of errors
    using the Strategy Pattern. Subclasses must implement the `handle` method
    to process specific exceptions and convert them into appropriate HTTP responses.

    Subclasses:
        - `ValidationErrorHandler`: Handles validation-related errors with HTTP 400.
        - `DatabaseErrorHandler`: Handles database-related errors with HTTP 500.
        - `NotFoundErrorHandler`: Handles missing resource errors with HTTP 404.

    Methods:
        handle(error): Abstract method to be implemented by subclasses for error handling.
    """

    @abstractmethod
    def handle(self, error):
        pass


# Specific strategies
class ValidationErrorHandler(ErrorHandler):
    def handle(self, error):
        logger.error(f"Validation Error: {error}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


class DatabaseErrorHandler(ErrorHandler):
    def handle(self, error):
        logger.critical(f"Database Error: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


class NotFoundErrorHandler(ErrorHandler):
    def handle(self, error):
        logger.warning(f"Not Found: {error}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


# Context class to switch strategies dynamically
class ErrorContext:
    def __init__(self, strategy: ErrorHandler):
        self.strategy = strategy

    def handle_error(self, error):
        self.strategy.handle(error)
