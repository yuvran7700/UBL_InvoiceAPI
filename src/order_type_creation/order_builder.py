"""
Builder for constructing an OrderType object step-by-step.
"""

from typing import List, Optional
from src.models.order_type import OrderType, OrderLineType
from src.models.common.party_attributes import PartyAttributes
from src.models.common.contact import Contact
from src.models.common.tax_scheme import PartyTaxScheme

class OrderBuilder:
    """
    Constructs an OrderType by incrementally setting its fields.
    """
    def __init__(self):
        self._order_id: Optional[str] = None
        self._sales_order_id: Optional[str] = None
        self._note: Optional[str] = None
        self._buyer: Optional[PartyAttributes] = None
        self._seller: Optional[PartyAttributes] = None
        self._payment_terms: Optional[str] = None
        self._order_lines: List[OrderLineType] = []

    def set_order_id(self, order_id: str) -> "OrderBuilder":
        """
        Sets the order reference.
        
        Args:
            order_id (str): The order reference.
        
        Returns:
            OrderBuilder: Self for chaining.
        """
        self._order_id = order_id
        return self

    def set_sales_order_id(self, sales_order_id: str) -> "OrderBuilder":
        """
        Sets the buyer reference.
        
        Args:
            sales_order_id (str): The buyer reference.
        
        Returns:
            OrderBuilder: Self for chaining.
        """
        self._sales_order_id = sales_order_id
        return self

    def set_note(self, note: Optional[str]) -> "OrderBuilder":
        """
        Sets the note for the order.
        
        Args:
            note (Optional[str]): The order note.
        
        Returns:
            OrderBuilder: Self for chaining.
        """
        self._note = note
        return self

    def set_buyer(self, buyer_data: dict) -> "OrderBuilder":
        """
        Sets the buyer details using provided data.
        
        Args:
            buyer_data (dict): Buyer information.
        
        Returns:
            OrderBuilder: Self for chaining.
        """
        self._buyer = self._build_party_attributes(buyer_data, is_buyer=True)
        return self

    def set_seller(self, seller_data: dict) -> "OrderBuilder":
        """
        Sets the seller details using provided data.
        
        Args:
            seller_data (dict): Seller information.
        
        Returns:
            OrderBuilder: Self for chaining.
        """
        self._seller = self._build_party_attributes(seller_data, is_buyer=False)
        return self

    def set_payment_terms(self, payment_terms: Optional[str]) -> "OrderBuilder":
        """
        Sets the payment terms.
        
        Args:
            payment_terms (Optional[str]): The payment terms.
        
        Returns:
            OrderBuilder: Self for chaining.
        """
        self._payment_terms = payment_terms
        return self

    def set_order_lines(self, order_lines: List[OrderLineType]) -> "OrderBuilder":
        """
        Sets the invoice lines.
        
        Args:
            order_lines (List[OrderLineType]): List of invoice lines.
        
        Returns:
            OrderBuilder: Self for chaining.
        """
        self._order_lines = order_lines
        return self

    def _build_party_attributes(self, party_data: dict, is_buyer: bool) -> PartyAttributes:
        """
        Helper method to build a PartyAttributes object from a dictionary.
        
        Args:
            party_data (dict): Data for the party.
            is_buyer (bool): True if building for buyer, False for seller.
        
        Returns:
            PartyAttributes: The constructed party attributes.
        """
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
        """
        Builds and returns the OrderType object after validating required fields.
        
        Returns:
            OrderType: The fully constructed order.
        
        Raises:
            ValueError: If required fields are missing.
        """
        if not self._order_id or not self._buyer or not self._seller:
            raise ValueError("Missing required order fields.")
        return OrderType(
            order_reference=self._order_id,
            buyer_reference=self._sales_order_id or "",
            note=self._note,
            AccountingCustomerParty=self._buyer.dict(),
            AccountingSupplierParty=self._seller.dict(),
            payment_terms=self._payment_terms,
            invoice_lines=self._order_lines,
        )
