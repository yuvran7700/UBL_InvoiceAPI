#src/models/invoice_response_models.py

from typing import List, Dict
from pydantic import BaseModel

class MissingFieldsReport(BaseModel):
    missing_invoice_fields: List[str]
    missing_invoice_lines: List[str]

class DraftInvoiceResponse(BaseModel):
    invoice: Dict
    missing_fields_report: MissingFieldsReport

class CompletedInvoiceResponse(BaseModel):
    invoice_id: str
    invoice: Dict