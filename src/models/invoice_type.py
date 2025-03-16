# models/invoice_type.py
"""
Pydantic models for the UBL/A‑NZ invoice.
These models define the structure for the generated invoice, including header, parties,
line items, tax information, and payment terms.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel
from src.models.order_type import OrderType


class InvoiceType(BaseModel):
    """
    Represents the complete draft invoice.

    The invoice is composed of an OrderType (which contains all the order data,
    including the correctly named AccountingCustomerParty and AccountingSupplierParty)
    along with extra invoice-specific fields.

    Attributes:
        invoice_id (str): Unique invoice identifier.
        issue_date (date): Invoice issue date.
        invoice_type_code (str): Code representing the invoice type (e.g., "380").
        legal_monetary_total (float): Total invoice amount.
        due_date (Optional[date]): Payment due date.
        payment_means (Optional[str]): Payment method/means.
        status (str): Invoice status (default "draft").
        order (OrderType): The complete order data used to generate this invoice.
    """

    invoice_id: str
    issue_date: date
    invoice_type_code: str
    legal_monetary_total: float
    due_date: Optional[date] = None
    payment_means: Optional[str] = None
    status: str = "draft"
    order: OrderType
