#src/order_type_creation/order_builder.py
"""
Builder for constructing an OrderType object step-by-step.
"""

from datetime import date
from typing import List, Optional
from src.models.order_type import OrderType, OrderLineType
from src.models.common.party_attributes import PartyAttributes
from src.models.common.contact import Contact
from src.models.common.tax_scheme import PartyTaxScheme

class OrderBuilder:
    def __init__(self):
        self._order_id: Optional[str] = None
        self._sales_order_id: Optional[str] = None
        self._note: Optional[str] = None
        self._buyer: Optional[PartyAttributes] = None
        self._seller: Optional[PartyAttributes] = None
        self._anticipated_line_extension_amount: float = 0.0
        self._anticipated_payable_amount: float = 0.0
        self._payment_terms: Optional[str] = None
        self._order_lines: List[OrderLineType] = []

    def set_order_id(self, order_id: str) -> "OrderBuilder":
        self._order_id = order_id
        return self

    def set_sales_order_id(self, sales_order_id: str) -> "OrderBuilder":
        self._sales_order_id = sales_order_id
        return self

    def set_note(self, note: Optional[str]) -> "OrderBuilder":
        self._note = note
        return self

    def set_buyer(self, buyer_data: dict) -> "OrderBuilder":
        self._buyer = self._build_party_attributes(buyer_data, is_buyer=True)
        return self

    def set_seller(self, seller_data: dict) -> "OrderBuilder":
        self._seller = self._build_party_attributes(seller_data, is_buyer=False)
        return self

    def set_anticipated_line_extension_amount(self, amount: float) -> "OrderBuilder":
        self._anticipated_line_extension_amount = amount
        return self

    def set_anticipated_payable_amount(self, amount: float) -> "OrderBuilder":
        self._anticipated_payable_amount = amount
        return self

    def set_payment_terms(self, payment_terms: Optional[str]) -> "OrderBuilder":
        self._payment_terms = payment_terms
        return self

    def set_order_lines(self, order_lines: List[OrderLineType]) -> "OrderBuilder":
        self._order_lines = order_lines
        return self

    
            
    def _build_party_attributes(self, party_data: dict, is_buyer: bool) -> PartyAttributes:
        """Helper method to build a PartyAttributes object from a dictionary."""
        if is_buyer:
            return PartyAttributes(
                customer_assigned_account_id=party_data["buyer_account_customer_id"],
                supplier_assigned_account_id=party_data["buyer_account_supplier_id"],
                party_name=party_data["buyer_name"],
                address=party_data["buyer_address"],
                endpoint_id=party_data.get("buyer_electronic_address"),
                contact=party_data.get("buyer_contact").dict() if party_data.get("buyer_contact") else None,
                tax_scheme=party_data.get("buyer_tax_scheme").dict() if party_data.get("buyer_tax_scheme") else None
            )
        else:
            return PartyAttributes(
                customer_assigned_account_id=party_data["seller_account"],
                supplier_assigned_account_id=party_data["seller_account"],
                party_name=party_data["seller_name"],
                address=party_data["seller_address"],
                endpoint_id=None,
                contact=party_data.get("seller_contact").dict() if party_data.get("seller_contact") else None,
                tax_scheme=party_data.get("seller_tax_scheme").dict() if party_data.get("seller_tax_scheme") else None
            )


    def build(self) -> OrderType:
        # Validate required fields
        if not self._order_id or not self._buyer or not self._seller:
            raise ValueError("Missing required order fields.")
        return OrderType(
            order_id=self._order_id,
            sales_order_id=self._sales_order_id or "",
            note=self._note,
            AccountingCustomerParty=self._buyer.dict(),
            AccountingSupplierParty=self._seller.dict(),
            anticipated_line_extension_amount=self._anticipated_line_extension_amount,
            anticipated_payable_amount=self._anticipated_payable_amount,
            payment_terms=self._payment_terms,
            order_lines=self._order_lines,
        )