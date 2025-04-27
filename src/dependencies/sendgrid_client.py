# src/dependencies/sendgrid_client.py

from sendgrid import SendGridAPIClient


SENDGRID_API_KEY = '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'


sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
