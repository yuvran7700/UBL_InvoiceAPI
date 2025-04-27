"""
Test cases for email validation API
Modules Tested: email_field_checker
"""
import pytest
import json
from src.validators.email_validator import check_fields
from src.exceptions.email_exceptions import EmailMissingFields

@pytest.mark.unit
def test_to_email_missing():

    email =  {
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "subject": "Your Invoice",
        "body": "<p>Attached is your invoice.</p>",
        "file_name": "invoice.json",
        "file_type": "json"
    }
    
    with pytest.raises(EmailMissingFields) as exc_info:
        check_fields(email).run()

    expected_message = "Missing required fields - 'to email'."
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == 422

@pytest.mark.unit
def test_subject_missing():

    to_emails = [
        ('alys1.weiss@gmail.com', 'Alys'),
    ]

    email = {
        "to_email": to_emails,
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "body": "<p>Attached is your invoice.</p>",
        "file_name": "invoice.json",
        "file_type": "json"
    }
    
    with pytest.raises(EmailMissingFields) as exc_info:
        check_fields(email).run()

    expected_message = "Missing required fields - 'subject'."
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == 422

@pytest.mark.unit
def test_file_name_missing():

    to_emails = [
        ('alys1.weiss@gmail.com', 'Alys'),
    ]

    email = {
        "to_email": to_emails,
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "subject": "Your Invoice",
        "body": "<p>Attached is your invoice.</p>",
        "file_type": "json"
    }
    
    with pytest.raises(EmailMissingFields) as exc_info:
        check_fields(email).run()

    expected_message = "Missing required fields - 'file name'."
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == 422

@pytest.mark.unit
def test_file_type_missing():

    to_emails = [
        ('alys1.weiss@gmail.com', 'Alys'),
    ]

    email = {
        "to_email": to_emails,
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "subject": "Your Invoice",
        "body": "<p>Attached is your invoice.</p>",
        "file_name": "invoice.json",
    }
    
    with pytest.raises(EmailMissingFields) as exc_info:
        check_fields(email).run()

    expected_message = "Missing required fields - 'file type'."
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == 422

@pytest.mark.unit
def test_missing_all():

    email = {
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "body": "<p>Attached is your invoice.</p>",
    }
    
    with pytest.raises(EmailMissingFields) as exc_info:
        check_fields(email).run()

    expected_message = "Missing required fields - 'to email', 'subject', 'file name', 'file type'."
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == 422