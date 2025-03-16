"""
Builder for constructing an OrderType object step-by-step.
"""

from datetime import date
from typing import List, Optional
from src.models.order_type import OrderType, OrderLineType
from src.models.common.party_attributes import PartyAttributes

class OrderBuilder:
    def __init__(self):
        self._order_id: Optional[str] = None
        self._sales_order_id: Optional[str] = None
        self._issue_date: Optional[date] = None
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

    def set_issue_date(self, issue_date: date) -> "OrderBuilder":
        self._issue_date = issue_date
        return self

    def set_note(self, note: Optional[str]) -> "OrderBuilder":
        self._note = note
        return self

    def set_buyer(self, buyer: PartyAttributes) -> "OrderBuilder":
        self._buyer = buyer
        return self

    def set_seller(self, seller: PartyAttributes) -> "OrderBuilder":
        self._seller = seller
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

    def add_order_line(self, order_line: OrderLineType) -> "OrderBuilder":
        self._order_lines.append(order_line)
        return self

    def build(self) -> OrderType:
        # Validate required fields
        if not self._order_id or not self._issue_date or not self._buyer or not self._seller:
            raise ValueError("Missing required order fields.")
        return OrderType(
            order_id=self._order_id,
            sales_order_id=self._sales_order_id or "",
            issue_date=self._issue_date,
            note=self._note,
            buyer=self._buyer,
            seller=self._seller,
            anticipated_line_extension_amount=self._anticipated_line_extension_amount,
            anticipated_payable_amount=self._anticipated_payable_amount,
            payment_terms=self._payment_terms,
            order_lines=self._order_lines,
        )
