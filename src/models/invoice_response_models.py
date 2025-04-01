#src/models/invoice_response_models.py

from typing import List, Dict, Optional
from pydantic import BaseModel

from src.models.invoice_update import InvoiceUpdateModel

from enum import Enum

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class MissingFieldsReport(BaseModel):
    missing_invoice_fields: List[str]
    missing_invoice_lines: List[str]

class InvoiceResponse(BaseModel):
    invoice_id: Optional[str]  # Present if completed, None otherwise
    invoice: InvoiceUpdateModel  # Full invoice structure (completed or draft)
    missing_fields_report: Optional[MissingFieldsReport]  # Only for drafts
    status: InvoiceStatus  # e.g., "draft" or "completed"

class DeleteInvoicesRequest(BaseModel):
    invoice_ids: List[str]
