#models/invoice_type.py
"""
Pydantic models for the UBL/A‑NZ invoice.
These models define the structure for the generated invoice, including header, parties,
line items, tax information, and payment terms.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class ClassifiedTaxCategory(BaseModel):
    """
    Represents the classified tax category for an invoice line.
    
    Attributes:
        tax_category_code (str): Tax category code (e.g. "S" for standard).
        tax_rate (float): Tax rate percentage.
        tax_scheme (str): Tax scheme identifier (e.g., "GST").
    """
    tax_category_code: str
    tax_rate: float
    tax_scheme: str

class Party(BaseModel):
    """
    Represents a party (seller or buyer) in the invoice.
    
    Attributes:
        name (str): The party name.
        account (str): The party account or identifier.
        address (str): The postal address.
        tax_identifier (Optional[str]): The tax number (e.g., GST number).
        electronic_address (Optional[str]): Electronic contact information.
    """
    name: str
    account: str
    address: str
    country_code: Optional[str] = None  # NEW FIELD
    tax_identifier: Optional[str] = None
    electronic_address: Optional[str] = None
    scheme_id: Optional[str] = None  # NEW FIELD

class InvoiceLine(BaseModel):
    """
    Represents a line item in the invoice.
    
    Attributes:
        id (int): A sequential line identifier.
        description (str): Description of the product/service.
        product_code (str): Product code (mapped from the order line).
        quantity (float): Invoiced quantity.
        unit_price (float): Unit price (exclusive of tax).
        line_extension_amount (float): Net amount for the line.
        classified_tax_category (Optional[ClassifiedTaxCategory]): Tax info for the line.
    """
    id: int
    description: str
    product_code: str
    quantity: float
    unit_price: float
    line_extension_amount: float
    classified_tax_category: Optional[ClassifiedTaxCategory] = None

class InvoiceType(BaseModel):
    """
    Represents the complete draft invoice.
    
    Attributes:
        invoice_id (str): Unique invoice identifier (used as the DynamoDB partition key).
        issue_date (date): Invoice issue date.
        invoice_type_code (str): Code representing the invoice type (e.g., "380").
        buyer_reference (Optional[str]): Buyer reference (e.g., sales order number).
        order_reference (str): Reference to the original order (order_id).
        due_date (Optional[date]): Payment due date.
        payment_means (Optional[str]): Payment method/means.
        seller (Party): Seller details.
        buyer (Party): Buyer details.
        invoice_lines (List[InvoiceLine]): List of invoice line items.
        legal_monetary_total (float): Total invoice amount.
    """
    invoice_id: str
    issue_date: date
    invoice_type_code: str
    buyer_reference: Optional[str] = None
    order_reference: str
    due_date: Optional[date] = None  # NEW FIELD
    payment_means: Optional[str] = None
    seller: Party
    buyer: Party
    invoice_lines: List[InvoiceLine]
    legal_monetary_total: float
    additional_document_reference_id: Optional[str] = None  # NEW FIELD
