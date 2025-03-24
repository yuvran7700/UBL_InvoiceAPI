import pytest

from src.exceptions.user_exceptions import (
    ABNValidationError,
    PasswordValidationError,
    EmailAlreadyRegisteredError,
    UserNotFoundError,
)


def test_abn_validation_error_default():
    with pytest.raises(ABNValidationError) as exc_info:
        raise ABNValidationError()
    exc = exc_info.value
    # Expect the default message without a field name.
    expected_message = "ABN validation failed"
    assert str(exc) == expected_message
    assert exc.message == expected_message
    assert exc.field_name is None


def test_abn_validation_error_with_field():
    with pytest.raises(ABNValidationError) as exc_info:
        raise ABNValidationError(field_name="abn")
    exc = exc_info.value
    expected_message = "ABN validation failed for field: abn"
    assert str(exc) == expected_message
    assert exc.message == expected_message
    assert exc.field_name == "abn"


def test_password_validation_error_default():
    with pytest.raises(PasswordValidationError) as exc_info:
        raise PasswordValidationError()
    exc = exc_info.value
    expected_message = "Password validation failed"
    assert str(exc) == expected_message
    assert exc.message == expected_message
    assert exc.field_name is None


def test_password_validation_error_with_field():
    with pytest.raises(PasswordValidationError) as exc_info:
        raise PasswordValidationError(field_name="password")
    exc = exc_info.value
    expected_message = "Password validation failed for field: password"
    assert str(exc) == expected_message
    assert exc.message == expected_message
    assert exc.field_name == "password"


def test_email_already_registered_error_default():
    with pytest.raises(EmailAlreadyRegisteredError) as exc_info:
        raise EmailAlreadyRegisteredError()
    exc = exc_info.value
    expected_message = "Account creation failed"
    assert str(exc) == expected_message
    assert exc.message == expected_message
    assert exc.field_name is None


def test_email_already_registered_error_with_field():
    with pytest.raises(EmailAlreadyRegisteredError) as exc_info:
        raise EmailAlreadyRegisteredError(field_name="email")
    exc = exc_info.value
    expected_message = "Account creation failed for field: email"
    assert str(exc) == expected_message
    assert exc.message == expected_message
    assert exc.field_name == "email"


def test_user_not_found_error_default():
    with pytest.raises(UserNotFoundError) as exc_info:
        raise UserNotFoundError()
    exc = exc_info.value
    expected_message = "User search failed"
    assert str(exc) == expected_message
    assert exc.message == expected_message
    assert exc.field_name is None


def test_user_not_found_error_with_field():
    with pytest.raises(UserNotFoundError) as exc_info:
        raise UserNotFoundError(field_name="user_id")
    exc = exc_info.value
    expected_message = "User search failed for field: user_id"
    assert str(exc) == expected_message
    assert exc.message == expected_message
    assert exc.field_name == "user_id"
