# src/services/email_service.py

import base64
import json
from typing import Union, List
from io import BytesIO
from datetime import date

from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition, ReplyTo
from weasyprint import HTML

from src.dependencies.sendgrid_client import sendgrid_client
from src.domain.models.email_models import SendEmailModel
from src.domain.models.invoice_update import InvoiceUpdateModel
from src.domain.models.invoice_response_models import InvoiceStatus
from src.exceptions.email_exceptions import EmailMissingFields, EmailSendError, EmailInvalidFileType
from src.exceptions.invoice_exceptions import InvoiceNotFoundError
from src.repositories.invoice_repository_v2 import get_invoice_by_id
from src.validators.email_field_checker import MissingEmailFieldChecker
from src.validators.email_validator import validate_email, check_fields
from src.marshallers.exporters.strategies.xml_format import XmlInvoiceFormatter
from src.utils.template_helpers import get_template  # If you're rendering PDFs from HTML templates

class EmailService:
    """
    Service class to handle sending invoices via email.
    """

    def __init__(self):
        self.from_email = "mercuryinvoicing@gmail.com"

    async def send_invoice_email(
        self,
        organisation_id: str,
        invoice_id: str,
        user_id: str,
        email_data: SendEmailModel
    ) -> dict:
        """
        Sends the invoice via email to an external recipient.
        """

        result = get_invoice_by_id(invoice_id, organisation_id)
        if not result:
            raise InvoiceNotFoundError(invoice_id)

        invoice, status = result

        if status != InvoiceStatus.COMPLETED:
            raise EmailSendError("Only completed invoices can be emailed.")

        # Validate fields
        check_fields(email_data)
        missing_fields = MissingEmailFieldChecker(email_data).run()
        if missing_fields.missing_email_fields:
            raise EmailMissingFields(missing=missing_fields.missing_email_fields)

        # Validate emails
        if email_data.to_email:
            for email_address, _ in email_data.to_email:
                validate_email(email_address)
        validate_email(email_data.reply_email)

        # Prepare attachment
        encoded_file, content_type, suffix = self._generate_attachment_content(invoice, email_data.file_type)
        attachment = self._build_attachment(encoded_file, content_type, f"{invoice.id}.{suffix}")

        # Build and send the email
        message = self._build_email_message(email_data, attachment)

        try:
            response = sendgrid_client.send(message)
            return {"message": "Email sent successfully.", "status_code": response.status_code}
        except Exception as e:
            raise EmailSendError(str(e))

    def _generate_attachment_content(self, invoice: InvoiceUpdateModel, file_type: str) -> tuple[str, str, str]:
        """
        Generates base64-encoded content for the invoice attachment directly in memory.
        """
        if file_type == "xml":
            formatter = XmlInvoiceFormatter()
            invoice_bytes = formatter.serialize(invoice)
            encoded = base64.b64encode(invoice_bytes).decode("utf-8")
            return encoded, "application/xml", "xml"

        elif file_type == "json":
            invoice_dict = invoice.dict(exclude_none=True)
            json_bytes = json.dumps(invoice_dict, indent=2, default=self._json_serializer).encode("utf-8")
            encoded = base64.b64encode(json_bytes).decode("utf-8")
            return encoded, "application/json", "json"

        elif file_type == "pdf":
            invoice_template = get_template("invoice_template.html")
            tax = invoice.legal_monetary_total.tax_inclusive_amount - invoice.legal_monetary_total.tax_exclusive_amount
            html_invoice = invoice_template.render(invoice=invoice, tax=tax)
            content = BytesIO()
            HTML(string=html_invoice).write_pdf(content)
            pdf_bytes = content.getvalue()
            encoded = base64.b64encode(pdf_bytes).decode("utf-8")
            return encoded, "application/pdf", "pdf"

        else:
            raise EmailInvalidFileType()

    def _build_attachment(self, encoded_content: str, content_type: str, filename: str) -> Attachment:
        """
        Builds the SendGrid attachment object.
        """
        return Attachment(
            file_content=FileContent(encoded_content),
            file_type=FileType(content_type),
            file_name=FileName(filename),
            disposition=Disposition("attachment")
        )

    def _build_email_message(self, email_data: SendEmailModel, attachment: Attachment) -> Mail:
        """
        Builds the SendGrid email message using the raw to_email list directly.
        """
        message = Mail(
            from_email=self.from_email,
            to_emails=email_data.to_email,
            subject=email_data.subject,
            html_content=email_data.body
        )
        message.attachment = attachment
        message.reply_to = ReplyTo(email_data.reply_email, email_data.sender_name)
        return message

    @staticmethod
    def _json_serializer(obj: Union[date, object]) -> str:
        """
        Converts datetime/date objects to ISO format for JSON serialization.
        """
        if isinstance(obj, date):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

