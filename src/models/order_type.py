#models/order_type.py
"""
Pydantic models for order data extracted from a UBL order document.
Includes key header fields, buyer/seller details, payment terms, and order lines.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class OrderLineType(BaseModel):
    note: Optional[str]
    line_id: str
    quantity: float
    line_extension_amount: float
    total_tax_amount: float
    unit_price: float
    item_description: str
    item_name: str
    buyers_item_id: str
    sellers_item_id: str

class OrderType(BaseModel):
    order_id: str
    sales_order_id: str
    issue_date: date
    note: Optional[str]
    buyer_account: str
    buyer_name: str
    buyer_address: str
    buyer_country: Optional[str] = None  # NEW FIELD
    buyer_scheme_id: Optional[str] = None  # NEW FIELD
    buyer_electronic_address: Optional[str] = None  # NEW FIELD
    seller_account: str
    seller_name: str
    seller_address: str
    anticipated_line_extension_amount: float
    anticipated_payable_amount: float
    payment_terms: Optional[str]
    order_lines: List[OrderLineType]
