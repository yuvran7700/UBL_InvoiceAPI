"""
Custom exceptions for database operations.
These exceptions handle various database-related errors.
"""

class DatabaseError(Exception):
    """Base class for database exceptions."""
    def __init__(self, message="Database operation failed"):
        self.message = message
        super().__init__(self.message)

class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""
    def __init__(self, message="Failed to connect to database"):
        super().__init__(message)

class DatabaseWriteError(DatabaseError):
    """Raised when writing to database fails."""
    def __init__(self, message="Failed to write to database"):
        super().__init__(message)

class DatabaseReadError(DatabaseError):
    """Raised when reading from database fails."""
    def __init__(self, message="Failed to read from database"):
        super().__init__(message)

class DynamoDBError(DatabaseError):
    """Raised for DynamoDB specific errors."""
    def __init__(self, operation: str, details: str = None):
        self.operation = operation
        message = f"DynamoDB {operation} operation failed"
        if details:
            message += f": {details}"
        super().__init__(message) 