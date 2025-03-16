"""
Pydantic models for order data extracted from a UBL order document.
Includes header, party, and invoice line details.
"""

from typing import List, Optional
from pydantic import BaseModel
from src.models.common.party_attributes import PartyAttributes


class OrderLineType(BaseModel):
    """
    Represents an individual invoice line (formerly order line) for an order.

    Attributes:
        note: Optional note for the invoice line.
        line_id: Unique identifier for the invoice line.
        quantity: Quantity of items.
        line_extension_amount: Calculated net amount (default is 0.0).
        total_tax_amount: Total tax for the line (default is 0.0).
        unit_price: Price per unit calculated from the XML.
        item_description: Description of the item.
        item_name: Name of the item.
        buyers_item_id: Identifier assigned by the buyer.
        sellers_item_id: Identifier assigned by the seller.
        discount: Optional discount applied (default 0.0).
        charge: Optional additional charge applied (default 0.0).
    """

    note: Optional[str]
    line_id: str
    quantity: float
    line_extension_amount: float = 0.0
    total_tax_amount: float = 0.0
    unit_price: float
    item_description: str
    item_name: str
    buyers_item_id: str
    sellers_item_id: str
    discount: Optional[float] = 0.0
    charge: Optional[float] = 0.0


class OrderType(BaseModel):
    """
    Represents an order extracted from a UBL XML order document.

    Attributes:
        order_reference: Unique order reference (formerly order_id).
        buyer_reference: Buyer reference identifier (formerly sales_order_id).
        note: Optional order note.
        AccountingCustomerParty: Buyer details.
        AccountingSupplierParty: Seller details.
        payment_terms: Payment terms associated with the order.
        invoice_lines: List of invoice lines (formerly order_lines).
    """

    order_reference: str
    buyer_reference: str
    note: Optional[str]
    AccountingCustomerParty: PartyAttributes
    AccountingSupplierParty: PartyAttributes
    payment_terms: Optional[str]
    invoice_lines: List[OrderLineType]
