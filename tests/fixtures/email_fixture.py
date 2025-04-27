#tests/fixtures/email_fixtures
import os
import pytest
import json

@pytest.fixture
def sample_email_json():
    """
    Creates the JSON data for email tests.
    """
    
    to_emails = [
        ('alys1.weiss@gmail.com', 'Alys'),
    ]

    return {
        "to_email": to_emails,
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "subject": "Your Invoice",
        "body": "<p>Attached is your invoice.</p>",
        "file_name": "invoice.json",
        "file_type": "json"
    }

@pytest.fixture
def sample_email_xml():
    """
    Creates the XML data for email tests.
    """

    to_emails = [
        ('alys1.weiss@gmail.com', 'Alys'),
    ]

    return {
        "to_email": to_emails,
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "subject": "Your Invoice",
        "body": "<p>Attached is your invoice.</p>",
        "file_name": "invoice.xml",
        "file_type": "xml"
    }

@pytest.fixture
def sample_email_pdf():
    """
    Creates the PDF data for email tests.
    """

    to_emails = [
        ('alys1.weiss@gmail.com', 'Alys'),
    ]

    return {
        "to_email": to_emails,
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "subject": "Your Invoice",
        "body": "<p>Attached is your invoice.</p>",
        "file_name": "invoice.txt",
        "file_type": "txt"
    }

@pytest.fixture
def sample_email_missing_fields_xml():
    """
    Creates XML data for email tests with missing fields.
    (Deliberately missing 'subject' or 'file_name' to test validation)
    """

    to_emails = [
        ('alys1.weiss@gmail.com', 'Alys'),
    ]

    return {
        "to_email": to_emails,
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        # "subject" intentionally missing
        "body": "<p>Attached is your invoice.</p>",
        "file_name": "invoice.xml",
        "file_type": "xml"
    }


@pytest.fixture
def sample_email_invalid_filetype():
    """
    Creates the TXT data for email tests.
    """

    to_emails = [
        ('alys1.weiss@gmail.com', 'Alys'),
    ]

    return {
        "to_email": to_emails,
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "subject": "Your Invoice",
        "body": "<p>Attached is your invoice.</p>",
        "file_name": "invoice.txt",
        "file_type": "txt"
    }

@pytest.fixture
def sample_email_not_complete():
    """
    Creates the XML data for email with incomplete data.
    """

    to_emails = [
        ('alys1.weiss@gmail.com', 'Alys'),
    ]

    return {
        "to_email": to_emails,
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "subject": "Your Invoice",
        "body": "<p>Attached is your invoice.</p>",
        "file_name": "invoice.json",
        "file_type": "json"
    }

@pytest.fixture
def sample_email_multiple_recipients_json():
    """
    Creates the JSON data for email tests with multiple recipients.
    """

    to_emails = [
        ('alys1.weiss@gmail.com', 'Alys'),
        ('alyscrunch@gmail.com', 'Alys')
    ]

    return {
        "to_email": to_emails,
        "reply_email": "alyscrunch@gmail.com",
        "sender_name": "Alys",
        "subject": "Your Invoice",
        "body": "<p>Attached is your invoice.</p>",
        "file_name": "invoice.json",
        "file_type": "json"
    }
