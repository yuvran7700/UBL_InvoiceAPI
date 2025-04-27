from typing import List, Union, Optional, Tuple
from pydantic import BaseModel, EmailStr, Field

class SendEmailModel(BaseModel):
    to_email: Optional[
        List[Union[EmailStr, Tuple[EmailStr, str]]]
    ] = Field(
        default=None,
        description="List of recipient emails or (email, name) pairs.",
        example=[
            "to@example.com",
            ("other@example.com", "Other Name")
        ]
    )

    reply_email: Optional[EmailStr] = Field(
        default=None,
        description="Email address that recipients can reply to.",
        example="company@example.com"
    )

    sender_name: Optional[str] = Field(
        default=None,
        description="Sender's display name.",
        example="Alys"
    )

    subject: Optional[str] = Field(
        default=None,
        description="Email subject line.",
        example="Invoice for 01/01/2024"
    )

    body: Optional[str] = Field(
        default=None,
        description="HTML or plain text content for the email body.",
        example="<p>Here is your invoice attached.</p>"
    )

    file_name: Optional[str] = Field(
        default=None,
        description="File name for the invoice attachment.",
        example="invoice.json"
    )

    file_type: Optional[str] = Field(
        default=None,
        description="Attachment file type. Must be one of 'json', 'xml', or 'pdf'.",
        example="json"
    )


class MissingEmailFieldsReport(BaseModel):
    missing_email_fields: List[str] = Field(
        default=None,
        description="List of missing required email fields.",
        example=["file_name", "file_type"]
    )
