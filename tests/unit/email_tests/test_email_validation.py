"""
Test cases for email validation API
Modules Tested: Validect
"""
from unittest.mock import MagicMock, patch
import pytest
from src.validators.email_validator import validate_email
from src.exceptions.email_exceptions import EmailDoesntExist, EmailInvalidDomain, EmailInvalidFormat, EmailInvalidMX

@patch("src.validators.email_validator.requests.get")
@pytest.mark.unit
def test_email_doesnt_exist(mock_get):
    email = 'wiouaawidaif@gmail.com'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'status': 'invalid',
        'reason': "rejected_email",
        'email': 'wiouaawidaif@gmail.com'
    }
    mock_get.return_value = mock_response
    with pytest.raises(EmailDoesntExist) as exc_info:
        validate_email(email)
    expected_message = "Email '{}' doesn't exist.".format(email)
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == 404

@patch("src.validators.email_validator.requests.get")
@pytest.mark.unit
def test_email_invalid_format(mock_get):
    email = 'alys1.weissgmail.com'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'status': 'invalid',
        'reason': "invalid_syntax",
        'email': 'alys1.weissgmail.com'
    }
    mock_get.return_value = mock_response
    with pytest.raises(EmailInvalidFormat) as exc_info:
        validate_email(email)
    expected_message = "The '{}' is not in a valid format.".format(email)
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == 400

@patch("src.validators.email_validator.requests.get")
@pytest.mark.unit
def test_email_invalid_mx(mock_get):
    email = 'alys1.weiss@example.com'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'status': 'invalid',
        'reason': "invalid_mx_record",
        'domain': 'example.com'
    }
    mock_get.return_value = mock_response
    with pytest.raises(EmailInvalidMX) as exc_info:
        validate_email(email)
    expected_message = "The MX record of the domain 'example.com' is not valid."
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == 422

@patch("src.validators.email_validator.requests.get")
@pytest.mark.unit
def test_email_invalid_domain(mock_get):
    email = 'alys1.weiss@gmail'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'status': 'invalid',
        'reason': "invalid_domain",
        'domain': 'gmail'
    }
    mock_get.return_value = mock_response
    with pytest.raises(EmailInvalidDomain) as exc_info:
        validate_email(email)
    expected_message = "The email domain 'gmail' is not valid."
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == 422

@patch("src.validators.email_validator.requests.get")
@pytest.mark.unit
def test_email_valid(mock_get):
    email = 'alys1.weiss@gmail.com'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'status': 'valid',
        'reason': "accepted_email"
    }
    mock_get.return_value = mock_response
    response = validate_email(email)
    data = response.json()
    assert response.status_code == 200
    assert data['status'] == 'valid'
    assert data['reason'] == "accepted_email"

