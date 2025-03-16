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
    
    Attributes:
        note: Optional note for the order line.
        line_id: Identifier for the order line.
        quantity: Quantity of items in the order line.
        line_extension_amount: Total amount for the line excluding taxes.
        total_tax_amount: Total tax amount for the line.
        unit_price: Unit price of the item.
        item_description: Description of the item.
        item_name: Name of the item.
        buyers_item_id: Identifier for the item assigned by the buyer.
        sellers_item_id: Identifier for the item assigned by the seller.
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
    issue_date: date
    note: Optional[str]
    buyer: PartyAttributes
    seller: PartyAttributes
    anticipated_line_extension_amount: float
    anticipated_payable_amount: float
    payment_terms: Optional[str]
    order_lines: List[OrderLineType]