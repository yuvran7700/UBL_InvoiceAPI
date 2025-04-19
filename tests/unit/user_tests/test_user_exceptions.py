import pytest

from src.exceptions.user_exceptions import (
    ABNValidationError,
    PasswordValidationError,
    EmailAlreadyRegisteredError,
    UserNotFoundError,
)

def test_abn_validation_error_default():
    with pytest.raises(ABNValidationError) as exc_info:
        raise ABNValidationError("12345678901")
    exc = exc_info.value
    expected_message = "The ABN '12345678901' is invalid. It must be 11 digits and pass ABN checksum validation."
    assert exc.message == expected_message

def test_password_validation_error_default():
    with pytest.raises(PasswordValidationError) as exc_info:
        raise PasswordValidationError("Too short")
    exc = exc_info.value
    expected_message = "Password is invalid: Too short"
    assert exc.message == expected_message

def test_email_already_registered_error_default():
    with pytest.raises(EmailAlreadyRegisteredError) as exc_info:
        raise EmailAlreadyRegisteredError("test@example.com")
    exc = exc_info.value
    expected_message = "Email 'test@example.com' is already registered."
    assert exc.message == expected_message

def test_user_not_found_error_default():
    with pytest.raises(UserNotFoundError) as exc_info:
        raise UserNotFoundError("user@example.com")
    exc = exc_info.value
    expected_message = "User with email 'user@example.com' was not found."
    assert exc.message == expected_message
