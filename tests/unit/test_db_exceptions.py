import pytest
from src.exceptions.db_exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseWriteError,
    DatabaseReadError,
    DynamoDBError,
)


def test_database_error_default_message():
    with pytest.raises(DatabaseError) as exc_info:
        raise DatabaseError()
    expected = "Database operation failed"
    # Verify both the string representation and the message attribute.
    assert str(exc_info.value) == expected
    assert exc_info.value.message == expected


def test_database_error_custom_message():
    custom_message = "Custom DB error message"
    with pytest.raises(DatabaseError) as exc_info:
        raise DatabaseError(custom_message)
    assert str(exc_info.value) == custom_message
    assert exc_info.value.message == custom_message


def test_database_connection_error_default():
    with pytest.raises(DatabaseConnectionError) as exc_info:
        raise DatabaseConnectionError()
    expected = "Failed to connect to database"
    assert str(exc_info.value) == expected
    assert exc_info.value.message == expected


def test_database_connection_error_custom():
    custom_message = "Connection error: host unreachable"
    with pytest.raises(DatabaseConnectionError) as exc_info:
        raise DatabaseConnectionError(custom_message)
    assert str(exc_info.value) == custom_message
    assert exc_info.value.message == custom_message


def test_database_write_error_default():
    with pytest.raises(DatabaseWriteError) as exc_info:
        raise DatabaseWriteError()
    expected = "Failed to write to database"
    assert str(exc_info.value) == expected
    assert exc_info.value.message == expected


def test_database_write_error_custom():
    custom_message = "Write error: permission denied"
    with pytest.raises(DatabaseWriteError) as exc_info:
        raise DatabaseWriteError(custom_message)
    assert str(exc_info.value) == custom_message
    assert exc_info.value.message == custom_message


def test_database_read_error_default():
    with pytest.raises(DatabaseReadError) as exc_info:
        raise DatabaseReadError()
    expected = "Failed to read from database"
    assert str(exc_info.value) == expected
    assert exc_info.value.message == expected


def test_database_read_error_custom():
    custom_message = "Read error: record not found"
    with pytest.raises(DatabaseReadError) as exc_info:
        raise DatabaseReadError(custom_message)
    assert str(exc_info.value) == custom_message
    assert exc_info.value.message == custom_message


def test_dynamodb_error_without_details():
    operation = "update"
    with pytest.raises(DynamoDBError) as exc_info:
        raise DynamoDBError(operation)
    expected = "DynamoDB update operation failed"
    assert str(exc_info.value) == expected
    assert exc_info.value.message == expected
    # Check that the operation attribute is set correctly.
    assert exc_info.value.operation == operation


def test_dynamodb_error_with_details():
    operation = "delete"
    details = "Item not found"
    with pytest.raises(DynamoDBError) as exc_info:
        raise DynamoDBError(operation, details)
    expected = "DynamoDB delete operation failed: Item not found"
    assert str(exc_info.value) == expected
    assert exc_info.value.message == expected
    assert exc_info.value.operation == operation
