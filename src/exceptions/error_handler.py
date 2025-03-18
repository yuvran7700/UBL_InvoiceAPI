''' This file defines the Error Handler that 
    - catch these domain-specific exceptions 
    - translates them into appropriate HTTP responses 
        (with status codes and details).

    Error Handler is created using a stragery pattern. 

    Usage: Within code, use handler to raise the correct http expectins
'''

from abc import ABC, abstractmethod
from fastapi import HTTPException, status
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Base error handling strategy
class ErrorHandler(ABC):
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database operation failed")

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
