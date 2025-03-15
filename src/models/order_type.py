# models/order_type.py
"""
Pydantic models for order data extracted from a UBL order document.
Includes key header fields, buyer/seller details, payment terms, and order lines.
"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel

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


class OrderType(BaseModel):
    """
    Pydantic model representing an order.
    
    Attributes:
        order_id: Identifier for the order.
        sales_order_id: Sales order identifier.
        issue_date: Date the order was issued.
        note: Optional note for the order.
        buyer_account: Account identifier for the buyer.
        buyer_name: Name of the buyer.
        buyer_address: Address of the buyer.
        buyer_country: Optional country code of the buyer.
        buyer_scheme_id: Optional scheme identifier for the buyer.
        buyer_electronic_address: Optional electronic address for the buyer.
        seller_account: Account identifier for the seller.
        seller_name: Name of the seller.
        seller_address: Address of the seller.
        anticipated_line_extension_amount: Anticipated total amount for all lines excluding taxes.
        anticipated_payable_amount: Anticipated total payable amount.
        payment_terms: Optional payment terms for the order.
        order_lines: List of order lines.
    """
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
