# models/order_type.py
"""
Pydantic models for order data extracted from a UBL order document.
Includes key header fields, buyer/seller details, payment terms, and order lines.
"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from models.common.party_attributes import PartyAttributes


class OrderLineType(BaseModel):
    """
    Pydantic model representing an individual order line.
    """
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
    """
    Pydantic model representing an order.
    """
    order_id: str
    sales_order_id: str
    note: Optional[str]
    AccountingCustomerParty: PartyAttributes #previous buyer: PartyAttributes
    AccountingSupplierParty: PartyAttributes #previous seller: PartyAttributes
    anticipated_line_extension_amount: float
    anticipated_payable_amount: float
    payment_terms: Optional[str]
    order_lines: List[OrderLineType]