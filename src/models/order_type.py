"""
Pydantic models for order data extracted from a UBL order document.
This model now includes key header fields, buyer/seller details (including addresses),
payment terms, and order lines with product code and tax details.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class OrderLineType(BaseModel):
    """
    Represents an individual order line item.
    
    Attributes:
        note (Optional[str]): Optional note for the order line.
        line_id (str): The line item identifier.
        quantity (float): Quantity ordered.
        line_extension_amount (float): The net amount for this line.
        total_tax_amount (float): Total tax for the line.
        unit_price (float): Unit price (exclusive of tax).
        item_description (str): Description of the item.
        item_name (str): Short name of the item.
        buyers_item_id (str): Product code provided by the buyer.
        sellers_item_id (str): Product code provided by the seller.
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
    Represents the enriched order extracted from the UBL XML.
    
    Attributes:
        order_id (str): Unique order identifier (cbc:ID).
        sales_order_id (str): Sales order reference (cbc:SalesOrderID).
        uuid (str): Universal unique identifier (cbc:UUID).
        issue_date (date): Order issue date (cbc:IssueDate).
        note (Optional[str]): Additional order notes.
        buyer_account (str): Buyer account ID from BuyerCustomerParty.
        buyer_name (str): Buyer name from PartyName.
        buyer_address (str): Formatted buyer postal address.
        seller_account (str): Seller account ID from SellerSupplierParty.
        seller_name (str): Seller name from PartyName.
        seller_address (str): Formatted seller postal address.
        anticipated_line_extension_amount (float): Total net amount.
        anticipated_payable_amount (float): Total payable amount.
        payment_terms (Optional[str]): Payment terms from TransactionConditions.
        order_lines (List[OrderLineType]): List of order line items.
    """
    order_id: str
    sales_order_id: str
    uuid: str
    issue_date: date
    note: Optional[str]
    buyer_account: str
    buyer_name: str
    buyer_address: str
    seller_account: str
    seller_name: str
    seller_address: str
    anticipated_line_extension_amount: float
    anticipated_payable_amount: float
    payment_terms: Optional[str]
    order_lines: List[OrderLineType]
